export interface PlayerDashboardTeam {
  id: number;
  name: string;
  logoUrl: string;
}


export interface PlayerDashboardLeague {
  id: number;
  name: string;
  logoUrl: string;
}


export interface PlayerDashboardProfile {
  id: number;

  name: string;

  firstname: string | null;
  lastname: string | null;

  birthDate: string | null;

  nationality: string | null;

  height: string | null;
  weight: string | null;

  primaryPosition: string | null;
  position: string | null;

  photoUrl: string | null;

  shirtNumber: number | null;

  team:
    PlayerDashboardTeam
    | null;

  league:
    PlayerDashboardLeague
    | null;

  season: number;
}


export interface PlayerSeasonSummary {
  appearances: number;

  minutes: number;

  goals: number;
  assists: number;

  avgRating: number;

  shots: number;
  shotsOnTarget: number;

  keyPasses: number;
}


export interface PlayerAttackingStats {
  goals: number;
  assists: number;

  shots: number;
  shotsOnTarget: number;

  offsides: number;

  penaltiesScored: number;
  penaltiesMissed: number;
}


export interface PlayerPassingStats {
  passes: number;

  passAccuracy: number;

  keyPasses: number;
}


export interface PlayerDribblingStats {
  attempted: number;
  successful: number;

  successRate: number;

  dribbledPast: number;
}


export interface PlayerDefendingStats {
  tackles: number;

  interceptions: number;

  blocks: number;

  duels: number;
  duelsWon: number;

  duelWinRate: number;
}


export interface PlayerDisciplineStats {
  foulsDrawn: number;

  foulsCommitted: number;

  yellowCards: number;

  redCards: number;
}


export interface PlayerGoalkeepingStats {
  saves: number;

  goalsConceded: number;

  penaltiesSaved: number;
}


export interface PlayerDetailedStats {
  attacking:
    PlayerAttackingStats;

  passing:
    PlayerPassingStats;

  dribbling:
    PlayerDribblingStats;

  defending:
    PlayerDefendingStats;

  discipline:
    PlayerDisciplineStats;

  goalkeeping:
    PlayerGoalkeepingStats;
}


export interface RecentPlayerMatch {
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
    logoUrl: string;
  };

  result: string | null;

  status: string;
}


/* =========================================
   FUTBUD RATING
========================================= */

export interface FutBudMetric {
  feature: string;

  value: number | null;

  percentile: number | null;

  weight: number | null;

  referencePlayers: number | null;
}


export interface FutBudRating {
  season: number;

  referenceSeason: number;

  position: string | null;

  orientation: string | null;

  orientationCluster:
    number | null;

  archetypeCluster:
    number | null;

  archetypeKey: string;

  archetype: string;

  minutes: number;

  appearances:
    number | null;

  starts:
    number | null;

  rawRating:
    number | null;

  minutesReliability:
    number | null;

  rating:
    number | null;

  percentile:
    number | null;

  status:
    string | null;

  metricCount:
    number | null;

  updatedAt:
    string | null;

  metrics:
    FutBudMetric[];
}


export interface PlayerDashboard {
  profile:
    PlayerDashboardProfile;

  summary:
    PlayerSeasonSummary;

  detailed:
    PlayerDetailedStats;

  futbud:
    FutBudRating | null;

  recentMatches:
    RecentPlayerMatch[];
}


const API =
  "http://127.0.0.1:8000";


export async function getPlayerDashboard(
  playerId: number,
  season = 2026,
): Promise<PlayerDashboard> {

  const response =
    await fetch(
      `${API}/players/${playerId}/dashboard?season=${season}`
    );


  if (!response.ok) {

    let message =
      "Failed to fetch player dashboard";

    try {

      const data =
        await response.json();

      if (data.detail) {
        message =
          data.detail;
      }

    } catch {
      // Keep default message.
    }

    throw new Error(
      message
    );
  }


  return response.json();
}