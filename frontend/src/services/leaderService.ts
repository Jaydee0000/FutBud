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


export interface Leaderboards {
  goals: StatLeader[];
  assists: StatLeader[];
  keyPasses: StatLeader[];
  interceptions: StatLeader[];
}


export async function getLeaders(
  season = 2026
): Promise<Leaderboards> {

  const response = await fetch(
    `${API_URL}/leaders?season=${season}&limit=5`
  );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch leaders"
    );
  }

  return response.json();
}
import { API_URL } from "../config/api";
