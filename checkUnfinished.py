import re

codeRE = re.compile('(?<=--)\S+_(\(\S+\))(?=_\S+\.json)')
chapterRE = re.compile('(\w{3})\",\s{5}\"(\S+)(?=\",:)')

with open('filesCutShort.txt', 'r') as f:
    files = f.readlines()

trans = {}
error = []


for file in files:

    code = re.search(codeRE, file).group(1).replace('_', ' ')

    if file.strip().endswith('ERROR'):
        error.append(code)

    else:
        chapterCodes = re.search(chapterRE, file)
        chapter = (chapterCodes.group(1), chapterCodes.group(2))
        trans[code] = chapter



import requests
import urllib.request
import bs4 as bs
import os
import traceback
import json

#Function to access web pages
def getPage(link):
    try:
        hdrs = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 OPR/68.0.3618.125',
        'Cookie': '__cfduid=db75f4bed8ce2e9aab6d81d433df836b01565780061; G_ENABLED_IDPS=google; _s=amp-sPucjHWU-CTP7P277jiuPA; _s=amp-sPucjHWU-CTP7P277jiuPA; __atssc=google%3B1; RecentVersions=%7B%22data%22%3A%5B144%5D%2C%22meta%22%3A%7B%22144%22%3A%7B%22id%22%3A144%2C%22abbreviation%22%3A%22MBB05%22%2C%22title%22%3A%22Magandang%20Balita%20Biblia%20(2005)%22%7D%7D%2C%22syncDate%22%3A%221970-01-01T00%3A00%3A00.000Z%22%2C%22changedDate%22%3A%222020-05-11T20%3A55%3A29.551Z%22%7D; _youversion-web_session=BAh7B0kiD3Nlc3Npb25faWQGOgZFVEkiJTQxNjNlOWY4MzAzMWM5ZTNmMGZiZjA0Mzg3NWFhM2M4BjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMUtWMk02dVhSVTBjUzBkaFErNUN4N1JXTEZaR2hMVGd6UE9wWXNvbVhTSFU9BjsARg%3D%3D--97861e6a8640c6bd0b0721b8b1590b089321ca41; version=2200; last_read=EZK.2; _gid=GA1.2.498862176.1591977521; locale=en; _ga=GA1.1.amp-vBjnbbpuSzYNU85EG0ANog; __atuvc=13%7C20%2C0%7C21%2C5%7C22%2C4%7C23%2C5%7C24; __atuvs=5ee3bce18cb3c4f1000; _ga_QDGZHKSWDQ=GS1.1.1591983327.144.0.1591983650.0'}
        #page = requests.get(link, headers=hdrs)
        req = urllib.request.Request(link, headers=hdrs)
        page = urllib.request.urlopen(req)
        print(page.getcode())
        page = page.read()
        #soupPage = bs.BeautifulSoup(page.text, features='lxml')
        soupPage = bs.BeautifulSoup(page, features='lxml')
        return soupPage
    except:
        tb = traceback.format_exc()
        print(tb)
        if 'HTTP Error 404' in tb:
            return '404'
        else:
            print("\nTrying again...\n")
            return getPage(link)


mainPageSoup = getPage('https://www.bible.com/versions')

links = {}

transLinks = mainPageSoup.find_all("a", class_="db pb2 lh-copy yv-green link")
transLinksDict = {}

for transLink in transLinks:
    transLinksDict[transLink.get_text()] = transLink.get('href')

for tran in trans.keys():
    for text, link in transLinksDict.items():
        if tran.lower() in text.lower():
            links[tran] = link
            transLinksDict.pop(text)
            break

good = []
bad = []

for code, link in links.items():
    pageSoup = getPage('https://www.bible.com' + link)
    trueLink = pageSoup.find('a', class_="db pb3 link yv-green lh-copy").get('href')
    linkEnd = f'{trans[code][0]}.{trans[code][1]}.{trueLink.split(".")[-1]}'
    linkStart = '/'.join(trueLink.split('/')[1:3])
    pageSoup = getPage('https://www.bible.com/' + linkStart + '/' + linkEnd)
    print('https://www.bible.com/' + linkStart + '/' + linkEnd)
    if pageSoup.select_one('a[data-vars-event-action="Next"]'):
        print(next)
        bad.append(code)
        print('bad')
    else:
        good.append(code)
        print('good')

with open('results.txt', 'w') as f:
    f.write('ERROR\n')
    for i in error:
        f.write('    ' + i + '\n')
    f.write('\n')
    f.write('GOOD\n')
    for i in good:
        f.write('    ' + i + '\n')
    f.write('\n')
    f.write('BAD\n')
    for i in bad:
        f.write('    ' + i + '\n')
