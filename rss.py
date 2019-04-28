#!/usr/bin/env python3
# coding=utf-8
import urllib.request as urllib
import sqlite3
import os
import sys
import logging
from datetime import datetime
from showfile import ShowFile
import settings

from xml.dom import minidom
import re


def httpGet(target_url):
    opener = urllib.build_opener()
    opener.addheaders.append(('Cookie', "uid={};usess={}".format(settings.UID, settings.USESS)))
    return opener.open(target_url).read()


def saveTorrent(url, filename):
    data = httpGet(url)
    if (data):
        f = open(filename, "wb")
        f.write(data)
        f.close()
        os.chmod(filename, 0o666)


def createTable():
    # Создание таблицы
    cursor.execute("""CREATE TABLE if not exists files
                    (showName text, originalName text, episodName text,
                    season text, episode text, quality text, pubDate text, link text, downloaded text)
                """)
    cursor.execute(
        "CREATE TABLE if not exists show (showName text, originalName text, quality text, PRIMARY KEY(originalName))")


def updateShow(showFile):
    cursor.execute("SELECT showName, originalName, quality FROM show WHERE originalName = :originalName",
                   {"originalName": showFile.originalName})
    if (cursor.fetchone() == None):
        logging.info('Found New show %s', showFile.originalName)
        cursor.execute("INSERT INTO show(showName, originalName) VALUES (:showName, :originalName)", {
                       "showName": showFile.showName, "originalName": showFile.originalName})


def updateFile(showFile):
    cursor.execute("SELECT _rowid_ FROM files WHERE originalName=:originalName AND season=:season AND episode=:episode AND quality=:quality",
                   {"originalName": showFile.originalName,
                    "season": showFile.season,
                    "episode": showFile.episode,
                    "quality": showFile.quality})
    if (cursor.fetchone() == None):
        logging.info('Found New Episode %s S%sE%s [%s]', showFile.originalName,
                     showFile.season, showFile.episode, showFile.quality)
        cursor.execute("""INSERT INTO files(showName, originalName, episodName,season, episode, quality, pubDate, link) 
        VALUES (:showName, :originalName, :episodName, :season, :episode, :quality, :pubDate, :link)""",
                       {
                           "showName": showFile.showName,
                           "originalName": showFile.originalName,
                           "episodName": showFile.episodName,
                           "season": showFile.season,
                           "episode": showFile.episode,
                           "quality": showFile.quality,
                           "pubDate": showFile.pubDate,
                           "link": showFile.link
                       })


def downloadAll():
    cursor.execute(
        "select files._rowid_ as rowid, link, originalName, season, episode, quality from files natural join show where downloaded is null and episode != 99")
    files = cursor.fetchall()
    for f in files:
        filename = '{originalName}_S{season}E{episode}_[{quality}].torrent'.format(
            originalName=f["originalName"],
            season=f["season"],
            episode=f["episode"],
            quality=f["quality"],

        )
        logging.info('Downloading %s', filename)
        saveTorrent(f["link"], filename)
        cursor.execute("UPDATE files set downloaded = :downloaded where  _rowid_ = :rowid",
                       {"downloaded": datetime.utcnow().isoformat(), "rowid": f["rowid"]})


def main():
    txt = httpGet("http://retre.org/rssdd.xml")
    xmldoc = minidom.parseString(txt.replace(' & ',' &amp;'))
    itemlist = xmldoc.getElementsByTagName('item')
    for s in itemlist:
        sf = ShowFile(s)
        updateShow(sf)
        updateFile(sf)
    downloadAll()


if __name__ == "__main__":
    logging.basicConfig(filename='lostfilm.log', level=logging.INFO, format='%(asctime)s %(message)s')
    logging.info('Rss read')
    conn = sqlite3.connect("lostfilm.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        createTable()
        main()
    except:
        logging.error(sys.exc_info())
        raise
    finally:
        conn.commit()
        conn.close()

