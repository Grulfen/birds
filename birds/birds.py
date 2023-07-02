import logging
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import click
import librosa
import matplotlib.pyplot as plt  # type: ignore
import numpy as np
from termcolor import colored
from extract_audio import write_loudest_two_seconds_to_file
from sklearn.model_selection import train_test_split  # type: ignore
from tensorflow import keras  # type: ignore

Spectrogram = np.ndarray

MODEL_PATH = Path("model/latest_model")


logging.basicConfig(level=logging.WARNING)

BIRDS = ["blue_tit", "great_tit"]


@dataclass
class Data:
    chirps: list[Spectrogram]
    birds: list[int]


def create_model():
    model = keras.models.Sequential()
    model.add(
        keras.layers.Conv2D(32, (3, 3), activation="relu", input_shape=(128, 87, 1))
    )
    model.add(keras.layers.MaxPooling2D((2, 2)))
    model.add(keras.layers.Conv2D(64, (3, 3), activation="relu"))
    model.add(keras.layers.MaxPooling2D((2, 2)))
    model.add(keras.layers.Conv2D(64, (3, 3), activation="relu"))

    model.add(keras.layers.Flatten())
    model.add(keras.layers.Dense(2, activation="softmax"))

    model.summary()

    return model


def fit_model(model, training_data: Data, validation_data: Data):
    model.compile(
        loss="sparse_categorical_crossentropy",
        optimizer=keras.optimizers.RMSprop(learning_rate=0.001),
        metrics="accuracy",
    )
    history = model.fit(
        training_data.chirps,
        training_data.birds,
        epochs=10,
        validation_data=(validation_data.chirps, validation_data.birds),
    )
    return history, model


def prepare_chirp(chirp_path: Path) -> Spectrogram:
    samples, sample_rate = librosa.load(chirp_path)
    return librosa.feature.melspectrogram(y=samples, sr=sample_rate)


def prepare_chirps() -> tuple[Data, Data, Data]:
    all_chirps = []
    birds = []
    for index, bird in enumerate(BIRDS):
        for chirp_file in Path(f"data/{bird.lower()}/short/").iterdir():
            all_chirps.append(prepare_chirp(chirp_file))
            birds.append(index)

    chirp_train, chirp_test, birds_train, birds_test = train_test_split(
        np.array(all_chirps), np.array(birds), test_size=0.33, random_state=12
    )

    chirp_validation, chirp_train, birds_validation, birds_train = train_test_split(
        np.array(chirp_test), np.array(birds_test), test_size=0.5, random_state=12
    )

    training_data = Data(chirp_train, birds_train)
    test_data = Data(chirp_test, birds_test)
    validation_data = Data(chirp_validation, birds_validation)

    return training_data, test_data, validation_data


def train() -> keras.models.Sequential:
    training_data, test_data, validation_data = prepare_chirps()
    model = create_model()
    history, model = fit_model(model, training_data, validation_data)
    plt.plot(history.history["accuracy"], label="accuracy")
    plt.plot(history.history["val_accuracy"], label="val_accuracy")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.ylim([0.5, 1])
    plt.legend(loc="lower right")
    plt.savefig("tjo.png")

    test_loss, test_accuracy = model.evaluate(
        test_data.chirps, test_data.birds, verbose=2
    )
    model.save(MODEL_PATH)
    return model


def get_model(retrain: bool) -> keras.models.Sequential:
    if retrain:
        logging.info("Retraining model")
        return train()
    if not MODEL_PATH.exists():
        logging.info("No model in {MODEL_PATH}. Training a new model")
        return train()
    logging.info(f"Loading model from {MODEL_PATH}")
    return keras.models.load_model(MODEL_PATH)


def confidence_color(confidence: float) -> str:
    if confidence > 0.9:
        return "green"
    if confidence > 0.7:
        return "yellow"
    return "red"


@click.command()
@click.option(
    "--train/--no-train", "retrain", default=False, help="If set, train a new model"
)
@click.option(
    "--classify",
    type=click.Path(exists=True, path_type=Path, dir_okay=False),
    multiple=True,
    help="paths to birds songs that are to be classified",
)
def main(retrain: bool, classify=Optional[Path]) -> None:
    model = get_model(retrain)
    if not classify:
        return
    chirps = []
    with tempfile.TemporaryDirectory() as tmpdir:
        short_path = Path(tmpdir) / "short.mp3"
        for to_classify in classify:
            write_loudest_two_seconds_to_file(to_classify, short_path)
            chirps.append(prepare_chirp(short_path))
    predictions = model.predict(np.array(chirps), verbose=0)
    for prediction in predictions:
        best_idx = np.argmax(prediction)
        confidence = prediction[best_idx]
        color = confidence_color(confidence)
        print(colored(BIRDS[best_idx], color), prediction)


if __name__ == "__main__":
    main()
