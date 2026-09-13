import argparse
import os
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from dotenv import load_dotenv

from football_config import LEAGUE_IDS


# ============================================================
# CONFIG
# ============================================================

DEFAULT_SEASON = 2025
DEFAULT_MIN_MINUTES = 900


# Stats that will be converted into per-90 values.
COUNTING_STATS = [
    "offsides",
    "shots_total",
    "shots_on_target",
    "goals",
    "assists",
    "passes_total",
    "key_passes",
    "tackles",
    "blocks",
    "interceptions",
    "duels_total",
    "duels_won",
    "dribbles_attempted",
    "dribbles_successful",
    "dribbled_past",
    "fouls_drawn",
    "fouls_committed",
    "yellow_cards",
    "red_cards",
    "penalties_won",
    "penalties_committed",
    "penalties_scored",
    "penalties_missed",
]


# ============================================================
# ARGUMENTS
# ============================================================

def get_args():

    parser = argparse.ArgumentParser(
        description=(
            "Build FutBud player-season archetype dataset."
        )
    )

    parser.add_argument(
        "--season",
        type=int,
        default=DEFAULT_SEASON,
        help="Season to build, e.g. 2025 or 2026",
    )

    parser.add_argument(
        "--min-minutes",
        type=int,
        default=DEFAULT_MIN_MINUTES,
        help=(
            "Minimum season minutes required for a player. "
            "Use 900 for completed seasons and a lower "
            "threshold such as 180 for the current season."
        ),
    )

    return parser.parse_args()


# ============================================================
# DATABASE
# ============================================================

def get_connection():

    load_dotenv()

    return psycopg.connect(
        host=os.getenv(
            "DB_HOST",
            "localhost",
        ),
        port=os.getenv(
            "DB_PORT",
            "5432",
        ),
        dbname=os.getenv(
            "DB_NAME",
            "futbud",
        ),
        user=os.getenv(
            "DB_USER",
            "futbud_user",
        ),
        password=os.getenv(
            "DB_PASSWORD",
        ),
    )


# ============================================================
# LOAD MATCH-LEVEL PLAYER DATA
# ============================================================

def load_match_player_data(
    season,
):

    placeholders = ", ".join(
        ["%s"] * len(LEAGUE_IDS)
    )

    query = f"""
        SELECT

            player_match_stats.match_id,
            matches.match_date,
            matches.league_id,

            leagues.name
                AS league_name,

            player_match_stats.player_id,

            players.name
                AS player_name,

            players.primary_position,

            players.photo_url,

            player_match_stats.team_id,

            teams.name
                AS team_name,

            player_match_stats.position,

            COALESCE(
                player_match_stats.minutes,
                0
            ) AS minutes,

            player_match_stats.provider_rating,

            player_match_stats.substitute,

            player_match_stats.offsides,

            player_match_stats.shots_total,
            player_match_stats.shots_on_target,

            player_match_stats.goals,
            player_match_stats.assists,

            player_match_stats.passes_total,
            player_match_stats.key_passes,

            player_match_stats.pass_accuracy,

            player_match_stats.tackles,
            player_match_stats.blocks,
            player_match_stats.interceptions,

            player_match_stats.duels_total,
            player_match_stats.duels_won,

            player_match_stats.dribbles_attempted,
            player_match_stats.dribbles_successful,
            player_match_stats.dribbled_past,

            player_match_stats.fouls_drawn,
            player_match_stats.fouls_committed,

            player_match_stats.yellow_cards,
            player_match_stats.red_cards,

            player_match_stats.penalties_won,
            player_match_stats.penalties_committed,
            player_match_stats.penalties_scored,
            player_match_stats.penalties_missed

        FROM player_match_stats

        JOIN matches
            ON matches.id =
               player_match_stats.match_id

        JOIN players
            ON players.id =
               player_match_stats.player_id

        JOIN teams
            ON teams.id =
               player_match_stats.team_id

        JOIN leagues
            ON leagues.id =
               matches.league_id

        WHERE matches.season = %s

          AND matches.league_id IN (
              {placeholders}
          )

        ORDER BY
            player_match_stats.player_id,
            matches.match_date;
    """

    params = [
        season,
        *LEAGUE_IDS,
    ]

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            cursor.execute(
                query,
                params,
            )

            column_names = [
                description.name
                for description
                in cursor.description
            ]

            rows = cursor.fetchall()

    finally:

        connection.close()

    return pd.DataFrame(
        rows,
        columns=column_names,
    )


# ============================================================
# POSITION
# ============================================================

def determine_primary_position(
    group,
):

    position_rows = group[
        group["position"].isin(
            [
                "G",
                "D",
                "M",
                "F",
            ]
        )
    ]

    if position_rows.empty:
        return None

    position_minutes = (
        position_rows
        .groupby(
            "position"
        )["minutes"]
        .sum()
    )

    if position_minutes.empty:
        return None

    return position_minutes.idxmax()


# ============================================================
# PRIMARY LEAGUE
# ============================================================

def determine_primary_league(
    group,
):

    league_minutes = (
        group
        .groupby(
            [
                "league_id",
                "league_name",
            ]
        )["minutes"]
        .sum()
        .reset_index()
    )

    if league_minutes.empty:

        return (
            None,
            None,
        )

    league_row = (
        league_minutes
        .sort_values(
            "minutes",
            ascending=False,
        )
        .iloc[0]
    )

    return (
        int(
            league_row[
                "league_id"
            ]
        ),
        league_row[
            "league_name"
        ],
    )


# ============================================================
# LATEST TEAM
# ============================================================

def determine_latest_team(
    group,
):

    valid = group[
        group["team_id"].notna()
    ].copy()

    if valid.empty:

        return (
            None,
            None,
        )

    valid = valid.sort_values(
        [
            "match_date",
            "match_id",
        ],
        ascending=True,
    )

    latest = valid.iloc[-1]

    return (
        int(
            latest[
                "team_id"
            ]
        ),
        latest[
            "team_name"
        ],
    )


# ============================================================
# PROVIDER RATING
# ============================================================

def calculate_weighted_provider_rating(
    group,
):

    valid = group[
        group[
            "provider_rating"
        ].notna()
    ].copy()

    if valid.empty:
        return None

    valid[
        "provider_rating"
    ] = pd.to_numeric(
        valid[
            "provider_rating"
        ],
        errors="coerce",
    )

    valid[
        "minutes"
    ] = pd.to_numeric(
        valid[
            "minutes"
        ],
        errors="coerce",
    ).fillna(0)

    valid = valid[
        valid[
            "provider_rating"
        ].notna()
    ]

    if valid.empty:
        return None

    positive_minutes = valid[
        valid["minutes"] > 0
    ]

    if not positive_minutes.empty:

        return np.average(
            positive_minutes[
                "provider_rating"
            ],
            weights=positive_minutes[
                "minutes"
            ],
        )

    return valid[
        "provider_rating"
    ].mean()


# ============================================================
# PASS ACCURACY
#
# IMPORTANT:
#
# In the API-Football data currently stored in FutBud,
# player_match_stats.pass_accuracy behaves as the number
# of accurate/completed passes, despite the misleading
# field name.
#
# Season accuracy therefore needs to be:
#
# accurate passes / attempted passes
#
# NOT an average of match percentages.
# ============================================================

def calculate_pass_accuracy(
    group,
):

    valid = group[
        (
            group[
                "passes_total"
            ].fillna(0)
            >
            0
        )
        &
        (
            group[
                "pass_accuracy"
            ].notna()
        )
    ]

    if valid.empty:
        return None

    total_passes = (
        valid[
            "passes_total"
        ]
        .sum()
    )

    accurate_passes = (
        valid[
            "pass_accuracy"
        ]
        .sum()
    )

    if total_passes <= 0:
        return None

    return (
        accurate_passes
        /
        total_passes
        *
        100
    )


# ============================================================
# GENERIC RATE
# ============================================================

def calculate_rate(
    numerator,
    denominator,
):

    if (
        denominator is None
        or
        denominator <= 0
    ):
        return None

    return (
        numerator
        /
        denominator
        *
        100
    )


# ============================================================
# AGGREGATE ONE PLAYER
# ============================================================

def aggregate_player(
    group,
):

    group = group.copy()

    group[
        "minutes"
    ] = pd.to_numeric(
        group[
            "minutes"
        ],
        errors="coerce",
    ).fillna(0)


    # --------------------------------------------------------
    # Identity
    # --------------------------------------------------------

    player_id = int(
        group[
            "player_id"
        ].iloc[0]
    )

    player_name = (
        group[
            "player_name"
        ].iloc[0]
    )

    photo_url = (
        group[
            "photo_url"
        ].iloc[0]
    )

    database_primary_position = (
        group[
            "primary_position"
        ].iloc[0]
    )


    # --------------------------------------------------------
    # Season position
    # --------------------------------------------------------

    position = (
        determine_primary_position(
            group
        )
    )


    # --------------------------------------------------------
    # League
    # --------------------------------------------------------

    (
        primary_league_id,
        primary_league_name,
    ) = determine_primary_league(
        group
    )


    # --------------------------------------------------------
    # Latest team
    # --------------------------------------------------------

    (
        latest_team_id,
        latest_team_name,
    ) = determine_latest_team(
        group
    )


    # --------------------------------------------------------
    # Minutes / appearances
    # --------------------------------------------------------

    minutes = int(
        group[
            "minutes"
        ].sum()
    )

    appearances = int(
        group[
            "match_id"
        ].nunique()
    )


    # --------------------------------------------------------
    # Starts
    #
    # substitute = False generally indicates starting XI.
    # --------------------------------------------------------

    if (
        "substitute"
        in group.columns
    ):

        starts = int(
            (
                group[
                    "substitute"
                ]
                ==
                False
            ).sum()
        )

    else:

        starts = None


    # --------------------------------------------------------
    # Provider rating
    # --------------------------------------------------------

    provider_rating = (
        calculate_weighted_provider_rating(
            group
        )
    )


    # --------------------------------------------------------
    # Aggregate counting statistics
    # --------------------------------------------------------

    totals = {}

    for stat in COUNTING_STATS:

        if stat not in group.columns:

            totals[
                stat
            ] = 0

            continue

        totals[
            stat
        ] = (
            pd.to_numeric(
                group[
                    stat
                ],
                errors="coerce",
            )
            .fillna(0)
            .sum()
        )


    # --------------------------------------------------------
    # Rate statistics
    # --------------------------------------------------------

    shot_accuracy_pct = (
        calculate_rate(
            totals[
                "shots_on_target"
            ],
            totals[
                "shots_total"
            ],
        )
    )


    duel_win_pct = (
        calculate_rate(
            totals[
                "duels_won"
            ],
            totals[
                "duels_total"
            ],
        )
    )


    dribble_success_pct = (
        calculate_rate(
            totals[
                "dribbles_successful"
            ],
            totals[
                "dribbles_attempted"
            ],
        )
    )


    pass_accuracy_pct = (
        calculate_pass_accuracy(
            group
        )
    )


    # --------------------------------------------------------
    # Base row
    # --------------------------------------------------------

    row = {

        "player_id":
            player_id,

        "player_name":
            player_name,

        "photo_url":
            photo_url,

        "database_primary_position":
            database_primary_position,

        "position":
            position,

        "primary_league_id":
            primary_league_id,

        "primary_league_name":
            primary_league_name,

        "latest_team_id":
            latest_team_id,

        "latest_team_name":
            latest_team_name,

        "minutes":
            minutes,

        "appearances":
            appearances,

        "starts":
            starts,

        "provider_rating":
            provider_rating,

        "shot_accuracy_pct":
            shot_accuracy_pct,

        "pass_accuracy_pct":
            pass_accuracy_pct,

        "duel_win_pct":
            duel_win_pct,

        "dribble_success_pct":
            dribble_success_pct,
    }


    # --------------------------------------------------------
    # Raw totals
    # --------------------------------------------------------

    for stat in COUNTING_STATS:

        row[
            stat
        ] = totals[
            stat
        ]


    # --------------------------------------------------------
    # Per-90 stats
    # --------------------------------------------------------

    for stat in COUNTING_STATS:

        column_name = (
            f"{stat}_per90"
        )

        if minutes > 0:

            row[
                column_name
            ] = (
                totals[
                    stat
                ]
                /
                minutes
                *
                90
            )

        else:

            row[
                column_name
            ] = None


    return row


# ============================================================
# BUILD PLAYER-SEASON DATASET
# ============================================================

def build_player_dataset(
    match_player_data,
):

    rows = []

    grouped = (
        match_player_data
        .groupby(
            "player_id",
            sort=False,
        )
    )


    for _, group in grouped:

        row = aggregate_player(
            group
        )

        rows.append(
            row
        )


    return pd.DataFrame(
        rows
    )


# ============================================================
# FILTER DATASET
# ============================================================

def filter_dataset(
    dataset,
    min_minutes,
):

    dataset = dataset.copy()


    # --------------------------------------------------------
    # We are not modeling goalkeepers yet.
    # --------------------------------------------------------

    dataset = dataset[
        dataset[
            "position"
        ].isin(
            [
                "D",
                "M",
                "F",
            ]
        )
    ].copy()


    # --------------------------------------------------------
    # Minimum sample size.
    # --------------------------------------------------------

    dataset = dataset[
        dataset[
            "minutes"
        ]
        >=
        min_minutes
    ].copy()


    dataset = dataset.reset_index(
        drop=True
    )


    return dataset


# ============================================================
# OUTPUT PATH
# ============================================================

def get_output_path(
    season,
):

    base_directory = Path(
        __file__
    ).parent

    data_directory = (
        base_directory
        /
        "data"
    )

    data_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return (
        data_directory
        /
        f"top5_archetypes_{season}.csv"
    )


# ============================================================
# PRINT SUMMARY
# ============================================================

def print_summary(
    dataset_before_filter,
    dataset,
    min_minutes,
):

    print()

    print(
        "Players before filtering:",
        len(
            dataset_before_filter
        ),
    )

    print(
        "Players after filtering:",
        len(
            dataset
        ),
    )

    print(
        "Minimum minutes:",
        min_minutes,
    )


    print()
    print(
        "Position counts:"
    )

    print(
        dataset[
            "position"
        ]
        .value_counts()
        .to_string()
    )


    print()
    print(
        "League counts:"
    )

    print(
        dataset[
            "primary_league_name"
        ]
        .value_counts()
        .to_string()
    )


    print()
    print(
        "Minutes:"
    )

    print(
        dataset[
            "minutes"
        ]
        .describe()
        .to_string()
    )


# ============================================================
# MAIN
# ============================================================

def main():

    args = get_args()

    season = (
        args.season
    )

    min_minutes = (
        args.min_minutes
    )


    if min_minutes < 0:

        raise ValueError(
            "--min-minutes cannot be negative."
        )


    print()
    print(
        "========================================"
    )

    print(
        "FutBud Archetype Dataset Builder"
    )

    print(
        "========================================"
    )

    print(
        f"Season: {season}"
    )

    print(
        f"Minimum minutes: "
        f"{min_minutes}"
    )


    # ========================================================
    # LOAD MATCH DATA
    # ========================================================

    match_player_data = (
        load_match_player_data(
            season
        )
    )


    print()

    print(
        "Match-player rows loaded:",
        len(
            match_player_data
        ),
    )


    if match_player_data.empty:

        raise ValueError(
            f"No player match data found "
            f"for season {season}."
        )


    # ========================================================
    # AGGREGATE
    # ========================================================

    player_dataset = (
        build_player_dataset(
            match_player_data
        )
    )


    unfiltered_dataset = (
        player_dataset.copy()
    )


    # ========================================================
    # FILTER
    # ========================================================

    player_dataset = (
        filter_dataset(
            player_dataset,
            min_minutes,
        )
    )


    # ========================================================
    # SORT
    # ========================================================

    player_dataset = (
        player_dataset
        .sort_values(
            [
                "position",
                "minutes",
                "player_name",
            ],
            ascending=[
                True,
                False,
                True,
            ],
        )
        .reset_index(
            drop=True
        )
    )


    # ========================================================
    # PRINT SUMMARY
    # ========================================================

    print_summary(
        unfiltered_dataset,
        player_dataset,
        min_minutes,
    )


    # ========================================================
    # SAVE
    # ========================================================

    output_path = (
        get_output_path(
            season
        )
    )


    player_dataset.to_csv(
        output_path,
        index=False,
    )


    print()
    print(
        "========================================"
    )

    print(
        "Dataset complete."
    )

    print(
        "========================================"
    )

    print(
        f"Saved to: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()