const API_URL =
  "http://127.0.0.1:8000";


export interface MatchTeam {
  id: number;
  name: string;
  logoUrl: string | null;
}


export interface MatchLeague {
  id: number;
  name: string;
  logoUrl: string | null;
}


export interface MatchStatus {
  long: string | null;
  short: string | null;
  elapsed: number | null;
}


export interface MatchHeader {
  id: number;
  date: string;
  season: number;

  round: string | null;
  referee: string | null;
  venue: string | null;

  status: MatchStatus;

  league: MatchLeague;

  homeTeam: MatchTeam;
  awayTeam: MatchTeam;

  score: {
    home: number | null;
    away: number | null;
  };
}


export interface MatchEvent {
  index: number;

  teamId: number | null;

  player: {
    id: number | null;
    name: string | null;
  };

  assist: {
    id: number | null;
    name: string | null;
  };

  time: {
    elapsed: number | null;
    extra: number | null;
  };

  type: string | null;
  detail: string | null;
  comments: string | null;
}


export interface LineupPlayer {
  id: number;
  name: string;
  photoUrl: string | null;

  shirtNumber: number | null;
  position: string | null;

  grid: string | null;
}


export interface TeamLineup {
  formation: string | null;

  coach: {
    id: number | null;
    name: string | null;
    photoUrl: string | null;
  } | null;

  starters: LineupPlayer[];
  bench: LineupPlayer[];
}


export interface TeamMatchStats {
  shots: {
    total: number | null;
    onTarget: number | null;
    offTarget: number | null;
    blocked: number | null;
    insideBox: number | null;
    outsideBox: number | null;
  };

  fouls: number | null;
  corners: number | null;
  offsides: number | null;

  possession: number | null;

  yellowCards: number | null;
  redCards: number | null;

  goalkeeperSaves: number | null;

  passes: {
    total: number | null;
    accurate: number | null;
    accuracy: number | null;
  };
}


export interface PlayerMatchStat {
  player: {
    id: number;
    name: string;
    photoUrl: string | null;
  };

  minutes: number | null;

  shirtNumber: number | null;
  position: string | null;

  rating: number | string | null;

  captain: boolean | null;
  substitute: boolean | null;

  offsides: number | null;

  shots: {
    total: number | null;
    onTarget: number | null;
  };

  goals: number | null;
  goalsConceded: number | null;
  assists: number | null;
  saves: number | null;

  passes: {
    total: number | null;
    key: number | null;

    /*
      Current backend may still be using
      this field as either count or %.
      We handle that safely in the UI.
    */
    accuracy: number | null;

    accurate?: number | null;
  };

  tackles: number | null;
  blocks: number | null;
  interceptions: number | null;

  duels: {
    total: number | null;
    won: number | null;
  };

  dribbles: {
    attempted: number | null;
    successful: number | null;
    past: number | null;
  };

  fouls: {
    drawn: number | null;
    committed: number | null;
  };

  cards: {
    yellow: number | null;
    red: number | null;
  };

  penalties: {
    won: number | null;
    committed: number | null;
    scored: number | null;
    missed: number | null;
    saved: number | null;
  };
}


export interface HeadToHeadMatch {
  id: number;
  date: string | null;
  status: string | null;

  league: MatchLeague;

  homeTeam: MatchTeam;
  awayTeam: MatchTeam;

  homeGoals: number | null;
  awayGoals: number | null;
}


export interface MatchDashboard {
  match: MatchHeader;

  events: MatchEvent[];

  lineups: {
    home: TeamLineup;
    away: TeamLineup;
  };

  matchStats: {
    home: TeamMatchStats | null;
    away: TeamMatchStats | null;
  };

  playerStats: {
    home: PlayerMatchStat[];
    away: PlayerMatchStat[];
  };

  headToHead: {
    homeWins: number;
    draws: number;
    awayWins: number;

    matches: HeadToHeadMatch[];
  };
}


export async function getMatchDashboard(
  matchId: number
): Promise<MatchDashboard> {

  const response = await fetch(
    `${API_URL}/matches/${matchId}/dashboard`
  );


  if (!response.ok) {

    throw new Error(
      `Match dashboard request failed: ${response.status}`
    );

  }


  return response.json();
}