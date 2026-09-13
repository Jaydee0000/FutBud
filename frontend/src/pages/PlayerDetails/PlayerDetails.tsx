import "./PlayerDetails.css";

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

  return (
    `${season}/${nextYear}`
  );
}

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  useParams,
} from "react-router";

import {
  getPlayerDashboard,
  type PlayerDashboard,
  type RecentPlayerMatch,
} from "../../services/playerDetailsService";


function calculateAge(
  birthDate: string | null
) {

  if (!birthDate) {
    return null;
  }

  const birth =
    new Date(birthDate);

  const today =
    new Date();

  let age =
    today.getFullYear()
    - birth.getFullYear();

  const monthDifference =
    today.getMonth()
    - birth.getMonth();

  if (
    monthDifference < 0
    ||
    (
      monthDifference === 0
      &&
      today.getDate()
      <
      birth.getDate()
    )
  ) {
    age--;
  }

  return age;
}


function formatMatchDate(
  date: string
) {

  return new Date(
    date
  ).toLocaleDateString(
    "en-US",
    {
      month: "short",
      day: "numeric",
    }
  );
}


function StatItem({
  label,
  value,
}: {
  label: string;
  value:
    | string
    | number;
}) {

  return (
    <div className="player-stat-item">

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>

    </div>
  );
}


function DetailedGroup({
  title,
  children,
}: {
  title: string;
  children:
    React.ReactNode;
}) {

  return (
    <section className="player-stat-group">

      <h3>
        {title}
      </h3>

      <div className="player-stat-group-list">

        {children}

      </div>

    </section>
  );
}


function resultClass(
  result: string | null
) {

  if (!result) {
    return "";
  }

  if (
    result.startsWith("W")
  ) {
    return "result-win";
  }

  if (
    result.startsWith("L")
  ) {
    return "result-loss";
  }

  return "result-draw";
}


function FormChart({
  matches,
  competitionName,
}: {
  matches:
    RecentPlayerMatch[];

  competitionName:
    string;
}) {

  const ordered =
    [...matches].reverse();

  const goals =
    ordered.map(
      match =>
        match.goals
    );

  const assists =
    ordered.map(
      match =>
        match.assists
    );

  const maxValue =
    Math.max(
      2,
      ...goals,
      ...assists,
    );


  function points(
    values: number[]
  ) {

    if (
      values.length === 0
    ) {
      return "";
    }

    if (
      values.length === 1
    ) {

      return (
        `50,${
          38
          -
          (
            values[0]
            / maxValue
          )
          * 28
        }`
      );

    }

    return values
      .map(
        (
          value,
          index
        ) => {

          const x =
            (
              index
              /
              (
                values.length
                - 1
              )
            )
            * 100;

          const y =
            38
            -
            (
              value
              / maxValue
            )
            * 28;

          return `${x},${y}`;

        }
      )
      .join(" ");
  }


  if (
    ordered.length === 0
  ) {

    return (
      <div className="player-empty-state">
        No  {competitionName} appearances yet.
      </div>
    );

  }


  return (
    <>

      <div className="form-legend">

        <span>
          <i className="goal-legend" />
          Goals
        </span>

        <span>
          <i className="assist-legend" />
          Assists
        </span>

      </div>


      <div className="form-chart">

        <svg
          viewBox="0 0 100 44"
          preserveAspectRatio="none"
          aria-label={
            `Goals and assists over the last ten ${competitionName} appearances`
            }
        >

          <line
            x1="0"
            y1="38"
            x2="100"
            y2="38"
            className="form-grid-line"
          />

          <line
            x1="0"
            y1="24"
            x2="100"
            y2="24"
            className="form-grid-line"
          />

          <line
            x1="0"
            y1="10"
            x2="100"
            y2="10"
            className="form-grid-line"
          />


          <polyline
            points={
              points(goals)
            }
            className="form-goals-line"
          />


          <polyline
            points={
              points(assists)
            }
            className="form-assists-line"
          />

        </svg>

      </div>


      <div className="form-opponents">

        {ordered.map(
          match => (

            <div
              key={match.id}
              className="form-opponent"
            >

              <img
                src={
                  match.opponent
                    .logoUrl
                }
                alt=""
              />

              <span>
                {
                  match.opponent
                    .name
                    .split(" ")[0]
                }
              </span>

            </div>

          )
        )}

      </div>

    </>
  );
}


function PlayerDetails() {

  const { playerId } =
    useParams();


  const [
    dashboard,
    setDashboard,
  ] =
    useState<
      PlayerDashboard | null
    >(null);


  const [
    loading,
    setLoading,
  ] =
    useState(true);


  const [
    error,
    setError,
  ] =
    useState<
      string | null
    >(null);


  useEffect(() => {

    const id =
      Number(playerId);


    if (
      !playerId
      ||
      Number.isNaN(id)
    ) {

      setError(
        "Invalid player."
      );

      setLoading(false);

      return;
    }


    setLoading(true);
    setError(null);


    getPlayerDashboard(id)
      .then(
        data => {

          setDashboard(
            data
          );

        }
      )
      .catch(
        error => {

          console.error(
            error
          );

          setError(
            "Unable to load player."
          );

        }
      )
      .finally(
        () => {

          setLoading(false);

        }
      );

  }, [playerId]);


  const age =
    useMemo(
      () =>
        calculateAge(
          dashboard
            ?.profile
            .birthDate
            ?? null
        ),
      [
        dashboard
          ?.profile
          .birthDate,
      ]
    );


  if (loading) {

    return (
      <main className="player-details-page">
        Loading player...
      </main>
    );

  }


  if (
    error
    ||
    !dashboard
  ) {

    return (
      <main className="player-details-page">

        <h1>
          Player unavailable
        </h1>

        <p>
          {error}
        </p>

      </main>
    );

  }


  const {
  profile,
  summary,
  detailed,
  futbud,
  recentMatches,
} = dashboard;

  const competitionName =
  profile.league?.name
  || "League";


const seasonLabel =
  formatSeason(
    profile.season
  );


  const goalkeeper =
    (
      profile.position
      ||
      profile.primaryPosition
      ||
      ""
    )
      .toLowerCase()
      .includes(
        "goal"
      );


  return (
    <main className="player-details-page">

      {/* =====================================
          PLAYER HEADER
      ====================================== */}

      <section className="player-profile-header">

        <div className="player-profile-photo">

          {profile.photoUrl ? (

            <img
              src={
                profile.photoUrl
              }
              alt={
                profile.name
              }
            />

          ) : (

            <div className="player-photo-placeholder">
              ?
            </div>

          )}

        </div>


        <div className="player-profile-main">

          <div className="player-name-row">

  <div className="player-name-block">

      <h1>
        {profile.name}
      </h1>

      <div className="player-subtitle">

        <span>
          {
            profile.nationality
            ||
            "Unknown nationality"
          }
        </span>

        <span>
          {
            profile.position
            ||
            profile.primaryPosition
            ||
            "Player"
          }
        </span>

        {profile.shirtNumber !== null && (

          <span>
            #{profile.shirtNumber}
          </span>

        )}

      </div>

    </div>


    <div className="futbud-rating-card">

      {futbud ? (
        <>

          <div className="futbud-rating-left">

            <span className="futbud-rating-label">
              FUTBUD RATING
            </span>

            <strong className="futbud-rating-number">
              {
                futbud.rating !== null
                  ? futbud.rating.toFixed(1)
                  : "—"
              }
            </strong>

          </div>


          <div className="futbud-rating-divider" />


          <div className="futbud-rating-details">

            <strong className="futbud-archetype">
              {futbud.archetype}
            </strong>

            <div className="futbud-rating-meta">

              <span>
                {futbud.status}
              </span>

              {futbud.percentile !== null && (

                <span>
                  {futbud.percentile.toFixed(1)}th percentile
                </span>

              )}

            </div>

          </div>

        </>
      ) : (

        <div className="futbud-unrated">

          <span className="futbud-rating-label">
            FUTBUD RATING
          </span>

          <strong>
            Not yet rated
          </strong>

          <small>
            180 minutes required
          </small>

        </div>

      )}

    </div>


    {profile.team && (

      <img
        className="player-club-logo"
        src={profile.team.logoUrl}
        alt={profile.team.name}
      />

    )}

  </div>


          <div className="player-profile-info">

            <div>

              <span>
                Club
              </span>

              <strong>
                {
                  profile.team
                    ?.name
                  ||
                  "Unknown"
                }
              </strong>

            </div>


            <div>

              <span>
                Age
              </span>

              <strong>
                {
                  age
                  ?? "—"
                }
              </strong>

            </div>


            <div>

              <span>
                Height
              </span>

              <strong>
                {
                  profile.height
                  || "—"
                }
              </strong>

            </div>


            <div>

              <span>
                Weight
              </span>

              <strong>
                {
                  profile.weight
                  || "—"
                }
              </strong>

            </div>


            <div>

              <span>
                Competition
              </span>

              <strong>
                {competitionName}
                </strong>

            </div>

          </div>

        </div>

      </section>


      {/* =====================================
          SUMMARY + FORM
      ====================================== */}

      <section className="player-dashboard-top">

        <section className="player-panel">

          <div className="player-panel-heading">

            <div>

              <span className="player-eyebrow">
                {competitionName}
                </span>

              <h2>
                Season Summary
              </h2>

            </div>


            <span className="season-label">
            {seasonLabel}
            </span>

          </div>


          <div className="season-summary-grid">

            <div>
              <strong>
                {
                  summary
                    .appearances
                }
              </strong>
              <span>
                Appearances
              </span>
            </div>

            <div>
              <strong>
                {
                  summary
                    .minutes
                    .toLocaleString()
                }
              </strong>
              <span>
                Minutes
              </span>
            </div>

            <div>
              <strong>
                {
                  summary
                    .goals
                }
              </strong>
              <span>
                Goals
              </span>
            </div>

            <div>
              <strong>
                {
                  summary
                    .assists
                }
              </strong>
              <span>
                Assists
              </span>
            </div>

            <div>
              <strong>
                {
                  summary
                    .avgRating
                    .toFixed(2)
                }
              </strong>
              <span>
                Avg Rating
              </span>
            </div>

            <div>
              <strong>
                {
                  summary
                    .shots
                }
              </strong>
              <span>
                Shots
              </span>
            </div>

            <div>
              <strong>
                {
                  summary
                    .shotsOnTarget
                }
              </strong>
              <span>
                On Target
              </span>
            </div>

            <div>
              <strong>
                {
                  summary
                    .keyPasses
                }
              </strong>
              <span>
                Key Passes
              </span>
            </div>

          </div>

        </section>


        <section className="player-panel">

          <div className="player-panel-heading">

            <div>

              <span className="player-eyebrow">
                {competitionName}
                </span>

              <h2>
                Form — Last 10
              </h2>

            </div>

          </div>


          <FormChart
            matches={recentMatches}
            competitionName={
                competitionName
            }
            />

        </section>

      </section>


      {/* =====================================
          DETAILED STATS
      ====================================== */}

      <section className="player-panel detailed-stats-panel">

        <div className="player-panel-heading">

          <div>

            <span className="player-eyebrow">
            {competitionName} {seasonLabel}
            </span>

            <h2>
              Detailed Stats
            </h2>

          </div>

        </div>


        <div className="detailed-stats-grid">

          <DetailedGroup
            title="Attacking"
          >

            <StatItem
              label="Goals"
              value={
                detailed.attacking
                  .goals
              }
            />

            <StatItem
              label="Assists"
              value={
                detailed.attacking
                  .assists
              }
            />

            <StatItem
              label="Shots"
              value={
                detailed.attacking
                  .shots
              }
            />

            <StatItem
              label="Shots on Target"
              value={
                detailed.attacking
                  .shotsOnTarget
              }
            />

            <StatItem
              label="Offsides"
              value={
                detailed.attacking
                  .offsides
              }
            />

            <StatItem
              label="Penalties Scored"
              value={
                detailed.attacking
                  .penaltiesScored
              }
            />

            <StatItem
              label="Penalties Missed"
              value={
                detailed.attacking
                  .penaltiesMissed
              }
            />

          </DetailedGroup>


          <DetailedGroup
            title="Passing"
          >

            <StatItem
              label="Total Passes"
              value={
                detailed.passing
                  .passes
                  .toLocaleString()
              }
            />

            <StatItem
              label="Pass Accuracy"
              value={
                `${
                  detailed.passing
                    .passAccuracy
                }%`
              }
            />

            <StatItem
              label="Key Passes"
              value={
                detailed.passing
                  .keyPasses
              }
            />

          </DetailedGroup>


          <DetailedGroup
            title="Dribbling"
          >

            <StatItem
              label="Attempted"
              value={
                detailed.dribbling
                  .attempted
              }
            />

            <StatItem
              label="Successful"
              value={
                detailed.dribbling
                  .successful
              }
            />

            <StatItem
              label="Success Rate"
              value={
                `${
                  detailed.dribbling
                    .successRate
                }%`
              }
            />

            <StatItem
              label="Dribbled Past"
              value={
                detailed.dribbling
                  .dribbledPast
              }
            />

          </DetailedGroup>


          <DetailedGroup
            title="Defending"
          >

            <StatItem
              label="Tackles"
              value={
                detailed.defending
                  .tackles
              }
            />

            <StatItem
              label="Interceptions"
              value={
                detailed.defending
                  .interceptions
              }
            />

            <StatItem
              label="Blocks"
              value={
                detailed.defending
                  .blocks
              }
            />

            <StatItem
              label="Duels"
              value={
                detailed.defending
                  .duels
              }
            />

            <StatItem
              label="Duels Won"
              value={
                detailed.defending
                  .duelsWon
              }
            />

            <StatItem
              label="Duel Win Rate"
              value={
                `${
                  detailed.defending
                    .duelWinRate
                }%`
              }
            />

          </DetailedGroup>


          <DetailedGroup
            title="Discipline"
          >

            <StatItem
              label="Fouls Drawn"
              value={
                detailed.discipline
                  .foulsDrawn
              }
            />

            <StatItem
              label="Fouls Committed"
              value={
                detailed.discipline
                  .foulsCommitted
              }
            />

            <StatItem
              label="Yellow Cards"
              value={
                detailed.discipline
                  .yellowCards
              }
            />

            <StatItem
              label="Red Cards"
              value={
                detailed.discipline
                  .redCards
              }
            />

          </DetailedGroup>


          {goalkeeper && (

            <DetailedGroup
              title="Goalkeeping"
            >

              <StatItem
                label="Saves"
                value={
                  detailed
                    .goalkeeping
                    .saves
                }
              />

              <StatItem
                label="Goals Conceded"
                value={
                  detailed
                    .goalkeeping
                    .goalsConceded
                }
              />

              <StatItem
                label="Penalties Saved"
                value={
                  detailed
                    .goalkeeping
                    .penaltiesSaved
                }
              />

            </DetailedGroup>

          )}

        </div>

      </section>


      {/* =====================================
          RECENT MATCHES
      ====================================== */}

      <section className="player-panel recent-matches-panel">

        <div className="player-panel-heading">

          <div>

            <span className="player-eyebrow">
            {competitionName}
            </span>

            <h2>
              Recent Matches
            </h2>

          </div>

        </div>


        <div className="recent-player-table">

          <div className="recent-player-row recent-player-heading">

            <span>
              Date
            </span>

            <span>
              Opponent
            </span>

            <span>
              Min
            </span>

            <span>
              G
            </span>

            <span>
              A
            </span>

            <span>
              Shots
            </span>

            <span>
              SOT
            </span>

            <span>
              KP
            </span>

            <span>
              Rating
            </span>

            <span>
              Result
            </span>

          </div>


          {recentMatches.map(
            match => (

              <div
                className="recent-player-row"
                key={match.id}
              >

                <span>
                  {
                    formatMatchDate(
                      match.date
                    )
                  }
                </span>


                <div className="recent-opponent">

                  <img
                    src={
                      match.opponent
                        .logoUrl
                    }
                    alt=""
                  />

                  <strong>
                    {
                      match.opponent
                        .name
                    }
                  </strong>

                </div>


                <span>
                  {match.minutes}
                </span>

                <strong>
                  {match.goals}
                </strong>

                <strong>
                  {match.assists}
                </strong>

                <span>
                  {match.shots}
                </span>

                <span>
                  {
                    match
                      .shotsOnTarget
                  }
                </span>

                <span>
                  {
                    match
                      .keyPasses
                  }
                </span>

                <strong>
                  {
                    match.rating
                    !== null
                      ?
                        match.rating
                          .toFixed(1)
                      :
                        "—"
                  }
                </strong>

                <span
                  className={
                    `recent-result ${
                      resultClass(
                        match.result
                      )
                    }`
                  }
                >
                  {
                    match.result
                    || "—"
                  }
                </span>

              </div>

            )
          )}

        </div>

      </section>

    </main>
  );
}


export default PlayerDetails;