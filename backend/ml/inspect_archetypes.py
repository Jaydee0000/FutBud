import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from ml.archetype_features import POSITION_NAMES


DEFAULT_SEASON = 2025
DEFAULT_COUNT = 10


def get_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--season",
        type=int,
        default=DEFAULT_SEASON,
    )

    parser.add_argument(
        "--position",
        choices=[
            "D",
            "M",
            "F",
        ],
        required=True,
    )

    parser.add_argument(
        "--count",
        type=int,
        default=DEFAULT_COUNT,
        help="Representative players per cluster",
    )

    return parser.parse_args()


def get_paths(
    season,
    position,
):

    base_directory = Path(__file__).parent

    assignments_path = (
        base_directory
        / "output"
        / (
            f"archetype_assignments_"
            f"{season}_{position}.csv"
        )
    )

    model_path = (
        base_directory
        / "models"
        / (
            f"archetype_model_"
            f"{season}_{position}.joblib"
        )
    )

    output_directory = (
        base_directory
        / "output"
    )

    return (
        assignments_path,
        model_path,
        output_directory,
    )


def load_data(
    assignments_path,
    model_path,
):

    df = pd.read_csv(
        assignments_path
    )

    model_bundle = joblib.load(
        model_path
    )

    return (
        df,
        model_bundle,
    )


def prepare_features(
    df,
    model_bundle,
):

    features = (
        model_bundle[
            "features"
        ]
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

    X = df[
        features
    ]

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

    return (
        X_scaled,
        features,
    )


def calculate_centroid_distances(
    df,
    X_scaled,
    model_bundle,
):

    model = (
        model_bundle[
            "model"
        ]
    )

    df = df.copy()

    distances = []

    for index, row in enumerate(
        X_scaled
    ):

        cluster = int(
            df.iloc[index][
                "cluster"
            ]
        )

        centroid = (
            model.cluster_centers_[
                cluster
            ]
        )

        distance = (
            np.linalg.norm(
                row - centroid
            )
        )

        distances.append(
            distance
        )

    df[
        "centroid_distance"
    ] = distances

    return df


def print_cluster_profile(
    cluster,
    df,
    X_scaled,
    features,
):

    indexes = (
        df.index[
            df["cluster"]
            ==
            cluster
        ]
        .tolist()
    )

    cluster_matrix = (
        X_scaled[
            indexes
        ]
    )

    averages = (
        cluster_matrix.mean(
            axis=0
        )
    )

    profile = (
        pd.Series(
            averages,
            index=features,
        )
        .sort_values(
            ascending=False
        )
    )

    print()

    print(
        "Style characteristics:"
    )

    print(
        "  Above average:"
    )

    for feature, value in (
        profile.head(5).items()
    ):

        print(
            f"    {feature:<30} "
            f"{value:+.2f}"
        )

    print(
        "  Below average:"
    )

    for feature, value in (
        profile.tail(5).items()
    ):

        print(
            f"    {feature:<30} "
            f"{value:+.2f}"
        )


def print_representative_players(
    cluster_df,
    count,
):

    representatives = (
        cluster_df
        .sort_values(
            "centroid_distance"
        )
        .head(
            count
        )
    )

    print()

    print(
        "Most representative players:"
    )

    for rank, (_, player) in enumerate(
        representatives.iterrows(),
        start=1,
    ):

        print(
            f"  {rank:>2}. "
            f"{player['player_name']:<25} "
            f"{player['latest_team_name']:<25} "
            f"distance="
            f"{player['centroid_distance']:.3f}"
        )

    return representatives


def print_extreme_players(
    cluster_df,
):

    extreme = (
        cluster_df
        .sort_values(
            "centroid_distance",
            ascending=False,
        )
        .head(5)
    )

    print()

    print(
        "Least typical / edge players:"
    )

    for _, player in (
        extreme.iterrows()
    ):

        print(
            f"  "
            f"{player['player_name']:<25} "
            f"{player['latest_team_name']:<25} "
            f"distance="
            f"{player['centroid_distance']:.3f}"
        )


def main():

    args = get_args()

    season = args.season
    position = args.position
    count = args.count

    (
        assignments_path,
        model_path,
        output_directory,
    ) = get_paths(
        season,
        position,
    )

    (
        df,
        model_bundle,
    ) = load_data(
        assignments_path,
        model_path,
    )

    (
        X_scaled,
        features,
    ) = prepare_features(
        df,
        model_bundle,
    )

    df = (
        calculate_centroid_distances(
            df,
            X_scaled,
            model_bundle,
        )
    )

    position_name = (
        POSITION_NAMES[
            position
        ]
    )

    print()
    print(
        "========================================"
    )

    print(
        f"FutBud {position_name} "
        f"Archetype Inspection"
    )

    print(
        "========================================"
    )

    representative_rows = []

    for cluster in sorted(
        df["cluster"].unique()
    ):

        cluster_df = (
            df[
                df["cluster"]
                ==
                cluster
            ]
        )

        print()
        print()
        print(
            "========================================"
        )

        print(
            f"CLUSTER {cluster}"
        )

        print(
            f"Players: "
            f"{len(cluster_df)}"
        )

        print(
            "========================================"
        )

        print_cluster_profile(
            cluster,
            df,
            X_scaled,
            features,
        )

        representatives = (
            print_representative_players(
                cluster_df,
                count,
            )
        )

        representatives = (
            representatives.copy()
        )

        representatives[
            "representative_rank"
        ] = range(
            1,
            len(
                representatives
            ) + 1
        )

        representative_rows.append(
            representatives
        )

        print_extreme_players(
            cluster_df
        )

    result = pd.concat(
        representative_rows,
        ignore_index=True,
    )

    output_path = (
        output_directory
        /
        (
            f"representative_players_"
            f"{season}_{position}.csv"
        )
    )

    result.to_csv(
        output_path,
        index=False,
    )

    print()
    print()
    print(
        "========================================"
    )

    print(
        "Inspection complete."
    )

    print(
        f"Saved to: "
        f"{output_path}"
    )

    print(
        "========================================"
    )


if __name__ == "__main__":
    main()