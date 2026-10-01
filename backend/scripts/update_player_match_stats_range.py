from datetime import date, datetime
import sys
import time

from scripts.import_player_match_stats import (
    get_connection,
    fetch_player_stats,
    save_fixture_stats,
)


SEASON = 2026


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

    # No arguments:
    # today only
    if len(args) == 0:
        today = date.today()

        return today, today

    # One argument:
    # single specified date
    if len(args) == 1:
        selected_date = parse_date(
            args[0]
        )

        return (
            selected_date,
            selected_date,
        )

    # Two arguments:
    # start date -> end date
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
        "scripts.update_player_match_stats_range"
    )

    print(
        "python -m "
        "scripts.update_player_match_stats_range "
        "2026-09-15"
    )

    print(
        "python -m "
        "scripts.update_player_match_stats_range "
        "2026-09-01 2026-09-15"
    )

    sys.exit(1)


def get_matches(
    start_date: date,
    end_date: date,
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            matches.id,
            leagues.name,
            matches.match_date,
            matches.status_short

        FROM matches

        JOIN leagues
            ON leagues.id =
               matches.league_id

        WHERE
            matches.season = %s

            AND DATE(
                matches.match_date
            )
            BETWEEN %s AND %s

        ORDER BY
            matches.match_date;
        """,
        (
            SEASON,
            start_date,
            end_date,
        ),
    )

    matches = cursor.fetchall()

    cursor.close()
    connection.close()

    return matches


def main():
    start_date, end_date = (
        get_date_range()
    )

    print()
    print("=" * 60)
    print(
        "FUTBUD PLAYER MATCH STATS UPDATE"
    )
    print("=" * 60)

    print()

    if start_date == end_date:
        print(
            f"Updating date: "
            f"{start_date}"
        )

    else:
        print(
            f"Updating range: "
            f"{start_date} "
            f"through "
            f"{end_date}"
        )

    matches = get_matches(
        start_date,
        end_date,
    )

    print(
        f"Matches found: "
        f"{len(matches)}"
    )

    if not matches:
        print()
        print(
            "No tracked matches found "
            "for this date range."
        )

        return

    total_saved = 0

    for index, match in enumerate(
        matches,
        start=1,
    ):
        fixture_id = match[0]
        league_name = match[1]
        match_date = match[2]
        status = match[3]

        print()
        print("-" * 60)

        print(
            f"[{index}/"
            f"{len(matches)}] "
            f"{league_name}"
        )

        print(
            f"Fixture: "
            f"{fixture_id}"
        )

        print(
            f"Date: "
            f"{match_date}"
        )

        print(
            f"Status: "
            f"{status}"
        )

        team_blocks = (
            fetch_player_stats(
                fixture_id
            )
        )

        if team_blocks is None:
            print(
                "API request failed."
            )

            continue

        if not team_blocks:
            print(
                "No player statistics "
                "available."
            )

            continue

        saved = save_fixture_stats(
            fixture_id,
            team_blocks,
        )

        total_saved += saved

        print(
            f"{saved} player stat "
            f"rows updated."
        )

        time.sleep(0.25)

    print()
    print("=" * 60)
    print(
        "PLAYER MATCH STATS UPDATE COMPLETE"
    )
    print("=" * 60)

    print()

    print(
        f"Matches processed: "
        f"{len(matches)}"
    )

    print(
        f"Player rows processed: "
        f"{total_saved}"
    )


if __name__ == "__main__":
    main()