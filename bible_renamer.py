import os
import bs4 as bs
import requests
import re

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
languageLinks = dict()
for name, code in languageList.items():
    for languageLink in potentialLanguageLinks:
        #Not all links in the gathered potentialLanguageLinks contain languagecodes
        try:
            if code in languageLink.get('title') and name in languageLink.getText():
                if languageLink.get('href') not in languageLinks:
                    languageLinks[name] = languageLink.get('href')
        except:
            continue

###Loop through the language links to get translation lists
translations = dict()
translationPattern = re.compile('(?<=versions/)(\w+)-([\w|%]+)?')
for languageName, languageLink in list(languageLinks.items())[:1]:
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
                if languageName in translations:
                    translations[languageName][('_'.join(item.getText().split())+'_'+str(codes[1])).replace(':', '')] = item.get('href')
                else:
                    translations[languageName] = {('_'.join(item.getText().split())+'_'+str(codes[1])).replace(':', ''):item.get('href')}
        except:
            continue

# Open each language directory
languageList = [dir for dir in os.listdir(path='.') if os.path.isdir(dir)]

for language in translations:
    newPath = os.getcwd() + '\\' + language
    
    # Open each translation file
    translationList = os.listdir(newPath)
    for translation in translationList:
        with open(newPath + '\\' + translation, 'r+', encoding='utf-8-sig') as file:
            text = file.readlines()
            headers = [line for line in text if line.isupper()]
                        
# Go to the corresponding starting link
            translationLink = translations[language][translation.split('--')[1][:-4]]
            print(translationLink)
            codes = re.search(translationPattern, translationLink).group(1, 2)
            link = 'http://www.bible.com/bible/{}/GEN.INTRO1.{}'.format(codes[0], codes[1])

            chapterSoup = getPage(link)
            #Check if the link is not broken (the first occurrence is https://www.bible.com/bible/37/S3Y.1.CEB)
            print(link) #delete
            print("    Initiating {}".format(chapterSoup.select_one('title').getText().split(',')[0]))
    
            # Append each chapter title with a code
            title = '_'.join(chapterSoup.select_one('title').getText().split(',')[0].upper().split()) + '\n'
            anchor = '_'.join(title.split('_')[:-1])
            code = re.search('(?<=\d\/).+?(?=\.)', link).group()

            for line in text:
                if not line.isupper():
                    continue
                elif anchor in line:
                    line = line.strip('\n') + ' (' + code + ')\n'
                    print("The anchor is in the line!")
                    print(line)
                    continue
                else:
                    print(line)
                    while True:
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

                            newCode = re.search('(?<=\d\/).+?(?=\.)', link).group()
                            chapterSoup = getPage(link)
                            if newCode == code:
                                continue
                            else:
                                code = newCode
                                title = '_'.join(chapterSoup.select_one('title').getText().split(',')[0].upper().split()) + '\n'
                                anchor = '_'.join(title.split('_')[:-1])
                            break
                        except:
                            raise
                            break
                    if line == title:
                        print("The link is the same as the title!")
                        line = line.strip('\n') + ' (' + code + ')\n'
                        print(line) 
                    
            # Save the file
            for line in text:
                file.write(line)
