# Bible-downloader
Download all bible translations from bible.com

The goal of this program is to download all bible translations for all languages uploaded at bible.com (there are 1,391 languages
with the total of 2,052 translations at the moment).
The texts are downloaded for further processing (regular expression search, search for specific verses, etc.) for linguistic purposes.

* downloadBible.py
Downloads the bible texts requests or urllib and saves them in separate txt files in separate directory for each language

* filesCutShort.py
Checks the list of downloaded texts and saves names of translations that do not end with REV 22:21 into filesCutShort.txt

* checkUnfinished.py
Checks if each of the translations in filesCutShort.txt was downloaded completely

* punctuation.py
Makes a list of all punctuation signs in all translations that should be separated in concordance



