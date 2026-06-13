from spotify.api import SpotifyClient

_clients = {}

def getLyrics(sp_dc, id):
    if sp_dc not in _clients:
        _clients[sp_dc] = SpotifyClient(sp_dc)
    return _clients[sp_dc].get_lyrics(id)
