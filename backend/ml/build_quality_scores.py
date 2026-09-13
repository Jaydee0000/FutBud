import argparse
from pathlib import Path

import pandas as pd

from ml.quality_features import (
    QUALITY_FEATURES,
    QUALITY_WEIGHTS,
    LOWER_IS_BETTER,
    ARCHETYPE_DISPLAY_NAMES,
)


DEFAULT_SEASON = 2025


# ============================================================
# FINAL ARCHETYPE MAPPINGS
# ============================================================


# ------------------------------------------------------------
# DEFENDERS
# ------------------------------------------------------------

DEFENDER_CLUSTER_MAP = {
    0: "positional_cb",
    1: "high_intensity_fullback",
    2: "stopper_cb",
    3: "creative_fullback",
}


# ------------------------------------------------------------
# MIDFIELD ORIENTATION
# ------------------------------------------------------------

MIDFIELD_ORIENTATION_MAP = {
    0: "wide",
    1: "central",
}


# ------------------------------------------------------------
# CENTRAL MIDFIELDERS
#
# Final k=3 interpretation:
#
# Cluster 0 -> AM / 10
# Cluster 1 -> DM / 6
# Cluster 2 -> CM / 8
# ------------------------------------------------------------

CENTRAL_MIDFIELD_CLUSTER_MAP = {
    0: "attacking_midfielder",
    1: "defensive_midfielder",
    2: "box_to_box_midfielder",
}


# ------------------------------------------------------------
# WIDE-ORIENTED MIDFIELDERS
#
# Final k=2 interpretation:
#
# Cluster 0 -> creative / attacking -> 8/10 Hybrid
# Cluster 1 -> defensive / physical -> 6/8 Hybrid
# ------------------------------------------------------------

WIDE_MIDFIELD_CLUSTER_MAP = {
    0: "eight_ten_hybrid",
    1: "six_eight_hybrid",
}


# ------------------------------------------------------------
# FORWARD ORIENTATION
#
# Cluster 0 -> wide forward
# Cluster 1 -> traditional No. 9
# ------------------------------------------------------------

FORWARD_ORIENTATION_MAP = {
    0: "wide",
    1: "central",
}


# ------------------------------------------------------------
# WIDE FORWARDS
#
# Final k=2 interpretation:
#
# Cluster 0 -> Direct Winger
# Cluster 1 -> Linking Winger
# ------------------------------------------------------------

WIDE_FORWARD_CLUSTER_MAP = {
    0: "direct_winger",
    1: "linking_winger",
}


# ============================================================
# STATUS BANDS
#
# These are applied to the player's percentile within their
# own archetype, NOT directly to the weighted rating.
# ============================================================

def get_status(percentile):

    if pd.isna(percentile):
        return None

    if percentile >= 95:
        return "Elite"

    if percentile >= 85:
        return "Excellent"

    if percentile >= 70:
        return "Very Good"

    if percentile >= 55:
        return "Good"

    if percentile >= 40:
        return "Average"

    if percentile >= 25:
        return "Below Average"

    return "Poor"


# ============================================================
# ARGUMENTS
# ============================================================

def get_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--season",
        type=int,
        default=DEFAULT_SEASON,
    )

    return parser.parse_args()


# ============================================================
# PATHS
# ============================================================

def get_paths(season):

    base_directory = Path(__file__).parent

    paths = {

        "base_dataset":
            base_directory
            / "data"
            / f"top5_archetypes_{season}.csv",

        "defenders":
            base_directory
            / "output"
            / f"archetype_assignments_{season}_D.csv",

        "midfield_orientation":
            base_directory
            / "output"
            / f"midfield_orientation_assignments_{season}.csv",

        "midfield_central":
            base_directory
            / "output"
            / (
                f"midfielder_archetype_"
                f"assignments_{season}_central.csv"
            ),

        "midfield_wide":
            base_directory
            / "output"
            / (
                f"midfielder_archetype_"
                f"assignments_{season}_wide.csv"
            ),

        "forward_orientation":
            base_directory
            / "output"
            / f"archetype_assignments_{season}_F.csv",

        "forward_wide":
            base_directory
            / "output"
            / (
                f"forward_archetype_"
                f"assignments_{season}_wide.csv"
            ),
    }

    output_directory = (
        base_directory
        / "output"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return (
        paths,
        output_directory,
    )


# ============================================================
# CSV LOADING
# ============================================================

def read_required_csv(
    path,
    description,
):

    if not path.exists():

        raise FileNotFoundError(
            f"{description} not found:\n"
            f"{path}"
        )

    return pd.read_csv(path)


# ============================================================
# MAP CLUSTER ASSIGNMENTS TO FINAL ROLE NAMES
# ============================================================

def map_assignment(
    players,
    assignments,
    cluster_column,
    cluster_map,
):

    assignment_map = (
        assignments[
            [
                "player_id",
                cluster_column,
            ]
        ]
        .drop_duplicates(
            subset=["player_id"]
        )
        .set_index("player_id")[
            cluster_column
        ]
        .map(cluster_map)
    )

    return players[
        "player_id"
    ].map(
        assignment_map
    )


# ============================================================
# ASSIGN FINAL ARCHETYPES
# ============================================================

def assign_final_archetypes(
    players,
    paths,
):

    players = players.copy()

    players[
        "orientation"
    ] = pd.NA

    players[
        "archetype_key"
    ] = pd.NA


    # ========================================================
    # DEFENDERS
    # ========================================================

    defender_assignments = (
        read_required_csv(
            paths["defenders"],
            "Defender assignments",
        )
    )

    defender_roles = map_assignment(
        players,
        defender_assignments,
        "cluster",
        DEFENDER_CLUSTER_MAP,
    )

    defender_mask = (
        players["position"]
        ==
        "D"
    )

    players.loc[
        defender_mask,
        "archetype_key",
    ] = defender_roles[
        defender_mask
    ]


    # ========================================================
    # MIDFIELDERS
    # ========================================================

    midfield_orientation = (
        read_required_csv(
            paths["midfield_orientation"],
            "Midfielder orientation assignments",
        )
    )

    midfield_orientation_values = (
        map_assignment(
            players,
            midfield_orientation,
            "orientation_cluster",
            MIDFIELD_ORIENTATION_MAP,
        )
    )

    midfielder_mask = (
        players["position"]
        ==
        "M"
    )

    players.loc[
        midfielder_mask,
        "orientation",
    ] = midfield_orientation_values[
        midfielder_mask
    ]


    # --------------------------------------------------------
    # CENTRAL MIDFIELDERS
    # --------------------------------------------------------

    central_midfield_assignments = (
        read_required_csv(
            paths["midfield_central"],
            "Central midfielder archetype assignments",
        )
    )

    central_roles = map_assignment(
        players,
        central_midfield_assignments,
        "archetype_cluster",
        CENTRAL_MIDFIELD_CLUSTER_MAP,
    )

    central_midfield_mask = (
        (players["position"] == "M")
        &
        (players["orientation"] == "central")
    )

    players.loc[
        central_midfield_mask,
        "archetype_key",
    ] = central_roles[
        central_midfield_mask
    ]


    # --------------------------------------------------------
    # WIDE-ORIENTED MIDFIELDERS
    # --------------------------------------------------------

    wide_midfield_assignments = (
        read_required_csv(
            paths["midfield_wide"],
            "Wide midfielder archetype assignments",
        )
    )

    wide_midfield_roles = (
        map_assignment(
            players,
            wide_midfield_assignments,
            "archetype_cluster",
            WIDE_MIDFIELD_CLUSTER_MAP,
        )
    )

    wide_midfield_mask = (
        (players["position"] == "M")
        &
        (players["orientation"] == "wide")
    )

    players.loc[
        wide_midfield_mask,
        "archetype_key",
    ] = wide_midfield_roles[
        wide_midfield_mask
    ]


    # ========================================================
    # FORWARDS
    # ========================================================

    forward_orientation = (
        read_required_csv(
            paths["forward_orientation"],
            "Forward orientation assignments",
        )
    )

    forward_orientation_values = (
        map_assignment(
            players,
            forward_orientation,
            "cluster",
            FORWARD_ORIENTATION_MAP,
        )
    )

    forward_mask = (
        players["position"]
        ==
        "F"
    )

    players.loc[
        forward_mask,
        "orientation",
    ] = forward_orientation_values[
        forward_mask
    ]


    # --------------------------------------------------------
    # TRADITIONAL NO. 9
    # --------------------------------------------------------

    traditional_9_mask = (
        (players["position"] == "F")
        &
        (players["orientation"] == "central")
    )

    players.loc[
        traditional_9_mask,
        "archetype_key",
    ] = "traditional_9"


    # --------------------------------------------------------
    # WIDE FORWARDS
    # --------------------------------------------------------

    wide_forward_assignments = (
        read_required_csv(
            paths["forward_wide"],
            "Wide forward archetype assignments",
        )
    )

    wide_forward_roles = (
        map_assignment(
            players,
            wide_forward_assignments,
            "archetype_cluster",
            WIDE_FORWARD_CLUSTER_MAP,
        )
    )

    wide_forward_mask = (
        (players["position"] == "F")
        &
        (players["orientation"] == "wide")
    )

    players.loc[
        wide_forward_mask,
        "archetype_key",
    ] = wide_forward_roles[
        wide_forward_mask
    ]


    # ========================================================
    # HUMAN-READABLE ROLE NAME
    # ========================================================

    players[
        "archetype_name"
    ] = players[
        "archetype_key"
    ].map(
        ARCHETYPE_DISPLAY_NAMES
    )

    return players


# ============================================================
# CHECK FINAL ROLE ASSIGNMENTS
# ============================================================

def validate_assignments(players):

    missing = players[
        players[
            "archetype_key"
        ].isna()
    ]

    print()
    print(
        "========================================"
    )

    print(
        "FINAL ARCHETYPE COUNTS"
    )

    print(
        "========================================"
    )

    print(
        players[
            "archetype_name"
        ]
        .value_counts(
            dropna=False
        )
        .to_string()
    )


    duplicate_ids = (
        players[
            "player_id"
        ]
        .duplicated()
        .sum()
    )

    print()
    print(
        f"Duplicate player IDs: "
        f"{duplicate_ids}"
    )


    if duplicate_ids > 0:

        raise ValueError(
            "Duplicate player IDs found."
        )


    if not missing.empty:

        print()
        print(
            f"WARNING: "
            f"{len(missing)} players "
            f"have no final archetype."
        )

        print()

        columns = [
            column
            for column in [
                "player_id",
                "player_name",
                "position",
                "orientation",
            ]
            if column in missing.columns
        ]

        print(
            missing[
                columns
            ]
            .head(30)
            .to_string(
                index=False
            )
        )

        raise ValueError(
            "Some players are missing "
            "archetype assignments."
        )


# ============================================================
# PERCENTILE CALCULATION
# ============================================================

def calculate_percentiles(series):

    numeric_series = pd.to_numeric(
        series,
        errors="coerce",
    )

    valid_count = (
        numeric_series
        .notna()
        .sum()
    )

    result = pd.Series(
        index=series.index,
        dtype=float,
    )


    if valid_count == 0:

        return result


    if valid_count == 1:

        result.loc[
            numeric_series.notna()
        ] = 50.0

        return result


    ranks = (
        numeric_series.rank(
            method="average",
            na_option="keep",
        )
    )


    percentiles = (
        (
            ranks
            -
            1
        )
        /
        (
            valid_count
            -
            1
        )
        *
        100
    )

    return percentiles


# ============================================================
# MINUTES RELIABILITY
# ============================================================

def calculate_minutes_reliability(
    players,
    role_mask,
):

    if (
        "total_minutes"
        in players.columns
    ):

        minutes = pd.to_numeric(
            players.loc[
                role_mask,
                "total_minutes",
            ],
            errors="coerce",
        )

    elif (
        "minutes"
        in players.columns
    ):

        minutes = pd.to_numeric(
            players.loc[
                role_mask,
                "minutes",
            ],
            errors="coerce",
        )

    else:

        minutes = pd.Series(
            2700.0,
            index=players.loc[
                role_mask
            ].index,
        )


    minutes = (
        minutes
        .fillna(900)
    )


    # --------------------------------------------------------
    # Reliability curve
    #
    # 900 minutes  -> about 86.7%
    # 1800 minutes -> about 93.3%
    # 2700+        -> 100%
    #
    # This does NOT massively punish smaller samples.
    # It only pulls extreme scores slightly toward 50.
    # --------------------------------------------------------

    reliability = (
        0.80
        +
        (
            0.20
            *
            (
                minutes.clip(
                    lower=0,
                    upper=2700,
                )
                /
                2700
            )
        )
    )

    return reliability


# ============================================================
# QUALITY SCORING
# ============================================================

def calculate_quality_scores(players):

    players = players.copy()


    players[
        "raw_quality_rating"
    ] = float("nan")

    players[
        "minutes_reliability"
    ] = float("nan")

    players[
        "futbud_rating"
    ] = float("nan")

    players[
        "role_rating_percentile"
    ] = float("nan")

    players[
        "quality_status"
    ] = pd.NA

    players[
        "quality_metric_count"
    ] = 0


    detailed_rows = []


    # ========================================================
    # SCORE EACH ARCHETYPE SEPARATELY
    # ========================================================

    for (
        archetype_key,
        features,
    ) in QUALITY_FEATURES.items():

        role_mask = (
            players[
                "archetype_key"
            ]
            ==
            archetype_key
        )

        role_players = (
            players.loc[
                role_mask
            ]
        )


        if role_players.empty:

            continue


        print()
        print(
            f"Scoring "
            f"{ARCHETYPE_DISPLAY_NAMES[archetype_key]}"
        )

        print(
            f"Players: "
            f"{len(role_players)}"
        )


        weights = (
            QUALITY_WEIGHTS[
                archetype_key
            ]
        )


        # ----------------------------------------------------
        # Make sure weights and features match
        # ----------------------------------------------------

        if (
            set(weights.keys())
            !=
            set(features)
        ):

            raise ValueError(
                f"Weight configuration does not "
                f"match features for "
                f"{archetype_key}."
            )


        weight_sum = sum(
            weights.values()
        )


        if abs(
            weight_sum
            -
            1.0
        ) > 0.001:

            raise ValueError(
                f"Weights for "
                f"{archetype_key} "
                f"sum to {weight_sum}, "
                f"not 1.0."
            )


        percentile_columns = []


        # ====================================================
        # CALCULATE ROLE-RELATIVE PERCENTILES
        # ====================================================

        for feature in features:

            if (
                feature
                not in players.columns
            ):

                raise ValueError(
                    f"Feature '{feature}' "
                    f"does not exist "
                    f"in the player dataset."
                )


            raw_values = (
                players.loc[
                    role_mask,
                    feature,
                ]
            )


            percentiles = (
                calculate_percentiles(
                    raw_values
                )
            )


            # ------------------------------------------------
            # Reverse negative metrics
            # ------------------------------------------------

            if (
                feature
                in LOWER_IS_BETTER
            ):

                percentiles = (
                    100
                    -
                    percentiles
                )


            percentile_column = (
                f"{feature}_quality"
            )


            players.loc[
                role_mask,
                percentile_column,
            ] = percentiles


            percentile_columns.append(
                percentile_column
            )


            # ------------------------------------------------
            # Save detailed stat explanation
            # ------------------------------------------------

            for player_index in (
                role_players.index
            ):

                detailed_rows.append(
                    {

                        "player_id":
                            players.at[
                                player_index,
                                "player_id",
                            ],

                        "player_name":
                            players.at[
                                player_index,
                                "player_name",
                            ],

                        "archetype_key":
                            archetype_key,

                        "archetype_name":
                            ARCHETYPE_DISPLAY_NAMES[
                                archetype_key
                            ],

                        "feature":
                            feature,

                        "weight":
                            weights[
                                feature
                            ],

                        "raw_value":
                            players.at[
                                player_index,
                                feature,
                            ],

                        "percentile":
                            players.at[
                                player_index,
                                percentile_column,
                            ],
                    }
                )


        # ====================================================
        # WEIGHTED ROLE SCORE
        # ====================================================

        role_percentiles = (
            players.loc[
                role_mask,
                percentile_columns,
            ]
        )


        weighted_total = pd.Series(
            0.0,
            index=role_percentiles.index,
        )


        available_weight = pd.Series(
            0.0,
            index=role_percentiles.index,
        )


        for feature in features:

            percentile_column = (
                f"{feature}_quality"
            )

            weight = (
                weights[
                    feature
                ]
            )


            valid = (
                role_percentiles[
                    percentile_column
                ]
                .notna()
            )


            weighted_total.loc[
                valid
            ] += (
                role_percentiles.loc[
                    valid,
                    percentile_column,
                ]
                *
                weight
            )


            available_weight.loc[
                valid
            ] += weight


        raw_quality_rating = (
            weighted_total
            /
            available_weight.replace(
                0,
                pd.NA,
            )
        )


        # ====================================================
        # MINUTES RELIABILITY
        # ====================================================

        reliability = (
            calculate_minutes_reliability(
                players,
                role_mask,
            )
        )


        # ----------------------------------------------------
        # Pull lower-minute extreme ratings toward 50.
        #
        # Example:
        #
        # Raw rating = 90
        # reliability = 0.87
        #
        # adjusted =
        # 50 + (90 - 50) * 0.87
        # ----------------------------------------------------

        adjusted_rating = (
            50
            +
            (
                raw_quality_rating
                -
                50
            )
            *
            reliability
        )


        metric_count = (
            role_percentiles
            .notna()
            .sum(
                axis=1
            )
        )


        players.loc[
            role_mask,
            "raw_quality_rating",
        ] = raw_quality_rating


        players.loc[
            role_mask,
            "minutes_reliability",
        ] = (
            reliability
            *
            100
        )


        players.loc[
            role_mask,
            "futbud_rating",
        ] = adjusted_rating


        players.loc[
            role_mask,
            "quality_metric_count",
        ] = metric_count


    # ========================================================
    # ROUND RATINGS
    # ========================================================

    players[
        "raw_quality_rating"
    ] = pd.to_numeric(
        players[
            "raw_quality_rating"
        ],
        errors="coerce",
    ).round(1)


    players[
        "minutes_reliability"
    ] = pd.to_numeric(
        players[
            "minutes_reliability"
        ],
        errors="coerce",
    ).round(1)


    players[
        "futbud_rating"
    ] = pd.to_numeric(
        players[
            "futbud_rating"
        ],
        errors="coerce",
    ).round(1)


    # ========================================================
    # RANK FINAL RATING WITHIN ROLE
    #
    # This is what determines:
    #
    # Elite
    # Excellent
    # Very Good
    # etc.
    #
    # It prevents us from requiring an impossible composite
    # score such as 95/100 to qualify as "Elite".
    # ========================================================

    players[
        "role_rating_percentile"
    ] = (
        players
        .groupby(
            "archetype_key"
        )[
            "futbud_rating"
        ]
        .rank(
            pct=True,
            method="average",
        )
        *
        100
    )


    players[
        "role_rating_percentile"
    ] = (
        players[
            "role_rating_percentile"
        ]
        .round(1)
    )


    players[
        "quality_status"
    ] = (
        players[
            "role_rating_percentile"
        ]
        .apply(
            get_status
        )
    )


    # ========================================================
    # DETAILED OUTPUT
    # ========================================================

    detailed = pd.DataFrame(
        detailed_rows
    )


    if not detailed.empty:

        detailed[
            "percentile"
        ] = pd.to_numeric(
            detailed[
                "percentile"
            ],
            errors="coerce",
        ).round(1)


        detailed[
            "raw_value"
        ] = pd.to_numeric(
            detailed[
                "raw_value"
            ],
            errors="coerce",
        ).round(3)


        detailed[
            "weight"
        ] = pd.to_numeric(
            detailed[
                "weight"
            ],
            errors="coerce",
        ).round(3)


    return (
        players,
        detailed,
    )


# ============================================================
# PROVIDER-RATING SANITY CHECK
# ============================================================

def print_provider_comparison(players):

    possible_provider_columns = [
        "provider_rating",
        "weighted_provider_rating",
        "average_provider_rating",
    ]


    provider_column = None


    for column in (
        possible_provider_columns
    ):

        if (
            column
            in players.columns
        ):

            provider_column = column
            break


    if provider_column is None:

        return


    comparison = (
        players[
            [
                "futbud_rating",
                provider_column,
            ]
        ]
        .apply(
            pd.to_numeric,
            errors="coerce",
        )
        .dropna()
    )


    if len(comparison) < 2:

        return


    correlation = (
        comparison[
            "futbud_rating"
        ]
        .corr(
            comparison[
                provider_column
            ]
        )
    )


    print()
    print(
        "========================================"
    )

    print(
        "PROVIDER SANITY CHECK"
    )

    print(
        "========================================"
    )

    print(
        f"FutBud vs provider rating "
        f"correlation: "
        f"{correlation:.3f}"
    )

    print()

    print(
        "Provider rating is NOT used "
        "to calculate FutBud Rating."
    )


# ============================================================
# PRINT TOP PLAYERS BY ROLE
# ============================================================

def print_top_players(players):

    print()
    print(
        "========================================"
    )

    print(
        "TOP PLAYERS BY ARCHETYPE"
    )

    print(
        "========================================"
    )


    for archetype_name in sorted(
        players[
            "archetype_name"
        ]
        .dropna()
        .unique()
    ):

        print()
        print(
            "-" * 80
        )

        print(
            archetype_name
        )

        print(
            "-" * 80
        )


        group = (
            players[
                players[
                    "archetype_name"
                ]
                ==
                archetype_name
            ]
            .sort_values(
                "futbud_rating",
                ascending=False,
            )
            .head(10)
        )


        columns = [
            column
            for column in [
                "player_name",
                "latest_team_name",
                "futbud_rating",
                "role_rating_percentile",
                "quality_status",
                "minutes_reliability",
            ]
            if column in group.columns
        ]


        print(
            group[
                columns
            ]
            .to_string(
                index=False
            )
        )


# ============================================================
# SAVE OUTPUTS
# ============================================================

def save_outputs(
    players,
    detailed,
    output_directory,
    season,
):

    summary_path = (
        output_directory
        /
        f"quality_scores_{season}.csv"
    )


    detailed_path = (
        output_directory
        /
        f"quality_percentiles_{season}.csv"
    )


    preferred_columns = [

        "player_id",
        "player_name",

        "position",
        "orientation",

        "archetype_key",
        "archetype_name",

        "minutes",
        "total_minutes",

        "latest_team_name",
        "primary_league_name",
        "league_name",

        "provider_rating",
        "weighted_provider_rating",

        "raw_quality_rating",
        "minutes_reliability",

        "futbud_rating",

        "role_rating_percentile",

        "quality_status",

        "quality_metric_count",
    ]


    summary_columns = [
        column
        for column in (
            preferred_columns
        )
        if column in players.columns
    ]


    quality_columns = [
        column
        for column in (
            players.columns
        )
        if column.endswith(
            "_quality"
        )
    ]


    summary_columns.extend(
        quality_columns
    )


    players[
        summary_columns
    ].to_csv(
        summary_path,
        index=False,
    )


    detailed.to_csv(
        detailed_path,
        index=False,
    )


    return (
        summary_path,
        detailed_path,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    args = get_args()

    season = (
        args.season
    )


    (
        paths,
        output_directory,
    ) = get_paths(
        season
    )


    print()
    print(
        "========================================"
    )

    print(
        "FutBud Quality Rating Builder"
    )

    print(
        "========================================"
    )

    print(
        f"Season: {season}"
    )


    players = (
        read_required_csv(
            paths[
                "base_dataset"
            ],
            "Archetype dataset",
        )
    )


    print(
        f"Players loaded: "
        f"{len(players)}"
    )


    # ========================================================
    # ASSIGN FINAL ROLES
    # ========================================================

    players = (
        assign_final_archetypes(
            players,
            paths,
        )
    )


    validate_assignments(
        players
    )


    # ========================================================
    # CALCULATE QUALITY SCORES
    # ========================================================

    (
        scored_players,
        detailed,
    ) = (
        calculate_quality_scores(
            players
        )
    )


    # ========================================================
    # SANITY CHECK AGAINST PROVIDER
    # ========================================================

    print_provider_comparison(
        scored_players
    )


    # ========================================================
    # PRINT TOP 10 IN EACH ROLE
    # ========================================================

    print_top_players(
        scored_players
    )


    # ========================================================
    # SAVE
    # ========================================================

    (
        summary_path,
        detailed_path,
    ) = save_outputs(
        scored_players,
        detailed,
        output_directory,
        season,
    )


    print()
    print(
        "========================================"
    )

    print(
        "QUALITY SCORING COMPLETE"
    )

    print(
        "========================================"
    )

    print(
        f"Ratings: "
        f"{summary_path}"
    )

    print(
        f"Metric percentiles: "
        f"{detailed_path}"
    )


if __name__ == "__main__":
    main()