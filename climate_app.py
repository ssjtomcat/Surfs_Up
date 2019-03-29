import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

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
        f"Hawaii Precipitation and Weather Data<br/><br/>"
        f"Pick from the available routes below:<br/><br/>"
        f"Precipiation from 2016-08-22 to 2017-08-23.<br/>"
        f"/api/v1.0/precipitation<br/><br/>"
        f"A list of all the weather stations in Hawaii.<br/>"
        f"/api/v1.0/stations<br/><br/>"
        f"The Temperature Observations (tobs) from 2016-08-22 to 2017-08-23.<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"Type in a single date (i.e., 2017-01-01) to see the min, max and avg temperature since that date.<br/>"
        f"/api/v1.0/<start><br/><br/>"
        f"Type in a date range (i.e., 2017-01-01/2017-01-10) to see the min, max and avg temperature for that range.<br/>"
        f"/api/v1.0/<start>/<end><br/><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Docstring 
    """Return a list of precipitations from last year"""
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Get the first element of the tuple
    max_date = max_date[0]

    # Calculate the date 1 year ago from today
    # The days are equal 366 so that the first day of the year is included
    year_ago = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=366)
    
    # Perform a query to retrieve the data and precipitation scores
    results_precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()

    # Convert list of tuples into normal list
    precipitation_dict = dict(results_precipitation)

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations(): 
    # Docstring
    """Return a JSON list of stations from the dataset."""
    # Query stations
    results_stations =  session.query(Measurement.station).group_by(Measurement.station).all()

    # Convert list of tuples into normal list
    stations_list = list(np.ravel(results_stations))

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs(): 
    # Docstring
    """Return a JSON list of Temperature Observations (tobs) for the previous year."""

    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Get the first element of the tuple
    max_date = max_date[0]

    # Calculate the date 1 year ago from today
    # The days are equal 366 so that the first day of the year is included
    year_ago = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=366)
    # Query tobs
    results_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).all()

    # Convert list of tuples into normal list
    tobs_list = list(results_tobs)

    return jsonify(tobs_list)



@app.route("/api/v1.0/<start>")
def start(start=None):

    # Docstring
    """Return a JSON list of tmin, tmax, tavg for the dates greater than or equal to the date provided"""

    from_start = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), 
                                func.avg(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    from_start_list=list(from_start)
    return jsonify(from_start_list)

    

@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    # Docstring
    """Return a JSON list of tmin, tmax, tavg for the dates in range of start date and end date inclusive"""
    
    between_dates = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), 
                                func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    between_dates_list=list(between_dates)
    return jsonify(between_dates_list)



if __name__ == '__main__':
    app.run(debug=True)