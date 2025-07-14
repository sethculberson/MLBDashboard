import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, MetaData, Table
from sqlalchemy.schema import ForeignKeyConstraint
from sqlalchemy.dialects import mysql
from sqlalchemy.exc import SQLAlchemyError
import re

DB_CONFIG = {
    'host':'localhost',
    'database':'baseball_analytics',
    'user':'root',
    'password':'#S3thIsCoo105302005',
    'port':3306
}

CSV_FILE_PATH = '2025MLB_STD_Batting.csv'

def generate_player_id(player_name, age=None, team=None, season=None):
    """
    Generates a slug-like player_id from the player's name.
    If age, team, or season are provided, they are appended to help differentiate
    players with identical names (e.g., "mike_trout_28_angels_2023").
    This helps ensure unique IDs for the database, especially when canonical IDs
    are not available.
    """
    if pd.isna(player_name):
        return None
    name = str(player_name).strip().lower()
    # Replace non-alphanumeric characters (except spaces) with nothing, then spaces with underscores
    name_slug = re.sub(r'[^a-z0-9\s]', '', name)
    name_slug = re.sub(r'\s+', '_', name_slug)

    # Append disambiguating factors if provided
    parts = [name_slug]
    if age is not None:
        parts.append(str(age))
    if team and str(team).strip() != 'N/A': # Only append if not empty/default
        parts.append(str(team).lower().replace(' ', '_')) # Slugify team name too
    if season is not None:
        parts.append(str(season))

    # Join the parts to form the final player_id
    # Ensure the length doesn't exceed 50 characters (VARCHAR(50))
    full_id = "_".join(parts)
    return full_id[:50] # Truncate to ensure it fits VARCHAR(50)

# --- Function to create SQLAlchemy engine and define tables ---
def setup_database_schema(db_config):
    """
    Sets up the SQLAlchemy engine and defines the table schemas.
    """
    db_url = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    engine = create_engine(db_url, echo=False) # Set echo=True to see generated SQL queries

    metadata = MetaData()

    # Define the players table
    players_table = Table(
        'players', metadata,
        Column('player_id', String(50), primary_key=True),
        Column('player_name', String(255), nullable=False),
        Column('primary_position', String(50), nullable=True),
        Column('mlb_debut_year', Integer, nullable=True)
    )

    # Define the player_stats table
    player_stats_table = Table(
        'player_stats', metadata,
        Column('stat_id', Integer, primary_key=True, autoincrement=True),
        Column('player_id', String(50), nullable=False),
        Column('season', Integer, nullable=False),
        Column('team', String(10), nullable=False),
        Column('games_played', Integer, nullable=True),
        Column('at_bats', Integer, nullable=True),
        Column('runs', Integer, nullable=True),
        Column('hits', Integer, nullable=True),
        Column('doubles', Integer, nullable=True),
        Column('triples', Integer, nullable=True),
        Column('home_runs', Integer, nullable=True),
        Column('rbi', Integer, nullable=True),
        Column('walks', Integer, nullable=True),
        Column('strikeouts', Integer, nullable=True),
        Column('obp', DECIMAL(5,3), nullable=True),
        Column('slg', DECIMAL(5,3), nullable=True),
        Column('ops', DECIMAL(5,3), nullable=True),
        Column('war', DECIMAL(5,2), nullable=True),
        Column('sb', Integer, nullable=True),
        Column('cs', Integer, nullable=True),
        Column('ops_plus', DECIMAL(5,1), nullable=True),
        Column('roba', DECIMAL(5,3), nullable=True),
        Column('rbat_plus', DECIMAL(5,1), nullable=True),
        Column('tb', Integer, nullable=True),
        Column('gidp', Integer, nullable=True),
        Column('hbp', Integer, nullable=True),
        Column('sh', Integer, nullable=True),
        Column('sf', Integer, nullable=True),
        Column('ibb', Integer, nullable=True),
        Column('position_played', String(50), nullable=True),
        Column('lg', String(10), nullable=True),
        ForeignKeyConstraint(['player_id'], ['players.player_id']) # Foreign key constraint
    )

    # Create all tables in the database (if they don't already exist)
    # This is a convenient way to ensure your schema matches your model
    try:
        metadata.create_all(engine)
        print("Database tables ensured to exist.")
    except SQLAlchemyError as e:
        print(f"Error creating tables: {e}")
        # If tables already exist, this might just pass, but catch for other errors.

    return engine, players_table, player_stats_table

# --- Function to insert data into players table ---
def insert_player(connection, players_table, player_id, player_name):
    """
    Inserts a player into the 'players' table if they don't already exist.
    """
    # Check if player already exists
    # Use SQLAlchemy's select() to build the query
    s = players_table.select().where(players_table.c.player_id == player_id)
    result = connection.execute(s).fetchone()

    if not result:
        # Use SQLAlchemy's insert() to build the insert statement
        ins = players_table.insert().values(
            player_id=player_id,
            player_name=player_name,
            primary_position=None, # Will be NULL for now
            mlb_debut_year=None     # Will be NULL for now
        )
        try:
            connection.execute(ins)
            connection.commit()
            print(f"Inserted new player: {player_name} (ID: {player_id})")
        except SQLAlchemyError as e:
            print(f"Error inserting player {player_name} (ID: {player_id}): {e}")
            connection.rollback() # Rollback on error
    # else:
        # print(f"Player {player_name} (ID: {player_id}) already exists.") # Uncomment for verbose output


# --- Function to insert data into player_stats table ---
def insert_player_stat(connection, player_stats_table, stat_data):
    """
    Inserts a single row of player statistics into the 'player_stats' table.
    """
    # Using a dictionary for insert values is generally more readable with SQLAlchemy
    ins = player_stats_table.insert().values(**stat_data)
    try:
        connection.execute(ins)
        connection.commit()
        print(f"Inserted stats for {stat_data['player_id']} in season {stat_data['season']} with team {stat_data['team']}")
    except SQLAlchemyError as e:
        print(f"Error inserting stats for {stat_data['player_id']} in season {stat_data['season']} (Team: {stat_data['team']}): {e}")
        connection.rollback() # Rollback on error

# --- Main script execution ---
if __name__ == "__main__":
    # Setup database engine and table objects
    engine, players_table, player_stats_table = setup_database_schema(DB_CONFIG)

    if engine:
        # Use a context manager for the connection
        with engine.connect() as conn:
            try:
                # Read the CSV file into a pandas DataFrame
                df = pd.read_csv(CSV_FILE_PATH)
                print(f"Loaded {len(df)} rows from {CSV_FILE_PATH}")

                # Rename columns to match database schema conventions where necessary
                # Make sure these match your CSV headers exactly!
                df = df.rename(columns={
                    'Player': 'player_name',
                    'Team': 'team',
                    'Lg': 'lg',
                    'G': 'games_played',
                    'PA': 'plate_appearances', # Not directly used in DB schema, but useful if needed later
                    'AB': 'at_bats',
                    'R': 'runs',
                    'H': 'hits',
                    '2B': 'doubles',
                    '3B': 'triples',
                    'HR': 'home_runs',
                    'RBI': 'rbi',
                    'SB': 'sb',
                    'CS': 'cs',
                    'BB': 'walks',
                    'SO': 'strikeouts',
                    'BA': 'batting_average', # Not directly used in DB schema, but useful if needed later
                    'OBP': 'obp',
                    'SLG': 'slg',
                    'OPS': 'ops',
                    'OPS+': 'ops_plus',
                    'rOBA': 'roba',
                    'Rbat+': 'rbat_plus',
                    'TB': 'tb',
                    'GIDP': 'gidp',
                    'HBP': 'hbp',
                    'SH': 'sh',
                    'SF': 'sf',
                    'IBB': 'ibb',
                    'Pos': 'position_played',
                    'WAR': 'war',
                    'Age': 'age' # Add age for potential future use or to infer season
                })

                # --- Data Cleaning and Type Conversion ---
                # Handle 'season' column
                # If your CSV *does not* have a 'season' column, you must infer it.
                # A common approach for single-season CSVs is to define it.
                # If your data comes from a source like Baseball-Reference yearly pages,
                # the year is often implicit or in the filename.
                if 'season' not in df.columns:
                    print("Warning: 'season' column not found. Assuming data is for 2023. Please verify.")
                    df['season'] = 2023 # Default to a recent year, adjust as needed


                # Define numerical columns for type conversion and NaN filling
                numerical_cols_to_fill = [
                    'games_played', 'at_bats', 'runs', 'hits', 'doubles', 'triples',
                    'home_runs', 'rbi', 'walks', 'strikeouts', 'sb', 'cs', 'tb',
                    'gidp', 'hbp', 'sh', 'sf', 'ibb', 'age', 'season' # Added season and age to numerical if they are in CSV
                ]
                decimal_cols_to_fill = [
                    'obp', 'slg', 'ops', 'war', 'ops_plus', 'roba', 'rbat_plus'
                ]

                # Apply type conversion and NaN filling
                for col in numerical_cols_to_fill:
                    if col in df.columns:
                        # Convert to numeric, coercing errors to NaN, then fill NaN, then convert to int
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
                for col in decimal_cols_to_fill:
                    if col in df.columns:
                        # Convert to numeric, coercing errors to NaN, then fill NaN, then convert to float
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0).astype(float)

                # Ensure string columns don't have NaN and are converted to string
                string_cols = ['player_name', 'team', 'lg', 'position_played']
                for col in string_cols:
                    if col in df.columns:
                        df[col] = df[col].fillna('N/A').astype(str)

                # Generate player_id for each row using multiple columns for uniqueness
                # Apply across rows (axis=1) to use age, team, and season
                df['player_id'] = df.apply(
                    lambda row: generate_player_id(
                        row['player_name'],
                        row.get('age'), # .get() to handle cases where 'age' might not be in the CSV
                        row.get('team'),
                        row.get('season')
                    ),
                    axis=1
                )

                # Drop rows where player_id could not be generated (e.g., missing name after string conversion)
                df.dropna(subset=['player_id', 'player_name'], inplace=True)
                if df.empty:
                    print("No valid player data to process after cleaning. Exiting.")
                    exit() # Exit if no data is left


                # Iterate over each row in the DataFrame and insert into MySQL
                for index, row in df.iterrows():
                    # Extract values for players table
                    player_id = row['player_id']
                    player_name = row['player_name']

                    # Insert into players table first
                    insert_player(conn, players_table, player_id, player_name) # Corrected call here

                    # Prepare data dictionary for player_stats table
                    # Using a dictionary makes it easier to pass to SQLAlchemy's insert().values()
                    stat_data = {
                        'player_id': player_id,
                        'season': row['season'],
                        'team': row['team'],
                        'games_played': row['games_played'],
                        'at_bats': row['at_bats'],
                        'runs': row['runs'],
                        'hits': row['hits'],
                        'doubles': row['doubles'],
                        'triples': row['triples'],
                        'home_runs': row['home_runs'],
                        'rbi': row['rbi'],
                        'walks': row['walks'],
                        'strikeouts': row['strikeouts'],
                        'obp': row['obp'],
                        'slg': row['slg'],
                        'ops': row['ops'],
                        'war': row['war'],
                        'sb': row['sb'],
                        'cs': row['cs'],
                        'ops_plus': row['ops_plus'],
                        'roba': row['roba'],
                        'rbat_plus': row['rbat_plus'],
                        'tb': row['tb'],
                        'gidp': row['gidp'],
                        'hbp': row['hbp'],
                        'sh': row['sh'],
                        'sf': row['sf'],
                        'ibb': row['ibb'],
                        'position_played': row['position_played'],
                        'lg': row['lg']
                    }
                    insert_player_stat(conn, player_stats_table, stat_data)

            except FileNotFoundError:
                print(f"Error: CSV file not found at {CSV_FILE_PATH}")
            except KeyError as e:
                print(f"Error: Missing expected column in CSV after renaming/processing: {e}. Please check your CSV file's header names and the rename dictionary.")
            except SQLAlchemyError as e:
                print(f"A SQLAlchemy error occurred during data loading: {e}")
            except Exception as e:
                print(f"An unexpected error occurred during data loading: {e}")
            finally:
                pass # Connection is managed by 'with' statement

    else:
        print("Could not establish a database engine. Exiting.")
