from pkg.Witness import Witness

import nltk
from itertools import combinations
from bs4 import BeautifulSoup
import re
from random import *
import pandas as pd

nltk.download('punkt')

################################################################ CLASS DEFINITIONS
#=============================================================== VariantFinder

class VariantsFinder:
    """
    This class create object handling the variants analysis between a list of text in ancien hebrew
    """

    def __init__(self, fileNames:list, unwanted_tags:list, folder:str = ""):
        """
        Create an object of type VariantsFinder
        """
        self.fileNames = fileNames
        self.witnesses = verse_matching(fileNames, unwanted_tags, folder)
        print("# Matching Done")

        for witness in self.witnesses:
            witness.cleanWitness()
        print("## Cleaning Done")

        for witness in self.witnesses:
            witness.collateVerse()
        print("### Collation Done")

        for witness in self.witnesses:
            witness.distance()
        print("#### Distance Done")

        for witness in self.witnesses:
            witness.inversion()
            witness.difference()
        print("##### Errors Classification Done")

    def getSampleVariant(self):
        """
        Gives the variant of a sample verse, by default 1
        """
        witness = choice(self.witnesses)
        witness.getSVG()

    def getDF(self):
        """
        Return the object as a dataframe
        """
        witness_as_list = [(x.verse_a, x.verse_b, x.variants_a, x.variants_b, x.manuscript_a, x.manuscript_b, x.chapter_a, x.chapter_b, x.verse_nb, x.levenshtein, x.hamming, x.inv, x.diff) for x in self.witnesses]
        columns = ['Verse A', 'Verse B', 'Variant A', 'Variant B', 'Manuscript A', 'Manuscript B', 'Chapter A', 'Chapter B', 'Verse', 'Levenshtein', 'Hamming', 'Inversion', 'Difference']
        return pd.DataFrame(witness_as_list, columns=columns)
    
    def getMarkdown(self, name:str = "Variants.md"):
        """
        Return the object as a dataframe
        """
        self.getDF().to_markdown(name)
    
    def getCSV(self, name:str = "Variants.csv"):
        """
        Return the object as a dataframe
        """
        self.getDF().to_csv(name)
        
############################################################ FUNCTIONS DEFINITIONS
#=========================================================== verse_matching

def verse_matching(fileNames:list, unwanted_tags:list, folder:str="") -> list:
    """
    Read all the XML files and do the verse matching
    """
    chapter = dict()
    verse_list = dict()
    verses = dict()

    for currFile in fileNames:
        with open(folder+currFile,encoding="utf8") as fp: 
            soup = BeautifulSoup(fp,features='xml')
            chs = list()
            verse_list[currFile] = dict()
            verses[currFile] = dict()

            for chap in soup.findAll("chap"):
                ch_string=chap.contents[0].strip()
                chs.append(ch_string) # strip to remove trailing spaces or new line characters
                verses_list = list()
                verse = chap.findAll("text")
                verses[currFile][ch_string] = dict()

                for verse_iter in verse:
                    if verse_iter.verse_nb:
                        verse_num = verse_iter.verse_nb.text.strip()

                    verses_list.append(verse_num)

                    # Clean tags TODO
                    [s.extract() for s in verse_iter(unwanted_tags)]
                    
                    if (ch_string and verse_num): # FileName will never be empty
                        verses[currFile][ch_string][verse_num] = verse_iter.text.replace("[","").replace("]","")


                verse_list[currFile][ch_string] = verses_list
            
            chapter[currFile] = chs

    witnesses = []

    for combo in combinations(fileNames, 2):  # 2 for pairs, 3 for triplets, etc
        matching_chs_list = []

        for chap_in_file1 in chapter[combo[0]]:
            for chap_in_file2 in chapter[combo[1]]:
                ch1_num = re.findall(r'\b\d+\b', chap_in_file1)
                ch2_num = re.findall(r'\b\d+\b', chap_in_file2)

                if ch1_num == ch2_num:
                    matching_chs_list.append([chap_in_file1,chap_in_file2]) 
            
        for [chap_in_file1,chap_in_file2] in matching_chs_list:
            common_verses = set(verse_list[combo[0]][chap_in_file1]).intersection(verse_list[combo[1]][chap_in_file2])

            for com_verse in filter(bool, common_verses):
                verse_a = verses[combo[0]][chap_in_file1][com_verse]
                verse_b = verses[combo[1]][chap_in_file2][com_verse]
                witnesses.append(Witness(verse_a, verse_b, combo[0], combo[1], chap_in_file1, chap_in_file2, com_verse))

    return witnesses