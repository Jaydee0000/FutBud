import psycopg
from datetime import date

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


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
    limit: int
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

            FROM player_match_stats AS latest_stats

            JOIN matches AS latest_match
                ON latest_match.id =
                   latest_stats.match_id

            JOIN teams
                ON teams.id =
                   latest_stats.team_id

            WHERE latest_stats.player_id =
                  player_totals.player_id

              AND latest_match.season = %s

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

    cursor.execute(
        query,
        (
            season,
            season,
            limit,
        ),
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
            } if row[4] is not None else None,
        })

    return leaders

@app.get("/leaders")
def get_leaders(
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
    )

    assists = get_stat_leaders(
        cursor,
        "assists",
        season,
        limit,
    )

    key_passes = get_stat_leaders(
        cursor,
        "key_passes",
        season,
        limit,
    )

    interceptions = get_stat_leaders(
        cursor,
        "interceptions",
        season,
        limit,
    )

    cursor.close()
    connection.close()

    return {
        "goals": goals,
        "assists": assists,
        "keyPasses": key_passes,
        "interceptions": interceptions,
    }


@app.get("/")
def home():
    return {
        "message": "FutBud API is running"
    }


@app.get("/players")
def get_players():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            players.id,
            players.name,
            players.position,
            players.rating,
            teams.id AS team_id,
            teams.name AS team_name,
            teams.short_name AS team_short_name
        FROM players
        JOIN teams
            ON players.team_id = teams.id
        ORDER BY players.rating DESC;
        """
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
                "position": row[2],
                "rating": float(row[3]) if row[3] is not None else None,

                "team": {
                    "id": row[4],
                    "name": row[5],
                    "shortName": row[6],
                },
            }
        )

    return players

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