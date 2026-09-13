import os
import requests

from psycopg.rows import dict_row

from dotenv import load_dotenv





import psycopg
from datetime import date

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_match_head_to_head(
    home_team_id: int,
    away_team_id: int,
    last: int = 10,
):
    api_key = os.getenv(
        "API_FOOTBALL_KEY"
    )

    print(
        "H2H API KEY FOUND:",
        bool(api_key)
    )


    empty_result = {
        "homeWins": 0,
        "draws": 0,
        "awayWins": 0,
        "matches": [],
    }

    if not api_key:
        print(
            "API_FOOTBALL_KEY missing. "
            "Skipping H2H."
        )

        return empty_result


    try:

        response = requests.get(
            (
                "https://v3.football."
                "api-sports.io/"
                "fixtures/headtohead"
            ),
            headers={
                "x-apisports-key":
                    api_key,
            },
            params={
                "h2h":
                    (
                        f"{home_team_id}-"
                        f"{away_team_id}"
                    ),
                "last":
                    last,
            },
            timeout=20,
        )

        response.raise_for_status()

        payload = response.json()

        if payload.get("errors"):

            print(
                "H2H API error:",
                payload["errors"],
            )

            return empty_result


        fixtures = (
            payload.get("response")
            or []
        )


        home_wins = 0
        draws = 0
        away_wins = 0

        meetings = []


        for item in fixtures:

            fixture = (
                item.get("fixture")
                or {}
            )

            league = (
                item.get("league")
                or {}
            )

            teams = (
                item.get("teams")
                or {}
            )

            goals = (
                item.get("goals")
                or {}
            )


            fixture_home = (
                teams.get("home")
                or {}
            )

            fixture_away = (
                teams.get("away")
                or {}
            )


            home_goals = goals.get(
                "home"
            )

            away_goals = goals.get(
                "away"
            )


            if (
                home_goals is not None
                and
                away_goals is not None
            ):

                if (
                    home_goals
                    == away_goals
                ):

                    draws += 1

                else:

                    winner_id = (
                        fixture_home.get("id")
                        if
                        home_goals
                        > away_goals
                        else
                        fixture_away.get("id")
                    )


                    if (
                        winner_id
                        == home_team_id
                    ):

                        home_wins += 1


                    elif (
                        winner_id
                        == away_team_id
                    ):

                        away_wins += 1


            meetings.append(
                {
                    "id":
                        fixture.get("id"),

                    "date":
                        fixture.get("date"),

                    "status":
                        (
                            fixture.get(
                                "status"
                            )
                            or {}
                        ).get("short"),

                    "league": {
                        "id":
                            league.get("id"),

                        "name":
                            league.get(
                                "name"
                            ),

                        "logoUrl":
                            league.get(
                                "logo"
                            ),
                    },

                    "homeTeam": {
                        "id":
                            fixture_home.get(
                                "id"
                            ),

                        "name":
                            fixture_home.get(
                                "name"
                            ),

                        "logoUrl":
                            fixture_home.get(
                                "logo"
                            ),
                    },

                    "awayTeam": {
                        "id":
                            fixture_away.get(
                                "id"
                            ),

                        "name":
                            fixture_away.get(
                                "name"
                            ),

                        "logoUrl":
                            fixture_away.get(
                                "logo"
                            ),
                    },

                    "homeGoals":
                        home_goals,

                    "awayGoals":
                        away_goals,
                }
            )


        return {
            "homeWins":
                home_wins,

            "draws":
                draws,

            "awayWins":
                away_wins,

            "matches":
                meetings,
        }


    except Exception as error:

        print(
            "H2H request failed:",
            error,
        )

        return empty_result

def get_team_stat_leaders(
    cursor,
    team_id: int,
    league_id: int,
    season: int,
    stat_column: str,
    limit: int = 3,
):

    allowed = {
        "goals",
        "assists",
        "key_passes",
    }

    if stat_column not in allowed:
        raise ValueError(
            "Invalid statistic"
        )

    cursor.execute(
        f"""
        SELECT
            players.id,
            players.name,
            players.photo_url,

            COALESCE(
                squads.shirt_number,
                NULL
            ),

            COALESCE(
                squads.position,
                players.primary_position
            ),

            SUM(
                COALESCE(
                    player_match_stats.{stat_column},
                    0
                )
            ) AS total

        FROM player_match_stats

        JOIN matches
            ON matches.id =
               player_match_stats.match_id

        JOIN players
            ON players.id =
               player_match_stats.player_id

        LEFT JOIN squads
            ON squads.player_id =
               players.id

            AND squads.team_id = %s
            AND squads.season = %s

        WHERE
            player_match_stats.team_id = %s

            AND matches.league_id = %s

            AND matches.season = %s

        GROUP BY
            players.id,
            players.name,
            players.photo_url,
            squads.shirt_number,
            squads.position,
            players.primary_position

        HAVING
            SUM(
                COALESCE(
                    player_match_stats.{stat_column},
                    0
                )
            ) > 0

        ORDER BY
            total DESC,
            players.name

        LIMIT %s;
        """,
        (
            team_id,
            season,
            team_id,
            league_id,
            season,
            limit,
        ),
    )

    return [
        {
            "player": {
                "id": row[0],
                "name": row[1],
                "photoUrl": row[2],
                "shirtNumber": row[3],
                "position": row[4],
            },
            "value": int(
                row[5] or 0
            ),
        }

        for row in cursor.fetchall()
    ]

@app.get("/matches/{match_id}/dashboard")
def get_match_dashboard(
    match_id: int,
):

    connection = get_connection()

    cursor = connection.cursor(
        row_factory=dict_row
    )

    try:

        # ==========================================
        # MATCH HEADER
        # ==========================================

        cursor.execute(
            """
            SELECT
                m.id,
                m.match_date,
                m.round,
                m.referee,
                m.venue_name,

                m.status_long,
                m.status_short,
                m.elapsed AS status_elapsed,

                m.home_goals,
                m.away_goals,

                m.season,

                l.id AS league_id,
                l.name AS league_name,
                l.logo_url AS league_logo_url,

                home.id AS home_team_id,
                home.name AS home_team_name,
                home.logo_url AS home_team_logo_url,

                away.id AS away_team_id,
                away.name AS away_team_name,
                away.logo_url AS away_team_logo_url

            FROM matches m

            JOIN leagues l
                ON l.id = m.league_id

            JOIN teams home
                ON home.id = m.home_team_id

            JOIN teams away
                ON away.id = m.away_team_id

            WHERE m.id = %s;
            """,
            (
                match_id,
            ),
        )


        match = cursor.fetchone()


        if not match:

            raise HTTPException(
                status_code=404,
                detail="Match not found",
            )


        home_team_id = (
            match["home_team_id"]
        )

        away_team_id = (
            match["away_team_id"]
        )


        # ==========================================
        # MATCH EVENTS
        # ==========================================

        cursor.execute(
            """
            SELECT
                event_index,
                team_id,

                player_id,
                player_name,

                assist_id,
                assist_name,

                elapsed,
                extra,

                event_type,
                detail,
                comments

            FROM match_events

            WHERE match_id = %s

            ORDER BY
                elapsed,
                extra NULLS FIRST,
                event_index;
            """,
            (
                match_id,
            ),
        )


        event_rows = (
            cursor.fetchall()
        )


        events = []


        for row in event_rows:

            events.append(
                {
                    "index":
                        row[
                            "event_index"
                        ],

                    "teamId":
                        row[
                            "team_id"
                        ],

                    "player": {
                        "id":
                            row[
                                "player_id"
                            ],

                        "name":
                            row[
                                "player_name"
                            ],
                    },

                    "assist": {
                        "id":
                            row[
                                "assist_id"
                            ],

                        "name":
                            row[
                                "assist_name"
                            ],
                    },

                    "time": {
                        "elapsed":
                            row[
                                "elapsed"
                            ],

                        "extra":
                            row[
                                "extra"
                            ],
                    },

                    "type":
                        row[
                            "event_type"
                        ],

                    "detail":
                        row[
                            "detail"
                        ],

                    "comments":
                        row[
                            "comments"
                        ],
                }
            )


        # ==========================================
        # LINEUP HEADER
        # formation + coach
        # ==========================================

        cursor.execute(
            """
            SELECT
                team_id,
                formation,

                coach_id,
                coach_name,
                coach_photo_url

            FROM match_lineups

            WHERE match_id = %s;
            """,
            (
                match_id,
            ),
        )


        lineup_rows = (
            cursor.fetchall()
        )


        lineups = {}


        for row in lineup_rows:

            team_id = (
                row["team_id"]
            )


            lineups[
                team_id
            ] = {
                "formation":
                    row[
                        "formation"
                    ],

                "coach": {
                    "id":
                        row[
                            "coach_id"
                        ],

                    "name":
                        row[
                            "coach_name"
                        ],

                    "photoUrl":
                        row[
                            "coach_photo_url"
                        ],
                },

                "starters": [],
                "bench": [],
            }


        # ==========================================
        # STARTING XI + BENCH
        # ==========================================

        cursor.execute(
            """
            SELECT
                ms.team_id,
                ms.role,

                ms.shirt_number,
                ms.position,
                ms.grid,

                p.id AS player_id,
                p.name AS player_name,
                p.photo_url AS player_photo_url

            FROM matchday_squad ms

            JOIN players p
                ON p.id = ms.player_id

            WHERE ms.match_id = %s

            ORDER BY
                ms.team_id,
                ms.role,
                ms.grid NULLS LAST,
                ms.shirt_number;
            """,
            (
                match_id,
            ),
        )


        squad_rows = (
            cursor.fetchall()
        )


        for row in squad_rows:

            team_id = (
                row["team_id"]
            )


            if team_id not in lineups:

                lineups[
                    team_id
                ] = {
                    "formation":
                        None,

                    "coach": {
                        "id": None,
                        "name": None,
                        "photoUrl": None,
                    },

                    "starters": [],
                    "bench": [],
                }


            player = {
                "id":
                    row[
                        "player_id"
                    ],

                "name":
                    row[
                        "player_name"
                    ],

                "photoUrl":
                    row[
                        "player_photo_url"
                    ],

                "shirtNumber":
                    row[
                        "shirt_number"
                    ],

                "position":
                    row[
                        "position"
                    ],

                "grid":
                    row[
                        "grid"
                    ],
            }


            if (
                row["role"]
                == "starter"
            ):

                lineups[
                    team_id
                ][
                    "starters"
                ].append(
                    player
                )

            else:

                lineups[
                    team_id
                ][
                    "bench"
                ].append(
                    player
                )


        # ==========================================
        # TEAM MATCH STATISTICS
        # Uses your REAL column names
        # ==========================================

        cursor.execute(
            """
            SELECT
                team_id,

                shots_on_goal
                    AS shots_on_target,

                shots_off_goal
                    AS shots_off_target,

                total_shots
                    AS shots_total,

                blocked_shots
                    AS shots_blocked,

                shots_inside_box,
                shots_outside_box,

                fouls,

                corner_kicks
                    AS corners,

                offsides,

                possession,

                yellow_cards,
                red_cards,

                goalkeeper_saves,

                total_passes
                    AS passes_total,

                accurate_passes
                    AS passes_accurate,

                pass_accuracy

            FROM team_match_stats

            WHERE match_id = %s;
            """,
            (
                match_id,
            ),
        )


        team_stat_rows = (
            cursor.fetchall()
        )


        team_stats = {}


        for row in team_stat_rows:

            team_id = (
                row["team_id"]
            )


            team_stats[
                team_id
            ] = {

                "shots": {
                    "total":
                        row[
                            "shots_total"
                        ],

                    "onTarget":
                        row[
                            "shots_on_target"
                        ],

                    "offTarget":
                        row[
                            "shots_off_target"
                        ],

                    "blocked":
                        row[
                            "shots_blocked"
                        ],

                    "insideBox":
                        row[
                            "shots_inside_box"
                        ],

                    "outsideBox":
                        row[
                            "shots_outside_box"
                        ],
                },


                "fouls":
                    row[
                        "fouls"
                    ],


                "corners":
                    row[
                        "corners"
                    ],


                "offsides":
                    row[
                        "offsides"
                    ],


                "possession":
                    row[
                        "possession"
                    ],


                "yellowCards":
                    row[
                        "yellow_cards"
                    ],


                "redCards":
                    row[
                        "red_cards"
                    ],


                "goalkeeperSaves":
                    row[
                        "goalkeeper_saves"
                    ],


                "passes": {
                    "total":
                        row[
                            "passes_total"
                        ],

                    "accurate":
                        row[
                            "passes_accurate"
                        ],

                    "accuracy":
                        row[
                            "pass_accuracy"
                        ],
                },
            }


        # ==========================================
        # PLAYER MATCH STATISTICS
        # ==========================================

        cursor.execute(
            """
            SELECT
                pms.team_id,

                p.id
                    AS player_id,

                p.name
                    AS player_name,

                p.photo_url
                    AS player_photo_url,

                pms.minutes,
                pms.shirt_number,
                pms.position,

                pms.provider_rating,

                pms.captain,
                pms.substitute,

                pms.offsides,

                pms.shots_total,
                pms.shots_on_target,

                pms.goals,
                pms.goals_conceded,
                pms.assists,
                pms.saves,

                pms.passes_total,
                pms.key_passes,
                pms.pass_accuracy,

                pms.tackles,
                pms.blocks,
                pms.interceptions,

                pms.duels_total,
                pms.duels_won,

                pms.dribbles_attempted,
                pms.dribbles_successful,
                pms.dribbled_past,

                pms.fouls_drawn,
                pms.fouls_committed,

                pms.yellow_cards,
                pms.red_cards,

                pms.penalties_won,
                pms.penalties_committed,
                pms.penalties_scored,
                pms.penalties_missed,
                pms.penalties_saved

            FROM player_match_stats pms

            JOIN players p
                ON p.id = pms.player_id

            WHERE pms.match_id = %s

            ORDER BY
                pms.team_id,
                pms.minutes DESC NULLS LAST,
                pms.provider_rating DESC NULLS LAST;
            """,
            (
                match_id,
            ),
        )


        player_rows = (
            cursor.fetchall()
        )


        player_stats = {
            home_team_id: [],
            away_team_id: [],
        }


        for row in player_rows:

            team_id = (
                row["team_id"]
            )


            if team_id not in player_stats:

                player_stats[
                    team_id
                ] = []


            player_stats[
                team_id
            ].append(
                {

                    "player": {
                        "id":
                            row[
                                "player_id"
                            ],

                        "name":
                            row[
                                "player_name"
                            ],

                        "photoUrl":
                            row[
                                "player_photo_url"
                            ],
                    },


                    "minutes":
                        row[
                            "minutes"
                        ],


                    "shirtNumber":
                        row[
                            "shirt_number"
                        ],


                    "position":
                        row[
                            "position"
                        ],


                    "rating":
                        row[
                            "provider_rating"
                        ],


                    "captain":
                        row[
                            "captain"
                        ],


                    "substitute":
                        row[
                            "substitute"
                        ],


                    "offsides":
                        row[
                            "offsides"
                        ],


                    "shots": {
                        "total":
                            row[
                                "shots_total"
                            ],

                        "onTarget":
                            row[
                                "shots_on_target"
                            ],
                    },


                    "goals":
                        row[
                            "goals"
                        ],


                    "goalsConceded":
                        row[
                            "goals_conceded"
                        ],


                    "assists":
                        row[
                            "assists"
                        ],


                    "saves":
                        row[
                            "saves"
                        ],


                    "passes": {
                        "total":
                            row[
                                "passes_total"
                            ],

                        "key":
                            row[
                                "key_passes"
                            ],

                        "accuracy":
                            row[
                                "pass_accuracy"
                            ],
                    },


                    "tackles":
                        row[
                            "tackles"
                        ],


                    "blocks":
                        row[
                            "blocks"
                        ],


                    "interceptions":
                        row[
                            "interceptions"
                        ],


                    "duels": {
                        "total":
                            row[
                                "duels_total"
                            ],

                        "won":
                            row[
                                "duels_won"
                            ],
                    },


                    "dribbles": {
                        "attempted":
                            row[
                                "dribbles_attempted"
                            ],

                        "successful":
                            row[
                                "dribbles_successful"
                            ],

                        "past":
                            row[
                                "dribbled_past"
                            ],
                    },


                    "fouls": {
                        "drawn":
                            row[
                                "fouls_drawn"
                            ],

                        "committed":
                            row[
                                "fouls_committed"
                            ],
                    },


                    "cards": {
                        "yellow":
                            row[
                                "yellow_cards"
                            ],

                        "red":
                            row[
                                "red_cards"
                            ],
                    },


                    "penalties": {
                        "won":
                            row[
                                "penalties_won"
                            ],

                        "committed":
                            row[
                                "penalties_committed"
                            ],

                        "scored":
                            row[
                                "penalties_scored"
                            ],

                        "missed":
                            row[
                                "penalties_missed"
                            ],

                        "saved":
                            row[
                                "penalties_saved"
                            ],
                    },
                }
            )


        # ==========================================
        # HEAD TO HEAD
        # ==========================================

        head_to_head = (
            get_match_head_to_head(
                home_team_id,
                away_team_id,
                last=10,
            )
        )


        # ==========================================
        # FINAL RESPONSE
        # ==========================================

        return {

            "match": {

                "id":
                    match[
                        "id"
                    ],


                "date":
                    match[
                        "match_date"
                    ],


                "season":
                    match[
                        "season"
                    ],


                "round":
                    match[
                        "round"
                    ],


                "referee":
                    match[
                        "referee"
                    ],


                "venue":
                    match[
                        "venue_name"
                    ],


                "status": {

                    "long":
                        match[
                            "status_long"
                        ],

                    "short":
                        match[
                            "status_short"
                        ],

                    "elapsed":
                        match[
                            "status_elapsed"
                        ],
                },


                "league": {

                    "id":
                        match[
                            "league_id"
                        ],

                    "name":
                        match[
                            "league_name"
                        ],

                    "logoUrl":
                        match[
                            "league_logo_url"
                        ],
                },


                "homeTeam": {

                    "id":
                        home_team_id,

                    "name":
                        match[
                            "home_team_name"
                        ],

                    "logoUrl":
                        match[
                            "home_team_logo_url"
                        ],
                },


                "awayTeam": {

                    "id":
                        away_team_id,

                    "name":
                        match[
                            "away_team_name"
                        ],

                    "logoUrl":
                        match[
                            "away_team_logo_url"
                        ],
                },


                "score": {

                    "home":
                        match[
                            "home_goals"
                        ],

                    "away":
                        match[
                            "away_goals"
                        ],
                },
            },


            "events":
                events,


            "lineups": {

                "home":
                    lineups.get(
                        home_team_id,
                        {
                            "formation":
                                None,

                            "coach":
                                None,

                            "starters":
                                [],

                            "bench":
                                [],
                        },
                    ),


                "away":
                    lineups.get(
                        away_team_id,
                        {
                            "formation":
                                None,

                            "coach":
                                None,

                            "starters":
                                [],

                            "bench":
                                [],
                        },
                    ),
            },


            "matchStats": {

                "home":
                    team_stats.get(
                        home_team_id
                    ),

                "away":
                    team_stats.get(
                        away_team_id
                    ),
            },


            "playerStats": {

                "home":
                    player_stats.get(
                        home_team_id,
                        [],
                    ),

                "away":
                    player_stats.get(
                        away_team_id,
                        [],
                    ),
            },


            "headToHead":
                head_to_head,
        }


    finally:

        cursor.close()
        connection.close()

@app.get("/matches")
def get_matches(
    match_date: date | None = None,
    team_id: int | None = None,
    league_id: int | None = None,
    season: int = 2026,
):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            matches.id,
            matches.round,
            matches.match_date,
            matches.status_long,
            matches.status_short,
            matches.elapsed,

            matches.home_goals,
            matches.away_goals,

            home.id,
            home.name,
            home.code,
            home.logo_url,

            away.id,
            away.name,
            away.code,
            away.logo_url,

            leagues.id,
            leagues.name,
            leagues.logo_url

        FROM matches

        JOIN teams AS home
            ON home.id = matches.home_team_id

        JOIN teams AS away
            ON away.id = matches.away_team_id

        JOIN leagues
            ON leagues.id = matches.league_id

        WHERE matches.season = %s
    """

    params = [season]

    if league_id is not None:
        query += """
            AND matches.league_id = %s
        """
        params.append(league_id)

    if match_date is not None:
        query += """
            AND DATE(matches.match_date) = %s
        """
        params.append(match_date)

    if team_id is not None:
        query += """
            AND (
                matches.home_team_id = %s
                OR matches.away_team_id = %s
            )
        """

        params.extend([
            team_id,
            team_id,
        ])

    query += """
        ORDER BY
            leagues.name,
            matches.match_date;
    """

    cursor.execute(query, params)

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    matches_list = []

    for row in rows:
        matches_list.append({
            "id": row[0],
            "round": row[1],
            "date": row[2],

            "status": {
                "long": row[3],
                "short": row[4],
                "elapsed": row[5],
            },

            "score": {
                "home": row[6],
                "away": row[7],
            },

            "homeTeam": {
                "id": row[8],
                "name": row[9],
                "code": row[10],
                "logoUrl": row[11],
            },

            "awayTeam": {
                "id": row[12],
                "name": row[13],
                "code": row[14],
                "logoUrl": row[15],
            },

            "league": {
                "id": row[16],
                "name": row[17],
                "logoUrl": row[18],
            },
        })

    return matches_list

@app.get("/teams")
def get_teams(
    league_id: int | None = None,
    season: int | None = None,
):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            teams.id,
            teams.name,
            teams.code,
            teams.country,
            teams.founded,
            teams.logo_url,
            teams.venue_id,
            teams.venue_name,
            teams.venue_city,
            teams.venue_capacity,
            teams.venue_image_url
        FROM teams
    """

    params = []

    if league_id is not None and season is not None:
        query += """
            JOIN team_league_seasons
                ON teams.id =
                   team_league_seasons.team_id

            WHERE
                team_league_seasons.league_id = %s
                AND team_league_seasons.season = %s
        """

        params.extend([
            league_id,
            season
        ])

    query += """
        ORDER BY teams.name;
    """

    cursor.execute(query, params)

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    teams = []

    for row in rows:
        teams.append(
            {
                "id": row[0],
                "name": row[1],
                "code": row[2],
                "country": row[3],
                "founded": row[4],
                "logoUrl": row[5],

                "venue": {
                    "id": row[6],
                    "name": row[7],
                    "city": row[8],
                    "capacity": row[9],
                    "imageUrl": row[10],
                },
            }
        )

    return teams


def get_connection():
    return psycopg.connect(
        dbname="futbud",
        user="futbud_user",
        password="Adid@s1738",
        host="localhost",
        port="5432",
    )

def get_stat_leaders(
    cursor,
    stat_column: str,
    season: int,
    limit: int,
    league_id: int | None = None,
):
    allowed_columns = {
        "goals",
        "assists",
        "key_passes",
        "interceptions",
    }

    if stat_column not in allowed_columns:
        raise ValueError(
            "Invalid leaderboard statistic"
        )

    query = f"""
        WITH player_totals AS (

            SELECT
                player_match_stats.player_id,

                SUM(
                    COALESCE(
                        player_match_stats.{stat_column},
                        0
                    )
                ) AS stat_total

            FROM player_match_stats

            JOIN matches
                ON matches.id =
                   player_match_stats.match_id

            WHERE matches.season = %s
    """

    params = [season]

    if league_id is not None:

        query += """
            AND matches.league_id = %s
        """

        params.append(
            league_id
        )

    query += f"""
            GROUP BY
                player_match_stats.player_id

            HAVING SUM(
                COALESCE(
                    player_match_stats.{stat_column},
                    0
                )
            ) > 0
        )

        SELECT
            players.id,
            players.name,
            players.photo_url,

            player_totals.stat_total,

            latest_team.team_id,
            latest_team.team_name,
            latest_team.team_logo

        FROM player_totals

        JOIN players
            ON players.id =
               player_totals.player_id

        LEFT JOIN LATERAL (

            SELECT
                teams.id AS team_id,
                teams.name AS team_name,
                teams.logo_url AS team_logo

            FROM player_match_stats
                AS latest_stats

            JOIN matches
                AS latest_match

                ON latest_match.id =
                   latest_stats.match_id

            JOIN teams
                ON teams.id =
                   latest_stats.team_id

            WHERE latest_stats.player_id =
                  player_totals.player_id

              AND latest_match.season = %s
    """

    params.append(
        season
    )

    if league_id is not None:

        query += """
              AND latest_match.league_id = %s
        """

        params.append(
            league_id
        )

    query += """
            ORDER BY
                latest_match.match_date DESC

            LIMIT 1

        ) AS latest_team

        ON TRUE

        ORDER BY
            player_totals.stat_total DESC,
            players.name

        LIMIT %s;
    """

    params.append(
        limit
    )

    cursor.execute(
        query,
        params,
    )

    rows = cursor.fetchall()

    leaders = []

    for row in rows:

        leaders.append({
            "player": {
                "id": row[0],
                "name": row[1],
                "photoUrl": row[2],
            },

            "value": row[3],

            "team": {
                "id": row[4],
                "name": row[5],
                "logoUrl": row[6],
            }
            if row[4] is not None
            else None,
        })

    return leaders

def build_leader_list(
    rows,
    stat_key,
    limit,
):

    eligible = [
        row
        for row in rows
        if (row[stat_key] or 0) > 0
    ]

    eligible.sort(
        key=lambda row: (
            -(row[stat_key] or 0),
            row["player_name"],
        )
    )

    leaders = []

    for row in eligible[:limit]:

        leaders.append(
            {
                "player": {
                    "id":
                        row["player_id"],

                    "name":
                        row["player_name"],

                    "photoUrl":
                        row["player_photo_url"],
                },

                "value":
                    int(
                        row[stat_key]
                        or 0
                    ),

                "team": {
                    "id":
                        row["team_id"],

                    "name":
                        row["team_name"],

                    "logoUrl":
                        row["team_logo_url"],
                }
                if row["team_id"]
                is not None
                else None,
            }
        )

    return leaders


@app.get("/leaders")
def get_leaders(
    season: int = 2026,
    limit: int = 5,
):

    connection = get_connection()

    cursor = connection.cursor(
        row_factory=dict_row
    )

    try:

        cursor.execute(
            """
            SELECT
                p.id
                    AS player_id,

                p.name
                    AS player_name,

                p.photo_url
                    AS player_photo_url,

                SUM(
                    COALESCE(
                        pms.goals,
                        0
                    )
                )
                    AS goals,

                SUM(
                    COALESCE(
                        pms.assists,
                        0
                    )
                )
                    AS assists,

                SUM(
                    COALESCE(
                        pms.key_passes,
                        0
                    )
                )
                    AS key_passes,

                SUM(
                    COALESCE(
                        pms.interceptions,
                        0
                    )
                )
                    AS interceptions,

                (
                    ARRAY_AGG(
                        t.id
                        ORDER BY
                            m.match_date DESC
                    )
                )[1]
                    AS team_id,

                (
                    ARRAY_AGG(
                        t.name
                        ORDER BY
                            m.match_date DESC
                    )
                )[1]
                    AS team_name,

                (
                    ARRAY_AGG(
                        t.logo_url
                        ORDER BY
                            m.match_date DESC
                    )
                )[1]
                    AS team_logo_url

            FROM player_match_stats pms

            JOIN matches m
                ON m.id =
                   pms.match_id

            JOIN players p
                ON p.id =
                   pms.player_id

            JOIN teams t
                ON t.id =
                   pms.team_id

            WHERE
                m.season = %s

            GROUP BY
                p.id,
                p.name,
                p.photo_url;
            """,
            (
                season,
            ),
        )

        rows = cursor.fetchall()

        return {
            "goals":
                build_leader_list(
                    rows,
                    "goals",
                    limit,
                ),

            "assists":
                build_leader_list(
                    rows,
                    "assists",
                    limit,
                ),

            "keyPasses":
                build_leader_list(
                    rows,
                    "key_passes",
                    limit,
                ),

            "interceptions":
                build_leader_list(
                    rows,
                    "interceptions",
                    limit,
                ),
        }

    finally:

        cursor.close()
        connection.close()


@app.get("/")
def home():
    return {
        "message": "FutBud API is running"
    }


@app.get("/teams/{team_id}/dashboard")
def get_team_dashboard(
    team_id: int,
    season: int = 2026,
):

    connection = get_connection()

    cursor = connection.cursor()

    # ============================================
    # TEAM + LEAGUE
    # ============================================

    cursor.execute(
        """
        SELECT
            teams.id,
            teams.name,
            teams.code,
            teams.country,
            teams.founded,
            teams.logo_url,

            teams.venue_name,
            teams.venue_city,
            teams.venue_capacity,
            teams.venue_image_url,

            leagues.id,
            leagues.name,
            leagues.logo_url

        FROM teams

        JOIN team_league_seasons
            ON team_league_seasons.team_id =
               teams.id

            AND team_league_seasons.season =
                %s

        JOIN leagues
            ON leagues.id =
               team_league_seasons.league_id

        WHERE teams.id = %s

        LIMIT 1;
        """,
        (
            season,
            team_id,
        ),
    )

    row = cursor.fetchone()

    if row is None:

        cursor.close()
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Team not found",
        )

    league_id = row[10]

    team = {
        "id": row[0],
        "name": row[1],
        "code": row[2],
        "country": row[3],
        "founded": row[4],
        "logoUrl": row[5],

        "venue": {
            "name": row[6],
            "city": row[7],
            "capacity": row[8],
            "imageUrl": row[9],
        },

        "league": {
            "id": row[10],
            "name": row[11],
            "logoUrl": row[12],
        },

        "season": season,
    }

    # ============================================
    # STANDING
    # ============================================

    cursor.execute(
        """
        SELECT
            rank,
            points,
            played,
            wins,
            draws,
            losses,
            goals_for,
            goals_against,
            goals_difference,
            form

        FROM standings

        WHERE team_id = %s
          AND league_id = %s
          AND season = %s;
        """,
        (
            team_id,
            league_id,
            season,
        ),
    )

    standing_row = cursor.fetchone()

    standing = None

    if standing_row:

        standing = {
            "rank":
                standing_row[0],

            "points":
                standing_row[1],

            "played":
                standing_row[2],

            "wins":
                standing_row[3],

            "draws":
                standing_row[4],

            "losses":
                standing_row[5],

            "goalsFor":
                standing_row[6],

            "goalsAgainst":
                standing_row[7],

            "goalDifference":
                standing_row[8],

            "form":
                standing_row[9],
        }

    # ============================================
    # ALL LEAGUE MATCHES FOR THIS TEAM
    # ============================================

    cursor.execute(
        """
        SELECT
            matches.id,
            matches.match_date,

            matches.status_long,
            matches.status_short,

            matches.home_goals,
            matches.away_goals,

            home.id,
            home.name,
            home.logo_url,

            away.id,
            away.name,
            away.logo_url

        FROM matches

        JOIN teams AS home
            ON home.id =
               matches.home_team_id

        JOIN teams AS away
            ON away.id =
               matches.away_team_id

        WHERE matches.season = %s

          AND matches.league_id =
              %s

          AND (
              matches.home_team_id =
                  %s

              OR

              matches.away_team_id =
                  %s
          )

        ORDER BY
            matches.match_date;
        """,
        (
            season,
            league_id,
            team_id,
            team_id,
        ),
    )

    match_rows = cursor.fetchall()

    all_matches = []

    for match in match_rows:

        is_home = match[6] == team_id

        team_goals = (
            match[4]
            if is_home
            else match[5]
        )

        opponent_goals = (
            match[5]
            if is_home
            else match[4]
        )

        opponent = (
            {
                "id": match[9],
                "name": match[10],
                "logoUrl": match[11],
            }
            if is_home
            else
            {
                "id": match[6],
                "name": match[7],
                "logoUrl": match[8],
            }
        )

        result = None

        if (
            match[3]
            in (
                "FT",
                "AET",
                "PEN",
            )
            and
            team_goals is not None
            and
            opponent_goals is not None
        ):

            if team_goals > opponent_goals:
                letter = "W"

            elif team_goals < opponent_goals:
                letter = "L"

            else:
                letter = "D"

            result = (
                f"{letter} "
                f"{team_goals}-"
                f"{opponent_goals}"
            )

        all_matches.append({
            "id": match[0],
            "date": match[1],

            "status": {
                "long": match[2],
                "short": match[3],
            },

            "homeTeam": {
                "id": match[6],
                "name": match[7],
                "logoUrl": match[8],
            },

            "awayTeam": {
                "id": match[9],
                "name": match[10],
                "logoUrl": match[11],
            },

            "homeGoals": match[4],
            "awayGoals": match[5],

            "homeAway":
                "H"
                if is_home
                else "A",

            "opponent": opponent,

            "result": result,
        })

    finished_statuses = {
        "FT",
        "AET",
        "PEN",
    }

    completed = [
        match
        for match in all_matches

        if match["status"]["short"]
        in finished_statuses
    ]

    upcoming = [
        match
        for match in all_matches

        if match["status"]["short"]
        not in finished_statuses
    ]

    recent_results = list(
        reversed(
            completed[-5:]
        )
    )

    next_match = (
        upcoming[0]
        if upcoming
        else None
    )

    # ============================================
    # LEAGUE CONTEXT
    # ============================================

    league_context = []

    if standing:

        cursor.execute(
            """
            SELECT
                standings.rank,

                teams.id,
                teams.name,
                teams.logo_url,

                standings.played,
                standings.goals_difference,
                standings.points

            FROM standings

            JOIN teams
                ON teams.id =
                   standings.team_id

            WHERE standings.league_id = %s
              AND standings.season = %s

            ORDER BY
                ABS(
                    standings.rank - %s
                ),
                standings.rank

            LIMIT 5;
            """,
            (
                league_id,
                season,
                standing["rank"],
            ),
        )

        context_rows = cursor.fetchall()

        context_rows.sort(
            key=lambda item:
                item[0]
        )

        league_context = [
            {
                "rank": item[0],

                "team": {
                    "id": item[1],
                    "name": item[2],
                    "logoUrl": item[3],
                },

                "played": item[4],

                "goalDifference":
                    item[5],

                "points":
                    item[6],
            }

            for item
            in context_rows
        ]

    # ============================================
    # TEAM LEADERS
    # ============================================

    goals_leaders = get_team_stat_leaders(
            cursor,
            team_id,
            league_id,
            season,
            "goals",
        )

    assist_leaders = get_team_stat_leaders(
            cursor,
            team_id,
            league_id,
            season,
            "assists",
        )

    key_pass_leaders = get_team_stat_leaders(
            cursor,
            team_id,
            league_id,
            season,
            "key_passes",
        )

    # ============================================
    # FUTBUD SQUAD
    #
    # Current registered player AND:
    #
    # 1. Has been named in a matchday squad
    # OR
    # 2. Is currently injured
    # ============================================

    cursor.execute(
        """
        WITH selection_totals AS (

            SELECT
                matchday_squad.player_id,

                COUNT(
                    DISTINCT
                    matchday_squad.match_id
                )
                AS matchday_selections,

                COUNT(
                    DISTINCT
                    matchday_squad.match_id
                )
                FILTER (
                    WHERE
                        matchday_squad.role =
                        'starter'
                )
                AS starts

            FROM matchday_squad

            JOIN matches
                ON matches.id =
                   matchday_squad.match_id

            WHERE
                matchday_squad.team_id = %s

                AND matches.league_id = %s

                AND matches.season = %s

            GROUP BY
                matchday_squad.player_id
        ),

        performance AS (

            SELECT
                player_match_stats.player_id,

                COUNT(*)
                FILTER (
                    WHERE
                        COALESCE(
                            player_match_stats.minutes,
                            0
                        ) > 0
                )
                AS appearances,

                COALESCE(
                    SUM(
                        player_match_stats.minutes
                    ),
                    0
                )
                AS minutes,

                COALESCE(
                    SUM(
                        player_match_stats.goals
                    ),
                    0
                )
                AS goals,

                COALESCE(
                    SUM(
                        player_match_stats.assists
                    ),
                    0
                )
                AS assists

            FROM player_match_stats

            JOIN matches
                ON matches.id =
                   player_match_stats.match_id

            WHERE
                player_match_stats.team_id =
                    %s

                AND matches.league_id =
                    %s

                AND matches.season =
                    %s

            GROUP BY
                player_match_stats.player_id
        )

        SELECT
            players.id,
            players.name,
            players.photo_url,
            players.nationality,
            players.birth_date,

            squads.shirt_number,

            COALESCE(
                squads.position,
                players.primary_position
            ),

            players.is_injured,

            COALESCE(
                selection_totals.matchday_selections,
                0
            ),

            COALESCE(
                selection_totals.starts,
                0
            ),

            COALESCE(
                performance.appearances,
                0
            ),

            COALESCE(
                performance.minutes,
                0
            ),

            COALESCE(
                performance.goals,
                0
            ),

            COALESCE(
                performance.assists,
                0
            ),

            player_season_ratings.futbud_rating

        FROM squads

        JOIN players
            ON players.id =
               squads.player_id

        LEFT JOIN selection_totals
            ON selection_totals.player_id =
               players.id

        LEFT JOIN performance
            ON performance.player_id =
               players.id

        LEFT JOIN player_season_ratings
            ON player_season_ratings.player_id =
                players.id

            AND player_season_ratings.season =
                %s

        WHERE
            squads.team_id = %s

            AND squads.season = %s

            AND (

                COALESCE(
                    selection_totals.matchday_selections,
                    0
                ) > 0

                OR

                players.is_injured = TRUE
            )

        ORDER BY
            squads.shirt_number
            NULLS LAST,

            players.name;
        """,
        (
            team_id,
            league_id,
            season,

            team_id,
            league_id,
            season,

            season,

            team_id,
            season,
        ),
    )

    squad_rows = cursor.fetchall()

    squad = [
        {
            "player": {
                "id": squad_row[0],
                "name": squad_row[1],
                "photoUrl": squad_row[2],
                "nationality": squad_row[3],
                "birthDate": squad_row[4],
            },

            "shirtNumber":
                squad_row[5],

            "position":
                squad_row[6],

            "injured":
                bool(squad_row[7]),

            "matchdaySelections":
                int(
                    squad_row[8]
                    or 0
                ),

            "starts":
                int(
                    squad_row[9]
                    or 0
                ),

            "appearances":
                int(
                    squad_row[10]
                    or 0
                ),

            "minutes":
                int(
                    squad_row[11]
                    or 0
                ),

            "goals":
                int(
                    squad_row[12]
                    or 0
                ),

            "assists":
                int(
                    squad_row[13]
                    or 0
                ),

            "futbudRating": (
                float(
                    squad_row[14]
                )
                if squad_row[14] is not None
                else None
            ),
        }

        for squad_row
        in squad_rows
    ]

    # ============================================
    # TEAM MATCH STATISTICS
    # ============================================

    cursor.execute(
        """
        SELECT
            COUNT(*),

            AVG(
                team_match_stats.possession
            ),

            COALESCE(
                SUM(
                    team_match_stats.total_shots
                ),
                0
            ),

            COALESCE(
                SUM(
                    team_match_stats.shots_on_goal
                ),
                0
            ),

            COALESCE(
                SUM(
                    team_match_stats.shots_off_goal
                ),
                0
            ),

            COALESCE(
                SUM(
                    team_match_stats.blocked_shots
                ),
                0
            ),

            COALESCE(
                SUM(
                    team_match_stats.shots_inside_box
                ),
                0
            ),

            COALESCE(
                SUM(
                    team_match_stats.shots_outside_box
                ),
                0
            ),

            COALESCE(
                SUM(
                    team_match_stats.corner_kicks
                ),
                0
            ),

            COALESCE(
                SUM(
                    team_match_stats.offsides
                ),
                0
            ),

            COALESCE(
                SUM(
                    team_match_stats.total_passes
                ),
                0
            ),

            COALESCE(
                SUM(
                    team_match_stats.accurate_passes
                ),
                0
            ),

            COALESCE(
                SUM(
                    team_match_stats.fouls
                ),
                0
            ),

            COALESCE(
                SUM(
                    team_match_stats.yellow_cards
                ),
                0
            ),

            COALESCE(
                SUM(
                    team_match_stats.red_cards
                ),
                0
            ),

            COALESCE(
                SUM(
                    team_match_stats.goalkeeper_saves
                ),
                0
            )

        FROM team_match_stats

        JOIN matches
            ON matches.id =
               team_match_stats.match_id

        WHERE
            team_match_stats.team_id =
                %s

            AND matches.league_id =
                %s

            AND matches.season =
                %s;
        """,
        (
            team_id,
            league_id,
            season,
        ),
    )

    stat_row = cursor.fetchone()

    games_with_stats = int(stat_row[0] or 0)

    def integer(
        index
    ):
        return int(
            stat_row[index]
            or 0
        )

    def per_game(
        value
    ):

        if games_with_stats == 0:
            return 0

        return round(
            value /
            games_with_stats,
            1,
        )

    possession = round(
        float(
            stat_row[1]
            or 0
        ),
        1,
    )

    total_shots = integer(2)

    shots_on_goal = integer(3)

    shots_off_goal = integer(4)

    blocked_shots = integer(5)

    shots_inside = integer(6)

    shots_outside = integer(7)

    corners = integer(8)

    offsides = integer(9)

    total_passes = integer(10)

    accurate_passes = integer(11)

    fouls = integer(12)

    yellows = integer(13)

    reds = integer(14)

    saves = integer(15)

    pass_accuracy = (
        round(
            (
                accurate_passes
                /
                total_passes
            )
            * 100,
            1,
        )

        if total_passes > 0

        else 0
    )

    clean_sheets = 0

    for match in completed:

        if (
            match["homeAway"] == "H"
            and
            match["awayGoals"] == 0
        ):
            clean_sheets += 1

        elif (
            match["homeAway"] == "A"
            and
            match["homeGoals"] == 0
        ):
            clean_sheets += 1

    goals_for = (
        standing["goalsFor"]
        if standing
        else 0
    )

    goals_against = (
        standing["goalsAgainst"]
        if standing
        else 0
    )

    stats = {
        "games":
            games_with_stats,

        "attacking": {
            "goals":
                goals_for,

            "goalsPerGame":
                per_game(
                    goals_for
                ),

            "shots":
                total_shots,

            "shotsPerGame":
                per_game(
                    total_shots
                ),

            "shotsOnTarget":
                shots_on_goal,

            "shotsOnTargetPerGame":
                per_game(
                    shots_on_goal
                ),

            "shotsOffTarget":
                shots_off_goal,

            "blockedShots":
                blocked_shots,

            "shotsInsideBox":
                shots_inside,

            "shotsOutsideBox":
                shots_outside,

            "corners":
                corners,

            "offsides":
                offsides,
        },

        "passing": {
            "possession":
                possession,

            "passes":
                total_passes,

            "passesPerGame":
                per_game(
                    total_passes
                ),

            "accuratePasses":
                accurate_passes,

            "passAccuracy":
                pass_accuracy,
        },

        "defending": {
            "goalsAgainst":
                goals_against,

            "goalsAgainstPerGame":
                per_game(
                    goals_against
                ),

            "cleanSheets":
                clean_sheets,

            "goalkeeperSaves":
                saves,

            "savesPerGame":
                per_game(
                    saves
                ),
        },

        "discipline": {
            "fouls":
                fouls,

            "foulsPerGame":
                per_game(
                    fouls
                ),

            "yellowCards":
                yellows,

            "redCards":
                reds,
        },

        "contributors": {
            "goals":
                goals_leaders,

            "assists":
                assist_leaders,

            "keyPasses":
                key_pass_leaders,
        },
    }

    cursor.close()
    connection.close()

    return {
        "team":
            team,

        "overview": {
            "standing":
                standing,

            "nextMatch":
                next_match,

            "recentResults":
                recent_results,

            "leagueContext":
                league_context,

            "leaders": {
                "goals":
                    goals_leaders[0]
                    if goals_leaders
                    else None,

                "assists":
                    assist_leaders[0]
                    if assist_leaders
                    else None,

                "keyPasses":
                    key_pass_leaders[0]
                    if key_pass_leaders
                    else None,
            },
        },

        "squad":
            squad,

        "results": {
            "matches":
                all_matches,

            "record": {
                "played":
                    (
                        standing["played"]
                        if standing
                        else len(completed)
                    ),

                "wins":
                    (
                        standing["wins"]
                        if standing
                        else 0
                    ),

                "draws":
                    (
                        standing["draws"]
                        if standing
                        else 0
                    ),

                "losses":
                    (
                        standing["losses"]
                        if standing
                        else 0
                    ),

                "goalsFor":
                    goals_for,

                "goalsAgainst":
                    goals_against,
            },
        },

        "stats":
            stats,
    }

@app.get("/teams/{team_id}")
def get_team(team_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            teams.id,
            teams.name,
            teams.code,
            teams.country,
            teams.founded,
            teams.logo_url,

            teams.venue_id,
            teams.venue_name,
            teams.venue_city,
            teams.venue_capacity,
            teams.venue_image_url,

            leagues.id,
            leagues.name,
            team_league_seasons.season

        FROM teams

        LEFT JOIN team_league_seasons
            ON teams.id = team_league_seasons.team_id

        LEFT JOIN leagues
            ON team_league_seasons.league_id = leagues.id

        WHERE teams.id = %s

        ORDER BY team_league_seasons.season DESC

        LIMIT 1;
        """,
        (team_id,),
    )

    row = cursor.fetchone()

    cursor.close()
    connection.close()

    if row is None:
        return {
            "error": "Team not found"
        }

    return {
        "id": row[0],
        "name": row[1],
        "code": row[2],
        "country": row[3],
        "founded": row[4],
        "logoUrl": row[5],

        "venue": {
            "id": row[6],
            "name": row[7],
            "city": row[8],
            "capacity": row[9],
            "imageUrl": row[10],
        },

        "league": {
            "id": row[11],
            "name": row[12],
            "season": row[13],
        },
    }

@app.get("/teams/{team_id}/squad")
def get_team_squad(
    team_id: int,
    season: int = 2026
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            players.id,
            players.name,
            players.firstname,
            players.lastname,
            players.nationality,
            players.photo_url,
            squads.shirt_number,
            squads.position
        FROM squads
        JOIN players
            ON players.id = squads.player_id
        WHERE squads.team_id = %s
          AND squads.season = %s
        ORDER BY
            squads.position,
            squads.shirt_number NULLS LAST,
            players.name;
        """,
        (
            team_id,
            season,
        ),
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    players = []

    for row in rows:
        players.append(
            {
                "id": row[0],
                "name": row[1],
                "firstname": row[2],
                "lastname": row[3],
                "nationality": row[4],
                "photoUrl": row[5],
                "shirtNumber": row[6],
                "position": row[7],
            }
        )

    return players

@app.get("/standings")
def get_standings(
    league_id: int = 39,
    season: int = 2026
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            standings.rank,

            teams.id,
            teams.name,
            teams.code,
            teams.logo_url,

            standings.played,
            standings.wins,
            standings.draws,
            standings.losses,

            standings.goals_for,
            standings.goals_against,
            standings.goals_difference,

            standings.points,
            standings.form,
            standings.status,
            standings.description

        FROM standings

        JOIN teams
            ON teams.id =
               standings.team_id

        WHERE standings.league_id = %s
          AND standings.season = %s

        ORDER BY standings.rank;
        """,
        (
            league_id,
            season,
        ),
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    standings_list = []

    for row in rows:

        standings_list.append({
            "rank": row[0],

            "team": {
                "id": row[1],
                "name": row[2],
                "code": row[3],
                "logoUrl": row[4],
            },

            "played": row[5],
            "wins": row[6],
            "draws": row[7],
            "losses": row[8],

            "goalsFor": row[9],
            "goalsAgainst": row[10],
            "goalDifference": row[11],

            "points": row[12],
            "form": row[13],
            "status": row[14],
            "description": row[15],
        })

    return standings_list

@app.get("/leagues/{league_id}")
def get_league(
    league_id: int,
    season: int = 2026
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            leagues.id,
            leagues.name,
            leagues.country,
            leagues.type,
            leagues.logo_url,
            leagues.country_flag_url

        FROM leagues

        JOIN league_seasons
            ON leagues.id =
               league_seasons.league_id

        WHERE leagues.id = %s
          AND league_seasons.season = %s;
        """,
        (
            league_id,
            season,
        ),
    )

    row = cursor.fetchone()

    cursor.close()
    connection.close()

    if row is None:
        return {
            "error": "League not found"
        }

    return {
        "id": row[0],
        "name": row[1],
        "country": row[2],
        "type": row[3],
        "logoUrl": row[4],
        "flagUrl": row[5],
    }

@app.get("/leagues/{league_id}/matchweek")
def get_current_matchweek(
    league_id: int,
    season: int = 2026
):
    connection = get_connection()
    cursor = connection.cursor()

    # Find the earliest round that still
    # contains an unfinished match.
    cursor.execute(
        """
        SELECT
            round,
            MIN(match_date) AS first_match

        FROM matches

        WHERE league_id = %s
          AND season = %s
          AND round IS NOT NULL

        GROUP BY round

        HAVING BOOL_AND(
            status_short IN (
                'FT',
                'AET',
                'PEN'
            )
        ) = FALSE

        ORDER BY first_match

        LIMIT 1;
        """,
        (
            league_id,
            season,
        ),
    )

    round_row = cursor.fetchone()

    # Season completely finished:
    # return the most recent round instead.
    if round_row is None:

        cursor.execute(
            """
            SELECT
                round,
                MIN(match_date)

            FROM matches

            WHERE league_id = %s
              AND season = %s
              AND round IS NOT NULL

            GROUP BY round

            ORDER BY
                MIN(match_date) DESC

            LIMIT 1;
            """,
            (
                league_id,
                season,
            ),
        )

        round_row = cursor.fetchone()

    if round_row is None:

        cursor.close()
        connection.close()

        return {
            "round": None,
            "matches": [],
        }

    current_round = round_row[0]

    cursor.execute(
        """
        SELECT
            matches.id,
            matches.match_date,

            matches.status_long,
            matches.status_short,
            matches.elapsed,

            matches.home_goals,
            matches.away_goals,

            home.id,
            home.name,
            home.code,
            home.logo_url,

            away.id,
            away.name,
            away.code,
            away.logo_url

        FROM matches

        JOIN teams AS home
            ON home.id =
               matches.home_team_id

        JOIN teams AS away
            ON away.id =
               matches.away_team_id

        WHERE matches.league_id = %s
          AND matches.season = %s
          AND matches.round = %s

        ORDER BY matches.match_date;
        """,
        (
            league_id,
            season,
            current_round,
        ),
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    match_list = []

    for row in rows:

        match_list.append({
            "id": row[0],
            "date": row[1],

            "status": {
                "long": row[2],
                "short": row[3],
                "elapsed": row[4],
            },

            "score": {
                "home": row[5],
                "away": row[6],
            },

            "homeTeam": {
                "id": row[7],
                "name": row[8],
                "code": row[9],
                "logoUrl": row[10],
            },

            "awayTeam": {
                "id": row[11],
                "name": row[12],
                "code": row[13],
                "logoUrl": row[14],
            },
        })

    return {
        "round": current_round,
        "matches": match_list,
    }

@app.get("/leagues/{league_id}/leaders")
def get_league_leaders(
    league_id: int,
    season: int = 2026,
    limit: int = 5
):
    connection = get_connection()
    cursor = connection.cursor()

    goals = get_stat_leaders(
        cursor,
        "goals",
        season,
        limit,
        league_id,
    )

    assists = get_stat_leaders(
        cursor,
        "assists",
        season,
        limit,
        league_id,
    )

    key_passes = get_stat_leaders(
        cursor,
        "key_passes",
        season,
        limit,
        league_id,
    )

    cursor.close()
    connection.close()

    return {
        "goals": goals,
        "assists": assists,
        "keyPasses": key_passes,
    }

@app.get("/leagues")
def get_leagues(
    season: int = 2026
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            leagues.id,
            leagues.name,
            leagues.country,
            leagues.type,
            leagues.logo_url,
            leagues.country_flag_url

        FROM leagues

        JOIN league_seasons
            ON leagues.id =
               league_seasons.league_id

        WHERE league_seasons.season = %s

        ORDER BY leagues.name;
        """,
        (season,),
    )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    leagues_list = []

    for row in rows:
        leagues_list.append({
            "id": row[0],
            "name": row[1],
            "country": row[2],
            "type": row[3],
            "logoUrl": row[4],
            "flagUrl": row[5],
        })

    return leagues_list

@app.get("/players/{player_id}/dashboard")
def get_player_dashboard(
    player_id: int,
    season: int = 2026,
):
    connection = get_connection()
    cursor = connection.cursor()

    def number(value):
        return int(value or 0)

    def decimal_number(value):
        return float(value or 0)

    # ==================================================
    # PLAYER
    # ==================================================

    cursor.execute(
        """
        SELECT
            id,
            name,
            firstname,
            lastname,
            birth_date,
            nationality,
            height,
            weight,
            primary_position,
            photo_url

        FROM players

        WHERE id = %s;
        """,
        (player_id,),
    )

    player_row = cursor.fetchone()

    if player_row is None:
        cursor.close()
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Player not found",
        )

    # ==================================================
    # CURRENT TEAM + LEAGUE
    #
    # We determine this from the player's squad,
    # not from a league supplied by the frontend.
    # ==================================================

    cursor.execute(
        """
        SELECT
            teams.id,
            teams.name,
            teams.logo_url,

            squads.shirt_number,

            COALESCE(
                squads.position,
                players.primary_position
            ),

            leagues.id,
            leagues.name,
            leagues.logo_url

        FROM squads

        JOIN players
            ON players.id =
               squads.player_id

        JOIN teams
            ON teams.id =
               squads.team_id

        JOIN team_league_seasons
            ON team_league_seasons.team_id =
               squads.team_id

            AND team_league_seasons.season =
                squads.season

        JOIN leagues
            ON leagues.id =
               team_league_seasons.league_id

        WHERE squads.player_id = %s
          AND squads.season = %s
          AND team_league_seasons.season = %s

        LIMIT 1;
        """,
        (
            player_id,
            season,
            season,
        ),
    )

    context_row = cursor.fetchone()

    if context_row is None:
        cursor.close()
        connection.close()

        raise HTTPException(
            status_code=404,
            detail=(
                "Player has no current team "
                "or league for this season"
            ),
        )

    team_id = context_row[0]
    league_id = context_row[5]

    profile = {
        "id": player_row[0],
        "name": player_row[1],
        "firstname": player_row[2],
        "lastname": player_row[3],
        "birthDate": player_row[4],
        "nationality": player_row[5],
        "height": player_row[6],
        "weight": player_row[7],
        "primaryPosition": player_row[8],
        "photoUrl": player_row[9],

        "shirtNumber": context_row[3],
        "position": context_row[4],

        "team": {
            "id": context_row[0],
            "name": context_row[1],
            "logoUrl": context_row[2],
        },

        "league": {
            "id": context_row[5],
            "name": context_row[6],
            "logoUrl": context_row[7],
        },

        "season": season,
    }

    # ==================================================
    # SEASON TOTALS
    #
    # IMPORTANT:
    # league_id was discovered above.
    # It is NOT hardcoded to 39.
    # ==================================================

    cursor.execute(
        """
        SELECT

            COUNT(*) FILTER (
                WHERE COALESCE(
                    player_match_stats.minutes,
                    0
                ) > 0
            ),

            COALESCE(
                SUM(player_match_stats.minutes),
                0
            ),

            COALESCE(
                SUM(player_match_stats.goals),
                0
            ),

            COALESCE(
                SUM(player_match_stats.assists),
                0
            ),

            ROUND(
                COALESCE(
                    AVG(
                        player_match_stats.provider_rating
                    )
                    FILTER (
                        WHERE
                            player_match_stats.provider_rating
                            IS NOT NULL
                    ),
                    0
                ),
                2
            ),

            COALESCE(
                SUM(player_match_stats.shots_total),
                0
            ),

            COALESCE(
                SUM(player_match_stats.shots_on_target),
                0
            ),

            COALESCE(
                SUM(player_match_stats.key_passes),
                0
            ),

            COALESCE(
                SUM(player_match_stats.offsides),
                0
            ),

            COALESCE(
                SUM(player_match_stats.penalties_scored),
                0
            ),

            COALESCE(
                SUM(player_match_stats.penalties_missed),
                0
            ),

            COALESCE(
                SUM(player_match_stats.passes_total),
                0
            ),

            COALESCE(
                ROUND(
                    (
                        SUM(
                            CASE
                                WHEN
                                    player_match_stats.pass_accuracy
                                    IS NOT NULL
                                THEN
                                    COALESCE(
                                        player_match_stats.passes_total,
                                        0
                                    )
                                    *
                                    player_match_stats.pass_accuracy

                                ELSE 0
                            END
                        )::NUMERIC

                        /

                        NULLIF(
                            SUM(
                                CASE
                                    WHEN
                                        player_match_stats.pass_accuracy
                                        IS NOT NULL
                                    THEN
                                        COALESCE(
                                            player_match_stats.passes_total,
                                            0
                                        )

                                    ELSE 0
                                END
                            ),
                            0
                        )
                    ),
                    1
                ),
                0
            ),

            COALESCE(
                SUM(
                    player_match_stats.dribbles_attempted
                ),
                0
            ),

            COALESCE(
                SUM(
                    player_match_stats.dribbles_successful
                ),
                0
            ),

            COALESCE(
                SUM(player_match_stats.dribbled_past),
                0
            ),

            COALESCE(
                SUM(player_match_stats.tackles),
                0
            ),

            COALESCE(
                SUM(player_match_stats.interceptions),
                0
            ),

            COALESCE(
                SUM(player_match_stats.blocks),
                0
            ),

            COALESCE(
                SUM(player_match_stats.duels_total),
                0
            ),

            COALESCE(
                SUM(player_match_stats.duels_won),
                0
            ),

            COALESCE(
                SUM(player_match_stats.fouls_drawn),
                0
            ),

            COALESCE(
                SUM(player_match_stats.fouls_committed),
                0
            ),

            COALESCE(
                SUM(player_match_stats.yellow_cards),
                0
            ),

            COALESCE(
                SUM(player_match_stats.red_cards),
                0
            ),

            COALESCE(
                SUM(player_match_stats.saves),
                0
            ),

            COALESCE(
                SUM(player_match_stats.goals_conceded),
                0
            ),

            COALESCE(
                SUM(player_match_stats.penalties_saved),
                0
            )

        FROM player_match_stats

        JOIN matches
            ON matches.id =
               player_match_stats.match_id

        WHERE player_match_stats.player_id = %s
          AND matches.league_id = %s
          AND matches.season = %s;
        """,
        (
            player_id,
            league_id,
            season,
        ),
    )

    stats = cursor.fetchone()

    appearances = number(stats[0])
    minutes = number(stats[1])

    goals = number(stats[2])
    assists = number(stats[3])

    avg_rating = decimal_number(
        stats[4]
    )

    shots = number(stats[5])
    shots_on_target = number(stats[6])

    key_passes = number(stats[7])

    offsides = number(stats[8])

    penalties_scored = number(
        stats[9]
    )

    penalties_missed = number(
        stats[10]
    )

    passes_total = number(
        stats[11]
    )

    pass_accuracy = decimal_number(
        stats[12]
    )

    dribbles_attempted = number(
        stats[13]
    )

    dribbles_successful = number(
        stats[14]
    )

    dribbled_past = number(
        stats[15]
    )

    tackles = number(
        stats[16]
    )

    interceptions = number(
        stats[17]
    )

    blocks = number(
        stats[18]
    )

    duels_total = number(
        stats[19]
    )

    duels_won = number(
        stats[20]
    )

    fouls_drawn = number(
        stats[21]
    )

    fouls_committed = number(
        stats[22]
    )

    yellow_cards = number(
        stats[23]
    )

    red_cards = number(
        stats[24]
    )

    saves = number(
        stats[25]
    )

    goals_conceded = number(
        stats[26]
    )

    penalties_saved = number(
        stats[27]
    )

    dribble_success_rate = (
        round(
            (
                dribbles_successful
                /
                dribbles_attempted
            )
            * 100,
            1,
        )
        if dribbles_attempted > 0
        else 0
    )

    duel_win_rate = (
        round(
            (
                duels_won
                /
                duels_total
            )
            * 100,
            1,
        )
        if duels_total > 0
        else 0
    )

    summary = {
        "appearances": appearances,
        "minutes": minutes,

        "goals": goals,
        "assists": assists,

        "avgRating": avg_rating,

        "shots": shots,
        "shotsOnTarget": shots_on_target,

        "keyPasses": key_passes,
    }

    detailed = {

        "attacking": {
            "goals": goals,
            "assists": assists,

            "shots": shots,
            "shotsOnTarget": shots_on_target,

            "offsides": offsides,

            "penaltiesScored":
                penalties_scored,

            "penaltiesMissed":
                penalties_missed,
        },

        "passing": {
            "passes": passes_total,

            "passAccuracy":
                pass_accuracy,

            "keyPasses":
                key_passes,
        },

        "dribbling": {
            "attempted":
                dribbles_attempted,

            "successful":
                dribbles_successful,

            "successRate":
                dribble_success_rate,

            "dribbledPast":
                dribbled_past,
        },

        "defending": {
            "tackles": tackles,

            "interceptions":
                interceptions,

            "blocks": blocks,

            "duels":
                duels_total,

            "duelsWon":
                duels_won,

            "duelWinRate":
                duel_win_rate,
        },

        "discipline": {
            "foulsDrawn":
                fouls_drawn,

            "foulsCommitted":
                fouls_committed,

            "yellowCards":
                yellow_cards,

            "redCards":
                red_cards,
        },

        "goalkeeping": {
            "saves": saves,

            "goalsConceded":
                goals_conceded,

            "penaltiesSaved":
                penalties_saved,
        },
    }

    # ==================================================
    # LAST 10 APPEARANCES IN THAT PLAYER'S LEAGUE
    # ==================================================

    cursor.execute(
        """
        SELECT
            matches.id,
            matches.match_date,

            player_match_stats.minutes,
            player_match_stats.goals,
            player_match_stats.assists,

            player_match_stats.shots_total,
            player_match_stats.shots_on_target,
            player_match_stats.key_passes,

            player_match_stats.provider_rating,

            player_match_stats.team_id,

            matches.home_team_id,
            matches.away_team_id,

            matches.home_goals,
            matches.away_goals,

            home_team.id,
            home_team.name,
            home_team.logo_url,

            away_team.id,
            away_team.name,
            away_team.logo_url,

            matches.status_short

        FROM player_match_stats

        JOIN matches
            ON matches.id =
               player_match_stats.match_id

        JOIN teams AS home_team
            ON home_team.id =
               matches.home_team_id

        JOIN teams AS away_team
            ON away_team.id =
               matches.away_team_id

        WHERE player_match_stats.player_id = %s
          AND matches.league_id = %s
          AND matches.season = %s

          AND COALESCE(
              player_match_stats.minutes,
              0
          ) > 0

        ORDER BY
            matches.match_date DESC

        LIMIT 10;
        """,
        (
            player_id,
            league_id,
            season,
        ),
    )

    rows = cursor.fetchall()

    recent_matches = []

    for row in rows:

        player_team_id = row[9]

        home_team_id = row[10]

        home_goals = row[12]
        away_goals = row[13]

        if (
            player_team_id
            ==
            home_team_id
        ):

            opponent = {
                "id": row[17],
                "name": row[18],
                "logoUrl": row[19],
            }

            team_goals = home_goals

            opponent_goals = (
                away_goals
            )

        else:

            opponent = {
                "id": row[14],
                "name": row[15],
                "logoUrl": row[16],
            }

            team_goals = away_goals

            opponent_goals = (
                home_goals
            )

        result = None

        if (
            team_goals is not None
            and
            opponent_goals is not None
        ):

            if (
                team_goals
                >
                opponent_goals
            ):
                result_letter = "W"

            elif (
                team_goals
                <
                opponent_goals
            ):
                result_letter = "L"

            else:
                result_letter = "D"

            result = (
                f"{result_letter} "
                f"{team_goals}-"
                f"{opponent_goals}"
            )

        recent_matches.append({
            "id": row[0],
            "date": row[1],

            "minutes":
                number(row[2]),

            "goals":
                number(row[3]),

            "assists":
                number(row[4]),

            "shots":
                number(row[5]),

            "shotsOnTarget":
                number(row[6]),

            "keyPasses":
                number(row[7]),

            "rating": (
                decimal_number(
                    row[8]
                )
                if row[8] is not None
                else None
            ),

            "opponent":
                opponent,

            "result":
                result,

            "status":
                row[20],
        })

        # ==================================================
    # FUTBUD RATING
    # ==================================================

    cursor.execute(
        """
        SELECT
            reference_season,

            position,

            orientation,
            orientation_cluster,

            archetype_cluster,
            archetype_key,
            archetype_name,

            minutes,
            appearances,
            starts,

            raw_quality_rating,
            minutes_reliability,

            futbud_rating,
            role_rating_percentile,

            quality_status,
            quality_metric_count,

            updated_at

        FROM player_season_ratings

        WHERE player_id = %s
          AND season = %s;
        """,
        (
            player_id,
            season,
        ),
    )

    rating_row = cursor.fetchone()


    futbud = None


    if rating_row is not None:

        # ==============================================
        # INDIVIDUAL RATING METRICS
        # ==============================================

        cursor.execute(
            """
            SELECT
                feature,
                raw_value,
                historical_percentile,
                weight,
                reference_players

            FROM player_season_rating_metrics

            WHERE player_id = %s
              AND season = %s

            ORDER BY
                weight DESC,
                feature;
            """,
            (
                player_id,
                season,
            ),
        )

        metric_rows = cursor.fetchall()


        metrics = [
            {
                "feature":
                    row[0],

                "value": (
                    float(row[1])
                    if row[1] is not None
                    else None
                ),

                "percentile": (
                    float(row[2])
                    if row[2] is not None
                    else None
                ),

                "weight": (
                    float(row[3])
                    if row[3] is not None
                    else None
                ),

                "referencePlayers":
                    row[4],
            }

            for row in metric_rows
        ]


        futbud = {

            "season":
                season,

            "referenceSeason":
                rating_row[0],

            "position":
                rating_row[1],

            "orientation":
                rating_row[2],

            "orientationCluster":
                rating_row[3],

            "archetypeCluster":
                rating_row[4],

            "archetypeKey":
                rating_row[5],

            "archetype":
                rating_row[6],

            "minutes":
                rating_row[7],

            "appearances":
                rating_row[8],

            "starts":
                rating_row[9],

            "rawRating": (
                float(rating_row[10])
                if rating_row[10] is not None
                else None
            ),

            "minutesReliability": (
                float(rating_row[11])
                if rating_row[11] is not None
                else None
            ),

            "rating": (
                float(rating_row[12])
                if rating_row[12] is not None
                else None
            ),

            "percentile": (
                float(rating_row[13])
                if rating_row[13] is not None
                else None
            ),

            "status":
                rating_row[14],

            "metricCount":
                rating_row[15],

            "updatedAt":
                rating_row[16],

            "metrics":
                metrics,
        }

    cursor.close()
    connection.close()

    return {
        "profile": profile,
        "summary": summary,
        "detailed": detailed,

        "futbud": futbud,

        "recentMatches":
            recent_matches,
    }

# ==================================================
# FUTBUD PLAYER RANKINGS
# ==================================================

@app.get("/rankings/players")
def get_player_rankings(
    season: int = 2026,
    limit: int = 100,
):

    limit = max(
        1,
        min(
            limit,
            500,
        ),
    )

    connection = get_connection()
    cursor = connection.cursor(
        row_factory=dict_row
    )

    try:

        base_select = """
            SELECT
                psr.player_id,
                p.name AS player_name,
                p.photo_url AS player_photo_url,

                psr.position,
                psr.archetype_key,
                psr.archetype_name,

                psr.futbud_rating,
                psr.role_rating_percentile,
                psr.quality_status,

                psr.minutes,
                psr.appearances,
                psr.starts,

                t.id AS team_id,
                t.name AS team_name,
                t.logo_url AS team_logo_url,

                l.id AS league_id,
                l.name AS league_name,
                l.logo_url AS league_logo_url

            FROM player_season_ratings psr

            JOIN players p
                ON p.id = psr.player_id

            LEFT JOIN teams t
                ON t.id = psr.latest_team_id

            LEFT JOIN leagues l
                ON l.id = psr.primary_league_id
        """

        def player_from_row(
            row,
            rank: int | None = None,
        ):

            return {
                "rank": rank,

                "id":
                    row["player_id"],

                "name":
                    row["player_name"],

                "photoUrl":
                    row["player_photo_url"],

                "position":
                    row["position"],

                "archetypeKey":
                    row["archetype_key"],

                "archetype":
                    row["archetype_name"],

                "rating": (
                    float(
                        row["futbud_rating"]
                    )
                    if row["futbud_rating"]
                    is not None
                    else None
                ),

                "percentile": (
                    float(
                        row[
                            "role_rating_percentile"
                        ]
                    )
                    if row[
                        "role_rating_percentile"
                    ] is not None
                    else None
                ),

                "status":
                    row["quality_status"],

                "minutes":
                    row["minutes"],

                "appearances":
                    row["appearances"],

                "starts":
                    row["starts"],

                "team": (
                    {
                        "id":
                            row["team_id"],

                        "name":
                            row["team_name"],

                        "logoUrl":
                            row[
                                "team_logo_url"
                            ],
                    }
                    if row["team_id"]
                    is not None
                    else None
                ),

                "league": (
                    {
                        "id":
                            row["league_id"],

                        "name":
                            row["league_name"],

                        "logoUrl":
                            row[
                                "league_logo_url"
                            ],
                    }
                    if row["league_id"]
                    is not None
                    else None
                ),
            }


        # ==========================================
        # OVERALL
        # ==========================================

        cursor.execute(
            base_select
            + """
            WHERE
                psr.season = %s
                AND psr.futbud_rating
                    IS NOT NULL

            ORDER BY
                psr.futbud_rating DESC,
                psr.role_rating_percentile DESC,
                p.name

            LIMIT %s;
            """,
            (
                season,
                limit,
            ),
        )

        overall_rows = cursor.fetchall()

        overall = [
            player_from_row(
                row,
                index + 1,
            )
            for index, row
            in enumerate(overall_rows)
        ]


        # ==========================================
        # TOP BY POSITION
        # ==========================================

        position_groups = {
            "forwards": "F",
            "midfielders": "M",
            "defenders": "D",
        }

        by_position = {}

        for (
            group_name,
            position_code,
        ) in position_groups.items():

            cursor.execute(
                base_select
                + """
                WHERE
                    psr.season = %s
                    AND psr.position = %s
                    AND psr.futbud_rating
                        IS NOT NULL

                ORDER BY
                    psr.futbud_rating DESC,
                    psr.role_rating_percentile DESC,
                    p.name

                LIMIT 5;
                """,
                (
                    season,
                    position_code,
                ),
            )

            position_rows = (
                cursor.fetchall()
            )

            by_position[
                group_name
            ] = [
                player_from_row(
                    row,
                    index + 1,
                )
                for index, row
                in enumerate(
                    position_rows
                )
            ]


        return {
            "season": season,
            "minimumMinutes": 180,
            "overall": overall,
            "byPosition": by_position,
        }

    finally:

        cursor.close()
        connection.close()


# ==========================================================
# GLOBAL SEARCH
# players + teams
# ==========================================================

@app.get("/search")
def global_search(
    q: str = "",
    season: int = 2026,
    limit: int = 6,
):
    query = q.strip()

    if len(query) < 2:
        return {
            "query": query,
            "players": [],
            "teams": [],
        }

    safe_limit = max(
        1,
        min(limit, 10),
    )

    contains_pattern = (
        f"%{query}%"
    )

    prefix_pattern = (
        f"{query}%"
    )

    connection = get_connection()

    cursor = connection.cursor(
        row_factory=dict_row
    )

    try:

        # ==============================================
        # PLAYERS
        # ==============================================

        cursor.execute(
            """
            SELECT
                p.id,
                p.name,
                p.photo_url,
                p.nationality,
                p.primary_position,

                latest_team.team_id,
                latest_team.team_name,
                latest_team.team_logo_url,

                psr.futbud_rating

            FROM players p

            LEFT JOIN LATERAL (

                SELECT
                    t.id
                        AS team_id,

                    t.name
                        AS team_name,

                    t.logo_url
                        AS team_logo_url

                FROM player_match_stats pms

                JOIN matches m
                    ON m.id =
                       pms.match_id

                JOIN teams t
                    ON t.id =
                       pms.team_id

                WHERE
                    pms.player_id = p.id

                ORDER BY
                    CASE
                        WHEN m.season = %s
                        THEN 0
                        ELSE 1
                    END,

                    m.match_date DESC

                LIMIT 1

            ) AS latest_team
                ON TRUE

            LEFT JOIN player_season_ratings psr
                ON psr.player_id = p.id

                AND psr.season = %s

            WHERE
                p.name ILIKE %s

            ORDER BY
                CASE
                    WHEN p.name ILIKE %s
                    THEN 0
                    ELSE 1
                END,

                p.name

            LIMIT %s;
            """,
            (
                season,
                season,
                contains_pattern,
                prefix_pattern,
                safe_limit,
            ),
        )

        player_rows = cursor.fetchall()

        players = [
            {
                "id": row["id"],
                "name": row["name"],
                "photoUrl": row["photo_url"],
                "nationality": row["nationality"],
                "position": row["primary_position"],
                "futbudRating": (
                    float(
                        row["futbud_rating"]
                    )
                    if row["futbud_rating"]
                    is not None
                    else None
                ),
                "team": (
                    {
                        "id": row["team_id"],
                        "name": row["team_name"],
                        "logoUrl": row[
                            "team_logo_url"
                        ],
                    }
                    if row["team_id"]
                    is not None
                    else None
                ),
            }
            for row in player_rows
        ]


        # ==============================================
        # TEAMS
        # ==============================================

        cursor.execute(
            """
            SELECT
                t.id,
                t.name,
                t.code,
                t.country,
                t.logo_url,

                latest_league.league_id,
                latest_league.league_name,
                latest_league.league_logo_url

            FROM teams t

            LEFT JOIN LATERAL (

                SELECT
                    l.id
                        AS league_id,

                    l.name
                        AS league_name,

                    l.logo_url
                        AS league_logo_url

                FROM team_league_seasons tls

                JOIN leagues l
                    ON l.id =
                       tls.league_id

                WHERE
                    tls.team_id = t.id

                ORDER BY
                    CASE
                        WHEN tls.season = %s
                        THEN 0
                        ELSE 1
                    END,

                    tls.season DESC

                LIMIT 1

            ) AS latest_league
                ON TRUE

            WHERE
                t.name ILIKE %s

                OR COALESCE(
                    t.code,
                    ''
                ) ILIKE %s

            ORDER BY
                CASE
                    WHEN t.name ILIKE %s
                    THEN 0
                    WHEN COALESCE(
                        t.code,
                        ''
                    ) ILIKE %s
                    THEN 1
                    ELSE 2
                END,

                t.name

            LIMIT %s;
            """,
            (
                season,
                contains_pattern,
                contains_pattern,
                prefix_pattern,
                prefix_pattern,
                safe_limit,
            ),
        )

        team_rows = cursor.fetchall()

        teams = [
            {
                "id": row["id"],
                "name": row["name"],
                "code": row["code"],
                "country": row["country"],
                "logoUrl": row["logo_url"],
                "league": (
                    {
                        "id": row[
                            "league_id"
                        ],
                        "name": row[
                            "league_name"
                        ],
                        "logoUrl": row[
                            "league_logo_url"
                        ],
                    }
                    if row["league_id"]
                    is not None
                    else None
                ),
            }
            for row in team_rows
        ]


        return {
            "query": query,
            "players": players,
            "teams": teams,
        }

    finally:
        cursor.close()
        connection.close()
