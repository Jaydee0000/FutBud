import subprocess
import sys
import time


# ============================================================
# FUTBUD QUICK REFRESH
#
# This script updates only frequently-changing data.
#
# It intentionally DOES NOT refresh:
#   - leagues
#   - teams
#   - full player list
#   - full club squads
#
# Those should only be refreshed occasionally.
# ============================================================


UPDATE_STAGES = [
    {
        "name": "Matches",
        "module": "scripts.import_matches",
    },

    {
        "name": "Matchday Squads",
        "module": "scripts.import_matchday_squads",
    },

    {
        "name": "Match Details",
        "module": "scripts.import_match_details",
    },

    {
        "name": "Standings",
        "module": "scripts.import_standings",
    },

    {
        "name": "Player Match Stats",
        "module": "scripts.import_player_match_stats",
    },

    {
        "name": "Team Match Stats",
        "module": "scripts.import_team_match_stats",
    },

    # Recalculate 2026/27 FutBud ratings
    # using the frozen 2025/26 models.
    {
        "name": "Calculate FutBud Ratings",
        "module": "ml.predict_current_season",
    },

    # Push the newly calculated ratings
    # into PostgreSQL.
    {
        "name": "Import FutBud Ratings",
        "module": "ml.import_current_ratings",
    },
]


def run_stage(name, module):
    print()
    print("=" * 60)
    print(f"STARTING: {name}")
    print("=" * 60)

    start_time = time.time()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            module,
        ]
    )

    elapsed = time.time() - start_time

    if result.returncode != 0:
        print()
        print("=" * 60)
        print(f"FAILED: {name}")
        print(
            f"Process exited with code "
            f"{result.returncode}"
        )
        print("=" * 60)

        return False

    print()
    print(
        f"FINISHED: {name} "
        f"({elapsed:.1f}s)"
    )

    return True


def main():
    print()
    print("=" * 60)
    print("FUTBUD QUICK REFRESH")
    print("=" * 60)

    print()
    print(
        f"{len(UPDATE_STAGES)} update stages "
        f"will be processed."
    )

    print()
    print(
        "Static league/team/player data "
        "will NOT be refreshed."
    )

    total_start = time.time()

    completed = []

    for stage in UPDATE_STAGES:

        success = run_stage(
            stage["name"],
            stage["module"],
        )

        if not success:

            print()
            print(
                "Quick refresh stopped."
            )

            print(
                "Fix the failed stage "
                "and run the script again."
            )

            print()
            print(
                "Successfully completed:"
            )

            for name in completed:
                print(
                    f"  ✓ {name}"
                )

            sys.exit(1)

        completed.append(
            stage["name"]
        )

    total_elapsed = (
        time.time()
        - total_start
    )

    print()
    print("=" * 60)
    print(
        "FUTBUD QUICK REFRESH COMPLETE"
    )
    print("=" * 60)

    print()

    for name in completed:
        print(
            f"✓ {name}"
        )

    print()

    print(
        f"Total stages: "
        f"{len(completed)}"
    )

    print(
        f"Total runtime: "
        f"{total_elapsed:.1f} seconds"
    )

    print()
    print(
        "Matches, statistics, standings, "
        "and FutBud ratings are up to date."
    )


if __name__ == "__main__":
    main()