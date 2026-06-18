from spotify.api import SpotifyClient
import logging

logger = logging.getLogger("spotipi")

def getLyrics(sp_dc, id):
    logger.debug("Initializing SpotifyClient for lyrics fetching")
    client = SpotifyClient(sp_dc)
    return client.get_lyrics(id)
