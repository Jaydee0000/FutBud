import argparse
from pathlib import Path

import joblib
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


DEFAULT_SEASON = 2025


FORWARD_ORIENTATION_CLUSTERS = {
    "wide": 0,
    "central": 1,
}


ARCHETYPE_FEATURES = {
    # Central / No. 9 forwards
    "central": [
        "shots_total_per90",
        "offsides_per90",
        "duels_total_per90",
        "fouls_drawn_per90",
        "passes_total_per90",
        "key_passes_per90",
        "dribbles_attempted_per90",
    ],

    # Wide / linking forwards
    "wide": [
        "dribbles_attempted_per90",
        "key_passes_per90",
        "passes_total_per90",
        "shots_total_per90",
        "fouls_drawn_per90",
        "offsides_per90",
        "duels_total_per90",
        ""
    ],
}


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--season",
        type=int,
        default=DEFAULT_SEASON,
    )

    parser.add_argument(
        "--orientation",
        required=True,
        choices=[
            "central",
            "wide",
        ],
    )

    parser.add_argument(
        "--clusters",
        type=int,
        required=True,
    )

    return parser.parse_args()


def get_paths(season):
    base_directory = Path(__file__).parent

    orientation_path = (
        base_directory
        / "output"
        / f"archetype_assignments_{season}_F.csv"
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
        orientation_path,
        output_directory,
        model_directory,
    )


def load_players(
    orientation_path,
    orientation,
):

    if not orientation_path.exists():
        raise FileNotFoundError(
            f"Forward orientation assignments not found: "
            f"{orientation_path}"
        )

    df = pd.read_csv(
        orientation_path
    )

    orientation_cluster = (
        FORWARD_ORIENTATION_CLUSTERS[
            orientation
        ]
    )

    players = (
        df[
            df["cluster"]
            ==
            orientation_cluster
        ]
        .copy()
        .reset_index(
            drop=True
        )
    )

    features = (
        ARCHETYPE_FEATURES[
            orientation
        ]
    )

    missing_features = [
        feature
        for feature in features
        if feature not in players.columns
    ]

    if missing_features:
        raise ValueError(
            "Missing features: "
            + ", ".join(
                missing_features
            )
        )

    return (
        players,
        features,
    )


def preprocess(
    players,
    features,
):

    X = players[
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
    number_of_clusters,
):

    model = KMeans(
        n_clusters=number_of_clusters,
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


def create_z_profiles(
    X_scaled,
    clusters,
    features,
):

    profile_df = pd.DataFrame(
        X_scaled,
        columns=features,
    )

    profile_df[
        "archetype_cluster"
    ] = clusters

    return (
        profile_df
        .groupby(
            "archetype_cluster"
        )
        .mean()
        .round(3)
    )


def create_raw_summary(
    players,
    features,
):

    return (
        players
        .groupby(
            "archetype_cluster"
        )[features]
        .mean()
        .round(3)
    )


def print_profiles(
    players,
    z_profiles,
):

    print()
    print(
        "========================================"
    )

    print(
        "FORWARD ARCHETYPE PROFILES"
    )

    print(
        "========================================"
    )

    for cluster, row in (
        z_profiles.iterrows()
    ):

        player_count = len(
            players[
                players[
                    "archetype_cluster"
                ]
                ==
                cluster
            ]
        )

        print()
        print(
            f"CLUSTER {cluster}"
        )

        print(
            f"Players: {player_count}"
        )

        ordered = (
            row.sort_values(
                ascending=False
            )
        )

        print()
        print(
            "Highest relative features:"
        )

        for feature, value in (
            ordered.head(5).items()
        ):

            print(
                f"  {feature:<30} "
                f"{value:+.2f}"
            )

        print()
        print(
            "Lowest relative features:"
        )

        for feature, value in (
            ordered.tail(5).items()
        ):

            print(
                f"  {feature:<30} "
                f"{value:+.2f}"
            )


def save_outputs(
    players,
    raw_summary,
    z_profiles,
    model,
    imputer,
    scaler,
    features,
    season,
    orientation,
    output_directory,
    model_directory,
):

    assignments_path = (
        output_directory
        /
        (
            f"forward_archetype_"
            f"assignments_{season}_{orientation}.csv"
        )
    )

    raw_summary_path = (
        output_directory
        /
        (
            f"forward_archetype_"
            f"summary_{season}_{orientation}.csv"
        )
    )

    z_profile_path = (
        output_directory
        /
        (
            f"forward_archetype_"
            f"zprofiles_{season}_{orientation}.csv"
        )
    )

    model_path = (
        model_directory
        /
        (
            f"forward_archetype_"
            f"model_{season}_{orientation}.joblib"
        )
    )

    players.to_csv(
        assignments_path,
        index=False,
    )

    raw_summary.to_csv(
        raw_summary_path
    )

    z_profiles.to_csv(
        z_profile_path
    )

    model_bundle = {
        "season":
            season,

        "orientation":
            orientation,

        "orientation_cluster":
            FORWARD_ORIENTATION_CLUSTERS[
                orientation
            ],

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

    return (
        assignments_path,
        raw_summary_path,
        z_profile_path,
        model_path,
    )


def main():

    args = get_args()

    season = args.season
    orientation = args.orientation
    number_of_clusters = args.clusters

    if number_of_clusters < 2:
        raise ValueError(
            "Number of clusters must be at least 2."
        )

    (
        orientation_path,
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
        "FutBud Forward Archetype Training"
    )

    print(
        "========================================"
    )

    print(
        f"Season: {season}"
    )

    print(
        f"Orientation: "
        f"{orientation.upper()}"
    )

    print(
        f"Clusters: "
        f"{number_of_clusters}"
    )

    (
        players,
        features,
    ) = load_players(
        orientation_path,
        orientation,
    )

    print()

    print(
        f"Players loaded: "
        f"{len(players)}"
    )

    (
        X_scaled,
        imputer,
        scaler,
    ) = preprocess(
        players,
        features,
    )

    (
        model,
        clusters,
    ) = train_model(
        X_scaled,
        number_of_clusters,
    )

    players[
        "archetype_cluster"
    ] = clusters

    silhouette = (
        silhouette_score(
            X_scaled,
            clusters,
        )
    )

    print()
    print(
        "Players per cluster:"
    )

    print(
        players[
            "archetype_cluster"
        ]
        .value_counts()
        .sort_index()
    )

    print()

    print(
        f"Silhouette score: "
        f"{silhouette:.3f}"
    )

    raw_summary = (
        create_raw_summary(
            players,
            features,
        )
    )

    z_profiles = (
        create_z_profiles(
            X_scaled,
            clusters,
            features,
        )
    )

    print_profiles(
        players,
        z_profiles,
    )

    (
        assignments_path,
        raw_summary_path,
        z_profile_path,
        model_path,
    ) = save_outputs(
        players,
        raw_summary,
        z_profiles,
        model,
        imputer,
        scaler,
        features,
        season,
        orientation,
        output_directory,
        model_directory,
    )

    print()
    print(
        "========================================"
    )

    print(
        "Training complete."
    )

    print(
        "========================================"
    )

    print(
        f"Assignments: "
        f"{assignments_path}"
    )

    print(
        f"Raw summary: "
        f"{raw_summary_path}"
    )

    print(
        f"Z profiles: "
        f"{z_profile_path}"
    )

    print(
        f"Model: "
        f"{model_path}"
    )


if __name__ == "__main__":
    main()