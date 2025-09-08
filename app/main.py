from fastapi import FastAPI
from fastapi.responses import FileResponse
import os
import yaml

from preprocess_data import preprocess_data
from fetch_param import fetch_param
from train_model import train_autoencoder
from generate_report import generate_report

app = FastAPI()

REPORT_DIR = "data\processed"
MODEL_DIR  = "model"
os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"Traffic Report Generator": "REST API"}

@app.get("/get_report")
def get_report():
    # preprocess data
    processed_data, segment_names, segment_mean_raw = preprocess_data()

    # import parameters from the current best model
    fetch_param()
    config_path = os.path.join(MODEL_DIR, "config.yaml")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    epochs = config["epochs"]
    batch_size = config["batch_size"]
    latent_dim = config["latent_dim"]
    validation_split=config["validation_split"]
    
    # train the model on the traffic data
    encoder = train_autoencoder(
        latent_dim, 
        processed_data, 
        input_shape=processed_data.shape[1:],
        validation_split=validation_split, 
        epochs=epochs, 
        batch_size=batch_size
    )

    # generate clustering report
    generate_report(processed_data, encoder, segment_names, segment_mean_raw)

    csv_path = os.path.join(REPORT_DIR, "road_segment_flow_level_clusters.csv")
    return FileResponse(
        path=csv_path,
        media_type="text/csv",
        filename="road_segment_flow_level_clusters.csv"
    )
    
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)