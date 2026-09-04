export interface Team {
  id: number;
  name: string;
  code: string;
  country: string;
  founded: number;
  logoUrl: string;

  venue: {
    id: number;
    name: string;
    city: string;
    capacity: number;
    imageUrl: string;
  };

  league?: {
    id: number;
    name: string;
    season: number;
  };
}


export interface SquadPlayer {
  id: number;
  name: string;

  firstname?: string;
  lastname?: string;
  nationality?: string;

  photoUrl: string;

  shirtNumber?: number;
  position?: string;
}


export async function getTeams(): Promise<Team[]> {
  const response = await fetch(
    "http://127.0.0.1:8000/teams?league_id=39&season=2026"
  );

  if (!response.ok) {
    throw new Error("Failed to fetch teams");
  }

  return response.json();
}


export async function getTeam(
  teamId: number
): Promise<Team> {

  const response = await fetch(
    `http://127.0.0.1:8000/teams/${teamId}`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch team");
  }

  const data = await response.json();

  if (data.error) {
    throw new Error(data.error);
  }

  return data;
}


export async function getTeamSquad(
  teamId: number,
  season = 2026
): Promise<SquadPlayer[]> {

  const response = await fetch(
    `http://127.0.0.1:8000/teams/${teamId}/squad?season=${season}`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch team squad");
  }

  return response.json();
}