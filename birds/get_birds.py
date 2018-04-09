""" Script to download bird songs """
import sys
import time
import requests
from bs4 import BeautifulSoup
from extract_audio import extract_two_loudest_seconds
import io


XENO_CANTO = "https://www.xeno-canto.org"


def is_audio(link):
    """ determine if @link is audio """
    if link.has_attr("download") and link.has_attr("href"):
        return link["download"].endswith(".mp3")
    return False


def audio_links(html_soup):
    """ Get all links with mp3 files """
    songs = []
    links = html_soup.find_all("a")
    for link in links:
        if is_audio(link):
            songs.append(link["href"])
    return songs


def write_chirp(chirp, name):
    """ Write chirp to file @name """
    with open(name, "bw") as chirp_file:
        chirp_file.write(chirp)


def download_chirp(chirp_link):
    """ Download a chirp """
    return requests.get(chirp_link).content


def download_chirps(bird: str, url: str, max_chirps: int):
    xeno_canto_request = requests.get(url)

    html_soup = BeautifulSoup(xeno_canto_request.content, "html.parser")
    chirp_links = audio_links(html_soup)

    for i, chirp_link in zip(range(max_chirps), chirp_links):
        chirp_file = "data/{bird}/{bird}_{i}".format(bird=bird, i=i)
        chirp_content = io.BytesIO(download_chirp(XENO_CANTO + chirp_link))
        extract_two_loudest_seconds(chirp_content, chirp_file + "_short.mp3")
        print(".", end="")
        sys.stdout.flush()
        time.sleep(2)


def main():
    """ Download bird songs """
    bird_urls = {"great_tit": "{}/species/Parus-major?query=type%3Asong".format(XENO_CANTO),
                 "blue_tit": "{}/species/Cyanistes-caeruleus?query=type%3Asong".format(XENO_CANTO)}

    for bird, url in bird_urls.items():
        download_chirps(bird, url, max_chirps=30)


if __name__ == "__main__":
    main()
