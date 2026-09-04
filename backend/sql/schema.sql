-- =========================================
-- FUTBUD DATABASE SCHEMA
-- Core tables
-- =========================================


-- Remove our early test tables
DROP TABLE IF EXISTS players CASCADE;
DROP TABLE IF EXISTS teams CASCADE;

DROP TABLE IF EXISTS matches CASCADE;
DROP TABLE IF EXISTS player_team_history CASCADE;
DROP TABLE IF EXISTS league_seasons CASCADE;
DROP TABLE IF EXISTS leagues CASCADE;


-- =========================================
-- LEAGUES
-- API-Football league ID is our ID
-- =========================================

CREATE TABLE leagues (
    id INTEGER PRIMARY KEY,

    name VARCHAR(100) NOT NULL,
    country VARCHAR(100),
    type VARCHAR(30),

    logo_url TEXT,
    country_flag_url TEXT
);


-- =========================================
-- LEAGUE SEASONS
-- Example:
-- Premier League + 2026
-- =========================================

CREATE TABLE league_seasons (
    league_id INTEGER NOT NULL,
    season INTEGER NOT NULL,

    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,

    PRIMARY KEY (league_id, season),

    FOREIGN KEY (league_id)
        REFERENCES leagues(id)
        ON DELETE CASCADE
);


-- =========================================
-- TEAMS
-- API-Football team ID is our ID
-- =========================================

CREATE TABLE teams (
    id INTEGER PRIMARY KEY,

    name VARCHAR(100) NOT NULL,
    code VARCHAR(10),
    country VARCHAR(100),

    founded SMALLINT,
    is_national BOOLEAN DEFAULT FALSE,

    logo_url TEXT,

    venue_id INTEGER,
    venue_name VARCHAR(150),
    venue_city VARCHAR(100),
    venue_capacity INTEGER,
    venue_image_url TEXT
);


-- =========================================
-- PLAYERS
-- API-Football player ID is our ID
-- =========================================

CREATE TABLE players (
    id INTEGER PRIMARY KEY,

    name VARCHAR(150) NOT NULL,
    firstname VARCHAR(100),
    lastname VARCHAR(100),

    birth_date DATE,
    birth_place VARCHAR(100),
    birth_country VARCHAR(100),

    nationality VARCHAR(100),

    height VARCHAR(20),
    weight VARCHAR(20),

    primary_position VARCHAR(30),

    photo_url TEXT
);


-- =========================================
-- PLAYER TEAM HISTORY
--
-- Handles transfers during a season.
--
-- Example:
-- Player starts at Chelsea,
-- moves to Arsenal in January.
-- =========================================

CREATE TABLE player_team_history (
    id BIGSERIAL PRIMARY KEY,

    player_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,

    season INTEGER NOT NULL,

    joined_date DATE,
    left_date DATE,

    shirt_number INTEGER,
    position VARCHAR(30),

    FOREIGN KEY (player_id)
        REFERENCES players(id)
        ON DELETE CASCADE,

    FOREIGN KEY (team_id)
        REFERENCES teams(id)
        ON DELETE CASCADE
);


-- =========================================
-- MATCHES
-- API-Football fixture ID is our ID
-- =========================================

CREATE TABLE matches (
    id INTEGER PRIMARY KEY,

    league_id INTEGER NOT NULL,
    season INTEGER NOT NULL,

    round VARCHAR(100),

    match_date TIMESTAMPTZ NOT NULL,

    referee VARCHAR(150),

    venue_id INTEGER,
    venue_name VARCHAR(150),

    status_long VARCHAR(50),
    status_short VARCHAR(10),
    elapsed INTEGER,

    home_team_id INTEGER NOT NULL,
    away_team_id INTEGER NOT NULL,

    home_goals INTEGER,
    away_goals INTEGER,

    halftime_home INTEGER,
    halftime_away INTEGER,

    fulltime_home INTEGER,
    fulltime_away INTEGER,

    extra_time_home INTEGER,
    extra_time_away INTEGER,

    penalty_home INTEGER,
    penalty_away INTEGER,

    FOREIGN KEY (league_id, season)
        REFERENCES league_seasons(league_id, season),

    FOREIGN KEY (home_team_id)
        REFERENCES teams(id),

    FOREIGN KEY (away_team_id)
        REFERENCES teams(id)
);


-- =========================================
-- INDEXES
-- These make common searches faster
-- =========================================

CREATE INDEX idx_matches_date
ON matches(match_date);

CREATE INDEX idx_matches_home_team
ON matches(home_team_id);

CREATE INDEX idx_matches_away_team
ON matches(away_team_id);

CREATE INDEX idx_player_team_history_player
ON player_team_history(player_id);

CREATE INDEX idx_player_team_history_team
ON player_team_history(team_id);