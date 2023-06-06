import pandas as pd
import datetime
import sqlite3
from flask import Flask, render_template

app = Flask(__name__)
DATABASE = 'time_slots.db'

def create_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS time_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            client TEXT
        )
    ''')
    conn.commit()
    conn.close()

def populate_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM time_slots')
    count = cursor.fetchone()[0]

    if count == 0:
        start_date = datetime.date(2023, 1, 1)
        end_date = datetime.date(2023, 12, 31)
        delta = datetime.timedelta(days=1)

        current_date = start_date
        while current_date <= end_date:
            if pd.to_datetime(current_date).dayofweek < 5:  # Check if it's a weekday (0 = Monday, 4 = Friday)
                time_slots = ['9:00 AM', '1:00 PM']
                for time_slot in time_slots:
                    cursor.execute('INSERT INTO time_slots (date, time, client) VALUES (?, ?, ?)', (current_date.strftime('%m/%d/%Y'), time_slot, ''))
            current_date += delta

        conn.commit()

    conn.close()

@app.route('/')
def index():
    create_database()
    populate_table()

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM time_slots')
    rows = cursor.fetchall()

    conn.close()

    # Group the rows by month
    months = {}
    for row in rows:
        month = datetime.datetime.strptime(row[1], '%m/%d/%Y').strftime('%B')
        week_number = datetime.datetime.strptime(row[1], '%m/%d/%Y').isocalendar()[1]
        if month not in months:
            months[month] = {}
        if week_number not in months[month]:
            months[month][week_number] = []
        months[month][week_number].append(row)

    # Render the table template and pass the grouped data
    return render_template('table.html', months=months)


if __name__ == '__main__':
    app.run()
