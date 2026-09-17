import numpy as np
from flask import Flask, render_template, request
import joblib
import pandas as pd

app = Flask(__name__)
model = joblib.load('simifinal.pkl')

@app.route('/')
@app.route('/main')
def main():
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
    return render_template('main.html', prediction_text="Your Bike Estimated Cost is INR: {}".format(output))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=False)



	
