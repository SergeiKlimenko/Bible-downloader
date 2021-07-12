import os
import json
import unicodedata

cwd = os.getcwd()
dirs = [dir for dir in os.scandir('.') if dir.is_dir()]

punctuation = {}
languages = {}
yes = ['Po', 'Pe', 'Ps', 'Pd', 'Pi', 'Pf', 'Pc', 'Sm', 'Sc', 'So', 'Cf', 'Cc', 'Co']

for dir in dirs:
    files = [f for f in os.scandir(dir) if f.name.endswith('json')]

    for file in files:
        spaces = 0
        print(file.name)
        with open(file, 'r', encoding='utf-8-sig') as f:
            # text = set(''.join([line for line in f.readlines()[2:-2] if not line in ['[\n', '  [\n', '  ],\n', '  ]\n', '][\n', '  [\n']][4::5]))
            text = json.loads("[" + f.read().replace("][", "],[") + "]")
            text = set(''.join([verse[4] for chapter in text for verse in chapter]))
            # text = ''.join(sorted(set(''.join([verse[4] for chapter in text for verse in chapter]))))
        
        # if 'mno' in text or 'абв' in text:
        #     continue
        
        for symbol in text:
            # if not symbol.isalnum() and unicodedata.category(symbol) in yes:
                # if symbol in punctuation.keys() and file.name in punctuation[symbol]:
            #         continue
            #     # print(symbol)
                # punctuation.setdefault(symbol, []).append(file.name)
        # print(file.name)
        # print(text)
            if not symbol.isalnum() and unicodedata.category(symbol) in yes:
                if symbol in punctuation.keys() and file.name in punctuation[symbol]:
                    continue
                try:
                    symbolName = unicodedata.name(symbol)
                except ValueError:
                    symbolName = None
                symbolCategory = unicodedata.category(symbol)
                print(symbol, symbolCategory, symbolName)
                punctuation.setdefault((symbol, symbolCategory, symbolName), []).append(file.name)
                languages.setdefault(file.name, []).append((symbol, symbolCategory, symbolName))

         
signsSorted = sorted(punctuation, key = lambda k: len(punctuation[k]), reverse=True)
sortedPunctuation = {}
for sign in signsSorted:
    sortedPunctuation[sign] = punctuation[sign]

with open('punctuation.txt', 'w', encoding='utf-8-sig') as f:
    for k, v in sortedPunctuation.items():
        f.write(str(k) + '\n')
        for i in v:
            f.write('    ' + i + '\n')

    for k, v in languages.items():
        f.write(str(k) + '\n')
        f.write(str(languages[k]) + '\n')