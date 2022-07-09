import datetime as dt
import logging
import os
import json

from airflow import DAG
from custom.hooks import MovielensHook
from airflow.operators.python import PythonOperator


with DAG(
    dag_id="02_hook",
    description="",
    start_date=dt.datetime(2019, 1, 1),
    end_date=dt.datetime(2019, 1, 3),
    schedule_interval="@daily",
) as dag:

    def _fetch_ratings(conn_id, template_dict, batch_size=100, **_):

        logger = logging.getLogger(__name__)

        start_date = template_dict["start_date"]
        end_date = template_dict["end_date"]
        output_path = template_dict["output_path"]

        hook = MovielensHook(conn_id=conn_id)
        ratings = hook.get_ratings(
                start_date=start_date,
                end_date=end_date,
                batch_size=batch_size
        )

        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)

        with open(output_path, "w") as file_:
            json.dump(ratings, fp=file_)


    PythonOperator(
        task_id="fetch_ratings",
        python_callable=_fetch_ratings,
        templates_dict={
            "start_date": "{{ds}}",
            "end_date": "{{next_ds}}",
            "output_path": "/data/custom_hook/{{ds}}.json",
        },
    )
