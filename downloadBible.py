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
        languageCode = re.search('(?<=\().{3}(?:_.{2,3})?(?=\))', languageLink.get('title')).group()
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
translationPattern = re.compile('(?<=versions/)(.+?)-(.+?)-')
for languageLink in languageLinks:
    languageName = {v: k for k, v in languageList.items()}[languageLink[11:]]
    print("Initiating {}".format(languageName))
    #Make a directory to store bible translations for one language
    newDir = os.path.join(os.getcwd(), languageName)
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
                if languageLink in translations:
                    translations[languageLink][item.getText()] = item.get('href')
                else:
                    translations[languageLink] = {item.getText():item.get('href')}
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
        fileName = os.path.join(newDir, '{}--{}.txt'.format(languageName, translationName))
        #Check if the file exists to skip if necessary (to resume the program when it hits an unexpected error)
        if os.path.isfile(fileName):
            continue
        with open(fileName, 'a', encoding='utf-8-sig') as f:
            link = 'http://www.bible.com/bible/{}/GEN.INTRO1.{}'.format(translationCode[0], translationCode[1])
            while True:
                chapterSoup = getPage(link)
                spans = chapterSoup.select('span[class^="verse"]')
                #Check if there is text (e.g Introduction) without a verse number
                if len(spans) == 0:
                    spans = chapterSoup.select('span[class="content"]')
                #Check if the link is not broken (the first occurrence is https://www.bible.com/bible/37/S3Y.1.CEB)
                try:
                    print("    Initiating {}".format(chapterSoup.select_one('title').getText().split(',')[0]))
                except:
                    if chapterSoup.select_one('body').getText().startswith('{"statusCode":404'):
                        if oldLink == 'http://www.bible.com/bible/37/LJE.INTRO1.CEB':
                            link = 'https://www.bible.com/bible/37/SUS.1.CEB'
                            continue
                        elif oldLink == 'http://www.bible.com/bible/37/MAN.1.CEB':
                            #The second occurrence of empty pages: https://www.bible.com/bible/37/PS2.1.CEB,
                            #https://www.bible.com/bible/37/PS2.2.CEB, and https://www.bible.com/bible/37/PS2.3.CEB
                            link = 'https://www.bible.com/bible/37/3MA.1.CEB'
                            continue
                        else:
                            raise
                #Write the book title and chapter number to the file
                f.write('_'.join(chapterSoup.select_one('title').getText().split(',')[0].upper().split()) + '\n')
                #Write verses to the file
                for span in spans:
                    if span.getText() == ' ':
                        continue
                    for child in span.children:
                        if child.get("class")[0] != "note":
                        f.write(child.getText())
                    f.write('\n')
                f.write('\n')
                #Get the next page link or break if it's the end of the book
                try:
                    nextLinkHtml = chapterSoup.select_one('a[data-vars-event-action="Next"]')
                    oldLink = link
                    link = 'http://www.bible.com' + nextLinkHtml.get('href')
                except:
                    break
