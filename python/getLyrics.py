from spotify.api import SpotifyClient
import logging

logger = logging.getLogger("spotipi")

_clients = {}


def getLyrics(sp_dc, id):
    if sp_dc not in _clients:
        logger.info("Initializing SpotifyClient for lyrics fetching")
        _clients[sp_dc] = SpotifyClient(sp_dc)
    return _clients[sp_dc].get_lyrics(id)
