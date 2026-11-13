# -*- coding: utf-8 -*-
# Converted from cities_reddit_colllection.ipynb.
# Project role: original macro-level workflow
# This standalone source contains the notebook code cells in order.
# Jupyter-only directives are retained as comments for provenance.

# --- code cell 1 ---
import pandas as pd
from google.colab import auth
from google.colab import files
from tqdm import tqdm_notebook
auth.authenticate_user()
print('Authenticated')

# --- code cell 2 ---
with open("/content/cities.txt","r") as f:
    lines = f.readlines()

cities = [line.strip() for line in lines]
subreddits = ['nyc', 'LosAngeles', 'chicago', 'Dallas', 'houston', 'washingtondc', 'Miami', 'philadelphia', 'Atlanta', 'phoenix', 'boston', 'sanfrancisco', 'Riverside', 'Detroit', 'Seattle', 'Minneapolis', 'sandiego', 'tampa', 'Denver', 'StLouis', 'baltimore', 'Charlotte', 'orlando', 'sanantonio', 'Portland', 'Sacramento', 'pittsburgh', 'LasVegas', 'Austin', 'cincinnati', 'kansascity', 'Columbus', 'indianapolis', 'Cleveland', 'SanJose', 'nashville', 'VirginiaBeach', 'providence', 'milwaukee', 'jacksonville', 'oklahomacity', 'raleigh', 'richmond', 'NewOrleans', 'Louisville', 'SaltLakeCity', 'Hartford', 'Buffalo', 'Birmingham']

dates=[]
for i in range(1,13):
    # Include the full 2015--2019 window described in the manuscript.
    for year in range(5,10):
        month = '0{}'.format(i)[-2:]
        dates.append('201{}_{}'.format(year, month))

# --- code cell 3 ---
from google.cloud import bigquery

# Construct a BigQuery client object.
client = bigquery.Client(project='YOUR_GCP_PROJECT')

for city_idx in tqdm_notebook(range(len(cities))):
    bodies = []
    subrs = []
    authors = []
    created = []

    for date in dates:
        query = """
                SELECT body,subreddit,author,created_utc 
                FROM `fh-bigquery.reddit_comments.{}` 
                WHERE (body LIKE @string OR body LIKE @string2) AND (subreddit = @subreddit)
                """.format(date)

        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("string", "STRING", '%{}%'.format(cities[city_idx])),
                              bigquery.ScalarQueryParameter("string2", "STRING", '%{}%'.format(cities[city_idx].lower())),
                              bigquery.ScalarQueryParameter("subreddit", "STRING", subreddits[city_idx]),])
        query_job = client.query(query, job_config=job_config)  # Make an API request.

        for row in query_job:
            bodies.append(row.body)
            subrs.append(row.subreddit)
            authors.append(row.author)
            created.append(row.created_utc)
    
    print("Collect {} comments from r/{}".format(len(bodies),subreddits[city_idx]))
    df = pd.DataFrame({'body':bodies,'subreddit':subrs,'author':authors,'created_utc':created})
    # Make the city cap explicit and deterministic for future re-extraction.
    # The archived aspect arrays used in the reported regressions are not
    # silently replaced by this corrected extraction path.
    df = df.drop_duplicates(subset=['body','subreddit','author','created_utc'])
    df = df.sort_values(['created_utc','subreddit','author','body'], kind='mergesort', na_position='last').head(50000)
    df.to_csv('{}.csv'.format(cities[city_idx]),header=1)
