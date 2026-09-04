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
    "/players/squads"
)


def get_connection():
    return psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )


def get_team_ids():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT DISTINCT
            team_league_seasons.team_id,
            teams.name,
            team_league_seasons.league_id

        FROM team_league_seasons

        JOIN teams
            ON teams.id =
               team_league_seasons.team_id

        WHERE
            team_league_seasons.season = %s

            AND team_league_seasons.league_id
                = ANY(%s)

        ORDER BY teams.name;
        """,
        (
            SEASON,
            LEAGUE_IDS,
        ),
    )

    teams = cursor.fetchall()

    cursor.close()
    connection.close()

    return teams


def fetch_squad(team_id):
    response = requests.get(
        API_URL,
        headers={
            "x-apisports-key": API_KEY
        },
        params={
            "team": team_id
        },
        timeout=30,
    )

    if not response.ok:

        print(
            f"Request failed for "
            f"team {team_id}"
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
            f"API error for "
            f"team {team_id}:",
            data["errors"]
        )

        return None

    response_data = (
        data.get("response")
        or []
    )

    if not response_data:
        return None

    return response_data[0]


def save_squad(
    squad_data,
    team_id
):
    connection = get_connection()
    cursor = connection.cursor()

    players = (
        squad_data.get("players")
        or []
    )

    # Clear previous current squad
    # for this team/season.
    cursor.execute(
        """
        DELETE FROM squads

        WHERE team_id = %s
          AND season = %s;
        """,
        (
            team_id,
            SEASON,
        ),
    )


    saved = 0


    for player in players:

        player_id = player.get("id")

        if player_id is None:
            continue


        # Make sure player exists.
        cursor.execute(
            """
            INSERT INTO players (
                id,
                name,
                primary_position,
                photo_url
            )

            VALUES (
                %s,
                %s,
                %s,
                %s
            )

            ON CONFLICT (id)

            DO UPDATE SET
                name =
                    EXCLUDED.name,

                primary_position =
                    COALESCE(
                        EXCLUDED.primary_position,
                        players.primary_position
                    ),

                photo_url =
                    COALESCE(
                        EXCLUDED.photo_url,
                        players.photo_url
                    );
            """,
            (
                player_id,
                player.get("name")
                or "Unknown Player",

                player.get(
                    "position"
                ),

                player.get(
                    "photo"
                ),
            ),
        )


        cursor.execute(
            """
            INSERT INTO squads (
                team_id,
                player_id,
                season,
                shirt_number,
                position
            )

            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s
            )

            ON CONFLICT (
                team_id,
                player_id,
                season
            )

            DO UPDATE SET
                shirt_number =
                    EXCLUDED.shirt_number,

                position =
                    EXCLUDED.position;
            """,
            (
                team_id,
                player_id,
                SEASON,

                player.get(
                    "number"
                ),

                player.get(
                    "position"
                ),
            ),
        )

        saved += 1


    connection.commit()

    cursor.close()
    connection.close()

    return saved


def main():

    teams = get_team_ids()

    print()
    print(
        f"Found {len(teams)} teams "
        f"across all tracked leagues."
    )
    print()


    for index, row in enumerate(
        teams,
        start=1
    ):

        team_id = row[0]
        team_name = row[1]
        league_id = row[2]


        print(
            f"[{index}/{len(teams)}] "
            f"{team_name} "
            f"(league {league_id})"
        )


        squad_data = fetch_squad(
            team_id
        )


        if squad_data is None:

            print(
                "  No squad returned."
            )

            continue


        saved = save_squad(
            squad_data,
            team_id
        )


        print(
            f"  {saved} players saved."
        )


        time.sleep(0.15)


    print()
    print(
        "All squad imports complete."
    )


if __name__ == "__main__":
    main()