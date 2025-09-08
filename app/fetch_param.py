import mlflow
import yaml
import os

MODEL_DIR = "model"

# function for fetching the parameters from the current best model
def fetch_param():
    mlflow.set_tracking_uri("../mlruns")

    experiment_name = "Autoencoder_Optimization"
    client = mlflow.tracking.MlflowClient()
    experiment = client.get_experiment_by_name(experiment_name)

    # finding the current best model
    best_run = client.search_runs(
        [experiment.experiment_id],
        order_by=["metrics.best_val_loss ASC"],
        max_results=1
    )[0]

    best_params = best_run.data.params
    print("Best run parameters:", best_params)

    for k, v in best_params.items():
        try:
            best_params[k] = int(v)
        except ValueError:
            try:
                best_params[k] = float(v)
            except ValueError:
                pass

    # adding validation split as an extra parameter
    if "validation_split" not in best_params:
        best_params["validation_split"] = 0.25

    # saving the parameters from the current best model
    config_path = os.path.join(MODEL_DIR, "config.yaml")
    with open(config_path, "w") as f:
        yaml.safe_dump(best_params, f)

    print("config.yaml generated successfully!")

if __name__ == '__main__':
    fetch_param()