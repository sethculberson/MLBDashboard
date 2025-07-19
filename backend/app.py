from flask import Flask, jsonify
from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, MetaData, Table, and_, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import os
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://localhost", "http://127.0.0.1", "http://localhost:80"]}})

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'mysql_db'),
    'database': os.getenv('DB_DATABASE', 'baseball_analytics'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': int(os.getenv('DB_PORT', 3306))
}

DB_URL = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

engine = None
try:
    engine = create_engine(DB_URL)
    with engine.connect() as connection:
        print("Successfully connected to the database from Flask.")
except SQLAlchemyError as e:
    print(f"Error connecting to database from Flask: {e}")
    engine = None

metadata = MetaData()

players_table = Table(
    'players', metadata,
    Column('player_id', String(50), primary_key=True, unique=True),
    Column('player_name', String(255), nullable=False),
    Column('primary_position', String(50), nullable=True),
    Column('mlb_debut_year', Integer, nullable=True),
    Column('mlbam_id', Integer, unique=True, nullable=True),
    Column('batting_hand', String(10), nullable=True)
)

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
    Column('lg', String(10), nullable=True)
)

player_contracts_table = Table(
    'player_contracts', metadata,
    Column('contract_id', Integer, primary_key=True, autoincrement=True),
    Column('player_id', String(50), nullable=False),
    Column('contract_start_year', Integer, nullable=True),
    Column('contract_end_year', Integer, nullable=True),
    Column('total_value_usd', Integer, nullable=True),
    Column('avg_annual_value_usd', Integer, nullable=True),
    Column('current_year_salary_usd', Integer, nullable=True),
    Column('year_in_contract', Integer, nullable=True),
    Column('contract_notes', String(1000), nullable=True)
)

Session = sessionmaker(bind=engine)

@app.route('/api/players', methods=['GET'])
def get_players():
    if not engine:
        return jsonify({"error": "Database connection not established."}), 500
    session = Session()
    try:
        query = session.query(players_table.c.player_id, players_table.c.player_name)
        players = []
        for player_id, player_name in query.all():
            players.append({'player_id': player_id, 'player_name': player_name})
        return jsonify(players)
    except SQLAlchemyError as e:
        print(f"Error fetching players: {e}")
        return jsonify({"error": "Could not retrieve players."}), 500
    finally:
        session.close()

@app.route('/api/player_contracts/<string:player_id>', methods=['GET'])
def get_player_contracts(player_id):
    if not engine:
        return jsonify({"error": "Database connection not established."}), 500
    session = Session()
    try:
        query = session.query(player_contracts_table).filter(
            player_contracts_table.c.player_id == player_id
        ).order_by(player_contracts_table.c.contract_start_year.desc())

        contracts = []
        for row in query.all():
            contract_dict = {
                'player_id': row.player_id,
                'contract_start_year': row.contract_start_year,
                'contract_end_year': row.contract_end_year,
                'total_value_usd': row.total_value_usd,
                'avg_annual_value_usd': row.avg_annual_value_usd,
                'current_year_salary_usd': row.current_year_salary_usd,
                'year_in_contract': row.year_in_contract,
                'contract_notes': row.contract_notes
            }
            contracts.append(contract_dict)
        if not contracts:
            return jsonify({"message": "No contract data found for this player."}), 404
        return jsonify(contracts[0])
    except SQLAlchemyError as e:
        print(f"Error fetching player contracts for {player_id}: {e}")
        return jsonify({"error": f"Could not retrieve contract data for {player_id}."}), 500
    finally:
        session.close()

@app.route('/api/player_stats/<string:player_id>/<int:season>', methods=['GET'])
def get_player_stats_for_season(player_id, season):
    if not engine:
        return jsonify({"error": "Database connection not established."}), 500
    session = Session()
    try:
        stmt = select(player_stats_table, players_table.c.player_name).join(
            players_table, player_stats_table.c.player_id == players_table.c.player_id
        ).filter(
            and_(player_stats_table.c.player_id == player_id,
                 player_stats_table.c.season == season)
        )
        result_row = session.execute(stmt).fetchone()

        if not result_row:
            return jsonify({"message": "No stats found for this player in the specified season."}), 404

        stats = {}
        for column in player_stats_table.columns:
            value = getattr(result_row, column.name)
            if isinstance(value, type(DECIMAL)):
                stats[column.name] = float(value)
            else:
                stats[column.name] = value
        stats['player_name'] = getattr(result_row, players_table.c.player_name.name)

        return jsonify(stats)
    except SQLAlchemyError as e:
        print(f"Error fetching player stats for {player_id} in {season}: {e}")
        return jsonify({"error": f"Could not retrieve stats for {player_id} in {season}."}), 500
    finally:
        session.close()

@app.route('/api/season_stats/<int:season>', methods=['GET'])
def get_all_player_stats_for_season(season):
    if not engine:
        return jsonify({"error": "Database connection not established."}), 500
    session = Session()
    try:
        stmt = select(player_stats_table, players_table.c.player_name).join(
            players_table, player_stats_table.c.player_id == players_table.c.player_id
        ).filter(player_stats_table.c.season == season)

        results = session.execute(stmt).fetchall()

        if not results:
            return jsonify({"message": f"No stats found for season {season}."}), 404

        all_stats_data = []
        stat_column_names = [col.name for col in player_stats_table.columns]

        for row in results:
            row_dict = {}
            for col_name in stat_column_names:
                value = getattr(row, col_name)
                if isinstance(value, type(DECIMAL)):
                    row_dict[col_name] = float(value)
                else:
                    row_dict[col_name] = value
            row_dict['player_name'] = getattr(row, players_table.c.player_name.name)
            all_stats_data.append(row_dict)

        return jsonify(all_stats_data)
    except SQLAlchemyError as e:
        print(f"Error fetching all player stats for season {season}: {e}")
        return jsonify({"error": f"Could not retrieve all player stats for season {season}."}), 500
    finally:
        session.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)