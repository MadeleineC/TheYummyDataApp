import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func,MetaData,inspect
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)

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

#get route for restaurant results
@app.route("/fetch", methods=["GET", "POST"]) #need to add <city_state_type>
def fetch():
    """send variables to python"""
    if request.method == "POST":
        city = request.form["city"]
        city = city.lower()
        state = request.form["state"]
        state = state.lower()
        cuisine = request.form["cuisine"]
        cuisine = cuisine.lower()

        # pet = Pet(name=name, lat=lat, lon=lon)
        # db.session.add(pet)
        # db.session.commit()
        print(city)
        print(state)
        print(cuisine)
        city_state = city+state
        print(city_state)
        redirect_link = "/zips/"+city_state
        print(redirect_link)
        # return redirect("http://localhost:5000/", code=302)
        return redirect(redirect_link)
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)

