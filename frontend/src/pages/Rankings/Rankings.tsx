import "./Rankings.css";

import {
  useEffect,
  useState,
} from "react";

import {
  Link as RouterLink,
} from "react-router";

import {
  getPlayerRankings,
  type PlayerRankingsResponse,
  type RankedFutBudPlayer,
} from "../../services/rankingService.ts";


type RankingLimit =
  25
  | 50
  | 100;


function initials(
  name: string
) {

  return name
    .split(" ")
    .filter(Boolean)
    .map(
      word => word[0]
    )
    .join("")
    .slice(0, 2)
    .toUpperCase();
}


function statusClass(
  status: string | null
) {

  if (!status) {
    return "";
  }

  return status
    .toLowerCase()
    .replaceAll(" ", "-");
}


function formatSeason(
  season: number
) {

  const nextYear =
    String(
      (season + 1) % 100
    ).padStart(
      2,
      "0"
    );

  return `${season}/${nextYear}`;
}


function PlayerAvatar({
  player,
}: {
  player: RankedFutBudPlayer;
}) {

  return (
    <div className="ranking-avatar">

      {player.photoUrl ? (

        <img
          src={player.photoUrl}
          alt=""
        />

      ) : (

        <span>
          {initials(player.name)}
        </span>

      )}

    </div>
  );
}


function PositionCard({
  title,
  players,
}: {
  title: string;
  players: RankedFutBudPlayer[];
}) {

  return (
    <section className="position-ranking-card">

      <div className="position-card-heading">

        <div>
          <span>
            FutBud Rating
          </span>

          <h2>
            {title}
          </h2>
        </div>

        <span className="position-card-count">
          Top {players.length}
        </span>

      </div>


      <div className="position-ranking-list">

        {players.map(
          (
            player,
            index
          ) => (

            <RouterLink
              to={`/players/${player.id}`}
              className="position-ranking-row"
              key={player.id}
            >

              <span className="position-rank">
                {index + 1}
              </span>


              <PlayerAvatar
                player={player}
              />


              <div className="position-player-info">

                <strong>
                  {player.name}
                </strong>

                <span>
                  {
                    player.archetype
                    || player.position
                    || "Player"
                  }
                </span>

              </div>


              <strong className="position-rating">
                {
                  player.rating !== null
                    ? player.rating.toFixed(1)
                    : "—"
                }
              </strong>

            </RouterLink>

          )
        )}

      </div>

    </section>
  );
}


function Rankings() {

  const [rankings, setRankings] =
    useState<PlayerRankingsResponse | null>(
      null
    );

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  const [limit, setLimit] =
    useState<RankingLimit>(25);

  const season = 2026;


  useEffect(() => {

    setLoading(true);
    setError(null);

    getPlayerRankings(
      season,
      limit
    )
      .then(
        data => {
          setRankings(data);
        }
      )
      .catch(
        error => {

          console.error(
            "Rankings error:",
            error
          );

          setError(
            error instanceof Error
              ? error.message
              : "Unable to load rankings."
          );
        }
      )
      .finally(
        () => {
          setLoading(false);
        }
      );

  }, [limit]);


  if (loading) {

    return (
      <main className="rankings-page">
        <div className="rankings-state">
          Loading FutBud rankings...
        </div>
      </main>
    );
  }


  if (
    error
    || !rankings
  ) {

    return (
      <main className="rankings-page">

        <div className="rankings-state error">
          <strong>
            Rankings unavailable
          </strong>

          <span>
            {
              error
              || "Unable to load FutBud rankings."
            }
          </span>
        </div>

      </main>
    );
  }


  return (
    <main className="rankings-page">

      {/* =========================================
          HEADER
      ========================================== */}

      <div className="rankings-heading">

        <div>

          <span className="rankings-kicker">
            FutBud Ratings
          </span>

          <h1>
            Player Power Rankings
          </h1>

          <p>
            FutBud's highest-rated players across the top five leagues.
          </p>

        </div>


        <div className="ranking-controls">

          <div className="ranking-season-chip">
            {formatSeason(rankings.season)}
          </div>

          <select
            value={limit}
            onChange={
              event =>
                setLimit(
                  Number(
                    event.target.value
                  ) as RankingLimit
                )
            }
            aria-label="Number of rankings to show"
          >
            <option value={25}>
              Top 25
            </option>

            <option value={50}>
              Top 50
            </option>

            <option value={100}>
              Top 100
            </option>
          </select>

        </div>

      </div>


      {/* =========================================
          OVERALL RANKINGS
      ========================================== */}

      <section className="ranking-card player-power-card">

        <div className="ranking-section-heading">

          <div>

            <p className="ranking-label">
              Overall
            </p>

            <h2>
              FutBud Player Rankings
            </h2>

          </div>


          <div className="ranking-method-note">
            Minimum {rankings.minimumMinutes} minutes
          </div>

        </div>


        <div className="player-ranking-table-wrap">

          <div className="player-ranking-table">

            <div className="player-ranking-row ranking-table-header">
              <span>#</span>
              <span>Player</span>
              <span>Play Style</span>
              <span>Rating</span>
              <span>Role Pct.</span>
              <span>Status</span>
            </div>


            {rankings.overall.map(
              player => (

                <RouterLink
                  to={`/players/${player.id}`}
                  className="player-ranking-row player-ranking-link"
                  key={player.id}
                >

                  <strong className="ranking-number">
                    {player.rank}
                  </strong>


                  <div className="ranked-player">

                    <PlayerAvatar
                      player={player}
                    />


                    <div className="ranked-player-info">

                      <strong>
                        {player.name}
                      </strong>

                      <div className="ranked-player-team">

                        {player.team?.logoUrl && (
                          <img
                            src={player.team.logoUrl}
                            alt=""
                          />
                        )}

                        <span>
                          {
                            player.team?.name
                            || "No club"
                          }
                        </span>

                        {player.league?.name && (
                          <span className="ranking-league-name">
                            {player.league.name}
                          </span>
                        )}

                      </div>

                    </div>

                  </div>


                  <div className="ranking-role">

                    <span className="ranking-position">
                      {
                        player.position
                        || "—"
                      }
                    </span>

                    <span className="ranking-archetype">
                      {
                        player.archetype
                        || "—"
                      }
                    </span>

                  </div>


                  <strong className="ranking-rating">
                    {
                      player.rating !== null
                        ? player.rating.toFixed(1)
                        : "—"
                    }
                  </strong>


                  <div className="ranking-percentile">

                    <strong>
                      {
                        player.percentile !== null
                          ? player.percentile.toFixed(1)
                          : "—"
                      }
                    </strong>

                    <span>
                      percentile
                    </span>

                  </div>


                  <span
                    className={
                      `ranking-status ${
                        statusClass(
                          player.status
                        )
                      }`
                    }
                  >
                    {
                      player.status
                      || "Unrated"
                    }
                  </span>

                </RouterLink>

              )
            )}

          </div>

        </div>

      </section>


      {/* =========================================
          TOP BY POSITION
      ========================================== */}

      <section className="position-section">

        <div className="rankings-subheading">

          <div>
            <span className="rankings-kicker">
              Position Leaders
            </span>

            <h2>
              Top by Position
            </h2>
          </div>

          <p>
            Highest-rated players in each broad FutBud position group.
          </p>

        </div>


        <div className="position-ranking-grid">

          <PositionCard
            title="Forwards"
            players={
              rankings
                .byPosition
                .forwards
            }
          />

          <PositionCard
            title="Midfielders"
            players={
              rankings
                .byPosition
                .midfielders
            }
          />

          <PositionCard
            title="Defenders"
            players={
              rankings
                .byPosition
                .defenders
            }
          />

        </div>

      </section>


      {/* =========================================
          RATING EXPLANATION
      ========================================== */}

      <section className="ranking-info-card">

        <div>
          <span className="rankings-kicker">
            FutBud Rating v1
          </span>

          <h2>
            Role-relative player evaluation
          </h2>
        </div>

        <p>
          Players are evaluated against historical players in the same
          FutBud play style. The rating combines role-specific performance
          metrics with a minutes reliability adjustment. Goalkeepers are not
          included in FutBud Rating v1.
        </p>

      </section>

    </main>
  );
}


export default Rankings;
