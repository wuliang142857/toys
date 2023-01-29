#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import urllib.parse
from argparse import ArgumentParser
import requests
from urllib.parse import urlparse
from http.cookiejar import MozillaCookieJar
from pathlib import Path
import base64
import json
import m3u8
import re
from Crypto.Cipher import AES
import os
import shutil
import ffmpeg

HEADERS = {
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Mobile Safari/537.36"
}

class VideoElement:
    def __init__(self, m3u8Url = None, tsBase = None, param=None):
        self.m3u8Url = m3u8Url
        self.tsBase = tsBase
        self.param = param

def getVideoDetail(videoUrl, cookieJar):
    parser = urlparse(videoUrl)
    videoId = parser.path.split("/")[-1]
    targetUrl = f"{parser.scheme}://{parser.hostname}/xe.course.business.video.detail_info.get/2.0.0"
    requestData = {
        'bizData[resource_id]': videoId,
        'bizData[product_id]': None,
        'bizData[opr_sys]': "MacIntel"
    }
    response = requests.post(targetUrl, headers=HEADERS, data=requestData, cookies=cookieJar)
    responseJson = response.json()
    videoUrlsString = responseJson["data"]["video_urls"]
    videoUrlsString = videoUrlsString.replace("__ba", "").replace("@", "1").replace("#", "2").replace("$", "3").replace("%", "4")
    videoElements = []
    for item in json.loads(base64.b64decode(videoUrlsString)):
        videoElement = VideoElement(m3u8Url=item["url"], tsBase=f"{item['ext']['host']}/{item['ext']['path']}", param=item['ext']['param'])
        videoElements.append(videoElement)
    return videoElements

def parseM3U8(m3u8Url):
    return m3u8.load(m3u8Url)
    
def getDecryptKey(keyUrl, cookieJar, userId):
    response = requests.get(keyUrl, headers=HEADERS, cookies=cookieJar)
    key = response.content
    # 基于用户userid解密（第二次解密）
    userIdBytes = bytes(userId.encode(encoding='utf-8'))
    resultList = []
    for index in range(0, len(key)):
        resultList.append(
            key[index] ^ userIdBytes[index])
    return bytes(resultList)

def getUserId(videoUrl, cookieJar):
    response = requests.get(videoUrl, headers=HEADERS, cookies=cookieJar)
    pattern = re.compile("window.USERID\s*=\s*\'(.*?)\';")
    return pattern.search(response.text).groups()[0]

def downloadAndDecryptTS(tsUrl, decryptKey, index, total, tmpDir):
    print(f"{index + 1}/{total} {tsUrl}")
    response = requests.get(tsUrl, headers=HEADERS)
    cryptor = AES.new(decryptKey, AES.MODE_CBC, decryptKey)
    descryptedVideo = cryptor.decrypt(response.content)
    tsFilename = os.path.join(tmpDir, str(index) + ".ts")
    fout = open(tsFilename, "wb")
    fout.write(descryptedVideo)
    fout.close()
    return tsFilename
    
def toH5Url(videoUrl, cookieJar):
    response = requests.get(videoUrl, headers=HEADERS, cookies=cookieJar)
    pattern = re.compile("window.APPID\s*=\s*\'(.*?)\';")
    appId = pattern.search(response.text).groups()[0]
    parser = urlparse(videoUrl)
    videoId = parser.path.split("/")[-1]
    return f"{parser.scheme}://{appId}.h5.xiaoeknow.com/p/course/video/{videoId}"

def getTitleAndPublishDate(videoUrl, cookieJar):
    parser = urlparse(videoUrl)
    videoId = parser.path.split("/")[-1]
    targetUrl = f"{parser.scheme}://{parser.hostname}/xe.course.business.core.info.get/2.0.0"
    requestData = {
        'bizData[resource_id]': videoId,
    }
    response = requests.post(targetUrl, headers=HEADERS, data=requestData, cookies=cookieJar)
    responseJson = response.json()
    return (responseJson["data"]["resource_name"], responseJson["data"]["sale_at"])
    
def main():
    parser = ArgumentParser(prog="xiaoeknow-downloader", description="下载小鹅通视频")
    parser.add_argument("--url", required=True, type=str, dest="url", help="视频地址")
    parser.add_argument("--cookies", required=True, type=str, dest="cookiesFile", help="cookies")
    parser.add_argument("--output-dir", required=True, type=str, dest="outputDir", help="输出目录")
    arguments = parser.parse_args()
    
    cookieJar = MozillaCookieJar(Path(arguments.cookiesFile))
    cookieJar.load()
    videoUrl = toH5Url(arguments.url, cookieJar=cookieJar)
    outputDir = arguments.outputDir
    
    title, publishDate = getTitleAndPublishDate(videoUrl, cookieJar)
    outputVideoFileName = f"{title}.{publishDate}"
    userId = getUserId(videoUrl, cookieJar)
    videoElements = getVideoDetail(videoUrl, cookieJar)

    index = 0
    tsFiles = []
    tmpDir = os.path.join(outputDir, outputVideoFileName)
    if os.path.exists(tmpDir):
        shutil.rmtree(tmpDir)
    os.makedirs(tmpDir, 0o755)
    
    for videoElement in videoElements:
        playlist = parseM3U8(videoElement.m3u8Url)
        keyUrl = f"{playlist.segments[0].key.uri}&uid={urllib.parse.quote(userId)}"
        descryptKey = getDecryptKey(keyUrl, cookieJar, userId)        
        for segment in playlist.segments:
            tsFilename = segment.absolute_uri.replace(segment.base_uri, "")
            tsUrl = f"{videoElement.tsBase}/{tsFilename}&{videoElement.param}"
            tsFile = downloadAndDecryptTS(tsUrl, descryptKey, index, len(playlist.segments), tmpDir)
            tsFiles.append(tsFile)
            index += 1
            
    outputFile = os.path.join(outputDir, outputVideoFileName + ".mp4")
    concatFile = os.path.join(outputDir, outputVideoFileName + ".list")
    with open(concatFile, "w") as fp:
        lines = [f"file '{line}'" for line in tsFiles]  
        fp.write(os.linesep.join(lines))
        fp.close()
    if os.path.exists(outputFile):
        os.unlink(outputFile)
    ffmpeg.input(concatFile, f="concat", safe=0).output(outputFile, c="copy").run()

    os.unlink(concatFile)
    shutil.rmtree(tmpDir)
    
if __name__ == '__main__':
    main()
