import { API_URL } from "../config/api";


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


export interface ArchetypeSummary {
  key: string;
  name: string;
  shortName: string;
  position: string;
  description: string;
  playerCount: number;
}


export interface ArchetypeGroup {
  key: string;
  name: string;
  position: string;
  archetypes: ArchetypeSummary[];
}


export interface ArchetypeListResponse {
  season: number;
  groups: ArchetypeGroup[];
}


export interface ArchetypeMetricDefinition {
  key: string;
  name: string;
  weight: number | null;
}


export interface ArchetypePlayerMetric
  extends ArchetypeMetricDefinition {
  value: number | null;
  percentile: number | null;
}


export interface ArchetypeRankedPlayer {
  rank: number;
  id: number;
  name: string;
  photoUrl: string | null;
  position: string | null;
  minutes: number;
  appearances: number | null;
  starts: number | null;
  rating: number | null;
  percentile: number | null;
  status: string | null;
  team: RankingTeam | null;
  league: RankingLeague | null;
  topMetrics: ArchetypePlayerMetric[];
}


export interface ArchetypeRankingsResponse {
  season: number;
  archetype: ArchetypeSummary & {
    positionGroup: string;
    metrics: ArchetypeMetricDefinition[];
  };
  players: ArchetypeRankedPlayer[];
}


const API = API_URL;


async function rankingRequest<T>(
  url: string,
  fallbackMessage: string,
): Promise<T> {

  const response = await fetch(url);

  if (!response.ok) {
    let message = fallbackMessage;

    try {
      const data = await response.json();

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


export async function getPlayerRankings(
  season = 2026,
  limit = 25,
): Promise<PlayerRankingsResponse> {

  return rankingRequest<PlayerRankingsResponse>(
    `${API}/rankings/players?season=${season}&limit=${limit}`,
    "Failed to fetch FutBud rankings",
  );
}


export async function getArchetypes(
  season = 2026,
): Promise<ArchetypeListResponse> {

  return rankingRequest<ArchetypeListResponse>(
    `${API}/rankings/archetypes?season=${season}`,
    "Failed to fetch FutBud archetypes",
  );
}


export async function getArchetypeRankings(
  archetypeKey: string,
  season = 2026,
): Promise<ArchetypeRankingsResponse> {

  return rankingRequest<ArchetypeRankingsResponse>(
    `${API}/rankings/archetypes/${encodeURIComponent(archetypeKey)}?season=${season}`,
    "Failed to fetch archetype rankings",
  );
}


export async function getPositionGroupRankings(
  position: string,
  season = 2026,
): Promise<ArchetypeRankingsResponse> {

  return rankingRequest<ArchetypeRankingsResponse>(
    `${API}/rankings/archetypes/positions/${encodeURIComponent(position)}?season=${season}`,
    "Failed to fetch position-group rankings",
  );
}
