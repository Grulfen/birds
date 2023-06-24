""" Script to download bird songs """
import concurrent.futures
import json
import logging
import pathlib
import time

import click
import requests
from tqdm import tqdm  # type: ignore

from birds.extract_audio import write_loudest_two_seconds_to_file

XENO_CANTO: str = "https://www.xeno-canto.org/api/2"


logging.basicConfig(level=logging.WARNING)

DATA_FOLDER = "data"


def download_chirp(chirp_link: str, path: pathlib.Path) -> None:
    """Download a chirp"""
    logging.info(f"Downloading {chirp_link} to {path}")
    with open(path, "wb") as chirp_file:
        chirp_file.write(requests.get(chirp_link).content)


def download_chirps(bird: str, url: str, max_chirps: int) -> None:
    current_time = time.time()
    request = requests.get(url)
    if request.status_code != 200:
        logging.warning(f"Request to {url} returned status_code {request.status_code}")
        return

    api_data = json.loads(request.content)
    if int(api_data["numSpecies"]) > 1:
        logging.warning(
            f'Recordings are of {api_data["numSpecies"]}'
            ", you might want to make the search more precise"
        )

    logging.info(f'Found {api_data["numRecordings"]} of {bird} songs')
    logging.info(f"Using first {max_chirps} recordings")
    bird_folder = pathlib.Path(f"{DATA_FOLDER}/{bird}")
    print(f"Downloading {bird} chirps")
    for i, recording in tqdm(
        enumerate(api_data["recordings"][:max_chirps]), total=max_chirps
    ):
        tmp_time = time.time()
        time_diff = tmp_time - current_time
        assert time_diff > 0
        if time_diff < 1.0:
            logging.info(
                f"Sleep {time_diff} seconds to rate limit to 1 request per second"
            )
            time.sleep(1 - time_diff)
        long_chirp_file = bird_folder / "long" / f"{bird}_{i}_long.mp3"
        download_chirp(f'{recording["file"]}', long_chirp_file)

    print("")


def convert_chirp(long_chirp_file: pathlib.Path):
    short_chirp_file_name = str(long_chirp_file).replace("long", "short")
    short_chirp_file = pathlib.Path(short_chirp_file_name)
    write_loudest_two_seconds_to_file(long_chirp_file, short_chirp_file)


def convert_chirps(bird) -> None:
    print(f"Converting {bird} chirps")
    bird_folder = pathlib.Path(f"{DATA_FOLDER}/{bird}")
    paths = list((bird_folder / "long").iterdir())
    with concurrent.futures.ProcessPoolExecutor() as executor:
        list(tqdm(executor.map(convert_chirp, paths), total=len(paths)))


def create_folder_for_chirps(bird: str) -> None:
    bird_folder = pathlib.Path(f"{DATA_FOLDER}/{bird}")
    long_sound_folder = bird_folder / "long"
    short_sound_folder = bird_folder / "short"
    long_sound_folder.mkdir(exist_ok=True, parents=True)
    short_sound_folder.mkdir(exist_ok=True, parents=True)


# TODO: Use async programming to download songs faster
@click.command()
@click.option("--num-birds", default=50)
@click.option("--download", default=True)
@click.option("--convert", default=True)
def main(num_birds: int, download: bool, convert: bool) -> None:
    """Download bird songs"""
    bird_urls = {
        "great_tit": f"{XENO_CANTO}/recordings?query=parus+major type:song q:A",
        "blue_tit": f"{XENO_CANTO}/recordings?query=cyanistes+caeruleus type:song q:A",
    }

    for bird, url in bird_urls.items():
        create_folder_for_chirps(bird)
        if download:
            download_chirps(bird, url, max_chirps=num_birds)
        if convert:
            convert_chirps(bird)


if __name__ == "__main__":
    main()
