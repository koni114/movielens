import datetime as dt

import json
import os

import pandas as pd
import requests

from airflow import DAG
from airflow.operators.python import PythonOperator

import pyupbit

with DAG(
        dag_id="bitcoin_dag",
        description="get bitcoin data from the pyupbit API using the Python Operator.",
        start_date=dt.datetime(2022, 7, 16),
        end_date=dt.datetime(2022, 7, 31),
        schedule_interval="@daily",
) as dag:

    def _get_upbit_data(ticker="KRW-BTC", count=288, interval="minute5"):
        """
            upbit api 를 활용하여 해당 티커의 시가/고가/저가/종가/거래량 데이터 추출
            날짜가 오름차순으로 정렬돼 최근 날짜가 마지막에 위치
        :param ticker:
            ex) KRW-BTC
        :param count:
            데이터 행 개수를 의미함
        :param interval:
            day/minute1/minute3/minute5/minute10/minute15/minute30/minute60/minute240/week/month
        :return:
            티커의 시가/고가/저가/종가/거래량 dataFrame
        """
        df = pyupbit.get_ohlcv(ticker, count=count, interval=interval)
        return df

    get_upbit_data = PythonOperator(
        task_id="get_upbit_data",
        python_callable=_get_upbit_data,
    )






24 * 60 / 5