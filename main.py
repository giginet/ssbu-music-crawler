import os
import pafy
import urllib.request
from bs4 import BeautifulSoup

class Song(object):
    def __init__(self, name, artist, videoId):
        self.name = name
        self.artist = artist
        self.videoId = videoId
        self.youtube = None

    def __str__(self):
        return "{}({})".format(self.name, self.artist)

    def download(self, dir):
        if not self.youtube:
            self.youtube = pafy.new(self.videoId)
        stream = self.youtube.getbestaudio()
        stream.download(dir)


class SmashBrosMusicCrawler(object):
    SOURCE_URL = 'http://smashbros-ultimate.com/music'
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'musics')

    def __init__(self):
        dir = self.OUTPUT_DIR
        if not os.path.exists(dir):
            os.mkdir(dir)

    def fetch(self):
        print("Fetching Music List")
        response = urllib.request.urlopen(self.SOURCE_URL)
        html = response.read()
        soup = BeautifulSoup(html)
        # `class`をキーワード引数に渡すことはできない
        song_elems = soup.find_all(**{'class': 'songLine'})

        def parse_song(song):
            name = song.find(**{'class': 'music_name'}).string
            artist = song.find(**{'class': 'music_game'}).string
            def has_audiolink(tag):
                return tag.has_attr('audiolink')
            videoId = song.find(has_audiolink)['audiolink']

            obj = Song(name, artist, videoId)
            return obj

        songs = [parse_song(song) for song in song_elems]
        count = len(songs)
        for i, song in enumerate(songs):
            info = (str(song), i + 1, count)
            print("Fetch {0} ({1} / {2})".format(*info))
            song.download(self.OUTPUT_DIR)


if __name__ == '__main__':
    crawler = SmashBrosMusicCrawler()
    crawler.fetch()
