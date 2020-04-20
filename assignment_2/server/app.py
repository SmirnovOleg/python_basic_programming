import json
import sqlite3

from flask import Flask, g, request
from flask_cors import CORS

from parsing import parse_pcgamer_website, parse_tomshardware_website

app = Flask(__name__)
CORS(app)
DATABASE = 'my_database.sqlite'


def get_db():
    db_conn = getattr(g, '_database', None)
    if db_conn is None:
        db_conn = g._database = sqlite3.connect(DATABASE)
    return db_conn


def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.executescript(
            '''CREATE TABLE IF NOT EXISTS GraphicUnits (
                   name TEXT PRIMARY KEY,
                   score FLOAT,
                   boost_freq TEXT NOT NULL,
                   memory TEXT NOT NULL,
                   power TEXT,
                   cuda_cores INTEGER,
                   buy_link TEXT
                );
            '''
        )
        db.commit()


def add_item_to_db(data, cursor):
    name = data.get('name', 'null')
    score = data.get('score', 'null')
    boost_freq = data.get('boost_freq', 'null')
    memory = data.get('memory', 'null')
    power = data.get('power', 'null')
    cuda_cores = data.get('cuda_cores', 'null')
    buy_link = data.get('buy_link', 'null')
    query = f"INSERT INTO GraphicUnits (name, score, boost_freq, memory, power, cuda_cores, buy_link) " \
            f"VALUES ('{name}', {score}, '{boost_freq}', '{memory}', '{power}', {cuda_cores}, '{buy_link}') " \
            f"ON CONFLICT (name) DO UPDATE SET cuda_cores={cuda_cores}"
    cursor.execute(query)


def update_initial_content():
    with app.app_context():
        db_conn = get_db()
        cursor = db_conn.cursor()
        for item in parse_tomshardware_website():
            add_item_to_db(item, cursor)
        for item in parse_pcgamer_website():
            add_item_to_db(item, cursor)
        db_conn.commit()


@app.route('/get_all')
def get_all():
    with app.app_context():
        db_cursor = get_db().cursor()
        db_cursor.row_factory = sqlite3.Row
        db_cursor.execute('SELECT * FROM GraphicUnits')
        result = db_cursor.fetchall()
        json_result = json.dumps([dict(row) for row in result])
        return json_result


@app.route('/create_new', methods=['POST'])
def create_new():
    data = request.get_json()
    print(data)
    return add_item_to_db(data)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    init_db()
    update_initial_content()
    app.run()
