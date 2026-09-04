import "./Leagues.css";
import { Link } from "react-router";

interface League {
  id: string;
  name: string;
  country: string;
  shortName: string;
  teams: number;
  leader: string;
  topPlayer: string;
  topRating: number;
  goalsPerGame: number;
  averageRating: number;
  competitiveness: number;
}

const leagues: League[] = [
  {
    id: "premier-league",
    name: "Premier League",
    country: "England",
    shortName: "PL",
    teams: 20,
    leader: "Arsenal",
    topPlayer: "Cole Palmer",
    topRating: 91,
    goalsPerGame: 3.01,
    averageRating: 78.4,
    competitiveness: 91,
  },
  {
    id: "la-liga",
    name: "La Liga",
    country: "Spain",
    shortName: "LL",
    teams: 20,
    leader: "Barcelona",
    topPlayer: "Player One",
    topRating: 92,
    goalsPerGame: 2.74,
    averageRating: 77.9,
    competitiveness: 83,
  },
  {
    id: "bundesliga",
    name: "Bundesliga",
    country: "Germany",
    shortName: "BL",
    teams: 18,
    leader: "Bayern Munich",
    topPlayer: "Player Two",
    topRating: 90,
    goalsPerGame: 3.18,
    averageRating: 77.2,
    competitiveness: 78,
  },
  {
    id: "serie-a",
    name: "Serie A",
    country: "Italy",
    shortName: "SA",
    teams: 20,
    leader: "Inter Milan",
    topPlayer: "Player Three",
    topRating: 89,
    goalsPerGame: 2.66,
    averageRating: 76.8,
    competitiveness: 81,
  },
  {
    id: "ligue-1",
    name: "Ligue 1",
    country: "France",
    shortName: "L1",
    teams: 18,
    leader: "Paris Saint-Germain",
    topPlayer: "Player Four",
    topRating: 88,
    goalsPerGame: 2.81,
    averageRating: 75.9,
    competitiveness: 74,
  },
];

function LeagueCard({ league }: { league: League }) {
  return (
    <article className="league-card">
      <div className="league-card-top">
        <div className="league-logo-placeholder">
          {league.shortName}
        </div>

        <div>
          <h2>{league.name}</h2>
          <span>{league.country}</span>
        </div>
      </div>

      <div className="league-card-details">
        <div>
          <span>Teams</span>
          <strong>{league.teams}</strong>
        </div>

        <div>
          <span>Current Leader</span>
          <strong>{league.leader}</strong>
        </div>

        <div>
          <span>Top Player</span>
          <strong>{league.topPlayer}</strong>
        </div>

        <div>
          <span>Top Rating</span>
          <strong className="league-green">
            {league.topRating}
          </strong>
        </div>
      </div>

      <Link
        to={`/leagues/${league.id}`}
        className="view-league-button"
      >
        View League
        <span>→</span>
      </Link>
    </article>
  );
}

function Leagues() {
  const featuredLeague = leagues[0];

  return (
    <main className="leagues-page">
      <div className="leagues-heading">
        <div>
          <h1>Leagues</h1>

          <p>
            Explore competitions, standings and top performers.
          </p>
        </div>

        <select defaultValue="2026">
          <option value="2026">
            2026/27 Season
          </option>
        </select>
      </div>

      {/* FEATURED LEAGUE */}

      <section className="featured-league">
        <div className="featured-league-left">
          <p className="league-section-label">
            Featured League
          </p>

          <div className="featured-league-info">
            <div className="featured-league-logo">
              {featuredLeague.shortName}
            </div>

            <div>
              <h2>{featuredLeague.name}</h2>
              <span>{featuredLeague.country}</span>
            </div>
          </div>

          <div className="featured-league-stats">
            <div>
              <span>Teams</span>
              <strong>{featuredLeague.teams}</strong>
            </div>

            <div>
              <span>Season</span>
              <strong>2026/27</strong>
            </div>

            <div>
              <span>Leader</span>
              <strong>{featuredLeague.leader}</strong>
            </div>

            <div>
              <span>Top Player</span>
              <strong>{featuredLeague.topPlayer}</strong>
            </div>
          </div>
        </div>

        <div className="featured-league-right">
          <span>Top FutBud Rating</span>

          <strong>
            {featuredLeague.topRating}
          </strong>

          <Link
            to={`/leagues/${featuredLeague.id}`}
            className="featured-league-button"
          >
            View League
            <span>→</span>
          </Link>
        </div>
      </section>

      {/* ALL LEAGUES */}

      <section className="all-leagues-section">
        <div className="league-section-heading">
          <div>
            <h2>Top European Leagues</h2>

            <p>
              Browse competitions available on FutBud.
            </p>
          </div>
        </div>

        <div className="league-card-grid">
          {leagues.map((league) => (
            <LeagueCard
              key={league.id}
              league={league}
            />
          ))}
        </div>
      </section>

      {/* LEAGUE COMPARISON */}

      <section className="league-comparison">
        <div className="league-section-heading">
          <div>
            <h2>League Comparison</h2>

            <p>
              Compare performance and competitiveness across leagues.
            </p>
          </div>
        </div>

        <div className="league-comparison-table">
          <div className="comparison-row comparison-header">
            <span>League</span>
            <span>Goals / Game</span>
            <span>Avg Rating</span>
            <span>Top Player</span>
            <span>Top Rating</span>
            <span>Competitiveness</span>
          </div>

          {leagues.map((league) => (
            <div
              className="comparison-row"
              key={league.id}
            >
              <div className="comparison-league">
                <div className="small-league-logo">
                  {league.shortName}
                </div>

                <div>
                  <strong>{league.name}</strong>
                  <span>{league.country}</span>
                </div>
              </div>

              <strong>{league.goalsPerGame}</strong>

              <strong>{league.averageRating}</strong>

              <span>{league.topPlayer}</span>

              <span className="comparison-rating">
                {league.topRating}
              </span>

              <div className="competitiveness">
                <div className="competitiveness-track">
                  <div
                    className="competitiveness-fill"
                    style={{
                      width: `${league.competitiveness}%`,
                    }}
                  />
                </div>

                <strong>
                  {league.competitiveness}
                </strong>
              </div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}

export default Leagues;