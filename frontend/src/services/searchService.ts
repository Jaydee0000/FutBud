export interface SearchPlayerTeam {
  id: number;
  name: string;
  logoUrl: string | null;
}


export interface SearchPlayer {
  id: number;
  name: string;
  photoUrl: string | null;
  nationality: string | null;
  position: string | null;
  futbudRating: number | null;
  team: SearchPlayerTeam | null;
}


export interface SearchTeamLeague {
  id: number;
  name: string;
  logoUrl: string | null;
}


export interface SearchTeam {
  id: number;
  name: string;
  code: string | null;
  country: string | null;
  logoUrl: string | null;
  league: SearchTeamLeague | null;
}


export interface GlobalSearchResults {
  query: string;
  players: SearchPlayer[];
  teams: SearchTeam[];
}


const API =
  "http://127.0.0.1:8000";


export async function searchFutBud(
  query: string,
  options?: {
    season?: number;
    limit?: number;
    signal?: AbortSignal;
  },
): Promise<GlobalSearchResults> {

  const trimmed =
    query.trim();

  if (trimmed.length < 2) {
    return {
      query: trimmed,
      players: [],
      teams: [],
    };
  }

  const season =
    options?.season ?? 2026;

  const limit =
    options?.limit ?? 6;

  const params =
    new URLSearchParams({
      q: trimmed,
      season: String(season),
      limit: String(limit),
    });

  const response =
    await fetch(
      `${API}/search?${params.toString()}`,
      {
        signal:
          options?.signal,
      },
    );

  if (!response.ok) {
    throw new Error(
      "Failed to search FutBud"
    );
  }

  return response.json();
}
