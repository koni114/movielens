import os
import time

import pandas as pd

from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

DEFAULT_ITEMS_PER_PAGE = 100


def _read_ratings(file_path):
    ratings_df = pd.read_csv(file_path)

    # subsample dataset
    ratings_df = ratings_df.sort_values(by=["timestamp", "userId", "movieId"])
    return ratings_df


app = Flask(__name__)
app.config["ratings"] = _read_ratings("/ratings.csv")

auth = HTTPBasicAuth()
users = {os.environ["API_USER"]: generate_password_hash(os.environ["API_PASSWORD"])}


@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False


@app.route("/")
def hello():
    return "Hello from the Movie Rating API!"


@app.route("/ratings")
@auth.login_required
def ratings():
    """
        인증 화면에서 Username, Password 입력.
        평점 API 의 엔드포인트에서 제공하는 평점 데이터.
        만약 특정 기간 동안 평점 데이터를 가져오려면 start_date 와 end_date 파라미터를 사용
    :example:
        http://localhost:5000/ratings?offset=100
        http://localhost:5000/ratings?limit=1000
        http://localhost:5000/ratings?start_date=2019-01-01&end_date=2019-01-02
    :return:
        json format
        평점데이터 -> Result, 시작 부분 -> offset, 한 번에 가져올 수 있는 레코드 수 -> limit
    """
    start_date_ds = _date_to_timestamp(request.args.get("start_date", None))
    end_date_ds = _date_to_timestamp(request.args.get("end_date", None))

    offset = int(request.args.get("offset", 0))
    limit = int(request.args.get("limit", DEFAULT_ITEMS_PER_PAGE))

    ratings_df = app.config.get("ratings")

    if start_date_ds:
        ratings_df = ratings_df.loc[ratings_df["timestamp"] >= start_date_ds]

    if end_date_ds:
        ratings_df = ratings_df.loc[ratings_df["timestamp"] < end_date_ds]

    subset = ratings_df.iloc[offset : offset + limit]

    return jsonify(
        {
            "result": subset.to_dict(orient="records"),
            "offset": offset,
            "limit": limit,
            "total": ratings_df.shape[0]
        }
    )


def _date_to_timestamp(date_str):
    if date_str is None:
        return None
    return int(time.mktime(time.strptime(date_str, "%Y-%m-%d")))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
