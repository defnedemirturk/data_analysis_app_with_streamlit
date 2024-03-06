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
import os

#specify the data URL and set up directories 
current_directory = os.path.dirname(os.path.abspath(__file__))
DATA_URL = os.path.join(current_directory, 'Motor_Vehicle_Collisions_-_Crashes.csv')

#add title to our web application
st.title("Motor Vehicle Collisions in New York City")
st.markdown("This application is a Streamlit dashboard that can be used to analyze motor vehicle Collisions in NYC.")


#to make the cpu cycle not add up quickly with the huge dataset:
#we will add a decorator here to make it more efficient
@st.cache_data(persist=True)	# we don't want to do the same computations everytime the app is run
#define a function to load data of 1.6 million rows of data
def load_data(nrows):
	data = pd.read_csv(DATA_URL,
						nrows=nrows,
						parse_dates=[['CRASH DATE', 'CRASH TIME']]
						)

	#get a subset of data where longitude and latitude are not NA
	data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)

	#lowercase each of the column names using a lambda func.
	lowercase = lambda x:str(x).lower()
	data.rename(lowercase, axis='columns', inplace=True)
	print(data.columns)
	# Replace spaces in column names with underscores
	data.columns = data.columns.str.replace(' ', '_')
	print(data.columns)
	data.rename(columns={'crash_date_crash_time':'date/time'}, inplace=True)
	#data.rename(columns={'number of persons injured':'injured_people'}, inplace=True)
	return data



#load 100k rows of our data
data = load_data(nrows=100000)
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


st.map(data.query("number_of_persons_injured >= @injured_people")[["latitude", "longitude"]].dropna(how="any"))
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
#hist, a = np.histogram(filtered['date/time'].dt.minute, bins=60, range=range(0,60))
#chart_data = pd.DataFrame({'minute':range(60), 'crashes':hist})
#figure = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
#st.write(figure)

# lastly we query down top dangerous streets according to injury/collision types
st.header("Top 5 dangerous streets by affected type")
# create a dropdown widget for the user tp choose the injury type to analyze
selected = st.selectbox('Affected type of people', ['Pedestrians', 'Cyclists', 'Motorists'])

# display filtered dataset to the user in tables according to injury type
if selected == 'Pedestrians':
	st.write(original_data.query("number_of_pedestrians_injured >= 1")[["on_street_name", "number_of_pedestrians_injured"]].sort_values(by=['number_of_pedestrians_injured'], ascending=False).dropna(how='any'))

elif selected == 'Cyclists':
	st.write(original_data.query("number_of_cyclists_injured >= 1")[["on_street_name", "number_of_cyclists_injured"]].sort_values(by=['number_of_cyclists_injured'], ascending=False).dropna(how='any'))

else:
	st.write(original_data.query("number_of_motorists_injured >= 1")[["on_street_name", "number_of_motorists_injured"]].sort_values(by=['number_of_motorists_injured'], ascending=False).dropna(how='any'))

# To enable the user to see the rwa data, we can add a checkbox widget to stremalit app and set it to be unchecked by default
if st.checkbox("Show Raw Data", False):
	# if the checkbox is checked' app will display our data as an interative table
	# when the checkbox is unchecked, the data is erased from display
	st.subheader('Raw Data')
	st.write(data)





