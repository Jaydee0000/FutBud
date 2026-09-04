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


def get_connection():
    return psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )


def main():
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
                "id": league_id,
                "season": SEASON,
            },
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        if data.get("errors"):
            print(data["errors"])
            continue

        if not data["response"]:
            print(
                "No league data returned."
            )
            continue

        result = data["response"][0]

        league = result["league"]
        country = result["country"]

        season_data = None

        for season in result["seasons"]:
            if (
                season["year"]
                == SEASON
            ):
                season_data = season
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
                league["id"],
                league["name"],
                country.get("name"),
                league.get("type"),
                league.get("logo"),
                country.get("flag"),
            ),
        )

        if season_data:
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
                    league["id"],
                    SEASON,
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
            f"{league['name']} saved."
        )

    connection.commit()

    cursor.close()
    connection.close()

    print(
        "All five leagues imported."
    )


if __name__ == "__main__":
    main()