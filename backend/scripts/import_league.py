import argparse
import os

import psycopg
import requests

from dotenv import load_dotenv

from football_config import (
    LEAGUES,
    SEASON,
)


load_dotenv()


API_KEY = os.getenv(
    "API_FOOTBALL_KEY"
)

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv(
    "DB_PASSWORD"
)
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


API_URL = (
    "https://v3.football.api-sports.io"
    "/leagues"
)


def get_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--season",
        type=int,
        default=SEASON,
        help="Season year to import",
    )

    return parser.parse_args()


def get_connection():

    return psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )


def main():

    args = get_args()

    target_season = args.season

    print()

    print(
        f"Importing Top-5 league data "
        f"for season {target_season}..."
    )

    print()

    connection = get_connection()
    cursor = connection.cursor()

    for league_config in LEAGUES:

        league_id = (
            league_config["id"]
        )

        print(
            f"Importing "
            f"{league_config['name']}..."
        )

        response = requests.get(
            API_URL,
            headers={
                "x-apisports-key":
                    API_KEY
            },
            params={
                "id":
                    league_id,

                "season":
                    target_season,
            },
            timeout=30,
        )

        if not response.ok:

            print(
                f"Request failed for "
                f"{league_config['name']}"
            )

            print(
                "Status:",
                response.status_code,
            )

            print(
                response.text
            )

            continue

        data = response.json()

        if data.get("errors"):

            print(
                f"API error for "
                f"{league_config['name']}:",
                data["errors"],
            )

            continue

        response_data = (
            data.get("response")
            or []
        )

        if not response_data:

            print(
                "No league data returned."
            )

            continue

        result = response_data[0]

        league = (
            result.get("league")
            or {}
        )

        country = (
            result.get("country")
            or {}
        )

        season_data = None

        for season_info in (
            result.get("seasons")
            or []
        ):

            if (
                season_info.get("year")
                ==
                target_season
            ):
                season_data = season_info
                break

        cursor.execute(
            """
            INSERT INTO leagues (
                id,
                name,
                country,
                type,
                logo_url,
                country_flag_url
            )

            VALUES (
                %s, %s, %s,
                %s, %s, %s
            )

            ON CONFLICT (id)

            DO UPDATE SET
                name =
                    EXCLUDED.name,

                country =
                    EXCLUDED.country,

                type =
                    EXCLUDED.type,

                logo_url =
                    EXCLUDED.logo_url,

                country_flag_url =
                    EXCLUDED.country_flag_url;
            """,
            (
                league.get("id"),
                league.get("name"),
                country.get("name"),
                league.get("type"),
                league.get("logo"),
                country.get("flag"),
            ),
        )

        if season_data is None:

            print(
                f"No season metadata found "
                f"for {target_season}."
            )

            continue

        cursor.execute(
            """
            INSERT INTO league_seasons (
                league_id,
                season,
                start_date,
                end_date,
                is_current
            )

            VALUES (
                %s, %s, %s,
                %s, %s
            )

            ON CONFLICT (
                league_id,
                season
            )

            DO UPDATE SET
                start_date =
                    EXCLUDED.start_date,

                end_date =
                    EXCLUDED.end_date,

                is_current =
                    EXCLUDED.is_current;
            """,
            (
                league.get("id"),
                target_season,

                season_data.get(
                    "start"
                ),

                season_data.get(
                    "end"
                ),

                season_data.get(
                    "current",
                    False,
                ),
            ),
        )

        print(
            f"{league.get('name')} "
            f"{target_season} saved."
        )

    connection.commit()

    cursor.close()
    connection.close()

    print()

    print(
        f"All five leagues for "
        f"{target_season} imported."
    )


if __name__ == "__main__":
    main()