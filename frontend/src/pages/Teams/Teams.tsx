import "./Teams.css";

import { Link } from "react-router";

import { useEffect, useState } from "react";

import { getTeams } from "../../services/teamService";
import type { Team as ApiTeam } from "../../services/teamService";

export interface Team {
  id: number;
  name: string;
  code: string;
  country: string;
  founded: number;
  logoUrl: string;

  venue: {
    id: number;
    name: string;
    city: string;
    capacity: number;
    imageUrl: string;
  };

  league?: {
    id: number;
    name: string;
    season: number;
  };
}


function Teams() {
  const [databaseTeams, setDatabaseTeams] =
    useState<ApiTeam[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);


  useEffect(() => {
    getTeams()
      .then((teams) => {
        console.log(
          "Teams from backend:",
          teams
        );

        setDatabaseTeams(teams);
      })
      .catch((error) => {
        console.error(
          "Error loading teams:",
          error
        );

        setError(
          "Unable to load teams."
        );
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);


  return (
    <main className="teams-page">

      <div className="teams-heading">
        <div>
          <h1>Teams</h1>

          <p>
            Explore clubs across the Premier League.
          </p>
        </div>

        <div className="team-filters">
          <select defaultValue="premier-league">
            <option value="premier-league">
              Premier League
            </option>
          </select>

          <select defaultValue="2026">
            <option value="2026">
              2026/27 Season
            </option>
          </select>
        </div>
      </div>


      {loading && (
        <p>
          Loading teams...
        </p>
      )}


      {error && (
        <p>
          {error}
        </p>
      )}


      {!loading && !error && (
        <section className="teams-grid">

          {databaseTeams.map((team) => (
            <article
              className="team-card"
              key={team.id}
            >

              <div className="team-card-logo">

                <img
                  src={team.logoUrl}
                  alt={`${team.name} logo`}
                />

              </div>


              <div className="team-card-info">

                <h2>
                  {team.name}
                </h2>

                <span>
                  {team.country}
                </span>

              </div>


              <div className="team-card-details">

                <div>
                  <span>
                    Founded
                  </span>

                  <strong>
                    {team.founded || "—"}
                  </strong>
                </div>


                <div>
                  <span>
                    Stadium
                  </span>

                  <strong>
                    {team.venue?.name || "Unknown"}
                  </strong>
                </div>


                <div>
                  <span>
                    Capacity
                  </span>

                  <strong>
                    {team.venue?.capacity
                      ? team.venue.capacity.toLocaleString()
                      : "—"}
                  </strong>
                </div>

              </div>


              <Link
                to={`/teams/${team.id}`}
                className="view-team-button"
              >
                View Team
                <span>→</span>
              </Link>

            </article>
          ))}

        </section>
      )}

    </main>
  );
}


export default Teams;