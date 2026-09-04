import psycopg

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


def get_connection():
    return psycopg.connect(
        dbname="futbud",
        user="futbud_user",
        password="Adid@s1738",
        host="localhost",
        port="5432",
    )


@app.get("/")
def home():
    return {
        "message": "FutBud API is running"
    }


@app.get("/players")
def get_players(
    team_id: int | None = None,
    season: int = 2026
):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            players.id,
            players.name,
            players.firstname,
            players.lastname,
            players.nationality,
            players.primary_position,
            players.photo_url,

            teams.id,
            teams.name,
            teams.code,
            teams.logo_url,

            squads.shirt_number,
            squads.position

        FROM players

        LEFT JOIN squads
            ON players.id = squads.player_id
            AND squads.season = %s

        LEFT JOIN teams
            ON squads.team_id = teams.id

        WHERE 1 = 1
    """

    params = [season]

    if team_id is not None:
        query += """
            AND teams.id = %s
        """

        params.append(team_id)

    query += """
        ORDER BY players.name;
    """

    cursor.execute(query, params)

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    players_list = []

    for row in rows:
        players_list.append({
            "id": row[0],
            "name": row[1],
            "firstname": row[2],
            "lastname": row[3],
            "nationality": row[4],

            "position": row[12] or row[5],
            "photoUrl": row[6],

            "shirtNumber": row[11],

            "team": (
                {
                    "id": row[7],
                    "name": row[8],
                    "shortName": row[9],
                    "logoUrl": row[10],
                }
                if row[7] is not None
                else None
            ),

            # Temporary until FutBud ratings exist
            "rating": 0,
        })

    return players_list