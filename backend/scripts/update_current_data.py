"""Selective current-data refresh for FutBud.

Run from ``backend/`` with::

    python -m scripts.update_current_data [START_DATE] [END_DATE]

With no dates, the updater checks yesterday/today plus stale or incomplete
current-season fixtures. One date means that date through today. Two dates
mean the exact inclusive range.
"""

import argparse
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from database_config import get_connection
from football_config import LEAGUES, SEASON
from scripts.import_match_details import sync_match
from scripts.import_matches import fetch_fixture, fetch_matches_range, save_matches
from scripts.import_player_match_stats import (
    fetch_player_stats,
    save_fixture_stats as save_player_stats,
)
from scripts.import_standings import fetch_standings, save_standings
from scripts.import_team_match_stats import (
    fetch_team_stats,
    save_fixture_stats as save_team_stats,
)


REFERENCE_SEASON = 2025
CURRENT_MIN_MINUTES = 180
REQUEST_DELAY_SECONDS = 0.25

FINISHED_STATUSES = {"FT", "AET", "PEN"}
LIVE_STATUSES = {
    "1H", "HT", "2H", "ET", "BT", "P", "LIVE", "INT", "SUSP"
}
STALE_STATUSES = LIVE_STATUSES | {"NS", "TBD", "PST"}
DEPENDENT_DATA_STATUSES = FINISHED_STATUSES | LIVE_STATUSES


@dataclass
class RefreshSummary:
    fixtures_checked: int = 0
    fixtures_changed: int = 0
    selected_fixture_ids: set[int] = field(default_factory=set)
    fixture_failures: list[str] = field(default_factory=list)
    detail_rows: int = 0
    detail_failures: list[str] = field(default_factory=list)
    player_rows: int = 0
    player_failures: list[str] = field(default_factory=list)
    team_rows: int = 0
    team_failures: list[str] = field(default_factory=list)
    standings_rows: int = 0
    standings_failures: list[str] = field(default_factory=list)


def parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            f"invalid date {value!r}; use YYYY-MM-DD"
        ) from error


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Refresh current FutBud data and ratings through today."
    )
    parser.add_argument(
        "dates",
        nargs="*",
        type=parse_date,
        metavar="YYYY-MM-DD",
        help="optional START_DATE and END_DATE",
    )
    args = parser.parse_args(argv)

    if len(args.dates) > 2:
        parser.error("provide at most START_DATE and END_DATE")

    today = date.today()
    explicit = bool(args.dates)

    if not args.dates:
        start_date = today - timedelta(days=1)
        end_date = today
    elif len(args.dates) == 1:
        start_date = args.dates[0]
        end_date = today
    else:
        start_date, end_date = args.dates

    if start_date > end_date:
        parser.error("START_DATE cannot be after END_DATE")

    return start_date, end_date, explicit


def print_stage(number, title, state="STARTING"):
    print(f"\n[{number}] {state}: {title}", flush=True)


def get_auto_candidates(today: date):
    recent_start = today - timedelta(days=1)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    matches.id,
                    matches.league_id,
                    DATE(matches.match_date)
                FROM matches
                WHERE matches.season = %s
                  AND DATE(matches.match_date) <= %s
                  AND (
                        DATE(matches.match_date) >= %s
                     OR matches.status_short = ANY(%s)
                     OR (
                            matches.status_short = ANY(%s)
                        AND (
                               NOT EXISTS (
                                   SELECT 1
                                   FROM player_match_stats
                                   WHERE player_match_stats.match_id = matches.id
                               )
                            OR NOT EXISTS (
                                   SELECT 1
                                   FROM team_match_stats
                                   WHERE team_match_stats.match_id = matches.id
                               )
                        )
                     )
                  )
                ORDER BY matches.match_date;
                """,
                (
                    SEASON,
                    today,
                    recent_start,
                    sorted(STALE_STATUSES),
                    sorted(FINISHED_STATUSES),
                ),
            )
            rows = cursor.fetchall()

    candidate_ids = {row[0] for row in rows}
    starts = {league["id"]: recent_start for league in LEAGUES}

    for _, league_id, match_date in rows:
        starts[league_id] = min(starts.get(league_id, recent_start), match_date)

    return candidate_ids, starts


def get_local_fixture_leagues(start_date, end_date):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, league_id
                FROM matches
                WHERE season = %s
                  AND DATE(match_date) BETWEEN %s AND %s;
                """,
                (SEASON, start_date, end_date),
            )
            return dict(cursor.fetchall())


def get_fixture_leagues(fixture_ids):
    if not fixture_ids:
        return {}

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, league_id
                FROM matches
                WHERE id = ANY(%s);
                """,
                (sorted(fixture_ids),),
            )
            return dict(cursor.fetchall())


def refresh_fixtures(start_date, end_date, explicit, summary):
    if explicit:
        fixture_leagues = get_local_fixture_leagues(start_date, end_date)
        starts = {league["id"]: start_date for league in LEAGUES}
    else:
        candidate_ids, starts = get_auto_candidates(end_date)
        fixture_leagues = get_fixture_leagues(candidate_ids)

    successful_requests = 0

    for league in LEAGUES:
        league_id = league["id"]
        league_start = starts[league_id]

        try:
            fixtures = fetch_matches_range(
                league_id,
                SEASON,
                league_start,
                end_date,
            )
            checked, changed_ids = save_matches(fixtures, return_ids=True)
            successful_requests += 1
            summary.fixtures_checked += checked
            summary.fixtures_changed += len(changed_ids)

            returned_ids = {
                item.get("fixture", {}).get("id")
                for item in fixtures
                if item.get("fixture", {}).get("id") is not None
            }

            if explicit:
                summary.selected_fixture_ids.update(returned_ids)
            else:
                summary.selected_fixture_ids.update(
                    returned_ids.intersection(candidate_ids)
                )
                summary.selected_fixture_ids.update(changed_ids)

        except Exception as error:
            fixtures = []
            returned_ids = set()
            summary.fixture_failures.append(
                f"league {league_id} ({league['name']}): {error}"
            )

        time.sleep(REQUEST_DELAY_SECONDS)

        # A range lookup will not return a fixture that the provider moved
        # outside the requested dates. Refresh any locally selected fixture
        # missing from that response by ID so postponements/reschedules are
        # still corrected.
        local_ids = {
            fixture_id
            for fixture_id, local_league_id in fixture_leagues.items()
            if local_league_id == league_id
        }

        for fixture_id in sorted(local_ids - returned_ids):
            try:
                fixture = fetch_fixture(fixture_id)
                if fixture is None:
                    raise RuntimeError("API returned no fixture")
                checked, changed_ids = save_matches([fixture], return_ids=True)
                successful_requests += 1
                summary.fixtures_checked += checked
                summary.fixtures_changed += len(changed_ids)
                summary.selected_fixture_ids.add(fixture_id)
            except Exception as error:
                summary.fixture_failures.append(
                    f"fixture {fixture_id}: {error}"
                )
            time.sleep(REQUEST_DELAY_SECONDS)

    if successful_requests == 0:
        raise RuntimeError(
            "every fixture refresh request failed: "
            + "; ".join(summary.fixture_failures)
        )


def load_selected_fixtures(fixture_ids):
    if not fixture_ids:
        return []

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    league_id,
                    match_date,
                    status_short,
                    home_goals,
                    away_goals
                FROM matches
                WHERE id = ANY(%s)
                ORDER BY match_date, id;
                """,
                (sorted(fixture_ids),),
            )
            return cursor.fetchall()


def update_match_details(fixtures, summary):
    eligible = [row for row in fixtures if row[3] in DEPENDENT_DATA_STATUSES]

    if not eligible:
        return 0

    connection = get_connection()
    try:
        for fixture_id, *_ in eligible:
            try:
                result = sync_match(connection, fixture_id)
                summary.detail_rows += (
                    result["lineup_rows"] + result["event_rows"]
                )
            except Exception as error:
                summary.detail_failures.append(f"fixture {fixture_id}: {error}")
            time.sleep(REQUEST_DELAY_SECONDS)
    finally:
        connection.close()

    return len(eligible)


def update_player_stats(fixtures, summary):
    eligible = [row for row in fixtures if row[3] in DEPENDENT_DATA_STATUSES]

    for fixture_id, *_ in eligible:
        try:
            blocks = fetch_player_stats(fixture_id, raise_on_error=True)
            if blocks:
                summary.player_rows += save_player_stats(fixture_id, blocks)
        except Exception as error:
            summary.player_failures.append(f"fixture {fixture_id}: {error}")
        time.sleep(REQUEST_DELAY_SECONDS)

    return len(eligible)


def update_team_stats(fixtures, summary):
    eligible = [row for row in fixtures if row[3] in DEPENDENT_DATA_STATUSES]

    for fixture_id, *_ in eligible:
        try:
            blocks = fetch_team_stats(fixture_id, raise_on_error=True)
            if blocks:
                summary.team_rows += save_team_stats(fixture_id, blocks)
        except Exception as error:
            summary.team_failures.append(f"fixture {fixture_id}: {error}")
        time.sleep(REQUEST_DELAY_SECONDS)

    return len(eligible)


def update_standings(fixtures, summary):
    league_ids = sorted({row[1] for row in fixtures})

    for league_id in league_ids:
        try:
            rows = fetch_standings(
                league_id,
                SEASON,
                raise_on_error=True,
            )
            if rows:
                summary.standings_rows += save_standings(rows, league_id, SEASON)
        except Exception as error:
            summary.standings_failures.append(f"league {league_id}: {error}")
        time.sleep(REQUEST_DELAY_SECONDS)

    return len(league_ids)


def run_module(module, *arguments):
    command = [sys.executable, "-m", module, *map(str, arguments)]
    result = subprocess.run(command, check=False)
    if result.returncode:
        raise RuntimeError(
            f"{' '.join(command)} exited with code {result.returncode}"
        )


def rebuild_ratings():
    run_module(
        "ml.build_archetype_dataset",
        "--season", SEASON,
        "--min-minutes", CURRENT_MIN_MINUTES,
    )
    run_module(
        "ml.predict_current_season",
        "--season", SEASON,
        "--reference-season", REFERENCE_SEASON,
    )
    run_module(
        "ml.import_current_ratings",
        "--season", SEASON,
        "--reference-season", REFERENCE_SEASON,
    )


def verify_database(fixtures):
    fixture_ids = [row[0] for row in fixtures]

    with get_connection() as connection:
        with connection.cursor() as cursor:
            if fixture_ids:
                cursor.execute(
                    """
                    SELECT
                        COUNT(*) FILTER (
                            WHERE status_short = ANY(%s)
                        ),
                        COUNT(*) FILTER (
                            WHERE status_short = ANY(%s)
                              AND NOT EXISTS (
                                  SELECT 1 FROM player_match_stats
                                  WHERE player_match_stats.match_id = matches.id
                              )
                        ),
                        COUNT(*) FILTER (
                            WHERE status_short = ANY(%s)
                              AND NOT EXISTS (
                                  SELECT 1 FROM team_match_stats
                                  WHERE team_match_stats.match_id = matches.id
                              )
                        )
                    FROM matches
                    WHERE id = ANY(%s);
                    """,
                    (
                        sorted(FINISHED_STATUSES),
                        sorted(FINISHED_STATUSES),
                        sorted(FINISHED_STATUSES),
                        fixture_ids,
                    ),
                )
                completed, missing_player, missing_team = cursor.fetchone()
            else:
                completed = missing_player = missing_team = 0

            cursor.execute(
                """
                SELECT COUNT(*), MAX(updated_at)
                FROM player_season_ratings
                WHERE season = %s;
                """,
                (SEASON,),
            )
            rating_count, ratings_updated_at = cursor.fetchone()

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM player_season_rating_metrics
                WHERE season = %s;
                """,
                (SEASON,),
            )
            metric_count = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM (
                    SELECT match_id, player_id
                    FROM player_match_stats
                    GROUP BY match_id, player_id
                    HAVING COUNT(*) > 1
                ) duplicates;
                """
            )
            duplicate_player_stats = cursor.fetchone()[0]

    if duplicate_player_stats:
        raise RuntimeError(
            f"verification found {duplicate_player_stats} duplicate player-stat keys"
        )
    if not rating_count or ratings_updated_at is None:
        raise RuntimeError("verification found no current-season ratings")

    return {
        "completed": completed,
        "missing_player": missing_player,
        "missing_team": missing_team,
        "rating_count": rating_count,
        "metric_count": metric_count,
        "ratings_updated_at": ratings_updated_at,
    }


def print_failures(label, failures):
    if not failures:
        return
    print(f"  {label} failures ({len(failures)}):")
    for failure in failures:
        print(f"    - {failure}")


def main(argv=None):
    start_date, end_date, explicit = parse_args(argv)
    summary = RefreshSummary()

    print("=" * 60)
    print("FUTBUD CURRENT DATA REFRESH")
    if explicit:
        print(f"Range: {start_date} -> {end_date}")
    else:
        print(f"Automatic window through: {end_date}")
    print(f"Season: {SEASON} | Frozen reference: {REFERENCE_SEASON}")
    print("=" * 60)

    try:
        print_stage(1, "Refreshing matches")
        refresh_fixtures(start_date, end_date, explicit, summary)
        fixtures = load_selected_fixtures(summary.selected_fixture_ids)
        print(
            f"SUCCESS: {summary.fixtures_checked} fixtures checked; "
            f"{summary.fixtures_changed} records changed; "
            f"{len(fixtures)} selected for dependent refresh"
        )
        print_failures("Fixture", summary.fixture_failures)

        print_stage(2, "Updating match details and lineups")
        detail_matches = update_match_details(fixtures, summary)
        state = "SUCCESS" if detail_matches else "SKIPPED"
        print(
            f"{state}: {detail_matches} matches processed; "
            f"{summary.detail_rows} lineup/event rows written"
        )
        print_failures("Detail", summary.detail_failures)

        print_stage(3, "Updating player match stats")
        player_matches = update_player_stats(fixtures, summary)
        state = "SUCCESS" if player_matches else "SKIPPED"
        print(
            f"{state}: {player_matches} matches processed; "
            f"{summary.player_rows} rows upserted"
        )
        print_failures("Player-stat", summary.player_failures)

        print_stage(4, "Updating team match stats")
        team_matches = update_team_stats(fixtures, summary)
        state = "SUCCESS" if team_matches else "SKIPPED"
        print(
            f"{state}: {team_matches} matches processed; "
            f"{summary.team_rows} rows upserted"
        )
        print_failures("Team-stat", summary.team_failures)

        print_stage(5, "Updating standings")
        leagues = update_standings(fixtures, summary)
        state = "SUCCESS" if leagues else "SKIPPED"
        print(
            f"{state}: {leagues} affected leagues processed; "
            f"{summary.standings_rows} rows upserted"
        )
        print_failures("Standings", summary.standings_failures)

        print_stage(6, "Rebuilding current-season FutBud ratings")
        rebuild_ratings()
        print("SUCCESS: dataset rebuilt and frozen-model inference completed")

        print_stage(7, "Verifying PostgreSQL")
        verification = verify_database(fixtures)
        print(
            "SUCCESS: "
            f"{verification['rating_count']} ratings; "
            f"{verification['metric_count']} metrics; "
            f"ratings updated {verification['ratings_updated_at']}"
        )
        print(
            "Selected completed fixtures: "
            f"{verification['completed']}; "
            f"missing player stats: {verification['missing_player']}; "
            f"missing team stats: {verification['missing_team']}"
        )

    except Exception as error:
        print(f"\nFAILED: {error}", file=sys.stderr)
        print("Refresh stopped before dependent stages could continue safely.")
        return 1

    all_failures = (
        summary.fixture_failures
        + summary.detail_failures
        + summary.player_failures
        + summary.team_failures
        + summary.standings_failures
    )

    print("\n" + "=" * 60)
    print("REFRESH COMPLETE")
    print(f"Individual API failures: {len(all_failures)}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
