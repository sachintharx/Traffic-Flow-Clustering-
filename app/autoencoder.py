from tensorflow import keras
from tensorflow.keras import layers

# function for building the autoencoder
def build_autoencoder(latent_dim, input_shape):
    # encoder
    inputs = keras.Input(shape=input_shape, name="input")
    x = layers.Conv1D(16, 5, padding="same", activation="relu")(inputs)
    x = layers.MaxPooling1D(2, padding="same")(x)
    x = layers.Conv1D(8, 5, padding="same", activation="relu")(x)
    x = layers.MaxPooling1D(2, padding="same")(x)
    x = layers.Conv1D(8, 3, padding="same", activation="relu")(x)

    # latent space
    x = layers.Flatten()(x)
    latent = layers.Dense(latent_dim, name="latent")(x)

    # decoder
    n_timesteps = input_shape[0]
    up_size = n_timesteps // 4 + (n_timesteps % 4 > 0)

    x = layers.Dense(up_size * 8, activation="relu")(latent)
    x = layers.Reshape((up_size, 8))(x)
    x = layers.UpSampling1D(2)(x)
    x = layers.Conv1D(8, 3, padding="same", activation="relu")(x)
    x = layers.UpSampling1D(2)(x)
    x = layers.Conv1D(16, 5, padding="same", activation="relu")(x)
    outputs = layers.Conv1D(1, 3, padding="same", activation=None)(x)

    # models for the complete autoencoder and the encoder
    autoencoder = keras.Model(inputs, outputs, name="conv1d_autoencoder")
    encoder = keras.Model(inputs, latent, name="encoder")

    autoencoder.compile(optimizer=keras.optimizers.Adam(1e-3), loss="mse")

    return autoencoder, encoder

if __name__ == '__main__':
    build_autoencoder()