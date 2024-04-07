#!/usr/bin/env python3
"""Main script."""

import argparse
from pathlib import Path

from .song_downloader import download_songs


def main():
    """Implement main function. Not implemented."""
    parser = argparse.ArgumentParser(
        description="get_mp3_from_url downloads song from url (e.g. Youtube) in mp3 format."
    )
    parser.add_argument(
        "-b",
        "--batch",
        help="batch file (text file with one url by line)",
        required=True,
    )
    parser.add_argument("-d", "--destination", help="destination where the music should be downloaded", required=True)
    parser.add_argument(
        "-a",
        "--already-downloaded",
        help="path to the cache files that keep track of already downloaded files",
        required=False,
        default=Path.home() / ".get_mp3_from_url" / "song_cache.txt",
    )
    parser.add_argument("-c", "--clean-songs", help="Attempt to clean song name after downloading", required=False)
    args = parser.parse_args()

    download_songs(Path(args.batch), Path(args.destination), Path(args.already_downloaded))


if __name__ == "__main__":
    main()  # pragma no cover
