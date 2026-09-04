import os

import psycopg
import requests

from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("API_FOOTBALL_KEY")

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


API_URL = "https://v3.football.api-sports.io/teams"

from football_config import (
    LEAGUES,
    SEASON,
)


def get_connection():
    return psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )


def fetch_teams():

    response = requests.get(
        API_URL,
        headers={
            "x-apisports-key": API_KEY
        },
        params={
            "league": PREMIER_LEAGUE_ID,
            "season": SEASON,
        },
        timeout=30,
    )

    if not response.ok:
        print("API status:", response.status_code)
        print("API response:", response.text)
        response.raise_for_status()

    data = response.json()

    if data["errors"]:
        raise Exception(data["errors"])

    return data["response"]


def save_teams(teams):

    connection = get_connection()
    cursor = connection.cursor()

    for item in teams:

        team = item["team"]
        venue = item["venue"]

        cursor.execute(
    """
    INSERT INTO team_league_seasons (
        team_id,
        league_id,
        season
    )
    VALUES (%s, %s, %s)

    ON CONFLICT (
        team_id,
        league_id,
        season
    )
    DO NOTHING;
    """,
    (
        team["id"],
        PREMIER_LEAGUE_ID,
        SEASON,
    ),
)

    connection.commit()

    cursor.close()
    connection.close()


def main():
    connection = get_connection()
    cursor = connection.cursor()

    for league in LEAGUES:
        league_id = league["id"]

        print(
            f"Importing teams from "
            f"{league['name']}..."
        )

        response = requests.get(
            API_URL,
            headers={
                "x-apisports-key": API_KEY
            },
            params={
                "league": league_id,
                "season": SEASON,
            },
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        if data.get("errors"):
            print(data["errors"])
            continue

        for item in data["response"]:
            team = item["team"]
            venue = item.get("venue") or {}

            cursor.execute(
                """
                INSERT INTO teams (
                    id,
                    name,
                    code,
                    country,
                    founded,
                    is_national,
                    logo_url,
                    venue_id,
                    venue_name,
                    venue_city,
                    venue_capacity,
                    venue_image_url
                )
                VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s
                )

                ON CONFLICT (id)
                DO UPDATE SET
                    name = EXCLUDED.name,
                    code = EXCLUDED.code,
                    country = EXCLUDED.country,
                    founded = EXCLUDED.founded,
                    is_national = EXCLUDED.is_national,
                    logo_url = EXCLUDED.logo_url,
                    venue_id = EXCLUDED.venue_id,
                    venue_name = EXCLUDED.venue_name,
                    venue_city = EXCLUDED.venue_city,
                    venue_capacity = EXCLUDED.venue_capacity,
                    venue_image_url = EXCLUDED.venue_image_url;
                """,
                (
                    team["id"],
                    team["name"],
                    team.get("code"),
                    team.get("country"),
                    team.get("founded"),
                    team.get("national", False),
                    team.get("logo"),

                    venue.get("id"),
                    venue.get("name"),
                    venue.get("city"),
                    venue.get("capacity"),
                    venue.get("image"),
                ),
            )

            cursor.execute(
                """
                INSERT INTO team_league_seasons (
                    team_id,
                    league_id,
                    season
                )
                VALUES (%s, %s, %s)

                ON CONFLICT (
                    team_id,
                    league_id,
                    season
                )
                DO NOTHING;
                """,
                (
                    team["id"],
                    league_id,
                    SEASON,
                ),
            )

        connection.commit()

        print(
            f"{league['name']} teams saved."
        )

    cursor.close()
    connection.close()

    print("All teams imported.")


if __name__ == "__main__":
    main()