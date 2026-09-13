export interface RankingTeam {
  id: number;
  name: string;
  logoUrl: string | null;
}


export interface RankingLeague {
  id: number;
  name: string;
  logoUrl: string | null;
}


export interface RankedFutBudPlayer {
  rank: number | null;

  id: number;
  name: string;
  photoUrl: string | null;

  position: string | null;

  archetypeKey: string;
  archetype: string;

  rating: number | null;
  percentile: number | null;
  status: string | null;

  minutes: number;
  appearances: number | null;
  starts: number | null;

  team: RankingTeam | null;
  league: RankingLeague | null;
}


export interface PlayerRankingsResponse {
  season: number;
  minimumMinutes: number;

  overall: RankedFutBudPlayer[];

  byPosition: {
    forwards: RankedFutBudPlayer[];
    midfielders: RankedFutBudPlayer[];
    defenders: RankedFutBudPlayer[];
  };
}


const API =
  "http://127.0.0.1:8000";


export async function getPlayerRankings(
  season = 2026,
  limit = 25,
): Promise<PlayerRankingsResponse> {

  const response =
    await fetch(
      `${API}/rankings/players?season=${season}&limit=${limit}`
    );


  if (!response.ok) {

    let message =
      "Failed to fetch FutBud rankings";

    try {

      const data =
        await response.json();

      if (data.detail) {
        message = data.detail;
      }

    } catch {
      // Keep the default message.
    }

    throw new Error(message);
  }


  return response.json();
}
