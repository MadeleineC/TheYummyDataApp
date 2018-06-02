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
def check_state(key):
    key = key.lower()
    key = ' '.join(word[0].upper() + word[1:] for word in key.split())
    us_state_abbrev = {
        'Alabama': 'AL',
        'Alaska': 'AK',
        'Arizona': 'AZ',
        'Arkansas': 'AR',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'Delaware': 'DE',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Hawaii': 'HI',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Iowa': 'IA',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Maine': 'ME',
        'Maryland': 'MD',
        'Massachusetts': 'MA',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Mississippi': 'MS',
        'Missouri': 'MO',
        'Montana': 'MT',
        'Nebraska': 'NE',
        'Nevada': 'NV',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'New York': 'NY',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Pennsylvania': 'PA',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Vermont': 'VT',
        'Virginia': 'VA',
        'Washington': 'WA',
        'West Virginia': 'WV',
        'Wisconsin': 'WI',
        'Wyoming': 'WY',
        'Washington, DC': 'DC',
        'District of Columbia': 'DC'
    }
    
    if key in us_state_abbrev.keys():
        return str(us_state_abbrev[key]).lower()
    elif key.upper() in us_state_abbrev.values():
        return key.lower()
    else:
        return "Not found"

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
        income=i.Wealthy

        #query geocoordinates from the zip_shape table in the DB
        geometry=session.query(zip_shapes.geometry).filter(zip_shapes.zip_code==int(zip_search))[0][0]
        
        #pass the string of geocoordinates json.load
        start_index=geometry.find('[[')
        coordinate=json.loads(geometry[start_index:-1])
        type_end=geometry.find("', 'coordinates")
        geo_type=geometry[10:type_end]

        #pull in information into one geoJSON feature 
        feature={'type':'Feature',\
             'properties':{'zipcode':zip_search,'population':population,'income_per_capita':income},\
            'geometry':{'type':geo_type,'coordinates':coordinate}\
                }
        #remove any postbox zipcode with a population with 0
        if feature['properties']['population']==0:
            print('>>>>>>>>>>>>>>>>>> delete' + feature['properties']['zipcode'])
        else:
            features.append(feature)
    #put all the features in to a feature_collections object
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
    
    yummy_info=[
                {
                    'city':city,
                    'state':state,
                    'cuisine':cuisine
                    }
                ]
    print(yummy_info)
    
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
        sleep(0.5)
        
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
    # print(kwargs)
    if("google_results" in kwargs and "city_state_cuisine" in kwargs): 
        google_results = kwargs['google_results']
        city_state_cuisine=kwargs['city_state_cuisine']
        
    else:
        google_results = []
    
    cleaned_google_results = []
    for i in range(0,len(google_results)):
        if ('formatted_address' in google_results[i]):
            address = google_results[i]['formatted_address']
            zip_store = re.findall('[A-Z]{2} [0-9]{5}',google_results[i]['formatted_address'])
            if zip_store==[]:
                zip_store='Nan'
            else:
                zip_store = zip_store[0][3:]
            # print(zip_store)
        else:
            address = 'Nan'

        business_name = google_results[i]['name']
        if re.findall('\"(.+?)\"', business_name)!=[]:
                print('>>>>>>>>>$$$$$$$$$$$$-Modify this Inquote {}'.format(business_name))
                # quot_start=dict_result['Name'].find('\"')
                business_name=' '.join(business_name.split('\"'))
                print('New business_name is {}'.format(business_name))

        latitude =  google_results[i]['geometry']['location']['lat']
        longitude = google_results[i]['geometry']['location']['lng']
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
            'Latitude' : latitude,
            'Longitude' : longitude,
            'Name' : business_name,
            'Price_Level' : price,
            'Rating' : rating,
            'Zip' : zip_store,
            'City_State_Cuisine':city_state_cuisine
            }
        #check if the restaurant is in the cleaned_google_results list already
        Flag = 'Not Found'
        for stored_item in cleaned_google_results:
            if item['Address']==stored_item['Address']:
                Flag='Found'
                break
        if address == 'Nan' or Flag=='Found' or zip_store=='Nan':
            print('************> deleted' + business_name )
        else:
            cleaned_google_results.append(item)
            # print(i)
            # print(item)
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

#get route for restaurant results
@app.route("/fetch/", methods=["GET", "POST"]) 
def fetch():
    print('******************* AT Fetch')
    """send variables to python"""
    if request.method == "POST":
        city = request.form["city"]
        city = city.lower().strip(' ')
        state = request.form["state"]
        state = state.strip(' ')
        state = check_state(state)
        cuisine = request.form["cuisine"]
        cuisine = cuisine.lower().strip(' ')
        
        # if a wrong state is in input set to the default
        if state=="Not found":
            demographics = get_demo()
            yummy_info=getYummyInfo()

        else:
            demographics=get_demo(city=city,state=state)
            yummy_info=getYummyInfo(city=city,state=state,cuisine=cuisine)

            #query if city_state_cuisine is in the database already
            city_state_cuisine='-'.join([city,state,cuisine])
            print('\n*******************\n Back in fetch city_state_cuisine is {}'.format(city_state_cuisine))
            search=session.query(user_input).filter(user_input.City_State_Cuisine==city_state_cuisine).first()
            if search == None:
                print('******************** search back in fetch')
                google_results = apiCall(city=city, state=state, cuisine=cuisine)
                print("********")
                # print(google_results)
                print("TTTTTT")
                # print(google_results[0])
                google_results = clean_google_results(google_results=google_results,city_state_cuisine=city_state_cuisine)
                
                #insert into the database if the google_results are not empty
                if google_results !=[]:
                    conn = engine.connect()
                    conn.execute(restaurant.__table__.insert(), google_results)
                    new_user=[{'City':city,'State':state,'Cuisine':cuisine,
                            'City_State':'-'.join([city,state]),'City_State_Cuisine':city_state_cuisine}]
                    conn.execute(user_input.__table__.insert(),new_user)
                print("SSSSS")
                print(google_results)
            else:
                print('DDDDDDDDDDDDDD DATABASE')
                results=session.query(restaurant).filter(restaurant.City_State_Cuisine==city_state_cuisine).all()
                google_results=[]
                for i in results:
                    dict_result=i.__dict__
                    del dict_result['_sa_instance_state']
                    if re.findall('\"(.+?)\"', dict_result['Name'])!=[]:
                        print('>>>>>>>>>$$$$$$$$$$$$-Modify this Inquote {}'.format(dict_result))
                        # quot_start=dict_result['Name'].find('\"')
                        dict_result['Name']=' '.join(dict_result['Name'].split('\"'))
                        print('New dict_result is {}'.format(dict_result['Name']))
                    google_results.append(dict_result)
                
                print('SSSSSSSSSSS-Queried-Result')
                print(google_results[0])

    return render_template("dashboard.html", demographics=demographics, yummy_info=yummy_info , google_results=google_results)

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
    print("\nGGGGGGGGGGGGGGGGGG\n At DASHBOARD--Initial Loading")
    demographics = get_demo()
    yummy_info = getYummyInfo()
    city=yummy_info[0]['city']
    state=yummy_info[0]['state']
    cuisine=yummy_info[0]['cuisine']
    city_state_cuisine='-'.join([city,state,cuisine])
    print("GGGGGGGGGGGGGGGG---city_state_cuisine{}".format(city_state_cuisine))
    search=session.query(user_input).filter(user_input.City_State_Cuisine==city_state_cuisine).first()
    if search == None:
        google_results = apiCall(city=city, state=state, cuisine=cuisine)
        print("XXXX")
        # print(google_results)
        print("TTTTTT")
        # print(google_results[0])
        google_results = clean_google_results(google_results=google_results,city_state_cuisine=city_state_cuisine)
        #insert into the database if the google_results are not empty
        if google_results !=[]:
            conn = engine.connect()
            conn.execute(restaurant.__table__.insert(), google_results)
            new_user=[{'City':city,'State':state,'Cuisine':cuisine,
                            'City_State':'-'.join([city,state]),'City_State_Cuisine':city_state_cuisine}]
            conn.execute(user_input.__table__.insert(),new_user)
        print("SSSSS")
        print('Inserted into DATABASE')
    else:
        print('DDDDDDDDDDDDDD QUERY DATABASE')
        results=session.query(restaurant).filter(restaurant.City_State_Cuisine==city_state_cuisine).all()
        google_results=[]
        for i in results:
            dict_result=i.__dict__
            del dict_result['_sa_instance_state']
            google_results.append(dict_result)
        print('SSSSSSSSSSS-Queried-Result')
        print(google_results[0])

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

