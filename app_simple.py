# -*- coding: utf-8 -*-
import os
import pandas as pd
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from user_definition import *

bike_df = pd.read_csv(os.path.join('data', 'fordgobike-tripdata.csv'))

start_stations_locations = bike_df[['start_station_name', 'start_station_id', 'start_station_longitude', 'start_station_latitude']].drop_duplicates()
start_stations_locations.columns = ['start_station_name', 'start_station_id', 'long', 'lat']
dow_dict = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
month_dict = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
              7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Dropdown(
            id='year--dropdown',
            options=[{'label': str(year), 'value': year} for year in bike_df['year'].unique()],
            value=2019
            ),
            dcc.Dropdown(
            id='month--dropdown',
            options=[{'label': str(month_dict[month]), 'value': month} for month in bike_df['month'].unique()],
            value=4
            )
        ], style= {'width': '10%', 'display': 'inline-block', 'vertical-align': 'top'}),
        html.Div([
            dcc.Graph(id='map-graph'),
            dcc.Slider(
                id='day--slider',
                min=bike_df['dayofmonth'].min(),
                max=bike_df['dayofmonth'].max(),
                value=bike_df['dayofmonth'].min(),
                marks={str(day): str(day) for day in bike_df['dayofmonth'].unique()}
            )
        # dcc.Graph(id='bar-chart')
        ], style={'width': '89%', 'display': 'inline-block'})
    ])
])

@app.callback(Output('map-graph', 'figure'),
              [Input('day--slider', 'value'),
               Input('month--dropdown', 'value'),
               Input('year--dropdown', 'value')])
            #   [Input('dow--slider', 'value'), Input('month--slider', 'value')])
def update_map(day_value, month_value, year_value):
    bike_df_filtered = bike_df[(bike_df['dayofmonth'] == day_value) & (bike_df['month'] == month_value) & (bike_df['year'] == year_value)]
    bike_df_filtered = bike_df_filtered.groupby(['start_station_name', 'start_station_longitude',
                                                 'start_station_latitude']).count().iloc[:, [0]].reset_index()
    bike_df_filtered.columns = ['start_station_name', 'lon', 'lat', 'count']
    bike_df_filtered['text'] = bike_df_filtered['start_station_name'] + '<br>Number of trips: ' + \
                            (bike_df_filtered['count']).astype(str)
    
    return {
        'data': [
            go.Scattermapbox(
                lat=bike_df_filtered['lat'],
                lon=bike_df_filtered['lon'],
                mode='markers',
                marker=go.Marker(size=bike_df_filtered['count']/10),
                text=bike_df_filtered['text'],
                hoverinfo='text'
            )
        ],
        'layout': go.Layout(
            title='SF Bike Share Station Popularity',
            autosize=True,
            hovermode='closest',
            showlegend=False,
            height=700,
            mapbox={'accesstoken': mapbox_access_token,
                    'bearing': 0,
                    'center': {'lat': start_stations_locations['lat'].mean(),
                               'lon': start_stations_locations['long'].mean()},
                    'pitch': 0, 
                    'zoom': 12,
                    'style': 'dark'}
        )
    }

# @app.callback(Output('bar-chart', 'figure'),
            #   [Input('map-graph', 'hoverData'), Input('dayofweek', 'value')])
# def update_barchart(hoverData, dow_value):
#     bike_df_filtered = bike_df[bike_df['day'] == int(dow_value)]
#     count_by_location_hour = bike_df_filtered.groupby(['start_station_id', 'start_station_name', 'hour']).count().iloc[:,[0]]
#     count_by_location_hour.columns = ['count']
#     count_by_location_hour.reset_index(inplace=True)
#     print(count_by_location_hour.info())
#     filtered_df = count_by_location_hour[count_by_location_hour['start_station_name'] == selected_location]
#     return {
#         'data': [go.Bar(
#             x=filtered_df['hour'],
#             y=filtered_df['count'],
#             marker={

#             }
#         )],
#         'layout': go.Layout(
#             xaxis={'title': 'Hour', 'dtick': 1},
#             yaxis={'title': 'Number of Bikes'},
#             hovermode='closest'
#         )
#     }


# @app.callback(Output('map-graph', 'figure'),
#               [Input('map-graph', 'hoverData')],
#               [State('map-graph', 'figure')])
# def update_map(hoverData, figure):
#     selected_location = hoverData['points'][0]['text']
#     traces = figure['data']
#     layout = figure['layout']
#     highlighted_point = go.Scattermapbox(
#                 lat=start_stations_locations[start_stations_locations['start_station_name']==selected_location]['lat'],
#                 lon=start_stations_locations[start_stations_locations['start_station_name']==selected_location]['long'],
#                 mode='markers',
#                 marker=go.Marker(size=10, color='red'),
#                 text=selected_location,
#                 hoverinfo='text'
#             )
#     traces.extend(highlighted_point)
#     return {'data': traces, 'layout': layout}

if __name__ == '__main__':
    app.run_server(debug=True)