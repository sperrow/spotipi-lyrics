import time
import sys
import logging
from logging.handlers import RotatingFileHandler
from getSongInfo import getSongInfo
from matrixText import MatrixText
import threading
import requests

if len(sys.argv) > 2:
    username = sys.argv[1]
    token_path = sys.argv[2]

    # Configures logger for storing song data
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', filename='spotipy.log', level=logging.INFO)
    logger = logging.getLogger('spotipy_logger')

    # automatically deletes logs more than 2000 bytes
    handler = RotatingFileHandler('spotipy.log', maxBytes=2000,  backupCount=3)
    logger.addHandler(handler)

    matrix = MatrixText()

    prevSong = ''
    currentSong = ''
    is_playing = False
    track = {}
    lyrics = []
    lyrics_synced = False
    currentLyricLine = {}
    progress_ms = '0'

    def fetchData(ev):
        global is_playing
        global track
        global progress_ms
        global prevSong
        global currentSong
        global lyrics_synced
        global lyrics
        try:
            start = time.time()
            resp = getSongInfo(username, token_path)
            end = time.time()
            # print('response time:', end - start)
            track = resp['item']
            progress_ms = resp['progress_ms']
            if (is_playing and not resp['is_playing']):
                matrix.clear()
            is_playing = resp['is_playing']
            currentSong = track['id']
            if (prevSong != currentSong):
                lyrics = []
                lyrics_synced = False
                res = requests.get(
                    'https://spotify-lyric-api.herokuapp.com/?trackid=' + currentSong)
                response = res.json()
                lyrics_synced = 'syncType' in response and response['syncType'] == 'LINE_SYNCED'
                if (not response['error'] and response['lines']):
                    lyrics = response['lines']
            prevSong = currentSong
            sleep = 1 if is_playing else 5
            threading.Timer(sleep, fetchData, [ev]).start()
        except Exception as e:
            print(e)
            threading.Timer(10, fetchData, [ev]).start()

    th_event = threading.Event()
    fetchData(th_event)

    try:
        while True:
            try:
                current_i = 0
                if (lyrics_synced):
                    currentLyricLine = lyrics[0]
                    for i in range(len(lyrics)):
                        line = lyrics[i]
                        # buffer 1 sec
                        if (int(progress_ms) < int(line['startTimeMs']) - 1000):
                            if (i == 0):
                                currentLyricLine = {}
                            break
                        currentLyricLine = line
                        current_i = i
                else:
                    currentLyricLine = {}

                if (is_playing):
                    if ('words' in currentLyricLine):
                        line_1 = currentLyricLine['words']
                        line_2 = ''
                        if (current_i+1 < len(lyrics) and 'words' in lyrics[current_i+1]):
                            line_2 = lyrics[current_i+1]['words']
                        matrix.displayText(line_1, line_2)
                    else:
                        matrix.displayText(
                            track['name'], track['artists'][0]['name'])
                skip_seconds = 1
                progress_ms = str(int(progress_ms) + skip_seconds * 1000)
                time.sleep(skip_seconds)
            except Exception as e:
                print(e)
                time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(0)

else:
    print('Usage: %s username' % (sys.argv[0],))
    sys.exit()
