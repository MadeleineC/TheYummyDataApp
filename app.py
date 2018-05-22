import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func,MetaData,inspect
from flask import (
    Flask,
    render_template,
    jsonify)

# create engine to connect to the database
engine=create_engine("sqlite:///yummydata_1.sqlite", echo=False)
#automap_base
Base = automap_base()
Base.prepare(engine, reflect=True)
#set up session queries
session=Session(engine)

# #inspect table names
# inspect(engine).get_table_names()

# Assign tables as objects
zip_demo=Base.classes.zip_demographics
restaurant=Base.classes.restaurant_search
user_input=Base.classes.user_input

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """Render Home Page."""
    return render_template("index.html")

#get route to return zip results
@app.route("/zips/<city_state>")
def zips(city_state):
    """Return sample names"""

    # sample names are column (from the 2nd column) names for the table samples
    results = session.query(zip_demo).filter(zip_demo.City_State==city_state).all()
    #convert result into dictionary
    results_list=[]
    for i in results:
        dict_result=i.__dict__
        del dict_result['_sa_instance_state']
        results_list.append(dict_result)
    return jsonify(results_list)

#get route for restaurant results
@app.route("/restaurant") #need to add <city_state_type>
def restaurnt():
    """Return sample names"""

    # sample names are column (from the 2nd column) names for the table samples
    results = session.query(restaurant).all()
    #convert result into dictionary
    results_list=[]
    for i in results:
        dict_result=i.__dict__
        del dict_result['_sa_instance_state']
        results_list.append(dict_result)
    return jsonify(results_list)


if __name__ == '__main__':
    app.run(debug=True)

