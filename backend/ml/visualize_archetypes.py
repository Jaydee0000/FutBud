import argparse
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn.decomposition import PCA

from ml.archetype_features import POSITION_NAMES


DEFAULT_SEASON = 2025


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

    return parser.parse_args()


def get_paths(
    season,
    position,
):

    base_directory = (
        Path(__file__).parent
    )

    assignments_path = (
        base_directory
        /
        "output"
        /
        (
            f"archetype_assignments_"
            f"{season}_{position}.csv"
        )
    )

    model_path = (
        base_directory
        /
        "models"
        /
        (
            f"archetype_model_"
            f"{season}_{position}.joblib"
        )
    )

    output_directory = (
        base_directory
        /
        "visualizations"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
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

    if not assignments_path.exists():

        raise FileNotFoundError(
            f"Assignments not found: "
            f"{assignments_path}"
        )

    if not model_path.exists():

        raise FileNotFoundError(
            f"Model not found: "
            f"{model_path}"
        )

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
        model_bundle["features"]
    )

    imputer = (
        model_bundle["imputer"]
    )

    scaler = (
        model_bundle["scaler"]
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


def create_pca_plot(
    df,
    X_scaled,
    season,
    position,
    output_directory,
):

    pca = PCA(
        n_components=2
    )

    coordinates = (
        pca.fit_transform(
            X_scaled
        )
    )

    plot_df = df.copy()

    plot_df["pc1"] = (
        coordinates[:, 0]
    )

    plot_df["pc2"] = (
        coordinates[:, 1]
    )

    plt.figure(
        figsize=(12, 8)
    )

    clusters = sorted(
        plot_df[
            "cluster"
        ].unique()
    )

    for cluster in clusters:

        cluster_players = (
            plot_df[
                plot_df["cluster"]
                ==
                cluster
            ]
        )

        plt.scatter(
            cluster_players["pc1"],
            cluster_players["pc2"],
            label=(
                f"Cluster {cluster} "
                f"({len(cluster_players)})"
            ),
            alpha=0.65,
            s=45,
        )

    # Label cluster centers
    for cluster in clusters:

        cluster_players = (
            plot_df[
                plot_df["cluster"]
                ==
                cluster
            ]
        )

        center_x = (
            cluster_players[
                "pc1"
            ].mean()
        )

        center_y = (
            cluster_players[
                "pc2"
            ].mean()
        )

        plt.text(
            center_x,
            center_y,
            f"Cluster {cluster}",
            fontsize=12,
            fontweight="bold",
            ha="center",
            va="center",
        )

    position_name = (
        POSITION_NAMES[
            position
        ]
    )

    explained = (
        pca.explained_variance_ratio_
        *
        100
    )

    plt.title(
        (
            f"FutBud {position_name} "
            f"Archetypes — {season}/{str(season + 1)[-2:]}"
        )
    )

    plt.xlabel(
        (
            "PCA Dimension 1 "
            f"({explained[0]:.1f}% variance)"
        )
    )

    plt.ylabel(
        (
            "PCA Dimension 2 "
            f"({explained[1]:.1f}% variance)"
        )
    )

    plt.legend()

    plt.grid(
        alpha=0.2
    )

    plt.tight_layout()

    output_path = (
        output_directory
        /
        (
            f"pca_clusters_"
            f"{season}_{position}.png"
        )
    )

    plt.savefig(
        output_path,
        dpi=200,
        bbox_inches="tight",
    )

    plt.show()

    return (
        output_path,
        plot_df
    )


def create_cluster_heatmap(
    df,
    X_scaled,
    features,
    season,
    position,
    output_directory,
):

    scaled_df = pd.DataFrame(
        X_scaled,
        columns=features,
    )

    scaled_df["cluster"] = (
        df["cluster"].values
    )

    cluster_profiles = (
        scaled_df
        .groupby("cluster")
        .mean()
    )

    data = (
        cluster_profiles
        .to_numpy()
    )

    figure_height = max(
        7,
        len(features) * 0.45,
    )

    fig, ax = plt.subplots(
        figsize=(
            10,
            figure_height,
        )
    )

    image = ax.imshow(
        data.T,
        aspect="auto",
    )

    ax.set_xticks(
        np.arange(
            len(
                cluster_profiles.index
            )
        )
    )

    ax.set_xticklabels(
        [
            f"Cluster {cluster}"
            for cluster
            in cluster_profiles.index
        ]
    )

    ax.set_yticks(
        np.arange(
            len(features)
        )
    )

    ax.set_yticklabels(
        features
    )

    for row_index in range(
        len(features)
    ):

        for column_index in range(
            len(
                cluster_profiles.index
            )
        ):

            value = (
                data[
                    column_index,
                    row_index
                ]
            )

            ax.text(
                column_index,
                row_index,
                f"{value:+.2f}",
                ha="center",
                va="center",
                fontsize=8,
            )

    position_name = (
        POSITION_NAMES[
            position
        ]
    )

    ax.set_title(
        (
            f"{position_name} "
            "Cluster Profiles"
        )
    )

    colorbar = (
        fig.colorbar(
            image,
            ax=ax,
        )
    )

    colorbar.set_label(
        "Standard deviations from position average"
    )

    plt.tight_layout()

    output_path = (
        output_directory
        /
        (
            f"cluster_heatmap_"
            f"{season}_{position}.png"
        )
    )

    plt.savefig(
        output_path,
        dpi=200,
        bbox_inches="tight",
    )

    plt.show()

    return output_path


def print_cluster_players(
    df,
):

    print()

    print(
        "================================"
    )

    print(
        "PLAYERS BY CLUSTER"
    )

    print(
        "================================"
    )

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

        print(
            f"Cluster {cluster}"
        )

        print(
            f"Players: "
            f"{len(cluster_df)}"
        )

        examples = (
            cluster_df
            .sort_values(
                "minutes",
                ascending=False,
            )
            .head(15)
        )

        for _, player in (
            examples.iterrows()
        ):

            print(
                f"  "
                f"{player['player_name']} "
                f"— "
                f"{player['latest_team_name']}"
            )


def main():

    args = get_args()

    season = args.season
    position = args.position

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

    (
        pca_path,
        plot_df,
    ) = create_pca_plot(
        df,
        X_scaled,
        season,
        position,
        output_directory,
    )

    heatmap_path = (
        create_cluster_heatmap(
            df,
            X_scaled,
            features,
            season,
            position,
            output_directory,
        )
    )

    print_cluster_players(
        plot_df
    )

    print()

    print(
        "Visualizations saved:"
    )

    print(
        pca_path
    )

    print(
        heatmap_path
    )


if __name__ == "__main__":
    main()