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


API_KEY = os.getenv("API_FOOTBALL_KEY")

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


API_URL = (
    "https://v3.football.api-sports.io/teams"
)


def get_connection():
    return psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
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


def fetch_teams(
    league_id,
    season,
):

    response = requests.get(
        API_URL,
        headers={
            "x-apisports-key":
                API_KEY
        },
        params={
            "league":
                league_id,

            "season":
                season,
        },
        timeout=30,
    )

    if not response.ok:

        print(
            f"Request failed for "
            f"league {league_id}"
        )

        print(
            "Status:",
            response.status_code,
        )

        print(
            response.text
        )

        return []

    data = response.json()

    if data.get("errors"):

        print(
            f"API error for league "
            f"{league_id}:",
            data["errors"],
        )

        return []

    return (
        data.get("response")
        or []
    )


def save_teams(
    teams,
    league_id,
    season,
):

    connection = get_connection()
    cursor = connection.cursor()

    saved = 0

    for item in teams:

        team = (
            item.get("team")
            or {}
        )

        venue = (
            item.get("venue")
            or {}
        )

        team_id = team.get("id")

        if team_id is None:
            continue

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
                name =
                    EXCLUDED.name,

                code =
                    EXCLUDED.code,

                country =
                    EXCLUDED.country,

                founded =
                    EXCLUDED.founded,

                is_national =
                    EXCLUDED.is_national,

                logo_url =
                    EXCLUDED.logo_url,

                venue_id =
                    EXCLUDED.venue_id,

                venue_name =
                    EXCLUDED.venue_name,

                venue_city =
                    EXCLUDED.venue_city,

                venue_capacity =
                    EXCLUDED.venue_capacity,

                venue_image_url =
                    EXCLUDED.venue_image_url;
            """,
            (
                team_id,
                team.get("name"),
                team.get("code"),
                team.get("country"),
                team.get("founded"),
                team.get(
                    "national",
                    False,
                ),
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

            VALUES (
                %s,
                %s,
                %s
            )

            ON CONFLICT (
                team_id,
                league_id,
                season
            )

            DO NOTHING;
            """,
            (
                team_id,
                league_id,
                season,
            ),
        )

        saved += 1

    connection.commit()

    cursor.close()
    connection.close()

    return saved


def main():

    args = get_args()

    season = args.season

    print()

    print(
        f"Importing Top-5 teams "
        f"for season {season}..."
    )

    print()

    for league in LEAGUES:

        league_id = league["id"]

        print(
            f"Importing teams from "
            f"{league['name']}..."
        )

        teams = fetch_teams(
            league_id,
            season,
        )

        print(
            f"{len(teams)} teams returned."
        )

        if not teams:

            print(
                f"No teams returned for "
                f"{league['name']}."
            )

            print()

            continue

        saved = save_teams(
            teams,
            league_id,
            season,
        )

        print(
            f"{saved} teams saved for "
            f"{league['name']}."
        )

        print()

    print(
        f"All teams for season "
        f"{season} imported."
    )


if __name__ == "__main__":
    main()