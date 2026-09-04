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
    "/fixtures/players"
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


def fetch_player_stats(
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
            f"Fixture {fixture_id} "
            f"failed."
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


        players = (
            team_block.get("players")
            or []
        )


        for player_item in players:

            player = (
                player_item.get("player")
                or {}
            )

            player_id = player.get("id")

            if player_id is None:
                continue


            # Make sure the player exists
            # before inserting stats.

            cursor.execute(
                """
                INSERT INTO players (
                    id,
                    name,
                    photo_url
                )

                VALUES (
                    %s,
                    %s,
                    %s
                )

                ON CONFLICT (id)

                DO UPDATE SET
                    name =
                        EXCLUDED.name,

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

                    player.get("photo"),
                ),
            )


            statistics_list = (
                player_item.get(
                    "statistics"
                )
                or []
            )


            if not statistics_list:
                continue


            stats = statistics_list[0]


            games = (
                stats.get("games")
                or {}
            )

            shots = (
                stats.get("shots")
                or {}
            )

            goals = (
                stats.get("goals")
                or {}
            )

            passes = (
                stats.get("passes")
                or {}
            )

            tackles = (
                stats.get("tackles")
                or {}
            )

            duels = (
                stats.get("duels")
                or {}
            )

            dribbles = (
                stats.get("dribbles")
                or {}
            )

            fouls = (
                stats.get("fouls")
                or {}
            )

            cards = (
                stats.get("cards")
                or {}
            )

            penalty = (
                stats.get("penalty")
                or {}
            )


            rating = games.get("rating")

            if rating is not None:

                try:
                    rating = float(
                        rating
                    )

                except (
                    ValueError,
                    TypeError
                ):
                    rating = None


            cursor.execute(
                """
                INSERT INTO player_match_stats (
                    match_id,
                    player_id,
                    team_id,

                    minutes,
                    shirt_number,
                    position,

                    provider_rating,

                    captain,
                    substitute,

                    offsides,

                    shots_total,
                    shots_on_target,

                    goals,
                    goals_conceded,
                    assists,
                    saves,

                    passes_total,
                    key_passes,
                    pass_accuracy,

                    tackles,
                    blocks,
                    interceptions,

                    duels_total,
                    duels_won,

                    dribbles_attempted,
                    dribbles_successful,
                    dribbled_past,

                    fouls_drawn,
                    fouls_committed,

                    yellow_cards,
                    red_cards,

                    penalties_won,
                    penalties_committed,
                    penalties_scored,
                    penalties_missed,
                    penalties_saved,

                    updated_at
                )

                VALUES (
                    %s, %s, %s,

                    %s, %s, %s,

                    %s,

                    %s, %s,

                    %s,

                    %s, %s,

                    %s, %s, %s, %s,

                    %s, %s, %s,

                    %s, %s, %s,

                    %s, %s,

                    %s, %s, %s,

                    %s, %s,

                    %s, %s,

                    %s, %s, %s,
                    %s, %s,

                    NOW()
                )

                ON CONFLICT (
                    match_id,
                    player_id
                )

                DO UPDATE SET

                    team_id =
                        EXCLUDED.team_id,

                    minutes =
                        EXCLUDED.minutes,

                    shirt_number =
                        EXCLUDED.shirt_number,

                    position =
                        EXCLUDED.position,

                    provider_rating =
                        EXCLUDED.provider_rating,

                    captain =
                        EXCLUDED.captain,

                    substitute =
                        EXCLUDED.substitute,

                    offsides =
                        EXCLUDED.offsides,

                    shots_total =
                        EXCLUDED.shots_total,

                    shots_on_target =
                        EXCLUDED.shots_on_target,

                    goals =
                        EXCLUDED.goals,

                    goals_conceded =
                        EXCLUDED.goals_conceded,

                    assists =
                        EXCLUDED.assists,

                    saves =
                        EXCLUDED.saves,

                    passes_total =
                        EXCLUDED.passes_total,

                    key_passes =
                        EXCLUDED.key_passes,

                    pass_accuracy =
                        EXCLUDED.pass_accuracy,

                    tackles =
                        EXCLUDED.tackles,

                    blocks =
                        EXCLUDED.blocks,

                    interceptions =
                        EXCLUDED.interceptions,

                    duels_total =
                        EXCLUDED.duels_total,

                    duels_won =
                        EXCLUDED.duels_won,

                    dribbles_attempted =
                        EXCLUDED.dribbles_attempted,

                    dribbles_successful =
                        EXCLUDED.dribbles_successful,

                    dribbled_past =
                        EXCLUDED.dribbled_past,

                    fouls_drawn =
                        EXCLUDED.fouls_drawn,

                    fouls_committed =
                        EXCLUDED.fouls_committed,

                    yellow_cards =
                        EXCLUDED.yellow_cards,

                    red_cards =
                        EXCLUDED.red_cards,

                    penalties_won =
                        EXCLUDED.penalties_won,

                    penalties_committed =
                        EXCLUDED.penalties_committed,

                    penalties_scored =
                        EXCLUDED.penalties_scored,

                    penalties_missed =
                        EXCLUDED.penalties_missed,

                    penalties_saved =
                        EXCLUDED.penalties_saved,

                    updated_at =
                        NOW();
                """,
                (
                    fixture_id,
                    player_id,
                    team_id,

                    games.get("minutes"),
                    games.get("number"),
                    games.get("position"),

                    rating,

                    games.get("captain"),
                    games.get("substitute"),

                    stats.get("offsides"),

                    shots.get("total"),
                    shots.get("on"),

                    goals.get("total"),
                    goals.get("conceded"),
                    goals.get("assists"),
                    goals.get("saves"),

                    passes.get("total"),
                    passes.get("key"),

                    parse_percentage(
                        passes.get(
                            "accuracy"
                        )
                    ),

                    tackles.get("total"),
                    tackles.get("blocks"),
                    tackles.get(
                        "interceptions"
                    ),

                    duels.get("total"),
                    duels.get("won"),

                    dribbles.get(
                        "attempts"
                    ),

                    dribbles.get(
                        "success"
                    ),

                    dribbles.get("past"),

                    fouls.get("drawn"),
                    fouls.get(
                        "committed"
                    ),

                    cards.get("yellow"),
                    cards.get("red"),

                    penalty.get("won"),

                    # API-Football spells this
                    # field "commited"
                    penalty.get(
                        "commited"
                    ),

                    penalty.get(
                        "scored"
                    ),

                    penalty.get(
                        "missed"
                    ),

                    penalty.get(
                        "saved"
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
            fetch_player_stats(
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
                "  No player statistics "
                "returned."
            )

            continue


        saved = save_fixture_stats(
            fixture_id,
            team_blocks,
        )


        total_saved += saved


        print(
            f"  {saved} player "
            f"stat rows saved."
        )


        # Small delay between API calls.
        time.sleep(0.25)


    print()
    print(
        "=============================="
    )

    print(
        "Player match stats import "
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