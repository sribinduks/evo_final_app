"""
app.py
File that deploys the dashboard
"""
#imports
import pickle
import base64
import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.express as px
import dash_daq as daq
import json
import best_solution as bs

objectives = bs.objectives

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

capital_obj = [i.capitalize() for i in objectives]
app.layout = html.Div([
    html.Img(src =r'assets/nulogo.png', alt='image', width=200, height=110),
    html.H4('Northeastern TA Assignment',
            style={'font-size': '27px', 'textAlign': 'center', 'text-decoration': 'underline'}),

    html.Div(children=[
        html.P('Pick two different objectives below:', style={'font-style': 'italic'}),
        # select objectives to plot trade-off curves
        dcc.Dropdown(id='objective_x',
                     options=objectives, value=objectives[0], clearable=False),
        dcc.Dropdown(id='objective_y',
                     options=objectives, value=objectives[-1], clearable=False),

        # display elapsed time
        html.Div(id='time_elapsed'),
        # allow users to input time limit
        dcc.Input(
            id="run_time", type="number", placeholder="Run Time (in secs)", size='400'),

        # plot scatter plot to display trade-off
        dcc.Graph(id="scatter", style={'width': '65vw', 'height': '55vh'}),

        # set interval component so that app retrieves solutions frequently
        dcc.Interval(
            id='interval-component',
            interval=1 * 500,  # in milliseconds
            n_intervals=0
        )], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '6vw'}),


html.Div(children=[
        html.Div(id='slider-output-container'),
        # give users option to set constraints on objectives
        html.P('Move sliders to change constraint value:',
               style={'textAlign': 'center', 'font-style': 'italic'}),
        html.Div(
            [html.P(objectives[0].capitalize()), dcc.Slider(0, 50, 5, id='obj1_slider', value=50,
                                                            marks={0: '0', 10: '10', 20: '20', 30: '30', 40: '40',
                                                                   50: '50'}, updatemode='drag',
                                                            tooltip={"placement": "bottom", "always_visible": True}),
             html.P(objectives[1].capitalize()), dcc.Slider(0, 50, 5, id='obj2_slider', value=50,
                                                            marks={0: '0', 10: '10', 20: '20', 30: '30', 40: '40',
                                                                   50: '50'}, updatemode='drag',
                                                            tooltip={"placement": "bottom", "always_visible": True}),
             html.P(objectives[2].capitalize()), dcc.Slider(0, 50, 5, id='obj3_slider', value=50,
                                                            marks={0: '0', 10: '10', 20: '20', 30: '30', 40: '40',
                                                                   50: '50'}, updatemode='drag',
                                                            tooltip={"placement": "bottom", "always_visible": True}),
             html.P(objectives[3].capitalize()), dcc.Slider(0, 50, 5, id='obj4_slider', value=50,
                                                            marks={0: '0', 10: '10', 20: '20', 30: '30', 40: '40',
                                                                   50: '50'}, updatemode='drag',
                                                            tooltip={"placement": "bottom", "always_visible": True}),
             html.P(objectives[4].capitalize()), dcc.Slider(0, 50, 1, id='obj5_slider', value=50,
                                                            marks={0: '0', 10: '10', 20: '20', 30: '30', 40: '40',
                                                                   50: '50'}, updatemode='drag',
                                                            tooltip={"placement": "bottom", "always_visible": True})
             ])
    ], style={'display': 'inline-block', 'margin-left': '3vw', 'margin-right': '3vw', 'margin-top': '3vw'}),

    html.Div([
        # user input index to retrieve assignment table
        html.P('Hover over a point in the plot and input its index to retrieve the solution:',
               style={'font-style': 'italic'}),
        dcc.Input(
            id="index_num", type="number", placeholder="Index #", size='400', value=1)],
        style={'margin-left': '6vw'}),
    html.P("Assignments Table", style={'font-size': '20px', 'textAlign': 'center', 'font-weight': 'bold'}),
    # display assignments table
    html.Div(id="df_table")
])


@app.callback(
    Output("scatter", "figure"),
    Output('time_elapsed', 'children'),
    Input("objective_x", "value"),
    Input("objective_y", "value"),
    Input('interval-component', 'n_intervals')
)
def data_selector(objective_x, objective_y, n):
    '''

    :param objective_x: string with user's objective dropdown selection on x
    :param objective_y: string with user's objective dropdown selection on y
    :param n: integer representing interval number
    :return: scatterplot that allows you to hover over points, view objective scores, and elapsed time since running

    '''
    # use pickle to read solutions from solutions.dat
    result = []
    with (open("solutions.dat", "rb")) as openfile:
        while True:
            try:
                result.append(pickle.load(openfile))
            except EOFError:
                break

    # access all the objective numbers from solutions
    objective_num = list(result[0].keys())

    # copy the objectives list
    obj = objectives.copy()
    # remove whatever the users have chosen in the objectives
    obj.remove(objective_x)
    obj.remove(objective_y)

    # initiate lists for all the objective numbers
    score_x = []
    score_y = []
    score1 = []
    score2 = []
    score3 = []
    # store the solution index
    index = []

    # go through all solutions
    for ob_tu in range(len(objective_num)):
        # store the solution index
        index.append(ob_tu)
        # go through all the objectives within a solution
        for ob in range(len(objective_num[ob_tu])):
            # if the objective is the one the user chosen, store in list
            if objective_num[ob_tu][ob][0] == objective_x:
                score_x.append(objective_num[ob_tu][ob][1])
            elif objective_num[ob_tu][ob][0] == objective_y:
                score_y.append(objective_num[ob_tu][ob][1])

            # if the objective is within the one user hasn't chosen, store in list
            elif objective_num[ob_tu][ob][0] == obj[0]:
                score1.append(objective_num[ob_tu][ob][1])
            elif objective_num[ob_tu][ob][0] == obj[1]:
                score2.append(objective_num[ob_tu][ob][1])
            elif objective_num[ob_tu][ob][0] == obj[2]:
                score3.append(objective_num[ob_tu][ob][1])

    # make the lists of objective score into dataframe so that it's easier to retrieve
    lst = [score_x, score_y, score1, score2, score3, index]
    df = pd.DataFrame(lst).transpose()
    df.columns = [objective_x, objective_y, obj[0], obj[1], obj[2], 'index']

    # plot the scatter plot and add the hover objectives
    fig = px.scatter(df, x=objective_x, y=objective_y, hover_data=[obj[0], obj[1], obj[2], 'index'])
    fig.update_layout(title={
        'text': '<b>' + objective_y.capitalize() + " Vs. " + objective_x.capitalize() +'</b>',
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        xaxis_title='<b>' + objective_x.capitalize() + '</b>',
        yaxis_title='<b>' + objective_y.capitalize() + '</b>',
        hoverlabel=dict(bgcolor="DarkBlue", font_size=12, font_family="Times"))

    # add time elapsed to dash from time_elapsed file
    with open('elapsed.json', 'r') as f:
        elapsed_time = json.load(f)
    elapsed_time = list(elapsed_time.items())
    elapsed = elapsed_time[0][1]
    return fig, 'Elapsed Time: {}'.format(elapsed)


@app.callback(
    Output('slider-output-container', 'children'),
    Input('run_time', 'value'),
    Input('obj1_slider', 'value'),
    Input('obj2_slider', 'value'),
    Input('obj3_slider', 'value'),
    Input('obj4_slider', 'value'),
    Input('obj5_slider', 'value')
)
def constraint_control(run_time, obj1_slider, obj2_slider, obj3_slider, obj4_slider, obj5_slider):
    '''
    :param run_time: integer expected run time from user
    :param obj1_slider: integer of objective 1 constraint value
    :param obj2_slider: integer of objective 2 constraint value
    :param obj3_slider: integer of objective 3 constraint value
    :param obj4_slider: integer of objective 4 constraint value
    :param obj5_slider: integer of objective 5 constraint value
    sliders that allow you to change the constraints in json file
    '''
    constraints_dict = {objectives[0]: obj1_slider, objectives[1]: obj2_slider, objectives[2]: obj3_slider,
                        objectives[3]: obj4_slider, objectives[4]: obj5_slider}

    # Serializing json
    json_object = json.dumps(constraints_dict)

    # Writing to constraints file
    with open("constraints.json", "w") as outfile:
        outfile.write(json_object)

    # create input item
    time_input = {}
    time_input["time"] = run_time

    # Serializing json
    json_object = json.dumps(time_input)

    # Writing to time_limit file
    with open("time_limit.json", "w") as file:
        file.write(json_object)


@app.callback(
    Output('df_table', 'children'),
    Input('index_num', 'value')
)
def display_table(index_num):
    '''
    :param index_num: integer of user input index
    :return: data table of TA assignments based on that index
    '''

    # creates data frame and list of column names
    df = bs.return_df(index_num)
    columns = [{'name': str(col), 'id': '_'.join(str(col))} for col in df.columns]

    data = [{"_".join(str(col)): val for col, val in row.items()} for row in df.to_dict('records')]

    # creates dash table with specified style parameters
    return dash_table.DataTable(data=data, columns=columns, fixed_rows={'headers': True},
                                style_table={'minWidth': '70%'},
                                style_cell={'textAlign': 'center', 'minWidth': 70, 'maxWidth': 70, 'width': 70,
                                            'font_size': '12px', 'whiteSpace': 'normal', 'height': 'auto'},
                                export_format="xlsx")


app.run_server(debug=True)