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
    "https://v3.football.api-sports.io/fixtures"
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


def fetch_matches(
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
            f"Failed league "
            f"{league_id}: "
            f"{response.status_code}"
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


def save_matches(matches):

    connection = get_connection()
    cursor = connection.cursor()

    saved = 0

    for item in matches:

        fixture = (
            item.get("fixture")
            or {}
        )

        league = (
            item.get("league")
            or {}
        )

        teams = (
            item.get("teams")
            or {}
        )

        goals = (
            item.get("goals")
            or {}
        )

        score = (
            item.get("score")
            or {}
        )

        home_team = (
            teams.get("home")
            or {}
        )

        away_team = (
            teams.get("away")
            or {}
        )

        venue = (
            fixture.get("venue")
            or {}
        )

        status = (
            fixture.get("status")
            or {}
        )

        halftime = (
            score.get("halftime")
            or {}
        )

        fulltime = (
            score.get("fulltime")
            or {}
        )

        extratime = (
            score.get("extratime")
            or {}
        )

        penalty = (
            score.get("penalty")
            or {}
        )

        fixture_id = fixture.get("id")

        if fixture_id is None:
            continue

        if home_team.get("id") is None:
            continue

        if away_team.get("id") is None:
            continue

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
                league_id =
                    EXCLUDED.league_id,

                season =
                    EXCLUDED.season,

                round =
                    EXCLUDED.round,

                match_date =
                    EXCLUDED.match_date,

                referee =
                    EXCLUDED.referee,

                venue_id =
                    EXCLUDED.venue_id,

                venue_name =
                    EXCLUDED.venue_name,

                status_long =
                    EXCLUDED.status_long,

                status_short =
                    EXCLUDED.status_short,

                elapsed =
                    EXCLUDED.elapsed,

                home_team_id =
                    EXCLUDED.home_team_id,

                away_team_id =
                    EXCLUDED.away_team_id,

                home_goals =
                    EXCLUDED.home_goals,

                away_goals =
                    EXCLUDED.away_goals,

                halftime_home =
                    EXCLUDED.halftime_home,

                halftime_away =
                    EXCLUDED.halftime_away,

                fulltime_home =
                    EXCLUDED.fulltime_home,

                fulltime_away =
                    EXCLUDED.fulltime_away,

                extra_time_home =
                    EXCLUDED.extra_time_home,

                extra_time_away =
                    EXCLUDED.extra_time_away,

                penalty_home =
                    EXCLUDED.penalty_home,

                penalty_away =
                    EXCLUDED.penalty_away;
            """,
            (
                fixture_id,

                league.get("id"),
                league.get("season"),
                league.get("round"),

                fixture.get("date"),
                fixture.get("referee"),

                venue.get("id"),
                venue.get("name"),

                status.get("long"),
                status.get("short"),
                status.get("elapsed"),

                home_team.get("id"),
                away_team.get("id"),

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

    print(
        f"Saved/updated "
        f"{saved} matches."
    )


def main():

    args = get_args()

    season = args.season

    print()

    print(
        f"Importing Top-5 fixtures "
        f"for season {season}..."
    )

    for league in LEAGUES:

        print()

        print(
            f"Importing fixtures from "
            f"{league['name']}..."
        )

        matches = fetch_matches(
            league["id"],
            season,
        )

        print(
            f"{len(matches)} "
            f"fixtures returned."
        )

        if not matches:

            print(
                f"No fixtures returned "
                f"for {league['name']}."
            )

            continue

        save_matches(
            matches
        )

        print(
            f"{league['name']} "
            f"fixtures saved."
        )

    print()

    print(
        f"All league fixtures for "
        f"season {season} imported."
    )


if __name__ == "__main__":
    main()