import "./Players.css";

import { useEffect, useState } from "react";
import {
  getPlayers,
  type Player,
} from "../../services/playerService";

interface PlayerStat {
  name: string;
  team: string;
  value: string | number;
}

interface StatCardProps {
  title: string;
  icon: string;
  players: PlayerStat[];
  footer: string;
  colorClass: string;
}

const topRated: PlayerStat[] = [
  { name: "Erling Haaland", team: "Manchester City", value: 94 },
  { name: "Cole Palmer", team: "Chelsea", value: 92 },
  { name: "Mohamed Salah", team: "Liverpool", value: 91 },
  { name: "Bukayo Saka", team: "Arsenal", value: 90 },
  { name: "Jude Bellingham", team: "Real Madrid", value: 89 },
];

const highestPaid: PlayerStat[] = [
  { name: "Player One", team: "Manchester City", value: "£400k/wk" },
  { name: "Player Two", team: "Manchester United", value: "£375k/wk" },
  { name: "Player Three", team: "Liverpool", value: "£350k/wk" },
  { name: "Player Four", team: "Chelsea", value: "£325k/wk" },
  { name: "Player Five", team: "Arsenal", value: "£300k/wk" },
];

const goalScorers: PlayerStat[] = [
  { name: "Erling Haaland", team: "Manchester City", value: 24 },
  { name: "Mohamed Salah", team: "Liverpool", value: 20 },
  { name: "Alexander Isak", team: "Newcastle", value: 18 },
  { name: "Cole Palmer", team: "Chelsea", value: 17 },
  { name: "Bukayo Saka", team: "Arsenal", value: 15 },
];

const assisters: PlayerStat[] = [
  { name: "Cole Palmer", team: "Chelsea", value: 13 },
  { name: "Bukayo Saka", team: "Arsenal", value: 11 },
  { name: "Mohamed Salah", team: "Liverpool", value: 10 },
  { name: "Bruno Fernandes", team: "Manchester United", value: 9 },
  { name: "Phil Foden", team: "Manchester City", value: 8 },
];

const saves: PlayerStat[] = [
  { name: "Goalkeeper One", team: "Everton", value: 102 },
  { name: "Goalkeeper Two", team: "Crystal Palace", value: 96 },
  { name: "Goalkeeper Three", team: "Brighton", value: 91 },
  { name: "Goalkeeper Four", team: "Chelsea", value: 87 },
  { name: "Goalkeeper Five", team: "Arsenal", value: 81 },
];

const cleanSheets: PlayerStat[] = [
  { name: "Goalkeeper One", team: "Arsenal", value: 15 },
  { name: "Goalkeeper Two", team: "Liverpool", value: 13 },
  { name: "Goalkeeper Three", team: "Manchester City", value: 12 },
  { name: "Goalkeeper Four", team: "Everton", value: 11 },
  { name: "Goalkeeper Five", team: "Chelsea", value: 10 },
];

const keyPasses: PlayerStat[] = [
  { name: "Cole Palmer", team: "Chelsea", value: 72 },
  { name: "Bruno Fernandes", team: "Manchester United", value: 68 },
  { name: "Bukayo Saka", team: "Arsenal", value: 61 },
  { name: "Mohamed Salah", team: "Liverpool", value: 58 },
  { name: "Phil Foden", team: "Manchester City", value: 54 },
];

const dribbles: PlayerStat[] = [
  { name: "Jeremy Doku", team: "Manchester City", value: 76 },
  { name: "Bukayo Saka", team: "Arsenal", value: 69 },
  { name: "Cole Palmer", team: "Chelsea", value: 62 },
  { name: "Mohamed Kudus", team: "West Ham", value: 59 },
  { name: "Luis Díaz", team: "Liverpool", value: 55 },
];

const risingStars: PlayerStat[] = [
  { name: "Young Player One", team: "Arsenal", value: 86 },
  { name: "Young Player Two", team: "Chelsea", value: 84 },
  { name: "Young Player Three", team: "Manchester City", value: 83 },
  { name: "Young Player Four", team: "Liverpool", value: 82 },
  { name: "Young Player Five", team: "Tottenham", value: 80 },
];

function getInitials(name: string) {
  return name
    .split(" ")
    .map((word) => word[0])
    .join("")
    .slice(0, 2);
}

function StatCard({
  title,
  icon,
  players,
  footer,
  colorClass,
}: StatCardProps) {
  return (
    <section className={`player-stat-card ${colorClass}`}>
      <div className="stat-card-heading">
        <div className="stat-card-title">
          <span className="stat-icon">{icon}</span>
          <h2>{title}</h2>
        </div>

        <button className="view-stat-button">
          View all
        </button>
      </div>

      <div className="stat-player-list">
        {players.map((player, index) => (
          <div
            className="stat-player-row"
            key={player.name}
          >
            <span className="stat-rank">
              {index + 1}
            </span>

            <div className="player-avatar">
              {getInitials(player.name)}
            </div>

            <div className="stat-player-info">
              <strong>{player.name}</strong>
              <span>{player.team}</span>
            </div>

            <strong className="stat-value">
              {player.value}
            </strong>
          </div>
        ))}
      </div>

      <div className="stat-footer">
        {footer}
      </div>
    </section>
  );
}

function Players() {
  const [databasePlayers, setDatabasePlayers] =
    useState<Player[]>([]);

  useEffect(() => {
    getPlayers()
      .then((players) => {
        console.log(
          "Players from backend:",
          players
        );

        setDatabasePlayers(players);
      })
      .catch((error) => {
        console.error(
          "Error loading players:",
          error
        );
      });
  }, []);

  const topRatedFromDatabase: PlayerStat[] = databasePlayers.map((player) => ({
      name: player.name,
      team: player.team.name,
      value: player.rating,
    }));

  return (
    <main className="players-page">
        

      <div className="players-heading">
        <div>
          <h1>Players</h1>

          <p>
            Explore the best performers across
            football.
          </p>
        </div>

        <div className="player-filters">
          <select defaultValue="all">
            <option value="all">
              All Leagues
            </option>

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

      <div className="stats-grid">

        <StatCard
          title="Top Rated Players"
          icon="★"
          players={topRatedFromDatabase}
          footer="Based on FutBud Rating"
          colorClass="green-card"
        />

        <StatCard
          title="Highest Paid Players"
          icon="$"
          players={highestPaid}
          footer="Estimated weekly wage"
          colorClass="purple-card"
        />

        <StatCard
          title="Top Goal Scorers"
          icon="⚽"
          players={goalScorers}
          footer="Goals this season"
          colorClass="lime-card"
        />

        <StatCard
          title="Top Assisters"
          icon="A"
          players={assisters}
          footer="Assists this season"
          colorClass="blue-card"
        />

        <StatCard
          title="Most Saves"
          icon="✋"
          players={saves}
          footer="Goalkeeper saves this season"
          colorClass="orange-card"
        />

        <StatCard
          title="Most Clean Sheets"
          icon="◇"
          players={cleanSheets}
          footer="Clean sheets this season"
          colorClass="cyan-card"
        />

        <StatCard
          title="Most Key Passes"
          icon="↗"
          players={keyPasses}
          footer="Passes leading directly to a shot"
          colorClass="yellow-card"
        />

        <StatCard
          title="Most Dribbles Completed"
          icon="◆"
          players={dribbles}
          footer="Successful dribbles this season"
          colorClass="pink-card"
        />

      </div>

      <section className="rising-stars">
        <div className="rising-stars-heading">
          <div>
            <h2>↗ Rising Stars to Watch</h2>

            <p>
              Young players making an impact
            </p>
          </div>

          <button>
            View all
          </button>
        </div>

        <div className="rising-stars-list">
          {risingStars.map((player, index) => (
            <div
              className="rising-star"
              key={player.name}
            >
              <span className="rising-rank">
                {index + 1}
              </span>

              <div className="player-avatar">
                {getInitials(player.name)}
              </div>

              <div className="stat-player-info">
                <strong>
                  {player.name}
                </strong>

                <span>
                  {player.team}
                </span>
              </div>

              <strong className="rising-rating">
                {player.value}
              </strong>
            </div>
          ))}
        </div>
      </section>

    </main>
  );
}

export default Players;