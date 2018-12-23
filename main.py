import os
import pafy
import urllib.request
from bs4 import BeautifulSoup
from pydub import AudioSegment

class Truncator(object):
    DURATION = 300 * 1000
    FADEOUT_DURATION = 3 * 1000
    OUTPUT_FORMAT = "mp3"
    OUTPUT_EXTENSION = "mp3"

    def __init__(self, song):
        self.song = song
        self.segment = AudioSegment.from_file(song.path, song.extension)

    def save_truncated(self, dir):
        if self.segment.duration_seconds >= 300:
            converted = self.segment[:self.DURATION].fade_out(self.FADEOUT_DURATION)
        else:
            converted = self.segment
        basename = self.song.videoId
        output_filename = f"{basename}.{self.OUTPUT_EXTENSION}"
        output_path = os.path.join(dir, output_filename)
        tags = {'title': self.song.name,
                'artist': self.song.artist, 
                'genre': 'Soundtrack',
                'album': 'Super Smash Bros. Ultimate',
                'comments': self.song.videoId}
        converted.export(output_path, bitrate="256k", format=self.OUTPUT_FORMAT, tags=tags)


class Song(object):
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'musics', 'original')

    def __init__(self, name, artist, videoId):
        self.name = name
        self.artist = artist
        self.videoId = videoId
        self.youtube = None

    def __str__(self):
        return "{}({})".format(self.name, self.artist)

    def fetch(self):
        self.youtube = pafy.new(self.videoId)
        self.stream = self.youtube.getbestaudio()
        self.extension = self.stream.extension
        self.path = os.path.join(self.OUTPUT_DIR, f"{self.videoId}.{self.extension}")

    def download(self):
        if self.youtube:
            self.stream.download(self.path)


class SmashBrosMusicCrawler(object):
    SOURCE_URL = 'http://smashbros-ultimate.com/music'
    ORIGINAL_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'musics', 'original')
    CONVERTED_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'musics', 'truncated')

    def __init__(self):
        os.makedirs(self.ORIGINAL_OUTPUT_DIR, exist_ok=True)
        os.makedirs(self.CONVERTED_OUTPUT_DIR, exist_ok=True)

    def fetch(self):
        print("Fetching Music List")
        response = urllib.request.urlopen(self.SOURCE_URL)
        html = response.read()
        soup = BeautifulSoup(html, features="html.parser")
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
        already_downloaded = os.listdir(self.ORIGINAL_OUTPUT_DIR)
        already_converted = os.listdir(self.CONVERTED_OUTPUT_DIR)
        for i, song in enumerate(songs):
            info = (str(song), i + 1, count)
            song.fetch()
            checked = [f for f in already_downloaded if f.startswith(song.videoId) and not f.endswith(".temp")]
            if len(checked) != 0: 
                print("{0} ({1} / {2}) is already downloaded".format(*info))
            else:
                print("Fetching {0} ({1} / {2})".format(*info))
                song.download()
            checked = [f for f in already_downloaded if f.startswith(song.videoId) and not f.endswith(".temp")]
            if len(checked) != 0: 
                print("Skip Converting")
            else:
                print("Converting...")
                truncator = Truncator(song)
                truncator.save_truncated(self.CONVERTED_OUTPUT_DIR)


if __name__ == '__main__':
    crawler = SmashBrosMusicCrawler()
    crawler.fetch()
