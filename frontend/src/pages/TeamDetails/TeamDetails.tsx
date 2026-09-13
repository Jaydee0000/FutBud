import "./TeamDetails.css";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Link as RouterLink,
  useLocation,
  useParams,
} from "react-router";

import {
  getTeamDashboard,
  type TeamDashboard,
  type TeamDashboardMatch,
  type TeamLeader,
  type TeamSquadPlayer,
} from "../../services/teamDetailsService";


type TeamSection =
  | "overview"
  | "squad"
  | "results"
  | "stats";


type ResultFilter =
  | "all"
  | "completed"
  | "upcoming";


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


function formatDate(
  dateString: string
) {

  return new Date(
    dateString
  ).toLocaleDateString(
    "en-US",
    {
      weekday: "short",
      month: "short",
      day: "numeric",
    }
  );
}


function formatLongDate(
  dateString: string
) {

  return new Date(
    dateString
  ).toLocaleDateString(
    "en-US",
    {
      weekday: "long",
      month: "long",
      day: "numeric",
    }
  );
}


function formatTime(
  dateString: string
) {

  return new Date(
    dateString
  ).toLocaleTimeString(
    "en-US",
    {
      hour: "numeric",
      minute: "2-digit",
    }
  );
}


function getMonthKey(
  dateString: string
) {

  return new Date(
    dateString
  ).toLocaleDateString(
    "en-US",
    {
      month: "long",
      year: "numeric",
    }
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
    return "team-result-win";
  }

  if (
    result.startsWith("L")
  ) {
    return "team-result-loss";
  }

  return "team-result-draw";
}


function positionGroup(
  position: string | null
) {

  const value =
    (
      position
      || ""
    ).toLowerCase();


  if (
    value.includes("goal")
    ||
    value === "g"
  ) {
    return "Goalkeepers";
  }


  if (
    value.includes("def")
    ||
    value === "d"
  ) {
    return "Defenders";
  }


  if (
    value.includes("mid")
    ||
    value === "m"
  ) {
    return "Midfielders";
  }


  if (
    value.includes("att")
    ||
    value.includes("forward")
    ||
    value.includes("striker")
    ||
    value === "f"
  ) {
    return "Forwards";
  }


  return "Other";
}


function SnapshotItem({
  label,
  value,
}: {
  label: string;
  value:
    string
    | number;
}) {

  return (
    <div className="team-snapshot-item">

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>

    </div>
  );
}


function TeamLeaderCard({
  title,
  unit,
  leader,
}: {
  title: string;
  unit: string;
  leader:
    TeamLeader
    | null;
}) {

  return (
    <section className="team-leader-card">

      <div className="team-leader-card-title">
        {title}
      </div>


      {!leader ? (

        <div className="team-empty-small">
          No data yet.
        </div>

      ) : (

        <RouterLink
          to={
            `/players/${leader.player.id}`
          }
          className="team-leader-player"
        >

          <div className="team-leader-photo">

            {leader.player.photoUrl ? (

              <img
                src={
                  leader.player.photoUrl
                }
                alt={
                  leader.player.name
                }
              />

            ) : (

              <span>
                ?
              </span>

            )}

          </div>


          <div className="team-leader-info">

            <strong>
              {leader.player.name}
            </strong>

            <span>
              {
                leader.player.position
                || "Player"
              }
            </span>

          </div>


          <div className="team-leader-number">

            <strong>
              {leader.value}
            </strong>

            <span>
              {unit}
            </span>

          </div>

        </RouterLink>

      )}

    </section>
  );
}


function MatchRow({
  match,
}: {
  match:
    TeamDashboardMatch;
}) {

  const completed =
    [
      "FT",
      "AET",
      "PEN",
    ].includes(
      match.status.short
    );


  return (
    <div className="team-match-row">

      <div className="team-match-date">

        <strong>
          {formatDate(match.date)}
        </strong>

        <span>
          {
            match.homeAway === "H"
              ? "Home"
              : "Away"
          }
        </span>

      </div>


      <div className="team-match-team team-match-home">

        <span>
          {match.homeTeam.name}
        </span>

        <img
          src={
            match.homeTeam.logoUrl
          }
          alt=""
        />

      </div>


      <div className="team-match-score">

        {completed ? (

          <>
            <strong>
              {
                match.homeGoals
                ?? 0
              }
              {" - "}
              {
                match.awayGoals
                ?? 0
              }
            </strong>

            <span>
              {
                match.status.short
              }
            </span>
          </>

        ) : (

          <>
            <strong>
              {formatTime(match.date)}
            </strong>

            <span>
              {
                match.status.short
              }
            </span>
          </>

        )}

      </div>


      <div className="team-match-team">

        <img
          src={
            match.awayTeam.logoUrl
          }
          alt=""
        />

        <span>
          {match.awayTeam.name}
        </span>

      </div>


      <div
        className={
          `team-match-result ${
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
      </div>

    </div>
  );
}


function TeamOverview({
  dashboard,
}: {
  dashboard:
    TeamDashboard;
}) {

  const {
    team,
    overview,
  } = dashboard;


  const standing =
    overview.standing;


  return (
    <div className="team-overview-body">

      {/* ====================================
          SEASON SNAPSHOT
      ===================================== */}

      <section className="team-panel">

        <div className="team-panel-heading">

          <div>

            <span className="team-eyebrow">
              {team.league.name}
            </span>

            <h2>
              Season Snapshot
            </h2>

          </div>


          <span className="team-season-chip">
            {
              formatSeason(
                team.season
              )
            }
          </span>

        </div>


        <div className="team-snapshot-grid">

          <SnapshotItem
            label="Position"
            value={
              standing
                ? `#${standing.rank}`
                : "—"
            }
          />


          <SnapshotItem
            label="Points"
            value={
              standing?.points
              ?? "—"
            }
          />


          <SnapshotItem
            label="Record"
            value={
              standing
                ? `${standing.wins}-${standing.draws}-${standing.losses}`
                : "—"
            }
          />


          <SnapshotItem
            label="+/-"
            value={
              standing
                ? `${standing.goalsFor}/${standing.goalsAgainst}`
                : "—"
            }
          />


          <SnapshotItem
            label="GD"
            value={
              standing
                ? `${
                    standing
                      .goalDifference > 0
                      ? "+"
                      : ""
                  }${standing.goalDifference}`
                : "—"
            }
          />


          <SnapshotItem
            label="Played"
            value={
              standing?.played
              ?? "—"
            }
          />

        </div>

      </section>


      {/* ====================================
          NEXT + RECENT + TABLE CONTEXT
      ===================================== */}

      <section className="team-overview-grid">

        {/* NEXT MATCH */}

        <section className="team-panel team-next-match">

          <div className="team-panel-heading">

            <div>

              <span className="team-eyebrow">
                Upcoming
              </span>

              <h2>
                Next Match
              </h2>

            </div>

          </div>


          {!overview.nextMatch ? (

            <div className="team-empty-state">
              No upcoming match.
            </div>

          ) : (

            <div className="next-match-content">

              <div className="next-match-date">

                <strong>
                  {
                    formatLongDate(
                      overview
                        .nextMatch
                        .date
                    )
                  }
                </strong>

                <span>
                  {
                    formatTime(
                      overview
                        .nextMatch
                        .date
                    )
                  }
                </span>

              </div>


              <div className="next-match-clubs">

                <RouterLink
                  to={
                    `/teams/${
                      overview
                        .nextMatch
                        .homeTeam
                        .id
                    }`
                  }
                  className="next-club"
                >

                  <img
                    src={
                      overview
                        .nextMatch
                        .homeTeam
                        .logoUrl
                    }
                    alt=""
                  />

                  <strong>
                    {
                      overview
                        .nextMatch
                        .homeTeam
                        .name
                    }
                  </strong>

                </RouterLink>


                <div className="next-match-vs">
                  VS
                </div>


                <RouterLink
                  to={
                    `/teams/${
                      overview
                        .nextMatch
                        .awayTeam
                        .id
                    }`
                  }
                  className="next-club"
                >

                  <img
                    src={
                      overview
                        .nextMatch
                        .awayTeam
                        .logoUrl
                    }
                    alt=""
                  />

                  <strong>
                    {
                      overview
                        .nextMatch
                        .awayTeam
                        .name
                    }
                  </strong>

                </RouterLink>

              </div>

            </div>

          )}

        </section>


        {/* RECENT RESULTS */}

        <section className="team-panel">

          <div className="team-panel-heading">

            <div>

              <span className="team-eyebrow">
                Form
              </span>

              <h2>
                Recent Results
              </h2>

            </div>

          </div>


          <div className="overview-results-list">

            {
              overview
                .recentResults
                .length === 0
              ? (

                <div className="team-empty-state">
                  No completed matches yet.
                </div>

              )
              : (

                overview
                  .recentResults
                  .map(
                    match => (

                      <div
                        className="overview-result-row"
                        key={match.id}
                      >

                        <img
                          src={
                            match
                              .opponent
                              .logoUrl
                          }
                          alt=""
                        />


                        <div className="overview-result-info">

                          <strong>
                            {
                              match
                                .opponent
                                .name
                            }
                          </strong>

                          <span>
                            {
                              formatDate(
                                match.date
                              )
                            }
                          </span>

                        </div>


                        <span
                          className={
                            `overview-result-score ${
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
                  )

              )
            }

          </div>

        </section>


        {/* LEAGUE CONTEXT */}

        <section className="team-panel">

          <div className="team-panel-heading">

            <div>

              <span className="team-eyebrow">
                {team.league.name}
              </span>

              <h2>
                League Position
              </h2>

            </div>


            <RouterLink
              to={
                `/leagues/${team.league.id}`
              }
              className="team-panel-link"
            >
              Full Table
            </RouterLink>

          </div>


          <div className="team-context-table">

            <div className="team-context-row team-context-header">

              <span>#</span>
              <span>Team</span>
              <span>P</span>
              <span>GD</span>
              <span>PTS</span>

            </div>


            {
              overview
                .leagueContext
                .map(
                  item => (

                    <RouterLink
                      to={
                        `/teams/${item.team.id}`
                      }
                      className={
                        `team-context-row ${
                          item.team.id
                          === team.id
                            ? "current-team"
                            : ""
                        }`
                      }
                      key={
                        item.team.id
                      }
                    >

                      <span>
                        {item.rank}
                      </span>


                      <div className="team-context-name">

                        <img
                          src={
                            item
                              .team
                              .logoUrl
                          }
                          alt=""
                        />

                        <strong>
                          {
                            item
                              .team
                              .name
                          }
                        </strong>

                      </div>


                      <span>
                        {item.played}
                      </span>


                      <span>
                        {
                          item
                            .goalDifference > 0
                            ? "+"
                            : ""
                        }
                        {
                          item
                            .goalDifference
                        }
                      </span>


                      <strong>
                        {item.points}
                      </strong>

                    </RouterLink>

                  )
                )
            }

          </div>

        </section>

      </section>


      {/* ====================================
          TEAM LEADERS
      ===================================== */}

      <section className="team-overview-leaders">

        <TeamLeaderCard
          title="Top Goalscorer"
          unit="Goals"
          leader={
            overview
              .leaders
              .goals
          }
        />


        <TeamLeaderCard
          title="Top Assister"
          unit="Assists"
          leader={
            overview
              .leaders
              .assists
          }
        />


        <TeamLeaderCard
          title="Most Key Passes"
          unit="Key Passes"
          leader={
            overview
              .leaders
              .keyPasses
          }
        />

      </section>

    </div>
  );
}


function TeamSquad({
  squad,
}: {
  squad:
    TeamSquadPlayer[];
}) {

  const groupedPlayers =
    useMemo(
      () => {

        const groups:
          Record<
            string,
            TeamSquadPlayer[]
          > = {
            Goalkeepers: [],
            Defenders: [],
            Midfielders: [],
            Forwards: [],
            Other: [],
          };


        squad.forEach(
          player => {

            const group =
              positionGroup(
                player.position
              );

            groups[group].push(
              player
            );

          }
        );


        return groups;

      },
      [squad]
    );


  const sections = [
    "Goalkeepers",
    "Defenders",
    "Midfielders",
    "Forwards",
    "Other",
  ];


  return (
    <div className="team-squad-body">

      <div className="team-section-intro">

        <div>

          <span className="team-eyebrow">
            Current Season
          </span>

          <h2>
            Matchday Squad
          </h2>

        </div>


        <p>
          Players shown have either been
          selected in a matchday squad this
          season or are currently classified
          as injured.
        </p>

      </div>


      {
        sections.map(
          section => {

            const players =
              groupedPlayers[
                section
              ];


            if (
              players.length === 0
            ) {
              return null;
            }


            return (

              <section
                className="team-panel squad-position-section"
                key={section}
              >

                <div className="team-panel-heading">

                  <h2>
                    {section}
                  </h2>

                  <span className="squad-count">
                    {
                      players.length
                    }{" "}
                    players
                  </span>

                </div>


                <div className="squad-table">

                  <div className="squad-row squad-header">

                    <span>Player</span>
                    <span>FutBud</span>
                    <span>#</span>
                    <span>Pos</span>
                    <span>Squads</span>
                    <span>Apps</span>
                    <span>Starts</span>
                    <span>Min</span>
                    <span>G</span>
                    <span>A</span>
                    <span>Status</span>

                  </div>


                  {
                    players.map(
                      player => (

                        <RouterLink
                          to={
                            `/players/${
                              player
                                .player
                                .id
                            }`
                          }
                          className="squad-row squad-player-row"
                          key={
                            player
                              .player
                              .id
                          }
                        >

                          <div className="squad-player">

                            <div className="squad-player-photo">

                              {
                                player
                                  .player
                                  .photoUrl
                                ? (

                                  <img
                                    src={
                                      player
                                        .player
                                        .photoUrl
                                    }
                                    alt=""
                                  />

                                )
                                : (

                                  <span>
                                    ?
                                  </span>

                                )
                              }

                            </div>


                            <div>

                              <strong>
                                {
                                  player
                                    .player
                                    .name
                                }
                              </strong>

                              <span>
                                {
                                  player
                                    .player
                                    .nationality
                                  || ""
                                }
                              </span>

                            </div>

                          </div>


                          <div className="squad-rating-slot">
                            {
                              player.futbudRating !== null
                              && (
                                <span className="squad-futbud-rating">
                                  {player.futbudRating.toFixed(1)}
                                </span>
                              )
                            }
                          </div>


                          <span>
                            {
                              player
                                .shirtNumber
                              ?? "—"
                            }
                          </span>


                          <span>
                            {
                              player
                                .position
                              || "—"
                            }
                          </span>


                          <span>
                            {
                              player
                                .matchdaySelections
                            }
                          </span>


                          <span>
                            {
                              player
                                .appearances
                            }
                          </span>


                          <span>
                            {
                              player
                                .starts
                            }
                          </span>


                          <span>
                            {
                              player
                                .minutes
                                .toLocaleString()
                            }
                          </span>


                          <strong>
                            {
                              player
                                .goals
                            }
                          </strong>


                          <strong>
                            {
                              player
                                .assists
                            }
                          </strong>


                          <span
                            className={
                              player
                                .injured
                                ? "squad-status injured"
                                : "squad-status available"
                            }
                          >
                            {
                              player
                                .injured
                                ? "Injured"
                                : "Available"
                            }
                          </span>

                        </RouterLink>

                      )
                    )
                  }

                </div>

              </section>

            );

          }
        )
      }


      {
        squad.length === 0
        && (

          <div className="team-empty-state large">
            No eligible squad players have
            been recorded yet.
          </div>

        )
      }

    </div>
  );
}


function TeamResults({
  dashboard,
}: {
  dashboard:
    TeamDashboard;
}) {

  const [
    filter,
    setFilter,
  ] =
    useState<ResultFilter>(
      "all"
    );


  const {
    results,
  } = dashboard;


  const filteredMatches =
    useMemo(
      () => {

        if (
          filter === "all"
        ) {
          return results.matches;
        }


        const finished = [
          "FT",
          "AET",
          "PEN",
        ];


        if (
          filter === "completed"
        ) {

          return results
            .matches
            .filter(
              match =>
                finished.includes(
                  match
                    .status
                    .short
                )
            );

        }


        return results
          .matches
          .filter(
            match =>
              !finished.includes(
                match
                  .status
                  .short
              )
          );

      },
      [
        filter,
        results.matches,
      ]
    );


  const groupedMatches =
    useMemo(
      () => {

        const groups =
          new Map<
            string,
            TeamDashboardMatch[]
          >();


        filteredMatches.forEach(
          match => {

            const month =
              getMonthKey(
                match.date
              );


            if (
              !groups.has(month)
            ) {
              groups.set(
                month,
                []
              );
            }


            groups
              .get(month)!
              .push(match);

          }
        );


        return Array.from(
          groups.entries()
        );

      },
      [filteredMatches]
    );


  return (
    <div className="team-results-body">

      <section className="team-panel">

        <div className="results-summary">

          <SnapshotItem
            label="Played"
            value={
              results
                .record
                .played
            }
          />

          <SnapshotItem
            label="Wins"
            value={
              results
                .record
                .wins
            }
          />

          <SnapshotItem
            label="Draws"
            value={
              results
                .record
                .draws
            }
          />

          <SnapshotItem
            label="Losses"
            value={
              results
                .record
                .losses
            }
          />

          <SnapshotItem
            label="+/-"
            value={
              `${
                results
                  .record
                  .goalsFor
              }/${
                results
                  .record
                  .goalsAgainst
              }`
            }
          />

        </div>

      </section>


      <div className="results-toolbar">

        <div>

          <span className="team-eyebrow">
            Season Schedule
          </span>

          <h2>
            Results & Fixtures
          </h2>

        </div>


        <div className="results-filters">

          {(
            [
              "all",
              "completed",
              "upcoming",
            ] as ResultFilter[]
          ).map(
            option => (

              <button
                type="button"
                key={option}
                onClick={
                  () =>
                    setFilter(
                      option
                    )
                }
                className={
                  filter === option
                    ? "active"
                    : ""
                }
              >
                {
                  option
                    .charAt(0)
                    .toUpperCase()
                  +
                  option.slice(1)
                }
              </button>

            )
          )}

        </div>

      </div>


      {
        groupedMatches
          .length === 0
        ? (

          <div className="team-empty-state large">
            No matches found.
          </div>

        )
        : (

          groupedMatches.map(
            ([
              month,
              matches,
            ]) => (

              <section
                className="team-panel results-month"
                key={month}
              >

                <div className="results-month-title">
                  {month}
                </div>


                <div className="team-match-list">

                  {
                    matches.map(
                      match => (

                        <MatchRow
                          match={match}
                          key={
                            match.id
                          }
                        />

                      )
                    )
                  }

                </div>

              </section>

            )
          )

        )
      }

    </div>
  );
}


function StatRow({
  label,
  value,
}: {
  label: string;
  value:
    string
    | number;
}) {

  return (
    <div className="team-stat-row">

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>

    </div>
  );
}


function ContributorList({
  title,
  unit,
  leaders,
}: {
  title: string;
  unit: string;
  leaders:
    TeamLeader[];
}) {

  return (
    <section className="team-panel contributor-panel">

      <div className="team-panel-heading">

        <h2>
          {title}
        </h2>

      </div>


      <div className="contributor-list">

        {
          leaders.length === 0
          ? (

            <div className="team-empty-small">
              No data.
            </div>

          )
          : (

            leaders.map(
              (
                leader,
                index
              ) => (

                <RouterLink
                  to={
                    `/players/${
                      leader
                        .player
                        .id
                    }`
                  }
                  className="contributor-row"
                  key={
                    leader
                      .player
                      .id
                  }
                >

                  <span className="contributor-rank">
                    {index + 1}
                  </span>


                  <div className="contributor-photo">

                    {
                      leader
                        .player
                        .photoUrl
                      ? (

                        <img
                          src={
                            leader
                              .player
                              .photoUrl
                          }
                          alt=""
                        />

                      )
                      : (

                        <span>
                          ?
                        </span>

                      )
                    }

                  </div>


                  <div className="contributor-info">

                    <strong>
                      {
                        leader
                          .player
                          .name
                      }
                    </strong>

                    <span>
                      {
                        leader
                          .player
                          .position
                        || ""
                      }
                    </span>

                  </div>


                  <div className="contributor-value">

                    <strong>
                      {leader.value}
                    </strong>

                    <span>
                      {unit}
                    </span>

                  </div>

                </RouterLink>

              )
            )

          )
        }

      </div>

    </section>
  );
}


function TeamStats({
  dashboard,
}: {
  dashboard:
    TeamDashboard;
}) {

  const {
    team,
    stats,
  } = dashboard;


  return (
    <div className="team-stats-body">

      <div className="team-section-intro">

        <div>

          <span className="team-eyebrow">
            {team.league.name}
          </span>

          <h2>
            Team Statistics
          </h2>

        </div>


        <p>
          Statistics reflect the current
          domestic league season only.
        </p>

      </div>


      {/* TOP NUMBERS */}

      <section className="team-panel">

        <div className="team-stat-highlight-grid">

          <SnapshotItem
            label="Goals"
            value={
              stats
                .attacking
                .goals
            }
          />


          <SnapshotItem
            label="Goals / Match"
            value={
              stats
                .attacking
                .goalsPerGame
            }
          />


          <SnapshotItem
            label="Conceded"
            value={
              stats
                .defending
                .goalsAgainst
            }
          />


          <SnapshotItem
            label="Shots / Match"
            value={
              stats
                .attacking
                .shotsPerGame
            }
          />


          <SnapshotItem
            label="Possession"
            value={
              `${
                stats
                  .passing
                  .possession
              }%`
            }
          />


          <SnapshotItem
            label="Pass Accuracy"
            value={
              `${
                stats
                  .passing
                  .passAccuracy
              }%`
            }
          />

        </div>

      </section>


      {/* DETAILED BOXES */}

      <section className="team-stat-groups">

        <section className="team-panel">

          <div className="team-panel-heading">
            <h2>
              Attacking
            </h2>
          </div>


          <div className="team-stat-list">

            <StatRow
              label="Goals"
              value={
                stats
                  .attacking
                  .goals
              }
            />

            <StatRow
              label="Goals / Match"
              value={
                stats
                  .attacking
                  .goalsPerGame
              }
            />

            <StatRow
              label="Total Shots"
              value={
                stats
                  .attacking
                  .shots
              }
            />

            <StatRow
              label="Shots / Match"
              value={
                stats
                  .attacking
                  .shotsPerGame
              }
            />

            <StatRow
              label="Shots on Target"
              value={
                stats
                  .attacking
                  .shotsOnTarget
              }
            />

            <StatRow
              label="Shots off Target"
              value={
                stats
                  .attacking
                  .shotsOffTarget
              }
            />

            <StatRow
              label="Blocked Shots"
              value={
                stats
                  .attacking
                  .blockedShots
              }
            />

            <StatRow
              label="Inside Box"
              value={
                stats
                  .attacking
                  .shotsInsideBox
              }
            />

            <StatRow
              label="Outside Box"
              value={
                stats
                  .attacking
                  .shotsOutsideBox
              }
            />

            <StatRow
              label="Corners"
              value={
                stats
                  .attacking
                  .corners
              }
            />

            <StatRow
              label="Offsides"
              value={
                stats
                  .attacking
                  .offsides
              }
            />

          </div>

        </section>


        <section className="team-panel">

          <div className="team-panel-heading">
            <h2>
              Passing
            </h2>
          </div>


          <div className="team-stat-list">

            <StatRow
              label="Possession"
              value={
                `${
                  stats
                    .passing
                    .possession
                }%`
              }
            />

            <StatRow
              label="Total Passes"
              value={
                stats
                  .passing
                  .passes
                  .toLocaleString()
              }
            />

            <StatRow
              label="Passes / Match"
              value={
                stats
                  .passing
                  .passesPerGame
              }
            />

            <StatRow
              label="Accurate Passes"
              value={
                stats
                  .passing
                  .accuratePasses
                  .toLocaleString()
              }
            />

            <StatRow
              label="Pass Accuracy"
              value={
                `${
                  stats
                    .passing
                    .passAccuracy
                }%`
              }
            />

          </div>

        </section>


        <section className="team-panel">

          <div className="team-panel-heading">
            <h2>
              Defending
            </h2>
          </div>


          <div className="team-stat-list">

            <StatRow
              label="Goals Conceded"
              value={
                stats
                  .defending
                  .goalsAgainst
              }
            />

            <StatRow
              label="Conceded / Match"
              value={
                stats
                  .defending
                  .goalsAgainstPerGame
              }
            />

            <StatRow
              label="Clean Sheets"
              value={
                stats
                  .defending
                  .cleanSheets
              }
            />

            <StatRow
              label="Goalkeeper Saves"
              value={
                stats
                  .defending
                  .goalkeeperSaves
              }
            />

            <StatRow
              label="Saves / Match"
              value={
                stats
                  .defending
                  .savesPerGame
              }
            />

          </div>

        </section>


        <section className="team-panel">

          <div className="team-panel-heading">
            <h2>
              Discipline
            </h2>
          </div>


          <div className="team-stat-list">

            <StatRow
              label="Fouls"
              value={
                stats
                  .discipline
                  .fouls
              }
            />

            <StatRow
              label="Fouls / Match"
              value={
                stats
                  .discipline
                  .foulsPerGame
              }
            />

            <StatRow
              label="Yellow Cards"
              value={
                stats
                  .discipline
                  .yellowCards
              }
            />

            <StatRow
              label="Red Cards"
              value={
                stats
                  .discipline
                  .redCards
              }
            />

          </div>

        </section>

      </section>


      {/* CONTRIBUTORS */}

      <section className="team-contributors-grid">

        <ContributorList
          title="Top Goalscorers"
          unit="Goals"
          leaders={
            stats
              .contributors
              .goals
          }
        />


        <ContributorList
          title="Top Assisters"
          unit="Assists"
          leaders={
            stats
              .contributors
              .assists
          }
        />


        <ContributorList
          title="Most Key Passes"
          unit="Key Passes"
          leaders={
            stats
              .contributors
              .keyPasses
          }
        />

      </section>

    </div>
  );
}


function TeamDetails() {

  const {
    teamId,
  } = useParams();


  const location =
    useLocation();


  const [
    dashboard,
    setDashboard,
  ] =
    useState<
      TeamDashboard | null
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


  let activeSection:
    TeamSection =
    "overview";


  if (
    location.pathname.endsWith(
      "/squad"
    )
  ) {

    activeSection =
      "squad";

  } else if (
    location.pathname.endsWith(
      "/results"
    )
  ) {

    activeSection =
      "results";

  } else if (
    location.pathname.endsWith(
      "/stats"
    )
  ) {

    activeSection =
      "stats";

  }


  useEffect(() => {

    const id =
      Number(teamId);


    if (
      !teamId
      ||
      Number.isNaN(id)
    ) {

      setError(
        "Invalid team."
      );

      setLoading(false);

      return;
    }


    setLoading(true);
    setError(null);


    getTeamDashboard(id)
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
            "Team dashboard error:",
            error
          );

          setError(
            "Unable to load team."
          );

        }
      )
      .finally(
        () => {

          setLoading(false);

        }
      );

  }, [teamId]);


  if (loading) {

    return (
      <main className="team-details-page">
        Loading team...
      </main>
    );

  }


  if (
    error
    ||
    !dashboard
  ) {

    return (
      <main className="team-details-page">

        <div className="team-page-error">

          <h1>
            Team unavailable
          </h1>

          <p>
            {error}
          </p>

        </div>

      </main>
    );

  }


  const {
    team,
  } = dashboard;


  return (
    <main className="team-details-page">

      {/* =====================================
          TEAM BANNER
      ====================================== */}

      <section className="team-banner">

        <div className="team-banner-logo">

          <img
            src={
              team.logoUrl
            }
            alt={
              team.name
            }
          />

        </div>


        <div className="team-banner-main">

          <span className="team-banner-league">
            {team.league.name}
          </span>


          <h1>
            {team.name}
          </h1>


          <div className="team-banner-meta">

            {
              team.country
              && (
                <span>
                  {team.country}
                </span>
              )
            }


            {
              team.founded
              && (
                <span>
                  Founded{" "}
                  {team.founded}
                </span>
              )
            }


            <span>
              {
                formatSeason(
                  team.season
                )
              }
            </span>

          </div>

        </div>


        <RouterLink
          to={
            `/leagues/${team.league.id}`
          }
          className="team-banner-competition"
        >

          <img
            src={
              team.league.logoUrl
            }
            alt=""
          />

          <div>

            <span>
              Competition
            </span>

            <strong>
              {team.league.name}
            </strong>

          </div>

        </RouterLink>

      </section>


      {/* =====================================
          NAVIGATION
      ====================================== */}

      <nav className="team-tabs">

        <RouterLink
          to={
            `/teams/${team.id}`
          }
          className={
            activeSection ===
            "overview"
              ? "team-tab active"
              : "team-tab"
          }
        >
          Overview
        </RouterLink>


        <RouterLink
          to={
            `/teams/${team.id}/squad`
          }
          className={
            activeSection ===
            "squad"
              ? "team-tab active"
              : "team-tab"
          }
        >
          Squad
        </RouterLink>


        <RouterLink
          to={
            `/teams/${team.id}/results`
          }
          className={
            activeSection ===
            "results"
              ? "team-tab active"
              : "team-tab"
          }
        >
          Results
        </RouterLink>


        <RouterLink
          to={
            `/teams/${team.id}/stats`
          }
          className={
            activeSection ===
            "stats"
              ? "team-tab active"
              : "team-tab"
          }
        >
          Stats
        </RouterLink>

      </nav>


      {/* =====================================
          BODY
      ====================================== */}

      <section className="team-details-body">

        {
          activeSection ===
          "overview"
          && (

            <TeamOverview
              dashboard={
                dashboard
              }
            />

          )
        }


        {
          activeSection ===
          "squad"
          && (

            <TeamSquad
              squad={
                dashboard.squad
              }
            />

          )
        }


        {
          activeSection ===
          "results"
          && (

            <TeamResults
              dashboard={
                dashboard
              }
            />

          )
        }


        {
          activeSection ===
          "stats"
          && (

            <TeamStats
              dashboard={
                dashboard
              }
            />

          )
        }

      </section>

    </main>
  );
}


export default TeamDetails;