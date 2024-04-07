"""Example of unittest file"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

from get_mp3_from_url.get_mp3_from_url.song_downloader import (
    YT_DL_OPTIONS,
    delete_webp_hook,
    download_songs,
    get_output_template,
)


class TestDownloadSongs(unittest.TestCase):
    def test_download_songs_raise_if_batch_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            download_songs(
                Path("Not existing"), Path("/home/foo/downloads"), Path("/home/foo/.get_mp3_from_url/cache.txt")
            )

    def test_download_songs_raise_if_destination_folder_not_found(self):
        with self.assertRaises(FileNotFoundError):
            download_songs(Path(__file__), Path("not existing"), Path("/home/foo/.get_mp3_from_url/cache.txt"))

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="https://www.youtube.com/watch?v=video1\nhttps://www.youtube.com/watch?v=video2\n",
    )
    @patch("get_mp3_from_url.get_mp3_from_url.song_downloader.yt_dlp.YoutubeDL")
    @patch("get_mp3_from_url.get_mp3_from_url.song_downloader.Path.exists")
    @patch("get_mp3_from_url.get_mp3_from_url.song_downloader.logging.warning")
    def test_download_songs(self, mock_warning, mock_exists, mock_youtube_dl, mock_open_file):
        # Prepare test data
        batch_file_path = Path("test_batch_file.txt")
        destination_folder = Path("test_destination_folder")
        already_downloaded_list_file_path = Path("non_existing_cache_file.txt")

        mock_youtube_downloader = MagicMock()
        mock_youtube_downloader.download.side_effect = lambda urls: print("Downloading:", urls)
        mock_youtube_dl.return_value.__enter__.return_value = mock_youtube_downloader

        mock_exists.side_effect = [True, True, False]

        download_songs(batch_file_path, destination_folder, already_downloaded_list_file_path)

        mock_open_file.assert_called_once_with(str(batch_file_path), encoding="utf-8")

        expected_options = YT_DL_OPTIONS
        expected_options["download_archive"] = str(already_downloaded_list_file_path)
        expected_options["outtmpl"] = get_output_template(destination_folder)

        mock_youtube_dl.assert_called_once_with(expected_options)

        expected_calls = [
            unittest.mock.call(["https://www.youtube.com/watch?v=video1"]),
            unittest.mock.call(["https://www.youtube.com/watch?v=video2"]),
        ]
        mock_youtube_downloader.download.assert_has_calls(expected_calls, any_order=False)
        mock_warning.assert_called_once_with(
            "Cache file not found %s. Will create one", str(already_downloaded_list_file_path)
        )


class TestGetOutputTemplate(unittest.TestCase):
    def test_get_output_template(self):
        destination_path = Path(Path.home() / "Downloads" / "mp3_from_url")
        expected_template = str(destination_path) + "/%(title)s.%(ext)s"
        self.assertEqual(expected_template, get_output_template(destination_path))


class TestDeleteWebpHook(unittest.TestCase):
    @patch("get_mp3_from_url.get_mp3_from_url.song_downloader.Path.exists")
    @patch("get_mp3_from_url.get_mp3_from_url.song_downloader.Path.unlink")
    def test_delete_webp_hook(self, mock_unlink, mock_exists):

        mock_exists.return_value = True
        mock_unlink.return_value = None

        delete_webp_hook({"status": "finished", "info_dict": {"__files_to_move": {"webp_file_path": "dummy_path"}}})

        mock_exists.assert_called_once_with()
        mock_unlink.assert_called_once_with()
