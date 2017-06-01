import plotly.plotly as py
from plotly.graph_objs import *

import numpy as np
import requests
import copy
import googlemaps

mapbox_access_token = 'pk.eyJ1IjoicHpoYW8wOTE4IiwiYSI6ImNpdmI2aXY4MjAwdHUyb3AzMzE0bTlrNmwifQ.L0X8_PvnvigkDvgsVk-NlA'
r = requests.get('https://www.tesla.com/en_CA/findus#/bounds/70,-50,42,-142,d?search=supercharger,&name=Canada')
r_copy = copy.deepcopy(r.text)
supercharger_locations = {}
valid_countries = ['United States', 'Canada']
params_for_locations = ['postal_code":"', 'country":"', 'latitude":"', 'longitude":"']
while True:
    # add address line to the dictionary
    index = r_copy.find('address_line_1":"')
    if index == -1:
        break
    index += len('address_line_1":"')

    index_end = index
    while r_copy[index_end] != '"':
        index_end += 1
    address_line_1 = r_copy[index:index_end]
    address_line_1 = str(address_line_1)
    supercharger_locations[address_line_1] = {}

    for param in params_for_locations:
        index = r_copy.find(param)
        if index == -1:
            break
        index += len(param)

        index_end = index
        while r_copy[index_end] != '"':
            index_end += 1
        supercharger_locations[address_line_1][param[0:-3]] = r_copy[index:index_end]

    r_copy = r_copy[index_end:len(r.text)]  # slice off the traversed code

all_keys = list(supercharger_locations)

for key in all_keys:
    if '\\' in supercharger_locations[key] or supercharger_locations[key] == '' or supercharger_locations[key]['postal_code'] == '' or supercharger_locations[key]['country'] not in valid_countries:
        del supercharger_locations[key]

def plot_route_between_tesla_stations(address_start, address_end, zoom=3, endpt_size=6):
    start = (supercharger_locations[address_start]['latitude'], supercharger_locations[address_start]['longitude'])
    end = (supercharger_locations[address_end]['latitude'], supercharger_locations[address_end]['longitude'])
    
    directions = gmaps.directions(start, end)
    steps = []
    steps.append(start)  # add starting coordinate to trip
    
    for index in range(len(directions[0]['legs'][0]['steps'])):
        start_coords = directions[0]['legs'][0]['steps'][index]['start_location']
        steps.append((start_coords['lat'], start_coords['lng']))

        if index == len(directions[0]['legs'][0]['steps']) - 1:
            end_coords = directions[0]['legs'][0]['steps'][index]['end_location']
            steps.append((end_coords['lat'], end_coords['lng']))

    steps.append(end)  # add ending coordinate to trip
    data = Data([
        Scattermapbox(
            lat=[item_x[0] for item_x in steps],
            lon=[item_y[1] for item_y in steps],
            mode='markers+lines',
            marker=Marker(
                size=[endpt_size] + [4 for j in range(len(steps) - 2)] + [endpt_size]
            ),
        )
    ])
    layout = Layout(
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            style='streets',
            center=dict(
                lat=np.mean([float(step[0]) for step in steps]),
                lon=np.mean([float(step[1]) for step in steps]),
            ),
            pitch=0,
            zoom=zoom
        ),
    )

    fig = dict(data=data, layout=layout)
    return fig

gmap_api_key = 'AIzaSyCpKt7PVTMeHKPOODBwS3fx3ZJneCNG_w0'

gmaps = googlemaps.Client(gmap_api_key)
address_start = '55 Parsonage Rd.'
address_end = '150th Ave and 147th St'
zoom=12.2
endpt_size=20

fig = plot_route_between_tesla_stations(address_start, address_end, zoom=12.2, endpt_size=20)
py.iplot(fig, filename='tesla-driving-directions-between-superchargers')
