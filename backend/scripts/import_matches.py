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


API_URL = "https://v3.football.api-sports.io/fixtures"

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


def fetch_matches(league_id):
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

    if not response.ok:
        print(
            f"Failed league {league_id}:",
            response.status_code
        )
        print(response.text)
        return []

    data = response.json()

    if data.get("errors"):
        print(
            f"API error for league "
            f"{league_id}:",
            data["errors"]
        )
        return []

    return data.get("response", [])


def save_matches(matches):
    connection = get_connection()
    cursor = connection.cursor()

    saved = 0

    for item in matches:

        fixture = item["fixture"]
        league = item["league"]
        teams = item["teams"]
        goals = item["goals"]
        score = item["score"]

        venue = fixture.get("venue") or {}
        status = fixture.get("status") or {}

        halftime = score.get("halftime") or {}
        fulltime = score.get("fulltime") or {}
        extratime = score.get("extratime") or {}
        penalty = score.get("penalty") or {}

        cursor.execute(
            """
            INSERT INTO matches (
                id,
                league_id,
                season,
                round,
                match_date,
                referee,
                venue_id,
                venue_name,
                status_long,
                status_short,
                elapsed,
                home_team_id,
                away_team_id,
                home_goals,
                away_goals,
                halftime_home,
                halftime_away,
                fulltime_home,
                fulltime_away,
                extra_time_home,
                extra_time_away,
                penalty_home,
                penalty_away
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s
            )

            ON CONFLICT (id)
            DO UPDATE SET
                round = EXCLUDED.round,
                match_date = EXCLUDED.match_date,
                referee = EXCLUDED.referee,

                venue_id = EXCLUDED.venue_id,
                venue_name = EXCLUDED.venue_name,

                status_long = EXCLUDED.status_long,
                status_short = EXCLUDED.status_short,
                elapsed = EXCLUDED.elapsed,

                home_goals = EXCLUDED.home_goals,
                away_goals = EXCLUDED.away_goals,

                halftime_home = EXCLUDED.halftime_home,
                halftime_away = EXCLUDED.halftime_away,

                fulltime_home = EXCLUDED.fulltime_home,
                fulltime_away = EXCLUDED.fulltime_away,

                extra_time_home = EXCLUDED.extra_time_home,
                extra_time_away = EXCLUDED.extra_time_away,

                penalty_home = EXCLUDED.penalty_home,
                penalty_away = EXCLUDED.penalty_away;
            """,
            (
                fixture["id"],
                league["id"],
                league["season"],
                league.get("round"),
                fixture["date"],
                fixture.get("referee"),

                venue.get("id"),
                venue.get("name"),

                status.get("long"),
                status.get("short"),
                status.get("elapsed"),

                teams["home"]["id"],
                teams["away"]["id"],

                goals.get("home"),
                goals.get("away"),

                halftime.get("home"),
                halftime.get("away"),

                fulltime.get("home"),
                fulltime.get("away"),

                extratime.get("home"),
                extratime.get("away"),

                penalty.get("home"),
                penalty.get("away"),
            ),
        )

        saved += 1

    connection.commit()

    cursor.close()
    connection.close()

    print(f"Saved/updated {saved} matches.")


def main():

    for league in LEAGUES:

        print()
        print(
            f"Importing fixtures from "
            f"{league['name']}..."
        )

        matches = fetch_matches(
            league["id"]
        )

        print(
            f"{len(matches)} fixtures returned."
        )

        if not matches:
            continue

        save_matches(matches)

        print(
            f"{league['name']} fixtures saved."
        )

    print()
    print("All league fixtures imported.")



if __name__ == "__main__":
    main()