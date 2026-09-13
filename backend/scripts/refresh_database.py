import subprocess
import sys
import time


IMPORTERS = [
    {
        "name": "Leagues",
        "module": "scripts.import_league",
    },
    {
        "name": "Teams",
        "module": "scripts.import_teams",
    },
    {
        "name": "Players",
        "module": "scripts.import_players",
    },
    {
        "name": "Squads",
        "module": "scripts.import_squads",
    },
    {
        "name": "Matches",
        "module": "scripts.import_matches",
    },
    {
        "name": "Matchday Squads",
        "module": "scripts.import_matchday_squads",
    },

    # NEW
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
]


def run_importer(name, module):
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
            f"Importer exited with code "
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
    print("FUTBUD FULL DATABASE REFRESH")
    print("=" * 60)

    print()
    print(
        f"{len(IMPORTERS)} import stages "
        f"will be processed."
    )

    total_start = time.time()

    completed = []

    for importer in IMPORTERS:

        success = run_importer(
            importer["name"],
            importer["module"],
        )

        if not success:
            print()
            print(
                "Database refresh stopped."
            )
            print(
                "Fix the failed importer "
                "and run this script again."
            )

            print()
            print(
                "Successfully completed:"
            )

            for name in completed:
                print(f"  ✓ {name}")

            sys.exit(1)

        completed.append(
            importer["name"]
        )

    total_elapsed = (
        time.time() - total_start
    )

    print()
    print("=" * 60)
    print(
        "FUTBUD DATABASE REFRESH COMPLETE"
    )
    print("=" * 60)

    for name in completed:
        print(f"✓ {name}")

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
        "FutBud database is up to date."
    )


if __name__ == "__main__":
    main()