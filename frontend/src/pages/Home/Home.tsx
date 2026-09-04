import "./Home.css";

import {
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import { Link } from "react-router";

import {
  getMatches,
  type Match,
} from "../../services/matchService";

import {
  getLeagues,
  type League,
} from "../../services/leagueService";

import {
  getLeaders,
  type Leaderboards,
  type StatLeader,
} from "../../services/leaderService";


function getDateKey(date: Date) {
  const year =
    date.getFullYear();

  const month =
    String(
      date.getMonth() + 1
    ).padStart(2, "0");

  const day =
    String(
      date.getDate()
    ).padStart(2, "0");

  return `${year}-${month}-${day}`;
}


function formatDate(date: Date) {
  return date.toLocaleDateString(
    "en-US",
    {
      weekday: "long",
      month: "long",
      day: "numeric",
    }
  );
}


function formatMatchTime(
  dateString: string
) {
  const date =
    new Date(dateString);

  return date.toLocaleTimeString(
    "en-US",
    {
      hour: "numeric",
      minute: "2-digit",
    }
  );
}


function Home() {

  const [selectedDate, setSelectedDate] =
    useState(new Date());

  const [matches, setMatches] =
    useState<Match[]>([]);

  const [leagues, setLeagues] =
    useState<League[]>([]);

  const [leaders, setLeaders] =
    useState<Leaderboards | null>(null);

  const [
    collapsedLeagues,
    setCollapsedLeagues,
  ] = useState<Set<number>>(
    new Set()
  );

  const [
    leaderboardIndex,
    setLeaderboardIndex,
  ] = useState(0);

  const [
    autoRotate,
    setAutoRotate,
  ] = useState(true);

  const [
    matchesLoading,
    setMatchesLoading,
  ] = useState(true);

  const [
    homeError,
    setHomeError,
  ] = useState<string | null>(
    null
  );


  /*
    Initial page information
  */

  useEffect(() => {

    Promise.all([
      getLeagues(),
      getLeaders(),
    ])
      .then(
        ([
          leaguesData,
          leadersData,
        ]) => {

          setLeagues(
            leaguesData
          );

          setLeaders(
            leadersData
          );

        }
      )
      .catch((error) => {

        console.error(
          "Home data error:",
          error
        );

        setHomeError(
          "Unable to load FutBud data."
        );

      });

  }, []);


  /*
    Fetch matches whenever
    the selected date changes.
  */

  useEffect(() => {

    setMatchesLoading(true);

    const date =
      getDateKey(
        selectedDate
      );

    getMatches(date)
      .then((data) => {

        setMatches(
          data
        );

      })
      .catch((error) => {

        console.error(
          "Match loading error:",
          error
        );

      })
      .finally(() => {

        setMatchesLoading(
          false
        );

      });

  }, [selectedDate]);


  /*
    Automatic leaderboard
    rotation every 5 seconds.
  */

  useEffect(() => {

    if (!autoRotate) {
      return;
    }

    const interval =
      window.setInterval(
        () => {

          setLeaderboardIndex(
            (current) =>
              (current + 1) % 4
          );

        },
        5000
      );

    return () => {
      window.clearInterval(
        interval
      );
    };

  }, [autoRotate]);


  /*
    Group matches by league.
  */

  const matchesByLeague =
    useMemo(() => {

      const groups =
        new Map<
          number,
          {
            league: Match["league"];
            matches: Match[];
          }
        >();

      matches.forEach(
        (match) => {

          if (
            !groups.has(
              match.league.id
            )
          ) {

            groups.set(
              match.league.id,
              {
                league:
                  match.league,
                matches: [],
              }
            );

          }

          groups
            .get(
              match.league.id
            )!
            .matches
            .push(match);

        }
      );

      return Array.from(
        groups.values()
      );

    }, [matches]);


  const leaderboardPanels = [
    {
      key: "goals",
      title: "Top Goalscorers",
      unit: "Goals",
      data:
        leaders?.goals || [],
    },

    {
      key: "assists",
      title: "Top Assisters",
      unit: "Assists",
      data:
        leaders?.assists || [],
    },

    {
      key: "keyPasses",
      title: "Most Key Passes",
      unit: "Key Passes",
      data:
        leaders?.keyPasses || [],
    },

    {
      key: "interceptions",
      title: "Most Interceptions",
      unit: "Interceptions",
      data:
        leaders?.interceptions || [],
    },
  ];


  const activeLeaderboard =
    leaderboardPanels[
      leaderboardIndex
    ];


  function changeDay(
    amount: number
  ) {

    setSelectedDate(
      (current) => {

        const next =
          new Date(current);

        next.setDate(
          next.getDate() +
            amount
        );

        return next;

      }
    );

  }


  function toggleLeague(
    leagueId: number
  ) {

    setCollapsedLeagues(
      (current) => {

        const updated =
          new Set(current);

        if (
          updated.has(
            leagueId
          )
        ) {

          updated.delete(
            leagueId
          );

        } else {

          updated.add(
            leagueId
          );

        }

        return updated;

      }
    );

  }


  function changeLeaderboard(
    direction: number
  ) {

    setAutoRotate(false);

    setLeaderboardIndex(
      (current) => {

        const total =
          leaderboardPanels.length;

        return (
          current +
          direction +
          total
        ) % total;

      }
    );

  }


  if (homeError) {

    return (
      <main className="home-page">

        <div className="home-error">

          <h1>
            FutBud
          </h1>

          <p>
            {homeError}
          </p>

        </div>

      </main>
    );

  }


  return (
    <main className="home-page">

      <section className="home-dashboard">

        {/* LEFT — LEAGUES */}

        <aside className="home-leagues">

          <div className="home-panel-title">

            <span className="panel-icon">
              ◈
            </span>

            <h2>
              Leagues
            </h2>

          </div>


          <div className="home-league-list">

            {leagues.map(
              (league) => (

                <Link
                  to={
                    `/leagues/${league.id}`
                  }
                  className="home-league-item"
                  key={league.id}
                >

                  <div className="home-league-logo">

                    {league.logoUrl ? (

                      <img
                        src={
                          league.logoUrl
                        }
                        alt={
                          league.name
                        }
                      />

                    ) : (

                      <span>
                        ⚽
                      </span>

                    )}

                  </div>


                  <div>

                    <strong>
                      {league.name}
                    </strong>

                    <span>
                      {league.country}
                    </span>

                  </div>

                </Link>

              )
            )}

          </div>

        </aside>


        {/* CENTER — MATCHES */}

        <section className="home-matches">


          {/* DATE CHANGER */}

          <div className="home-date-picker">

            <button
              type="button"
              onClick={
                () =>
                  changeDay(-1)
              }
              aria-label="Previous day"
            >
              <ChevronLeft size={20} />
            </button>


            <div>

              <strong>
                {formatDate(
                  selectedDate
                )}
              </strong>

              <span>
                {getDateKey(
                  selectedDate
                )}
              </span>

            </div>


            <button
              type="button"
              onClick={
                () =>
                  changeDay(1)
              }
              aria-label="Next day"
            >
              <ChevronRight size={20} />
            </button>

          </div>


          {/* MATCH AREA */}

          <div className="home-match-scroll">

            {matchesLoading ? (

              <div className="home-no-games">

                <h3>
                  Loading matches...
                </h3>

              </div>

            ) : matchesByLeague.length ===
              0 ? (

              <div className="home-no-games">

                <div className="no-game-icon">
                  ⚽
                </div>

                <h3>
                  No Games Found
                </h3>

                <p>
                  None of the tracked
                  leagues have matches
                  on this date.
                </p>

              </div>

            ) : (

              matchesByLeague.map(
                ({
                  league,
                  matches:
                    leagueMatches,
                }) => {

                  const collapsed =
                    collapsedLeagues.has(
                      league.id
                    );

                  return (

                    <article
                      className="home-league-matches"
                      key={
                        league.id
                      }
                    >

                      <button
                        type="button"
                        className="home-match-league-header"
                        onClick={() =>
                          toggleLeague(
                            league.id
                          )
                        }
                      >

                        <div>

                          <div className="home-match-league-logo">

                            {league.logoUrl && (

                              <img
                                src={
                                  league.logoUrl
                                }
                                alt={
                                  league.name
                                }
                              />

                            )}

                          </div>


                          <strong>
                            {league.name}
                          </strong>


                          <span>
                            {
                              leagueMatches.length
                            }{" "}
                            {
                              leagueMatches.length ===
                              1
                                ? "match"
                                : "matches"
                            }
                          </span>

                        </div>


                        <span className="collapse-arrow">

                          {collapsed
                            ? "›"
                            : "⌄"}

                        </span>

                      </button>


                      {!collapsed && (

                        <div className="home-match-list">

                          {leagueMatches.map(
                            (match) => (

                              <div
                                className="home-match-row"
                                key={
                                  match.id
                                }
                              >

                                <div className="home-match-team home-match-home">

                                  <span>
                                    {
                                      match
                                        .homeTeam
                                        .name
                                    }
                                  </span>

                                  <img
                                    src={
                                      match
                                        .homeTeam
                                        .logoUrl
                                    }
                                    alt=""
                                  />

                                </div>


                                <div className="home-match-center">

                                  {match
                                    .score
                                    .home !==
                                    null &&
                                  match
                                    .score
                                    .away !==
                                    null ? (

                                    <strong>
                                      {
                                        match
                                          .score
                                          .home
                                      }
                                      {" - "}
                                      {
                                        match
                                          .score
                                          .away
                                      }
                                    </strong>

                                  ) : (

                                    <strong>
                                      {formatMatchTime(
                                        match.date
                                      )}
                                    </strong>

                                  )}

                                  <span>
                                    {
                                      match
                                        .status
                                        .short
                                    }
                                  </span>

                                </div>


                                <div className="home-match-team home-match-away">

                                  <img
                                    src={
                                      match
                                        .awayTeam
                                        .logoUrl
                                    }
                                    alt=""
                                  />

                                  <span>
                                    {
                                      match
                                        .awayTeam
                                        .name
                                    }
                                  </span>

                                </div>

                              </div>

                            )
                          )}

                        </div>

                      )}

                    </article>

                  );

                }
              )

            )}

          </div>

        </section>


        {/* RIGHT — LEADERS */}

        <aside className="home-leaders">

          <div className="home-panel-title">

            <span className="panel-icon">
              ↗
            </span>

            <h2>
              Stat Leaders
            </h2>

          </div>


          <div className="leaderboard-navigation">

            <button
              type="button"
              onClick={() =>
                changeLeaderboard(
                  -1
                )
              }
            >
              <ChevronLeft size={20} />
            </button>


            <h3>
              {
                activeLeaderboard.title
              }
            </h3>


            <button
              type="button"
              onClick={() =>
                changeLeaderboard(
                  1
                )
              }
            >
              <ChevronRight size={20} />
            </button>

          </div>


          <div className="home-leader-list">

            {activeLeaderboard
              .data.length === 0 ? (

              <div className="leader-empty">
                No statistics yet.
              </div>

            ) : (

              activeLeaderboard.data.map(
                (
                  leader:
                    StatLeader,
                  index
                ) => (

                  <div
                    className="home-leader-row"
                    key={
                      leader.player
                        .id
                    }
                  >

                    <span className="leader-rank">

                      {index + 1}

                    </span>


                    <div className="leader-photo">

                      {leader.player
                        .photoUrl ? (

                        <img
                          src={
                            leader
                              .player
                              .photoUrl
                          }
                          alt={
                            leader
                              .player
                              .name
                          }
                        />

                      ) : (

                        <span>
                          ?
                        </span>

                      )}

                    </div>


                    <div className="leader-info">

                      <strong>
                        {
                          leader
                            .player
                            .name
                        }
                      </strong>

                      <span>
                        {leader.team
                          ?.name ||
                          ""}
                      </span>

                    </div>


                    <div className="leader-value">

                      <strong>
                        {
                          leader.value
                        }
                      </strong>

                      <span>
                        {
                          activeLeaderboard.unit
                        }
                      </span>

                    </div>

                  </div>

                )
              )

            )}

          </div>


          <div className="leader-dots">

            {leaderboardPanels.map(
              (
                panel,
                index
              ) => (

                <button
                  type="button"
                  key={
                    panel.key
                  }
                  className={
                    index ===
                    leaderboardIndex
                      ? "active"
                      : ""
                  }
                  aria-label={
                    panel.title
                  }
                  onClick={() => {

                    setAutoRotate(
                      false
                    );

                    setLeaderboardIndex(
                      index
                    );

                  }}
                />

              )
            )}

          </div>


          <div className="leader-auto">

            {autoRotate
              ? "Auto-rotates every 5 seconds"
              : "Manual navigation"}

          </div>

        </aside>

      </section>

    </main>
  );
}


export default Home;