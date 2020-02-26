#! /usr/bin/env python3

import requests
import bs4 as bs
import re
import os

bibleBooks = {'Genesis': 'GEN', 'Exodus': 'EXO', 'Leviticus': 'LEV', 'Numbers': 'NUM', 'Deuteronomy': 'DEU', 'Joshua': 'JOS', 'Judges': 'JDG', 'Ruth': 'RUT', '1 Samuel': '1SA', '2 Samuel': '2SA', '1 Kings': '1KI', '2 Kings': '2KI', '1 Chronicles': '1CH', '2 Chronicles': '2CH', 'Ezra': 'EZR', 'Nehemiah': 'NEH', 'Esther': 'EST', 'Job': 'JOB', 'Psalms': 'PSA', 'Proverbs': 'PRO', 'Ecclesiastes': 'ECC', 'Song of Solomon': 'SNG', 'Isaiah': 'ISA', 'Jeremiah': 'JER', 'Lamentations': 'LAM', 'Ezekiel': 'EZK', 'Daniel': 'DAN', 'Hosea': 'HOS', 'Joel': 'JOL', 'Amos': 'AMO', 'Obadiah': 'OBA', 'Jonah': 'JON', 'Micah': 'MIC', 'Nahum': 'NAM', 'Habakkuk': 'HAB', 'Zephaniah': 'ZEP', 'Haggai': 'HAG', 'Zechariah': 'ZEC', 'Malachi': 'MAL', 'Matthew': 'MAT', 'Mark': 'MRK', 'Luke': 'LUK', 'John': 'JHN', 'Acts': 'ACT', 'Romans': 'ROM', '1 Chorinthians': '1CO', '2 Chorinthians': '2CO', 'Galatians': 'GAL', 'Ephesians': 'EPH', 'Philippians': 'PHP', 'Collosians': 'COL', '1 Thessalonians': '1TH', '2 Thessalonians': '2TH', '1 Timothy': '1TI', '2 Timothy': '2TI', 'Titus': 'TIT', 'Philemon': 'PHM', 'Hebrews': 'HEB', 'James': 'JAS', '1 Peter': '1PE', '2 Peter': '2PE', '1 John': '1JN', '2 John': '2JN', '3 John': '3JN', 'Jude': 'JUD', 'Revelation': 'REV'}

#Function to access web pages
def getPage(link):
    page = requests.get(link)
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
for languageLink in languageLinks[:1]:
    languageName = {v: k for k, v in languageList.items()}[languageLink[11:]]
    #Make a directory to store bible translations for one language
    newDir = os.path.join(os.getcwd(), languageName)
    os.makedirs(newDir)
    print("Initiating {}".format(languageName))
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
        print("Initiating {}".format(translationName))
        codes = re.search(translationPattern, translationLink).group(1, 2)
        translationCodes[translationName] = codes
        for translationName, translationCode in translationCodes.items():
            #Write into a file for the particular translation
            with open(os.path.join(newDir, '{}: {}.txt'.format(languageName, translationName)), 'a', encoding='utf-8-sig') as f:
                link = 'http://www.bible.com/bible/{}/GEN.INTRO1.{}'.format(translationCode[0], translationCode[1])
                while True:
                    chapterSoup = getPage(link)
                    spans = chapterSoup.select('span[class^="verse"]')
                    #Write the book title and chapter number to the file
                    f.write('\n' + '_'.join(chapterSoup.select_one('title').getText().split(',')[0].upper().split()) + '\n')
                    for span in spans:
                        if span.getText() != ' ':
                            f.write(span.getText() + '\n')
                    try:
                        nextLinkHtml = chapterSoup.select_one('a[data-vars-event-action="Next"]')
                    except:
                        break
                    link = 'http://www.bible.com' + nextLinkHtml.get('href')
