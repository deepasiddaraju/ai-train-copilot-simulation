from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class TrainLog(db.Model):
    __tablename__ = "train_logs"
    id = db.Column(db.Integer, primary_key=True)

    # Basic info
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    day = db.Column(db.Integer)
    day_of_week = db.Column(db.Integer)

    # Train identifiers
    train_operator = db.Column(db.String(100))   # longer length for mapped names
    train_number = db.Column(db.String(20))      # store as string (IDs can mix letters/numbers)
    coach_id = db.Column(db.String(20))

    # Stations
    source_station = db.Column(db.String(100))   # longer length for mapped names
    destination_station = db.Column(db.String(100))

    # Timing
    scheduled_departure = db.Column(db.Integer)  # int64 in dataset
    actual_departure = db.Column(db.Float)
    delay_departure = db.Column(db.Float)

    scheduled_arrival = db.Column(db.Integer)
    actual_arrival = db.Column(db.Float)
    delay_arrival = db.Column(db.Float)

    # Status
    diverted = db.Column(db.Boolean)
    cancelled = db.Column(db.Boolean)
    cancellation_reason = db.Column(db.String(100))

    # Delay breakdowns
    system_delay = db.Column(db.Float)
    security_delay = db.Column(db.Float)
    operator_delay = db.Column(db.Float)
    late_train_delay = db.Column(db.Float)
    weather_delay = db.Column(db.Float)

    # Extra fields for full dataset coverage
    platform_time_out = db.Column(db.Float)
    train_departure_event = db.Column(db.Float)
    scheduled_time = db.Column(db.Float)
    elapsed_time = db.Column(db.Float)
    run_time = db.Column(db.Float)
    distance_km = db.Column(db.Integer)
    left_source_station_time = db.Column(db.Float)
    platform_time_in = db.Column(db.Float)
