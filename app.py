## This is main file for the code. 
from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import pickle
import pandas as pd
import numpy as np

app = FastAPI()

# Load the trained model from pickle file
with open('linear_regression_model.pkl', 'rb') as file:
    pipe = pickle.load(file)

# Load location options from CSV file
locations = pd.read_csv("cleaned_data.csv")['location'].unique().tolist()

# Set up templates
templates = Jinja2Templates(directory="templates")

# Adding CORS middleware to allow front-end access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "locations": locations})

@app.post("/predict")
async def predict(bath: float = Form(...), total_sqft: float = Form(...), bhk: float = Form(...), location: str = Form(...)):
    if np.isnan(bath) or np.isnan(total_sqft) or np.isnan(bhk):
        raise HTTPException(status_code=400, detail="Please enter valid numeric values for all features.")

    # Combine Input Data
    input_data = pd.DataFrame({
        'bath': [bath],
        'total_sqft': [total_sqft],
        'bhk': [bhk],
        'location': [location]
    })

    # Ensure the input data columns are in the same order as during training
    input_data = input_data[['bath', 'total_sqft', 'bhk', 'location']]

    # Make Prediction
    try:
        prediction = pipe.predict(input_data)[0]
        #print(prediction)
        if prediction > 0:
            return {"prediction": f'The estimated price of the house is {prediction/100:,.2f} crores'}
        else:
            return {"Prediction": 'Negative value have been generated please enter the correct inputs'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)
