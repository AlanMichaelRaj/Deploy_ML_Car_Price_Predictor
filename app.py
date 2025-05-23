import pickle
from flask import Flask, request, render_template
import pandas as pd
import numpy as np
from catboost import CatBoostRegressor

app = Flask(__name__)

# Load models and encoders
try:
    model = pickle.load(open('./models/Model.pkl', 'rb'))
    Brand_Encoder = pickle.load(open('./models/Brand_Encoder.pkl', 'rb'))
    Model_Encoder = pickle.load(open('./models/Model_Encoder.pkl', 'rb'))
    OneHot_Encoder = pickle.load(open('./models/OneHot_Encoder.pkl', 'rb'))
except Exception as e:
    print(f"❌ Error loading model or encoders: {e}")

@app.route('/', methods=['GET'])
def Home():
    return render_template('index.html')

@app.route("/predict", methods=['POST'])
def predict():
    try:
        # Extract form data
        Brand = request.form['Brand']
        Model_Name = request.form['Model']
        Fuel = request.form['Fuel']
        Transmission = request.form['Transmission']
        Year = int(request.form['Year'])
        EngineSize = float(request.form['EngineSize'])
        Mileage = int(request.form['Mileage'])
        Doors = int(request.form['Doors'])
        OwnerCount = int(request.form['OwnerCount'])

        # Prepare input DataFrame
        input_df = pd.DataFrame({
            'Brand': [Brand],
            'Model': [Model_Name],
            'Year': [Year],
            'EngineSize': [EngineSize],
            'Fuel': [Fuel],
            'Transmission': [Transmission],
            'Mileage': [Mileage],
            'Doors': [Doors],
            'OwnerCount': [OwnerCount]
        })

        # Encode Brand and Model
        input_df['Encoded_Brand'] = input_df['Brand'].map(Brand_Encoder)
        input_df['Encoded_Model'] = input_df['Model'].map(Model_Encoder)
        input_df['Encoded_Brand'].fillna(input_df['Encoded_Brand'].mean(), inplace=True)
        input_df['Encoded_Model'].fillna(input_df['Encoded_Model'].mean(), inplace=True)
        input_df.drop(['Brand', 'Model'], axis=1, inplace=True)

        # One-hot encode categorical columns
        categorical_cols = ['Fuel', 'Transmission']
        encoded_array = OneHot_Encoder.transform(input_df[categorical_cols])
        encoded_df = pd.DataFrame(encoded_array, columns=OneHot_Encoder.get_feature_names_out(categorical_cols))

        # Merge encoded columns with input data
        input_df_encoded = input_df.drop(columns=categorical_cols).reset_index(drop=True)
        input_data = pd.concat([input_df_encoded, encoded_df], axis=1)

        # Predict
        prediction = model.predict(input_data)
        output = round(prediction[0], 2)

        if output < 0:
            return render_template('index.html', prediction_texts="Sorry, you cannot sell this car.")
        else:
            return render_template('index.html', prediction_text="Car is worth at: $ {}".format(output))

    except Exception as e:
        print(f"❌ Error in prediction route: {e}")
        return render_template('index.html', prediction_text=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app.run(debug=True)
