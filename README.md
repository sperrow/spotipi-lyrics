# Spotipi

### Video

https://www.youtube.com/shorts/PKM1I0vdbhE

### Overview

This project is to display lyrics from the Spotify web api on a 64x32 led matrix.

- Recommend using a RPi 3 or higher (Zero is too slow for this).
- Originally forked from Ryan Ward's project for displaying cover art: https://github.com/ryanwa18/spotipi
- Uses [librelyrics-spotify](https://github.com/libre-lyrics/librelyrics-spotify) to fetch the lyrics data from Spotify

### Getting Started

Guide: https://sperrow.cc/2024/05/09/spotipi-lyrics.html

- Create a new application within the [Spotify developer dashboard](https://developer.spotify.com/dashboard/applications). Set the redirect uri to any local url such as http://127.0.0.1/callback
- SSH to your raspberry pi to clone the repository

```
git clone https://github.com/sperrow/spotipi-lyrics
```

- Change into the directory

```
cd spotipi-lyrics
```

- Install the software: <br />

```
sudo bash install.sh
```

- Run the configuration script and enter the prompted spotify credentials using

```
bash configure-credentials.sh
```

- This will generate a file named `.spotipi-config` which will be used for authentication
    - A url will show up in the terminal window and you must copy this into your own web broswer
    - The url will redirect you to another url and you need to copy/paste this in the terminal when prompted.
