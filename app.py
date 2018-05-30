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
from uszipcode import ZipcodeSearchEngine
import uszipcode
import json
import requests
from time import sleep
import re
from flask_cors import CORS


############
#       keyz
############
google_places_api_key = "AIzaSyB_i6T2QOcNmKeJUxF6FC5B1XN1j-mixjI"



#################################################
# SQLite Setup
#################################################

# create engine to connect to the database
engine=create_engine("sqlite:///yummydata.sqlite", echo=False)
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
zip_shapes=Base.classes.zip_shapes



###
# Path Layout:
#   /fetch + form data 
#               -- put form data into object    
#           -- run API call with form data
#               <- return API call as object 
#       -> /zips/<citystate>
#           -- search ziplist by citystate ziplist
#               <- return demographics info
#           OR
#           -- search python zipcode package by citystate
#               <- return demographics info
#   -- plot with info
###

###
# Step 2:
#   /fetch + form data
#           -- put form data into object
#       -- run API call with form data
#           <- return API call as object
#       -> /zips/<citystate>
#           -- query zipsDB by citystate
#               <- return demographic info
#   -- plot with info
###

###
# ideal:
#   /fetch + form data
#           -- put form data into object
#       -- query zipsDB by citystate
#           -- NOTFOUND:
#               - run API call with form data
#               - search python zipcode package for demographic info
#               <- return API call + demo info object
#           -- FOUND:
#               - search python zipcode package for demographic info
#               <- return database objects + demo info object
#   -- plot with info
#   -- update JS elements with info:
#       - timestamp of search
###

#################################################
# Functions
#################################################

def get_demo(**kwargs):
    print("in get_demo")
    print(kwargs)
    if("city" in kwargs and "state" in kwargs): 
        city = kwargs['city']
        state = kwargs['state']
    else:
        city = "waco"
        state= "tx"
    print(city,state)
    zipSearch = ZipcodeSearchEngine()
    demoCall = zipSearch.by_city_and_state(city, state, returns=0, standard_only=False)
    # print(type(demoCall))
    # demographics = json.dumps(demographics)
    # demographics = json.loads(demographics)
    print("0000000")
    # demographics = jsonify(demographics)
    features=[]
    for i in demoCall:
        feature={}
        zip_search = i.Zipcode
        population=i.Population
        income_per_capita=i.Wealthy
        geometry=session.query(zip_shapes.geometry).filter(zip_shapes.zip_code==int(zip_search))[0][0]
        start_index=geometry.find('[[')
        # coordinate=geometry[start_index:-1]
        coordinate=json.loads(geometry[start_index:-1])
        type_end=geometry.find("', 'coordinates")
        geo_type=geometry[10:type_end]
#     coordinates=json.loads(geometry[35:-1])
        feature={'type':'Feature',\
             'properties':{'zipcode':zip_search,'population':population,'income_per_capita':i.Wealthy},\
            'geometry':{'type':'MultiPolygon','coordinates':coordinate}\
                }
        features.append(feature)
    feature_collections={"type": "FeatureCollection","crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::4269" } },"name": "cb_2017_us_zcta510_500k","features":features}
    return feature_collections

def getYummyInfo(**kwargs):
    print("in getYummyInfo")
    print(kwargs)
    if("city" in kwargs and "state" in kwargs and "cuisine" in kwargs): 
        city = kwargs['city']
        state = kwargs['state']
        cuisine = kwargs['cuisine']
    else:
        city = "waco"
        state= "tx"
        cuisine = "sushi"
    # print(city)
    # pythondata=[{'foo':'bar','baz':'jazz'}]
    # pythondata=[
    #             {
    #                 'city':'austin',
    #                 'state':'tx',
    #                 'cuisine':'french'
    #                 }
    #             ]
    yummy_info=[
                {
                    'city':city,
                    'state':state,
                    'cuisine':cuisine
                    }
                ]
    print(yummy_info)
    # print(json.dumps(yummy_info, default=lambda o: o.__dict__))
    # yummy_info = json.dumps(yummy_info)
    # yummy_info = json.loads(yummy_info)
    return yummy_info

def get_ziplist(**kwargs):
    print("in get_ziplist")
    print(kwargs)
    if("city" in kwargs and "state" in kwargs): 
        city = kwargs['city']
        state = kwargs['state']
    else:
        city = "waco"
        state= "tx"
    print(city,state)
    ziplist = []
    zipSearch = ZipcodeSearchEngine()
    zipCall = zipSearch.by_city_and_state(city=city, state=state, returns=0, standard_only=False)
    print(len(zipCall))
    for i in zipCall:
        print(i.Zipcode)
    for i in zipCall:
        d = i.Zipcode
        ziplist.append(d)
        # print(demographics)
    print(ziplist)
    return ziplist

def apiCall(**kwargs):
    print("in apiCall")
    #google places API 
    api_key=google_places_api_key
    if("city" in kwargs and "state" in kwargs and "cuisine" in kwargs): 
        city = kwargs['city']
        state = kwargs['state']
        key_word = kwargs['cuisine']
    else:
        city = "waco"
        state= "tx"
        key_word = "sushi"

    search_type='restaurant'
    root_url='https://maps.googleapis.com/maps/api/place/textsearch/json?'
        
    info_list=[]
    zip_list = get_ziplist(city=city, state=state)
    #loop in zip_code list
    for i in zip_list:
        #set up a page counter
        page=1
        # logging.info(page)
        #set up url for the first call 
        initial_url=root_url+'query={}+in+{}'.format(key_word,i)+'&type='+search_type+'&key='+api_key
        response=requests.get(initial_url).json()
        
        #extract results in a variable called results
        results=response['results']
        
        # logging.info('zip_code:{} page:{}/n {}/n/n'.format(i,page,initial_url))
        # logging.info('debug hey i have {} restaurants'.format(len(results)))
        
        #assign a variable to store nextpage token
        next_page=response.get("next_page_token")
        
        #sometimes it give me empty results if I make calls too often 
        sleep(1)
        
        #use a while loop for flipping pages, google allows a maximum of 3 pages 
        while bool(next_page)==True: 
            # logging.info('debug hey I am under the while loop')
            #update page counter
            page+=1
#             logging.info('debug the current page is {}'.format(page))
            #set up API call for the next page and logging it
            next_page_url=root_url+"pagetoken="+next_page+'&key='+api_key
            # logging.info('zip_code:{} page:{}/n {}/n/n'.format(i,page,next_page_url))
            response=requests.get(next_page_url).json()
            # logging.info('debug current page has {} restaurants'.format(len(response['results'])))
            
            #Add the new results to results here using 
            results=results+response["results"]
            # logging.info('debug now i have a total of {} restaurants'.format(len(results)))
            sleep(1)
            #update next_page token
            next_page=response.get("next_page_token")
            # logging.info('debug the current token is {}'.format(next_page))
        
        info_list=info_list+results 
        # logging.info('current length info_list is {}'.format(len(info_list)))
    
    print('Harvested all data')
    print('{} cells are retrieved'.format(len(info_list)))
    return info_list

def clean_google_results(**kwargs):
    print("in clean_google_results")
    print(kwargs)
    if("google_results" in kwargs): 
        google_results = kwargs['google_results']
        
    else:
        google_results = []
    
    cleaned_google_results = []
    for i in range(0,len(google_results)):
        if ('formatted_address' in google_results[i]):
            address = google_results[i]['formatted_address']
            zip_store = re.findall('[A-Z]{2} [0-9]{5}',google_results[i]['formatted_address'])
            zip_store = zip_store[0][3:]
            print(zip_store)
        else:
            address = 'Nan'
        google_id = google_results[i]['id']
        latitude =  google_results[i]['geometry']['location']['lat']
        longitude = google_results[i]['geometry']['location']['lng']
        business_name = google_results[i]['name']
        if ('price_level' in google_results[i]):
            price = google_results[i]['price_level']
        else:
            price = 0
        if ('rating' in google_results[i]):
            rating = google_results[i]['rating']
        else:
            rating = 0
        item = {
            'Address' : address,
            'Google_ID' : google_id,
            'Latitude' : latitude,
            'Longitude' : longitude,
            'Name' : business_name,
            'Price_Level' : price,
            'Rating' : rating,
            'Zip' : zip_store
        }
        #check if the restaurant is in the cleaned_google_results list already
        Flag = 'Not Found'
        for stored_item in cleaned_google_results:
            if item['Google_ID']==stored_item['Google_ID']:
                Flag='Found'
                break
        if address == 'Nan' or Flag=='Found':
            print('************> deleted' + business_name )
        else:
            cleaned_google_results.append(item)
            print(i)
            print(item)
    #remove duplicate restaurants and convert it back to list
    
    
    print('done')
    # print(cleaned_google_results[0])
    print('#{} cleaned results after removing duplicates'.format(len(cleaned_google_results)))
    return cleaned_google_results

#################################################
# Flask Setup
#################################################

app = Flask(__name__)
# cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

#################################################
# Flask Routes
#################################################

# @app.route("/")
# def home():
#     """Render Home Page."""
#     return render_template("dashboard.html")

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
@app.route("/restaurant/") #need to add <city_state_type>
def restarant():
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

#### original:
# #get route for restaurant results
# @app.route("/fetch/", methods=["GET", "POST"]) #need to add <city_state_type>
# def fetch():
#     """send variables to python"""
#     if request.method == "POST":
#         city = request.form["city"]
#         city = city.lower()
#         state = request.form["state"]
#         state = state.lower()
#         cuisine = request.form["cuisine"]
#         cuisine = cuisine.lower()


#         demographics = get_demo(city, state)
#         print(demographics)

#         # api_results = api_call(city, state, cuisine)
#         # print(api_results)

#         # pet = Pet(name=name, lat=lat, lon=lon)
#         # db.session.add(pet)
#         # db.session.commit()
#         print(city)
#         print(state)
#         print(cuisine)
#         city_state = city+state
#         print(city_state)
#         redirect_link = "/zips/"+city_state
#         print(redirect_link)
#         # return jsonify(a[0].City)
#         # return redirect("http://localhost:5000/", code=302)
#         return redirect(redirect_link)
#     return render_template("index.html")


#get route for restaurant results
@app.route("/fetch/", methods=["GET", "POST"]) #need to add <city_state_type>
def fetch():
    """send variables to python"""
    if request.method == "POST":
        city = request.form["city"]
        city = city.lower()
        state = request.form["state"]
        state = state.lower()
        cuisine = request.form["cuisine"]
        cuisine = cuisine.lower()

        print("----")
        demographics = get_demo(city=city, state=state)
        # print(demographics)
        # demographics = json.loads(demographics)
        print("ZZZZZZ")
        print(demographics)

        # api_results = api_call(city, state, cuisine)
        # print(api_results)

        # pet = Pet(name=name, lat=lat, lon=lon)
        # db.session.add(pet)
        # # db.session.commit()
        # print(city)
        # print(state)
        # print(cuisine)

        yummy_info = getYummyInfo(city=city, state=state, cuisine=cuisine)
        # yummy_info = json.loads(yummy_info)
        print('b')
        # print(yummy_info)

        google_results = apiCall(city=city, state=state, cuisine=cuisine)
        print("XXXX")
        # print(google_results)
        print("TTTTTT")
        # print(google_results[0])
        google_results = clean_google_results(google_results=google_results, state=state)
        print("SSSSS")
        print(google_results)

        # city_state = city+state
        # print(city_state)
        # redirect_link = "/zips/"+city_state
        # print(redirect_link)
        # return jsonify(a[0].City)
        # return redirect("http://localhost:5000/", code=302)
        # return redirect(redirect_link)
    return render_template("dashboard.html", demographics=demographics, yummy_info=yummy_info, google_results=google_results)

@app.route('/getpythondata/')
def get_python_data():
    # print(city)
    # pythondata=[{'foo':'bar','baz':'jazz'}]
    pythondata=[
                {
                    'city':'austin',
                    'state':'tx',
                    'cuisine':'french'
                    }
                ]

    return jsonify(pythondata)

@app.route('/')
@app.route('/dashboard/')
def dashboard():
    print("initial page load")
    demographics = get_demo()
    yummy_info = getYummyInfo()
    google_results = apiCall()
    google_results = clean_google_results(google_results=google_results) #,state='TX')
    return render_template("dashboard.html", demographics=demographics, yummy_info=yummy_info, google_results=google_results)

#deal with crossorgin issue
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

if __name__ == '__main__':
    app.run(debug=True)

