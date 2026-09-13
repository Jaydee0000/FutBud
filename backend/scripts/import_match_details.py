import argparse
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


API_KEY = os.getenv(
    "API_FOOTBALL_KEY"
)

BASE_URL = (
    "https://v3.football.api-sports.io"
)


DB_HOST = os.getenv(
    "DB_HOST",
    "localhost",
)

DB_PORT = os.getenv(
    "DB_PORT",
    "5432",
)

DB_NAME = os.getenv(
    "DB_NAME",
    "futbud",
)

DB_USER = os.getenv(
    "DB_USER",
    "futbud_user",
)

DB_PASSWORD = os.getenv(
    "DB_PASSWORD",
)


FINISHED_STATUSES = (
    "FT",
    "AET",
    "PEN",
)


def get_connection():

    return psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def api_get(
    endpoint: str,
    params: dict,
):

    if not API_KEY:
        raise RuntimeError(
            "API_FOOTBALL_KEY is missing."
        )

    response = requests.get(
        f"{BASE_URL}{endpoint}",
        headers={
            "x-apisports-key":
                API_KEY,
        },
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    payload = response.json()

    errors = payload.get(
        "errors"
    )

    if errors:
        raise RuntimeError(
            f"API-Football error: {errors}"
        )

    return payload.get(
        "response",
        [],
    )


def ensure_player(
    cursor,
    player_id,
    player_name,
    position,
):

    if not player_id:
        return

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
            player_name
            or f"Player {player_id}",
            position,
        ),
    )


def save_lineups(
    cursor,
    match_id: int,
    lineup_data: list,
):

    # We replace this match's lineup every
    # time we sync it. This avoids stale data.
    cursor.execute(
        """
        DELETE FROM matchday_squad
        WHERE match_id = %s;
        """,
        (match_id,),
    )

    cursor.execute(
        """
        DELETE FROM match_lineups
        WHERE match_id = %s;
        """,
        (match_id,),
    )


    for lineup in lineup_data:

        team = (
            lineup.get("team")
            or {}
        )

        team_id = team.get(
            "id"
        )

        if not team_id:
            continue


        formation = lineup.get(
            "formation"
        )


        coach = (
            lineup.get("coach")
            or {}
        )


        cursor.execute(
            """
            INSERT INTO match_lineups (
                match_id,
                team_id,

                formation,

                coach_id,
                coach_name,
                coach_photo_url,

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
                team_id
            )

            DO UPDATE SET

                formation =
                    EXCLUDED.formation,

                coach_id =
                    EXCLUDED.coach_id,

                coach_name =
                    EXCLUDED.coach_name,

                coach_photo_url =
                    EXCLUDED.coach_photo_url,

                updated_at =
                    NOW();
            """,
            (
                match_id,
                team_id,

                formation,

                coach.get("id"),
                coach.get("name"),
                coach.get("photo"),
            ),
        )


        starters = (
            lineup.get("startXI")
            or []
        )

        substitutes = (
            lineup.get("substitutes")
            or []
        )


        save_lineup_players(
            cursor=cursor,
            match_id=match_id,
            team_id=team_id,
            players=starters,
            role="starter",
        )


        save_lineup_players(
            cursor=cursor,
            match_id=match_id,
            team_id=team_id,
            players=substitutes,
            role="bench",
        )


def save_lineup_players(
    cursor,
    match_id: int,
    team_id: int,
    players: list,
    role: str,
):

    for entry in players:

        player = (
            entry.get("player")
            or {}
        )


        player_id = player.get(
            "id"
        )

        player_name = player.get(
            "name"
        )

        number = player.get(
            "number"
        )

        position = player.get(
            "pos"
        )

        grid = player.get(
            "grid"
        )


        if not player_id:
            continue


        ensure_player(
            cursor=cursor,
            player_id=player_id,
            player_name=player_name,
            position=position,
        )


        cursor.execute(
            """
            INSERT INTO matchday_squad (
                match_id,
                team_id,
                player_id,

                role,
                shirt_number,
                position,
                grid,

                updated_at
            )

            VALUES (
                %s,
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

                grid =
                    EXCLUDED.grid,

                updated_at =
                    NOW();
            """,
            (
                match_id,
                team_id,
                player_id,

                role,
                number,
                position,
                grid,
            ),
        )


def save_events(
    cursor,
    match_id: int,
    events: list,
):

    cursor.execute(
        """
        DELETE FROM match_events
        WHERE match_id = %s;
        """,
        (match_id,),
    )


    for index, event in enumerate(
        events
    ):

        team = (
            event.get("team")
            or {}
        )

        player = (
            event.get("player")
            or {}
        )

        assist = (
            event.get("assist")
            or {}
        )

        event_time = (
            event.get("time")
            or {}
        )


        cursor.execute(
            """
            INSERT INTO match_events (
                match_id,
                event_index,

                team_id,

                player_id,
                player_name,

                assist_id,
                assist_name,

                elapsed,
                extra,

                event_type,
                detail,

                comments
            )

            VALUES (
                %s,
                %s,

                %s,

                %s,
                %s,

                %s,
                %s,

                %s,
                %s,

                %s,
                %s,

                %s
            );
            """,
            (
                match_id,
                index,

                team.get("id"),

                player.get("id"),
                player.get("name"),

                assist.get("id"),
                assist.get("name"),

                event_time.get(
                    "elapsed"
                ),

                event_time.get(
                    "extra"
                ),

                event.get("type"),
                event.get("detail"),

                event.get("comments"),
            ),
        )


def sync_match(
    connection,
    match_id: int,
):

    print(
        f"\nSyncing fixture {match_id}..."
    )


    # -----------------------------------
    # LINEUPS
    # -----------------------------------

    lineup_data = api_get(
        "/fixtures/lineups",
        {
            "fixture":
                match_id,
        },
    )


    print(
        f"  Lineup teams: "
        f"{len(lineup_data)}"
    )


    # -----------------------------------
    # EVENTS
    # -----------------------------------

    event_data = api_get(
        "/fixtures/events",
        {
            "fixture":
                match_id,
        },
    )


    print(
        f"  Events: "
        f"{len(event_data)}"
    )


    try:

        with connection.cursor() as cursor:

            save_lineups(
                cursor=cursor,
                match_id=match_id,
                lineup_data=lineup_data,
            )


            save_events(
                cursor=cursor,
                match_id=match_id,
                events=event_data,
            )


        connection.commit()


        print(
            f"✓ Fixture {match_id} synced."
        )


    except Exception:

        connection.rollback()

        raise


def get_missing_matches(
    connection,
    limit: int,
):

    with connection.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                matches.id,
                matches.match_date,
                matches.home_team_id,
                matches.away_team_id

            FROM matches

            WHERE matches.season = %s

              AND matches.league_id =
                  ANY(%s)

              AND matches.status_short =
                  ANY(%s)

              AND NOT EXISTS (
                  SELECT 1

                  FROM match_lineups

                  WHERE
                      match_lineups.match_id =
                      matches.id
              )

            ORDER BY
                matches.match_date DESC

            LIMIT %s;
            """,
            (
                SEASON,
                LEAGUE_IDS,
                list(
                    FINISHED_STATUSES
                ),
                limit,
            ),
        )


        return cursor.fetchall()


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Import fixture lineups and "
            "events into FutBud."
        )
    )


    parser.add_argument(
        "--match-id",
        type=int,
        help=(
            "Sync one specific "
            "API-Football fixture ID."
        ),
    )


    parser.add_argument(
        "--limit",
        type=int,
        default=25,
        help=(
            "Number of missing completed "
            "matches to import."
        ),
    )


    args = parser.parse_args()


    connection = get_connection()


    try:

        # --------------------------------
        # ONE SPECIFIC MATCH
        # --------------------------------

        if args.match_id:

            sync_match(
                connection,
                args.match_id,
            )

            return


        # --------------------------------
        # RECENT MISSING MATCHES
        # --------------------------------

        matches = get_missing_matches(
            connection,
            args.limit,
        )


        print(
            f"Found {len(matches)} "
            f"matches to sync."
        )


        for (
            match_id,
            match_date,
            home_team_id,
            away_team_id,
        ) in matches:

            print(
                "\n"
                "----------------------------"
            )

            print(
                f"{match_date}"
            )

            print(
                f"{home_team_id}"
                " vs "
                f"{away_team_id}"
            )


            try:

                sync_match(
                    connection,
                    match_id,
                )

            except Exception as error:

                print(
                    f"✗ Fixture "
                    f"{match_id} failed:"
                )

                print(error)


            # Avoid hammering the API.
            time.sleep(
                0.30
            )


    finally:

        connection.close()


if __name__ == "__main__":
    main()