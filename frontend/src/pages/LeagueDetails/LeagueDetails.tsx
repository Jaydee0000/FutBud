import "./LeagueDetails.css";
import { Link, useParams } from "react-router";

interface Standing {
  position: number;
  team: string;
  shortName: string;
  played: number;
  won: number;
  drawn: number;
  lost: number;
  goalDifference: number;
  points: number;
}

interface Leader {
  name: string;
  team: string;
  value: number;
}

interface Match {
  home: string;
  away: string;
  homeScore?: number;
  awayScore?: number;
  date: string;
}

interface LeagueData {
  id: string;
  name: string;
  shortName: string;
  country: string;
  season: string;
  teams: number;
  matches: number;
  goals: number;
  goalsPerMatch: number;
  averageRating: number;

  standings: Standing[];

  topPlayers: Leader[];
  scorers: Leader[];
  assisters: Leader[];

  recentMatches: Match[];
  upcomingMatches: Match[];

  leaders: {
    bestAttack: string;
    bestDefense: string;
    bestForm: string;
    highestRated: string;
    highestPayroll: string;
    bestValue: string;
  };
}

const premierLeague: LeagueData = {
  id: "premier-league",
  name: "Premier League",
  shortName: "PL",
  country: "England",
  season: "2026/27",
  teams: 20,
  matches: 380,
  goals: 812,
  goalsPerMatch: 3.01,
  averageRating: 78.4,

  standings: [
    {
      position: 1,
      team: "Arsenal",
      shortName: "ARS",
      played: 28,
      won: 21,
      drawn: 5,
      lost: 2,
      goalDifference: 42,
      points: 68,
    },
    {
      position: 2,
      team: "Liverpool",
      shortName: "LIV",
      played: 28,
      won: 20,
      drawn: 5,
      lost: 3,
      goalDifference: 37,
      points: 65,
    },
    {
      position: 3,
      team: "Manchester City",
      shortName: "MCI",
      played: 28,
      won: 19,
      drawn: 5,
      lost: 4,
      goalDifference: 35,
      points: 62,
    },
    {
      position: 4,
      team: "Chelsea",
      shortName: "CHE",
      played: 28,
      won: 17,
      drawn: 6,
      lost: 5,
      goalDifference: 26,
      points: 57,
    },
    {
      position: 5,
      team: "Newcastle",
      shortName: "NEW",
      played: 28,
      won: 16,
      drawn: 5,
      lost: 7,
      goalDifference: 20,
      points: 53,
    },
  ],

  topPlayers: [
    { name: "Cole Palmer", team: "Chelsea", value: 92 },
    { name: "Erling Haaland", team: "Manchester City", value: 91 },
    { name: "Bukayo Saka", team: "Arsenal", value: 90 },
    { name: "Mohamed Salah", team: "Liverpool", value: 89 },
    { name: "Alexander Isak", team: "Newcastle", value: 88 },
  ],

  scorers: [
    { name: "Erling Haaland", team: "Manchester City", value: 24 },
    { name: "Mohamed Salah", team: "Liverpool", value: 20 },
    { name: "Alexander Isak", team: "Newcastle", value: 18 },
    { name: "Cole Palmer", team: "Chelsea", value: 17 },
    { name: "Bukayo Saka", team: "Arsenal", value: 15 },
  ],

  assisters: [
    { name: "Cole Palmer", team: "Chelsea", value: 13 },
    { name: "Bukayo Saka", team: "Arsenal", value: 11 },
    { name: "Mohamed Salah", team: "Liverpool", value: 10 },
    { name: "Bruno Fernandes", team: "Manchester United", value: 9 },
    { name: "Phil Foden", team: "Manchester City", value: 8 },
  ],

  recentMatches: [
    {
      home: "Arsenal",
      away: "Chelsea",
      homeScore: 3,
      awayScore: 1,
      date: "August 24",
    },
    {
      home: "Liverpool",
      away: "Tottenham",
      homeScore: 2,
      awayScore: 0,
      date: "August 24",
    },
    {
      home: "Manchester City",
      away: "Newcastle",
      homeScore: 2,
      awayScore: 2,
      date: "August 23",
    },
  ],

  upcomingMatches: [
    {
      home: "Arsenal",
      away: "Liverpool",
      date: "August 30 • 2:00 PM",
    },
    {
      home: "Chelsea",
      away: "Newcastle",
      date: "August 30 • 4:30 PM",
    },
    {
      home: "Manchester City",
      away: "Tottenham",
      date: "August 31 • 11:30 AM",
    },
  ],

  leaders: {
    bestAttack: "Arsenal",
    bestDefense: "Liverpool",
    bestForm: "Chelsea",
    highestRated: "Arsenal",
    highestPayroll: "Manchester City",
    bestValue: "Brighton",
  },
};

const leagueData: Record<string, LeagueData> = {
  "premier-league": premierLeague,

  "la-liga": {
    ...premierLeague,
    id: "la-liga",
    name: "La Liga",
    shortName: "LL",
    country: "Spain",
  },

  bundesliga: {
    ...premierLeague,
    id: "bundesliga",
    name: "Bundesliga",
    shortName: "BL",
    country: "Germany",
    teams: 18,
  },

  "serie-a": {
    ...premierLeague,
    id: "serie-a",
    name: "Serie A",
    shortName: "SA",
    country: "Italy",
  },

  "ligue-1": {
    ...premierLeague,
    id: "ligue-1",
    name: "Ligue 1",
    shortName: "L1",
    country: "France",
    teams: 18,
  },
};

function LeaderCard({
  title,
  players,
  suffix = "",
}: {
  title: string;
  players: Leader[];
  suffix?: string;
}) {
  return (
    <section className="league-detail-card">
      <h2>{title}</h2>

      <div className="league-leader-list">
        {players.map((player, index) => (
          <div className="league-leader-row" key={player.name}>
            <span className="league-leader-rank">
              {index + 1}
            </span>

            <div className="league-leader-player">
              <strong>{player.name}</strong>
              <span>{player.team}</span>
            </div>

            <strong className="league-leader-value">
              {player.value}
              {suffix}
            </strong>
          </div>
        ))}
      </div>
    </section>
  );
}

function LeagueDetails() {
  const { leagueId } = useParams();

  const league =
    leagueData[leagueId || "premier-league"];

  if (!league) {
    return (
      <main className="league-details-page">
        <h1>League not found</h1>

        <Link to="/leagues" className="back-to-leagues">
          ← Back to Leagues
        </Link>
      </main>
    );
  }

  return (
    <main className="league-details-page">

      <Link to="/leagues" className="back-to-leagues">
        ← Back to Leagues
      </Link>

      {/* LEAGUE HEADER */}

      <section className="league-detail-hero">
        <div className="league-detail-identity">
          <div className="league-detail-logo">
            {league.shortName}
          </div>

          <div>
            <p>Competition</p>
            <h1>{league.name}</h1>
            <span>
              {league.country} • {league.season}
            </span>
          </div>
        </div>

        <div className="league-detail-summary">
          <div>
            <span>Teams</span>
            <strong>{league.teams}</strong>
          </div>

          <div>
            <span>Matches</span>
            <strong>{league.matches}</strong>
          </div>

          <div>
            <span>Avg Rating</span>
            <strong>{league.averageRating}</strong>
          </div>
        </div>
      </section>


      {/* STANDINGS + TOP PLAYERS */}

      <section className="league-dashboard-top">

        <div className="league-detail-card standings-card">
          <div className="league-card-heading">
            <h2>Standings</h2>

            <button>Full Table</button>
          </div>

          <div className="standings-table">
            <div className="standing-row standing-header">
              <span>#</span>
              <span>Club</span>
              <span>PL</span>
              <span>W</span>
              <span>D</span>
              <span>L</span>
              <span>GD</span>
              <span>PTS</span>
            </div>

            {league.standings.map((team) => (
              <div
                className="standing-row"
                key={team.team}
              >
                <strong>{team.position}</strong>

                <div className="standing-team">
                  <div className="standing-logo">
                    {team.shortName}
                  </div>

                  <strong>{team.team}</strong>
                </div>

                <span>{team.played}</span>
                <span>{team.won}</span>
                <span>{team.drawn}</span>
                <span>{team.lost}</span>

                <span>
                  {team.goalDifference > 0 ? "+" : ""}
                  {team.goalDifference}
                </span>

                <strong className="standing-points">
                  {team.points}
                </strong>
              </div>
            ))}
          </div>
        </div>

        <LeaderCard
          title="Top Rated Players"
          players={league.topPlayers}
        />

      </section>


      {/* SCORERS + ASSISTERS */}

      <section className="league-two-column">
        <LeaderCard
          title="Top Goal Scorers"
          players={league.scorers}
        />

        <LeaderCard
          title="Top Assisters"
          players={league.assisters}
        />
      </section>


      {/* MATCHES */}

      <section className="league-two-column">

        <section className="league-detail-card">
          <h2>Recent Results</h2>

          <div className="league-match-list">
            {league.recentMatches.map((match, index) => (
              <div
                className="league-match-row"
                key={index}
              >
                <div className="match-date">
                  {match.date}
                </div>

                <div className="match-teams-line">
                  <span>{match.home}</span>

                  <strong>
                    {match.homeScore} - {match.awayScore}
                  </strong>

                  <span>{match.away}</span>
                </div>
              </div>
            ))}
          </div>
        </section>


        <section className="league-detail-card">
          <h2>Upcoming Matches</h2>

          <div className="league-match-list">
            {league.upcomingMatches.map((match, index) => (
              <div
                className="league-match-row"
                key={index}
              >
                <div className="match-date">
                  {match.date}
                </div>

                <div className="match-teams-line">
                  <span>{match.home}</span>

                  <strong className="versus-text">
                    VS
                  </strong>

                  <span>{match.away}</span>
                </div>
              </div>
            ))}
          </div>
        </section>

      </section>


      {/* SEASON OVERVIEW */}

      <section className="season-overview">
        <div className="season-overview-heading">
          <h2>Season Overview</h2>
          <p>
            Competition-wide performance statistics.
          </p>
        </div>

        <div className="season-stat-grid">

          <div>
            <span>Matches</span>
            <strong>{league.matches}</strong>
          </div>

          <div>
            <span>Total Goals</span>
            <strong>{league.goals}</strong>
          </div>

          <div>
            <span>Goals / Match</span>
            <strong>{league.goalsPerMatch}</strong>
          </div>

          <div>
            <span>Average Rating</span>
            <strong>{league.averageRating}</strong>
          </div>

        </div>
      </section>


      {/* LEAGUE LEADERS */}

      <section className="league-leaders-section">
        <div className="season-overview-heading">
          <h2>League Leaders</h2>
          <p>
            Clubs leading important performance categories.
          </p>
        </div>

        <div className="league-leader-grid">

          <div>
            <span>Best Attack</span>
            <strong>{league.leaders.bestAttack}</strong>
          </div>

          <div>
            <span>Best Defense</span>
            <strong>{league.leaders.bestDefense}</strong>
          </div>

          <div>
            <span>Best Form</span>
            <strong>{league.leaders.bestForm}</strong>
          </div>

          <div>
            <span>Highest Rated</span>
            <strong>{league.leaders.highestRated}</strong>
          </div>

          <div>
            <span>Highest Payroll</span>
            <strong>{league.leaders.highestPayroll}</strong>
          </div>

          <div>
            <span>Best Value Squad</span>
            <strong>{league.leaders.bestValue}</strong>
          </div>

        </div>
      </section>

    </main>
  );
}

export default LeagueDetails;