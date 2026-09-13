--
-- PostgreSQL database dump
--

\restrict r2zcJFih0PWbLWRxjXHk8yuteqNYPlAANGJkiNkYwhYRwUu6dzeEW2erjYuwQzN

-- Dumped from database version 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: league_seasons; Type: TABLE; Schema: public; Owner: futbud_user
--

CREATE TABLE public.league_seasons (
    league_id integer NOT NULL,
    season integer NOT NULL,
    start_date date,
    end_date date,
    is_current boolean DEFAULT false
);


ALTER TABLE public.league_seasons OWNER TO futbud_user;

--
-- Name: leagues; Type: TABLE; Schema: public; Owner: futbud_user
--

CREATE TABLE public.leagues (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    country character varying(100),
    type character varying(30),
    logo_url text,
    country_flag_url text
);


ALTER TABLE public.leagues OWNER TO futbud_user;

--
-- Name: match_events; Type: TABLE; Schema: public; Owner: futbud_user
--

CREATE TABLE public.match_events (
    match_id integer NOT NULL,
    event_index integer NOT NULL,
    team_id integer,
    player_id integer,
    player_name character varying(100),
    assist_id integer,
    assist_name character varying(100),
    elapsed integer,
    extra integer,
    event_type character varying(30),
    detail character varying(100),
    comments text
);


ALTER TABLE public.match_events OWNER TO futbud_user;

--
-- Name: match_lineups; Type: TABLE; Schema: public; Owner: futbud_user
--

CREATE TABLE public.match_lineups (
    match_id integer NOT NULL,
    team_id integer NOT NULL,
    formation character varying(20),
    coach_id integer,
    coach_name character varying(100),
    coach_photo_url text,
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.match_lineups OWNER TO futbud_user;

--
-- Name: matchday_squad; Type: TABLE; Schema: public; Owner: futbud_user
--

CREATE TABLE public.matchday_squad (
    match_id integer NOT NULL,
    team_id integer NOT NULL,
    player_id integer NOT NULL,
    role character varying(20) NOT NULL,
    shirt_number integer,
    "position" character varying(30),
    updated_at timestamp with time zone DEFAULT now(),
    grid character varying(10)
);


ALTER TABLE public.matchday_squad OWNER TO futbud_user;

--
-- Name: matches; Type: TABLE; Schema: public; Owner: futbud_user
--

CREATE TABLE public.matches (
    id integer NOT NULL,
    league_id integer NOT NULL,
    season integer NOT NULL,
    round character varying(100),
    match_date timestamp with time zone NOT NULL,
    referee character varying(150),
    venue_id integer,
    venue_name character varying(150),
    status_long character varying(50),
    status_short character varying(10),
    elapsed integer,
    home_team_id integer NOT NULL,
    away_team_id integer NOT NULL,
    home_goals integer,
    away_goals integer,
    halftime_home integer,
    halftime_away integer,
    fulltime_home integer,
    fulltime_away integer,
    extra_time_home integer,
    extra_time_away integer,
    penalty_home integer,
    penalty_away integer
);


ALTER TABLE public.matches OWNER TO futbud_user;

--
-- Name: player_match_stats; Type: TABLE; Schema: public; Owner: futbud_user
--

CREATE TABLE public.player_match_stats (
    match_id integer NOT NULL,
    player_id integer NOT NULL,
    team_id integer NOT NULL,
    minutes integer,
    shirt_number integer,
    "position" character varying(30),
    provider_rating numeric(4,2),
    captain boolean,
    substitute boolean,
    offsides integer,
    shots_total integer,
    shots_on_target integer,
    goals integer,
    goals_conceded integer,
    assists integer,
    saves integer,
    passes_total integer,
    key_passes integer,
    pass_accuracy integer,
    tackles integer,
    blocks integer,
    interceptions integer,
    duels_total integer,
    duels_won integer,
    dribbles_attempted integer,
    dribbles_successful integer,
    dribbled_past integer,
    fouls_drawn integer,
    fouls_committed integer,
    yellow_cards integer,
    red_cards integer,
    penalties_won integer,
    penalties_committed integer,
    penalties_scored integer,
    penalties_missed integer,
    penalties_saved integer,
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.player_match_stats OWNER TO futbud_user;

--
-- Name: player_team_history; Type: TABLE; Schema: public; Owner: futbud_user
--

CREATE TABLE public.player_team_history (
    id bigint NOT NULL,
    player_id integer NOT NULL,
    team_id integer NOT NULL,
    season integer NOT NULL,
    joined_date date,
    left_date date,
    shirt_number integer,
    "position" character varying(30)
);


ALTER TABLE public.player_team_history OWNER TO futbud_user;

--
-- Name: player_team_history_id_seq; Type: SEQUENCE; Schema: public; Owner: futbud_user
--

CREATE SEQUENCE public.player_team_history_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.player_team_history_id_seq OWNER TO futbud_user;

--
-- Name: player_team_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: futbud_user
--

ALTER SEQUENCE public.player_team_history_id_seq OWNED BY public.player_team_history.id;


--
-- Name: players; Type: TABLE; Schema: public; Owner: futbud_user
--

CREATE TABLE public.players (
    id integer NOT NULL,
    name character varying(150) NOT NULL,
    firstname character varying(100),
    lastname character varying(100),
    birth_date date,
    birth_place character varying(100),
    birth_country character varying(100),
    nationality character varying(100),
    height character varying(20),
    weight character varying(20),
    primary_position character varying(30),
    photo_url text,
    is_injured boolean DEFAULT false NOT NULL
);


ALTER TABLE public.players OWNER TO futbud_user;

--
-- Name: squads; Type: TABLE; Schema: public; Owner: futbud_user
--

CREATE TABLE public.squads (
    team_id integer NOT NULL,
    player_id integer NOT NULL,
    season integer NOT NULL,
    shirt_number integer,
    "position" character varying(30)
);


ALTER TABLE public.squads OWNER TO futbud_user;

--
-- Name: standings; Type: TABLE; Schema: public; Owner: futbud_user
--

CREATE TABLE public.standings (
    league_id integer NOT NULL,
    season integer NOT NULL,
    team_id integer NOT NULL,
    rank integer NOT NULL,
    points integer,
    goals_difference integer,
    form character varying(20),
    status character varying(20),
    description text,
    played integer,
    wins integer,
    draws integer,
    losses integer,
    goals_for integer,
    goals_against integer,
    home_played integer,
    home_wins integer,
    home_draws integer,
    home_losses integer,
    home_goals_for integer,
    home_goals_against integer,
    away_played integer,
    away_wins integer,
    away_draws integer,
    away_losses integer,
    away_goals_for integer,
    away_goals_against integer,
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.standings OWNER TO futbud_user;

--
-- Name: team_league_seasons; Type: TABLE; Schema: public; Owner: futbud_user
--

CREATE TABLE public.team_league_seasons (
    team_id integer NOT NULL,
    league_id integer NOT NULL,
    season integer NOT NULL
);


ALTER TABLE public.team_league_seasons OWNER TO futbud_user;

--
-- Name: team_match_stats; Type: TABLE; Schema: public; Owner: futbud_user
--

CREATE TABLE public.team_match_stats (
    match_id integer NOT NULL,
    team_id integer NOT NULL,
    shots_on_goal integer,
    shots_off_goal integer,
    total_shots integer,
    blocked_shots integer,
    shots_inside_box integer,
    shots_outside_box integer,
    fouls integer,
    corner_kicks integer,
    offsides integer,
    possession integer,
    yellow_cards integer,
    red_cards integer,
    goalkeeper_saves integer,
    total_passes integer,
    accurate_passes integer,
    pass_accuracy integer,
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.team_match_stats OWNER TO futbud_user;

--
-- Name: teams; Type: TABLE; Schema: public; Owner: futbud_user
--

CREATE TABLE public.teams (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    code character varying(10),
    country character varying(100),
    founded smallint,
    is_national boolean DEFAULT false,
    logo_url text,
    venue_id integer,
    venue_name character varying(150),
    venue_city character varying(100),
    venue_capacity integer,
    venue_image_url text
);


ALTER TABLE public.teams OWNER TO futbud_user;

--
-- Name: player_team_history id; Type: DEFAULT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.player_team_history ALTER COLUMN id SET DEFAULT nextval('public.player_team_history_id_seq'::regclass);


--
-- Name: league_seasons league_seasons_pkey; Type: CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.league_seasons
    ADD CONSTRAINT league_seasons_pkey PRIMARY KEY (league_id, season);


--
-- Name: leagues leagues_pkey; Type: CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.leagues
    ADD CONSTRAINT leagues_pkey PRIMARY KEY (id);


--
-- Name: match_events match_events_pkey; Type: CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.match_events
    ADD CONSTRAINT match_events_pkey PRIMARY KEY (match_id, event_index);


--
-- Name: match_lineups match_lineups_pkey; Type: CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.match_lineups
    ADD CONSTRAINT match_lineups_pkey PRIMARY KEY (match_id, team_id);


--
-- Name: matchday_squad matchday_squad_pkey; Type: CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.matchday_squad
    ADD CONSTRAINT matchday_squad_pkey PRIMARY KEY (match_id, team_id, player_id);


--
-- Name: matches matches_pkey; Type: CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.matches
    ADD CONSTRAINT matches_pkey PRIMARY KEY (id);


--
-- Name: player_match_stats player_match_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.player_match_stats
    ADD CONSTRAINT player_match_stats_pkey PRIMARY KEY (match_id, player_id);


--
-- Name: player_team_history player_team_history_pkey; Type: CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.player_team_history
    ADD CONSTRAINT player_team_history_pkey PRIMARY KEY (id);


--
-- Name: players players_pkey; Type: CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.players
    ADD CONSTRAINT players_pkey PRIMARY KEY (id);


--
-- Name: squads squads_pkey; Type: CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.squads
    ADD CONSTRAINT squads_pkey PRIMARY KEY (team_id, player_id, season);


--
-- Name: standings standings_pkey; Type: CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.standings
    ADD CONSTRAINT standings_pkey PRIMARY KEY (league_id, season, team_id);


--
-- Name: team_league_seasons team_league_seasons_pkey; Type: CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.team_league_seasons
    ADD CONSTRAINT team_league_seasons_pkey PRIMARY KEY (team_id, league_id, season);


--
-- Name: team_match_stats team_match_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.team_match_stats
    ADD CONSTRAINT team_match_stats_pkey PRIMARY KEY (match_id, team_id);


--
-- Name: teams teams_pkey; Type: CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT teams_pkey PRIMARY KEY (id);


--
-- Name: player_team_history unique_player_team_season; Type: CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.player_team_history
    ADD CONSTRAINT unique_player_team_season UNIQUE (player_id, team_id, season);


--
-- Name: idx_matchday_squad_player; Type: INDEX; Schema: public; Owner: futbud_user
--

CREATE INDEX idx_matchday_squad_player ON public.matchday_squad USING btree (player_id);


--
-- Name: idx_matchday_squad_team; Type: INDEX; Schema: public; Owner: futbud_user
--

CREATE INDEX idx_matchday_squad_team ON public.matchday_squad USING btree (team_id);


--
-- Name: idx_matches_away_team; Type: INDEX; Schema: public; Owner: futbud_user
--

CREATE INDEX idx_matches_away_team ON public.matches USING btree (away_team_id);


--
-- Name: idx_matches_date; Type: INDEX; Schema: public; Owner: futbud_user
--

CREATE INDEX idx_matches_date ON public.matches USING btree (match_date);


--
-- Name: idx_matches_home_team; Type: INDEX; Schema: public; Owner: futbud_user
--

CREATE INDEX idx_matches_home_team ON public.matches USING btree (home_team_id);


--
-- Name: idx_player_match_stats_player; Type: INDEX; Schema: public; Owner: futbud_user
--

CREATE INDEX idx_player_match_stats_player ON public.player_match_stats USING btree (player_id);


--
-- Name: idx_player_match_stats_team; Type: INDEX; Schema: public; Owner: futbud_user
--

CREATE INDEX idx_player_match_stats_team ON public.player_match_stats USING btree (team_id);


--
-- Name: idx_player_team_history_player; Type: INDEX; Schema: public; Owner: futbud_user
--

CREATE INDEX idx_player_team_history_player ON public.player_team_history USING btree (player_id);


--
-- Name: idx_player_team_history_team; Type: INDEX; Schema: public; Owner: futbud_user
--

CREATE INDEX idx_player_team_history_team ON public.player_team_history USING btree (team_id);


--
-- Name: idx_standings_rank; Type: INDEX; Schema: public; Owner: futbud_user
--

CREATE INDEX idx_standings_rank ON public.standings USING btree (league_id, season, rank);


--
-- Name: idx_team_match_stats_team; Type: INDEX; Schema: public; Owner: futbud_user
--

CREATE INDEX idx_team_match_stats_team ON public.team_match_stats USING btree (team_id);


--
-- Name: league_seasons league_seasons_league_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.league_seasons
    ADD CONSTRAINT league_seasons_league_id_fkey FOREIGN KEY (league_id) REFERENCES public.leagues(id) ON DELETE CASCADE;


--
-- Name: match_events match_events_match_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.match_events
    ADD CONSTRAINT match_events_match_id_fkey FOREIGN KEY (match_id) REFERENCES public.matches(id) ON DELETE CASCADE;


--
-- Name: match_lineups match_lineups_match_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.match_lineups
    ADD CONSTRAINT match_lineups_match_id_fkey FOREIGN KEY (match_id) REFERENCES public.matches(id) ON DELETE CASCADE;


--
-- Name: match_lineups match_lineups_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.match_lineups
    ADD CONSTRAINT match_lineups_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.teams(id) ON DELETE CASCADE;


--
-- Name: matchday_squad matchday_squad_match_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.matchday_squad
    ADD CONSTRAINT matchday_squad_match_id_fkey FOREIGN KEY (match_id) REFERENCES public.matches(id) ON DELETE CASCADE;


--
-- Name: matchday_squad matchday_squad_player_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.matchday_squad
    ADD CONSTRAINT matchday_squad_player_id_fkey FOREIGN KEY (player_id) REFERENCES public.players(id) ON DELETE CASCADE;


--
-- Name: matchday_squad matchday_squad_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.matchday_squad
    ADD CONSTRAINT matchday_squad_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.teams(id) ON DELETE CASCADE;


--
-- Name: matches matches_away_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.matches
    ADD CONSTRAINT matches_away_team_id_fkey FOREIGN KEY (away_team_id) REFERENCES public.teams(id);


--
-- Name: matches matches_home_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.matches
    ADD CONSTRAINT matches_home_team_id_fkey FOREIGN KEY (home_team_id) REFERENCES public.teams(id);


--
-- Name: matches matches_league_id_season_fkey; Type: FK CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.matches
    ADD CONSTRAINT matches_league_id_season_fkey FOREIGN KEY (league_id, season) REFERENCES public.league_seasons(league_id, season);


--
-- Name: player_match_stats player_match_stats_match_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.player_match_stats
    ADD CONSTRAINT player_match_stats_match_id_fkey FOREIGN KEY (match_id) REFERENCES public.matches(id) ON DELETE CASCADE;


--
-- Name: player_match_stats player_match_stats_player_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.player_match_stats
    ADD CONSTRAINT player_match_stats_player_id_fkey FOREIGN KEY (player_id) REFERENCES public.players(id) ON DELETE CASCADE;


--
-- Name: player_match_stats player_match_stats_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.player_match_stats
    ADD CONSTRAINT player_match_stats_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.teams(id) ON DELETE CASCADE;


--
-- Name: player_team_history player_team_history_player_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.player_team_history
    ADD CONSTRAINT player_team_history_player_id_fkey FOREIGN KEY (player_id) REFERENCES public.players(id) ON DELETE CASCADE;


--
-- Name: player_team_history player_team_history_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.player_team_history
    ADD CONSTRAINT player_team_history_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.teams(id) ON DELETE CASCADE;


--
-- Name: squads squads_player_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.squads
    ADD CONSTRAINT squads_player_id_fkey FOREIGN KEY (player_id) REFERENCES public.players(id) ON DELETE CASCADE;


--
-- Name: squads squads_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.squads
    ADD CONSTRAINT squads_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.teams(id) ON DELETE CASCADE;


--
-- Name: standings standings_league_id_season_fkey; Type: FK CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.standings
    ADD CONSTRAINT standings_league_id_season_fkey FOREIGN KEY (league_id, season) REFERENCES public.league_seasons(league_id, season) ON DELETE CASCADE;


--
-- Name: standings standings_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.standings
    ADD CONSTRAINT standings_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.teams(id) ON DELETE CASCADE;


--
-- Name: team_league_seasons team_league_seasons_league_id_season_fkey; Type: FK CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.team_league_seasons
    ADD CONSTRAINT team_league_seasons_league_id_season_fkey FOREIGN KEY (league_id, season) REFERENCES public.league_seasons(league_id, season) ON DELETE CASCADE;


--
-- Name: team_league_seasons team_league_seasons_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.team_league_seasons
    ADD CONSTRAINT team_league_seasons_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.teams(id) ON DELETE CASCADE;


--
-- Name: team_match_stats team_match_stats_match_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.team_match_stats
    ADD CONSTRAINT team_match_stats_match_id_fkey FOREIGN KEY (match_id) REFERENCES public.matches(id) ON DELETE CASCADE;


--
-- Name: team_match_stats team_match_stats_team_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: futbud_user
--

ALTER TABLE ONLY public.team_match_stats
    ADD CONSTRAINT team_match_stats_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.teams(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict r2zcJFih0PWbLWRxjXHk8yuteqNYPlAANGJkiNkYwhYRwUu6dzeEW2erjYuwQzN

