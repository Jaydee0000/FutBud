import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


DEFAULT_SEASON = 2025
DEFAULT_REPRESENTATIVES = 15


# These are intentionally mostly VOLUME features.
# We want to learn HOW/WHERE a midfielder plays,
# not how efficient or good they are.
ORIENTATION_FEATURES = [
    "passes_total_per90",
    "tackles_per90",
    "interceptions_per90",
    "duels_total_per90",
    "dribbles_attempted_per90",
    "key_passes_per90",
    "shots_total_per90",
    "fouls_drawn_per90",
]


def get_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--season",
        type=int,
        default=DEFAULT_SEASON,
    )

    parser.add_argument(
        "--count",
        type=int,
        default=DEFAULT_REPRESENTATIVES,
        help="Representative players shown per group",
    )

    return parser.parse_args()


def get_paths(
    season,
):

    base_directory = Path(__file__).parent

    dataset_path = (
        base_directory
        / "data"
        / f"top5_archetypes_{season}.csv"
    )

    output_directory = (
        base_directory
        / "output"
    )

    model_directory = (
        base_directory
        / "models"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return (
        dataset_path,
        output_directory,
        model_directory,
    )


def load_midfielders(
    dataset_path,
):

    if not dataset_path.exists():

        raise FileNotFoundError(
            f"Dataset not found: "
            f"{dataset_path}"
        )

    df = pd.read_csv(
        dataset_path
    )

    midfielders = (
        df[
            df["position"] == "M"
        ]
        .copy()
        .reset_index(
            drop=True
        )
    )

    missing_features = [
        feature
        for feature in ORIENTATION_FEATURES
        if feature not in midfielders.columns
    ]

    if missing_features:

        raise ValueError(
            "Missing features: "
            + ", ".join(
                missing_features
            )
        )

    return midfielders


def preprocess(
    df,
):

    X = df[
        ORIENTATION_FEATURES
    ].copy()

    imputer = SimpleImputer(
        strategy="median"
    )

    X_imputed = (
        imputer.fit_transform(
            X
        )
    )

    scaler = StandardScaler()

    X_scaled = (
        scaler.fit_transform(
            X_imputed
        )
    )

    return (
        X_scaled,
        imputer,
        scaler,
    )


def train_orientation_model(
    X_scaled,
):

    model = KMeans(
        n_clusters=2,
        random_state=42,
        n_init=20,
    )

    clusters = (
        model.fit_predict(
            X_scaled
        )
    )

    return (
        model,
        clusters,
    )


def add_centroid_distances(
    df,
    X_scaled,
    model,
):

    df = df.copy()

    distances = []

    for index, row in enumerate(
        X_scaled
    ):

        cluster = int(
            df.iloc[index][
                "orientation_cluster"
            ]
        )

        centroid = (
            model.cluster_centers_[
                cluster
            ]
        )

        distance = np.linalg.norm(
            row - centroid
        )

        distances.append(
            distance
        )

    df[
        "orientation_distance"
    ] = distances

    return df


def create_cluster_summary(
    X_scaled,
    clusters,
):

    scaled_df = pd.DataFrame(
        X_scaled,
        columns=ORIENTATION_FEATURES,
    )

    scaled_df[
        "orientation_cluster"
    ] = clusters

    return (
        scaled_df
        .groupby(
            "orientation_cluster"
        )
        .mean()
        .round(3)
    )


def print_cluster_summary(
    summary,
):

    print()
    print(
        "========================================"
    )

    print(
        "ORIENTATION PROFILES"
    )

    print(
        "========================================"
    )

    for cluster, row in (
        summary.iterrows()
    ):

        print()
        print(
            f"GROUP {cluster}"
        )

        ordered = (
            row.sort_values(
                ascending=False
            )
        )

        print()
        print(
            "Most above average:"
        )

        for feature, value in (
            ordered.head(4).items()
        ):

            print(
                f"  {feature:<30} "
                f"{value:+.2f}"
            )

        print()
        print(
            "Most below average:"
        )

        for feature, value in (
            ordered.tail(4).items()
        ):

            print(
                f"  {feature:<30} "
                f"{value:+.2f}"
            )


def print_representative_players(
    df,
    count,
):

    for cluster in sorted(
        df[
            "orientation_cluster"
        ].unique()
    ):

        group = (
            df[
                df[
                    "orientation_cluster"
                ]
                ==
                cluster
            ]
            .sort_values(
                "orientation_distance"
            )
        )

        print()
        print()
        print(
            "========================================"
        )

        print(
            f"GROUP {cluster}"
        )

        print(
            f"Players: {len(group)}"
        )

        print(
            "========================================"
        )

        print()
        print(
            "Most representative players:"
        )

        for rank, (_, player) in enumerate(
            group.head(
                count
            ).iterrows(),
            start=1,
        ):

            print(
                f"{rank:>2}. "
                f"{player['player_name']:<25} "
                f"{player['latest_team_name']:<25} "
                f"distance="
                f"{player['orientation_distance']:.3f}"
            )


def save_outputs(
    df,
    summary,
    model,
    imputer,
    scaler,
    season,
    output_directory,
    model_directory,
):

    assignments_path = (
        output_directory
        /
        (
            f"midfield_orientation_"
            f"assignments_{season}.csv"
        )
    )

    summary_path = (
        output_directory
        /
        (
            f"midfield_orientation_"
            f"summary_{season}.csv"
        )
    )

    model_path = (
        model_directory
        /
        (
            f"midfield_orientation_"
            f"model_{season}.joblib"
        )
    )

    df.to_csv(
        assignments_path,
        index=False,
    )

    summary.to_csv(
        summary_path
    )

    model_bundle = {
        "season":
            season,

        "features":
            ORIENTATION_FEATURES,

        "imputer":
            imputer,

        "scaler":
            scaler,

        "model":
            model,
    }

    joblib.dump(
        model_bundle,
        model_path,
    )

    return (
        assignments_path,
        summary_path,
        model_path,
    )


def main():

    args = get_args()

    season = args.season
    count = args.count

    (
        dataset_path,
        output_directory,
        model_directory,
    ) = get_paths(
        season
    )

    print()
    print(
        "========================================"
    )

    print(
        "FutBud Midfielder Orientation Model"
    )

    print(
        "========================================"
    )

    print(
        f"Season: {season}"
    )

    print()

    midfielders = (
        load_midfielders(
            dataset_path
        )
    )

    print(
        f"Midfielders loaded: "
        f"{len(midfielders)}"
    )

    (
        X_scaled,
        imputer,
        scaler,
    ) = preprocess(
        midfielders
    )

    (
        model,
        clusters,
    ) = train_orientation_model(
        X_scaled
    )

    midfielders[
        "orientation_cluster"
    ] = clusters

    midfielders = (
        add_centroid_distances(
            midfielders,
            X_scaled,
            model,
        )
    )

    silhouette = (
        silhouette_score(
            X_scaled,
            clusters,
        )
    )

    print()
    print(
        "Players per orientation group:"
    )

    print(
        midfielders[
            "orientation_cluster"
        ]
        .value_counts()
        .sort_index()
    )

    print()

    print(
        f"Silhouette score: "
        f"{silhouette:.3f}"
    )

    summary = (
        create_cluster_summary(
            X_scaled,
            clusters,
        )
    )

    print_cluster_summary(
        summary
    )

    print_representative_players(
        midfielders,
        count,
    )

    (
        assignments_path,
        summary_path,
        model_path,
    ) = save_outputs(
        midfielders,
        summary,
        model,
        imputer,
        scaler,
        season,
        output_directory,
        model_directory,
    )

    print()
    print()
    print(
        "========================================"
    )

    print(
        "Orientation model complete."
    )

    print(
        "========================================"
    )

    print(
        f"Assignments: "
        f"{assignments_path}"
    )

    print(
        f"Summary: "
        f"{summary_path}"
    )

    print(
        f"Model: "
        f"{model_path}"
    )


if __name__ == "__main__":
    main()