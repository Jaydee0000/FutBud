from datetime import date, datetime
import os
import sys
import time

import requests

from scripts.import_player_match_stats import (
    get_connection,
)


SEASON = 2026

API_URL = (
    "https://v3.football.api-sports.io/fixtures"
)

API_KEY = os.getenv(
    "API_FOOTBALL_KEY"
)


def parse_date(value: str) -> date:
    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d",
        ).date()

    except ValueError:
        print()
        print(
            f"Invalid date: {value}"
        )
        print(
            "Use YYYY-MM-DD"
        )

        sys.exit(1)


def get_date_range():
    args = sys.argv[1:]

    if len(args) == 0:
        today = date.today()

        return today, today

    if len(args) == 1:
        selected_date = parse_date(
            args[0]
        )

        return (
            selected_date,
            selected_date,
        )

    if len(args) == 2:
        start_date = parse_date(
            args[0]
        )

        end_date = parse_date(
            args[1]
        )

        if start_date > end_date:
            print()
            print(
                "Start date cannot be "
                "after end date."
            )

            sys.exit(1)

        return (
            start_date,
            end_date,
        )

    print()
    print(
        "Usage:"
    )

    print(
        "python -m "
        "scripts.update_matches_range"
    )

    print(
        "python -m "
        "scripts.update_matches_range "
        "2026-09-14"
    )

    print(
        "python -m "
        "scripts.update_matches_range "
        "2026-09-01 2026-09-15"
    )

    sys.exit(1)


def get_matches_from_database(
    start_date,
    end_date,
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            match_date,
            status_short,
            home_goals,
            away_goals

        FROM matches

        WHERE season = %s

          AND DATE(match_date)
              BETWEEN %s AND %s

        ORDER BY match_date;
        """,
        (
            SEASON,
            start_date,
            end_date,
        ),
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return rows


def fetch_fixture(
    fixture_id,
):
    if not API_KEY:
        raise RuntimeError(
            "API_FOOTBALL_KEY is not set."
        )

    response = requests.get(
        API_URL,
        headers={
            "x-apisports-key":
                API_KEY,
        },
        params={
            "id":
                fixture_id,
        },
        timeout=30,
    )

    response.raise_for_status()

    payload = response.json()

    if payload.get("errors"):
        print(
            "API error:",
            payload["errors"],
        )

        return None

    fixtures = (
        payload.get("response")
        or []
    )

    if not fixtures:
        return None

    return fixtures[0]


def update_match(
    fixture_id,
    api_match,
):
    fixture = (
        api_match.get("fixture")
        or {}
    )

    status = (
        fixture.get("status")
        or {}
    )

    goals = (
        api_match.get("goals")
        or {}
    )

    score = (
        api_match.get("score")
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

    penalty = (
        score.get("penalty")
        or {}
    )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE matches

        SET
            status_long = %s,
            status_short = %s,
            elapsed = %s,

            home_goals = %s,
            away_goals = %s,

            halftime_home = %s,
            halftime_away = %s,

            fulltime_home = %s,
            fulltime_away = %s,

            penalty_home = %s,
            penalty_away = %s

        WHERE id = %s;
        """,
        (
            status.get("long"),
            status.get("short"),
            status.get("elapsed"),

            goals.get("home"),
            goals.get("away"),

            halftime.get("home"),
            halftime.get("away"),

            fulltime.get("home"),
            fulltime.get("away"),

            penalty.get("home"),
            penalty.get("away"),

            fixture_id,
        ),
    )

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "status":
            status.get("short"),

        "elapsed":
            status.get("elapsed"),

        "home":
            goals.get("home"),

        "away":
            goals.get("away"),
    }

def main():
    start_date, end_date = (
        get_date_range()
    )

    print()
    print("=" * 60)
    print(
        "FUTBUD MATCH DATABASE REFRESH"
    )
    print("=" * 60)

    print()

    if start_date == end_date:
        print(
            f"Refreshing: "
            f"{start_date}"
        )

    else:
        print(
            f"Refreshing: "
            f"{start_date} "
            f"through "
            f"{end_date}"
        )

    matches = (
        get_matches_from_database(
            start_date,
            end_date,
        )
    )

    print(
        f"Matches found: "
        f"{len(matches)}"
    )

    if not matches:
        print()
        print(
            "No matches found."
        )
        return

    updated = 0
    failed = 0

    for index, match in enumerate(
        matches,
        start=1,
    ):
        fixture_id = match[0]

        old_status = match[2]
        old_home = match[3]
        old_away = match[4]

        print()
        print("-" * 60)

        print(
            f"[{index}/"
            f"{len(matches)}] "
            f"Fixture {fixture_id}"
        )

        print(
            "Before:"
        )

        print(
            f"  Status: "
            f"{old_status}"
        )

        print(
            f"  Score: "
            f"{old_home}-"
            f"{old_away}"
        )

        try:
            api_match = (
                fetch_fixture(
                    fixture_id
                )
            )

        except Exception as error:
            print(
                f"API request failed: "
                f"{error}"
            )

            failed += 1
            continue

        if api_match is None:
            print(
                "No fixture returned "
                "by API."
            )

            failed += 1
            continue

        result = update_match(
            fixture_id,
            api_match,
        )

        print(
            "After:"
        )

        print(
            f"  Status: "
            f"{result['status']}"
        )

        print(
            f"  Elapsed: "
            f"{result['elapsed']}"
        )

        print(
            f"  Score: "
            f"{result['home']}-"
            f"{result['away']}"
        )

        updated += 1

        time.sleep(0.25)

    print()
    print("=" * 60)
    print(
        "MATCH DATABASE REFRESH COMPLETE"
    )
    print("=" * 60)

    print(
        f"Updated: {updated}"
    )

    print(
        f"Failed: {failed}"
    )


if __name__ == "__main__":
    main()