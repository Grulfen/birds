""" Script to download bird songs """
import asyncio
import concurrent.futures
import logging
import pathlib

import aiohttp
import click
from tqdm import tqdm  # type: ignore
from tqdm.asyncio import tqdm_asyncio  # type: ignore

from birds.extract_audio import write_loudest_two_seconds_to_file

XENO_CANTO: str = "https://www.xeno-canto.org/api/2"


logging.basicConfig(level=logging.WARNING)

DATA_FOLDER = "data"


class RateLimiter:
    def __init__(self, queries_per_second: int):
        self.loop = asyncio.get_event_loop()
        self.last_time = None
        self.queued_calls = 0
        self.queries_per_second = queries_per_second

    async def __aenter__(self):
        if self.last_time is None:
            self.last_time = self.loop.time()
            return

        self.queued_calls += 1
        interval = 1 / self.queries_per_second
        elapsed_time = self.loop.time() - self.last_time
        time_to_wait = self.queued_calls * interval - elapsed_time
        if time_to_wait > 0:
            await asyncio.sleep(time_to_wait)
        self.last_time = self.loop.time()
        self.queued_calls -= 1

    async def __aexit__(self, exc_type, exc, tb):
        pass


async def download_chirp(
    chirp_link: str, path: pathlib.Path, rate_limiter: RateLimiter
) -> None:
    """Download a chirp"""
    if path.exists():
        logging.info(f"{path} already exists, skipping {chirp_link}")
        return
    loop = asyncio.get_event_loop()
    async with rate_limiter:
        async with aiohttp.ClientSession() as session:
            async with session.get(chirp_link) as response:
                logging.info(f"{loop.time():.2f}: -> {chirp_link} to {path}")
                content = await response.read()
                logging.info(f"{loop.time():.2f}: <- got response for {chirp_link}")
                with open(path, "wb") as chirp_file:
                    chirp_file.write(content)


async def download_chirps(bird: str, url: str, max_chirps: int) -> None:
    rate_limiter = RateLimiter(queries_per_second=1)
    async with rate_limiter:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    logging.warning(
                        f"Request to {url} returned status_code {response.status}"
                    )
                    return

                api_data = await response.json()

    if int(api_data["numSpecies"]) > 1:
        logging.warning(
            f'Recordings are of {api_data["numSpecies"]}'
            ", you might want to make the search more precise"
        )

    logging.info(f'Found {api_data["numRecordings"]} of {bird} songs')
    logging.info(f"Using first {max_chirps} recordings")
    bird_folder = pathlib.Path(f"{DATA_FOLDER}/{bird}")
    downloads = []
    for i, recording in enumerate(api_data["recordings"][:max_chirps]):
        long_chirp_file = bird_folder / "long" / f'{bird}_{recording["id"]}_long.mp3'
        downloads.append(
            download_chirp(f'{recording["file"]}', long_chirp_file, rate_limiter)
        )
    await tqdm_asyncio.gather(*downloads, desc=bird)


def convert_chirp(long_chirp_file: pathlib.Path):
    short_chirp_file_name = str(long_chirp_file).replace("long", "short")
    short_chirp_file = pathlib.Path(short_chirp_file_name)
    if short_chirp_file.exists():
        return
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
            asyncio.run(download_chirps(bird, url, max_chirps=num_birds))
        if convert:
            convert_chirps(bird)


if __name__ == "__main__":
    main()
