import time
import sys
import os
import logging
from logging.handlers import RotatingFileHandler
from getSongInfo import getSongInfo
from getLyrics import getLyrics
from matrixText import MatrixText

LOG_FILE = 'spotipy.log'
SKIP_SECONDS = 0.5
RETRY_SECONDS = 10


def configure_logger():
    logging.basicConfig(
        format='%(asctime)s %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        filename=LOG_FILE,
        level=logging.INFO,
    )
    logger = logging.getLogger('spotipy_logger')
    handler = RotatingFileHandler(LOG_FILE, maxBytes=2000, backupCount=3)
    logger.addHandler(handler)
    return logger


class DisplayLyricsApp:
    def __init__(self, username, sp_dc, token_path):
        self.username = username
        self.sp_dc = sp_dc
        self.token_path = token_path
        self.logger = configure_logger()
        self.matrix = MatrixText()

        self.is_playing = False
        self.track = None
        self.lyrics = []
        self.lyrics_synced = False
        self.current_lyric_line = {}
        self.current_lyric_index = -1
        self.progress_ms = 0
        self.scroll_counter = 0
        self.prev_song_id = None

    def run(self):
        self.logger.info('Starting DisplayLyricsApp for user %s', self.username)
        while True:
            try:
                if not self.fetch_spotify_state():
                    time.sleep(RETRY_SECONDS)
                    continue

                if self.is_playing:
                    self.render()
                    self.progress_ms += int(SKIP_SECONDS * 1000)
                time.sleep(SKIP_SECONDS)
            except KeyboardInterrupt:
                self.logger.info('KeyboardInterrupt received, exiting.')
                sys.exit(0)
            except Exception as exc:
                self.logger.error('main loop error: %s', exc)
                time.sleep(1)

    def fetch_spotify_state(self):
        response = getSongInfo(self.username, self.token_path)
        if response is None:
            self.logger.error('Spotify state fetch failed for user %s', self.username)
            return False

        is_playing = response.get('is_playing', False)
        item = response.get('item')

        if self.is_playing and not is_playing:
            self.logger.info('Playback stopped, clearing matrix')
            self.matrix.clear()

        self.is_playing = is_playing
        self.progress_ms = int(response.get('progress_ms', 0))

        if item is None:
            self.logger.warning('No currently playing item returned from Spotify')
            return True

        current_song_id = item.get('id')
        if current_song_id and current_song_id != self.prev_song_id:
            self.logger.info('Track changed: %s', current_song_id)
            self.track = item
            self.prev_song_id = current_song_id
            self.reset_lyrics_state()
            self.fetch_lyrics_for_current_track(current_song_id)

        return True

    def reset_lyrics_state(self):
        self.lyrics = []
        self.lyrics_synced = False
        self.current_lyric_line = {}
        self.current_lyric_index = -1
        self.scroll_counter = 0

    def fetch_lyrics_for_current_track(self, track_id):
        response = getLyrics(self.sp_dc, track_id)
        if not isinstance(response, dict) or 'lyrics' not in response:
            self.logger.error('getLyrics returned invalid data: %s', response)
            return

        lyrics_payload = response['lyrics']
        self.lyrics_synced = lyrics_payload.get('syncType') == 'LINE_SYNCED'
        language = lyrics_payload.get('language')
        if language:
            self.matrix.setLanguage(language)

        self.lyrics = lyrics_payload.get('lines') or []
        self.logger.info('Loaded %d lyric lines (synced=%s)', len(self.lyrics), self.lyrics_synced)

    def render(self):
        if self.lyrics_synced and self.lyrics:
            current_index = self.find_current_lyric_index()
            if current_index >= 0:
                self.current_lyric_line = self.lyrics[current_index]
                self.display_lyrics(current_index)
                return

        self.display_track_info()

    def find_current_lyric_index(self):
        current_index = -1
        for index, line in enumerate(self.lyrics):
            start_ms = int(line.get('startTimeMs', 0)) - int(SKIP_SECONDS * 1000)
            if self.progress_ms < start_ms:
                break
            current_index = index
        return current_index

    def display_lyrics(self, current_index):
        if 'words' not in self.current_lyric_line:
            self.logger.debug('Current lyric line missing words, falling back to track info')
            self.display_track_info()
            return

        next_words = ''
        if current_index + 1 < len(self.lyrics):
            next_line = self.lyrics[current_index + 1]
            next_words = next_line.get('words', '')

        if current_index == self.current_lyric_index:
            self.scroll_counter += 1
        else:
            self.scroll_counter = 0

        self.current_lyric_index = current_index
        self.matrix.displayText(
            self.current_lyric_line['words'],
            next_words,
            self.scroll_counter,
        )

    def display_track_info(self):
        if not self.track:
            self.logger.debug('No track information available to display')
            return

        title = self.track.get('name', '')
        artist = ''
        artists = self.track.get('artists')
        if isinstance(artists, list) and artists:
            artist = artists[0].get('name', '')

        self.matrix.displayText(title, artist, self.scroll_counter, False)
        self.scroll_counter += 1


def resolve_token_path():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_dir, '.cache')


def print_usage_and_exit():
    print('Usage: {} <username> <sp_dc>'.format(sys.argv[0]))
    sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print_usage_and_exit()

    username = sys.argv[1]
    sp_dc = sys.argv[2]
    token_path = resolve_token_path()

    app = DisplayLyricsApp(username, sp_dc, token_path)
    app.run()
