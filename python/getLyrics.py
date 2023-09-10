from syrics.api import Spotify

def getLyrics(sp_dc, id):
    sp = Spotify(sp_dc)
    return sp.get_lyrics(id)