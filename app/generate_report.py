import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

RESULTS_PATH = "data/processed/road_segment_flow_level_clusters.csv"

# function for training autoencoder model
def generate_report(processed_data, encoder_model, road_segments, road_segment_raw_mean):
    x_seq = processed_data
    encoder = encoder_model

    # getting the latent space
    z = encoder.predict(x_seq, verbose=0)

    # clustering using the latent space
    kmeans = KMeans(n_clusters=3, n_init=20, random_state=42)
    cluster_labels = kmeans.fit_predict(z)

    cluster_to_avg = {}
    for c in range(3):
        idx = np.where(cluster_labels == c)[0]
        cluster_to_avg[c] = float(road_segment_raw_mean.iloc[idx].mean()) if len(idx) > 0 else -np.inf

    ranked = sorted(cluster_to_avg.items(), key=lambda x: x[1], reverse=True)
    rank_to_name = {0: "Low Flow Level", 1: "Medium Flow Level", 2: "High Flow Level"}
    cluster_to_category = {}

    for rank, (cluster_id, _) in enumerate(ranked):
        cluster_to_category[cluster_id] = rank_to_name[rank]

    categories = [cluster_to_category[c] for c in cluster_labels]

    # saving the results to a csv file
    result_df = pd.DataFrame({
        "segment": road_segments,
        "cluster_id": cluster_labels,
        "category": categories,
        "avg_raw_traffic": road_segment_raw_mean.values,
    })

    result_df.to_csv(RESULTS_PATH, index=False)
    print("Saved results to:", RESULTS_PATH)

if __name__ == '__main__':
    generate_report()