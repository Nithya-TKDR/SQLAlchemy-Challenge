#################################################
# SQLAchemy Challenge - Part 2
# Flask API Climate App
# This app is based on the queries developed in Part 1 of this challenge via SQLAlchemy ORM queries, Pandas and Matplotlib.
#################################################
# The following are the requirements for each route within the app:
#   1. / - Start at the homepage and list all available routes.
#   2. /api/v1.0/precipitation - Return a JSON representation of the dictionary that provides the precipitation analysis of the past 12 months (date as key, prcp as value).
#   3. /api/v1.0/stations - Returns a JSON list of all stations in the dataset.
#   4. /api/v1.0/tobs - Return a JSON list of temperature observations for the previous year for the most-active station.
#   5. /api/v1.0/<start> and /api/v1.0/<start>/<end>
#       a) For a specified start date, returns a JSON list of the minimum temperature (TMIN), the average temperature (TAVG), and the maximum temperature (TMAX) \ 
#          for all the dates greater than or equal to the start date.
#       b) For a specified start date and end date, returns a JSON list of the minimum temperature (TMIN), the average temperature (TAVG), and the maximum temperature (TMAX) \ 
#          from the start date to the end date (both inclusive).
#################################################
# Input Date Range (based on the climate dataset) is between 2010-01-01 and 2017-08-23 (both inclusive).
# Output - Upon successful debugging and compiling the output is viewed on a dedicated URL on the browser on a development server (http://127.0.0.1:5000)

#################################################
# Import the dependencies
#################################################
import numpy as np

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

import datetime as dt
import os

#################################################
# Database Setup
#################################################
DB_File_Path = os.getcwd() + "\Resources\hawaii.sqlite"
SQLALCHEMY_DATABASE_URI = "sqlite:///" + DB_File_Path
engine = create_engine(SQLALCHEMY_DATABASE_URI)

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with = engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

####################################################
# Flask Setup - Ensure Indentation for Neat Printing
####################################################

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

#################################################
# Flask Routes
# Set the landing page for the App. List all routes that are available for reference. 
#################################################

@app.route("/")
def welcome():
    return (
        f"<h1>Welcome to the Climate App: A Flask API for Vacation Planning!</h1>"
        f"<h3>This App has the following available routes:</h3>"
        f"-----------------------------------------------------<br/>"
        f"Precipitation Analysis: Date and Precipitation for the past year:<br/>"
        f"/api/v1.0/precipitation<br/><br/>"
        f"List of all stations in the dataset:<br/>"
        f"/api/v1.0/stations<br/><br/>"
        f"Dates and Temperature Observations (TOBS) for the most active station for the last one year:<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"Temperature Statistics: TMIN, TMAX and TAVG - for all dates after a specified start date<br/>"
        f"/api/v1.0/start_date<br/><br/>"
        f"Temperature Statistics: TMIN, TMAX and TAVG - for all dates between the specified start and end dates (both inclusive) <br/>"
        f"/api/v1.0/start_date/end_date<br/>"
        f"-----------------------------------------------------<br/>"
    )

#################################################
# Requirement 1: Query the last 12 months of precipitation data and return the results as dictionary (date as key, precipitation as value)
#################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year from the last date in data set
    last_twelve_months = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Query to retrieve the date and precipitation for the last 12 months
    precipitation_query_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_twelve_months).all()
    session.close()

    # Convert the query results to a dictionary using date as the key and prcp as the value
    precipication_dict = {date: prcp for date, prcp in precipitation_query_results}

    # Return the JSON representation of dictionary
    return jsonify(precipication_dict)

#################################################
# Requirement 2: Return a JSON list of stations from the given dataset
#################################################
@app.route("/api/v1.0/stations")
def stations():
    # Query to return the list of all stations in the dataset
    results = session.query(Station.station, Station.name).all()

    # Convert the query results to a list - use 'ravel' function to accomplish this
    all_stations = list(np.ravel(results))
    
    session.close()

    # Return the JSON representation of the list above
    return jsonify(all_stations)

#################################################
# Requirement 3: Query the dates and temperature observations (TOBS) of the most active station for the last year of data
#################################################

@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date 1 year ago from the last data point in the database
    last_twelve_months = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Find the most active station
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count().desc()).first()

    # Get the station id of the most active station
    (most_active_station_id, ) = most_active_station

    # Query to retrieve the date and temperature for the most active station for the last one year.
    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station_id).filter(Measurement.date >= last_twelve_months).all()
    
    session.close()

    # Convert the query results to a list using date as the key and temperature as the value - use 'ravel' function to accomplish this
    all_temp = list(np.ravel(tobs_data))
    
    # Return the JSON representation of the list above
    return jsonify(all_temp)

#################################################
# Requirement 4: For a given start date or start-end date range, return a JSON list of the TMIN (Minimum Temperature), TAVG (Average Temperature) and the TMAX (Maximum Temperature)
#################################################

@app.route('/api/v1.0/<start_date>')
@app.route("/api/v1.0/<start_date>/<end_date>")
def start_date_end_date_stats(start_date, end_date = None):
    if end_date != None:
        temp_query_results = session.query(func.min(Measurement.tobs), func.round(func.avg(Measurement.tobs),2), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    else:
        temp_query_results = session.query(func.min(Measurement.tobs), func.round(func.avg(Measurement.tobs),2), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()

    session.close()

    # Convert the query results to a list.
    temp_query_list = []
    no_temp_data = False
    for tmin, tavg, tmax in temp_query_results:
        if tmin == None or tavg == None or tmax == None:
            no_temp_data = True
        temp_query_list.append(tmin)
        temp_query_list.append(tavg)
        temp_query_list.append(tmax)
        
    # Return the JSON representation of the list.
    if no_temp_data == True:
        return f"No temperature data found for the given date range. Please try another date range between 2010-01-01 and 2017-08-23."
    else:
        return jsonify(temp_query_list)

# #################################################
# Step 4: Define Main Module for App Execution
# ################################################# 
if __name__ == "__main__":
    app.run(debug = True)