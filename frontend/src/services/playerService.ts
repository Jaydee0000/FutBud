export interface Player {
  id: number;
  name: string;
  position: string;
  rating: number;

  team: {
    id: number;
    name: string;
    shortName: string;
  };
}

export interface FutBudMetric {
  feature: string;
  value: number | null;
  percentile: number | null;
  weight: number | null;
  referencePlayers: number;
}

export interface FutBudRating {
  season: number;
  referenceSeason: number;

  position: string | null;

  orientation: string | null;
  orientationCluster: number | null;

  archetypeCluster: number | null;
  archetypeKey: string;
  archetype: string;

  minutes: number;
  appearances: number | null;
  starts: number | null;

  rawRating: number | null;
  minutesReliability: number | null;

  rating: number | null;
  percentile: number | null;

  status: string | null;
  metricCount: number | null;

  updatedAt: string | null;

  metrics: FutBudMetric[];
}

export interface PlayerProfile {
  id: number;
  name: string;

  firstname: string | null;
  lastname: string | null;

  birthDate: string | null;
  nationality: string | null;

  height: string | null;
  weight: string | null;

  primaryPosition: string | null;
  photoUrl: string | null;

  shirtNumber: number | null;
  position: string | null;

  team: {
    id: number;
    name: string;
    logoUrl: string | null;
  };

  league: {
    id: number;
    name: string;
    logoUrl: string | null;
  };

  season: number;
}

export interface PlayerSummary {
  appearances: number;
  minutes: number;

  goals: number;
  assists: number;

  avgRating: number;

  shots: number;
  shotsOnTarget: number;

  keyPasses: number;
}

export interface PlayerDetailedStats {
  attacking: {
    goals: number;
    assists: number;

    shots: number;
    shotsOnTarget: number;

    offsides: number;

    penaltiesScored: number;
    penaltiesMissed: number;
  };

  passing: {
    passes: number;
    passAccuracy: number;
    keyPasses: number;
  };

  dribbling: {
    attempted: number;
    successful: number;
    successRate: number;
    dribbledPast: number;
  };

  defending: {
    tackles: number;
    interceptions: number;
    blocks: number;

    duels: number;
    duelsWon: number;
    duelWinRate: number;
  };

  discipline: {
    foulsDrawn: number;
    foulsCommitted: number;

    yellowCards: number;
    redCards: number;
  };

  goalkeeping: {
    saves: number;
    goalsConceded: number;
    penaltiesSaved: number;
  };
}

export interface PlayerRecentMatch {
  id: number;
  date: string;

  minutes: number;

  goals: number;
  assists: number;

  shots: number;
  shotsOnTarget: number;

  keyPasses: number;

  rating: number | null;

  opponent: {
    id: number;
    name: string;
    logoUrl: string | null;
  };

  result: string | null;
  status: string;
}

export interface PlayerDashboard {
  profile: PlayerProfile;

  summary: PlayerSummary;

  detailed: PlayerDetailedStats;

  futbud: FutBudRating | null;

  recentMatches: PlayerRecentMatch[];
}

const API_URL = "http://127.0.0.1:8000";

export async function getPlayers(): Promise<Player[]> {
  const response = await fetch(
    `${API_URL}/players`
  );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch players"
    );
  }

  return response.json();
}

export async function getPlayerDashboard(
  playerId: number,
  season: number = 2026
): Promise<PlayerDashboard> {
  const response = await fetch(
    `${API_URL}/players/${playerId}/dashboard?season=${season}`
  );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch player dashboard"
    );
  }

  return response.json();
}