#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from sqlalchemy import create_engine
from time import  time
import argparse
import os

def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url
    csv_name = 'output.csv'

    # if url.endswith('.csv.gz'):
    #     csv_name = 'output.csv.gz'
    # else:
    #     csv_name = 'output.csv'

    os.system(f"wget {url} -O {csv_name}")

    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000, compression='gzip')
    df = next(df_iter)

    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    df.head(0).to_sql(name=table_name, con=engine, if_exists='replace')

    df.to_sql(name=table_name, con=engine, if_exists='append')

    # Iterate through the dataset chunk by chunk
    for chunk_number, df in enumerate(df_iter, start=1):
        time_start = time()

        # Convert datetime columns to the correct format
        df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
        df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])

        # Insert the chunk into the SQL table
        df.to_sql(name=table_name, con=engine, if_exists='append')

        time_end = time()

        print(f'Inserted chunk {chunk_number}, took {time_end - time_start:.3f} seconds')

    print("All data has been processed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')

    parser.add_argument('--user', help='username for postgres')
    parser.add_argument('--password', help='password for postgres')
    parser.add_argument('--host', help='host for postgres')
    parser.add_argument('--port', help='port for postgres')
    parser.add_argument('--db', help='database name for postgres')
    parser.add_argument('--table_name', help='table name where results will be written to')
    parser.add_argument('--url', help='url of the csv file')

    args = parser.parse_args()

    main(args)
