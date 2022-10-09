from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as pd
import ast
import requests, zipfile, io
from os import path

app = Flask(__name__)
api = Api(app)

# Logic to calculate the revenue and budget for a given production company id
# and year from cached csv file
# TODO: add type checking for inputs
def budget_and_rev(prod_comp_id, year):
    def clean(year):
        if year and type("string") == type(year):
            return year.split("-")[0]
    meta = pd.read_csv('movies_metadata.csv')
    meta['release_date'] = meta['release_date'].apply(clean)
    filtered_by_year = meta.loc[meta['release_date'] == year]

    revenue = 0
    budget = 0

    # add up the revenue and budget for each production
    for i in range(len(filtered_by_year['production_companies'])):
        row = filtered_by_year[['production_companies', 'revenue', 'budget']].iloc[i]
        lst = ast.literal_eval(row['production_companies'])
        for pc in lst:
            if pc["id"] == prod_comp_id:
                revenue += int(row['revenue'])
                budget += int(row['budget'])

    return (revenue, budget)

# If there is no cached csv (called movies_metadata.csv), download the csv from the s3 bucket provided.
# Even though we only extract one csv, this takes 30 seconds to a minute
def get_csv():
    if path.exists("movies_metadata.csv"):
        return
    URL = "https://s3-us-west-2.amazonaws.com/com.guild.us-west-2.public-data/project-data/the-movies-dataset.zip"

    r = requests.get(url = URL, stream=True)

    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extract('movies_metadata.csv')

# TODO: more error handling, checking that inputs are valid and safe
# Endpoint to calculate the revenue and budget for a company in a given year
class ProductionCompany(Resource):
    def get(self):
        get_csv()

        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('production_id', required=True)  # add args
        parser.add_argument('year', required=True)
        args = parser.parse_args()  # parse arguments to dictionary

        revenue, budget = budget_and_rev(int(args['production_id']), args['year'])

        data = {}
        data['revenue'] = revenue
        data['budget'] = budget

        return {'data': data}, 200  # return data and 200 OK

# Logic to calculate the most popular genre in a year by summing up the popularity
# scores for each movie in a genre
def most_pop_genre(year):
    def clean(year):
        if year and type("string") == type(year):
            return year.split("-")[0]
    meta = pd.read_csv('movies_metadata.csv')
    meta['release_date'] = meta['release_date'].apply(clean)
    filtered_by_year = meta.loc[meta['release_date'] == year]

    # dict of genre to popularity
    popularity = dict()

    #calculate popularity for all genres
    for i in range(len(filtered_by_year['production_companies'])):
        row = filtered_by_year[['genres', 'popularity']].iloc[i]
        genre = row["genres"]
        lst = ast.literal_eval(genre)
        for pc in lst:
            popularity[pc['name']] = popularity.get(pc['name'], 0) + float(row['popularity'])

    max_count = 0
    mp_genre = None
    for genre in popularity.keys():
        if popularity[genre] > max_count:
            mp_genre = genre
            max_counnt = popularity[genre]

    return mp_genre


# TODO: more error handling, checking that inputs are valid and safe
# Endpoint to calculate the most popular genre
class Genre(Resource):
    def get(self):
        get_csv()

        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('year', required=True)
        args = parser.parse_args()  # parse arguments to dictionary

        genre = most_pop_genre(args['year'])

        data = {}
        data['genre'] = genre

        return {'data': data}, 200  # return data and 200 OK


api.add_resource(ProductionCompany, '/production_company')  # add endpoints
api.add_resource(Genre, '/genre')

if __name__ == '__main__':
    app.run(debug=True)  # run our Flask app
