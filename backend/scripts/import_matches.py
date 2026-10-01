import argparse
import os

import requests

from dotenv import load_dotenv

from football_config import (
    LEAGUES,
    SEASON,
)
from database_config import get_connection


load_dotenv()


API_KEY = os.getenv("API_FOOTBALL_KEY")

API_URL = (
    "https://v3.football.api-sports.io/fixtures"
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


def fetch_matches_range(
    league_id,
    season,
    start_date,
    end_date,
):
    if not API_KEY:
        raise RuntimeError(
            "API_FOOTBALL_KEY is not set."
        )

    response = requests.get(
        API_URL,
        headers={
            "x-apisports-key": API_KEY,
        },
        params={
            "league": league_id,
            "season": season,
            "from": start_date.isoformat(),
            "to": end_date.isoformat(),
        },
        timeout=30,
    )

    response.raise_for_status()
    data = response.json()

    if data.get("errors"):
        raise RuntimeError(
            f"API-Football error for league {league_id}: "
            f"{data['errors']}"
        )

    return data.get("response") or []


def fetch_fixture(fixture_id):
    """Fetch one fixture, including fixtures whose date was rescheduled."""

    if not API_KEY:
        raise RuntimeError(
            "API_FOOTBALL_KEY is not set."
        )

    response = requests.get(
        API_URL,
        headers={
            "x-apisports-key": API_KEY,
        },
        params={"id": fixture_id},
        timeout=30,
    )

    response.raise_for_status()
    data = response.json()

    if data.get("errors"):
        raise RuntimeError(
            f"API-Football error for fixture {fixture_id}: "
            f"{data['errors']}"
        )

    fixtures = data.get("response") or []
    return fixtures[0] if fixtures else None


def save_matches(matches, *, return_ids=False):

    connection = get_connection()
    cursor = connection.cursor()

    saved = 0
    changed_ids = []

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
                    EXCLUDED.penalty_away

            WHERE ROW(
                matches.league_id,
                matches.season,
                matches.round,
                matches.match_date,
                matches.referee,
                matches.venue_id,
                matches.venue_name,
                matches.status_long,
                matches.status_short,
                matches.elapsed,
                matches.home_team_id,
                matches.away_team_id,
                matches.home_goals,
                matches.away_goals,
                matches.halftime_home,
                matches.halftime_away,
                matches.fulltime_home,
                matches.fulltime_away,
                matches.extra_time_home,
                matches.extra_time_away,
                matches.penalty_home,
                matches.penalty_away
            ) IS DISTINCT FROM ROW(
                EXCLUDED.league_id,
                EXCLUDED.season,
                EXCLUDED.round,
                EXCLUDED.match_date,
                EXCLUDED.referee,
                EXCLUDED.venue_id,
                EXCLUDED.venue_name,
                EXCLUDED.status_long,
                EXCLUDED.status_short,
                EXCLUDED.elapsed,
                EXCLUDED.home_team_id,
                EXCLUDED.away_team_id,
                EXCLUDED.home_goals,
                EXCLUDED.away_goals,
                EXCLUDED.halftime_home,
                EXCLUDED.halftime_away,
                EXCLUDED.fulltime_home,
                EXCLUDED.fulltime_away,
                EXCLUDED.extra_time_home,
                EXCLUDED.extra_time_away,
                EXCLUDED.penalty_home,
                EXCLUDED.penalty_away
            )

            RETURNING id;
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

        returned = cursor.fetchone()
        if returned:
            changed_ids.append(returned[0])

    connection.commit()

    cursor.close()
    connection.close()

    print(
        f"Saved/updated "
        f"{saved} matches."
    )

    if return_ids:
        return saved, changed_ids

    return saved


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
