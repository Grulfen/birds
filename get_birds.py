""" Script to download bird songs """
import sys
import time
import logging
import json
import pathlib
import requests
from birds.extract_audio import extract_two_loudest_seconds
import io

XENO_CANTO: str = "https://www.xeno-canto.org/api/2"


logging.basicConfig(level=logging.INFO)


def write_chirp(chirp, name):
    """ Write chirp to file @name """
    with open(name, "bw") as chirp_file:
        chirp_file.write(chirp)


def download_chirp(chirp_link) -> bytes:
    """ Download a chirp """
    logging.info(f"Downloading {chirp_link}")
    return requests.get(chirp_link).content


def download_chirps(bird: str, url: str, max_chirps: int) -> None:
    request = requests.get(url)
    if request.status_code != 200:
        logging.warning(f"Request to {url} returned status_code {request.status_code}")
        return

    api_data = json.loads(request.content)
    if int(api_data["numSpecies"]) > 1:
        logging.warning(f'Recordings are of {api_data["numSpecies"]}, you might want to make the search more precise')

    logging.info(f'Found {api_data["numRecordings"]} of {bird} songs')
    logging.info(f'Using first {max_chirps} recordings')
    for i, recording in zip(range(max_chirps), api_data["recordings"]):
        # TODO: Use pathlib here
        chirp_file = f"data/{bird}/{bird}_{i}"
        chirp_content = io.BytesIO(download_chirp(f'http:{recording["file"]}'))
        extract_two_loudest_seconds(chirp_content, f"{chirp_file}_short.mp3")
        print(".", end="")
        sys.stdout.flush()
        time.sleep(2)
    print("")


def create_folder_for_chirps(bird: str) -> None:
    bird_folder = pathlib.Path(f"data/{bird}")
    bird_folder.mkdir(exist_ok=True, parents=True)


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
