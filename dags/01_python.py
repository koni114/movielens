import datetime as dt
import logging
import json
import os

import pandas as pd
import requests

from airflow import DAG
from airflow.operators.python import PythonOperator

from custom.ranking import rank_movie_by_rating

MOVIELENS_HOST = os.environ.get("MOVIELENS_HOST", "movielens")
MOVIELENS_SCHEMA = os.environ.get("MOVIELENS_SCHEMA", "http")
MOVIELENS_PORT = os.environ.get("MOVIELENS_PORT", "5000")

MOVIELENS_USER = os.environ.get("MOVIELENS_USERS", "airflow")
MOVIELENS_PASSWORD = os.environ.get("MOVIELENS_PASSWORD", "airflow")


def _get_ratings(start_date, end_date, batch_size=100):
    session, base_url = _get_session()

    yield from _get_with_pagination(
        session=session,
        url=base_url + "/ratings",
        params={"start_date": start_date, "end_date": end_date},
        batch_size=batch_size,
    )


def _get_session():
    session = requests.Session()
    session.auth = (MOVIELENS_USER, MOVIELENS_PASSWORD)

    # Define API base url from connection details.
    schema = MOVIELENS_SCHEMA
    host = MOVIELENS_HOST
    port = MOVIELENS_PORT

    base_url = f"{schema}://{host}:{port}"
    return session, base_url


def _get_with_pagination(session, url, params, batch_size=100):
    offset = 0
    total = None
    while total is None or offset < total:
        response = session.get(
            url, params={**params, **{"offset": offset, "limit": batch_size}}
        )
        response.raise_for_status()  # 쿼리의 정상 수행 여부 check
        # 쿼리의 결과는 content 속성에서 가져오거나, json 메서드를 사용할 수 있음
        response_json = response.json()

        yield from response_json["result"]

        offset += batch_size
        total = response_json["total"]


with DAG(
    dag_id="01_python",
    description="Fetches ratings from the Movielens API using the Python Operator.",
    start_date=dt.datetime(2022, 1, 1),
    end_date=dt.datetime(2019, 1, 10),
    schedule_interval="@daily",
) as dag:

    def _fetch_ratings(templates_dict, batch_size=1000, **_):
        """
            start_date < -- > end_date 사이의 영화 평점 데이터를
            output_path 에 저장하는 함수

        :param templates_dict: context dictionary
        :param batch_size:     데이터를 한 번에 fetch 할 데이터 크기
        :param _:
        """
        logger = logging.getLogger(__name__)

        start_date = templates_dict["start_date"]
        end_date = templates_dict["end_date"]
        output_path = templates_dict["output_path"]

        logger.info(f"Fetching ratings for {start_date} to {end_date}")
        ratings = list(
            _get_ratings(
                start_date=start_date, end_date=end_date, batch_size=batch_size
            )
        )

        logger.info(f"Fetched {len(ratings)} ratings")
        logger.info(f"Writing ratings to {output_path}")

        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)

        with open(output_path, "w") as file_:
            json.dump(ratings, fp=file_)

    fetch_ratings = PythonOperator(
        task_id="fetch_ratings",
        python_callable=_fetch_ratings,
        templates_dict={
            "start_date": "{{ds}}",
            "end_date": "{{next_ds}}",
            "output_path": "/data/python/ratings/{{ds}}.json",
        },
    )

    def _rank_movies(templates_dict, min_ratings=2, **_):
        input_path = templates_dict["input_path"]
        output_path = templates_dict["output_path"]

        ratings = pd.read_json(input_path)
        ranking = rank_movie_by_rating(ratings, min_ratings=min_ratings)

        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)

        ranking.to_csv(output_path, index=True)

    rank_movies = PythonOperator(
        task_id="rank_movies",
        python_callable=_rank_movies,
        templates_dict={
            "input_path": "/data/python/ratings/{{ds}}.json",
            "output_path": "/data/python/ratings/{{ds}}.csv",
        },
    )

    fetch_ratings >> rank_movies
