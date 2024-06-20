# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
print(max_payload)

options=[{'label': 'All Sites', 'value': 'ALL'}] + \
        [{'label': site, 'value': site} for site in spacex_df["Launch Site"].unique()]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown', options=options, value='ALL',
                                placeholder="Select a Launch Site", searchable=True),
                                
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider', 
                                                min=0, max=10000, step=1000,
                                                marks={num: str(num) for num in range(0, 11000, 1000)},
                                                value=[0, 10000]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))      
def get_pie_chart(entered_site):
    filtered_df = spacex_df.groupby("Launch Site")["class"].sum().reset_index()
    if entered_site == 'ALL':
        fig = px.pie(filtered_df, values='class', 
        names='Launch Site', 
        title='Successful Launches by Launch Site')
        return fig
    else:
        site_df = spacex_df.groupby("class")["Launch Site"].value_counts().reset_index()
        labels = {0:'Fail', 1:'Success'}
        site_df['class'] = site_df['class'].map(labels) 
        site_df = site_df[site_df["Launch Site"] == entered_site]
        fig = px.pie(site_df, values='count', 
        names='class',
        title= 'Successful Launch Rate at ' + entered_site)
        return fig
        # return the outcomes piechart for a selected site

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
              Input(component_id='payload-slider', component_property='value')])      
def get_scatter_plot(entered_site, payload):
    payload_min, payload_max = payload[0], payload[1]
    range_df = spacex_df[(spacex_df['Payload Mass (kg)'] > payload_min) & (spacex_df['Payload Mass (kg)'] < payload_max)]
    if entered_site == 'ALL':
        fig = px.scatter(range_df, x='Payload Mass (kg)', y='class', 
        color="Booster Version Category", 
        title='Correlation Between Success and Payload at all site')
        return fig
    else:
        filtered_df = range_df[range_df['Launch Site']==entered_site]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', 
        color="Booster Version Category", 
        title='Correlation Between Success and Payload at ' + entered_site)
        return fig

        # return the outcomes piechart for a selected site
# Run the app
if __name__ == '__main__':
    app.run_server()
