import spotipy
import spotipy.util as util
import logging

logger = logging.getLogger("spotipi")


def getSongInfo(username, token_path):
    scope = "user-read-currently-playing"
    token = util.prompt_for_user_token(username, scope, cache_path=token_path)
    if token:
        sp = spotipy.Spotify(auth=token)
        result = sp.current_user_playing_track()

        if result is None:
            logger.debug("No song playing")
            return {}
        else:
            song = result["item"]["name"]
            logger.debug("getSongInfo: %s", song)
            return result
    else:
        logger.error("Can't get token for %s", username)
        return None
