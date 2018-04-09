""" Script to download bird songs """
import sys
import time
import requests
from bs4 import BeautifulSoup
from extract_audio import extract_two_loudest_seconds


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


def main():
    """ Download bird songs """
    xeno_canto = "https://www.xeno-canto.org"
    bird_urls = {"great_tit": "{}/species/Parus-major?query=type%3Asong".format(xeno_canto),
                 "blue_tit": "{}/species/Cyanistes-caeruleus?query=type%3Asong".format(xeno_canto)}

    for bird, url in bird_urls.items():
        # TODO: Move this to its own function
        xeno_canto_request = requests.get(url)

        html_soup = BeautifulSoup(xeno_canto_request.content, "html.parser")
        chirp_links = audio_links(html_soup)

        max_links = 30

        for i, chirp_link in zip(range(max_links), chirp_links):
            chirp_file = "data/{bird}/{bird}_{i}".format(bird=bird, i=i)
            write_chirp(download_chirp(xeno_canto + chirp_link),
                        chirp_file + ".mp3")
            extract_two_loudest_seconds(chirp_file + ".mp3",
                                        chirp_file + "_short.mp3")
            print(".", end="")
            sys.stdout.flush()
            time.sleep(2)


if __name__ == "__main__":
    main()
