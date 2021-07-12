#! /usr/bin/env python3

import requests
import urllib.request
import bs4 as bs
import re
import os
import traceback
import json


def lookForNotes(text, child):
    for c in child.children:
        if isinstance(c, bs.NavigableString):
            text.append(c.strip())
        elif not c.get("class")[0].startswith("note"):
            return lookForNotes(text, c)
    return text


#Function to access web pages
def getPage(link):
    try:
        hdrs = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 OPR/68.0.3618.125',
        'Cookie': '__cfduid=db75f4bed8ce2e9aab6d81d433df836b01565780061; G_ENABLED_IDPS=google; _s=amp-sPucjHWU-CTP7P277jiuPA; _s=amp-sPucjHWU-CTP7P277jiuPA; __atssc=google%3B1; RecentVersions=%7B%22data%22%3A%5B144%5D%2C%22meta%22%3A%7B%22144%22%3A%7B%22id%22%3A144%2C%22abbreviation%22%3A%22MBB05%22%2C%22title%22%3A%22Magandang%20Balita%20Biblia%20(2005)%22%7D%7D%2C%22syncDate%22%3A%221970-01-01T00%3A00%3A00.000Z%22%2C%22changedDate%22%3A%222020-05-11T20%3A55%3A29.551Z%22%7D; _youversion-web_session=BAh7B0kiD3Nlc3Npb25faWQGOgZFVEkiJTQxNjNlOWY4MzAzMWM5ZTNmMGZiZjA0Mzg3NWFhM2M4BjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMUtWMk02dVhSVTBjUzBkaFErNUN4N1JXTEZaR2hMVGd6UE9wWXNvbVhTSFU9BjsARg%3D%3D--97861e6a8640c6bd0b0721b8b1590b089321ca41; version=2200; last_read=EZK.2; _gid=GA1.2.498862176.1591977521; locale=en; _ga=GA1.1.amp-vBjnbbpuSzYNU85EG0ANog; __atuvc=13%7C20%2C0%7C21%2C5%7C22%2C4%7C23%2C5%7C24; __atuvs=5ee3bce18cb3c4f1000; _ga_QDGZHKSWDQ=GS1.1.1591983327.144.0.1591983650.0'}
        ###Some links contain non-ascii symbols
        splitLink = link.split('/')
        quotedStart = '/'.join(splitLink[:-1]) + '/'
        quotedEnd = urllib.parse.quote(splitLink[-1])
        page = requests.get(quotedStart + quotedEnd, headers=hdrs)
        # req = urllib.request.Request(quotedStart + quotedEnd, headers=hdrs)
        #######################################
        # page = urllib.request.urlopen(req)
        # print(page.getcode())
        print(page.status_code)
        # page = page.read()
        soupPage = bs.BeautifulSoup(page.text, features='lxml')
        # soupPage = bs.BeautifulSoup(page, features='lxml')
        return soupPage
    except:
        tb = traceback.format_exc()
        print(tb)
        if 'HTTP Error 404' in tb:
            return '404'
        else:
            print("\nTrying again...\n")
            return getPage(link)


###Download the list of languages
mainPageSoup = getPage('https://www.bible.com/languages')

#Finding parts of the page with the language list containing language codes
potentialLanguageLinks = mainPageSoup.select('td > a')
languageList = dict()

#Get language codes in the shape of 'tgl' or 'spa_es' or 'mya_zaw'
for languageLink in potentialLanguageLinks:
    #Not all links in the gathered potentialLanguageLinks contain language codes
    try:
        languageCode = re.search('(?<=\().{3}(?:_.{2,3})?(?=\)$)', languageLink.get('title')).group()
        languageList[languageLink.getText().strip()] = languageCode
    except:
        continue
###Loop through the list of languages to get links for every language
languageLinks = list()

for name, code in languageList.items():
    for languageLink in potentialLanguageLinks:
        #Not all links in the gathered potentialLanguageLinks contain languagecodes
        try:
            if code in languageLink.get('title') and name in languageLink.getText():
                if languageLink.get('href') not in languageLinks:
                    languageLinks.append(languageLink.get('href'))
        except:
            continue
###Loop through the language links to get translation lists
translations = dict()
translationPattern = re.compile('(?<=versions/)(\w+)-([\w|%]+)?')

for languageLink in languageLinks:
    languageName = {v: k for k, v in languageList.items()}[languageLink[11:]]
    print(f"Initiating {languageName}")
    #Make a directory to store bible translations for one language
    newDir = os.path.join(os.getcwd(), languageName.replace(':', '').replace('/', '-'))
    try:
        os.makedirs(newDir)
    except:
        print(f"The directory for {languageName} already exists.")
    translationCodes = dict()
    #Get to the translation list page
    translationListLink = 'http://www.bible.com/' + languageLink
    translationListSoup = getPage(translationListLink)
    #Get html parts than can contain links to translations
    for item in translationListSoup.select('a[role="button"]'):
        #Get actual translation links
        try:
            if '/versions/' in item.get('href'):
                #Check if the language is already in the dictionary to add another translation:
                codes = re.search(translationPattern, item.get('href')).group(1, 2)
                if languageLink in translations:
                    translations[languageLink][item.getText()+'_'+str(codes[1])] = item.get('href')
                else:
                    translations[languageLink] = {item.getText()+'_'+str(codes[1]):item.get('href')}
        except:
            continue
    #Access each tranlation
    for translationName, translationLink in translations[languageLink].items():
        codes = re.search(translationPattern, translationLink).group(1, 2)
        translationCodes[translationName] = codes
    for translationName, translationCode in translationCodes.items():
        print(f"Initiating {translationName}")
        #Write into a file for the particular translation
        languageName = '_'.join(languageName.split(' '))
        translationName = '_'.join(translationName.split(' '))
        fileName = os.path.join(newDir, f'{languageName}--{translationName}.json'.replace(':', '').replace('/', '-').replace('"', '').replace('|', ''))
        #Check if the file exists to skip if necessary (to resume the program when it hits an unexpected error)
        if os.path.isfile(fileName):
            continue
        with open(fileName, 'a', encoding='utf-8-sig') as f:
            link = f'http://www.bible.com/bible/{translationCode[0]}/GEN.INTRO1.{translationCode[1]}'
            chapterSoup = getPage(link)
            if chapterSoup.select_one('body').getText() == 'Not Found':
                continue
            link = chapterSoup.select_one('link[rel="canonical"]').get('href')
            while True:
                chapterSoup = getPage(link)
                # try:###delete
                spans = chapterSoup.select('span[class^="verse"]')

                #Check if there is text (e.g Introduction) without a verse number
                #if len(spans) == 0:
                    #spans = chapterSoup.select('span[class="content"]')

                #Check if the link is not broken (the first occurrence is https://www.bible.com/bible/37/S3Y.1.CEB)
                print(link) #delete
                # except:###delete

                if '"statusCode":404' in chapterSoup.getText():
                #if chapterSoup.select_one('body').getText().startswith('{"statusCode":404'):
                    if oldLink == 'http://www.bible.com/bible/37/LJE.1.CEB':
                        link = 'https://www.bible.com/bible/37/SUS.1.CEB'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/37/MAN.1.CEB':
                        #The second occurrence of empty pages: https://www.bible.com/bible/37/PS2.1.CEB,
                        #https://www.bible.com/bible/37/PS2.2.CEB, and https://www.bible.com/bible/37/PS2.3.CEB
                        link = 'https://www.bible.com/bible/37/3MA.1.CEB'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/303/LJE.1_1.CEVDCI':
                        #The third occurrence: https://www.bible.com/fr/bible/303/S3Y.1.CEVDCI
                        link = 'https://www.bible.com/bible/303/SUS.1_1.CEVDCI'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/416/LJE.1.GNBDC':
                        #The fourth occurrence
                        link = 'https://www.bible.com/bible/416/SUS.INTRO1.GNBDC'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/69/LJE.1_1.GNTD':
                        #The fifth occurrence
                        link = 'https://www.bible.com/bible/69/SUS.INTRO1.GNTD'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/546/BAR.6.KJVA':
                        #The sixth occurrence
                        link = 'https://www.bible.com/bible/546/SUS.INTRO1.KJVA'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/546/BAR.6.KJVAAE':
                        link = 'https://www.bible.com/bible/546/SUS.INTRO1.KJVAAE'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/2015/LJE.1_1.NRSV-CI':
                        link = 'https://www.bible.com/bible/2015/SUS.1_1.NRSV-CI'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/2017/LJE.1_1.RSV-CI':
                        link = 'https://www.bible.com/bible/2017/SUS.1_1.RSV-CI'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/1922/LJE.1_1.RV1895':
                        link = 'https://www.bible.com/bible/1922/SUS.1.RV1895'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/206/LJE.6.WEB':
                        link = 'https://www.bible.com/bible/206/SUS.1.WEB'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/206/MAN.1.WEB':
                        break
                    elif oldLink == 'http://www.bible.com/bible/1204/4MA.18.WEBBE':
                        link = 'https://www.bible.com/bible/1204/DAG.1.WEBBE'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/2407/LJE.1.WBMS':
                        link = 'https://www.bible.com/bible/2407/SUS.1.WBMS'
                        continue
                    elif oldLink == 'http://www.bible.com/ms/bible/377/LJE.1_1.BMDC':
                        link = 'https://www.bible.com/ms/bible/377/SUS.1_1.BMDC'
                        continue
                    elif oldLink == 'http://www.bible.com/cy/bible/221/LJE.1.BCNDA':
                        link = 'https://www.bible.com/cy/bible/221/SUS.1.BCNDA'
                        continue
                    elif oldLink.endswith('bible/2101/LJE.1_1.BWMA'):
                        link = 'https://www.bible.com/bible/2101/SUS.1.BWMA'
                        continue
                    elif oldLink.endswith('bible/178/LJE.1_1.TLAI'):
                        link = 'https://www.bible.com/bible/178/SUS.1_1.TLAI'
                        continue
                    elif oldLink.endswith('bible/2197/LJE.1.MBBTAG12'):
                        link = 'https://www.bible.com/bible/2197/SUS.1.MBBTAG12'
                        continue
                    elif oldLink.endswith('bible/144/LJE.1.MBB05'):
                        link = 'https://www.bible.com/bible/144/SUS.1.MBB05'
                        continue
                    elif oldLink.endswith('bible/393/LJE.1.BHND'):
                        link = 'https://www.bible.com/bible/393/SUS.1.BHND'
                        continue
                    elif oldLink.endswith('bible/1817/LJE.1.SUVDC'):
                        link = 'https://www.bible.com/bible/1817/SUS.1.SUVDC'
                        continue
                    elif oldLink == 'http://www.bible.com/sw/bible/1817/LJE.1.SRUVDC':
                        link = 'http://www.bible.com/sw/bible/1817/SUS.1.SRUVDC'
                        continue
                    elif oldLink.endswith('bible/228/LJE.1.BPT09DC'):
                        link = 'https://www.bible.com/bible/228/SUS.1.BPT09DC'
                        continue
                    elif oldLink.endswith('bible/464/LJE.1_1.SEBDT'):
                        link = 'https://www.bible.com/bible/464/SUS.1_1.SEBDT'
                        continue
                    elif oldLink.endswith('bible/2308/LJE.1.KKDEU'):
                        link = 'https://www.bible.com/bible/2308/SUS.1.KKDEU'
                        continue
                    elif oldLink.endswith('bible/2308/MAN.1.KKDEU'):
                        link = 'https://www.bible.com/bible/2308/4MA.1.KKDEU'
                        continue
                    elif oldLink.endswith('bible/901/BEL.1.%D0%9D%D0%9F'):
                        link = 'http://www.bible.com/bible/901/MAN.1.НП'
                        continue
                    elif oldLink.endswith('bible/901/MAN.1.НП'):
                        link = 'https://www.bible.com/bible/901/MAT.1.НП'
                        continue
                    elif oldLink.endswith('bible/1819/BEL.1.%E6%96%B0%E5%85%B1%E5%90%8C%E8%A8%B3'):
                        link = 'http://www.bible.com/bible/1819/1ES.1.%E6%96%B0%E5%85%B1%E5%90%8C%E8%A8%B3'
                        continue
                    elif oldLink.endswith('bible/1889/LJE.1_1.%E6%AC%A1%E7%B6%93'):
                        link = 'https://www.bible.com/bible/1889/SUS.1_1.%E6%AC%A1%E7%B6%93'
                        continue
                    elif oldLink.endswith('bible/592/BAR.6.KCB'):
                        link = 'http://www.bible.com/bible/592/SUS.1_1.KCB'
                        continue
                    elif oldLink.endswith('bible/2188/LJE.1_1.MBBCEB99'):
                        link = 'http://www.bible.com/bible/2188/SUS.1.MBBCEB99'
                        continue
                    elif oldLink.endswith('bible/890/LJE.1.BPV'):
                        link = 'https://www.bible.com/bible/890/SUS.1.BPV'
                        continue
                    elif oldLink.endswith('bible/1754/LJE.1.AKKDC08'):
                        link = 'http://www.bible.com/bible/1754/SUS.1_1.AKKDC08'
                        continue
                    elif oldLink.endswith('/bible/905/LJE.1.FBDC'):
                        link = 'http://www.bible.com/bible/905/SUS.1_1.FBDC'
                        continue
                    elif oldLink.endswith('bible/1807/BAR.6.MACGAP'):
                        link = 'http://www.bible.com/bible/1807/SUS.1.MACGAP'
                        continue
                    elif oldLink.endswith('bible/2190/LJE.1.MBBHIL12'):
                        link = 'http://www.bible.com/bible/2190/SUS.1.MBBHIL12'
                        continue
                    elif oldLink.endswith('bible/171/LJE.1.BK'):
                        link = 'http://www.bible.com/bible/171/SUS.INTRO1.BK'
                        continue
                    elif oldLink.endswith('bible/1079/BAR.6.ABK'):
                        link = 'http://www.bible.com/bible/1079/SUS.1.ABK'
                        continue
                    elif oldLink.endswith('bible/1202/BAR.6.GIKDC'):
                        link = 'http://www.bible.com/bible/1202/SUS.INTRO1.GIKDC'
                        continue
                    elif oldLink.endswith('bible/387/LJE.1_1.BIRD'):
                        link = 'http://www.bible.com/bible/387/SUS.1_1.BIRD'
                        continue
                    elif oldLink.endswith('bible/552/LJE.1.BBBLI'):
                        link = 'http://www.bible.com/bible/552/SUS.INTRO1.BBBLI'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/1393/DAN.12.BKPDCG':
                        link = 'http://www.bible.com/bible/1393/SUS.1_1.BKPDCG'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/1957/LJE.1.HAT98':
                        link = 'http://www.bible.com/bible/1957/SUS.1_1.HAT98'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/552/LJE.1.BB03':
                        link = 'http://www.bible.com/bible/552/SUS.INTRO1.BB03'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/825/LJE.1_1.BYK09':
                        link = 'http://www.bible.com/bible/825/SUS.1.BYK09'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/99/LJE.1.TMT':
                        link = 'http://www.bible.com/bible/99/SUS.1_1.TMT'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/868/LJE.1.GB11DC':
                        link = 'https://www.bible.com/bible/868/SUS.1.GB11DC'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/2235/LJE.1_1.BASSARDC':
                        link = 'https://www.bible.com/bible/2235/SUS.1_1.BASSARDC'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/1141/LJE.1.PMPV':
                        link = 'http://www.bible.com/bible/1141/SUS.1.PMPV'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/2194/LJE.1.MBBPAN83':
                        link = 'http://www.bible.com/bible/2194/SUS.1.MBBPAN83'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/1166/LJE.1.PNPV':
                        link = 'http://www.bible.com/bible/1166/SUS.1.PNPV'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/614/LJE.1.SIDC':
                        link = 'https://www.bible.com/bible/614/SUS.1.SIDC'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/1515/LJE.1_1.KBDC':
                        link = 'http://www.bible.com/bible/1515/SUS.INTRO1.KBDC'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/445/LJE.1_1.BSDC':
                        link = 'http://www.bible.com/bible/445/SUS.1_1.BSDC'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/1053/LJE.1.BSK':
                        link = 'http://www.bible.com/bible/1053/SUS.INTRO1.BSK'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/2156/LJE.1.SHKDCB':
                        link = 'http://www.bible.com/bible/2156/SUS.INTRO1.SHKDCB'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/2415/BEL.1.DAL1584':
                        link = 'http://www.bible.com/bible/2415/MAN.1.DAL1584'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/1256/SUS.1.SOG':
                        link = 'http://www.bible.com/bible/1256/BEL.INTRO1.SOG'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/550/LJE.1.BEGDC':
                        link = 'http://www.bible.com/bible/550/SUS.INTRO1.BEGDC'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/382/LJE.1.TZE97':
                        link = 'http://www.bible.com/bible/382/SUS.1_1.TZE97'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/2353/BAR.6.DQDC':
                        link = 'http://www.bible.com/bible/2353/SUS.1_1.DQDC'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/2249/BAR.6.QCHSB':
                        link = 'http://www.bible.com/bible/2249/SUS.1_1.QCHSB'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/675/BAR.5.FNVDC12':
                        link = 'http://www.bible.com/bible/675/SUS.INTRO1.FNVDC12'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/2198/LJE.1.MBBSAM':
                        link = 'http://www.bible.com/bible/2198/SUS.1.MBBSAM'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/418/LJE.1.TSO89':
                        link = 'http://www.bible.com/bible/418/SUS.1.TSO89'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/2248/BAR.6.SCLBD':
                        link = 'http://www.bible.com/bible/2248/1MA.INTRO1.SCLBD'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/2202/MAN.1.GEO02':
                        link = 'http://www.bible.com/bible/2202/3MA.1.GEO02'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/2368/MAN.1.%E1%83%A5%E1%83%91%E1%83%A1%E1%83%95':
                        link = 'http://www.bible.com/bible/2368/3MA.1.ქბსვ'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/384/LJE.1.DIEMDC':
                        link = 'http://www.bible.com/bible/384/SUS.1_1.DIEMDC'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/2535/1JN.3.NCG':
                        break
                    elif oldLink == 'http://www.bible.com/bible/1202/REV.22.GKN':
                        link = 'https://www.bible.com/bible/1202/SUS.INTRO1.GKN'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/2676/LJE.1_1.BILKDC13':
                        link = 'https://www.bible.com/bible/2676/SUS.INTRO1.BILKDC13'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/2687/LJE.1_1.MAYADC':
                        link = 'https://www.bible.com/bible/2687/SUS.1_1.MAYADC'
                        continue
                    elif oldLink == "http://www.bible.com/bible/825/LJE.1_1.LOZI09":
                        link = 'https://www.bible.com/bible/825/SUS.1.LOZI09'
                        continue
                    elif oldLink == "http://www.bible.com/bible/1365/PSA.150.MP1650":
                        break
                    elif oldLink == 'http://www.bible.com/bible/2804/LJE.1.LBWD03':
                        link = 'http://www.bible.com/bible/2804/SUS.INTRO1.LBWD03'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/2803/LJE.1.NIB2008':
                        link = 'https://www.bible.com/bible/2803/SUS.INTRO1.NIB2008'
                        continue
                    elif oldLink == 'http://www.bible.com/bible/2806/LJE.1.BRR2008':
                        link = 'https://www.bible.com/bible/2806/SUS.INTRO1.BRR2008'
                        continue
                    else:
                        raise

                print(f"    Initiating {chapterSoup.select_one('title').getText().split(',')[0]}")

                #Create a list with the chapter content
                chapterContent = []

                #Write the book title and chapter number to the file
                splitLink = link.split('/')[-1]
                codes = re.search('(\w+\.\w+)(?=\.)', splitLink).group()
                #Extract the book code and chapter number from the "codes"
                bookCode = codes.split('.')[0]
                chapterNo = codes.split('.')[1]
                #Extract the book title
                bookTitle = ' '.join(chapterSoup.select_one('title').getText().split(',')[0].split()[:-1])

                #f.write('_'.join(chapterSoup.select_one('title').getText().split(',')[0].upper().split()) + ' (' + codes + ')\n')

                #Write verses to the file
                for span in spans:
                    text = []
                    verseNo = False
                    if span.getText() == ' ' or span.parent.name == 'td' or span.parent.name == 'th':
                        continue
                    for child in span.children:
                        #Some children of spans are just strings (e.g. '; ')
                        try:
                            if child.strip() == ';':
                                text.append(child.strip())
                                continue
                        except:
                            #Extract the verse number
                            if child.get("class")[0] == "label":
                                verse = child.getText()
                                verseNo = True
                            #Extract the verse text
                            elif not child.get("class")[0].startswith("note") and child.getText() != ' ':
                                if verseNo == False and len(chapterContent) == 0:
                                    verse = '1'
                                text = lookForNotes(text, child)
                    #Join the text list
                    text = ' '.join(text)
                    #Some verses are empty (English ASV ROM.16.24)
                    if text == '':
                        continue
                    #Append the verse data to the chapter content list. Two cases: verse lines without verse numbers and with them.
                    if len(chapterContent) > 0 and verse == chapterContent[-1][-2]:
                        chapterContent[-1][-1] += (' ' + text)
                    else:
                        chapterContent.append([bookTitle, bookCode, chapterNo, verse, text])

                #Convert the chapter content string into json
                chapterContent = json.dumps(chapterContent, indent=2)
                #Write the chapter content into a file
                f.write(str(chapterContent))

                #Get the next page link or break if it's the end of the book
                leftToRight = chapterSoup.select_one('a[data-vars-event-action="Next"]')
                rightToLeft = chapterSoup.find_all('div', class_='prev-arrow')
                nextArrow = chapterSoup.find_all('div', class_='next-arrow')
                if leftToRight != None:
                    nextLinkHtml = leftToRight
                ###Belarusian translations are left to right but use the same html outline
                elif '/be/' in link and nextArrow != 0 and nextArrow[0].findChildren('a', recursive=False)[0] != 0:
                    nextLinkHtml = nextArrow[0].findChildren('a', recursive=False)[0]
                elif len(rightToLeft) != 0 and len(rightToLeft[0].findChildren('a', recursive=False)) != 0:
                    nextLinkHtml = rightToLeft[0].findChildren('a', recursive=False)[0]
                else:
                    break
                oldLink = link
                link = 'http://www.bible.com' + nextLinkHtml.get('href').replace(' ', '%20')
                #This Ukrainian translation has wrong links on some pages, leading to the same page
                if oldLink.endswith('bible/1755/1SA.21.%D0%A3%D0%A2%D0%A2') and link.endswith('bible/1755/1SA.21.%D0%A3%D0%A2%D0%A2'):
                    link = 'http://www.bible.com/uk/bible/1755/1SA.22.%D0%A3%D0%A2%D0%A2'
                elif oldLink.endswith('bible/1755/ESG.1.%D0%A3%D0%A2%D0%A2') and link.endswith('bible/1755/ESG.1.%D0%A3%D0%A2%D0%A2'):
                    link = 'http://www.bible.com/uk/bible/1755/ESG.2.%D0%A3%D0%A2%D0%A2'
                elif oldLink.endswith('bible/1755/ESG.3.%D0%A3%D0%A2%D0%A2') and link.endswith('bible/1755/ESG.3.%D0%A3%D0%A2%D0%A2'):
                    link = 'http://www.bible.com/uk/bible/1755/ESG.4.%D0%A3%D0%A2%D0%A2'
                elif oldLink.endswith('bible/1755/ESG.4.%D0%A3%D0%A2%D0%A2') and link.endswith('bible/1755/ESG.4.%D0%A3%D0%A2%D0%A2'):
                    link = 'http://www.bible.com/uk/bible/1755/ESG.5.%D0%A3%D0%A2%D0%A2'
                elif oldLink.endswith('bible/1755/ESG.5.%D0%A3%D0%A2%D0%A2') and link.endswith('bible/1755/ESG.5.%D0%A3%D0%A2%D0%A2'):
                    link = 'http://www.bible.com/uk/bible/1755/ESG.6.%D0%A3%D0%A2%D0%A2'
                elif oldLink.endswith('bible/1755/ESG.8.%D0%A3%D0%A2%D0%A2') and link.endswith('bible/1755/ESG.8.%D0%A3%D0%A2%D0%A2'):
                    link = 'http://www.bible.com/uk/bible/1755/ESG.9.%D0%A3%D0%A2%D0%A2'
                elif oldLink.endswith('bible/1755/ESG.10.%D0%A3%D0%A2%D0%A2') and link.endswith('bible/1755/ESG.10.%D0%A3%D0%A2%D0%A2'):
                    link = 'http://www.bible.com/uk/bible/1755/JOB.1.%D0%A3%D0%A2%D0%A2'
                elif oldLink.endswith('bible/1755/SIR.1.%D0%A3%D0%A2%D0%A2') and link.endswith('bible/1755/SIR.1.%D0%A3%D0%A2%D0%A2'):
                    link = 'http://www.bible.com/uk/bible/1755/SIR.2.%D0%A3%D0%A2%D0%A2'
                elif oldLink.endswith('bible/1755/SIR.5.%D0%A3%D0%A2%D0%A2') and link.endswith('bible/1755/SIR.5.%D0%A3%D0%A2%D0%A2'):
                    link = 'http://www.bible.com/uk/bible/1755/SIR.6.%D0%A3%D0%A2%D0%A2'
                elif oldLink.endswith('bible/1755/ISA.63.%D0%A3%D0%A2%D0%A2') and link.endswith('bible/1755/ISA.63.%D0%A3%D0%A2%D0%A2'):
                    link = 'http://www.bible.com/uk/bible/1755/ISA.64.%D0%A3%D0%A2%D0%A2'
                elif oldLink.endswith('bible/2525/2KI.11.RAMB') and link.endswith('bible/2525/2KI.11.RAMB'):
                    link = 'http://www.bible.com/bible/2525/2KI.18.RAMB'


                # try:
                #     nextLinkHtml = chapterSoup.select_one('a[data-vars-event-action="Next"]')
                #     oldLink = link
                #     link = 'http://www.bible.com' + nextLinkHtml.get('href')
                # except:
                #     break

# TODO: Remove undersocring before and after dashes in language names in filenames
