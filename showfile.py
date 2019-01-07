# coding=utf-8
import re
from xml.dom import minidom


class ShowFile:
    def __init__(self, item):
        self.parseXml(item)

    def parseXml(self, item):
        self.parseTitle(ShowFile.getText(item.getElementsByTagName("title")[0].childNodes))
        self.pubDate = ShowFile.getText(item.getElementsByTagName("pubDate")[0].childNodes)
        self.link = ShowFile.getText(item.getElementsByTagName("link")[0].childNodes)


    @staticmethod
    def getText(nodelist):
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)

    def parseTitle(self, title):
        regex = r"^(?P<showName>.*)\s\((?P<originalName>.*)\)\.\s(?P<episodName>.*)\s\(S(?P<season>\d+)E(?P<episode>\d+)\)\s\[(?P<quality>\w+)\]$"
        match = re.match(regex, title)
        if(match):
            self.showName = match.group("showName")
            self.originalName = match.group("originalName")
            self.episodName = match.group("episodName")
            self.season = match.group("season")
            self.episode = match.group("episode")
            self.quality = match.group("quality")
