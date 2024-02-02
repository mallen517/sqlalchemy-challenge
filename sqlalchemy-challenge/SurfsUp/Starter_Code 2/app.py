# Import the dependencies.
import matplotlib
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask, jsonify
import datetime as dt
import numpy as np

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text, inspect, func


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)


# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station


# Create our session (link) from Python to the DB
session = session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)




#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/measurement<br/>"
        f"/api/v1.0/station"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def prcp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for the dates and precipitation values
    results =   session.query(measurement.date, measurement.prcp).\
                order_by(measurement.date).all()

    # Convert to list of dictionaries to jsonify
    prcp_date_list = []

    for date, prcp in results:
        new_dict = {}
        new_dict[date] = prcp
        prcp_date_list.append(new_dict)

    session.close()

    return jsonify(prcp_date_list)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    stations = {}

    # Query all stations
    results = session.query(station.station, station.name).all()
    for s,name in results:
        stations[s] = name

    session.close()
 
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Get the last date contained in the dataset and date from one year ago
    last_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_year_date = (dt.datetime.strptime(last_date[0],'%Y-%m-%d') \
                    - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    # Query for the dates and temperature values
    results =   session.query(measurement.date, measurement.tobs).\
                filter(measurement.date >= last_year_date).\
                order_by(measurement.date).all()

    # Convert to list of dictionaries to jsonify
    tobs_date_list = []

    for date, tobs in results:
        new_dict = {}
        new_dict[date] = tobs
        tobs_date_list.append(new_dict)

    session.close()

    return jsonify(tobs_date_list)

@app.route("/api/v1.0/<start>")
def start_date(start):

    # run the query to pull the min, max, and average temperatures for the range of dates
    start_date_temps = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).filter(measurement.date>=start).all()
    
     # Convert list of tuples into normal list
    temp_list = list(np.ravel(start_date_temps))
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start,end):

    # run the query to pull the min, max, and average temperatures for the range of dates
    start_date_temps = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).filter(measurement.date>=start).filter(measurement.date<=end).all()
    
     # Convert list of tuples into normal list
    temp_list = list(np.ravel(start_date_temps))
    return jsonify(temp_list)

# close the session
session.close()  

if __name__ == '__main__':
    app.run(debug=True)
