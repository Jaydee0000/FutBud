import "./GlobalSearch.css";

import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  useNavigate,
} from "react-router";

import {
  searchFutBud,
  type GlobalSearchResults,
  type SearchPlayer,
  type SearchTeam,
} from "../../services/searchService.ts";


const EMPTY_RESULTS:
  GlobalSearchResults = {
    query: "",
    players: [],
    teams: [],
  };


function SearchIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      aria-hidden="true"
      className="global-search-icon"
    >
      <path
        d="m21 21-4.35-4.35m2.35-5.65a8 8 0 1 1-16 0 8 8 0 0 1 16 0Z"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}


function PlayerResult({
  player,
  onSelect,
}: {
  player: SearchPlayer;
  onSelect: () => void;
}) {

  return (
    <button
      type="button"
      className="global-search-result"
      onClick={onSelect}
    >

      <div className="global-search-result-image player-image">
        {
          player.photoUrl
            ? (
              <img
                src={player.photoUrl}
                alt=""
              />
            )
            : (
              <span>
                {
                  player.name
                    .charAt(0)
                    .toUpperCase()
                }
              </span>
            )
        }
      </div>


      <div className="global-search-result-main">

        <strong>
          {player.name}
        </strong>

        <span>
          {
            player.team?.name
            || player.nationality
            || "Player"
          }
        </span>

      </div>


      <div className="global-search-result-side">

        {
          player.futbudRating !== null
          && (
            <strong className="global-search-rating">
              {player.futbudRating.toFixed(1)}
            </strong>
          )
        }

        <span>
          {player.position || "Player"}
        </span>

      </div>

    </button>
  );
}


function TeamResult({
  team,
  onSelect,
}: {
  team: SearchTeam;
  onSelect: () => void;
}) {

  return (
    <button
      type="button"
      className="global-search-result"
      onClick={onSelect}
    >

      <div className="global-search-result-image team-image">
        {
          team.logoUrl
            ? (
              <img
                src={team.logoUrl}
                alt=""
              />
            )
            : (
              <span>
                {
                  team.code
                  || team.name
                    .slice(0, 2)
                    .toUpperCase()
                }
              </span>
            )
        }
      </div>


      <div className="global-search-result-main">

        <strong>
          {team.name}
        </strong>

        <span>
          {
            team.league?.name
            || team.country
            || "Club"
          }
        </span>

      </div>


      <div className="global-search-result-side">
        <span className="global-search-type">
          Team
        </span>
      </div>

    </button>
  );
}


function GlobalSearch() {

  const navigate =
    useNavigate();

  const containerRef =
    useRef<HTMLDivElement | null>(
      null
    );

  const [query, setQuery] =
    useState("");

  const [results, setResults] =
    useState<GlobalSearchResults>(
      EMPTY_RESULTS
    );

  const [loading, setLoading] =
    useState(false);

  const [open, setOpen] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  useEffect(() => {

    const trimmed =
      query.trim();

    if (trimmed.length < 2) {
      setResults(
        EMPTY_RESULTS
      );
      setLoading(false);
      setError(null);
      return;
    }

    const controller =
      new AbortController();

    const timer =
      window.setTimeout(
        () => {

          setLoading(true);
          setError(null);

          searchFutBud(
            trimmed,
            {
              season: 2026,
              limit: 6,
              signal:
                controller.signal,
            },
          )
            .then(data => {
              setResults(data);
              setOpen(true);
            })
            .catch(searchError => {

              if (
                searchError
                instanceof DOMException
                && searchError.name
                === "AbortError"
              ) {
                return;
              }

              console.error(
                "FutBud search failed:",
                searchError,
              );

              setError(
                "Unable to search right now."
              );

            })
            .finally(() => {
              setLoading(false);
            });

        },
        220,
      );


    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };

  }, [query]);


  useEffect(() => {

    function handlePointerDown(
      event: MouseEvent,
    ) {

      if (
        containerRef.current
        && !containerRef.current.contains(
          event.target as Node
        )
      ) {
        setOpen(false);
      }
    }

    document.addEventListener(
      "mousedown",
      handlePointerDown,
    );

    return () => {
      document.removeEventListener(
        "mousedown",
        handlePointerDown,
      );
    };

  }, []);


  function closeAndClear() {
    setOpen(false);
    setQuery("");
    setResults(
      EMPTY_RESULTS
    );
  }


  function goToPlayer(
    playerId: number,
  ) {
    closeAndClear();
    navigate(
      `/players/${playerId}`
    );
  }


  function goToTeam(
    teamId: number,
  ) {
    closeAndClear();
    navigate(
      `/teams/${teamId}`
    );
  }


  function handleKeyDown(
    event:
      React.KeyboardEvent<HTMLInputElement>,
  ) {

    if (event.key === "Escape") {
      setOpen(false);
      return;
    }

    if (event.key !== "Enter") {
      return;
    }

    const firstPlayer =
      results.players[0];

    const firstTeam =
      results.teams[0];

    if (firstPlayer) {
      goToPlayer(
        firstPlayer.id
      );
      return;
    }

    if (firstTeam) {
      goToTeam(
        firstTeam.id
      );
    }
  }


  const hasResults =
    results.players.length > 0
    || results.teams.length > 0;

  const showDropdown =
    open
    && query.trim().length >= 2;


  return (
    <div
      className="global-search"
      ref={containerRef}
    >

      <div className="global-search-input-wrap">

        <SearchIcon />

        <input
          type="search"
          value={query}
          placeholder="Search players or teams"
          aria-label="Search FutBud players or teams"
          autoComplete="off"
          onChange={event => {
            setQuery(
              event.target.value
            );
            setOpen(true);
          }}
          onFocus={() => {
            if (
              query.trim().length >= 2
            ) {
              setOpen(true);
            }
          }}
          onKeyDown={handleKeyDown}
        />

        {
          loading
          && (
            <span className="global-search-loading">
              Searching
            </span>
          )
        }

      </div>


      {
        showDropdown
        && (
          <div className="global-search-dropdown">

            {
              error
              ? (
                <div className="global-search-message error">
                  {error}
                </div>
              )
              : !loading
                && !hasResults
                ? (
                  <div className="global-search-message">
                    No players or teams found.
                  </div>
                )
                : (
                  <>

                    {
                      results.players.length > 0
                      && (
                        <section className="global-search-group">

                          <div className="global-search-group-title">
                            Players
                          </div>

                          {
                            results.players.map(
                              player => (
                                <PlayerResult
                                  key={player.id}
                                  player={player}
                                  onSelect={() =>
                                    goToPlayer(
                                      player.id
                                    )
                                  }
                                />
                              )
                            )
                          }

                        </section>
                      )
                    }


                    {
                      results.teams.length > 0
                      && (
                        <section className="global-search-group">

                          <div className="global-search-group-title">
                            Teams
                          </div>

                          {
                            results.teams.map(
                              team => (
                                <TeamResult
                                  key={team.id}
                                  team={team}
                                  onSelect={() =>
                                    goToTeam(
                                      team.id
                                    )
                                  }
                                />
                              )
                            )
                          }

                        </section>
                      )
                    }

                  </>
                )
            }

          </div>
        )
      }

    </div>
  );
}


export default GlobalSearch;
