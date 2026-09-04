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


API_URL = "https://v3.football.api-sports.io/players"

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


def fetch_all_players(
    league_id
):
    page = 1
    all_players = []

    while True:

        print(
            f"Fetching page {page}..."
        )

        response = requests.get(
            API_URL,
            headers={
                "x-apisports-key": API_KEY
            },
            params={
                "league": league_id,
                "season": SEASON,
                "page": page,
            },
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        if data.get("errors"):
            raise Exception(
                data["errors"]
            )

        all_players.extend(
            data["response"]
        )

        current_page = (
            data["paging"]["current"]
        )

        total_pages = (
            data["paging"]["total"]
        )

        print(
            f"Page {current_page}/"
            f"{total_pages}"
        )

        if (
            current_page
            >= total_pages
        ):
            break

        page += 1

    return all_players

def save_players(api_players):
    connection = get_connection()
    cursor = connection.cursor()

    saved_players = 0
    saved_memberships = 0

    for item in api_players:
        player = item["player"]
        statistics = item["statistics"]

        birth = player.get("birth") or {}

        primary_position = None

        if statistics:
            primary_position = (
                statistics[0]
                .get("games", {})
                .get("position")
            )

        cursor.execute(
            """
            INSERT INTO players (
                id,
                name,
                firstname,
                lastname,
                birth_date,
                birth_place,
                birth_country,
                nationality,
                height,
                weight,
                primary_position,
                photo_url
            )
            VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s
            )

            ON CONFLICT (id)
            DO UPDATE SET
                name = EXCLUDED.name,
                firstname = EXCLUDED.firstname,
                lastname = EXCLUDED.lastname,
                birth_date = EXCLUDED.birth_date,
                birth_place = EXCLUDED.birth_place,
                birth_country = EXCLUDED.birth_country,
                nationality = EXCLUDED.nationality,
                height = EXCLUDED.height,
                weight = EXCLUDED.weight,
                primary_position = EXCLUDED.primary_position,
                photo_url = EXCLUDED.photo_url;
            """,
            (
                player["id"],
                player["name"],
                player.get("firstname"),
                player.get("lastname"),
                birth.get("date"),
                birth.get("place"),
                birth.get("country"),
                player.get("nationality"),
                player.get("height"),
                player.get("weight"),
                primary_position,
                player.get("photo"),
            ),
        )

        saved_players += 1

        for stat in statistics:
            team = stat.get("team") or {}
            games = stat.get("games") or {}

            team_id = team.get("id")

            if team_id is None:
                continue

            cursor.execute(
                """
                INSERT INTO player_team_history (
                    player_id,
                    team_id,
                    season,
                    position
                )
                VALUES (%s, %s, %s, %s)

                ON CONFLICT (
                    player_id,
                    team_id,
                    season
                )
                DO UPDATE SET
                    position = EXCLUDED.position;
                """,
                (
                    player["id"],
                    team_id,
                    SEASON,
                    games.get("position"),
                ),
            )

            saved_memberships += 1

    connection.commit()

    cursor.close()
    connection.close()

    print(f"Saved {saved_players} players")
    print(
        f"Saved/updated {saved_memberships} team memberships"
    )


def main():

    for league in LEAGUES:

        print(
            f"\nImporting players from "
            f"{league['name']}..."
        )

        players = fetch_all_players(
            league["id"]
        )

        print(
            f"{len(players)} players "
            f"returned."
        )

        save_players(players)

    print(
        "\nAll league players imported."
    )


if __name__ == "__main__":
    main()



    