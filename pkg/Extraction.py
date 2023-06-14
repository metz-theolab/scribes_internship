 
import nltk
from itertools import combinations
from bs4 import BeautifulSoup
import re
from collatex import Collation, collate
#import unicodedata
from random import *
import pandas as pd

nltk.download('punkt')

################################################################ CLASS DEFINITIONS
#=============================================================== VariantFinder

class VariantsFinder:
    """
    This class create object handling the variants analysis between a list of text in ancien hebrew
    Class made by Prunelle
    """

    def __init__(self, fileNames:list, folder:str = ""):
        """
        Create an object of type VariantsFinder
        """
        self.fileNames = fileNames
        self.witnesses = verse_matching(fileNames, folder)
        print("# Matching Done")

        for witness in self.witnesses:
            witness.cleanWitness()
        print("## Cleaning Done")

        for witness in self.witnesses:
            witness.collateVerse()
        print("### Collation Done")

    def getSampleVariant(self):
        """
        Gives the variant of a sample verse, by default 1
        Function made by Shehenaz, adapted into method by Prunelle
        """
        witness = choice(self.witnesses)
        witness.getSVG()

    def getDF(self):
        """
        Return the object as a dataframe
        """
        witness_as_list = [(x.verse_a, x.verse_b, x.manuscript_a, x.manuscript_b, x.chapter_a, x.chapter_b, x.verse_nb) for x in self.witnesses]
        columns = ['Verse A', 'Verse B', 'Manuscript A', 'Manuscript B', 'Chapter A', 'Chapter B', 'Verse']
        return pd.DataFrame(witness_as_list, columns=columns)
    
    def getLaTeX(self):
        """
        Return the object as a dataframe
        """
        return self.getDF().to_latex()

#=============================================================== Witness     

class Witness:
    """
    This class creates object handling a witness for collatex
    Class made by Prunelle
    """

    def __init__(self, verse_a:str, verse_b:str, manuscript_a:str, manuscript_b:str, chapter_a:str, chapter_b:str, verse_nb):
        """
        Create a witness containing the two different verses and all the chapter information
        Method made by Prunelle on an idea by Shehnaz
        """
        self.verse_a = verse_a
        self.verse_b = verse_b
        self.manuscript_a = manuscript_a
        self.manuscript_b = manuscript_b
        self.chapter_a = chapter_a
        self.chapter_b = chapter_b
        self.verse_nb = verse_nb

        self.variants = []
        self.alignment_table = None

    def cleanWitness(self):
        """
        This function clean the two verses of the witness
        Method made by Prunelle
        """
        self.verse_a = clean_hebrew_punctuations(self.verse_a)
        self.verse_b = clean_hebrew_punctuations(self.verse_b)

    def collateVerse(self):
        """
        Perform the collation on the two verses of the witness
        Method made by Prunelle adapting a code by Shehnaz
        """
        collation = Collation()
        collation.add_plain_witness("A", self.verse_a)
        collation.add_plain_witness("B", self.verse_b)
        # Perform the collation
        self.alignment_table = collate(collation)
        # Lets start trying to find the variants
        for column in self.alignment_table.columns:
            if column.variant:
            # Add to variants the tokens as strings       
                for manuscript, tokens in column.tokens_per_witness.items():
                    token_strings = [token.token_string for token in tokens]
                    self.variants.append(token_strings)
    
    def getSVG(self):
        """
        Show the collation on the two verses of the witness as a svg
        Directly printed with Jupyter Notebook
        Method made by Prunelle adapting a code by Shehnaz
        """
        collation = Collation()
        collation.add_plain_witness("A", self.verse_a)
        collation.add_plain_witness("B", self.verse_b)
        # Perform the collation
        collate(collation, output='svg_simple')
    
    def getHTML(self):
        """
        Show the collation on the two verses of the witness as an html code
        Directly printed with Jupyter Notebook
        Method made by Prunelle adapting a code by Shehnaz
        """
        collation = Collation()
        collation.add_plain_witness("A", self.verse_a)
        collation.add_plain_witness("B", self.verse_b)
        collate(collation, output='html')
    
    def getCSV(self):
        """
        Show the collation on the two verses of the witness as a n html code
        Need to ne printed
        Method made by Prunelle adapting a code by Shehnaz
        """
        collation = Collation()
        collation.add_plain_witness("A", self.verse_a)
        collation.add_plain_witness("B", self.verse_b)
        return(collate(collation, output='csv'))

    def __str__(self):
        if self.alignment_table:
            return f"Verse {self.verse_nb} : aligned\n{self.alignment_table}"
        return f"Verse {self.verse_nb} : non aligned"
    
    def __repr__(self):
        return str(self)
        
############################################################ FUNCTIONS DEFINITIONS
#=========================================================== For information

"""
TO UNDERSTAND THE XML FILES :
<!ELEMENT folio (#PCDATA)> <!-- shelfmark of the manuscript and folio number -->
<!ELEMENT verse_nb (#PCDATA)> <!-- verse (children of chapter) -->
<!ELEMENT line (#PCDATA)> <!-- line on the manuscript -->
<!ELEMENT vacat_car (#PCDATA)> <!-- a space into the manuscript -->
<!ELEMENT greek (#PCDATA)> <!-- greek word or letter -->
<!ELEMENT reconstructed (#PCDATA)> <!-- Hebrew reconstructed -->
<!ELEMENT superscript (#PCDATA)> <!-- Hebrew superscript letters or words -->
<!ELEMENT supralinear (#PCDATA)> <!-- Hebrew supralinear letters or words (I think = superscript) -->
<!ELEMENT margin_reconstructed (#PCDATA)> <!-- marginal notation reconstructed -->
<!ELEMENT margin_car (#PCDATA)> <!-- marginal notation -->
<!ELEMENT margin_infralinear (#PCDATA)> <!-- marginal notation -->
<!ELEMENT margin_supralinear (#PCDATA)> <!-- marginal notation -->
"""

#=========================================================== verse_matching

def verse_matching(fileNames:list, folder:str="") -> list:
    """
    Read all the XML files and do the verse matching
    Algorithm made by Shehnaz, adapted into function by Prunelle
    """
    soup = dict()
    chapter = dict()
    verse_list = dict()
    verses = dict()

    for currFile in fileNames:
        with open(folder+currFile,encoding="utf8") as fp: #TODO : get rid of the workdir stuff
            soup[currFile] = BeautifulSoup(fp,features='xml')
            chs = list()
            verse_list[currFile] = dict()
            verses[currFile] =dict()

            for i in soup[currFile].findAll("chap"):
                ch_string=i.contents[0].strip()
                chs.append(ch_string) # strip to remove trailing spaces or new line characters
                verses_list = list()
                verse = i.findAll("text")
                verses[currFile][ch_string] = dict()

                for verse_iter in verse:
                    if verse_iter.verse_nb:
                        verse_num=verse_iter.verse_nb.text.strip()
                    verses_list.append(verse_num)

                    # For now clean the text which might be enclosed in the tags
                    unwanted_tags= ["folio","verse_nb","line","vacat_car","greek","reconstructed","superscript",\
                    "supralinear","margin_reconstructed","margin_car","margin_infralinear",\
                    "margin_supralinear","Article"]
                    
                    # Clean tags
                    [s.extract() for s in verse_iter(unwanted_tags)]
                    
                    # FileName will never be empty
                    if (ch_string and verse_num):
                        verses[currFile][ch_string][verse_num] = verse_iter.text.replace("[","").replace("]","")
                verse_list[currFile][ch_string]=verses_list
            
            chapter[currFile] = chs

    chap_matching = dict()
    witnesses = []

    for combo in combinations(fileNames, 2):  # 2 for pairs, 3 for triplets, etc
        matching_chs_list = []

        if combo[0] in chap_matching.keys():
            pass
        else:
            chap_matching[combo[0]] = dict()

        for chap_in_file1 in chapter[combo[0]]:
            for chap_in_file2 in chapter[combo[1]]:
                ch1_num=re.findall(r'\b\d+\b', chap_in_file1)
                ch2_num=re.findall(r'\b\d+\b', chap_in_file2)

                if ch1_num == ch2_num:
                    matching_chs_list.append([chap_in_file1,chap_in_file2]) 
                    # Lets see if we can find common verses
                    common_verses= set(verse_list[combo[0]][chap_in_file1]).intersection(verse_list[combo[1]][chap_in_file2])

                    for com_verse in common_verses:
                        if com_verse:
                            verse_a = verses[combo[0]][chap_in_file1][com_verse]
                            verse_b = verses[combo[1]][chap_in_file2][com_verse]
                            manuscript_a = combo[0]
                            manuscript_b = combo[1]
                            chapter_a = chap_in_file1
                            chapter_b = chap_in_file2
                            verse_nb = com_verse
                            witness = Witness(verse_a, verse_b, manuscript_a, manuscript_b, chapter_a, chapter_b, verse_nb)
                            witnesses.append(witness)

        chap_matching[combo[0]][combo[1]]=matching_chs_list
        return witnesses
    
#=========================================================== clean_hebrew_punctuations

def clean_hebrew_punctuations(text:str) -> str:
    """
    Clean a text coming from an ancient hebrew manuscript
    Function made by Shehnaz
    """
    filtered_text = ''
    for char in text:
        if '\u0591' <= char <= '\u05F4' or '\uFB1D' <= char <= '\uFB4F' or char == '\u0020' or char =='\u0009':
            if char != '\u059F':  # Exclude this character
                if char == '\u0009':
                    filtered_text += '\u0020'
                else:
                    filtered_text += char
    return filtered_text