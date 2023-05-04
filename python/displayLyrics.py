import time
import sys
import logging
from logging.handlers import RotatingFileHandler
from getSongInfo import getSongInfo
from matrixText import MatrixText
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
    lyrics = []
    lyrics_synced = False
    currentLyricLine = {}

    try:
        while True:
            try:
                resp = getSongInfo(username, token_path)
                track = resp['item']
                print('is_playing:', resp['is_playing'])
                currentSong = track['id']
                if (prevSong != currentSong):
                    res = requests.get(
                        'https://spotify-lyric-api.herokuapp.com/?trackid=' + currentSong)
                    response = res.json()
                    print('response:', response)
                    lyrics_synced = 'syncType' in response and response['syncType'] == 'LINE_SYNCED'
                    if (not response['error'] and response['lines']):
                        lyrics = response['lines']
                prevSong = currentSong
                current_i = 0
                print('lyrics_synced:', lyrics_synced)
                if (lyrics_synced):
                    currentLyricLine = lyrics[0]
                    for i in range(len(lyrics)):
                        line = lyrics[i]
                        # buffer 1 sec
                        if (int(resp['progress_ms']) < int(line['startTimeMs']) - 1000):
                            if (i == 0):
                                currentLyricLine = {}
                            break
                        currentLyricLine = line
                        current_i = i
                else:
                    currentLyricLine = {}

                if (resp['is_playing']):
                    if ('words' in currentLyricLine):
                        line_1 = currentLyricLine['words']
                        line_2 = ''
                        if (current_i+1 < len(lyrics) and 'words' in lyrics[current_i+1]):
                            line_2 = lyrics[current_i+1]['words']
                        matrix.displayText(line_1, line_2)
                    else:
                        matrix.displayText(
                            track['name'], track['artists'][0]['name'])
                time.sleep(1)
            except Exception as e:
                print(e)
                time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(0)

else:
    print('Usage: %s username' % (sys.argv[0],))
    sys.exit()
