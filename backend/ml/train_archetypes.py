import argparse
from pathlib import Path

import joblib
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from ml.archetype_features import (
    ARCHETYPE_FEATURES,
    POSITION_NAMES,
)


DEFAULT_SEASON = 2025
DEFAULT_CLUSTERS = 4


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
        "--clusters",
        type=int,
        default=DEFAULT_CLUSTERS,
    )

    return parser.parse_args()


def get_dataset_path(
    season,
):

    return (
        Path(__file__).parent
        /
        "data"
        /
        f"top5_archetypes_{season}.csv"
    )


def load_dataset(
    season,
):

    dataset_path = (
        get_dataset_path(
            season
        )
    )

    if not dataset_path.exists():

        raise FileNotFoundError(
            f"Dataset not found: "
            f"{dataset_path}"
        )

    return pd.read_csv(
        dataset_path
    )


def prepare_position_data(
    df,
    position,
):

    position_df = (
        df[
            df["position"]
            ==
            position
        ]
        .copy()
        .reset_index(
            drop=True
        )
    )

    features = (
        ARCHETYPE_FEATURES[
            position
        ]
    )

    missing_features = [
        feature
        for feature in features
        if feature not in position_df.columns
    ]

    if missing_features:

        raise ValueError(
            "Dataset is missing features: "
            +
            ", ".join(
                missing_features
            )
        )

    return (
        position_df,
        features,
    )


def preprocess_features(
    position_df,
    features,
):

    X = position_df[
        features
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


def train_model(
    X_scaled,
    cluster_count,
):

    model = KMeans(
        n_clusters=cluster_count,
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


def calculate_silhouette(
    X_scaled,
    clusters,
):

    unique_clusters = (
        len(
            set(clusters)
        )
    )

    if unique_clusters <= 1:
        return None

    if len(X_scaled) <= unique_clusters:
        return None

    return silhouette_score(
        X_scaled,
        clusters,
    )


def create_raw_summary(
    position_df,
    features,
):

    summary = (
        position_df
        .groupby("cluster")[
            features
        ]
        .mean()
        .round(3)
    )

    counts = (
        position_df
        .groupby("cluster")
        .size()
        .rename("player_count")
    )

    summary.insert(
        0,
        "player_count",
        counts,
    )

    return summary


def create_standardized_summary(
    X_scaled,
    clusters,
    features,
):

    scaled_df = pd.DataFrame(
        X_scaled,
        columns=features,
    )

    scaled_df[
        "cluster"
    ] = clusters

    return (
        scaled_df
        .groupby("cluster")
        .mean()
        .round(3)
    )


def print_cluster_profiles(
    standardized_summary,
):

    print()
    print(
        "================================"
    )

    print(
        "CLUSTER PROFILES"
    )

    print(
        "================================"
    )

    for cluster_id, row in (
        standardized_summary.iterrows()
    ):

        sorted_features = (
            row.sort_values(
                ascending=False
            )
        )

        strongest = (
            sorted_features.head(4)
        )

        weakest = (
            sorted_features.tail(4)
        )

        print()
        print(
            f"Cluster {cluster_id}"
        )

        print(
            "Strongest characteristics:"
        )

        for feature, value in (
            strongest.items()
        ):

            print(
                f"  {feature}: "
                f"{value:+.2f}"
            )

        print(
            "Weakest characteristics:"
        )

        for feature, value in (
            weakest.items()
        ):

            print(
                f"  {feature}: "
                f"{value:+.2f}"
            )


def save_outputs(
    position_df,
    raw_summary,
    standardized_summary,
    model,
    imputer,
    scaler,
    features,
    season,
    position,
):

    base_directory = (
        Path(__file__).parent
    )

    output_directory = (
        base_directory
        /
        "output"
    )

    model_directory = (
        base_directory
        /
        "models"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    assignments_path = (
        output_directory
        /
        (
            f"archetype_assignments_"
            f"{season}_{position}.csv"
        )
    )

    summary_path = (
        output_directory
        /
        (
            f"archetype_summary_"
            f"{season}_{position}.csv"
        )
    )

    standardized_path = (
        output_directory
        /
        (
            f"archetype_zprofiles_"
            f"{season}_{position}.csv"
        )
    )

    model_path = (
        model_directory
        /
        (
            f"archetype_model_"
            f"{season}_{position}.joblib"
        )
    )

    position_df.to_csv(
        assignments_path,
        index=False,
    )

    raw_summary.to_csv(
        summary_path
    )

    standardized_summary.to_csv(
        standardized_path
    )

    model_bundle = {
        "season":
            season,

        "position":
            position,

        "features":
            features,

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

    return {
        "assignments":
            assignments_path,

        "summary":
            summary_path,

        "standardized":
            standardized_path,

        "model":
            model_path,
    }


def main():

    args = get_args()

    season = args.season
    position = args.position
    cluster_count = args.clusters

    position_name = (
        POSITION_NAMES[
            position
        ]
    )

    print()
    print(
        "================================"
    )

    print(
        "FutBud Archetype Training"
    )

    print(
        "================================"
    )

    print(
        f"Season: {season}"
    )

    print(
        f"Position: "
        f"{position_name}"
    )

    print(
        f"Requested clusters: "
        f"{cluster_count}"
    )

    df = load_dataset(
        season
    )

    (
        position_df,
        features,
    ) = prepare_position_data(
        df,
        position,
    )

    print(
        f"Players available: "
        f"{len(position_df)}"
    )

    if len(position_df) < cluster_count:

        raise ValueError(
            "Not enough players to "
            "create the requested "
            "number of clusters."
        )

    (
        X_scaled,
        imputer,
        scaler,
    ) = preprocess_features(
        position_df,
        features,
    )

    (
        model,
        clusters,
    ) = train_model(
        X_scaled,
        cluster_count,
    )

    position_df[
        "cluster"
    ] = clusters

    silhouette = (
        calculate_silhouette(
            X_scaled,
            clusters,
        )
    )

    raw_summary = (
        create_raw_summary(
            position_df,
            features,
        )
    )

    standardized_summary = (
        create_standardized_summary(
            X_scaled,
            clusters,
            features,
        )
    )

    print()

    print(
        "Players per cluster:"
    )

    print(
        position_df[
            "cluster"
        ]
        .value_counts()
        .sort_index()
    )

    if silhouette is not None:

        print()

        print(
            f"Silhouette score: "
            f"{silhouette:.3f}"
        )

    print_cluster_profiles(
        standardized_summary
    )

    paths = save_outputs(
        position_df,
        raw_summary,
        standardized_summary,
        model,
        imputer,
        scaler,
        features,
        season,
        position,
    )

    print()
    print(
        "================================"
    )

    print(
        "Training complete."
    )

    print(
        "================================"
    )

    print()

    for name, path in paths.items():

        print(
            f"{name}: "
            f"{path}"
        )


if __name__ == "__main__":
    main()