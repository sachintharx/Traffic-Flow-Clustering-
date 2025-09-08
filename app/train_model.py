from tensorflow.keras.callbacks import EarlyStopping

from autoencoder import build_autoencoder

# function for training the autoencoder model
def train_autoencoder(latent_dim, processed_data, input_shape, validation_split=0.25, epochs=50, batch_size=32):
        x_seq = processed_data
        autoencoder, encoder = build_autoencoder(latent_dim, input_shape)

        early_stop = EarlyStopping(
            monitor="val_loss",
            patience=5,
            mode="min",
            restore_best_weights=True,
            verbose=0
        )
        
        # training the model with early stopping
        history = autoencoder.fit(
            x_seq, x_seq,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            shuffle=True,
            verbose=0,
            callbacks=[early_stop]
        )

        print("Validation Loss:", min(history.history["val_loss"]))

        return encoder

if __name__ == '__main__':
    train_autoencoder()