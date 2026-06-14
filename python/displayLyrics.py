import time
import sys
import os
import logging
from logging.handlers import RotatingFileHandler
from getSongInfo import getSongInfo
from getLyrics import getLyrics
from matrixText import MatrixText

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "spotipy.log")
SKIP_SECONDS = 0.5
FETCH_SECONDS_PLAYING = 1
FETCH_SECONDS_IDLE = 5
RETRY_SECONDS = 10
LYRICS_RETRY_SECONDS = 10


def configure_logger():
    logger = logging.getLogger("spotipi")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )

    # File handler
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=100000, backupCount=3)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class DisplayLyricsApp:
    def __init__(self, username, sp_dc, token_path):
        self.username = username
        self.sp_dc = sp_dc
        self.token_path = token_path
        self.logger = configure_logger()
        self.matrix = MatrixText()

        self.is_playing = False
        self.is_idle = False
        self.track = None
        self.lyrics = []
        self.lyrics_synced = False
        self.current_lyric_index = -1
        self.progress_ms = 0
        self.scroll_counter = 0
        self.prev_song_id = None
        self.next_fetch_time = 0
        self.lyrics_retry_song_id = None
        self.next_lyrics_retry_time = 0

    def run(self):
        self.logger.info("Starting DisplayLyricsApp for user %s", self.username)
        while True:
            try:
                self.maybe_fetch_spotify_state()

                if self.is_playing:
                    self.render()
                    self.progress_ms += int(SKIP_SECONDS * 1000)
                time.sleep(SKIP_SECONDS)
            except Exception:
                self.logger.exception("main loop error")
                time.sleep(1)

    def maybe_fetch_spotify_state(self):
        if time.monotonic() < self.next_fetch_time:
            return

        try:
            fetch_succeeded = self.fetch_spotify_state()
        except Exception:
            self.logger.exception("Spotify state fetch error")
            fetch_succeeded = False

        if fetch_succeeded:
            delay = FETCH_SECONDS_PLAYING if self.is_playing else FETCH_SECONDS_IDLE
        else:
            delay = RETRY_SECONDS
        self.next_fetch_time = time.monotonic() + delay

    def fetch_spotify_state(self):
        response = getSongInfo(self.username, self.token_path)
        if response is None:
            self.logger.error("Spotify state fetch failed for user %s", self.username)
            return False

        is_playing = response.get("is_playing", False)
        item = response.get("item")

        if item is None:
            if not self.is_idle:
                self.logger.info("No active playback, entering idle state")
                self.matrix.clear()
                self.is_idle = True
                self.is_playing = False
                self.prev_song_id = None
            return True

        # If we reach here, we have an item (song is active)
        self.is_idle = False
        
        if self.is_playing and not is_playing:
            self.logger.info("Playback paused, clearing matrix")
            self.matrix.clear()

        self.is_playing = is_playing
        self.progress_ms = safe_int(response.get("progress_ms"))

        current_song_id = item.get("id")
        if current_song_id and current_song_id != self.prev_song_id:
            if current_song_id != self.lyrics_retry_song_id:
                self.logger.info("Track changed: %s", current_song_id)
                self.track = item
                self.reset_lyrics_state()
                self.lyrics_retry_song_id = current_song_id
                self.next_lyrics_retry_time = 0

            if time.monotonic() < self.next_lyrics_retry_time:
                return True

            if self.fetch_lyrics_for_current_track(current_song_id):
                self.prev_song_id = current_song_id
                self.lyrics_retry_song_id = None
            else:
                self.next_lyrics_retry_time = time.monotonic() + LYRICS_RETRY_SECONDS

        return True

    def reset_lyrics_state(self):
        self.lyrics = []
        self.lyrics_synced = False
        self.current_lyric_index = -1
        self.scroll_counter = 0

    def fetch_lyrics_for_current_track(self, track_id):
        response = getLyrics(self.sp_dc, track_id)
        if response is None:
            self.logger.info("No lyrics found for track %s", track_id)
            return False
            
        if not isinstance(response, dict) or "lyrics" not in response:
            self.logger.error("getLyrics returned invalid data: %s", response)
            return False

        lyrics_payload = response["lyrics"]
        if not isinstance(lyrics_payload, dict):
            self.logger.error(
                "getLyrics returned invalid lyrics payload: %s", lyrics_payload
            )
            return False

        self.lyrics_synced = lyrics_payload.get("syncType") == "LINE_SYNCED"
        language = lyrics_payload.get("language")
        if language:
            self.matrix.setLanguage(language)

        lines = lyrics_payload.get("lines") or []
        if not isinstance(lines, list):
            self.logger.error("getLyrics returned invalid lyric lines: %s", lines)
            return False

        self.lyrics = lines
        self.logger.info(
            "Loaded %d lyric lines (synced=%s)", len(self.lyrics), self.lyrics_synced
        )
        return True

    def render(self):
        if self.lyrics_synced and self.lyrics:
            current_index = self.find_current_lyric_index()
            if current_index >= 0:
                self.display_lyrics(current_index, self.lyrics[current_index])
                return

        self.display_track_info()

    def find_current_lyric_index(self):
        current_index = -1
        for index, line in enumerate(self.lyrics):
            start_ms = safe_int(line.get("startTimeMs")) - int(SKIP_SECONDS * 1000)
            if self.progress_ms < start_ms:
                break
            current_index = index
        return current_index

    def display_lyrics(self, current_index, current_lyric_line):
        if "words" not in current_lyric_line:
            self.logger.debug(
                "Current lyric line missing words, falling back to track info"
            )
            self.display_track_info()
            return

        next_words = ""
        if current_index + 1 < len(self.lyrics):
            next_line = self.lyrics[current_index + 1]
            next_words = next_line.get("words", "")

        if current_index == self.current_lyric_index:
            self.scroll_counter += 1
        else:
            self.scroll_counter = 0

        self.current_lyric_index = current_index
        self.matrix.displayText(
            current_lyric_line["words"],
            next_words,
            self.scroll_counter,
        )

    def display_track_info(self):
        if not self.track:
            self.logger.debug("No track information available to display")
            return

        title = self.track.get("name", "")
        artist = ""
        artists = self.track.get("artists")
        if isinstance(artists, list) and artists:
            artist = artists[0].get("name", "")

        self.matrix.displayText(title, artist, self.scroll_counter, False)
        self.scroll_counter += 1


def resolve_token_path():
    return os.path.join(BASE_DIR, ".cache")


def print_usage_and_exit():
    print("Usage: {} <username> <sp_dc>".format(sys.argv[0]))
    sys.exit(1)


def main():
    if len(sys.argv) < 3:
        print_usage_and_exit()

    username = sys.argv[1]
    sp_dc = sys.argv[2]
    token_path = resolve_token_path()

    app = DisplayLyricsApp(username, sp_dc, token_path)
    app.run()


if __name__ == "__main__":
    logger = configure_logger()
    try:
        main()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received, exiting.")
        sys.exit(0)
    except Exception:
        logger.exception("startup error")
        sys.exit(1)
