export interface MatchTeam {
  id: number;
  name: string;
  code: string;
  logoUrl: string;
}

export interface Match {
  id: number;
  round: string;
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

  league: {
    id: number;
    name: string;
    logoUrl: string;
  };
}


export async function getMatches(
  matchDate?: string,
  leagueId?: number
): Promise<Match[]> {

  const params =
    new URLSearchParams();

  params.append(
    "season",
    "2026"
  );

  if (matchDate) {
    params.append(
      "match_date",
      matchDate
    );
  }

  if (leagueId !== undefined) {
    params.append(
      "league_id",
      leagueId.toString()
    );
  }

  const response = await fetch(
    `http://127.0.0.1:8000/matches?${params.toString()}`
  );

  if (!response.ok) {
    throw new Error(
      "Failed to fetch matches"
    );
  }

  return response.json();
}