import "./Matches.css";

import { useEffect, useState } from "react";

import {
  getMatches,
  type Match,
} from "../../services/matchService";


function getDateKey(date: Date) {
  const year = date.getFullYear();

  const month = String(
    date.getMonth() + 1
  ).padStart(2, "0");

  const day = String(
    date.getDate()
  ).padStart(2, "0");

  return `${year}-${month}-${day}`;
}


function formatDate(date: Date) {
  return date.toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  });
}


function formatMatchTime(dateString: string) {
  const date = new Date(dateString);

  return date.toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
  });
}


function isSameDay(date1: Date, date2: Date) {
  return (
    date1.getFullYear() === date2.getFullYear() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getDate() === date2.getDate()
  );
}


function Matches() {

  const [matches, setMatches] =
    useState<Match[]>([]);

  const [selectedDate, setSelectedDate] =
    useState(new Date());

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);


  const today = new Date();


  useEffect(() => {

    const dateString =
      getDateKey(selectedDate);

    setLoading(true);
    setError(null);

    getMatches(dateString)
      .then((data) => {

        console.log(
          "Matches from backend:",
          data
        );

        setMatches(data);

      })
      .catch((error) => {

        console.error(
          "Failed to load matches:",
          error
        );

        setError(
          "Unable to load matches."
        );

      })
      .finally(() => {

        setLoading(false);

      });

  }, [selectedDate]);


  /*
    Group the matches returned from FastAPI
    by league name.

    Example:

    {
      "Premier League": [...]
    }
  */

  const matchesByLeague =
    matches.reduce<Record<string, Match[]>>(
      (groups, match) => {

        const leagueName =
          match.league.name;

        if (!groups[leagueName]) {
          groups[leagueName] = [];
        }

        groups[leagueName].push(match);

        return groups;

      },
      {}
    );


  function changeDay(amount: number) {

    setSelectedDate((currentDate) => {

      const nextDate =
        new Date(currentDate);

      nextDate.setDate(
        nextDate.getDate() + amount
      );

      return nextDate;

    });

  }


  function goToToday() {
    setSelectedDate(new Date());
  }


  return (
    <main className="matches-page">

      {/* PAGE HEADING */}

      <div className="matches-heading">

        <div>

          <h1>
            Matches
          </h1>

          <p>
            All matches for the selected date.
          </p>

        </div>


        <select defaultValue="2026">

          <option value="2026">
            2026/27 Season
          </option>

        </select>

      </div>


      {/* DATE NAVIGATION */}

      <section className="match-date-navigation">

        <button
          className="date-arrow"
          type="button"
          onClick={() => changeDay(-1)}
        >
          ‹
        </button>


        <div className="selected-date">

          <span className="calendar-icon">
            ▣
          </span>


          <div>

            <strong>
              {formatDate(selectedDate)}
            </strong>


            {isSameDay(
              selectedDate,
              today
            ) ? (

              <span className="today-label">
                Today
              </span>

            ) : (

              <button
                type="button"
                className="return-today"
                onClick={goToToday}
              >
                Return to Today
              </button>

            )}

          </div>

        </div>


        <button
          className="date-arrow"
          type="button"
          onClick={() => changeDay(1)}
        >
          ›
        </button>

      </section>


      {/* LOADING */}

      {loading && (

        <section className="no-matches">

          <h2>
            Loading Matches...
          </h2>

        </section>

      )}


      {/* ERROR */}

      {!loading && error && (

        <section className="no-matches">

          <h2>
            Unable to Load Matches
          </h2>

          <p>
            {error}
          </p>

        </section>

      )}


      {/* MATCHES */}

      {!loading && !error && matches.length > 0 && (

        <section className="league-match-sections">

          {Object.entries(matchesByLeague).map(
            ([leagueName, leagueMatches]) => (

              <section
                className="match-league-card"
                key={leagueName}
              >

                {/* LEAGUE HEADER */}

                <div className="match-league-header">

                  <div className="match-league-title">

                    <div className="match-league-logo">

                      {leagueMatches[0]
                        .league
                        .logoUrl ? (

                        <img
                          src={
                            leagueMatches[0]
                              .league
                              .logoUrl
                          }
                          alt={`${leagueName} logo`}
                        />

                      ) : (

                        <span>
                          PL
                        </span>

                      )}

                    </div>


                    <h2>
                      {leagueName}
                    </h2>

                  </div>


                  <span>

                    {leagueMatches.length}{" "}

                    {leagueMatches.length === 1
                      ? "Match"
                      : "Matches"}

                  </span>

                </div>


                {/* MATCH ROWS */}

                <div className="match-list">

                  {leagueMatches.map((match) => {

                    const matchFinished =
                      match.score.home !== null &&
                      match.score.away !== null;


                    return (

                      <div
                        className="match-row"
                        key={match.id}
                      >

                        {/* TIME */}

                        <span className="match-time">

                          {match.status.short === "FT"
                            ? "FT"
                            : formatMatchTime(
                                match.date
                              )}

                        </span>


                        {/* HOME TEAM */}

                        <div className="match-team home-team">

                          <span>
                            {match.homeTeam.name}
                          </span>


                          <div className="match-team-logo">

                            {match.homeTeam.logoUrl ? (

                              <img
                                src={
                                  match.homeTeam
                                    .logoUrl
                                }
                                alt={
                                  match.homeTeam
                                    .name
                                }
                              />

                            ) : (

                              <span>
                                {match.homeTeam.code}
                              </span>

                            )}

                          </div>

                        </div>


                        {/* SCORE / VS */}

                        <div className="match-score">

                          {matchFinished ? (

                            <>

                              <strong>
                                {match.score.home}
                              </strong>

                              <span>
                                -
                              </span>

                              <strong>
                                {match.score.away}
                              </strong>

                            </>

                          ) : (

                            <span className="match-vs">
                              VS
                            </span>

                          )}

                        </div>


                        {/* AWAY TEAM */}

                        <div className="match-team away-team">

                          <div className="match-team-logo">

                            {match.awayTeam.logoUrl ? (

                              <img
                                src={
                                  match.awayTeam
                                    .logoUrl
                                }
                                alt={
                                  match.awayTeam
                                    .name
                                }
                              />

                            ) : (

                              <span>
                                {match.awayTeam.code}
                              </span>

                            )}

                          </div>


                          <span>
                            {match.awayTeam.name}
                          </span>

                        </div>


                        {/* VIEW MATCH */}

                        <button
                          type="button"
                          className="view-match-button"
                        >
                          View
                          <span>→</span>
                        </button>

                      </div>

                    );

                  })}

                </div>

              </section>

            )
          )}

        </section>

      )}


      {/* NO MATCHES */}

      {!loading &&
        !error &&
        matches.length === 0 && (

          <section className="no-matches">

            <h2>
              No Matches
            </h2>

            <p>
              FutBud is not tracking any matches
              for this date.
            </p>

          </section>

        )}

    </main>
  );
}


export default Matches;