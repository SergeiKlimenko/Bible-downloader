#! /usr/bin/env python3

import requests
import bs4 as bs
import re
import os
import traceback

#Function to access web pages
def getPage(link):
    try:
        page = requests.get(link)
    except:
        tb = traceback.format_exc()
        print(tb)
        print("\nTrying again...\n")
        return getPage(link)
    soupPage = bs.BeautifulSoup(page.text, features='lxml')
    return soupPage

###Download the list of languages
mainPageSoup = getPage('http://www.bible.com/languages')
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
    print("Initiating {}".format(languageName))
    #Make a directory to store bible translations for one language
    newDir = os.path.join(os.getcwd(), languageName.replace(':', ''))
    try:
        os.makedirs(newDir)
    except:
        print("The directory for {} already exists.".format(languageName))
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
        print("Initiating {}".format(translationName))
        #Write into a file for the particular translation
        languageName = '_'.join(languageName.split(' '))
        translationName = '_'.join(translationName.split(' '))
        fileName = os.path.join(newDir, '{}--{}.txt'.format(languageName, translationName).replace(':', '').replace('/', '-').replace('"', ''))
        #Check if the file exists to skip if necessary (to resume the program when it hits an unexpected error)
        if os.path.isfile(fileName):
            continue
        with open(fileName, 'a', encoding='utf-8-sig') as f:
            link = 'http://www.bible.com/bible/{}/GEN.INTRO1.{}'.format(translationCode[0], translationCode[1])
            chapterSoup = getPage(link)
            link = chapterSoup.select_one('link[rel="canonical"]').get('href')
            while True:
                chapterSoup = getPage(link)
                spans = chapterSoup.select('span[class^="verse"]')
                #Check if there is text (e.g Introduction) without a verse number
                if len(spans) == 0:
                    spans = chapterSoup.select('span[class="content"]')
                #Check if the link is not broken (the first occurrence is https://www.bible.com/bible/37/S3Y.1.CEB)
                print(link) #delete
                try:
                    print("    Initiating {}".format(chapterSoup.select_one('title').getText().split(',')[0]))
                except:
                    if chapterSoup.select_one('body').getText().startswith('{"statusCode":404'):                     
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
                        elif oldLink == 'http://www.bible.com/bible/377/LJE.1_1.BMDC':
                            link = 'https://www.bible.com/bible/377/SUS.1_1.BMDC'
                            continue
                        elif oldLink == 'http://www.bible.com/bible/221/LJE.1.BCNDA':
                            link = 'https://www.bible.com/bible/221/SUS.1.BCNDA'
                            continue
                        elif oldLink == 'http://www.bible.com/bible/2101/LJE.1_1.BWMA':
                            link = 'https://www.bible.com/bible/2101/SUS.1.BWMA'
                            continue
                        elif oldLink == 'http://www.bible.com/bible/178/LJE.1_1.TLAI':
                            link = 'https://www.bible.com/bible/178/SUS.1_1.TLAI'
                            continue
                        elif oldLink == 'http://www.bible.com/bible/2197/LJE.1.MBBTAG12':
                            link = 'https://www.bible.com/bible/2197/SUS.1.MBBTAG12'
                            continue
                        elif oldLink == 'http://www.bible.com/bible/144/LJE.1.MBB05':
                            link = 'https://www.bible.com/bible/144/SUS.1.MBB05'
                            continue
                        elif oldLink == 'http://www.bible.com/bible/393/LJE.1.BHND':
                            link = 'https://www.bible.com/bible/393/SUS.1.BHND'
                            continue
                        elif oldLink == 'http://www.bible.com/bible/1817/LJE.1.SUVDC':
                            link = 'https://www.bible.com/bible/1817/SUS.1.SUVDC'
                            continue
                        elif oldLink == 'http://www.bible.com/bible/228/LJE.1.BPT09DC':
                            link = 'https://www.bible.com/bible/228/SUS.1.BPT09DC'
                            continue
                        elif oldLink == 'http://www.bible.com/bible/464/LJE.1_1.SEBDT':
                            link = 'https://www.bible.com/bible/464/SUS.1_1.SEBDT'
                            continue
                        elif oldLink == 'http://www.bible.com/bible/2308/LJE.1.KKDEU':
                            link = 'https://www.bible.com/bible/2308/SUS.1.KKDEU'
                            continue
                        elif oldLink == 'http://www.bible.com/bible/2308/MAN.1.KKDEU':
                            link = 'https://www.bible.com/bible/2308/4MA.1.KKDEU'
                            continue
                        elif oldLink == 'http://www.bible.com/bible/901/BEL.1.%D0%9D%D0%9F':
                            link = 'http://www.bible.com/bible/901/MAN.1.НП'
                            continue
                        elif oldLink == 'http://www.bible.com/bible/901/MAN.1.НП':
                            link = 'https://www.bible.com/bible/901/MAT.1.НП'
                            continue
                        elif oldLink == 'http://www.bible.com/bible/1819/BEL.1.%E6%96%B0%E5%85%B1%E5%90%8C%E8%A8%B3':
                            link = 'http://www.bible.com/bible/1819/1ES.1.新共同訳'
                            continue
                        elif oldLink == 'http://www.bible.com/bible/1889/LJE.1_1.%E6%AC%A1%E7%B6%93':
                            link = 'https://www.bible.com/bible/1889/SUS.1_1.次經'
                            continue
                        elif oldLink == 'http://www.bible.com/bible/592/BAR.6.KCB':
                            link = 'http://www.bible.com/bible/592/SUS.1_1.KCB'
                            continue
                        elif oldLink == 'http://www.bible.com/bible/2188/LJE.1_1.MBBCEB99':
                            link = 'http://www.bible.com/bible/2188/SUS.1.MBBCEB99'
                            continue
                        elif oldLink == 'http://www.bible.com/bible/890/LJE.1.BPV':
                            link = 'https://www.bible.com/bible/890/SUS.1.BPV'
                            continue
                        elif oldLink == 'http://www.bible.com/bible/1754/LJE.1.AKKDC08':
                            link = 'http://www.bible.com/bible/1754/SUS.1_1.AKKDC08'
                            continue
                        elif oldLink == 'http://www.bible.com/bible/905/LJE.1.FBDC':
                            link = 'http://www.bible.com/bible/905/SUS.1_1.FBDC'
                            continue
                        elif oldLink == 'http://www.bible.com/bible/1807/BAR.6.MACGAP':
                            link = 'http://www.bible.com/bible/1807/SUS.1.MACGAP'
                            continue
                        elif oldLink == 'http://www.bible.com/bible/2190/LJE.1.MBBHIL12':
                            link = 'http://www.bible.com/bible/2190/SUS.1.MBBHIL12'
                            continue
                        elif oldLink == 'http://www.bible.com/bible/171/LJE.1.BK':
                            link = 'http://www.bible.com/bible/171/SUS.INTRO1.BK'
                            continue
                        elif oldLink == 'http://www.bible.com/bible/1079/BAR.6.ABK':
                            link = 'http://www.bible.com/bible/1079/SUS.1.ABK'
                            continue
                        elif oldLink == 'http://www.bible.com/bible/1202/BAR.6.GIKDC':
                            link = 'http://www.bible.com/bible/1202/SUS.INTRO1.GIKDC'
                            continue
                        elif oldLink == 'http://www.bible.com/bible/387/LJE.1_1.BIRD':
                            link = 'http://www.bible.com/bible/387/SUS.1_1.BIRD'
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
                        else:
                            raise
                #Write the book title and chapter number to the file
                splitLink = link.split('/')[-1]
                codes = re.search('(\w+\.\w+)(?=\.)', splitLink).group()
                
                f.write('_'.join(chapterSoup.select_one('title').getText().split(',')[0].upper().split()) + ' (' + codes + ')\n')
                #Write verses to the file
                for span in spans:
                    if span.getText() == ' ':
                        continue
                    for child in span.children:
                        if isinstance(child, bs.element.NavigableString):
                            f.write(child)
                            continue
                        if child.get("class")[0] != "note":
                            f.write(child.getText())
                    f.write('\n')
                f.write('\n')
                #Get the next page link or break if it's the end of the book
                try:
                    nextLinkHtml = chapterSoup.select_one('a[data-vars-event-action="Next"]')
                    oldLink = link
                    link = 'http://www.bible.com' + nextLinkHtml.get('href')
                    #This Ukrainian translation has wrong links on some pages, leading to the same page
                    if oldLink == 'http://www.bible.com/bible/1755/1SA.21.UTT' and link == 'http://www.bible.com/bible/1755/1SA.21.UTT':
                        link = 'http://www.bible.com/bible/1755/1SA.22.UTT'
                    elif oldLink == 'http://www.bible.com/bible/1755/ESG.1.UTT' and link == 'http://www.bible.com/bible/1755/ESG.1.UTT':
                        link = 'http://www.bible.com/bible/1755/ESG.2.UTT'
                    elif oldLink == 'http://www.bible.com/bible/1755/ESG.3.UTT' and link == 'http://www.bible.com/bible/1755/ESG.3.UTT':
                        link = 'http://www.bible.com/bible/1755/ESG.4.UTT'
                    elif oldLink == 'http://www.bible.com/bible/1755/ESG.4.UTT' and link == 'http://www.bible.com/bible/1755/ESG.4.UTT':
                        link = 'http://www.bible.com/bible/1755/ESG.5.UTT'
                    elif oldLink == 'http://www.bible.com/bible/1755/ESG.5.UTT' and link == 'http://www.bible.com/bible/1755/ESG.5.UTT':
                        link = 'http://www.bible.com/bible/1755/ESG.6.UTT'
                    elif oldLink == 'http://www.bible.com/bible/1755/ESG.8.UTT' and link == 'http://www.bible.com/bible/1755/ESG.8.UTT':
                        link = 'http://www.bible.com/bible/1755/ESG.9.UTT'
                    elif oldLink == 'http://www.bible.com/bible/1755/ESG.10.UTT' and link == 'http://www.bible.com/bible/1755/ESG.10.UTT':
                        link = 'http://www.bible.com/bible/1755/JOB.1.UTT'
                    elif oldLink == 'http://www.bible.com/bible/1755/SIR.1.UTT' and link == 'http://www.bible.com/bible/1755/SIR.1.UTT':
                        link = 'http://www.bible.com/bible/1755/SIR.2.UTT'
                    elif oldLink == 'http://www.bible.com/bible/1755/SIR.5.UTT' and link == 'http://www.bible.com/bible/1755/SIR.5.UTT':
                        link = 'http://www.bible.com/bible/1755/SIR.6.UTT'
                    elif oldLink == 'http://www.bible.com/bible/1755/ISA.63.UTT' and link == 'http://www.bible.com/bible/1755/ISA.63.UTT':
                        link = 'http://www.bible.com/bible/1755/ISA.64.UTT'
                except:
                    break

# TODO: Remove undersocring before and after dashes in language names in filenames
