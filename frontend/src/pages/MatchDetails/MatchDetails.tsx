import "./MatchDetails.css";

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
  getMatchDashboard,
  type HeadToHeadMatch,
  type LineupPlayer,
  type MatchDashboard,
  type MatchEvent,
  type MatchTeam,
  type PlayerMatchStat,
  type TeamLineup,
  type TeamMatchStats,
} from "../../services/matchDetailsService";


type MatchSection =
  | "overview"
  | "lineups"
  | "stats"
  | "players"
  | "h2h";


type PlayerTeamSelection =
  | "home"
  | "away";


function displayValue(
  value:
    number
    | string
    | null
    | undefined
) {

  if (
    value === null
    ||
    value === undefined
  ) {
    return "—";
  }

  return value;
}


function formatDate(
  dateString: string
) {

  return new Date(
    dateString
  ).toLocaleDateString(
    "en-US",
    {
      month: "short",
      day: "numeric",
      year: "numeric",
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
      year: "numeric",
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


function getMatchSection(
  pathname: string
): MatchSection {

  if (
    pathname.endsWith(
      "/lineups"
    )
  ) {
    return "lineups";
  }

  if (
    pathname.endsWith(
      "/stats"
    )
  ) {
    return "stats";
  }

  if (
    pathname.endsWith(
      "/players"
    )
  ) {
    return "players";
  }

  if (
    pathname.endsWith(
      "/h2h"
    )
  ) {
    return "h2h";
  }

  return "overview";
}


function formatMatchMinute(
  event: MatchEvent
) {

  const minute =
    event.time.elapsed
    ?? 0;

  const extra =
    event.time.extra;

  if (
    extra
    &&
    extra > 0
  ) {

    return `${minute}+${extra}'`;

  }

  return `${minute}'`;
}


function getEventIcon(
  event: MatchEvent
) {

  const type =
    (
      event.type
      || ""
    ).toLowerCase();

  const detail =
    (
      event.detail
      || ""
    ).toLowerCase();


  if (
    type === "goal"
  ) {
    return "⚽";
  }


  if (
    type === "card"
  ) {

    if (
      detail.includes("red")
    ) {
      return "🟥";
    }

    return "🟨";

  }


  if (
    type === "subst"
  ) {
    return "↔";
  }


  if (
    type === "var"
  ) {
    return "VAR";
  }


  return "•";
}


function TeamLink({
  team,
  reverse = false,
}: {
  team: MatchTeam;
  reverse?: boolean;
}) {

  return (
    <RouterLink
      to={`/teams/${team.id}`}
      className={
        reverse
          ? "match-team-link reverse"
          : "match-team-link"
      }
    >

      {reverse && (

        <span>
          {team.name}
        </span>

      )}


      {team.logoUrl && (

        <img
          src={team.logoUrl}
          alt=""
        />

      )}


      {!reverse && (

        <span>
          {team.name}
        </span>

      )}

    </RouterLink>
  );
}


function EventList({
  dashboard,
  limit,
}: {
  dashboard: MatchDashboard;
  limit?: number;
}) {

  const events =
    limit
      ? dashboard.events.slice(
          0,
          limit
        )
      : dashboard.events;


  if (
    events.length === 0
  ) {

    return (
      <div className="match-empty">
        No match events available.
      </div>
    );

  }


  return (
    <div className="match-event-list">

      {events.map(
        event => {

          const isHome =
            event.teamId ===
            dashboard
              .match
              .homeTeam
              .id;


          const playerName =
            event.player.name
            || "Unknown";


          const assistName =
            event.assist.name;


          return (
            <div
              className="match-event-row"
              key={event.index}
            >

              <span className="match-event-minute">
                {
                  formatMatchMinute(
                    event
                  )
                }
              </span>


              <span className="match-event-icon">
                {
                  getEventIcon(
                    event
                  )
                }
              </span>


              <div className="match-event-content">

                <strong>
                  {playerName}
                </strong>


                {assistName && (

                  <span>
                    {
                      event.type
                        ?.toLowerCase()
                        === "goal"
                        ? `Assist: ${assistName}`
                        : assistName
                    }
                  </span>

                )}


                {!assistName
                  &&
                  event.comments
                  && (

                    <span>
                      {
                        event.comments
                      }
                    </span>

                  )}

              </div>


              <div className="match-event-team">

                {(
                  isHome
                    ? dashboard.match.homeTeam.logoUrl
                    : dashboard.match.awayTeam.logoUrl
                ) && (

                  <img
                    src={
                      isHome
                        ? dashboard.match.homeTeam.logoUrl!
                        : dashboard.match.awayTeam.logoUrl!
                    }
                    alt=""
                  />

                )}

              </div>

            </div>
          );

        }
      )}

    </div>
  );
}


function StatComparisonRow({
  label,
  home,
  away,
  suffix = "",
}: {
  label: string;
  home:
    number
    | null
    | undefined;
  away:
    number
    | null
    | undefined;
  suffix?: string;
}) {

  const homeNumber =
    typeof home === "number"
      ? home
      : 0;

  const awayNumber =
    typeof away === "number"
      ? away
      : 0;

  const total =
    homeNumber
    +
    awayNumber;

  const homePercent =
    total > 0
      ? (
          homeNumber
          /
          total
        ) * 100
      : 50;


  return (
    <div className="match-stat-comparison">

      <div className="match-stat-values">

        <strong>
          {
            home === null
            ||
            home === undefined
              ? "—"
              : `${home}${suffix}`
          }
        </strong>


        <span>
          {label}
        </span>


        <strong>
          {
            away === null
            ||
            away === undefined
              ? "—"
              : `${away}${suffix}`
          }
        </strong>

      </div>


      <div className="match-stat-track">

        <div
          className="match-stat-track-home"
          style={{
            width:
              `${homePercent}%`,
          }}
        />

        <div
          className="match-stat-track-away"
          style={{
            width:
              `${
                100
                -
                homePercent
              }%`,
          }}
        />

      </div>

    </div>
  );
}


function MatchStatsContent({
  dashboard,
  compact = false,
}: {
  dashboard: MatchDashboard;
  compact?: boolean;
}) {

  const home =
    dashboard
      .matchStats
      .home;

  const away =
    dashboard
      .matchStats
      .away;


  if (
    !home
    ||
    !away
  ) {

    return (
      <div className="match-empty">
        Match statistics are
        unavailable.
      </div>
    );

  }


  const rows = [
    {
      label:
        "Possession",

      home:
        home.possession,

      away:
        away.possession,

      suffix:
        "%",
    },
    {
      label:
        "Total Shots",

      home:
        home.shots.total,

      away:
        away.shots.total,
    },
    {
      label:
        "Shots on Target",

      home:
        home.shots.onTarget,

      away:
        away.shots.onTarget,
    },
    {
      label:
        "Shots off Target",

      home:
        home.shots.offTarget,

      away:
        away.shots.offTarget,
    },
    {
      label:
        "Blocked Shots",

      home:
        home.shots.blocked,

      away:
        away.shots.blocked,
    },
    {
      label:
        "Shots Inside Box",

      home:
        home.shots.insideBox,

      away:
        away.shots.insideBox,
    },
    {
      label:
        "Shots Outside Box",

      home:
        home.shots.outsideBox,

      away:
        away.shots.outsideBox,
    },
    {
      label:
        "Corners",

      home:
        home.corners,

      away:
        away.corners,
    },
    {
      label:
        "Offsides",

      home:
        home.offsides,

      away:
        away.offsides,
    },
    {
      label:
        "Fouls",

      home:
        home.fouls,

      away:
        away.fouls,
    },
    {
      label:
        "Passes",

      home:
        home.passes.total,

      away:
        away.passes.total,
    },
    {
      label:
        "Accurate Passes",

      home:
        home.passes.accurate,

      away:
        away.passes.accurate,
    },
    {
      label:
        "Pass Accuracy",

      home:
        home.passes.accuracy,

      away:
        away.passes.accuracy,

      suffix:
        "%",
    },
    {
      label:
        "Yellow Cards",

      home:
        home.yellowCards,

      away:
        away.yellowCards,
    },
    {
      label:
        "Red Cards",

      home:
        home.redCards,

      away:
        away.redCards,
    },
    {
      label:
        "Saves",

      home:
        home.goalkeeperSaves,

      away:
        away.goalkeeperSaves,
    },
  ];


  const visibleRows =
    compact
      ? rows.slice(
          0,
          6
        )
      : rows;


  return (
    <div className="match-stat-list">

      {
        visibleRows.map(
          row => (

            <StatComparisonRow
              key={row.label}
              label={row.label}
              home={row.home}
              away={row.away}
              suffix={
                row.suffix
                || ""
              }
            />

          )
        )
      }

    </div>
  );
}


function getPitchPosition(
  grid: string | null
) {

  if (!grid) {

    return {
      left: 50,
      top: 50,
    };

  }


  const [
    rowText,
    columnText,
  ] =
    grid.split(":");


  const row =
    Number(
      rowText
    );

  const column =
    Number(
      columnText
    );


  const rowCounts:
    Record<
      number,
      number
    > = {};


  return {
    row,
    column,
    rowCounts,
  };
}


function FormationPitch({
  lineup,
  team,
  compact = false,
}: {
  lineup: TeamLineup;
  team: MatchTeam;
  compact?: boolean;
}) {

  if (
    lineup
      .starters
      .length === 0
  ) {

    return (
      <div className="match-empty">
        Lineup unavailable.
      </div>
    );

  }


  const rows =
    new Map<
      number,
      LineupPlayer[]
    >();


  lineup
    .starters
    .forEach(
      player => {

        if (!player.grid) {
          return;
        }


        const [
          rowText,
        ] =
          player
            .grid
            .split(":");


        const row =
          Number(
            rowText
          );


        if (
          !rows.has(row)
        ) {

          rows.set(
            row,
            []
          );

        }


        rows
          .get(row)!
          .push(
            player
          );

      }
    );


  const maxRow =
    Math.max(
      ...Array.from(
        rows.keys()
      )
    );


  const positions =
    lineup
      .starters
      .map(
        player => {

          if (!player.grid) {

            return {
              player,
              left: 50,
              top: 50,
            };

          }


          const [
            rowText,
            columnText,
          ] =
            player
              .grid
              .split(":");


          const row =
            Number(
              rowText
            );

          const column =
            Number(
              columnText
            );


          const playersInRow =
            rows.get(row)
            || [];


          const columns =
            Math.max(
              playersInRow.length,
              1
            );


          const left =
            (
              column
              /
              (
                columns
                +
                1
              )
            )
            *
            100;


          const top =
            maxRow > 1
              ? (
                  (
                    row
                    -
                    1
                  )
                  /
                  (
                    maxRow
                    -
                    1
                  )
                )
                *
                78
                +
                10
              : 50;


          return {
            player,
            left,
            top,
          };

        }
      );


  return (
    <div
      className={
        compact
          ? "formation-pitch compact"
          : "formation-pitch"
      }
    >

      <div className="pitch-halfway" />
      <div className="pitch-circle" />

      <div className="pitch-box pitch-box-top" />
      <div className="pitch-box pitch-box-bottom" />


      {
        positions.map(
          ({
            player,
            left,
            top,
          }) => (

            <RouterLink
              to={
                `/players/${player.id}`
              }
              key={player.id}
              className="pitch-player"
              style={{
                left:
                  `${left}%`,

                top:
                  `${top}%`,
              }}
            >

              <div className="pitch-player-circle">

                {player.photoUrl ? (

                  <img
                    src={
                      player.photoUrl
                    }
                    alt=""
                  />

                ) : (

                  <span>
                    {
                      player
                        .shirtNumber
                      ?? "?"
                    }
                  </span>

                )}

              </div>


              <span className="pitch-player-name">
                {
                  compact
                    ? player.name
                        .split(" ")
                        .slice(-1)[0]
                    : player.name
                }
              </span>

            </RouterLink>

          )
        )
      }


      <div className="pitch-team-label">

        {team.logoUrl && (

          <img
            src={team.logoUrl}
            alt=""
          />

        )}

        <strong>
          {team.name}
        </strong>

        <span>
          {
            lineup.formation
            || "Formation"
          }
        </span>

      </div>

    </div>
  );
}


function LineupSide({
  team,
  lineup,
}: {
  team: MatchTeam;
  lineup: TeamLineup;
}) {

  return (
    <section className="match-card">

      <div className="match-card-header">

        <TeamLink
          team={team}
        />


        <span className="match-card-label">
          {
            lineup.formation
            || "—"
          }
        </span>

      </div>


      <FormationPitch
        team={team}
        lineup={lineup}
      />


      <div className="lineup-meta">

        <div>

          <span>
            Manager
          </span>

          <strong>
            {
              lineup
                .coach
                ?.name
              || "—"
            }
          </strong>

        </div>

      </div>


      <div className="lineup-bench">

        <h3>
          Substitutes
        </h3>


        {
          lineup
            .bench
            .length === 0
          ? (

            <div className="match-empty small">
              No bench data.
            </div>

          )
          : (

            lineup
              .bench
              .map(
                player => (

                  <RouterLink
                    to={
                      `/players/${player.id}`
                    }
                    className="lineup-bench-player"
                    key={player.id}
                  >

                    <span className="lineup-bench-number">
                      {
                        player
                          .shirtNumber
                        ?? "—"
                      }
                    </span>

                    <div className="lineup-bench-photo">

                      {
                        player
                          .photoUrl
                        ? (

                          <img
                            src={
                              player
                                .photoUrl
                            }
                            alt=""
                          />

                        )
                        : null
                      }

                    </div>

                    <strong>
                      {player.name}
                    </strong>

                    <span>
                      {
                        player
                          .position
                        || "—"
                      }
                    </span>

                  </RouterLink>

                )
              )

          )
        }

      </div>

    </section>
  );
}


function PlayerStatTable({
  players,
}: {
  players:
    PlayerMatchStat[];
}) {

  return (
    <div className="player-stat-table-wrap">

      <div className="player-stat-table">

        <div className="player-stat-row player-stat-header">

          <span>Player</span>
          <span>Min</span>
          <span>G</span>
          <span>A</span>
          <span>Shots</span>
          <span>SOT</span>
          <span>KP</span>
          <span>Pass</span>
          <span>Tkl</span>
          <span>Int</span>
          <span>Rating</span>

        </div>


        {
          players.map(
            stat => (

              <RouterLink
                to={
                  `/players/${stat.player.id}`
                }
                className="player-stat-row"
                key={stat.player.id}
              >

                <div className="player-stat-name">

                  <div className="player-stat-photo">

                    {
                      stat
                        .player
                        .photoUrl
                      && (

                        <img
                          src={
                            stat
                              .player
                              .photoUrl
                          }
                          alt=""
                        />

                      )
                    }

                  </div>


                  <div>

                    <strong>
                      {
                        stat
                          .player
                          .name
                      }
                    </strong>

                    <span>
                      {
                        stat.position
                        || "—"
                      }
                    </span>

                  </div>

                </div>


                <span>
                  {
                    displayValue(
                      stat.minutes
                    )
                  }
                </span>


                <strong>
                  {
                    displayValue(
                      stat.goals
                    )
                  }
                </strong>


                <strong>
                  {
                    displayValue(
                      stat.assists
                    )
                  }
                </strong>


                <span>
                  {
                    displayValue(
                      stat.shots.total
                    )
                  }
                </span>


                <span>
                  {
                    displayValue(
                      stat.shots.onTarget
                    )
                  }
                </span>


                <span>
                  {
                    displayValue(
                      stat.passes.key
                    )
                  }
                </span>


                <span>
                  {
                    displayValue(
                      stat.passes.total
                    )
                  }
                </span>


                <span>
                  {
                    displayValue(
                      stat.tackles
                    )
                  }
                </span>


                <span>
                  {
                    displayValue(
                      stat.interceptions
                    )
                  }
                </span>


                <span className="player-rating">
                  {
                    stat.rating
                    ?? "—"
                  }
                </span>

              </RouterLink>

            )
          )
        }

      </div>

    </div>
  );
}


function HeadToHeadMeeting({
  meeting,
}: {
  meeting:
    HeadToHeadMatch;
}) {

  return (
    <div className="h2h-meeting-row">

      <div className="h2h-meeting-date">

        <strong>
          {
            meeting.date
              ? formatDate(
                  meeting.date
                )
              : "—"
          }
        </strong>

        <span>
          {
            meeting
              .league
              .name
            || "Competition"
          }
        </span>

      </div>


      <TeamLink
        team={
          meeting.homeTeam
        }
        reverse
      />


      <div className="h2h-meeting-score">

        <strong>
          {
            meeting.homeGoals
            ?? "—"
          }
          {" - "}
          {
            meeting.awayGoals
            ?? "—"
          }
        </strong>

      </div>


      <TeamLink
        team={
          meeting.awayTeam
        }
      />

    </div>
  );
}


function HeadToHeadRecord({
  dashboard,
}: {
  dashboard:
    MatchDashboard;
}) {

  const h2h =
    dashboard.headToHead;


  const total =
    h2h.homeWins
    +
    h2h.draws
    +
    h2h.awayWins;


  if (
    total === 0
    &&
    h2h.matches.length
      === 0
  ) {

    return (
      <div className="match-empty h2h-empty">
        Head-to-head data is not
        available yet.
      </div>
    );

  }


  const homeWidth =
    total > 0
      ? (
          h2h.homeWins
          /
          total
        ) * 100
      : 0;

  const drawWidth =
    total > 0
      ? (
          h2h.draws
          /
          total
        ) * 100
      : 0;

  const awayWidth =
    total > 0
      ? (
          h2h.awayWins
          /
          total
        ) * 100
      : 0;


  return (
    <div className="h2h-record">

      <div className="h2h-record-numbers">

        <div>

          <strong>
            {h2h.homeWins}
          </strong>

          <span>
            {
              dashboard
                .match
                .homeTeam
                .name
            } wins
          </span>

        </div>


        <div>

          <strong>
            {h2h.draws}
          </strong>

          <span>
            Draws
          </span>

        </div>


        <div>

          <strong>
            {h2h.awayWins}
          </strong>

          <span>
            {
              dashboard
                .match
                .awayTeam
                .name
            } wins
          </span>

        </div>

      </div>


      <div className="h2h-bar">

        <span
          className="h2h-home"
          style={{
            width:
              `${homeWidth}%`,
          }}
        />

        <span
          className="h2h-draw"
          style={{
            width:
              `${drawWidth}%`,
          }}
        />

        <span
          className="h2h-away"
          style={{
            width:
              `${awayWidth}%`,
          }}
        />

      </div>

    </div>
  );
}


function Overview({
  dashboard,
}: {
  dashboard:
    MatchDashboard;
}) {

  const topPlayers =
    [
      ...dashboard
        .playerStats
        .home,
      ...dashboard
        .playerStats
        .away,
    ]
      .filter(
        player =>
          player.rating !== null
          &&
          Number(
            player.rating
          ) > 0
      )
      .sort(
        (a, b) =>
          Number(
            b.rating
          )
          -
          Number(
            a.rating
          )
      )
      .slice(
        0,
        5
      );


  return (
    <div className="match-overview">

      <div className="match-overview-grid">

        <section className="match-card">

          <div className="match-card-header">

            <div>

              <span className="match-eyebrow">
                Previous meetings
              </span>

              <h2>
                Head to Head
              </h2>

            </div>


            <RouterLink
              to={
                `/matches/${dashboard.match.id}/h2h`
              }
              className="match-card-link"
            >
              Full H2H
            </RouterLink>

          </div>


          <HeadToHeadRecord
            dashboard={
              dashboard
            }
          />

        </section>


        <section className="match-card">

          <div className="match-card-header">

            <div>

              <span className="match-eyebrow">
                Latest
              </span>

              <h2>
                Recent Meetings
              </h2>

            </div>

          </div>


          {
            dashboard
              .headToHead
              .matches
              .length === 0
            ? (

              <div className="match-empty">
                Historical meetings
                unavailable.
              </div>

            )
            : (

              <div className="h2h-preview-list">

                {
                  dashboard
                    .headToHead
                    .matches
                    .slice(
                      0,
                      4
                    )
                    .map(
                      meeting => (

                        <HeadToHeadMeeting
                          meeting={
                            meeting
                          }
                          key={
                            meeting.id
                          }
                        />

                      )
                    )
                }

              </div>

            )
          }

        </section>

      </div>


      <div className="match-overview-grid">

        <section className="match-card">

          <div className="match-card-header">

            <div>

              <span className="match-eyebrow">
                Starting XI
              </span>

              <h2>
                Lineups
              </h2>

            </div>


            <RouterLink
              to={
                `/matches/${dashboard.match.id}/lineups`
              }
              className="match-card-link"
            >
              Full Lineups
            </RouterLink>

          </div>


          <FormationPitch
            team={
              dashboard
                .match
                .homeTeam
            }
            lineup={
              dashboard
                .lineups
                .home
            }
            compact
          />

        </section>


        <section className="match-card">

          <div className="match-card-header">

            <div>

              <span className="match-eyebrow">
                Comparison
              </span>

              <h2>
                Match Statistics
              </h2>

            </div>


            <RouterLink
              to={
                `/matches/${dashboard.match.id}/stats`
              }
              className="match-card-link"
            >
              All Stats
            </RouterLink>

          </div>


          <MatchStatsContent
            dashboard={
              dashboard
            }
            compact
          />

        </section>

      </div>


      <div className="match-overview-grid">

        <section className="match-card">

          <div className="match-card-header">

            <div>

              <span className="match-eyebrow">
                Timeline
              </span>

              <h2>
                Key Events
              </h2>

            </div>

          </div>


          <EventList
            dashboard={
              dashboard
            }
            limit={8}
          />

        </section>


        <section className="match-card">

          <div className="match-card-header">

            <div>

              <span className="match-eyebrow">
                Best performances
              </span>

              <h2>
                Player Stats
              </h2>

            </div>


            <RouterLink
              to={
                `/matches/${dashboard.match.id}/players`
              }
              className="match-card-link"
            >
              All Players
            </RouterLink>

          </div>


          <div className="top-player-list">

            {
              topPlayers.map(
                (
                  stat,
                  index
                ) => (

                  <RouterLink
                    to={
                      `/players/${stat.player.id}`
                    }
                    className="top-player-row"
                    key={
                      stat.player.id
                    }
                  >

                    <span className="top-player-rank">
                      {index + 1}
                    </span>


                    <div className="top-player-photo">

                      {
                        stat
                          .player
                          .photoUrl
                        && (

                          <img
                            src={
                              stat
                                .player
                                .photoUrl
                            }
                            alt=""
                          />

                        )
                      }

                    </div>


                    <div className="top-player-info">

                      <strong>
                        {
                          stat
                            .player
                            .name
                        }
                      </strong>

                      <span>
                        {
                          stat
                            .position
                          || "Player"
                        }
                      </span>

                    </div>


                    <div className="top-player-output">

                      <span>
                        {
                          stat.goals
                          ?? 0
                        } G
                      </span>

                      <span>
                        {
                          stat.assists
                          ?? 0
                        } A
                      </span>

                    </div>


                    <strong className="top-player-rating">
                      {
                        stat.rating
                        ?? "—"
                      }
                    </strong>

                  </RouterLink>

                )
              )
            }

          </div>

        </section>

      </div>

    </div>
  );
}


function LineupsPage({
  dashboard,
}: {
  dashboard:
    MatchDashboard;
}) {

  return (
    <div className="match-lineups-page">

      <div className="match-page-heading">

        <div>

          <span className="match-eyebrow">
            Match setup
          </span>

          <h2>
            Starting Lineups
          </h2>

        </div>

      </div>


      <div className="match-lineup-grid">

        <LineupSide
          team={
            dashboard
              .match
              .homeTeam
          }
          lineup={
            dashboard
              .lineups
              .home
          }
        />


        <LineupSide
          team={
            dashboard
              .match
              .awayTeam
          }
          lineup={
            dashboard
              .lineups
              .away
          }
        />

      </div>

    </div>
  );
}


function StatsPage({
  dashboard,
}: {
  dashboard:
    MatchDashboard;
}) {

  return (
    <section className="match-card">

      <div className="match-card-header match-stats-header">

        <TeamLink
          team={
            dashboard
              .match
              .homeTeam
          }
        />


        <div>

          <span className="match-eyebrow">
            Full Time
          </span>

          <h2>
            Match Statistics
          </h2>

        </div>


        <TeamLink
          team={
            dashboard
              .match
              .awayTeam
          }
          reverse
        />

      </div>


      <div className="full-match-stats">

        <MatchStatsContent
          dashboard={
            dashboard
          }
        />

      </div>

    </section>
  );
}


function PlayersPage({
  dashboard,
}: {
  dashboard:
    MatchDashboard;
}) {

  const [
    selected,
    setSelected,
  ] =
    useState<PlayerTeamSelection>(
      "home"
    );


  const selectedTeam =
    selected === "home"
      ? dashboard
          .match
          .homeTeam
      : dashboard
          .match
          .awayTeam;


  const players =
    selected === "home"
      ? dashboard
          .playerStats
          .home
      : dashboard
          .playerStats
          .away;


  return (
    <section className="match-card">

      <div className="match-card-header">

        <div>

          <span className="match-eyebrow">
            Individual performance
          </span>

          <h2>
            Player Statistics
          </h2>

        </div>


        <div className="player-team-switch">

          <button
            type="button"
            onClick={
              () =>
                setSelected(
                  "home"
                )
            }
            className={
              selected
              === "home"
                ? "active"
                : ""
            }
          >

            {
              dashboard
                .match
                .homeTeam
                .logoUrl
              && (

                <img
                  src={
                    dashboard
                      .match
                      .homeTeam
                      .logoUrl
                  }
                  alt=""
                />

              )
            }

            {
              dashboard
                .match
                .homeTeam
                .name
            }

          </button>


          <button
            type="button"
            onClick={
              () =>
                setSelected(
                  "away"
                )
            }
            className={
              selected
              === "away"
                ? "active"
                : ""
            }
          >

            {
              dashboard
                .match
                .awayTeam
                .logoUrl
              && (

                <img
                  src={
                    dashboard
                      .match
                      .awayTeam
                      .logoUrl
                  }
                  alt=""
                />

              )
            }

            {
              dashboard
                .match
                .awayTeam
                .name
            }

          </button>

        </div>

      </div>


      <div className="player-stat-team-heading">

        <TeamLink
          team={
            selectedTeam
          }
        />

      </div>


      <PlayerStatTable
        players={
          players
        }
      />

    </section>
  );
}


function HeadToHeadPage({
  dashboard,
}: {
  dashboard:
    MatchDashboard;
}) {

  return (
    <div className="match-h2h-page">

      <section className="match-card">

        <div className="match-card-header">

          <div>

            <span className="match-eyebrow">
              Historical record
            </span>

            <h2>
              Head to Head
            </h2>

          </div>

        </div>


        <HeadToHeadRecord
          dashboard={
            dashboard
          }
        />

      </section>


      <section className="match-card">

        <div className="match-card-header">

          <div>

            <span className="match-eyebrow">
              Previous fixtures
            </span>

            <h2>
              Recent Meetings
            </h2>

          </div>

        </div>


        {
          dashboard
            .headToHead
            .matches
            .length === 0
          ? (

            <div className="match-empty large">
              Historical head-to-head
              fixtures are not
              available yet.
            </div>

          )
          : (

            <div className="h2h-full-list">

              {
                dashboard
                  .headToHead
                  .matches
                  .map(
                    meeting => (

                      <HeadToHeadMeeting
                        meeting={
                          meeting
                        }
                        key={
                          meeting.id
                        }
                      />

                    )
                  )
              }

            </div>

          )
        }

      </section>

    </div>
  );
}


function MatchDetails() {

  const {
    matchId,
  } =
    useParams();


  const location =
    useLocation();


  const [
    dashboard,
    setDashboard,
  ] =
    useState<
      MatchDashboard | null
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


  const activeSection =
    getMatchSection(
      location.pathname
    );


  useEffect(
    () => {

      const id =
        Number(
          matchId
        );


      if (
        !matchId
        ||
        Number.isNaN(id)
      ) {

        setError(
          "Invalid match."
        );

        setLoading(false);

        return;

      }


      setLoading(true);
      setError(null);


      getMatchDashboard(id)
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
              "Match dashboard error:",
              error
            );

            setError(
              "Unable to load match."
            );

          }
        )
        .finally(
          () => {

            setLoading(false);

          }
        );

    },
    [matchId]
  );


  const goalEvents =
    useMemo(
      () => {

        if (!dashboard) {
          return [];
        }


        return dashboard
          .events
          .filter(
            event =>
              event.type
                ?.toLowerCase()
                === "goal"
              &&
              !(
                event.detail
                  ?.toLowerCase()
                  .includes(
                    "cancel"
                  )
              )
          );

      },
      [dashboard]
    );


  if (loading) {

    return (
      <main className="match-details-page">
        Loading match...
      </main>
    );

  }


  if (
    error
    ||
    !dashboard
  ) {

    return (
      <main className="match-details-page">

        <div className="match-page-error">

          <h1>
            Match unavailable
          </h1>

          <p>
            {
              error
              || "Unable to load match."
            }
          </p>

        </div>

      </main>
    );

  }


  const match =
    dashboard.match;


  const homeGoalEvents =
    goalEvents.filter(
      event =>
        event.teamId
        ===
        match.homeTeam.id
    );


  const awayGoalEvents =
    goalEvents.filter(
      event =>
        event.teamId
        ===
        match.awayTeam.id
    );


  return (
    <main className="match-details-page">

      <section className="match-hero">

        <div className="match-hero-league">

          {
            match
              .league
              .logoUrl
            && (

              <img
                src={
                  match
                    .league
                    .logoUrl
                }
                alt=""
              />

            )
          }


          <div>

            <RouterLink
              to={
                `/leagues/${match.league.id}`
              }
            >
              {
                match
                  .league
                  .name
              }
            </RouterLink>

            <span>
              {
                match.round
                || `Season ${match.season}`
              }
            </span>

          </div>

        </div>


        <div className="match-hero-main">

          <div className="match-hero-team home">

            <RouterLink
              to={
                `/teams/${match.homeTeam.id}`
              }
            >

              {
                match
                  .homeTeam
                  .logoUrl
                && (

                  <img
                    src={
                      match
                        .homeTeam
                        .logoUrl
                    }
                    alt=""
                  />

                )
              }


              <h1>
                {
                  match
                    .homeTeam
                    .name
                }
              </h1>

            </RouterLink>


            <div className="match-goalscorers">

              {
                homeGoalEvents.map(
                  event => (

                    <span
                      key={
                        event.index
                      }
                    >
                      {
                        event
                          .player
                          .name
                        || "Goal"
                      }
                      {" "}
                      {
                        formatMatchMinute(
                          event
                        )
                      }
                    </span>

                  )
                )
              }

            </div>

          </div>


          <div className="match-score-center">

            <span className="match-status-badge">
              {
                match
                  .status
                  .long
                || match
                    .status
                    .short
              }
            </span>


            <div className="match-score">

              <strong>
                {
                  match
                    .score
                    .home
                  ?? "—"
                }
              </strong>

              <span>
                -
              </span>

              <strong>
                {
                  match
                    .score
                    .away
                  ?? "—"
                }
              </strong>

            </div>


            <span className="match-date">
              {
                formatLongDate(
                  match.date
                )
              }
            </span>


            <span className="match-time">
              {
                formatTime(
                  match.date
                )
              }
            </span>

          </div>


          <div className="match-hero-team away">

            <RouterLink
              to={
                `/teams/${match.awayTeam.id}`
              }
            >

              {
                match
                  .awayTeam
                  .logoUrl
                && (

                  <img
                    src={
                      match
                        .awayTeam
                        .logoUrl
                    }
                    alt=""
                  />

                )
              }


              <h1>
                {
                  match
                    .awayTeam
                    .name
                }
              </h1>

            </RouterLink>


            <div className="match-goalscorers">

              {
                awayGoalEvents.map(
                  event => (

                    <span
                      key={
                        event.index
                      }
                    >
                      {
                        event
                          .player
                          .name
                        || "Goal"
                      }
                      {" "}
                      {
                        formatMatchMinute(
                          event
                        )
                      }
                    </span>

                  )
                )
              }

            </div>

          </div>

        </div>


        <div className="match-hero-meta">

          {
            match.venue
            && (

              <span>
                {match.venue}
              </span>

            )
          }


          {
            match.referee
            && (

              <span>
                Referee:{" "}
                {
                  match.referee
                }
              </span>

            )
          }

        </div>

      </section>


      <nav className="match-tabs">

        <RouterLink
          to={
            `/matches/${match.id}`
          }
          className={
            activeSection
            === "overview"
              ? "match-tab active"
              : "match-tab"
          }
        >
          Overview
        </RouterLink>


        <RouterLink
          to={
            `/matches/${match.id}/lineups`
          }
          className={
            activeSection
            === "lineups"
              ? "match-tab active"
              : "match-tab"
          }
        >
          Lineups
        </RouterLink>


        <RouterLink
          to={
            `/matches/${match.id}/stats`
          }
          className={
            activeSection
            === "stats"
              ? "match-tab active"
              : "match-tab"
          }
        >
          Match Stats
        </RouterLink>


        <RouterLink
          to={
            `/matches/${match.id}/players`
          }
          className={
            activeSection
            === "players"
              ? "match-tab active"
              : "match-tab"
          }
        >
          Player Stats
        </RouterLink>


        <RouterLink
          to={
            `/matches/${match.id}/h2h`
          }
          className={
            activeSection
            === "h2h"
              ? "match-tab active"
              : "match-tab"
          }
        >
          Head to Head
        </RouterLink>

      </nav>


      <section className="match-details-body">

        {
          activeSection
          === "overview"
          && (

            <Overview
              dashboard={
                dashboard
              }
            />

          )
        }


        {
          activeSection
          === "lineups"
          && (

            <LineupsPage
              dashboard={
                dashboard
              }
            />

          )
        }


        {
          activeSection
          === "stats"
          && (

            <StatsPage
              dashboard={
                dashboard
              }
            />

          )
        }


        {
          activeSection
          === "players"
          && (

            <PlayersPage
              dashboard={
                dashboard
              }
            />

          )
        }


        {
          activeSection
          === "h2h"
          && (

            <HeadToHeadPage
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


export default MatchDetails;