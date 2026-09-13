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


API_URL = (
    "https://v3.football.api-sports.io"
)

API_KEY = os.getenv(
    "API_FOOTBALL_KEY"
)


def get_connection():

    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv(
            "DB_PORT",
            "5432",
        ),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv(
            "DB_PASSWORD"
        ),
    )


def get_matches():

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

          AND NOT EXISTS (

              SELECT 1

              FROM matchday_squad

              WHERE matchday_squad.match_id =
                    matches.id
          )

        ORDER BY
            matches.match_date;
        """,
        (
            SEASON,
            LEAGUE_IDS,
        ),
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return rows


def fetch_lineup(
    match_id: int
):

    response = requests.get(
            (
                f"{API_URL}"
                "/fixtures/lineups"
            ),
            headers={
                "x-apisports-key":
                    API_KEY
            },
            params={
                "fixture":
                    match_id
            },
            timeout=30,
        )

    response.raise_for_status()

    payload = response.json()

    errors = payload.get(
            "errors"
        )

    if errors:
        print(
            f"API error for "
            f"{match_id}: "
            f"{errors}"
        )

        return []

    return payload.get(
        "response",
        [],
    )


def save_player(
    cursor,
    player
):

    player_id = player.get("id")

    if player_id is None:
        return None

    cursor.execute(
        """
        INSERT INTO players (
            id,
            name,
            primary_position
        )

        VALUES (
            %s,
            %s,
            %s
        )

        ON CONFLICT (id)
        DO UPDATE SET

            name =
                COALESCE(
                    EXCLUDED.name,
                    players.name
                ),

            primary_position =
                COALESCE(
                    players.primary_position,
                    EXCLUDED.primary_position
                );
        """,
        (
            player_id,
            player.get("name"),
            player.get("pos"),
        ),
    )

    return player_id


def save_lineups(
    match_id: int,
    lineups
):

    if not lineups:
        return 0

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM matchday_squad
        WHERE match_id = %s;
        """,
        (match_id,),
    )

    saved = 0

    for lineup in lineups:

        team = lineup.get(
                "team",
                {},
            )

        team_id = team.get("id")

        if team_id is None:
            continue

        groups = [
            (
                "starter",
                lineup.get(
                    "startXI",
                    [],
                ),
            ),
            (
                "bench",
                lineup.get(
                    "substitutes",
                    [],
                ),
            ),
        ]

        for role, players in groups:

            for item in players:

                player = item.get(
                        "player",
                        {},
                    )

                player_id = save_player(
                        cursor,
                        player,
                    )

                if player_id is None:
                    continue

                cursor.execute(
                    """
                    INSERT INTO matchday_squad (
                        match_id,
                        team_id,
                        player_id,
                        role,
                        shirt_number,
                        position,
                        updated_at
                    )

                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        NOW()
                    )

                    ON CONFLICT (
                        match_id,
                        team_id,
                        player_id
                    )

                    DO UPDATE SET

                        role =
                            EXCLUDED.role,

                        shirt_number =
                            EXCLUDED.shirt_number,

                        position =
                            EXCLUDED.position,

                        updated_at =
                            NOW();
                    """,
                    (
                        match_id,
                        team_id,
                        player_id,
                        role,
                        player.get(
                            "number"
                        ),
                        player.get(
                            "pos"
                        ),
                    ),
                )

                saved += 1

    connection.commit()

    cursor.close()
    connection.close()

    return saved


def main():

    matches = get_matches()

    print()
    print(
        f"{len(matches)} matches "
        "need lineup data."
    )

    total = 0

    for (
        match_id,
        league_name,
        match_date,
    ) in matches:

        print(
            f"{league_name} | "
            f"{match_date} | "
            f"{match_id}"
        )

        try:

            lineups = fetch_lineup(
                    match_id
                )

            saved = save_lineups(
                    match_id,
                    lineups,
                )

            total += saved

            print(
                f"  {saved} "
                "matchday players saved"
            )

        except Exception as error:

            print(
                f"  ERROR: {error}"
            )

        time.sleep(0.25)

    print()
    print(
        f"Finished. "
        f"{total} matchday "
        "player rows saved."
    )


if __name__ == "__main__":
    main()