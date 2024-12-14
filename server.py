from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

DATABASE = 'economicDB.db'

def create_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        ''')

    c.execute('''CREATE TABLE IF NOT EXISTS Region (
      id INTEGER PRIMARY KEY,
      Population INTEGER,
      Square REAL,
      VVP REAL,
      Name VARCHAR(50)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS Statistical_data (
      id INTEGER PRIMARY KEY,
      Date DATE,
      Data VARCHAR(50),
      id_region INTEGER,
      id_branch INTEGER,
      id_show INTEGER,
      FOREIGN KEY (id_region) REFERENCES Region(id),
      FOREIGN KEY (id_branch) REFERENCES Branch(id),
      FOREIGN KEY (id_show) REFERENCES Show(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS Show (
      id INTEGER PRIMARY KEY,
      Name VARCHAR(50),
      Unit_measurement VARCHAR(50)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS Branch (
      id INTEGER PRIMARY KEY,
      Name_branch VARCHAR(50),
      Description VARCHAR(50)
    )''')

    conn.commit()
    conn.close()


create_db()

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

@app.route('/users', methods=['POST'])
def register_user():
    data = request.json
    username = data['username']
    password = data['password']
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return jsonify({"message": "User  registered successfully."}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "User  already exists."}), 400
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    username = data['username']
    password = data['password']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        return jsonify({"message": "Login successful."}), 200
    else:
        return jsonify({"error": "Invalid credentials."}), 401


@app.route('/table/<table_name>', methods=['GET'])
def get_table_data(table_name):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {table_name}')
    rows = cursor.fetchall()
    conn.close()

    return jsonify(rows)

@app.route('/record_count/<table_name>', methods=['GET'])
def get_record_count(table_name):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
    count = cursor.fetchone()[0]
    conn.close()
    return jsonify(count)

@app.route('/validate_ids', methods=['POST'])
def validate_ids():
    data = request.json
    id_region = data.get('id_region')
    id_branch = data.get('id_branch')
    id_show = data.get('id_show')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM Region WHERE id = ?', (id_region,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({"valid": False, "message": "Некорректный id_region."}), 400

    cursor.execute('SELECT id FROM Branch WHERE id = ?', (id_branch,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({"valid": False, "message": "Некорректный id_branch."}), 400

    cursor.execute('SELECT id FROM Show WHERE id = ?', (id_show,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({"valid": False, "message": "Некорректный id_show."}), 400

    conn.close()
    return jsonify({"valid": True, "message": "Все идентификаторы корректны."}), 200

@app.route('/add_record', methods=['POST'])
def add_record():
    data = request.json
    table_name = data['table_name']
    values = data['values']
    if table_name == 'Statistical_data':
        valid, message = validate_ids(values['id_region'], values['id_branch'], values['id_show'])
        if not valid:
            return jsonify({'error': message}), 400
    conn = get_db()
    cursor = conn.cursor()
    columns = ', '.join(values.keys())
    placeholders = ', '.join('?' for _ in values)
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    cursor.execute(query, tuple(values.values()))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Запись добавлена успешно'}), 201

@app.route('/update_record', methods=['POST'])
def update_record():
    data = request.json
    table_name = data['table_name']
    id = data['id']
    values_to_update = data['values_to_update']
    if table_name == 'Statistical_data':
        valid, message = validate_ids(values_to_update['id_region'], values_to_update['id_branch'], values_to_update['id_show'])
        if not valid:
            return jsonify({'error': message}), 400
    conn = get_db()
    cursor = conn.cursor()
    columns = ', '.join([f"{key} = ?" for key in values_to_update])
    query = f"UPDATE {table_name} SET {columns} WHERE id = ?"
    cursor.execute(query, tuple(values_to_update.values()) + (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Запись обновлена успешно'}), 200

@app.route('/delete_record', methods=['POST'])
def delete_record_from_db():
    data = request.json
    table_name = data['table_name']
    record_id = data['record_id']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f'DELETE FROM {table_name} WHERE id = ?', (record_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Запись обновлена успешно'}), 200


def get_table_fields(table_name):
    conn = sqlite3.connect('economicDB.db')
    cursor = conn.cursor()
    cursor.execute(f'PRAGMA table_info({table_name})')
    fields = [column[1] for column in cursor.fetchall()]
    conn.close()
    return fields


@app.route('/search_record', methods=['GET'])
def search_record():
    table_name = request.args.get('table_name')
    search_id = request.args.get('search_id')

    if not table_name or not search_id:
        return jsonify({'error': 'Table name and search ID are required'}), 400

    if not search_id.isdigit():
        return jsonify({'error': 'Search ID must be an integer'}), 400

    try:
        conn = sqlite3.connect('economicDB.db')
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM {table_name} WHERE id = ?', (int(search_id),))
        record = cursor.fetchone()
        conn.close()

        if record is None:
            return jsonify({'error': 'Record not found'}), 404

        fields = get_table_fields(table_name)
        record_data = {field: value for field, value in zip(fields, record)}
        return jsonify({'record': record_data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_table_fields', methods=['GET'])
def get_fields():
    table_name = request.args.get('table_name')
    if not table_name:
        return jsonify({'error': 'Table name is required'}), 400

    try:
        fields = get_table_fields(table_name)
        return jsonify({'fields': fields}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_record_count_by_value', methods=['POST'])
def get_record_count_by_value():
    data = request.json
    table_name = data['table_name']
    column_name = data['column_name']
    value = data['value']

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f'SELECT COUNT(*) FROM {table_name} WHERE {column_name} = ?', (value,))
    count = cursor.fetchone()[0]
    conn.close()

    return jsonify({'count': count})

@app.route('/get_records_by_id', methods=['GET'])
def get_records_by_id():
    record_ids = request.args.getlist('record_ids')
    table_name = request.args.get('table_name')

    conn = get_db()
    cursor = conn.cursor()

    if not record_ids:
        return jsonify([])

    cursor.execute(f'SELECT * FROM {table_name} WHERE id IN ({",".join("?" for _ in record_ids)})', record_ids)
    records = cursor.fetchall()
    conn.close()

    return jsonify(records)

if __name__ == '__main__':
    app.run(debug=True)