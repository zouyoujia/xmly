#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2016/10/10
# Created by 独自等待
# 博客 http://www.waitalone.cn/
import requests
import urllib
import json
import sys
import re
import os

reload(sys)
sys.setdefaultencoding('utf-8')


class ximalaya:
    def __init__(self, url):
        self.url = url  # 传入的专辑URL,类似http://www.ximalaya.com/16960840/album/294567
        self.urlheader = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': self.url,
            'Cookie': '_ga=GA1.2.1628478964.1476015684; _gat=1',
        }

    def getpage(self):
        '获取分页数方法'
        pagelist = []  # 保存分页数
        try:
            response = requests.get(self.url, headers=self.urlheader).text.encode('utf-8')
        except Exception, msg:
            print u'网页打开出错,请检查!', msg
        else:
            reg_list = [
                re.compile(r"class=\"pagingBar_wrapper\" url=\"(.*?)\""),
                re.compile(r"<a href='(/\d+/album/\d+\?page=\d+)' data-page='\d+'")
            ]
            for reg in reg_list:
                pagelist.extend(reg.findall(response))
        if pagelist:
            return ['http://www.ximalaya.com' + x for x in pagelist[:-1]]
        else:
            return [self.url]

    def analyze(self, trackid):
        '解析真实mp3地址'
        trackurl = 'http://www.ximalaya.com/tracks/%s.json' % trackid
        try:
            response = requests.get(trackurl, headers=self.urlheader).text
        except Exception:
            print trackurl + '解析失败!'
            with open('analyze_false.txt', 'ab+') as false_analyze:
                false_analyze.write(trackurl + '\n')
        else:
            jsonobj = json.loads(response)
            title = jsonobj['title']
            mp3 = jsonobj['play_path']
            filename = title.strip() + '.mp3'
            print filename, mp3
            urllib.urlretrieve(mp3, filename)
            # 乱码问题比较难以解决。
            with open('mp3.txt', 'ab+') as mp3file:
                mp3file.write('%s | %s\n' % (filename, mp3))

    def todownlist(self):
        '生成待下载的文件列表'
        if 'sound' in self.url:  # 解析单条mp3
            trackid = self.url[self.url.rfind('/') + 1:]
            self.analyze(trackid)
        else:
            for purl in self.getpage():  # 解析每个专辑页面中的所有mp3地址
                try:
                    response = requests.get(purl, headers=self.urlheader).text
                except Exception, msg:
                    print u'分页请求失败!', msg
                else:
                    ids_reg = re.compile(r'sound_ids="(.+?)"')
                    ids_res = ids_reg.findall(response)
                    idslist = [j for j in ids_res[0].split(',')]
                    for trackid in idslist:
                        self.analyze(trackid)


if __name__ == '__main__':
    print '+' + '-' * 50 + '+'
    print u'\t   Python 喜马拉雅mp3批量下载工具'
    print u'\t   Blog：http://www.waitalone.cn/'
    print u'\t\t Code BY： 独自等待'
    print u'\t\t Time：2016-07-29'
    print '+' + '-' * 50 + '+'
    if len(sys.argv) != 2:
        print u'用法: ' + os.path.basename(sys.argv[0]) + u' 你要下载的专辑mp3主页地址,地址如下：'
        print u'实例: ' + os.path.basename(sys.argv[0]) + ' http://www.ximalaya.com/12495477/album/269179'
        sys.exit()
    ximalaya = ximalaya(sys.argv[1])  # 实例化类
    ximalaya.todownlist()
