"""Unit test of main."""

import argparse
import unittest
from pathlib import Path
from unittest.mock import patch

from get_mp3_from_url.get_mp3_from_url.main import main


class TestMain(unittest.TestCase):

    @patch("get_mp3_from_url.get_mp3_from_url.main.download_songs")
    def test_main(self, mock_download_songs):
        batch_file = "batch_file.txt"
        destination_folder = "destination_folder"
        cache_file = "cache_file.txt"

        # Call main function with mocked download_songs
        with patch(
            "argparse.ArgumentParser.parse_args",
            return_value=argparse.Namespace(
                batch=batch_file, destination=destination_folder, already_downloaded=cache_file
            ),
        ):
            main()

        # Check that download_songs has been called once with the correct arguments
        mock_download_songs.assert_called_once_with(Path(batch_file), Path(destination_folder), Path(cache_file))
