# get_mp3_from_url

This utility will download song from url (e.g. Youtube) in mp3 format.

## Installation

```bash
python3 -m pip install get_mp3_from_url
```

## Usage

You can save url in a batch file and use a `-b` argument.
You can specify the folder where to download them using `-d` argument.
The utility keep track of url already downloaded to prevent double downloading.
You can override the path to this cache file using `-a` argument.
Default is `"$HOME"/.get_mp3_from_url/song_downloaded.txt`

You can specify optional `-c` argument to let to utility
*try to* clean the song file name from ugly pattern.

```bash
get_mp3_from_url -b song_list.txt -d "$HOME"/Downloads -a "$HOME"/.get_mp3_from_url/song_downloaded.txt -c
```
