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


API_URL = (
    "https://v3.football.api-sports.io"
    "/standings"
)

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


def fetch_standings(league_id):

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

    response_data = (
        data.get("response")
        or []
    )

    if not response_data:
        return []

    league_data = (
        response_data[0]
        .get("league")
        or {}
    )

    standings_groups = (
        league_data.get("standings")
        or []
    )

    if not standings_groups:
        return []

    return standings_groups[0]


def save_standings(
    rows,
    league_id
):
    connection = get_connection()
    cursor = connection.cursor()

    saved = 0

    for row in rows:

        team = (
            row.get("team")
            or {}
        )

        team_id = team.get("id")

        if team_id is None:
            continue


        all_stats = (
            row.get("all")
            or {}
        )

        home_stats = (
            row.get("home")
            or {}
        )

        away_stats = (
            row.get("away")
            or {}
        )


        all_goals = (
            all_stats.get("goals")
            or {}
        )

        home_goals = (
            home_stats.get("goals")
            or {}
        )

        away_goals = (
            away_stats.get("goals")
            or {}
        )


        cursor.execute(
            """
            INSERT INTO standings (
                league_id,
                season,
                team_id,

                rank,
                points,
                goals_difference,

                form,
                status,
                description,

                played,
                wins,
                draws,
                losses,

                goals_for,
                goals_against,

                home_played,
                home_wins,
                home_draws,
                home_losses,
                home_goals_for,
                home_goals_against,

                away_played,
                away_wins,
                away_draws,
                away_losses,
                away_goals_for,
                away_goals_against,

                updated_at
            )

            VALUES (
                %s, %s, %s,

                %s, %s, %s,

                %s, %s, %s,

                %s, %s, %s, %s,

                %s, %s,

                %s, %s, %s, %s,
                %s, %s,

                %s, %s, %s, %s,
                %s, %s,

                NOW()
            )

            ON CONFLICT (
                league_id,
                season,
                team_id
            )

            DO UPDATE SET
                rank =
                    EXCLUDED.rank,

                points =
                    EXCLUDED.points,

                goals_difference =
                    EXCLUDED.goals_difference,

                form =
                    EXCLUDED.form,

                status =
                    EXCLUDED.status,

                description =
                    EXCLUDED.description,

                played =
                    EXCLUDED.played,

                wins =
                    EXCLUDED.wins,

                draws =
                    EXCLUDED.draws,

                losses =
                    EXCLUDED.losses,

                goals_for =
                    EXCLUDED.goals_for,

                goals_against =
                    EXCLUDED.goals_against,

                home_played =
                    EXCLUDED.home_played,

                home_wins =
                    EXCLUDED.home_wins,

                home_draws =
                    EXCLUDED.home_draws,

                home_losses =
                    EXCLUDED.home_losses,

                home_goals_for =
                    EXCLUDED.home_goals_for,

                home_goals_against =
                    EXCLUDED.home_goals_against,

                away_played =
                    EXCLUDED.away_played,

                away_wins =
                    EXCLUDED.away_wins,

                away_draws =
                    EXCLUDED.away_draws,

                away_losses =
                    EXCLUDED.away_losses,

                away_goals_for =
                    EXCLUDED.away_goals_for,

                away_goals_against =
                    EXCLUDED.away_goals_against,

                updated_at =
                    NOW();
            """,
            (
                league_id,
                SEASON,
                team_id,

                row.get("rank"),
                row.get("points"),
                row.get("goalsDiff"),

                row.get("form"),
                row.get("status"),
                row.get("description"),

                all_stats.get("played"),
                all_stats.get("win"),
                all_stats.get("draw"),
                all_stats.get("lose"),

                all_goals.get("for"),
                all_goals.get("against"),

                home_stats.get("played"),
                home_stats.get("win"),
                home_stats.get("draw"),
                home_stats.get("lose"),

                home_goals.get("for"),
                home_goals.get("against"),

                away_stats.get("played"),
                away_stats.get("win"),
                away_stats.get("draw"),
                away_stats.get("lose"),

                away_goals.get("for"),
                away_goals.get("against"),
            ),
        )

        saved += 1


    connection.commit()

    cursor.close()
    connection.close()

    print(
        f"Saved/updated "
        f"{saved} standings rows."
    )


def main():
    total_saved = 0

    for league in LEAGUES:
        league_id = league["id"]
        league_name = league["name"]

        print()
        print(
            "=============================="
        )
        print(
            f"Importing standings: "
            f"{league_name}"
        )
        print(
            f"League ID: {league_id}"
        )
        print(
            "=============================="
        )

        standings = fetch_standings(
            league_id
        )

        print(
            f"API returned "
            f"{len(standings)} teams."
        )

        if not standings:
            print(
                f"No standings returned for "
                f"{league_name}."
            )
            continue

        saved = save_standings(
            standings,
            league_id,
        )

        if saved is None:
            saved = len(standings)

        total_saved += saved

        print(
            f"{league_name} "
            f"standings saved."
        )

    print()
    print(
        "=============================="
    )
    print(
        "Standings import complete."
    )
    print(
        f"Total standings rows processed: "
        f"{total_saved}"
    )
    print(
        "=============================="
    )



if __name__ == "__main__":
    main()