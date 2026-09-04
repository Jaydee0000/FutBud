import os
import time

import psycopg
import requests

from dotenv import load_dotenv

from football_config import (
    LEAGUE_IDS,
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
    "https://v3.football.api-sports.io"
    "/fixtures/statistics"
)


def get_connection():
    return psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )


def parse_percentage(value):
    if value is None:
        return None

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    value = (
        str(value)
        .replace("%", "")
        .strip()
    )

    if not value:
        return None

    try:
        return int(float(value))

    except ValueError:
        return None


def get_completed_matches():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            matches.id,
            leagues.name,
            matches.match_date

        FROM matches

        JOIN leagues
            ON leagues.id =
               matches.league_id

        WHERE matches.season = %s

          AND matches.league_id =
              ANY(%s)

          AND matches.status_short IN (
              'FT',
              'AET',
              'PEN'
          )

        ORDER BY matches.match_date;
        """,
        (
            SEASON,
            LEAGUE_IDS,
        ),
    )

    matches = cursor.fetchall()

    cursor.close()
    connection.close()

    return matches


def fetch_team_stats(
    fixture_id
):
    response = requests.get(
        API_URL,
        headers={
            "x-apisports-key":
                API_KEY,
        },
        params={
            "fixture":
                fixture_id,
        },
        timeout=30,
    )

    if not response.ok:

        print(
            f"Fixture {fixture_id} failed."
        )

        print(
            "Status:",
            response.status_code
        )

        print(
            response.text
        )

        return None


    data = response.json()


    if data.get("errors"):

        print(
            f"API error for fixture "
            f"{fixture_id}:",
            data["errors"]
        )

        return None


    return (
        data.get("response")
        or []
    )


def statistics_to_dict(
    statistics
):
    result = {}

    for stat in statistics:

        stat_type = stat.get("type")
        value = stat.get("value")

        if stat_type:
            result[stat_type] = value

    return result


def save_fixture_stats(
    fixture_id,
    team_blocks
):
    connection = get_connection()
    cursor = connection.cursor()

    saved = 0


    for team_block in team_blocks:

        team = (
            team_block.get("team")
            or {}
        )

        team_id = team.get("id")

        if team_id is None:
            continue


        statistics = (
            team_block.get("statistics")
            or []
        )

        stats = statistics_to_dict(
            statistics
        )


        cursor.execute(
            """
            INSERT INTO team_match_stats (
                match_id,
                team_id,

                shots_on_goal,
                shots_off_goal,
                total_shots,
                blocked_shots,

                shots_inside_box,
                shots_outside_box,

                fouls,
                corner_kicks,
                offsides,

                possession,

                yellow_cards,
                red_cards,

                goalkeeper_saves,

                total_passes,
                accurate_passes,
                pass_accuracy,

                updated_at
            )

            VALUES (
                %s, %s,

                %s, %s, %s, %s,

                %s, %s,

                %s, %s, %s,

                %s,

                %s, %s,

                %s,

                %s, %s, %s,

                NOW()
            )

            ON CONFLICT (
                match_id,
                team_id
            )

            DO UPDATE SET

                shots_on_goal =
                    EXCLUDED.shots_on_goal,

                shots_off_goal =
                    EXCLUDED.shots_off_goal,

                total_shots =
                    EXCLUDED.total_shots,

                blocked_shots =
                    EXCLUDED.blocked_shots,

                shots_inside_box =
                    EXCLUDED.shots_inside_box,

                shots_outside_box =
                    EXCLUDED.shots_outside_box,

                fouls =
                    EXCLUDED.fouls,

                corner_kicks =
                    EXCLUDED.corner_kicks,

                offsides =
                    EXCLUDED.offsides,

                possession =
                    EXCLUDED.possession,

                yellow_cards =
                    EXCLUDED.yellow_cards,

                red_cards =
                    EXCLUDED.red_cards,

                goalkeeper_saves =
                    EXCLUDED.goalkeeper_saves,

                total_passes =
                    EXCLUDED.total_passes,

                accurate_passes =
                    EXCLUDED.accurate_passes,

                pass_accuracy =
                    EXCLUDED.pass_accuracy,

                updated_at =
                    NOW();
            """,
            (
                fixture_id,
                team_id,

                stats.get(
                    "Shots on Goal"
                ),

                stats.get(
                    "Shots off Goal"
                ),

                stats.get(
                    "Total Shots"
                ),

                stats.get(
                    "Blocked Shots"
                ),

                stats.get(
                    "Shots insidebox"
                ),

                stats.get(
                    "Shots outsidebox"
                ),

                stats.get(
                    "Fouls"
                ),

                stats.get(
                    "Corner Kicks"
                ),

                stats.get(
                    "Offsides"
                ),

                parse_percentage(
                    stats.get(
                        "Ball Possession"
                    )
                ),

                stats.get(
                    "Yellow Cards"
                ),

                stats.get(
                    "Red Cards"
                ),

                stats.get(
                    "Goalkeeper Saves"
                ),

                stats.get(
                    "Total passes"
                ),

                stats.get(
                    "Passes accurate"
                ),

                parse_percentage(
                    stats.get(
                        "Passes %"
                    )
                ),
            ),
        )

        saved += 1


    connection.commit()

    cursor.close()
    connection.close()

    return saved


def main():

    completed_matches = (
        get_completed_matches()
    )


    print()
    print(
        f"Found "
        f"{len(completed_matches)} "
        f"completed matches across "
        f"all tracked leagues."
    )
    print()


    total_saved = 0


    for index, match in enumerate(
        completed_matches,
        start=1
    ):

        fixture_id = match[0]
        league_name = match[1]
        match_date = match[2]


        print(
            f"[{index}/"
            f"{len(completed_matches)}] "
            f"{league_name} | "
            f"Fixture {fixture_id} | "
            f"{match_date}"
        )


        team_blocks = (
            fetch_team_stats(
                fixture_id
            )
        )


        if team_blocks is None:

            print(
                "  Request failed."
            )

            continue


        if not team_blocks:

            print(
                "  No team statistics "
                "returned."
            )

            continue


        saved = save_fixture_stats(
            fixture_id,
            team_blocks,
        )


        total_saved += saved


        print(
            f"  {saved} team "
            f"stat rows saved."
        )


        time.sleep(0.25)


    print()
    print(
        "=============================="
    )

    print(
        "Team match stats import "
        "complete."
    )

    print(
        f"Total rows processed: "
        f"{total_saved}"
    )

    print(
        "=============================="
    )


if __name__ == "__main__":
    main()