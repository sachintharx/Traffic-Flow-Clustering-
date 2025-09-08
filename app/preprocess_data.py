import pandas as pd
from sklearn.preprocessing import StandardScaler

# function for preprocessing data
def preprocess_data():
        # fetching traffic data
        path = 'data/raw/vehicle_count.csv'
        unprocessed_data = pd.read_csv(path)

        unprocessed_data = unprocessed_data.set_index(unprocessed_data.columns[0])
        x_segments = unprocessed_data.T.copy()

        # create data required for the report generation
        segment_names = x_segments.index.to_list()
        segment_mean_raw = x_segments.mean(axis=1)

        # scaling input data
        scaler = StandardScaler()
        x_scaled = scaler.fit_transform(x_segments.values)

        # preparing the input data for the autoencoder
        n_segments, n_timesteps = x_scaled.shape
        x_seq = x_scaled.reshape((n_segments, n_timesteps, 1))

        return x_seq, segment_names, segment_mean_raw

if __name__ == '__main__':
    preprocess_data()