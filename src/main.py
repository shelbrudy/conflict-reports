import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import os
import pandas as pd
import plotly.graph_objs as go
import plotly.plotly as py


mapbox_access_token = os.environ['MAPBOX_KEY']

app = dash.Dash(__name__)

server = app.server

full_df = pd.read_csv('../data/africa_data.csv')

violent_events = ['Explosions/Remote violence', 'Battles', 'Violence against civilians', 'All']

congo = full_df.loc[(full_df['event_type'].isin(violent_events))]

congo_yearly_dfs = {year:congo.loc[congo['year'] == year] for year in congo['year'].unique()}

congo_event_dfs = {event_type:congo.loc[congo['event_type'] == event_type] for event_type in congo['event_type'].unique()}


event_types = {'Explosions/Remote violence': "#FFAA00", 'Battles': "#F2B134", 'Violence against civilians': "#ED553B", 'All': "#75E4B3"}

colors = {
    'header': '#318BA3',
    'text': '#33CFA5',
    'background': '#454545'}

layout = go.Layout(
    height = 600,
    margin = dict( t=0, b=0, l=0, r=0 ),
    showlegend=False,
    mapbox=go.layout.Mapbox(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=go.layout.mapbox.Center(
            lat=5,
            lon=24
        ),
        pitch=0,
        zoom=2.25,
        style='light'
    ),
)

updatemenus = list([dict(active=-1, buttons=list(), pad = {'r': 0, 't': 8},
                         x = 0.05,
                         xanchor = 'left',
                         y = 1.0,
                         yanchor = 'top',
                         bgcolor = '#AAAAAA',
                         bordercolor = '#FFFFFF',
                         font = dict(size=11, color='#000000'))])

updatemenus.append(dict(
                        buttons=list([
                            dict(
                                args=['mapbox.style', 'light'],
                                label='Light',
                                method='relayout'
                            ),                    
                            dict(
                                args=['mapbox.style', 'dark'],
                                label='Dark',
                                method='relayout'
                            ),
                            dict(
                                args=['mapbox.style', 'satellite'],
                                label='Satellite',
                                method='relayout'
                            ),
                            dict(
                                args=['mapbox.style', 'satellite-streets'],
                                label='Satellite with Streets',
                                method='relayout'
                            )                    
                        ]),
                        direction = 'up',
                        x = 0.70,
                        xanchor = 'left',
                        y = 0.04,
                        yanchor = 'bottom',
                        bgcolor = '#A6A6A6',
                        bordercolor = '#FFFFFF',
                        font = dict(size=11)
                    ))


layout['updatemenus'] = updatemenus

app.layout = html.Div(
    children=[
    html.Div(
        className="app-header",
        children=[
            html.H1('Conflict in Africa', className="app-header--title")
        ]
    ),
    html.Div(
        children=html.Div([
            html.H2('Motivation'),
            html.Div('''
                This project was built to help learn Dash and Plotly,
                in addition to visualizing conflict in Africa.
            ''')
        ])
    ),
    html.Div(
        children=html.Div([
            html.H2('Source Data'),
            html.Div('''
                Data sourced by ACLED.
            ''')
        ])
    ),

    html.Div([
        html.Div([
                dcc.Dropdown(
                    id='country-year',
                    options=[{'label': i, 'value': i} for i in congo['year'].unique()],
                    value='2018',
                    clearable=False
                )
            ],
            style={'width': '30%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='country-event-type',
                options=[{'label': i, 'value': i} for i in violent_events],
                value='Battles',
                clearable=False
            )
        ],style={'width': '30%', 'float': 'left', 'display': 'inline-block'})
    ]),

    html.Div([
        html.Div([
                    dcc.Graph(
                        id='congo-yearly',
                        config=({'scrollZoom': True})
                    ),
            ],
            style={'width': '60%', 'display': 'inline-block'}),

        html.Div([
            html.H2(id='my-div')
        ],style={'width': '30%', 'float': 'right', 'display': 'inline-block'})
    ]),
])

app.title='CONFLICT REPORTS'

@app.callback(
    [Output('congo-yearly', 'figure'),
     Output('my-div', component_property='children')],
    [Input('country-year', 'value'),
     Input('country-event-type', 'value')])
def update_map(country_year, country_event_type):
    if country_event_type == 'All':
        df = congo.loc[(congo['year'] == country_year)]
        traces = [go.Scattermapbox(
                            lat=congo_event_dfs[event]['latitude'],
                            lon=congo_event_dfs[event]['longitude'],
                            mode='markers',
                            name = str(event),
                            marker=go.scattermapbox.Marker(
                                size=4,
                                color=event_types[event].lower()
                        ),
                            text=congo_event_dfs[event]['sub_event_type'],
                        ) for event in df['event_type'].unique()
                ]
    else:
        df = congo.loc[(congo['year'] == country_year) & (congo['event_type'] == country_event_type)]
        traces = [go.Scattermapbox(
                            lat=df['latitude'],
                            lon=df['longitude'],
                            mode='markers',
                            name = str(country_year),
                            marker=go.scattermapbox.Marker(
                                size=4,
                                color=event_types[country_event_type].lower()
                        ),
                            text=df['sub_event_type'],
                        )
                ]


    return {
        'data': traces,
        'layout': layout
    }, 'Fatalities: {}'.format(df['fatalities'].sum())


if __name__ == '__main__':
    app.run_server(debug=False)


