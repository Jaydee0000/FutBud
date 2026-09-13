export interface TeamDashboardPlayer {
  id: number;
  name: string;
  photoUrl: string | null;
  shirtNumber: number | null;
  position: string | null;
}


export interface TeamLeader {
  player: TeamDashboardPlayer;
  value: number;
}


export interface TeamDashboardMatch {
  id: number;
  date: string;

  status: {
    long: string;
    short: string;
  };

  homeTeam: {
    id: number;
    name: string;
    logoUrl: string;
  };

  awayTeam: {
    id: number;
    name: string;
    logoUrl: string;
  };

  homeGoals: number | null;
  awayGoals: number | null;

  homeAway: "H" | "A";

  opponent: {
    id: number;
    name: string;
    logoUrl: string;
  };

  result: string | null;
}


export interface TeamSquadPlayer {
  player: {
    id: number;
    name: string;
    photoUrl: string | null;
    nationality: string | null;
    birthDate: string | null;
  };

  futbudRating: number | null;

  shirtNumber: number | null;
  position: string | null;

  injured: boolean;

  matchdaySelections: number;
  starts: number;
  appearances: number;

  minutes: number;

  goals: number;
  assists: number;
}


export interface TeamDashboard {
  team: {
    id: number;
    name: string;
    code: string | null;
    country: string | null;
    founded: number | null;
    logoUrl: string;

    venue: {
      name: string | null;
      city: string | null;
      capacity: number | null;
      imageUrl: string | null;
    };

    league: {
      id: number;
      name: string;
      logoUrl: string;
    };

    season: number;
  };

  overview: {
    standing: {
      rank: number;
      points: number;
      played: number;
      wins: number;
      draws: number;
      losses: number;
      goalsFor: number;
      goalsAgainst: number;
      goalDifference: number;
      form: string | null;
    } | null;

    nextMatch:
      TeamDashboardMatch | null;

    recentResults:
      TeamDashboardMatch[];

    leagueContext: {
      rank: number;

      team: {
        id: number;
        name: string;
        logoUrl: string;
      };

      played: number;
      goalDifference: number;
      points: number;
    }[];

    leaders: {
      goals: TeamLeader | null;
      assists: TeamLeader | null;
      keyPasses: TeamLeader | null;
    };
  };

  squad: TeamSquadPlayer[];

  results: {
    matches: TeamDashboardMatch[];

    record: {
      played: number;
      wins: number;
      draws: number;
      losses: number;
      goalsFor: number;
      goalsAgainst: number;
    };
  };

  stats: {
    games: number;

    attacking: {
      goals: number;
      goalsPerGame: number;
      shots: number;
      shotsPerGame: number;
      shotsOnTarget: number;
      shotsOnTargetPerGame: number;
      shotsOffTarget: number;
      blockedShots: number;
      shotsInsideBox: number;
      shotsOutsideBox: number;
      corners: number;
      offsides: number;
    };

    passing: {
      possession: number;
      passes: number;
      passesPerGame: number;
      accuratePasses: number;
      passAccuracy: number;
    };

    defending: {
      goalsAgainst: number;
      goalsAgainstPerGame: number;
      cleanSheets: number;
      goalkeeperSaves: number;
      savesPerGame: number;
    };

    discipline: {
      fouls: number;
      foulsPerGame: number;
      yellowCards: number;
      redCards: number;
    };

    contributors: {
      goals: TeamLeader[];
      assists: TeamLeader[];
      keyPasses: TeamLeader[];
    };
  };
}


const API =
  "http://127.0.0.1:8000";


export async function getTeamDashboard(
  teamId: number,
  season = 2026,
): Promise<TeamDashboard> {

  const response =
    await fetch(
      `${API}/teams/${teamId}/dashboard?season=${season}`
    );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch team dashboard"
    );
  }

  return response.json();
}
