import "./LeagueDetails.css";

import {
  Link as PlayerLink,
  useParams,
} from "react-router";

import TeamLink from "../../components/TeamLink/TeamLink";

import {
  useEffect,
  useMemo,
  useState,
} from "react";


import {
  getLeague,
  getStandings,
  getMatchweek,
  getLeagueLeaders,

  type League,
  type Standing,
  type Matchweek,
  type LeagueLeaders,
  type StatLeader,
} from "../../services/leagueService";

function getQualificationClass(
  description: string | null
) {
  if (!description) {
    return "";
  }

  const value =
    description.toLowerCase();

  if (
    value.includes("champions league")
  ) {
    return "qualification-champions";
  }

  if (
    value.includes("europa league")
  ) {
    return "qualification-europa";
  }

  if (
    value.includes("conference league")
  ) {
    return "qualification-conference";
  }

  if (
    value.includes("relegation")
  ) {
    return "qualification-relegation";
  }

  if (
    value.includes("qualif")
  ) {
    return "qualification-playoff";
  }

  return "";
}


function dateKey(
  dateString: string
) {
  const date =
    new Date(dateString);

  return date.toLocaleDateString(
    "en-US",
    {
      weekday: "long",
      month: "long",
      day: "numeric",
    }
  );
}


function matchTime(
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


function LeaderCard({
  title,
  label,
  players,
}: {
  title: string;
  label: string;
  players: StatLeader[];
}) {

  return (
    <section className="league-leader-card">

      <h2>
        {title}
      </h2>

      <div className="league-leader-list">

        {players.map(
          (leader, index) => (

            <PlayerLink
                to={`/players/${leader.player.id}`}
                className="league-leader-row"
                key={leader.player.id}
              >

              <span className="league-leader-rank">
                {index + 1}
              </span>


              <div className="league-player-photo">

                {leader.player.photoUrl && (

                  <img
                    src={
                      leader.player.photoUrl
                    }
                    alt={
                      leader.player.name
                    }
                  />

                )}

              </div>


              <div className="league-player-info">

                <strong>
                  {leader.player.name}
                </strong>

                <span>
                  {leader.team?.name || ""}
                </span>

              </div>


              <div className="league-player-value">

                <strong>
                  {leader.value}
                </strong>

                <span>
                  {label}
                </span>

              </div>

            </PlayerLink>

          )
        )}

      </div>

    </section>
  );
}


function LeagueDetails() {

  const { leagueId } =
    useParams();

  const [league, setLeague] =
    useState<League | null>(null);

  const [standings, setStandings] =
    useState<Standing[]>([]);

  const [matchweek, setMatchweek] =
    useState<Matchweek | null>(null);

  const [leaders, setLeaders] =
    useState<LeagueLeaders | null>(
      null
    );

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);


  useEffect(() => {

    const id = Number(
      leagueId
    );

    if (
      !leagueId ||
      Number.isNaN(id)
    ) {

      setError(
        "Invalid league."
      );

      setLoading(false);

      return;
    }


    setLoading(true);
    setError(null);


    Promise.all([
      getLeague(id),
      getStandings(id),
      getMatchweek(id),
      getLeagueLeaders(id),
    ])
      .then(
        ([
          leagueData,
          standingsData,
          matchweekData,
          leaderData,
        ]) => {

          setLeague(
            leagueData
          );

          setStandings(
            standingsData
          );

          setMatchweek(
            matchweekData
          );

          setLeaders(
            leaderData
          );

        }
      )
      .catch((error) => {

        console.error(
          error
        );

        setError(
          "Unable to load league."
        );

      })
      .finally(() => {

        setLoading(false);

      });

  }, [leagueId]);


  const matchesByDate =
    useMemo(() => {

      const groups =
        new Map<
          string,
          NonNullable<
            typeof matchweek
          >["matches"]
        >();

      if (!matchweek) {
        return [];
      }

      matchweek.matches.forEach(
        (match) => {

          const date =
            dateKey(
              match.date
            );

          if (
            !groups.has(date)
          ) {

            groups.set(
              date,
              []
            );

          }

          groups
            .get(date)!
            .push(match);

        }
      );

      return Array.from(
        groups.entries()
      );

    }, [matchweek]);


  if (loading) {

    return (
      <main className="league-details-page">
        Loading league...
      </main>
    );

  }


  if (
    error ||
    !league
  ) {

    return (
      <main className="league-details-page">

        <h1>
          League unavailable
        </h1>

        <p>
          {error}
        </p>

      </main>
    );

  }


  return (
    <main className="league-details-page">

      {/* HEADER */}

      <header className="league-details-header">

        <div className="league-title-group">

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


          <div>

            <h1>
              {league.name}
            </h1>

            <span>
              {league.country}
              {" · "}
              2026/27
            </span>

          </div>

        </div>

      </header>


      {/* TOP ROW */}

      <section className="league-main-grid">

        {/* STANDINGS */}

        <section className="league-standings-card">

          <div className="standings-header">

            <h2>
              Standings
            </h2>

          </div>


          <div className="standings-table">

            <div className="standing-row standing-heading">

              <span>#</span>
              <span>Team</span>

              <span>P</span>
              <span>W</span>
              <span>D</span>
              <span>L</span>

              <span>+/-</span>

              <span>GD</span>

              <span>PTS</span>

            </div>


            {standings.map(
              (standing) => (

                <div
                  className={`standing-row ${getQualificationClass(
                    standing.description
                  )}`}
                  key={standing.team.id}
                  title={
                    standing.description || ""
                  }
                >

                  <span>
                    {
                      standing.rank
                    }
                  </span>


                  <TeamLink
                    teamId={standing.team.id}
                    name={standing.team.name}
                    logoUrl={standing.team.logoUrl}
                    className="standing-team"
                  />


                  <span>
                    {
                      standing.played
                    }
                  </span>

                  <span>
                    {
                      standing.wins
                    }
                  </span>

                  <span>
                    {
                      standing.draws
                    }
                  </span>

                  <span>
                    {
                      standing.losses
                    }
                  </span>


                  <span>
                    {
                      standing.goalsFor
                    }
                    /
                    {
                      standing.goalsAgainst
                    }
                  </span>


                  <span>
                    {standing
                      .goalDifference >
                    0
                      ? "+"
                      : ""}

                    {
                      standing
                        .goalDifference
                    }
                  </span>


                  <strong className="standing-points">

                    {
                      standing.points
                    }

                  </strong>

                </div>

              )
            )}

          </div>

        </section>


        {/* MATCHWEEK */}

        <aside className="league-matchweek-card">

          <div className="matchweek-header">

            <div>

              <span>
                Current Matchweek
              </span>

              <h2>
                {matchweek?.round ||
                  "Matchweek"}
              </h2>

            </div>

          </div>


          <div className="matchweek-days">

            {matchesByDate.map(
              ([date, matches]) => (

                <section
                  className="matchweek-day"
                  key={date}
                >

                  <h3>
                    {date}
                  </h3>


                  {matches.map(
                    (match) => {

                      const finished =
                        match.status
                          .short ===
                          "FT";

                      return (

                        <div
                          className="league-fixture-row"
                          key={
                            match.id
                          }
                        >

                          <div className="fixture-team fixture-home">

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


                          <div className="fixture-time">

                            {finished ? (

                              <strong>
                                {
                                  match
                                    .score
                                    .home
                                }
                                -
                                {
                                  match
                                    .score
                                    .away
                                }
                              </strong>

                            ) : (

                              <strong>
                                {matchTime(
                                  match.date
                                )}
                              </strong>

                            )}

                          </div>


                          <div className="fixture-team">

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

                      );

                    }
                  )}

                </section>

              )
            )}

          </div>

        </aside>

      </section>


      {/* LEADERS */}

      {leaders && (

        <section className="league-leaders-grid">

          <LeaderCard
            title="Top Goalscorers"
            label="Goals"
            players={
              leaders.goals
            }
          />


          <LeaderCard
            title="Top Assisters"
            label="Assists"
            players={
              leaders.assists
            }
          />


          <LeaderCard
            title="Most Key Passes"
            label="Key Passes"
            players={
              leaders.keyPasses
            }
          />

        </section>

      )}

    </main>
  );
}


export default LeagueDetails;