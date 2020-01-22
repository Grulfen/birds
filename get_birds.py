""" Script to download bird songs """
import sys
import time
import logging
import json
import pathlib
import requests
from birds.extract_audio import write_loudest_two_seconds_to_file

XENO_CANTO: str = "https://www.xeno-canto.org/api/2"


logging.basicConfig(level=logging.INFO)


def download_chirp(chirp_link: str, path: pathlib.Path) -> None:
    """ Download a chirp """
    logging.info(f"Downloading {chirp_link} to {path}")
    with open(path, "wb") as chirp_file:
        chirp_file.write(requests.get(chirp_link).content)


def download_chirps(bird: str, url: str, max_chirps: int) -> None:
    # TODO: Add path where to save chirps
    request = requests.get(url)
    if request.status_code != 200:
        logging.warning(f"Request to {url} returned status_code {request.status_code}")
        return

    api_data = json.loads(request.content)
    if int(api_data["numSpecies"]) > 1:
        logging.warning(
            f'Recordings are of {api_data["numSpecies"]}, you might want to make the search more precise'
        )

    logging.info(f'Found {api_data["numRecordings"]} of {bird} songs')
    logging.info(f"Using first {max_chirps} recordings")
    bird_folder = pathlib.Path(f"data/{bird}")
    for i, recording in zip(range(max_chirps), api_data["recordings"]):
        long_chirp_file = bird_folder / "long" / f"{bird}_{i}_long.mp3"
        short_chirp_file = bird_folder / "short" / f"{bird}_{i}_short.ogg"
        download_chirp(f'http:{recording["file"]}', long_chirp_file)
        write_loudest_two_seconds_to_file(long_chirp_file, short_chirp_file)
        print(".", end="")
        sys.stdout.flush()
        time.sleep(2)
    print("")


def create_folder_for_chirps(bird: str) -> None:
    bird_folder = pathlib.Path(f"data/{bird}")
    long_sound_folder = bird_folder / "long"
    short_sound_folder = bird_folder / "short"
    long_sound_folder.mkdir(exist_ok=True, parents=True)
    short_sound_folder.mkdir(exist_ok=True, parents=True)


def main():
    """ Download bird songs """
    bird_urls = {
        "great_tit": f"{XENO_CANTO}/recordings?query=parus+major type:song q:A",
        "blue_tit": f"{XENO_CANTO}/recordings?query=cyanistes+caeruleus type:song q:A",
    }

    for bird, url in bird_urls.items():
        create_folder_for_chirps(bird)
        print(f"Downloading {bird} chirps")
        download_chirps(bird, url, max_chirps=30)


if __name__ == "__main__":
    main()
