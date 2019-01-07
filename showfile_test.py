# coding=utf-8
import unittest
from xml.dom import minidom
from showfile import ShowFile


class TestLostfilmRss(unittest.TestCase):

    def test_create_showFile_from_xml(self):
        txt = """<rss version="0.91">
        <channel>
        <title>LostFilm.TV</title>
        <description>Свежачок от LostFilm.TV</description>
        <link>https://www.lostfilm.tv/</link>
        <lastBuildDate>Sat, 05 Jan 2019 21:25:52 +0000</lastBuildDate>
        <language>ru</language>
        <item>
        <title>Возвращение (Homecoming). Работа (S01E09) [MP4]</title>
        <category>[MP4]</category>
        <pubDate>Sat, 05 Jan 2019 20:23:35 +0000</pubDate>
        <link>http://tracktor.in/rssdownloader.php?id=31421</link>
        </item>
        </channel>
        </rss>
        """
        xmldoc = minidom.parseString(txt)
        item = xmldoc.getElementsByTagName('item')[0]
        
        e = ShowFile(item)

        self.assertEqual('Возвращение', e.showName)
        self.assertEqual('Homecoming', e.originalName)
        self.assertEqual('Работа', e.episodName)
        self.assertEqual('01', e.season)
        self.assertEqual('09', e.episode)
        self.assertEqual('MP4', e.quality)
        self.assertEqual('Sat, 05 Jan 2019 20:23:35 +0000', e.pubDate)
        self.assertEqual('http://tracktor.in/rssdownloader.php?id=31421', e.link)


if __name__ == '__main__':
    unittest.main()
