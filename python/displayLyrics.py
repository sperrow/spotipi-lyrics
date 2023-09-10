import time
import sys
import logging
from logging.handlers import RotatingFileHandler
from getSongInfo import getSongInfo
from getLyrics import getLyrics
from matrixText import MatrixText
import threading

if len(sys.argv) > 2:
    username = sys.argv[1]
    token_path = sys.argv[2]
    sp_dc = sys.argv[3]

    # Configures logger for storing song data
    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', filename='spotipy.log', level=logging.INFO)
    logger = logging.getLogger('spotipy_logger')

    # automatically deletes logs more than 2000 bytes
    handler = RotatingFileHandler('spotipy.log', maxBytes=2000,  backupCount=3)
    logger.addHandler(handler)

    matrix = MatrixText()

    skip_seconds = 0.5
    prevSong = ''
    currentSong = ''
    is_playing = False
    track = {}
    lyrics = []
    lyrics_synced = False
    currentLyricLine = {}
    currentLyricIndex = -1
    progress_ms = '0'
    counter = 0

    def fetchData(ev):
        global is_playing
        global track
        global progress_ms
        global prevSong
        global currentSong
        global lyrics_synced
        global lyrics
        global currentLyricLine
        global currentLyricIndex
        try:
            start = time.time()
            resp1 = getSongInfo(username, token_path)
            end = time.time()
            # print('response time:', end - start)
            track = resp1['item']
            progress_ms = resp1['progress_ms']
            if (is_playing and not resp1['is_playing']):
                matrix.clear()
            is_playing = resp1['is_playing']
            currentSong = track['id']
            if (prevSong != currentSong):
                lyrics = []
                lyrics_synced = False
                currentLyricLine = {}
                currentLyricIndex = -1
                resp2 = getLyrics(sp_dc, currentSong)
                if (type(resp2) is dict):
                    response = resp2['lyrics']
                    lyrics_synced = 'syncType' in response and response['syncType'] == 'LINE_SYNCED'
                    if (response['lines']):
                        lyrics = response['lines']
                else:
                    print('resp2:', resp2)
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
                        # add skip_seconds to show current lyric slighty early
                        currentStartTimeMs = int(line['startTimeMs']) - int(skip_seconds * 1000)
                        # current lyric is first line that is greater than progress_ms
                        if (int(progress_ms) < currentStartTimeMs):
                            if (i == 0):
                                # song's first lyric hasn't started yet
                                currentLyricLine = {}
                                currentLyricIndex = -1
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
                progress_ms = str(int(progress_ms) + int(skip_seconds * 1000))
                time.sleep(skip_seconds)
            except Exception as e:
                print(e)
                time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(0)

else:
    print('Usage: %s username' % (sys.argv[0],))
    sys.exit()
