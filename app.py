# @author : Defne Demirtuerk
# Python Streamlit web application for data visualization and manipulation using 
# pandas, numpy and plotly.
# This implementation is the final product of a Coursera Certification Project. 
# The web application analyzes the motor vehicle Collisions in NYC.

import streamlit as st
import requests
# for data manipulation and data loading we will use numpy and pandas
import pandas as pd
import numpy as np
import pydeck as pdk 
import plotly.express as px

#specify the data URL
#DATA_URL = ("../data/_your_file_name_here.csv")
def download_file(url, filename):
    """
    Helper method handling downloading large files from `url` to `filename`. Returns a pointer to `filename`.
    """
    r = requests.get(url, stream=True)
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
    return filename

dataset = download_file("https://data.cityofnewyork.us/api/views/h9gi-nx95/rows.csv?accessType=DOWNLOAD",
                    "NYPD Motor Vehicle Collisions.csv")


#add title to our web application
st.title("Motor Vehicle Collisions in new York City")
st.markdown("This application is a Streamlit dashboard that can be used to analyze motor vehicle Collisions in NYC _enter_emoji_here")


#to make the cpu cycle not add up quickly with the huge dataset:
#we will add a decorator here to make it more efficient
@st.cache(persist=True)	# we don't want to do the same computations everytime the app is run
#define a function to load data of 1.6 million rows of data
def load_data(nrows):
	data = pd.read_csv(DATA_URL,
						nrows=nrows,
						parse_dates=[['CRASH_DATE', 'CRASH_TIME']]
						)

	#get a subset of data where longitude and latitude are not NA
	data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)

	#lowercase each of the column names using a lambda func.
	lowercase = lambda x:str(x).lower()
	data.rename(lowercase, axis='columns', inplace=True)
	data.rename(columns={'crash_data_crash_time':'date/time'}, inplace=True)
	return data



#load 100k rows of our data
#data = load_data(nrows=100000)
data = pd.read_csv(dataset, index_col=23)
original_data = data    # will be used for further analysis

# NEXT: We will use pandas to answer questions regarding our data
# Q) Where in NYC are the most people injured in vehicle collisions?
# filter the data according to injuries and overlay the results
st.header("Where are the most people injured in NYC?")
# we can add a slider widget 
# by that we let the user control the amount of injured people between 0-MAX_NUM in dataset
injured_people = st.slider("Number of people injured in vehicle collisions", 0, 19)
# we can plot our data on a map regarding a column value in our dataset
#here the @injure_people is the number specified in the slider widget
st.map(data.query("injured_persons >= @injured_people")[["latitude", "longitude"]].dropna(how="any"))
# we have dropped any all rows with NA values if any of lat or long columns have them


# Q) How many collisions occur during a given time of a day?
# create a slider to let user select the hour of the day
st.header("How many collisions occur during a given time of day?")
hour = st.slider("Hour to check data for", 0, 23)
#subset our data to the hour slider value against data/time column
# the date/time column is in pandas date-time format
data = data[data['date/time'].dt.hour == hour]

# state which time frame we are looking at in a markdown on the app page
st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour, (hour+1) % 24))

midpoint = (np.average(data['latitude']), np.average(data['longitude']))
#create a 3d map to show the density of collitions 
st.write(pdk.Deck(
	map_style="mapbox://styles/mapbox/light-v9",
	# set the initial location to focus according to mean values of dataset
	initial_view_state={
		"latitude": midpoint[0],
		"longitude": midpoint[1],
		"zoom": 11,
		"pitch":50
	},
	layers=[
		pdk.Layer(
			"HexagonLayer",
			data=data[['date/time', 'latitude', 'longitude']],
			get_position=['longitude', 'latitude'],
			radius=100, # the argument for radius of our pins
			extruded=True, #this argument makes the pins 3D
			pickable=True,
			elevation_scale=4,
			elevation_range=[0, 1000],
			),
	],
))

# now we will analyze crashes happening by minutes
st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))

# filter the dataset down to the samples in range of the hour
filtered = data[
	(data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour + 1))
]

# create a histogram of the crashes within the specified time range
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range(0,60))[0]
chart_data = pd.DataFrame({'minute':range(60), 'crashes':hist})
figure = px.bar(chart_data, x='mu+inute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(figure)

# lastly we query down top dangerous streets according to injury/collision types
st.header("Top 5 dangerous streets by affected type")
# create a dropdown widget for the user tp choose the injury type to analyze
selected = st.selectbox('Affected type of people', ['Pedestrians', 'Cyclists', 'Motorists'])

# display filtered dataset to the user in tables according to injury type
if selected == 'Pedestrians':
	st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(by=['injured_pedestrians'], ascending=False).dropna(how='any'))

elif selected == 'Cyclists':
	st.write(original_data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(by=['injured_cyclists'], ascending=False).dropna(how='any'))

else:
	st.write(original_data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(by=['injured_motorists'], ascending=False).dropna(how='any'))

# To enable the user to see the rwa data, we can add a checkbox widget to stremalit app and set it to be unchecked by default
if st.checkbox("Show Raw Data", False):
	# if the checkbox is checked' app will display our data as an interative table
	# when the checkbox is unchecked, the data is erased from display
	st.subheader('Raw Data')
	st.write(data)





