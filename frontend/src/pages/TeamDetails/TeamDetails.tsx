import "./TeamDetails.css";

import { useEffect, useState } from "react";
import { useParams } from "react-router";

import {
  getTeam,
  getTeamSquad,
} from "../../services/teamService";

import type {
  Team,
  SquadPlayer,
} from "../../services/teamService";


function TeamDetails() {
  const { teamId } = useParams();

  const [team, setTeam] =
    useState<Team | null>(null);

  const [squad, setSquad] =
    useState<SquadPlayer[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);


  useEffect(() => {

    if (!teamId) {
      setError("Team ID is missing.");
      setLoading(false);
      return;
    }

    const id = Number(teamId);

    if (Number.isNaN(id)) {
      setError("Invalid team ID.");
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    Promise.all([
      getTeam(id),
      getTeamSquad(id),
    ])
      .then(([teamData, squadData]) => {

        setTeam(teamData);
        setSquad(squadData);

      })
      .catch((error) => {

        console.error(
          "Error loading team:",
          error
        );

        setError(
          "Unable to load team."
        );

      })
      .finally(() => {
        setLoading(false);
      });

  }, [teamId]);


  if (loading) {
    return (
      <main className="team-details-page">
        <p>Loading team...</p>
      </main>
    );
  }


  if (error || !team) {
    return (
      <main className="team-details-page">

        <h1>
          Team not found
        </h1>

        <p>
          {error}
        </p>

      </main>
    );
  }


  return (
    <main className="team-details-page">

      {/* TEAM HERO */}

      <section className="team-hero">

        <div className="team-hero-main">

          <div className="team-crest">

            <img
              src={team.logoUrl}
              alt={`${team.name} logo`}
            />

          </div>


          <div className="team-hero-info">

            <span className="team-league-label">
              {team.league?.name || "League"}
            </span>

            <h1>
              {team.name}
            </h1>

            <p>
              {team.country}
            </p>

          </div>

        </div>


        <div className="team-basic-stats">

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

      </section>


      {/* STADIUM */}

      <section className="team-stadium-section">

        <div className="team-stadium-info">

          <h2>
            {team.venue?.name || "Stadium"}
          </h2>

          <p>
            {team.venue?.city || ""}
          </p>

        </div>


        {team.venue?.imageUrl && (

          <img
            src={team.venue.imageUrl}
            alt={team.venue.name}
          />

        )}

      </section>


      {/* SQUAD */}

      <section className="team-squad-section">

        <div className="team-section-heading">

          <div>

            <h2>
              Squad
            </h2>

            <p>
              {team.league?.season
                ? `${team.league.season}/${String(
                    team.league.season + 1
                  ).slice(-2)} Season`
                : "Current squad"}
            </p>

          </div>

          <span>
            {squad.length} Players
          </span>

        </div>


        <div className="team-squad-grid">

          {squad.map((player) => (

            <article
              className="squad-player-card"
              key={player.id}
            >

              <div className="squad-player-photo">

                {player.photoUrl ? (

                  <img
                    src={player.photoUrl}
                    alt={player.name}
                  />

                ) : (

                  <div className="squad-photo-placeholder">
                    ?
                  </div>

                )}

              </div>


              <div className="squad-player-info">

                <div className="squad-player-top">

                  <span className="squad-number">
                    {player.shirtNumber
                      ? `#${player.shirtNumber}`
                      : "—"}
                  </span>

                  <span className="squad-position">
                    {player.position || "Player"}
                  </span>

                </div>


                <h3>
                  {player.name}
                </h3>


                <p>
                  {player.nationality || ""}
                </p>

              </div>

            </article>

          ))}

        </div>

      </section>

    </main>
  );
}


export default TeamDetails;