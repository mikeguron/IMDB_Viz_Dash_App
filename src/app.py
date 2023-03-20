from dash import Dash, html, dcc, Input, Output
import altair as alt
from vega_datasets import data
import dash_bootstrap_components as dbc
import pandas as pd 
import numpy as np

# Data Reading, Cleaning, and Wrangling
movies = pd.read_csv("../data/imdb_top_1000.csv", dtype={'Runtime': str})
movies['Runtime'] = movies['Runtime'].str.extract('(\d+)').astype(int)
movies = movies.loc[:,['Series_Title', 'Director', 'Certificate', 'Runtime', 'IMDB_Rating', 'Meta_score', 'No_of_Votes', 'Gross']]
movies = movies.dropna()
movies['Gross Revenue ($USD)'] = pd.to_numeric(movies['Gross'].str.replace(',', ''))
movies.drop('Gross', axis=1, inplace=True)
movies.rename(columns={'Series_Title': 'Movie Title',
                       'Runtime': 'Runtime (min)',
                       'IMDB_Rating': 'IMDB Rating',
                       'Meta_Score': 'Meta Score',
                       'No_of_Votes': 'Number of Votes'},
                       inplace=True)
certificates = movies['Certificate'].unique()
directors = movies['Director'].unique()

# Creating app layout/frontend
app = Dash(external_stylesheets=[dbc.themes.SLATE])
server = app.server

app.layout = dbc.Container([
    html.H1('IMDB Top 1000 Exploration Dashboard'),
    dbc.Row([
        html.Label('Select A Director:'),
            dcc.Dropdown(
                id='director1',
                value='Christopher Nolan',  
                options=[{'label': dir1, 'value': dir1} for dir1 in directors]),
        html.Label('Select the Metric:'),
            dcc.Dropdown(
                id='metric1',
                value='Runtime (min)',  
                options=[{'label': met1, 'value': met1} for met1 in movies.columns[3:8]])]),
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody(
                    html.Iframe(id='boxplot_director',
                                style={'border-width': '0', 'width': '100%', 'height': '250px'})
                )
            ])
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardBody(
                    html.Iframe(id='top3_director',
                                style={'border-width': '0', 'width': '100%', 'height': '250px'})
                )
            ])
        )
    ]),
    dbc.Row([
        html.Label('Select A Certificate:'),
            dcc.Dropdown(
                id='certificate1',
                value='G',  
                options=[{'label': cert, 'value': cert} for cert in certificates]),
        html.Label('Select The Metric:'),
            dcc.Dropdown(
                id='metric2',
                value='IMDB Rating',  
                options=[{'label': met2, 'value': met2} for met2 in movies.columns[3:8]])]),
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody(
                    html.Iframe(id='boxplot_certificate',
                                style={'border-width': '0', 'width': '100%', 'height': '250px'})
                )
            ])
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardBody(
                    html.Iframe(id='top3_certificate',
                                style={'border-width': '0', 'width': '100%', 'height': '250px'})
                )
            ])
        )
    ]),
])

# Creating app callbacks/backend
@app.callback(
    Output('boxplot_director', 'srcDoc'),
    Input('director1', 'value'),
    Input('metric1', 'value')
    )

def plot_director(director1, metric1):
    movies_dir = movies.query("Director == @director1")
    padding_amt = (movies_dir[metric1].max() - movies_dir[metric1].min())/10
    xmin = movies_dir[metric1].min() - padding_amt
    xmax = movies_dir[metric1].max() + padding_amt
    boxplot_director = alt.Chart(movies_dir, width=400, height=100).mark_boxplot(clip=True).encode(
        x=alt.X(metric1, scale=alt.Scale(domain=[xmin, xmax])),
        y='Director',
    ).properties(title = 'Boxplot of ' + metric1 + ' for ' + director1 + "'s Movies")
    output = boxplot_director + boxplot_director.mark_point(size = 7)
    return output.to_html()

@app.callback(
    Output('top3_director', 'srcDoc'),
    Input('director1', 'value'),
    Input('metric1', 'value')
    )
def plot_top3_director(director1, metric1):
    movies_dir = movies.query("Director == @director1")
    movies_dir = movies_dir.sort_values(by=[metric1], ascending=False)
    movies_dir = movies_dir.head(3)

    top3_directors = alt.Chart(movies_dir, width=400, height=100).mark_bar().encode(
        x=metric1,
        y=alt.Y('Movie Title', sort='-x'),
        tooltip=metric1,
    ).properties(title = director1 + "'s Top 3 Movies by " + metric1)
    output = top3_directors
    return output.to_html()

@app.callback(
    Output('boxplot_certificate', 'srcDoc'),
    Input('certificate1', 'value'),
    Input('metric2', 'value')
    )

def plot_certificate(certificate1, metric2):
    movies_cert = movies.query("Certificate == @certificate1")
    padding_amt = (movies_cert[metric2].max() - movies_cert[metric2].min())/10
    xmin = movies_cert[metric2].min() - padding_amt
    xmax = movies_cert[metric2].max() + padding_amt

    boxplot_certificate = alt.Chart(movies_cert, width=400, height=100).mark_boxplot(clip=True).encode(
        x=alt.X(metric2, scale=alt.Scale(domain=[xmin, xmax])),
        y='Certificate',
    ).properties(title = 'Boxplot of ' + metric2 + ' for ' + certificate1 + '-Rated Movies')
    output = boxplot_certificate + boxplot_certificate.mark_point(size = 7)
    return output.to_html()

@app.callback(
    Output('top3_certificate', 'srcDoc'),
    Input('certificate1', 'value'),
    Input('metric2', 'value')
    )
def plot_top3_certificate(certificate1, metric2):
    movies_cert = movies.query("Certificate == @certificate1")
    movies_cert = movies_cert.sort_values(by=[metric2], ascending=False)
    movies_cert = movies_cert.head(3)

    top3_certificate = alt.Chart(movies_cert, width=400, height=100).mark_bar().encode(
        x=metric2,
        y=alt.Y('Movie Title', sort='-x'),
        tooltip=metric2,
    ).properties(title = 'Top 3 ' + certificate1 + '-Rated Movies by ' + metric2)
    output = top3_certificate
    return output.to_html()

if __name__ == '__main__':
    app.run_server(debug=True)

