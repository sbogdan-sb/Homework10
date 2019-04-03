from flask import Flask, jsonify

import numpy as np
import pandas as pd
from datetime import datetime
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)


# List available routes
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/(yyyy-mm-dd)<br/>"
        f"/api/v1.0/(yyyy-mm-dd)/(yyyy-mm-dd)"

    )

# Return a dictionary of date/precipitation key/value pairs
@app.route("/api/v1.0/precipitation")
def precip():
    print("Server received request for precipitation dictionary")

    session = Session(engine)

    query_result = session.query(Measurement.date, Measurement.prcp).all()

    precip_dict = {}
    for row in query_result:
        precip_dict.update({row[0] : row[1]})

    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for list of stations")

    session = Session(engine)
    station_list = []

    for row in session.query(Station.station).all():
        station_list.append(row[0])
    
    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def temp():
    print("Server received request for list temp observations")

    session = Session(engine)

    # Find date of lastest measurement in Measurement table and covert to date object
    last_date_result = session.query(func.max(Measurement.date)).all()[0]
    last_date = datetime.strptime(last_date_result[0], '%Y-%m-%d').date()

    # Calculate the date 1 year ago from the last data point in the database
    first_date = last_date.replace(year=last_date.year - 1)

    # Perform a query to retrieve the data and precipitation scores
    temp_list = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date.between(first_date, last_date)).\
        order_by(Measurement.date.desc()).all()
    
    return jsonify(temp_list)


@app.route("/api/v1.0/<start_date>")
def temp_stat_start_only(start_date):
    print("Server received request for temp stats")

    session = Session(engine)

    # This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
    # and return the minimum, average, and maximum temperatures for that range of dates
    def calc_temps(start_date, end_date):
        """TMIN, TAVG, and TMAX for a list of dates.
    
        Args:
            start_date (string): A date string in the format %Y-%m-%d
            end_date (string): A date string in the format %Y-%m-%d
        
        Returns:
            TMIN, TAVE, and TMAX
        """
    
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    #get start date arg and conver to date object
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

    #Find last date in data set to use as default range end date
    end_date_result = session.query(func.max(Measurement.date)).all()[0]
    end_date = datetime.strptime(end_date_result[0], '%Y-%m-%d').date()

    temp_stats = calc_temps(start_date, end_date)

        
    return jsonify(temp_stats) 


@app.route("/api/v1.0/<start_date>/<end_date>")
def temp_stat_start_stop(start_date, end_date):
    print("Server received request for temp stats for date range")

    session = Session(engine)

    # This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
    # and return the minimum, average, and maximum temperatures for that range of dates
    def calc_temps(start_date, end_date):
        """TMIN, TAVG, and TMAX for a list of dates.
    
        Args:
            start_date (string): A date string in the format %Y-%m-%d
            end_date (string): A date string in the format %Y-%m-%d
        
        Returns:
            TMIN, TAVE, and TMAX
        """
    
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    #get start and end date args and conver to date objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    
    temp_stats = calc_temps(start_date, end_date)

        
    return jsonify(temp_stats) 

if __name__ == "__main__":
    app.run(debug=True)