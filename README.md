# movies_api

This project is an api that connects to the kaggle movies dataset (https://www.kaggle.com/rounakbanik/the-movies-dataset) using the url
https://s3-us-west-2.amazonaws.com/com.guild.us-west-2.public-data/project-data/the-movies-dataset.zip.
It uses the Flask API framework and pandas to process csv files.

See email for ERD

Dependencies:
python3
pip to install dependencies
flask, flask_restful, pandas, ast, requests, zipfile, io, os

To run, navigate to the folder containing this director and run "python flask_api.py" in the command line.
Then, use curl to make requests.
NOTE: The first time you run a curl request, the app will fetch the dataset csv file. This can take up to a minute since it's a large file. After the first request, it is cached locally even after the session ends.

Endpoint #1: Enter the id for a movie production company and a year, and endpoint will return the total budget and revenue for that company for that year

example command: curl --header "Content-Type: application/json" -d '{"production_id":"3", "year":"2010"}' -X GET http://127.0.0.1:5000/production_company

Endpoint #2: Enter the year, and endpoint will return the most popular genre in a year by summing up the popularities of each movie
curl --header "Content-Type: application/json" -d '{"year":"2010"}' -X GET http://127.0.0.1:5000/genre


Further improvements include: creating a pipenv and lock file to manage dependencies easily.
I'm not sure I calculated popularity correctly, as the docs were unclear on the definition of the popularity column
Downloading the csv file is really slow. Caching the csv file helps, but I'm not fetching the csv file again when I run the app again in case there's any changed, and I don't delete the csv file when the app shuts down.
I tried using boto3 (a python module that lets provides functionality to innteract with web3 buckets), which could have been faster, but I couldn't get it working.
Ideally, I would do the database searching on the server that contains the csv files so I don't have to download them.
In a production environment, I would add a lot more type checking and error handling, especially if the csv files were going to have new values added that I don't know the format of. Or, if a malicious actor can modify the database.
