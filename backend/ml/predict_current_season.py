import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from ml.quality_features import (
    QUALITY_FEATURES,
    QUALITY_WEIGHTS,
    LOWER_IS_BETTER,
    ARCHETYPE_DISPLAY_NAMES,
)


DEFAULT_SEASON = 2026
DEFAULT_REFERENCE_SEASON = 2025


# ============================================================
# FINAL V1 CLUSTER MAPPINGS
# ============================================================

DEFENDER_CLUSTER_MAP = {
    0: "positional_cb",
    1: "high_intensity_fullback",
    2: "stopper_cb",
    3: "creative_fullback",
}


MIDFIELD_ORIENTATION_MAP = {
    0: "wide",
    1: "central",
}


CENTRAL_MIDFIELD_CLUSTER_MAP = {
    0: "attacking_midfielder",
    1: "defensive_midfielder",
    2: "box_to_box_midfielder",
}


WIDE_MIDFIELD_CLUSTER_MAP = {
    0: "eight_ten_hybrid",
    1: "six_eight_hybrid",
}


FORWARD_ORIENTATION_MAP = {
    0: "wide",
    1: "central",
}


WIDE_FORWARD_CLUSTER_MAP = {
    0: "direct_winger",
    1: "linking_winger",
}


# ============================================================
# STATUS
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

    parser = argparse.ArgumentParser(
        description=(
            "Apply frozen FutBud models "
            "to a current season."
        )
    )

    parser.add_argument(
        "--season",
        type=int,
        default=DEFAULT_SEASON,
    )

    parser.add_argument(
        "--reference-season",
        type=int,
        default=DEFAULT_REFERENCE_SEASON,
    )

    return parser.parse_args()


# ============================================================
# PATHS
# ============================================================

def get_paths(
    season,
    reference_season,
):

    base_directory = Path(
        __file__
    ).parent

    model_directory = (
        base_directory
        / "models"
    )

    output_directory = (
        base_directory
        / "output"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    paths = {

        # ----------------------------------------------------
        # Current season dataset
        # ----------------------------------------------------

        "current_dataset":
            base_directory
            / "data"
            / f"top5_archetypes_{season}.csv",


        # ----------------------------------------------------
        # Frozen 2025 models
        # ----------------------------------------------------

        "defender_model":
            model_directory
            / (
                f"archetype_model_"
                f"{reference_season}_D.joblib"
            ),

        "midfield_orientation_model":
            model_directory
            / (
                f"midfield_orientation_"
                f"model_{reference_season}.joblib"
            ),

        "central_midfield_model":
            model_directory
            / (
                f"midfielder_archetype_"
                f"model_{reference_season}_central.joblib"
            ),

        "wide_midfield_model":
            model_directory
            / (
                f"midfielder_archetype_"
                f"model_{reference_season}_wide.joblib"
            ),

        "forward_orientation_model":
            model_directory
            / (
                f"archetype_model_"
                f"{reference_season}_F.joblib"
            ),

        "wide_forward_model":
            model_directory
            / (
                f"forward_archetype_"
                f"model_{reference_season}_wide.joblib"
            ),


        # ----------------------------------------------------
        # Frozen 2025 quality benchmarks
        # ----------------------------------------------------

        "reference_percentiles":
            output_directory
            / (
                f"quality_percentiles_"
                f"{reference_season}.csv"
            ),

        "reference_scores":
            output_directory
            / (
                f"quality_scores_"
                f"{reference_season}.csv"
            ),
    }

    return (
        paths,
        output_directory,
    )


# ============================================================
# FILE HELPERS
# ============================================================

def read_csv_required(
    path,
    description,
):

    if not path.exists():

        raise FileNotFoundError(
            f"{description} not found:\n"
            f"{path}"
        )

    return pd.read_csv(
        path
    )


def load_model_required(
    path,
    description,
):

    if not path.exists():

        raise FileNotFoundError(
            f"{description} not found:\n"
            f"{path}"
        )

    return joblib.load(
        path
    )


# ============================================================
# MODEL PREDICTION
# ============================================================

def predict_clusters(
    players,
    model_bundle,
):

    features = (
        model_bundle[
            "features"
        ]
    )

    missing_features = [
        feature
        for feature in features
        if feature not in players.columns
    ]

    if missing_features:

        raise ValueError(
            "Missing model features: "
            + ", ".join(
                missing_features
            )
        )


    X = (
        players[
            features
        ]
        .apply(
            pd.to_numeric,
            errors="coerce",
        )
    )


    imputer = (
        model_bundle[
            "imputer"
        ]
    )

    scaler = (
        model_bundle[
            "scaler"
        ]
    )

    model = (
        model_bundle[
            "model"
        ]
    )


    X_imputed = (
        imputer.transform(
            X
        )
    )


    X_scaled = (
        scaler.transform(
            X_imputed
        )
    )


    clusters = (
        model.predict(
            X_scaled
        )
    )


    return pd.Series(
        clusters,
        index=players.index,
        dtype="Int64",
    )


# ============================================================
# ASSIGN CURRENT PLAYER ROLES
# ============================================================

def assign_current_roles(
    players,
    models,
):

    players = players.copy()


    players[
        "orientation"
    ] = pd.NA

    players[
        "orientation_cluster"
    ] = pd.NA

    players[
        "archetype_cluster"
    ] = pd.NA

    players[
        "archetype_key"
    ] = pd.NA


    # ========================================================
    # DEFENDERS
    # ========================================================

    defender_mask = (
        players[
            "position"
        ]
        ==
        "D"
    )


    if defender_mask.any():

        defenders = (
            players.loc[
                defender_mask
            ]
        )

        defender_clusters = (
            predict_clusters(
                defenders,
                models[
                    "defender"
                ],
            )
        )

        players.loc[
            defender_mask,
            "archetype_cluster",
        ] = defender_clusters


        players.loc[
            defender_mask,
            "archetype_key",
        ] = defender_clusters.map(
            DEFENDER_CLUSTER_MAP
        )


    # ========================================================
    # MIDFIELDERS
    # ========================================================

    midfielder_mask = (
        players[
            "position"
        ]
        ==
        "M"
    )


    if midfielder_mask.any():

        midfielders = (
            players.loc[
                midfielder_mask
            ]
        )


        orientation_clusters = (
            predict_clusters(
                midfielders,
                models[
                    "midfield_orientation"
                ],
            )
        )


        players.loc[
            midfielder_mask,
            "orientation_cluster",
        ] = orientation_clusters


        players.loc[
            midfielder_mask,
            "orientation",
        ] = orientation_clusters.map(
            MIDFIELD_ORIENTATION_MAP
        )


        # ----------------------------------------------------
        # CENTRAL
        # ----------------------------------------------------

        central_mask = (
            midfielder_mask
            &
            (
                players[
                    "orientation"
                ]
                ==
                "central"
            )
        )


        if central_mask.any():

            central_players = (
                players.loc[
                    central_mask
                ]
            )


            central_clusters = (
                predict_clusters(
                    central_players,
                    models[
                        "central_midfield"
                    ],
                )
            )


            players.loc[
                central_mask,
                "archetype_cluster",
            ] = central_clusters


            players.loc[
                central_mask,
                "archetype_key",
            ] = central_clusters.map(
                CENTRAL_MIDFIELD_CLUSTER_MAP
            )


        # ----------------------------------------------------
        # WIDE
        # ----------------------------------------------------

        wide_mask = (
            midfielder_mask
            &
            (
                players[
                    "orientation"
                ]
                ==
                "wide"
            )
        )


        if wide_mask.any():

            wide_players = (
                players.loc[
                    wide_mask
                ]
            )


            wide_clusters = (
                predict_clusters(
                    wide_players,
                    models[
                        "wide_midfield"
                    ],
                )
            )


            players.loc[
                wide_mask,
                "archetype_cluster",
            ] = wide_clusters


            players.loc[
                wide_mask,
                "archetype_key",
            ] = wide_clusters.map(
                WIDE_MIDFIELD_CLUSTER_MAP
            )


    # ========================================================
    # FORWARDS
    # ========================================================

    forward_mask = (
        players[
            "position"
        ]
        ==
        "F"
    )


    if forward_mask.any():

        forwards = (
            players.loc[
                forward_mask
            ]
        )


        orientation_clusters = (
            predict_clusters(
                forwards,
                models[
                    "forward_orientation"
                ],
            )
        )


        players.loc[
            forward_mask,
            "orientation_cluster",
        ] = orientation_clusters


        players.loc[
            forward_mask,
            "orientation",
        ] = orientation_clusters.map(
            FORWARD_ORIENTATION_MAP
        )


        # ----------------------------------------------------
        # CENTRAL / TRADITIONAL 9
        # ----------------------------------------------------

        central_forward_mask = (
            forward_mask
            &
            (
                players[
                    "orientation"
                ]
                ==
                "central"
            )
        )


        players.loc[
            central_forward_mask,
            "archetype_key",
        ] = "traditional_9"


        # ----------------------------------------------------
        # WIDE FORWARDS
        # ----------------------------------------------------

        wide_forward_mask = (
            forward_mask
            &
            (
                players[
                    "orientation"
                ]
                ==
                "wide"
            )
        )


        if wide_forward_mask.any():

            wide_forwards = (
                players.loc[
                    wide_forward_mask
                ]
            )


            wide_forward_clusters = (
                predict_clusters(
                    wide_forwards,
                    models[
                        "wide_forward"
                    ],
                )
            )


            players.loc[
                wide_forward_mask,
                "archetype_cluster",
            ] = wide_forward_clusters


            players.loc[
                wide_forward_mask,
                "archetype_key",
            ] = wide_forward_clusters.map(
                WIDE_FORWARD_CLUSTER_MAP
            )


    # ========================================================
    # DISPLAY NAME
    # ========================================================

    players[
        "archetype_name"
    ] = (
        players[
            "archetype_key"
        ]
        .map(
            ARCHETYPE_DISPLAY_NAMES
        )
    )


    return players


# ============================================================
# VALIDATE ROLE ASSIGNMENTS
# ============================================================

def validate_roles(
    players,
):

    missing = (
        players[
            players[
                "archetype_key"
            ]
            .isna()
        ]
    )


    duplicate_count = (
        players[
            "player_id"
        ]
        .duplicated()
        .sum()
    )


    print()
    print(
        "========================================"
    )

    print(
        "CURRENT ROLE COUNTS"
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


    print()

    print(
        f"Duplicate player IDs: "
        f"{duplicate_count}"
    )


    if duplicate_count > 0:

        raise ValueError(
            "Duplicate current-season players found."
        )


    if not missing.empty:

        print()

        print(
            "Players missing a role:"
        )

        print(
            missing[
                [
                    "player_id",
                    "player_name",
                    "position",
                    "orientation",
                ]
            ]
            .head(30)
            .to_string(
                index=False
            )
        )

        raise ValueError(
            "Some players could not be assigned "
            "a current FutBud role."
        )


# ============================================================
# HISTORICAL PERCENTILE
#
# Current players are compared against the COMPLETED
# 2025/26 population for the SAME ROLE.
# ============================================================

def historical_percentile(
    value,
    reference_values,
):

    if pd.isna(value):
        return np.nan

    reference = (
        pd.to_numeric(
            reference_values,
            errors="coerce",
        )
        .dropna()
        .to_numpy(
            dtype=float,
            copy=True,
        )
    )

    if len(reference) == 0:
        return np.nan

    reference = np.sort(
        reference
    )

    value = float(
        value
    )

    left = np.searchsorted(
        reference,
        value,
        side="left",
    )

    right = np.searchsorted(
        reference,
        value,
        side="right",
    )

    equal_count = (
        right
        -
        left
    )

    percentile = (
        (
            left
            +
            (
                0.5
                *
                equal_count
            )
        )
        /
        len(reference)
        *
        100
    )

    return float(
        np.clip(
            percentile,
            0,
            100,
        )
    )


# ============================================================
# MINUTES RELIABILITY
#
# Same V1 logic as the frozen 2025 rating system.
# ============================================================

def calculate_minutes_reliability(
    minutes,
):

    if pd.isna(minutes):
        minutes = 0


    minutes = float(
        minutes
    )


    reliability = (
        0.80
        +
        (
            0.20
            *
            (
                min(
                    max(
                        minutes,
                        0,
                    ),
                    2700,
                )
                /
                2700
            )
        )
    )


    return reliability


# ============================================================
# SCORE CURRENT PLAYERS AGAINST 2025 BENCHMARKS
# ============================================================

def score_current_players(
    players,
    reference_percentiles,
    reference_scores,
):

    players = players.copy()


    players[
        "raw_quality_rating"
    ] = np.nan

    players[
        "minutes_reliability"
    ] = np.nan

    players[
        "futbud_rating"
    ] = np.nan

    players[
        "role_rating_percentile"
    ] = np.nan

    players[
        "quality_status"
    ] = pd.NA

    players[
        "quality_metric_count"
    ] = 0


    detailed_rows = []


    # ========================================================
    # SCORE EACH ROLE
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


        if not role_mask.any():
            continue


        role_players = (
            players.loc[
                role_mask
            ]
        )


        weights = (
            QUALITY_WEIGHTS[
                archetype_key
            ]
        )


        print()

        print(
            f"Scoring "
            f"{ARCHETYPE_DISPLAY_NAMES[archetype_key]}"
        )

        print(
            f"Current players: "
            f"{len(role_players)}"
        )


        percentile_columns = []


        # ====================================================
        # STAT-BY-STAT HISTORICAL PERCENTILES
        # ====================================================

        for feature in features:

            if feature not in players.columns:

                raise ValueError(
                    f"Current dataset is missing "
                    f"'{feature}'."
                )


            benchmark = (
                reference_percentiles[
                    (
                        reference_percentiles[
                            "archetype_key"
                        ]
                        ==
                        archetype_key
                    )
                    &
                    (
                        reference_percentiles[
                            "feature"
                        ]
                        ==
                        feature
                    )
                ][
                    "raw_value"
                ]
            )


            if benchmark.empty:

                raise ValueError(
                    f"No 2025 benchmark found for "
                    f"{archetype_key} / {feature}."
                )


            percentile_column = (
                f"{feature}_quality"
            )


            current_values = (
                pd.to_numeric(
                    players.loc[
                        role_mask,
                        feature,
                    ],
                    errors="coerce",
                )
            )


            percentiles = (
                current_values.apply(
                    lambda value:
                        historical_percentile(
                            value,
                            benchmark,
                        )
                )
            )


            if (
                feature
                in LOWER_IS_BETTER
            ):

                percentiles = (
                    100
                    -
                    percentiles
                )


            players.loc[
                role_mask,
                percentile_column,
            ] = percentiles


            percentile_columns.append(
                percentile_column
            )


            # ------------------------------------------------
            # Explanation output
            # ------------------------------------------------

            for index in role_players.index:

                detailed_rows.append(
                    {

                        "player_id":
                            players.at[
                                index,
                                "player_id",
                            ],

                        "player_name":
                            players.at[
                                index,
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
                                index,
                                feature,
                            ],

                        "historical_percentile":
                            players.at[
                                index,
                                percentile_column,
                            ],

                        "reference_players":
                            len(
                                pd.to_numeric(
                                    benchmark,
                                    errors="coerce",
                                )
                                .dropna()
                            ),
                    }
                )


        # ====================================================
        # WEIGHTED QUALITY SCORE
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


        raw_rating = (
            weighted_total
            /
            available_weight.replace(
                0,
                np.nan,
            )
        )


        # ====================================================
        # MINUTES RELIABILITY
        # ====================================================

        reliability = (
            pd.to_numeric(
                players.loc[
                    role_mask,
                    "minutes",
                ],
                errors="coerce",
            )
            .apply(
                calculate_minutes_reliability
            )
        )


        adjusted_rating = (
            50
            +
            (
                raw_rating
                -
                50
            )
            *
            reliability
        )


        players.loc[
            role_mask,
            "raw_quality_rating",
        ] = raw_rating


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
        ] = (
            role_percentiles
            .notna()
            .sum(
                axis=1
            )
        )


        # ====================================================
        # RATING PERCENTILE AGAINST 2025 ROLE RATINGS
        # ====================================================

        historical_role_ratings = (
            reference_scores[
                reference_scores[
                    "archetype_key"
                ]
                ==
                archetype_key
            ][
                "futbud_rating"
            ]
        )


        current_role_percentiles = (
            adjusted_rating.apply(
                lambda value:
                    historical_percentile(
                        value,
                        historical_role_ratings,
                    )
            )
        )


        players.loc[
            role_mask,
            "role_rating_percentile",
        ] = current_role_percentiles


    # ========================================================
    # FINAL FORMATTING
    # ========================================================

    for column in [
        "raw_quality_rating",
        "minutes_reliability",
        "futbud_rating",
        "role_rating_percentile",
    ]:

        players[
            column
        ] = (
            pd.to_numeric(
                players[
                    column
                ],
                errors="coerce",
            )
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


    detailed = pd.DataFrame(
        detailed_rows
    )


    if not detailed.empty:

        detailed[
            "raw_value"
        ] = pd.to_numeric(
            detailed[
                "raw_value"
            ],
            errors="coerce",
        ).round(3)


        detailed[
            "historical_percentile"
        ] = pd.to_numeric(
            detailed[
                "historical_percentile"
            ],
            errors="coerce",
        ).round(1)


    return (
        players,
        detailed,
    )


# ============================================================
# PRINT TOP PLAYERS
# ============================================================

def print_top_players(
    players,
):

    print()
    print(
        "========================================"
    )

    print(
        "TOP CURRENT PLAYERS BY ROLE"
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
            "-" * 90
        )

        print(
            archetype_name
        )

        print(
            "-" * 90
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
            "player_name",
            "latest_team_name",
            "minutes",
            "futbud_rating",
            "role_rating_percentile",
            "quality_status",
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

    ratings_path = (
        output_directory
        /
        f"current_quality_scores_{season}.csv"
    )


    percentiles_path = (
        output_directory
        /
        f"current_quality_percentiles_{season}.csv"
    )


    preferred_columns = [

        "player_id",
        "player_name",

        "position",

        "orientation",
        "orientation_cluster",

        "archetype_cluster",
        "archetype_key",
        "archetype_name",

        "minutes",
        "appearances",
        "starts",

        "latest_team_id",
        "latest_team_name",

        "primary_league_id",
        "primary_league_name",

        "provider_rating",

        "raw_quality_rating",
        "minutes_reliability",

        "futbud_rating",

        "role_rating_percentile",
        "quality_status",

        "quality_metric_count",
    ]


    columns = [
        column
        for column in preferred_columns
        if column in players.columns
    ]


    quality_columns = [
        column
        for column in players.columns
        if column.endswith(
            "_quality"
        )
    ]


    columns.extend(
        quality_columns
    )


    players[
        columns
    ].to_csv(
        ratings_path,
        index=False,
    )


    detailed.to_csv(
        percentiles_path,
        index=False,
    )


    return (
        ratings_path,
        percentiles_path,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    args = get_args()

    season = (
        args.season
    )

    reference_season = (
        args.reference_season
    )


    (
        paths,
        output_directory,
    ) = get_paths(
        season,
        reference_season,
    )


    print()
    print(
        "========================================"
    )

    print(
        "FutBud Current Season Inference"
    )

    print(
        "========================================"
    )

    print(
        f"Current season: "
        f"{season}"
    )

    print(
        f"Reference season: "
        f"{reference_season}"
    )


    # ========================================================
    # LOAD CURRENT DATA
    # ========================================================

    players = (
        read_csv_required(
            paths[
                "current_dataset"
            ],
            "Current player dataset",
        )
    )


    print()

    print(
        f"Current players loaded: "
        f"{len(players)}"
    )


    # ========================================================
    # LOAD FROZEN MODELS
    # ========================================================

    models = {

        "defender":
            load_model_required(
                paths[
                    "defender_model"
                ],
                "Defender model",
            ),

        "midfield_orientation":
            load_model_required(
                paths[
                    "midfield_orientation_model"
                ],
                "Midfield orientation model",
            ),

        "central_midfield":
            load_model_required(
                paths[
                    "central_midfield_model"
                ],
                "Central midfielder model",
            ),

        "wide_midfield":
            load_model_required(
                paths[
                    "wide_midfield_model"
                ],
                "Wide midfielder model",
            ),

        "forward_orientation":
            load_model_required(
                paths[
                    "forward_orientation_model"
                ],
                "Forward orientation model",
            ),

        "wide_forward":
            load_model_required(
                paths[
                    "wide_forward_model"
                ],
                "Wide forward model",
            ),
    }


    # ========================================================
    # ASSIGN CURRENT ROLES
    # ========================================================

    players = (
        assign_current_roles(
            players,
            models,
        )
    )


    validate_roles(
        players
    )


    # ========================================================
    # LOAD 2025 QUALITY BENCHMARKS
    # ========================================================

    reference_percentiles = (
        read_csv_required(
            paths[
                "reference_percentiles"
            ],
            "Historical quality percentiles",
        )
    )


    reference_scores = (
        read_csv_required(
            paths[
                "reference_scores"
            ],
            "Historical quality scores",
        )
    )


    # ========================================================
    # SCORE CURRENT PLAYERS
    # ========================================================

    (
        scored_players,
        detailed,
    ) = score_current_players(
        players,
        reference_percentiles,
        reference_scores,
    )


    # ========================================================
    # PRINT
    # ========================================================

    print_top_players(
        scored_players
    )


    # ========================================================
    # SAVE
    # ========================================================

    (
        ratings_path,
        percentiles_path,
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
        "CURRENT SEASON INFERENCE COMPLETE"
    )

    print(
        "========================================"
    )

    print(
        f"Current ratings: "
        f"{ratings_path}"
    )

    print(
        f"Current percentiles: "
        f"{percentiles_path}"
    )


if __name__ == "__main__":
    main()