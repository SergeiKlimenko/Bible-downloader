import os
import bs4 as bs
import requests
import re
import traceback

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
        with open(newPath + '\\' + translation, 'r', encoding='utf-8-sig') as file:
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
                print(link)
                if line.isupper() and '_' in line:
                    if anchor in line:
                        
                        text[text.index(line)] = line.strip('\n') + ' (' + code + ')\n'
                        print("The anchor is in the line!")
                        print(line)
                        continue
                    else:
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
    
                                chapterSoup = getPage(link)
                                if chapterSoup.select_one('body').getText().startswith('{"statusCode":404'):                     
                                    if oldLink == 'http://www.bible.com/bible/37/LJE.1.CEB':
                                        link = 'https://www.bible.com/bible/37/SUS.1.CEB'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/37/MAN.1.CEB':
                                        #The second occurrence of empty pages: https://www.bible.com/bible/37/PS2.1.CEB,
                                        #https://www.bible.com/bible/37/PS2.2.CEB, and https://www.bible.com/bible/37/PS2.3.CEB
                                        link = 'https://www.bible.com/bible/37/3MA.1.CEB'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/303/LJE.1_1.CEVDCI':
                                        #The third occurrence: https://www.bible.com/fr/bible/303/S3Y.1.CEVDCI
                                        link = 'https://www.bible.com/bible/303/SUS.1_1.CEVDCI'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/416/LJE.1.GNBDC':
                                        #The fourth occurrence
                                        link = 'https://www.bible.com/bible/416/SUS.INTRO1.GNBDC'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/69/LJE.1_1.GNTD':
                                        #The fifth occurrence
                                        link = 'https://www.bible.com/bible/69/SUS.INTRO1.GNTD'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/546/BAR.6.KJVA':
                                        #The sixth occurrence
                                        link = 'https://www.bible.com/bible/546/SUS.INTRO1.KJVA'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/2015/LJE.1_1.NRSV-CI':
                                        link = 'https://www.bible.com/bible/2015/SUS.1_1.NRSV-CI'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/2017/LJE.1_1.RSV-CI':
                                        link = 'https://www.bible.com/bible/2017/SUS.1_1.RSV-CI'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/1922/LJE.1_1.RV1895':
                                        link = 'https://www.bible.com/bible/1922/SUS.1.RV1895'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/206/LJE.6.WEB':
                                        link = 'https://www.bible.com/bible/206/SUS.1.WEB'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/206/MAN.1.WEB':
                                        break
                                    elif oldLink == 'http://www.bible.com/bible/1204/4MA.18.WEBBE':
                                        link = 'https://www.bible.com/bible/1204/DAG.1.WEBBE'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/2407/LJE.1.WBMS':
                                        link = 'https://www.bible.com/bible/2407/SUS.1.WBMS'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/377/LJE.1_1.BMDC':
                                        link = 'https://www.bible.com/bible/377/SUS.1_1.BMDC'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/221/LJE.1.BCNDA':
                                        link = 'https://www.bible.com/bible/221/SUS.1.BCNDA'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/2101/LJE.1_1.BWMA':
                                        link = 'https://www.bible.com/bible/2101/SUS.1.BWMA'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/178/LJE.1_1.TLAI':
                                        link = 'https://www.bible.com/bible/178/SUS.1_1.TLAI'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/2197/LJE.1.MBBTAG12':
                                        link = 'https://www.bible.com/bible/2197/SUS.1.MBBTAG12'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/144/LJE.1.MBB05':
                                        link = 'https://www.bible.com/bible/144/SUS.1.MBB05'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/393/LJE.1.BHND':
                                        link = 'https://www.bible.com/bible/393/SUS.1.BHND'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/1817/LJE.1.SUVDC':
                                        link = 'https://www.bible.com/bible/1817/SUS.1.SUVDC'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/228/LJE.1.BPT09DC':
                                        link = 'https://www.bible.com/bible/228/SUS.1.BPT09DC'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/464/LJE.1_1.SEBDT':
                                        link = 'https://www.bible.com/bible/464/SUS.1_1.SEBDT'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/2308/LJE.1.KKDEU':
                                        link = 'https://www.bible.com/bible/2308/SUS.1.KKDEU'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/2308/MAN.1.KKDEU':
                                        link = 'https://www.bible.com/bible/2308/4MA.1.KKDEU'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/901/BEL.1.%D0%9D%D0%9F':
                                        link = 'http://www.bible.com/bible/901/MAN.1.НП'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/901/MAN.1.НП':
                                        link = 'https://www.bible.com/bible/901/MAT.1.НП'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/1819/BEL.1.%E6%96%B0%E5%85%B1%E5%90%8C%E8%A8%B3':
                                        link = 'http://www.bible.com/bible/1819/1ES.1.新共同訳'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/1889/LJE.1_1.%E6%AC%A1%E7%B6%93':
                                        link = 'https://www.bible.com/bible/1889/SUS.1_1.次經'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/592/BAR.6.KCB':
                                        link = 'http://www.bible.com/bible/592/SUS.1_1.KCB'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/2188/LJE.1_1.MBBCEB99':
                                        link = 'http://www.bible.com/bible/2188/SUS.1.MBBCEB99'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/890/LJE.1.BPV':
                                        link = 'https://www.bible.com/bible/890/SUS.1.BPV'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/1754/LJE.1.AKKDC08':
                                        link = 'http://www.bible.com/bible/1754/SUS.1_1.AKKDC08'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/905/LJE.1.FBDC':
                                        link = 'http://www.bible.com/bible/905/SUS.1_1.FBDC'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/1807/BAR.6.MACGAP':
                                        link = 'http://www.bible.com/bible/1807/SUS.1.MACGAP'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/2190/LJE.1.MBBHIL12':
                                        link = 'http://www.bible.com/bible/2190/SUS.1.MBBHIL12'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/171/LJE.1.BK':
                                        link = 'http://www.bible.com/bible/171/SUS.INTRO1.BK'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/1079/BAR.6.ABK':
                                        link = 'http://www.bible.com/bible/1079/SUS.1.ABK'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/1202/BAR.6.GIKDC':
                                        link = 'http://www.bible.com/bible/1202/SUS.INTRO1.GIKDC'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/387/LJE.1_1.BIRD':
                                        link = 'http://www.bible.com/bible/387/SUS.1_1.BIRD'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/1393/DAN.12.BKPDCG':
                                        link = 'http://www.bible.com/bible/1393/SUS.1_1.BKPDCG'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/1957/LJE.1.HAT98':
                                        link = 'http://www.bible.com/bible/1957/SUS.1_1.HAT98'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/552/LJE.1.BB03':
                                        link = 'http://www.bible.com/bible/552/SUS.INTRO1.BB03'
                                        
                                    elif oldLink == 'http://www.bible.com/bible/825/LJE.1_1.BYK09':
                                        link = 'http://www.bible.com/bible/825/SUS.1.BYK09'
                                        
                                    else:
                                        print("A NEW OCCURRENCE OF MISSING PAGES")
                                        exit()
                                chapterSoup = getPage(link)
    
                                newCode = re.search('(?<=\d\/).+?(?=\.)', link).group()
                                
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
                            text[text.index(line)] = line.strip('\n') + ' (' + code + ')\n'
                            #print(line) 
                else:
                    print("Nothing here")
                    continue
        # Save the file
        with open(newPath + '\\' + translation, 'w', encoding='utf-8-sig') as file:
            for line in text:
                file.write(line)
