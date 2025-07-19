CREATE DATABASE IF NOT EXISTS baseball_analytics;
USE baseball_analytics;

CREATE TABLE IF NOT EXISTS players (
    player_id VARCHAR(50) PRIMARY KEY,
    player_name VARCHAR(255) NOT NULL,
    primary_position VARCHAR(50),
    mlb_debut_year INT,
    mlbam_id INT UNIQUE,
    batting_hand VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS player_stats (
    stat_id INT AUTO_INCREMENT PRIMARY KEY,
    player_id VARCHAR(50) NOT NULL,
    season INT NOT NULL,
    team VARCHAR(10) NOT NULL,
    games_played INT,
    at_bats INT,
    runs INT,
    hits INT,
    doubles INT,
    triples INT,
    home_runs INT,
    rbi INT,
    walks INT,
    strikeouts INT,
    obp DECIMAL(5,3),
    slg DECIMAL(5,3),
    ops DECIMAL(5,3),
    war DECIMAL(5,2),
    sb INT,
    cs INT,
    ops_plus DECIMAL(5,1),
    roba DECIMAL(5,3),
    rbat_plus DECIMAL(5,1),
    tb INT,
    gidp INT,
    hbp INT,
    sh INT,
    sf INT,
    ibb INT,
    position_played VARCHAR(50),
    lg VARCHAR(10),
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);

CREATE TABLE IF NOT EXISTS player_contracts (
    contract_id INT AUTO_INCREMENT PRIMARY KEY,
    player_id VARCHAR(50) NOT NULL,
    contract_start_year INT,
    contract_end_year INT,
    total_value_usd BIGINT,
    avg_annual_value_usd BIGINT,
    current_year_salary_usd BIGINT,
    year_in_contract INT,
    contract_notes TEXT,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);
