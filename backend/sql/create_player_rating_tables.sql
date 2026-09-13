CREATE TABLE IF NOT EXISTS player_season_ratings (
    player_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    reference_season INTEGER NOT NULL,

    position VARCHAR(10),

    orientation VARCHAR(20),
    orientation_cluster INTEGER,

    archetype_cluster INTEGER,
    archetype_key VARCHAR(50) NOT NULL,
    archetype_name VARCHAR(100) NOT NULL,

    minutes INTEGER NOT NULL DEFAULT 0,
    appearances INTEGER,
    starts INTEGER,

    latest_team_id INTEGER,
    primary_league_id INTEGER,

    provider_rating NUMERIC(6, 2),

    raw_quality_rating NUMERIC(6, 2),
    minutes_reliability NUMERIC(6, 2),

    futbud_rating NUMERIC(6, 2),

    role_rating_percentile NUMERIC(6, 2),
    quality_status VARCHAR(30),

    quality_metric_count INTEGER,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (player_id, season),

    CONSTRAINT player_season_ratings_player_fk
        FOREIGN KEY (player_id)
        REFERENCES players(id)
        ON DELETE CASCADE,

    CONSTRAINT player_season_ratings_team_fk
        FOREIGN KEY (latest_team_id)
        REFERENCES teams(id)
        ON DELETE SET NULL,

    CONSTRAINT player_season_ratings_league_fk
        FOREIGN KEY (primary_league_id)
        REFERENCES leagues(id)
        ON DELETE SET NULL
);


CREATE TABLE IF NOT EXISTS player_season_rating_metrics (
    player_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    feature VARCHAR(100) NOT NULL,

    archetype_key VARCHAR(50) NOT NULL,
    archetype_name VARCHAR(100) NOT NULL,

    raw_value NUMERIC(14, 6),
    historical_percentile NUMERIC(6, 2),

    weight NUMERIC(8, 6),
    reference_players INTEGER,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (
        player_id,
        season,
        feature
    ),

    CONSTRAINT player_rating_metrics_rating_fk
        FOREIGN KEY (
            player_id,
            season
        )
        REFERENCES player_season_ratings(
            player_id,
            season
        )
        ON DELETE CASCADE
);


CREATE INDEX IF NOT EXISTS idx_player_season_ratings_season
    ON player_season_ratings(season);


CREATE INDEX IF NOT EXISTS idx_player_season_ratings_rating
    ON player_season_ratings(
        season,
        futbud_rating DESC
    );


CREATE INDEX IF NOT EXISTS idx_player_season_ratings_archetype
    ON player_season_ratings(
        season,
        archetype_key
    );


CREATE INDEX IF NOT EXISTS idx_player_rating_metrics_player
    ON player_season_rating_metrics(
        player_id,
        season
    );