import {
  useEffect,
  useMemo,
  useState,
} from "react";

import { Link as RouterLink } from "react-router";

import {
  getArchetypeRankings,
  getArchetypes,
  getPositionGroupRankings,
  type ArchetypeGroup,
  type ArchetypeRankedPlayer,
  type ArchetypeRankingsResponse,
} from "../../services/rankingService.ts";


const TIER_ORDER = [
  "Elite",
  "Excellent",
  "Very Good",
  "Good",
  "Average",
  "Below Average",
  "Poor",
];


function initials(name: string) {
  return name
    .split(" ")
    .filter(Boolean)
    .map(word => word[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}


function statusClass(status: string | null) {
  return status
    ? status.toLowerCase().replaceAll(" ", "-")
    : "unrated";
}


function ordinal(value: number | null) {
  if (value === null) {
    return "—";
  }

  const rounded = Math.round(value);
  const remainder100 = rounded % 100;
  const remainder10 = rounded % 10;
  let suffix = "th";

  if (remainder100 < 11 || remainder100 > 13) {
    if (remainder10 === 1) suffix = "st";
    if (remainder10 === 2) suffix = "nd";
    if (remainder10 === 3) suffix = "rd";
  }

  return `${value.toFixed(1)}${suffix}`;
}


function PlayerImage({
  player,
}: {
  player: ArchetypeRankedPlayer;
}) {
  const [failed, setFailed] = useState(false);

  return (
    <div className="archetype-player-avatar">
      {player.photoUrl && !failed ? (
        <img
          src={player.photoUrl}
          alt=""
          onError={() => setFailed(true)}
        />
      ) : (
        <span>{initials(player.name)}</span>
      )}
    </div>
  );
}


function TeamIdentity({
  player,
}: {
  player: ArchetypeRankedPlayer;
}) {
  const [failed, setFailed] = useState(false);

  return (
    <span className="archetype-team">
      {player.team?.logoUrl && !failed && (
        <img
          src={player.team.logoUrl}
          alt=""
          onError={() => setFailed(true)}
        />
      )}
      <span>{player.team?.name || "No club"}</span>
    </span>
  );
}


function TopPlayerCard({
  player,
}: {
  player: ArchetypeRankedPlayer;
}) {
  return (
    <RouterLink
      to={`/players/${player.id}`}
      className="archetype-top-player"
    >
      <div className="archetype-top-player-head">
        <span className="archetype-card-rank">#{player.rank}</span>
        <span className={`ranking-status ${statusClass(player.status)}`}>
          {player.status || "Unrated"}
        </span>
      </div>

      <PlayerImage player={player} />

      <div className="archetype-top-player-name">
        <strong>{player.name}</strong>
        <TeamIdentity player={player} />
      </div>

      <div className="archetype-player-numbers">
        <div>
          <strong>
            {player.rating !== null ? player.rating.toFixed(1) : "—"}
          </strong>
          <span>FutBud rating</span>
        </div>
        <div>
          <strong>{ordinal(player.percentile)}</strong>
          <span>role percentile</span>
        </div>
        <div>
          <strong>{player.minutes.toLocaleString()}</strong>
          <span>minutes</span>
        </div>
      </div>

      <div className="archetype-strengths">
        <span>Why they rank highly</span>

        {player.topMetrics.length ? (
          <ul>
            {player.topMetrics.map(metric => (
              <li key={metric.key}>
                <span>{metric.name}</span>
                <strong>{ordinal(metric.percentile)}</strong>
              </li>
            ))}
          </ul>
        ) : (
          <p>Metric detail is unavailable.</p>
        )}
      </div>
    </RouterLink>
  );
}


function ArchetypeRankings({
  season,
}: {
  season: number;
}) {
  const [groups, setGroups] = useState<ArchetypeGroup[]>([]);
  const [groupKey, setGroupKey] = useState("defenders");
  const [archetypeKey, setArchetypeKey] = useState("all");
  const [rankings, setRankings] =
    useState<ArchetypeRankingsResponse | null>(null);
  const [listLoading, setListLoading] = useState(true);
  const [rankingsLoading, setRankingsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  const selectedGroup =
    groups.find(group => group.key === groupKey) || groups[0];

  useEffect(() => {
    setListLoading(true);
    setError(null);

    getArchetypes(season)
      .then(data => {
        setGroups(data.groups);
        const firstGroup = data.groups[0];

        if (firstGroup) {
          setGroupKey(firstGroup.key);
          setArchetypeKey("all");
        }
      })
      .catch(caught => {
        setError(
          caught instanceof Error
            ? caught.message
            : "Unable to load archetypes.",
        );
      })
      .finally(() => setListLoading(false));
  }, [season]);

  useEffect(() => {
    if (!archetypeKey || !selectedGroup) return;

    let active = true;
    setRankingsLoading(true);
    setRankings(null);
    setError(null);

    const request = archetypeKey === "all"
      ? getPositionGroupRankings(selectedGroup.position, season)
      : getArchetypeRankings(archetypeKey, season);

    request
      .then(data => {
        if (active) setRankings(data);
      })
      .catch(caught => {
        if (!active) return;
        setError(
          caught instanceof Error
            ? caught.message
            : "Unable to load archetype rankings.",
        );
      })
      .finally(() => {
        if (active) setRankingsLoading(false);
      });

    return () => {
      active = false;
    };
  }, [archetypeKey, season, selectedGroup]);

  const visiblePlayers = useMemo(() => {
    const query = search.trim().toLocaleLowerCase();

    if (!rankings || !query) {
      return rankings?.players || [];
    }

    return rankings.players.filter(player =>
      player.name.toLocaleLowerCase().includes(query)
      || player.team?.name.toLocaleLowerCase().includes(query)
      || player.league?.name.toLocaleLowerCase().includes(query)
    );
  }, [rankings, search]);

  const tiers = useMemo(() => {
    const grouped = new Map<string, ArchetypeRankedPlayer[]>();

    for (const player of visiblePlayers) {
      const status = player.status || "Unrated";
      grouped.set(status, [...(grouped.get(status) || []), player]);
    }

    const ordered = TIER_ORDER
      .filter(status => grouped.has(status))
      .map(status => [status, grouped.get(status) || []] as const);

    for (const [status, players] of grouped) {
      if (!TIER_ORDER.includes(status)) ordered.push([status, players]);
    }

    return ordered;
  }, [visiblePlayers]);

  function chooseGroup(group: ArchetypeGroup) {
    setGroupKey(group.key);
    setArchetypeKey("all");
    setSearch("");
  }

  if (listLoading) {
    return <div className="rankings-state">Loading FutBud archetypes...</div>;
  }

  if (error && !rankings && !groups.length) {
    return (
      <div className="rankings-state error">
        <strong>Archetypes unavailable</strong>
        <span>{error}</span>
      </div>
    );
  }

  return (
    <div className="archetype-rankings">
      <section className="archetype-selector-card">
        <div className="archetype-selector-row">
          <span>Position group</span>
          <div className="archetype-position-buttons">
            {groups.map(group => (
              <button
                type="button"
                key={group.key}
                className={group.key === selectedGroup?.key ? "active" : ""}
                onClick={() => chooseGroup(group)}
              >
                {group.name}
              </button>
            ))}
          </div>
        </div>

        <div className="archetype-choice-grid">
          <button
            type="button"
            className={archetypeKey === "all" ? "active" : ""}
            onClick={() => {
              setArchetypeKey("all");
              setSearch("");
            }}
          >
            <strong>All {selectedGroup?.name}</strong>
            <span>
              {selectedGroup?.archetypes.reduce(
                (total, archetype) => total + archetype.playerCount,
                0,
              ) || 0} players
            </span>
          </button>

          {selectedGroup?.archetypes.map(archetype => (
            <button
              type="button"
              key={archetype.key}
              className={archetype.key === archetypeKey ? "active" : ""}
              onClick={() => {
                setArchetypeKey(archetype.key);
                setSearch("");
              }}
            >
              <strong>{archetype.shortName}</strong>
              <span>{archetype.playerCount} players</span>
            </button>
          ))}
        </div>
      </section>

      {rankingsLoading && (
        <div className="archetype-inline-state">Loading ranking...</div>
      )}

      {error && (
        <div className="archetype-inline-state error">{error}</div>
      )}

      {!rankingsLoading && rankings && (
        <>
          <section className="archetype-overview">
            <div className="archetype-overview-copy">
              <span className="rankings-kicker">
                {rankings.archetype.positionGroup} · FutBud v1
              </span>
              <h2>{rankings.archetype.name}</h2>
              <p>{rankings.archetype.description}</p>
              <span className="archetype-player-count">
                {rankings.archetype.playerCount} rated players
              </span>
            </div>
          </section>

          {rankings.players.length ? (
            <>
              <section className="archetype-top-section">
                <div className="rankings-subheading">
                  <div>
                    <span className="rankings-kicker">Role leaders</span>
                    <h2>Top Players</h2>
                  </div>
                  <p>
                    Ranked by stored FutBud rating, then role percentile.
                  </p>
                </div>

                <div className="archetype-top-grid">
                  {rankings.players.slice(0, 5).map(player => (
                    <TopPlayerCard key={player.id} player={player} />
                  ))}
                </div>
              </section>

              <section className="archetype-tier-section">
                <div className="archetype-tier-heading">
                  <div>
                    <span className="rankings-kicker">Complete ranking</span>
                    <h2>{rankings.archetype.name} Tier List</h2>
                  </div>
                  <label className="archetype-search">
                    <span>Search players</span>
                    <input
                      type="search"
                      value={search}
                      onChange={event => setSearch(event.target.value)}
                      placeholder="Player, team, or league"
                    />
                  </label>
                </div>

                {tiers.length ? (
                  <div className="archetype-tier-list">
                    {tiers.map(([status, players]) => (
                      <section
                        className={`archetype-tier tier-${statusClass(status)}`}
                        key={status}
                      >
                        <div className="archetype-tier-label">
                          <strong>{status}</strong>
                          <span>{players.length}</span>
                        </div>
                        <div className="archetype-tier-players">
                          {players.map(player => (
                            <RouterLink
                              to={`/players/${player.id}`}
                              className="archetype-tier-player"
                              key={player.id}
                            >
                              <PlayerImage player={player} />
                              <div className="archetype-tier-player-copy">
                                <strong>{player.name}</strong>
                                <TeamIdentity player={player} />
                              </div>
                              <div className="archetype-tier-score">
                                <strong>
                                  {player.rating !== null
                                    ? player.rating.toFixed(1)
                                    : "—"}
                                </strong>
                                <span>{ordinal(player.percentile)} pct.</span>
                              </div>
                            </RouterLink>
                          ))}
                        </div>
                      </section>
                    ))}
                  </div>
                ) : (
                  <div className="archetype-empty-state">
                    No players match your search.
                  </div>
                )}
              </section>
            </>
          ) : (
            <div className="archetype-empty-state">
              No eligible players are available for this archetype and season.
            </div>
          )}
        </>
      )}
    </div>
  );
}


export default ArchetypeRankings;
