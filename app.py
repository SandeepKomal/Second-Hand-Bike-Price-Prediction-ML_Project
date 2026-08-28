import numpy as np
from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import joblib
import pandas as pd
import uuid
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-to-a-random-secret-key")

# --- DB CONFIG (PostgreSQL) ---------------------------------------------
# Format: postgresql://<username>:<password>@<host>:<port>/<database_name>
# Store this in an environment variable in production -- never hardcode
# real credentials in source control.
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "postgresql://myuser:mypassword@localhost:5432/bike_searches"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

model = joblib.load('simifinal.pkl')


# --- MODEL: one row per search ------------------------------------------
class SearchLog(db.Model):
    __tablename__ = "search_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), nullable=False)  # anonymous visitor ID

    km_driven = db.Column(db.Integer)
    make_year = db.Column(db.Integer)
    bike_name = db.Column(db.String(50))
    bike_model = db.Column(db.String(50))
    state = db.Column(db.String(50))
    city = db.Column(db.String(50))

    predicted_price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


def get_or_create_user_id():
    """Give every visitor a stable anonymous ID, stored in their browser cookie."""
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())
    return session["user_id"]


@app.route('/')
@app.route('/main')
def main():
    get_or_create_user_id()
    return render_template('main.html')


@app.route('/predict', methods=['POST'])
def predict():
    int_features = [x for x in request.form.values()]
    check = [int_features]
    check = pd.DataFrame(check, columns=["km_driven", "make_year", "bike_name", "bike_model", "state", "city"])
    ohot = joblib.load('ohe.joblib')
    dino = pd.DataFrame(ohot.transform(check.iloc[:, 2:6]))
    dino.columns = ohot.get_feature_names_out()
    check = pd.concat([check.iloc[:, 0:2], dino], axis=1)
    output = model.predict(check)

    predicted_value = float(output[0])

    log_entry = SearchLog(
        user_id=get_or_create_user_id(),
        km_driven=int(int_features[0]) if int_features[0] else None,
        make_year=int(int_features[1]) if int_features[1] else None,
        bike_name=int_features[2],
        bike_model=int_features[3],
        state=int_features[4],
        city=int_features[5],
        predicted_price=predicted_value,
    )
    db.session.add(log_entry)
    db.session.commit()

    return render_template('main.html', prediction_text="Your Bike Estimated Cost is INR: {}".format(output))


@app.route('/my-searches')
def my_searches():
    user_id = get_or_create_user_id()
    searches = (
        SearchLog.query
        .filter_by(user_id=user_id)
        .order_by(SearchLog.created_at.desc())
        .all()
    )
    return {
        "searches": [
            {
                "id": s.id,
                "km_driven": s.km_driven,
                "make_year": s.make_year,
                "bike_name": s.bike_name,
                "bike_model": s.bike_model,
                "state": s.state,
                "city": s.city,
                "predicted_price": s.predicted_price,
                "created_at": s.created_at.isoformat(),
            }
            for s in searches
        ]
    }


if __name__ == "__main__":
    with app.app_context():
        db.create_all()   # creates the search_logs table in Postgres if not already there
    app.run(host='0.0.0.0', port=8000, debug=False)
