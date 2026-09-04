import "./Rankings.css";

interface RankedPlayer {
  rank: number;
  name: string;
  team: string;
  position: string;
  rating: number;
  change: number;
}

interface PositionPlayer {
  name: string;
  team: string;
  rating: number;
}

interface RankedTeam {
  rank: number;
  name: string;
  shortName: string;
  rating: number;
  change: number;
}

const playerRankings: RankedPlayer[] = [
  {
    rank: 1,
    name: "Cole Palmer",
    team: "Chelsea",
    position: "AM",
    rating: 92,
    change: 2,
  },
  {
    rank: 2,
    name: "Erling Haaland",
    team: "Manchester City",
    position: "ST",
    rating: 91,
    change: 0,
  },
  {
    rank: 3,
    name: "Mohamed Salah",
    team: "Liverpool",
    position: "RW",
    rating: 90,
    change: -1,
  },
  {
    rank: 4,
    name: "Bukayo Saka",
    team: "Arsenal",
    position: "RW",
    rating: 89,
    change: 1,
  },
  {
    rank: 5,
    name: "Declan Rice",
    team: "Arsenal",
    position: "CM",
    rating: 88,
    change: 3,
  },
  {
    rank: 6,
    name: "Virgil van Dijk",
    team: "Liverpool",
    position: "CB",
    rating: 88,
    change: -2,
  },
  {
    rank: 7,
    name: "Alexander Isak",
    team: "Newcastle",
    position: "ST",
    rating: 87,
    change: 1,
  },
  {
    rank: 8,
    name: "William Saliba",
    team: "Arsenal",
    position: "CB",
    rating: 87,
    change: 0,
  },
  {
    rank: 9,
    name: "Phil Foden",
    team: "Manchester City",
    position: "AM",
    rating: 86,
    change: -3,
  },
  {
    rank: 10,
    name: "Alisson",
    team: "Liverpool",
    position: "GK",
    rating: 86,
    change: 2,
  },
];

const forwards: PositionPlayer[] = [
  {
    name: "Erling Haaland",
    team: "Manchester City",
    rating: 91,
  },
  {
    name: "Mohamed Salah",
    team: "Liverpool",
    rating: 90,
  },
  {
    name: "Bukayo Saka",
    team: "Arsenal",
    rating: 89,
  },
];

const midfielders: PositionPlayer[] = [
  {
    name: "Cole Palmer",
    team: "Chelsea",
    rating: 92,
  },
  {
    name: "Declan Rice",
    team: "Arsenal",
    rating: 88,
  },
  {
    name: "Phil Foden",
    team: "Manchester City",
    rating: 86,
  },
];

const defenders: PositionPlayer[] = [
  {
    name: "Virgil van Dijk",
    team: "Liverpool",
    rating: 88,
  },
  {
    name: "William Saliba",
    team: "Arsenal",
    rating: 87,
  },
  {
    name: "Gabriel",
    team: "Arsenal",
    rating: 85,
  },
];

const goalkeepers: PositionPlayer[] = [
  {
    name: "Alisson",
    team: "Liverpool",
    rating: 86,
  },
  {
    name: "David Raya",
    team: "Arsenal",
    rating: 85,
  },
  {
    name: "Ederson",
    team: "Manchester City",
    rating: 84,
  },
];

const risers = [
  {
    name: "Cole Palmer",
    team: "Chelsea",
    change: 5,
  },
  {
    name: "Declan Rice",
    team: "Arsenal",
    change: 4,
  },
  {
    name: "Alexander Isak",
    team: "Newcastle",
    change: 3,
  },
  {
    name: "Alisson",
    team: "Liverpool",
    change: 3,
  },
];

const fallers = [
  {
    name: "Player One",
    team: "Manchester United",
    change: -6,
  },
  {
    name: "Player Two",
    team: "Tottenham",
    change: -5,
  },
  {
    name: "Player Three",
    team: "Chelsea",
    change: -4,
  },
  {
    name: "Player Four",
    team: "Aston Villa",
    change: -3,
  },
];

const teamRankings: RankedTeam[] = [
  {
    rank: 1,
    name: "Arsenal",
    shortName: "ARS",
    rating: 91,
    change: 1,
  },
  {
    rank: 2,
    name: "Liverpool",
    shortName: "LIV",
    rating: 89,
    change: -1,
  },
  {
    rank: 3,
    name: "Manchester City",
    shortName: "MCI",
    rating: 88,
    change: 0,
  },
  {
    rank: 4,
    name: "Chelsea",
    shortName: "CHE",
    rating: 85,
    change: 2,
  },
  {
    rank: 5,
    name: "Newcastle",
    shortName: "NEW",
    rating: 82,
    change: 0,
  },
];

function Movement({ change }: { change: number }) {
  if (change > 0) {
    return (
      <span className="ranking-change up">
        ↑ {change}
      </span>
    );
  }

  if (change < 0) {
    return (
      <span className="ranking-change down">
        ↓ {Math.abs(change)}
      </span>
    );
  }

  return (
    <span className="ranking-change neutral">
      —
    </span>
  );
}

function PositionCard({
  title,
  players,
}: {
  title: string;
  players: PositionPlayer[];
}) {
  return (
    <section className="position-ranking-card">
      <h2>{title}</h2>

      <div className="position-ranking-list">
        {players.map((player, index) => (
          <div
            className="position-ranking-row"
            key={player.name}
          >
            <span className="position-rank">
              {index + 1}
            </span>

            <div className="ranking-avatar">
              {player.name
                .split(" ")
                .map((word) => word[0])
                .join("")
                .slice(0, 2)}
            </div>

            <div className="position-player-info">
              <strong>{player.name}</strong>
              <span>{player.team}</span>
            </div>

            <strong className="position-rating">
              {player.rating}
            </strong>
          </div>
        ))}
      </div>
    </section>
  );
}

function Rankings() {
  return (
    <main className="rankings-page">

      {/* HEADING */}

      <div className="rankings-heading">
        <div>
          <h1>Rankings</h1>

          <p>
            FutBud player and team power rankings.
          </p>
        </div>

        <div className="ranking-filters">
          <select defaultValue="premier-league">
            <option value="premier-league">
              Premier League
            </option>

            <option value="la-liga">
              La Liga
            </option>

            <option value="bundesliga">
              Bundesliga
            </option>

            <option value="serie-a">
              Serie A
            </option>

            <option value="ligue-1">
              Ligue 1
            </option>
          </select>

          <select defaultValue="2026">
            <option value="2026">
              2026/27 Season
            </option>
          </select>
        </div>
      </div>


      {/* PLAYER POWER RANKINGS */}

      <section className="ranking-card player-power-card">

        <div className="ranking-section-heading">
          <div>
            <p className="ranking-label">
              FutBud Ratings
            </p>

            <h2>
              Player Power Rankings
            </h2>
          </div>

          <span>
            Updated Weekly
          </span>
        </div>

        <div className="player-ranking-table">

          <div className="player-ranking-row ranking-table-header">
            <span>#</span>
            <span>Player</span>
            <span>Position</span>
            <span>Rating</span>
            <span>Change</span>
          </div>

          {playerRankings.map((player) => (
            <div
              className="player-ranking-row"
              key={player.name}
            >
              <strong className="ranking-number">
                {player.rank}
              </strong>

              <div className="ranked-player">
                <div className="ranking-avatar">
                  {player.name
                    .split(" ")
                    .map((word) => word[0])
                    .join("")
                    .slice(0, 2)}
                </div>

                <div>
                  <strong>
                    {player.name}
                  </strong>

                  <span>
                    {player.team}
                  </span>
                </div>
              </div>

              <span className="ranking-position">
                {player.position}
              </span>

              <strong className="ranking-rating">
                {player.rating}
              </strong>

              <Movement
                change={player.change}
              />
            </div>
          ))}

        </div>
      </section>


      {/* POSITION RANKINGS */}

      <section className="position-section">

        <div className="rankings-subheading">
          <h2>
            Top by Position
          </h2>

          <p>
            Highest-rated players by role.
          </p>
        </div>

        <div className="position-ranking-grid">

          <PositionCard
            title="Forwards"
            players={forwards}
          />

          <PositionCard
            title="Midfielders"
            players={midfielders}
          />

          <PositionCard
            title="Defenders"
            players={defenders}
          />

          <PositionCard
            title="Goalkeepers"
            players={goalkeepers}
          />

        </div>
      </section>


      {/* RISERS / FALLERS */}

      <section className="movement-grid">

        <div className="ranking-card">
          <div className="movement-heading">
            <div>
              <h2>Biggest Risers</h2>

              <p>
                Largest ranking gains.
              </p>
            </div>

            <span className="movement-arrow up">
              ↑
            </span>
          </div>

          <div className="movement-list">
            {risers.map((player, index) => (
              <div
                className="movement-row"
                key={player.name}
              >
                <span>
                  {index + 1}
                </span>

                <div>
                  <strong>
                    {player.name}
                  </strong>

                  <small>
                    {player.team}
                  </small>
                </div>

                <strong className="movement-positive">
                  +{player.change}
                </strong>
              </div>
            ))}
          </div>
        </div>


        <div className="ranking-card">
          <div className="movement-heading">
            <div>
              <h2>Biggest Fallers</h2>

              <p>
                Largest ranking drops.
              </p>
            </div>

            <span className="movement-arrow down">
              ↓
            </span>
          </div>

          <div className="movement-list">
            {fallers.map((player, index) => (
              <div
                className="movement-row"
                key={player.name}
              >
                <span>
                  {index + 1}
                </span>

                <div>
                  <strong>
                    {player.name}
                  </strong>

                  <small>
                    {player.team}
                  </small>
                </div>

                <strong className="movement-negative">
                  {player.change}
                </strong>
              </div>
            ))}
          </div>
        </div>

      </section>


      {/* TEAM RANKINGS */}

      <section className="ranking-card team-power-card">

        <div className="ranking-section-heading">
          <div>
            <p className="ranking-label">
              Club Ratings
            </p>

            <h2>
              Team Power Rankings
            </h2>
          </div>

          <span>
            Premier League
          </span>
        </div>

        <div className="team-ranking-list">

          {teamRankings.map((team) => (
            <div
              className="team-ranking-row"
              key={team.name}
            >

              <strong className="ranking-number">
                {team.rank}
              </strong>

              <div className="ranked-team">

                <div className="ranking-team-logo">
                  {team.shortName}
                </div>

                <strong>
                  {team.name}
                </strong>

              </div>

              <strong className="ranking-rating">
                {team.rating}
              </strong>

              <Movement
                change={team.change}
              />

            </div>
          ))}

        </div>
      </section>

    </main>
  );
}

export default Rankings;