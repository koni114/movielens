import pandas as pd


def rank_movie_by_rating(ratings, min_ratings=2):
    ranking = (
        ratings.groupby("movieId")
        .agg(
            avg_rating=pd.NamedAgg(column="rating", aggfunc="mean"),
            num_ratings=pd.NamedAgg(column="userId", aggfunc="nunique"),
        )
        .loc[lambda df: df["avg_rating"] > min_ratings]
        .sort_values(["avg_rating", "num_ratings"], ascending=False)
    )
    return ranking
