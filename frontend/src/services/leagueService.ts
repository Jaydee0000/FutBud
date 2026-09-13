import type {
  MatchTeam,
} from "./matchService";


export interface League {
  id: number;
  name: string;
  country: string;
  type: string;
  logoUrl: string;
  flagUrl: string;
}


export interface Standing {
  rank: number;

  team: {
    id: number;
    name: string;
    code: string;
    logoUrl: string;
  };

  played: number;
  wins: number;
  draws: number;
  losses: number;

  goalsFor: number;
  goalsAgainst: number;
  goalDifference: number;

  points: number;

  form: string | null;
  description: string | null;
}


export interface MatchweekMatch {
  id: number;
  date: string;

  status: {
    long: string;
    short: string;
    elapsed: number | null;
  };

  score: {
    home: number | null;
    away: number | null;
  };

  homeTeam: MatchTeam;
  awayTeam: MatchTeam;
}


export interface Matchweek {
  round: string | null;
  matches: MatchweekMatch[];
}


export interface StatLeader {
  player: {
    id: number;
    name: string;
    photoUrl: string;
  };

  team: {
    id: number;
    name: string;
    logoUrl: string;
  } | null;

  value: number;
}


export interface LeagueLeaders {
  goals: StatLeader[];
  assists: StatLeader[];
  keyPasses: StatLeader[];
}


const API =
  "http://127.0.0.1:8000";


/*
  Used by Home.tsx to show
  all tracked leagues.
*/
export async function getLeagues(
  season = 2026
): Promise<League[]> {

  const response = await fetch(
    `${API}/leagues?season=${season}`
  );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch leagues"
    );
  }

  return response.json();
}


/*
  Single league
*/
export async function getLeague(
  leagueId: number
): Promise<League> {

  const response = await fetch(
    `${API}/leagues/${leagueId}?season=2026`
  );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch league"
    );
  }

  const data =
    await response.json();

  if (data.error) {
    throw new Error(
      data.error
    );
  }

  return data;
}


/*
  League standings
*/
export async function getStandings(
  leagueId: number
): Promise<Standing[]> {

  const response = await fetch(
    `${API}/standings?league_id=${leagueId}&season=2026`
  );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch standings"
    );
  }

  return response.json();
}


/*
  Current unfinished matchweek
*/
export async function getMatchweek(
  leagueId: number
): Promise<Matchweek> {

  const response = await fetch(
    `${API}/leagues/${leagueId}/matchweek?season=2026`
  );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch matchweek"
    );
  }

  return response.json();
}


/*
  Goals / assists / key passes
  for one league.
*/
export async function getLeagueLeaders(
  leagueId: number
): Promise<LeagueLeaders> {

  const response = await fetch(
    `${API}/leagues/${leagueId}/leaders?season=2026&limit=5`
  );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch league leaders"
    );
  }

  return response.json();
}