from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import sqlite3
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import requests
from datetime import datetime
import re

app = Flask(__name__)
CORS(app)

DB_FILE = "railways.db"
MODEL_FILE = "delay_model.pkl"



def query_db(sql, params=None):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(sql, conn, params=params, index_col=None)
    conn.close()
    return df


def get_weather(lat, lon, scenario_weather=None):
    """
    Return weather condition based on scenario override.
    No external API call is made.
    """
    if scenario_weather:
        return scenario_weather
    return "unknown"

def run_what_if(train_no, scenario):
    conn = sqlite3.connect("railways.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tp.station_code, tp.avg_delay_minutes,
               COALESCE(bs.traffic, 0) as traffic,
               st.lat, st.lon
        FROM train_performance tp
        LEFT JOIN (
            SELECT sc.station_code, COUNT(*) as traffic
            FROM schedules sc
            GROUP BY sc.station_code
        ) bs ON tp.station_code = bs.station_code
        JOIN stations st ON tp.station_code = st.station_code
        WHERE tp.train_no = ?
    """, (train_no,))
    rows = cursor.fetchall()
    conn.close()

    results = []
    for station_code, delay, traffic, lat, lon in rows:
        new_delay = delay if delay is not None else 0

        # ✅ Skip overrides everything
        if scenario.get("skip_station") == station_code:
            new_delay = 0
            likely_cause = "Skipped station"
            condition = "none"

        else:
            # ✅ Weather/maintenance only apply if not skipped
            if scenario.get("maintenance"):
                new_delay += 15
            condition = scenario.get("weather", "unknown")

            if "rain" in condition or "shower" in condition:
                new_delay += 10
                likely_cause = "Weather impact (rain)"
            elif "fog" in condition:
                new_delay += 5
                likely_cause = "Weather impact (fog)"
            elif scenario.get("maintenance"):
                likely_cause = "Maintenance impact"
            elif traffic > 50000 and new_delay > 20:
                likely_cause = "Passenger congestion"
            elif traffic <= 10000 and new_delay > 20:
                likely_cause = "Infrastructure issue"
            elif new_delay > 0:
                likely_cause = "Operational bottleneck"
            else:
                likely_cause = "On time"

            # ✅ Mark rerouted stations
            if scenario.get("reroute") and station_code in scenario["reroute"]:
                likely_cause = "Rerouted path"

        results.append({
            "station_code": station_code,
            "predicted_delay": new_delay,
            "likely_cause": likely_cause,
            "weather_condition": condition,
            "traffic_volume": traffic
        })

    return results



# --- Analytics Endpoints ---
@app.route("/analytics/busiest", methods=["GET"])
def busiest_stations():
    sql = """
    SELECT sc.station_code,
           st.station_name,
           COALESCE(st.zone, 'Unknown') AS zone,
           COUNT(*) AS traffic
    FROM schedules sc
    JOIN stations st ON sc.station_code = st.station_code
    GROUP BY sc.station_code, st.station_name, st.zone
    ORDER BY traffic DESC
    LIMIT 20
    """
    df = query_db(sql)
    if df.empty:
        return jsonify({"message": "No data available"})
    return jsonify(df.to_dict(orient="records"))

@app.route("/analytics/zone", methods=["GET"])
def zone_density():
    sql = """
    SELECT COALESCE(zone, 'Unknown') AS zone,
           COUNT(*) AS station_count
    FROM stations
    GROUP BY zone
    ORDER BY station_count DESC
    """
    df = query_db(sql)
    if df.empty:
        return jsonify({"message": "No data available"})
    return jsonify(df.to_dict(orient="records"))

@app.route("/stations/search", methods=["GET"])
def search_stations():
    name = request.args.get("name", "")
    sql = """
    SELECT station_code,
           station_name,
           COALESCE(zone, 'Unknown') AS zone,
           lat,
           lon
    FROM stations
    WHERE station_name LIKE ? OR station_code LIKE ?
    LIMIT 20
    """
    df = query_db(sql, [f"%{name}%", f"%{name}%"])
    if df.empty:
        return jsonify({"message": "No data available"})
    return jsonify(df.to_dict(orient="records"))

# --- Train schedule ---
@app.route("/train/<train_no>", methods=["GET"])
def train_schedule(train_no):
    sql = """
    SELECT sc.train_no,
           sc.train_name,
           sc.station_code,
           st.station_name,
           COALESCE(st.zone, 'Unknown') AS zone,
           sc.arrival,
           sc.departure,
           sc.day
    FROM schedules sc
    JOIN stations st ON sc.station_code = st.station_code
    WHERE sc.train_no = ?
    ORDER BY sc.day ASC
    """
    df = query_db(sql, [train_no])
    if df.empty:
        return jsonify({"message": "No data available"})
    return jsonify(df.to_dict(orient="records"))

# --- Train ML Model ---
# --- Train ML Model ---


def train_model():
    sql = """
    SELECT train_no, station_code, avg_delay_minutes,
           pct_on_time, pct_slight_delay, pct_significant_delay, pct_cancelled
    FROM train_performance
    """
    df = query_db(sql)
    df = df.dropna()
    if df.empty:
        return None

    df["train_no"] = df["train_no"].astype(int)
    df["station_code"] = df["station_code"].astype("category").cat.codes

    X = df[["train_no", "station_code", "pct_on_time",
            "pct_slight_delay", "pct_significant_delay", "pct_cancelled"]]
    y = df["avg_delay_minutes"]

    # Split into train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train Random Forest
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    print("📊 Model Evaluation:")
    print("R² Score:", r2_score(y_test, y_pred))
    print("MAE:", mean_absolute_error(y_test, y_pred))

    # Save model for API use
    joblib.dump(model, MODEL_FILE)
    return model

try:
    model = joblib.load(MODEL_FILE)
except:
    model = train_model()


# --- Prediction Endpoint ---
@app.route("/predict/<train_no>", methods=["GET"])
def predict_delay(train_no):
    sql = """
    SELECT sc.train_no, sc.train_name, sc.station_code, st.station_name,
           sc.arrival, sc.departure, st.lat, st.lon
    FROM schedules sc
    JOIN stations st ON sc.station_code = st.station_code
    WHERE sc.train_no = ?
    ORDER BY sc.day ASC
    """
    df = query_db(sql, [train_no])
    if df.empty:
        return jsonify({"message": "No schedule available"})

    results = []
    for _, row in df.iterrows():
        # Try Kaggle stats first
        perf_sql = """
        SELECT pct_on_time, pct_slight_delay, pct_significant_delay, pct_cancelled
        FROM train_performance
        WHERE train_no = ? AND station_code = ?
        """
        perf = query_db(perf_sql, [row["train_no"], row["station_code"]])

        delay = None
        if not perf.empty and model is not None:
            # Use ML model with Kaggle features
            features = pd.DataFrame([{
                "train_no": int(row["train_no"]),
                "station_code": pd.Series([row["station_code"]]).astype("category").cat.codes[0],
                "pct_on_time": perf.iloc[0]["pct_on_time"],
                "pct_slight_delay": perf.iloc[0]["pct_slight_delay"],
                "pct_significant_delay": perf.iloc[0]["pct_significant_delay"],
                "pct_cancelled": perf.iloc[0]["pct_cancelled"]
            }])
            pred = model.predict(features)[0]
            delay = round(float(pred), 2)
        else:
            # Fallback: estimate based on dwell time
            arr, dep = row["arrival"], row["departure"]
            if arr and dep:
                try:
                    arr_sec = int(pd.to_timedelta(arr).total_seconds())
                    dep_sec = int(pd.to_timedelta(dep).total_seconds())
                    dwell = dep_sec - arr_sec
                    if dwell <= 0:
                        delay = 0
                    elif dwell <= 120:
                        delay = 2
                    elif dwell <= 600:
                        delay = 5
                    else:
                        delay = 15
                except Exception:
                    delay = None

        results.append({
            "train_no": row["train_no"],
            "train_name": row["train_name"],
            "station_code": row["station_code"],
            "station_name": row["station_name"],
            "lat": row["lat"],
            "lon": row["lon"],
            "predicted_delay_minutes": delay
        })

    return jsonify(results)

@app.route("/analytics/delay_trends", methods=["GET"])
def delay_trends():
    train_no = request.args.get("train_no")
    if not train_no:
        return jsonify({"error": "train_no required"}), 400

    # Load Kaggle dataset
    df = pd.read_csv("data/kaggle_train_performance.csv")

    # Filter by train number
    train_df = df[df["train_number"] == int(train_no)]

    if train_df.empty:
        return jsonify([])

    # Group by date
    train_df["date"] = pd.to_datetime(train_df["scraped_at"]).dt.date
    trend = train_df.groupby("date")["average_delay_minutes"].mean().reset_index()

    # ✅ Ensure at least last 7 days are returned
    today = pd.to_datetime("today").date()
    last_7_days = pd.date_range(end=today, periods=7).date

    filled_trend = []
    for d in last_7_days:
        match = trend[trend["date"] == d]
        if not match.empty:
            avg_delay = match.iloc[0]["average_delay_minutes"]
        else:
            avg_delay = 0  # fill missing days
        filled_trend.append({"date": str(d), "avg_delay": avg_delay})

    return jsonify(filled_trend)


# --- Train Comparison Endpoint ---
@app.route("/analytics/train_compare", methods=["GET"])
def train_compare():
    train_nos = request.args.get("trains")
    if not train_nos:
        return jsonify({"error": "trains required"}), 400

    train_list = train_nos.split(",")

    conn = sqlite3.connect("railways.db")
    cursor = conn.cursor()

    results = []
    summary = {"on_time": 0, "slight": 0, "significant": 0, "cancelled": 0}
    alerts = []
    zone_delays = {}

    for t in train_list:
        cursor.execute("""
            SELECT train_no, station_code, avg_delay_minutes,
                   pct_on_time, pct_slight_delay, pct_significant_delay, pct_cancelled
            FROM train_performance WHERE train_no = ?
        """, (t,))
        row = cursor.fetchone()
        if row:
            delay = row[2] or 0
            category = "on_time"
            if delay > 0 and delay <= 5:
                category = "slight"
            elif delay > 5 and delay <= 30:
                category = "significant"
            elif delay > 30:
                category = "cancelled"

            summary[category] += 1

            # Delay alert
            if delay > 30:
                alerts.append(f"Train {row[0]} expected delay {int(delay)} min at {row[1]}")

            # Cancellation risk alert
            if row[6] and row[6] > 20:
                alerts.append(f"Train {row[0]} has high cancellation risk ({row[6]}%)")

            # Zone congestion tracking
            zone = row[1][:2]  # simple zone grouping by station code prefix
            if delay > 15:
                zone_delays.setdefault(zone, 0)
                zone_delays[zone] += 1

            results.append({
                "train_no": row[0],
                "station_code": row[1],
                "avg_delay_minutes": delay,
                "on_time": row[3],
                "slight_delay": row[4],
                "significant_delay": row[5],
                "cancelled": row[6],
                "category": category
            })
        else:
            cursor.execute("SELECT train_no, train_name FROM trains WHERE train_no = ?", (t,))
            row2 = cursor.fetchone()
            if row2:
                results.append({
                    "train_no": row2[0],
                    "train_name": row2[1],
                    "message": "No delay performance data available"
                })
            else:
                results.append({"train_no": t, "message": "Train not found"})

    conn.close()

    # Zone congestion alerts
    for zone, count in zone_delays.items():
        if count > 2:  # threshold: 3+ trains delayed in same zone
            alerts.append(f"Zone {zone}: {count} trains delayed, congestion risk high")

    return jsonify({"results": results, "summary": summary, "alerts": alerts})







@app.route("/analytics/what_if", methods=["POST"])
def what_if():
    data = request.json
    train_no = data.get("train_no")
    scenario = data.get("scenario", {})

    conn = sqlite3.connect("railways.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tp.station_code, tp.avg_delay_minutes,
               COALESCE(bs.traffic, 0) as traffic,
               st.lat, st.lon
        FROM train_performance tp
        LEFT JOIN (
            SELECT sc.station_code, COUNT(*) as traffic
            FROM schedules sc
            GROUP BY sc.station_code
        ) bs ON tp.station_code = bs.station_code
        JOIN stations st ON tp.station_code = st.station_code
        WHERE tp.train_no = ?
    """, (train_no,))
    rows = cursor.fetchall()
    conn.close()

    # ✅ Apply reroute filter
    reroute_list = scenario.get("reroute")
    if reroute_list:
        rows = [row for row in rows if row[0] in reroute_list]

    if not rows:
        return jsonify({"train_no": train_no, "scenario": scenario, "results": []})

    results = []
    for station_code, delay, traffic, lat, lon in rows:
        new_delay = delay if delay is not None else 0

        if scenario.get("skip_station") == station_code:
            new_delay = 0
            likely_cause = "Skipped station"
        else:
            if scenario.get("maintenance"):
                new_delay += 15

            condition = get_weather(lat, lon, scenario.get("weather"))

            if "rain" in condition or "shower" in condition:
                new_delay += 10
                likely_cause = "Weather impact (rain)"
            elif "fog" in condition:
                new_delay += 5
                likely_cause = "Weather impact (fog)"
            elif scenario.get("maintenance"):
                likely_cause = "Maintenance impact"
            elif traffic > 50000 and new_delay > 20:
                likely_cause = "Passenger congestion"
            elif traffic <= 10000 and new_delay > 20:
                likely_cause = "Infrastructure issue"
            elif new_delay > 0:
                likely_cause = "Operational bottleneck"
            else:
                likely_cause = "On time"

        results.append({
            "station_code": station_code,
            "predicted_delay": new_delay,
            "likely_cause": likely_cause,
            "weather_condition": condition,
            "traffic_volume": traffic
        })

    return jsonify({"train_no": train_no, "scenario": scenario, "results": results})


# ✅ Log controller actions
@app.route("/analytics/log_action", methods=["POST"])
def log_action():
    data = request.json
    train_no = data.get("train_no")
    action = data.get("action")   # "skip", "reroute", "hold"
    station = data.get("station")
    weather = data.get("weather")

    conn = sqlite3.connect("controller_actions.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS actions (
        train_no TEXT, action TEXT, station TEXT, weather TEXT, timestamp TEXT
    )""")
    c.execute("INSERT INTO actions VALUES (?, ?, ?, ?, ?)",
              (train_no, action, station, weather, datetime.now().isoformat()))
    conn.commit()
    conn.close()

    return jsonify({"status": "logged"})


# ✅ Generate learned recommendations
@app.route("/analytics/recommendations", methods=["GET"])
def recommendations():
    weather = request.args.get("weather", "")
    conn = sqlite3.connect("controller_actions.db")
    c = conn.cursor()

    # Example: if reroute via AJJ during fog is frequent
    c.execute("""SELECT COUNT(*) FROM actions 
                 WHERE action='reroute' AND station='AJJ' AND weather=?""", (weather,))
    count = c.fetchone()[0]
    conn.close()

    alerts = []
    if count >= 3:  # threshold
        alerts.append(f"🤝 Learned Preference: Reroute via AJJ during {weather} is recommended based on past controller actions.")

    return jsonify(alerts)



@app.route("/analytics/alerts", methods=["GET"])
def zone_alerts():
    # Load dataset
    df = pd.read_csv("data/kaggle_train_performance.csv")

    # Example: derive zone from first 2 letters of station_code
    df["zone"] = df["station_code"].str[:2]

    # Count trains with delay > 20 minutes per zone
    congestion = df.groupby("zone")["average_delay_minutes"].apply(lambda x: (x > 20).sum()).reset_index()

    alerts = []
    for _, row in congestion.iterrows():
        if row["average_delay_minutes"] >= 3:  # threshold: 3 trains delayed
            alerts.append(f"🚦 Zone {row['zone']}: {row['average_delay_minutes']} trains delayed, congestion risk high.")

    return jsonify(alerts)



@app.route("/analytics/alerts", methods=["GET"])
def alerts():
    conn = sqlite3.connect("railways.db")
    cursor = conn.cursor()

    alerts = []
    zone_delays = {}

    cursor.execute("""
        SELECT train_no, station_code, avg_delay_minutes, pct_cancelled
        FROM train_performance
    """)
    rows = cursor.fetchall()
    conn.close()

    for train_no, station_code, delay, cancelled_pct in rows:
        # Severe delay alert
        if delay and delay > 30:
            alerts.append(f"🚨 Train {train_no} severe delay: {int(delay)} min at {station_code}")

        # Cancellation risk alert
        if cancelled_pct and cancelled_pct > 20:
            alerts.append(f"⚠️ Train {train_no} high cancellation risk ({cancelled_pct}%)")

        # Zone congestion tracking
        if delay and delay > 15:
            zone = station_code[:2]  # simple zone grouping
            zone_delays.setdefault(zone, 0)
            zone_delays[zone] += 1

    # Zone congestion alerts
    for zone, count in zone_delays.items():
        if count >= 3:
            alerts.append(f"🚦 Zone {zone}: {count} trains delayed, congestion risk high")

    return jsonify({"alerts": alerts})


@app.route("/analytics/check_train/<train_no>", methods=["GET"])
def check_train(train_no):
    conn = sqlite3.connect("railways.db")
    cursor = conn.cursor()
    cursor.execute("SELECT station_code, avg_delay_minutes FROM train_performance WHERE train_no = ?", (train_no,))
    rows = cursor.fetchall()
    conn.close()
    return jsonify({"train_no": train_no, "rows": rows})




#voice assistance

@app.route("/voice_query", methods=["POST"])
def voice_query():
    data = request.json
    query = data.get("query", "").lower()

    # Extract train number
    train_no_match = re.search(r"\b\d{4,5}\b", query)
    train_no = train_no_match.group(0) if train_no_match else None

    # Load valid station codes from DB
    conn = sqlite3.connect("railways.db")
    cursor = conn.cursor()
    cursor.execute("SELECT station_code FROM stations")
    valid_codes = [row[0].upper() for row in cursor.fetchall()]
    conn.close()

    station_code = None
    for code in valid_codes:
        if code in query.upper().split():
            station_code = code
            break

    # Detect weather
    weather = None
    if "fog" in query:
        weather = "fog"
    elif "rain" in query or "shower" in query:
        weather = "rain"
    elif "storm" in query:
        weather = "storm"

    # Delay prediction
    if "delay" in query and train_no:
        result = predict_delay(train_no)   # existing function
        return jsonify({
            "message": f"Predicted delays for Train {train_no}",
            "details": result.get_json(),
            "type": "delay"
        })

    # Reroute scenario
    if "reroute" in query and train_no:
        scenario = {"reroute": [station_code]} if station_code else {}
        if weather:
            scenario["weather"] = weather
        results = run_what_if(train_no, scenario)
        return jsonify({
            "message": f"Reroute suggestion for Train {train_no}",
            "details": results,
            "type": "reroute"
        })

    # Skip station scenario
    if "skip" in query and train_no and station_code:
        scenario = {"skip_station": station_code}
        if weather:
            scenario["weather"] = weather
        results = run_what_if(train_no, scenario)
        return jsonify({
            "message": f"Skip {station_code} scenario for Train {train_no}",
            "details": results,
            "type": "skip"
        })

    # Alerts scenario
    if "alert" in query and train_no:
        # Call the DB-based alerts function
        conn = sqlite3.connect("railways.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT train_no, station_code, avg_delay_minutes, pct_cancelled
            FROM train_performance WHERE train_no = ?
        """, (train_no,))
        rows = cursor.fetchall()
        conn.close()

        alerts = []
        zone_delays = {}
        for train_no, station_code, delay, cancelled_pct in rows:
            if delay and delay > 30:
                alerts.append(f"🚨 Train {train_no} severe delay: {int(delay)} min at {station_code}")
            if cancelled_pct and cancelled_pct > 20:
                alerts.append(f"⚠️ Train {train_no} high cancellation risk ({cancelled_pct}%)")
            if delay and delay > 15:
                zone = station_code[:2]
                zone_delays.setdefault(zone, 0)
                zone_delays[zone] += 1

        for zone, count in zone_delays.items():
            if count >= 3:
                alerts.append(f"🚦 Zone {zone}: {count} trains delayed, congestion risk high")

        return jsonify({
            "message": f"Alerts for Train {train_no}",
            "details": alerts,
            "type": "alerts"
        })

    return jsonify({"message": "Sorry, I couldn’t understand the query."})



if __name__ == "__main__":
    app.run(debug=True)
