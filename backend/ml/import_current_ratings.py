import argparse
import os
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from dotenv import load_dotenv


DEFAULT_SEASON = 2026
DEFAULT_REFERENCE_SEASON = 2025


# ============================================================
# ARGUMENTS
# ============================================================

def get_args():

    parser = argparse.ArgumentParser(
        description=(
            "Import FutBud current-season ratings "
            "into PostgreSQL."
        )
    )

    parser.add_argument(
        "--season",
        type=int,
        default=DEFAULT_SEASON,
    )

    parser.add_argument(
        "--reference-season",
        type=int,
        default=DEFAULT_REFERENCE_SEASON,
    )

    return parser.parse_args()


# ============================================================
# DATABASE
# ============================================================

def get_connection():

    load_dotenv()

    return psycopg.connect(
        host=os.getenv(
            "DB_HOST",
            "localhost",
        ),
        port=os.getenv(
            "DB_PORT",
            "5432",
        ),
        dbname=os.getenv(
            "DB_NAME",
            "futbud",
        ),
        user=os.getenv(
            "DB_USER",
            "futbud_user",
        ),
        password=os.getenv(
            "DB_PASSWORD",
        ),
    )


# ============================================================
# PATHS
# ============================================================

def get_paths(
    season,
):

    base_directory = Path(
        __file__
    ).parent

    output_directory = (
        base_directory
        / "output"
    )

    ratings_path = (
        output_directory
        / f"current_quality_scores_{season}.csv"
    )

    metrics_path = (
        output_directory
        / f"current_quality_percentiles_{season}.csv"
    )

    return (
        ratings_path,
        metrics_path,
    )


# ============================================================
# VALUE HELPERS
# ============================================================

def clean_value(
    value,
):

    if pd.isna(value):
        return None

    if isinstance(
        value,
        np.generic,
    ):
        return value.item()

    return value


def optional_int(
    value,
):

    if pd.isna(value):
        return None

    return int(
        value
    )


def optional_float(
    value,
):

    if pd.isna(value):
        return None

    return float(
        value
    )


def optional_string(
    value,
):

    if pd.isna(value):
        return None

    return str(
        value
    )


# ============================================================
# LOAD FILES
# ============================================================

def load_files(
    ratings_path,
    metrics_path,
):

    if not ratings_path.exists():

        raise FileNotFoundError(
            f"Rating file not found:\n"
            f"{ratings_path}"
        )


    if not metrics_path.exists():

        raise FileNotFoundError(
            f"Metric file not found:\n"
            f"{metrics_path}"
        )


    ratings = pd.read_csv(
        ratings_path
    )

    metrics = pd.read_csv(
        metrics_path
    )


    return (
        ratings,
        metrics,
    )


# ============================================================
# VALIDATE
# ============================================================

def validate_ratings(
    ratings,
):

    required_columns = [

        "player_id",
        "position",

        "archetype_key",
        "archetype_name",

        "minutes",

        "futbud_rating",
        "role_rating_percentile",

        "quality_status",
    ]


    missing = [

        column
        for column in required_columns
        if column not in ratings.columns
    ]


    if missing:

        raise ValueError(
            "Ratings CSV missing columns: "
            +
            ", ".join(
                missing
            )
        )


    duplicate_players = (
        ratings[
            "player_id"
        ]
        .duplicated()
        .sum()
    )


    if duplicate_players > 0:

        raise ValueError(
            f"Found {duplicate_players} "
            f"duplicate player IDs."
        )


# ============================================================
# IMPORT MAIN RATINGS
# ============================================================

def import_ratings(
    cursor,
    ratings,
    season,
    reference_season,
):

    query = """
        INSERT INTO player_season_ratings (

            player_id,
            season,
            reference_season,

            position,

            orientation,
            orientation_cluster,

            archetype_cluster,
            archetype_key,
            archetype_name,

            minutes,
            appearances,
            starts,

            latest_team_id,
            primary_league_id,

            provider_rating,

            raw_quality_rating,
            minutes_reliability,

            futbud_rating,

            role_rating_percentile,
            quality_status,

            quality_metric_count,

            updated_at
        )

        VALUES (

            %s, %s, %s,

            %s,

            %s, %s,

            %s, %s, %s,

            %s, %s, %s,

            %s, %s,

            %s,

            %s, %s,

            %s,

            %s, %s,

            %s,

            NOW()
        )

        ON CONFLICT (
            player_id,
            season
        )

        DO UPDATE SET

            reference_season =
                EXCLUDED.reference_season,

            position =
                EXCLUDED.position,

            orientation =
                EXCLUDED.orientation,

            orientation_cluster =
                EXCLUDED.orientation_cluster,

            archetype_cluster =
                EXCLUDED.archetype_cluster,

            archetype_key =
                EXCLUDED.archetype_key,

            archetype_name =
                EXCLUDED.archetype_name,

            minutes =
                EXCLUDED.minutes,

            appearances =
                EXCLUDED.appearances,

            starts =
                EXCLUDED.starts,

            latest_team_id =
                EXCLUDED.latest_team_id,

            primary_league_id =
                EXCLUDED.primary_league_id,

            provider_rating =
                EXCLUDED.provider_rating,

            raw_quality_rating =
                EXCLUDED.raw_quality_rating,

            minutes_reliability =
                EXCLUDED.minutes_reliability,

            futbud_rating =
                EXCLUDED.futbud_rating,

            role_rating_percentile =
                EXCLUDED.role_rating_percentile,

            quality_status =
                EXCLUDED.quality_status,

            quality_metric_count =
                EXCLUDED.quality_metric_count,

            updated_at =
                NOW();
    """


    rows = []


    for _, row in ratings.iterrows():

        rows.append(
            (

                int(
                    row[
                        "player_id"
                    ]
                ),

                season,

                reference_season,

                optional_string(
                    row.get(
                        "position"
                    )
                ),

                optional_string(
                    row.get(
                        "orientation"
                    )
                ),

                optional_int(
                    row.get(
                        "orientation_cluster"
                    )
                ),

                optional_int(
                    row.get(
                        "archetype_cluster"
                    )
                ),

                str(
                    row[
                        "archetype_key"
                    ]
                ),

                str(
                    row[
                        "archetype_name"
                    ]
                ),

                int(
                    row[
                        "minutes"
                    ]
                ),

                optional_int(
                    row.get(
                        "appearances"
                    )
                ),

                optional_int(
                    row.get(
                        "starts"
                    )
                ),

                optional_int(
                    row.get(
                        "latest_team_id"
                    )
                ),

                optional_int(
                    row.get(
                        "primary_league_id"
                    )
                ),

                optional_float(
                    row.get(
                        "provider_rating"
                    )
                ),

                optional_float(
                    row.get(
                        "raw_quality_rating"
                    )
                ),

                optional_float(
                    row.get(
                        "minutes_reliability"
                    )
                ),

                optional_float(
                    row.get(
                        "futbud_rating"
                    )
                ),

                optional_float(
                    row.get(
                        "role_rating_percentile"
                    )
                ),

                optional_string(
                    row.get(
                        "quality_status"
                    )
                ),

                optional_int(
                    row.get(
                        "quality_metric_count"
                    )
                ),
            )
        )


    cursor.executemany(
        query,
        rows,
    )


    return len(
        rows
    )


# ============================================================
# IMPORT METRICS
# ============================================================

def import_metrics(
    cursor,
    metrics,
    season,
):

    required_columns = [

        "player_id",
        "archetype_key",
        "archetype_name",

        "feature",

        "weight",
        "raw_value",

        "historical_percentile",
        "reference_players",
    ]


    missing = [

        column
        for column in required_columns
        if column not in metrics.columns
    ]


    if missing:

        raise ValueError(
            "Metrics CSV missing columns: "
            +
            ", ".join(
                missing
            )
        )


    query = """
        INSERT INTO player_season_rating_metrics (

            player_id,
            season,

            feature,

            archetype_key,
            archetype_name,

            raw_value,
            historical_percentile,

            weight,
            reference_players,

            updated_at
        )

        VALUES (

            %s, %s,

            %s,

            %s, %s,

            %s, %s,

            %s, %s,

            NOW()
        )

        ON CONFLICT (
            player_id,
            season,
            feature
        )

        DO UPDATE SET

            archetype_key =
                EXCLUDED.archetype_key,

            archetype_name =
                EXCLUDED.archetype_name,

            raw_value =
                EXCLUDED.raw_value,

            historical_percentile =
                EXCLUDED.historical_percentile,

            weight =
                EXCLUDED.weight,

            reference_players =
                EXCLUDED.reference_players,

            updated_at =
                NOW();
    """


    rows = []


    for _, row in metrics.iterrows():

        rows.append(
            (

                int(
                    row[
                        "player_id"
                    ]
                ),

                season,

                str(
                    row[
                        "feature"
                    ]
                ),

                str(
                    row[
                        "archetype_key"
                    ]
                ),

                str(
                    row[
                        "archetype_name"
                    ]
                ),

                optional_float(
                    row.get(
                        "raw_value"
                    )
                ),

                optional_float(
                    row.get(
                        "historical_percentile"
                    )
                ),

                optional_float(
                    row.get(
                        "weight"
                    )
                ),

                optional_int(
                    row.get(
                        "reference_players"
                    )
                ),
            )
        )


    cursor.executemany(
        query,
        rows,
    )


    return len(
        rows
    )


# ============================================================
# VERIFY
# ============================================================

def verify_import(
    cursor,
    season,
):

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM player_season_ratings
        WHERE season = %s;
        """,
        (
            season,
        ),
    )


    rating_count = (
        cursor.fetchone()[0]
    )


    cursor.execute(
        """
        SELECT COUNT(*)
        FROM player_season_rating_metrics
        WHERE season = %s;
        """,
        (
            season,
        ),
    )


    metric_count = (
        cursor.fetchone()[0]
    )


    cursor.execute(
        """
        SELECT
            players.name,
            player_season_ratings.archetype_name,
            player_season_ratings.futbud_rating

        FROM player_season_ratings

        JOIN players
            ON players.id =
               player_season_ratings.player_id

        WHERE player_season_ratings.season = %s

        ORDER BY
            player_season_ratings.futbud_rating DESC

        LIMIT 10;
        """,
        (
            season,
        ),
    )


    top_players = (
        cursor.fetchall()
    )


    return (
        rating_count,
        metric_count,
        top_players,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    args = get_args()

    season = (
        args.season
    )

    reference_season = (
        args.reference_season
    )


    (
        ratings_path,
        metrics_path,
    ) = get_paths(
        season
    )


    print()
    print(
        "========================================"
    )

    print(
        "FutBud PostgreSQL Rating Import"
    )

    print(
        "========================================"
    )

    print(
        f"Season: {season}"
    )

    print(
        f"Reference season: "
        f"{reference_season}"
    )


    (
        ratings,
        metrics,
    ) = load_files(
        ratings_path,
        metrics_path,
    )


    print()

    print(
        f"Rating rows loaded: "
        f"{len(ratings)}"
    )

    print(
        f"Metric rows loaded: "
        f"{len(metrics)}"
    )


    validate_ratings(
        ratings
    )


    connection = (
        get_connection()
    )


    try:

        with connection.cursor() as cursor:

            rating_count = (
                import_ratings(
                    cursor,
                    ratings,
                    season,
                    reference_season,
                )
            )


            metric_count = (
                import_metrics(
                    cursor,
                    metrics,
                    season,
                )
            )


            connection.commit()


            (
                database_rating_count,
                database_metric_count,
                top_players,
            ) = verify_import(
                cursor,
                season,
            )


    except Exception:

        connection.rollback()

        raise


    finally:

        connection.close()


    print()

    print(
        f"Ratings imported/upserted: "
        f"{rating_count}"
    )

    print(
        f"Metrics imported/upserted: "
        f"{metric_count}"
    )


    print()

    print(
        f"Ratings now in database: "
        f"{database_rating_count}"
    )

    print(
        f"Metrics now in database: "
        f"{database_metric_count}"
    )


    print()

    print(
        "Top FutBud ratings:"
    )


    for (
        player_name,
        archetype_name,
        futbud_rating,
    ) in top_players:

        print(
            f"{player_name:<30} "
            f"{str(futbud_rating):>6}   "
            f"{archetype_name}"
        )


    print()

    print(
        "========================================"
    )

    print(
        "DATABASE IMPORT COMPLETE"
    )

    print(
        "========================================"
    )


if __name__ == "__main__":
    main()