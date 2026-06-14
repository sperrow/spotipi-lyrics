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

1. **Spotify Developer Setup**:
    - Create a new application in the [Spotify developer dashboard](https://developer.spotify.com/dashboard/applications).
    - Set the redirect URI to `http://127.0.0.1/callback`.

2. **Installation**:
   SSH to your Raspberry Pi and run:

    ```bash
    git clone https://github.com/sperrow/spotipi-lyrics
    cd spotipi-lyrics
    sudo bash install.sh
    ```

3. **Configuration**:
   Run the interactive configuration script:

    ```bash
    bash configure-credentials.sh
    ```

    _Note: You can press Enter to keep existing values if you have already configured them._

4. **Authentication**:
    - The script will provide a URL to visit in your browser.
    - After authorizing, copy the URL you are redirected to (the one starting with `http://127.0.0.1/callback`) and paste it back into the terminal.

### Usage

The service will start automatically on reboot. You can also manage it manually: `sudo systemctl restart spotipi`

### Troubleshooting

Logs are stored in `spotipy.log` in the project root. To view them in real-time:

```bash
tail -f spotipy.log
```
