from flask import Flask,jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine,func
import numpy as np
import datetime as dt
import pandas as pd

#create engine
engine = create_engine('sqlite:///hawaii.sqlite')
Base = automap_base()

Base.prepare(engine,reflect = True)
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

#step 1:
app = Flask(__name__)

@app.route("/")
def helloWorld():
    #urls thatt tell the user the end points are avaialble    

    return"""<html>
    <h1>List of all available Hawaii Climate API routes</h1>
    <ul>
    <br>
    <li>
    Return a list of precipitations from last year:
    <br>
    <a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a>
    </li>
    <br>
    <li>
    Return a JSON list of stations from the dataset: 
    <br>
   <a href="/api/v1.0/stations">/api/v1.0/stations</a>
   </li>
    <br>
    <li>
    Return a JSON list of Temperature Observations (tobs) for the previous year:
    <br>
    <a href="/api/v1.0/tobs">/api/v1.0/tobs</a>
    </li>
    <br>
    <li>
    Return a JSON list of tmin, tmax, tavg for the dates greater than or equal to the date provided:
    <br>Replace &ltstart&gt with a date in Year-Month-Day format.
    <br>
    <a href="/api/v1.0/2017-07-15">/api/v1.0/2017-07-0115</a>
    </li>
    <br>
    <li>
    Return a JSON list of tmin, tmax, tavg for the dates in range of start date and end date inclusive:
    <br>
    Replace &ltstart&gt and &ltend&gt with a date in Year-Month-Day format. 
    <br>
    <br>
    <a href="/api/v1.0/2017-07-01/2017-07-15">/api/v1.0/2017-07-01/2017-07-15</a>
    </li>
    <br>
    </ul>
    </html>
    """



@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    """Return a list of precipitations from last year"""
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    max_date = session.query(func.max(Measurement.date)).scalar()

    # Calculate the date 1 year ago from today
    # The days are equal 365 so that the first day of the year is included
    lastDayMinusOneYear = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=365)
    
    # Perform a query to retrieve the data and precipitation scores
    lastYearsResults = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= lastDayMinusOneYear).\
        order_by((Measurement.date).desc()).all()

    # Convert list of tuples into normal list
    prcp_dict = dict(lastYearsResults)
    session.close()

    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    #return a list of all the stations in json format
    listOfStations = session.query(Station.station).all()
    stationOneDimension = list(np.ravel(listOfStations))

    session.close()

    return jsonify(stationOneDimension)

@app.route("/api/v1.0/tobs")
def tobs(): 
    session = Session(engine)

    """Return a JSON list of Temperature Observations (tobs) for the previous year."""

    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    max_date = session.query(func.max(Measurement.date)).scalar()

    # Calculate the date 1 year ago from today
    # The days are equal 365 so that the first day of the year is included
    lastDayMinusOneYear = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=365)
    # Query tobs
    results_tobs = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= lastDayMinusOneYear).all()

    # Convert list of tuples into normal list
    tobs_list = list(results_tobs)
    session.close()

    return jsonify(tobs_list)



@app.route("/api/v1.0/<start>")
def start(start=None):
    session = Session(engine)

    """Return a JSON list of tmin, tmax, tavg for the dates greater than or equal to the date provided"""

    from_start = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    from_start_list=list(from_start)

    session.close()   
    return jsonify(from_start_list)

    

@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    session = Session(engine)

    """Return a JSON list of tmin, tmax, tavg for the dates in range of start date and end date inclusive"""
    
    between_dates = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    between_dates_list=list(between_dates)
    session.close()

    return jsonify(between_dates_list)


#last step:
if __name__ == '__main__':
    app.run()