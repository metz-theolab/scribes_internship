 
import nltk
from itertools import combinations
from bs4 import BeautifulSoup
import re
from collatex import Collation, collate
import unicodedata


nltk.download('punkt')

################################################################ CLASS DEFINITIONS

class VariantsFinder:
    """
    This class create object handling the variants analysis between a list of text in ancien hebrew
    Class made by Prunelle
    """

    def __init__(self, fileNames:list):
        """
        Create an object of type VariantsFinder
        """
        self.fileNames = fileNames
        self.witnesses, self.chap_info = verse_matching(fileNames)
        print("# Matching Done")

        for witness in self.witnesses.values():
            for verse in witness.values():
                verse = clean_hebrew_punctuations(verse)
        print("## Cleaning Done")

        self.variants = verse_collation(self.witnesses)
        print("### Collation Done")

    def getSampleVariant(self, x:int = 1):
        """
        Gives the variant of a sample verse, by default 1
        Function made by Shehenaz, adapted into method by Prunelle
        """
        collation = Collation()
        collation.add_plain_witness("A", self.witnesses[x]['A'])
        collation.add_plain_witness("B", self.witnesses[x]['B'])
        print("\nManuscript A: " + self.witnesses[x]['A'])
        print("Manuscript B: " + self.witnesses[x]['B']+"\n")
        print(self.chap_info[x])
        collate(collation,output="svg")

############################################################ FUNCTIONS DEFINITIONS

def test():
    """
    A little test function to test the pkg stuff
    """
    print("test")

def verse_matching(fileNames):
    """
    NEED DOCSTRING
    Algorithm made by Shehnaz, adapted into function by Prunelle
    """
    soup = dict()
    chapter = dict()
    verse_list = dict()
    verses = dict()

    for currFile in fileNames:
        with open("WorkDir/"+currFile,encoding="utf8") as fp: #TODO : get rid of the workdir stuff
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
                    """
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
    witnesses = dict()
    chap_info = dict()
    count = 0
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
                            witnesses[count] = dict()
                            witnesses[count]['A'] = verses[combo[0]][chap_in_file1][com_verse]
                            witnesses[count]['B'] = verses[combo[1]][chap_in_file2][com_verse]
                            chap_info[count] = (combo[0],chap_in_file1,combo[1],chap_in_file2,com_verse)
                            count = count+1;
        chap_matching[combo[0]][combo[1]]=matching_chs_list
        
        return witnesses, chap_info
    
def clean_hebrew_punctuations(text):
    """
    NEED DOCSTRING
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

def verse_collation(witnesses):
    """
    NEED DOCSTRING
    Algorithm made by Shehnaz, adapted into function by Prunelle
    """
    # Use the collatex library to perform the collation and build the variants

    num_witnesses = len(witnesses)
    # Lets create an empty dictionary to store the variants
    variants = dict()
    # For chapter information we can refer to the dictionary chap_info
    # The dictionary indexes are same across all the data

    # Lets loop of each witness
    for witness_ind in range(num_witnesses):
        # Lets run the collation for each set of witnesses
        # Create empty dictionary for each element
        variants[witness_ind] = dict()
        variants[witness_ind]['A'] = '' # Empty initialisatiom
        variants[witness_ind]['B'] = ''
        collation = Collation()
        collation.add_plain_witness("A", witnesses[witness_ind]['A'])
        collation.add_plain_witness("B", witnesses[witness_ind]['B'])
        # Perform the collation
        alignment_table = collate(collation)
        # Lets start trying to find the variants
        for column in alignment_table.columns:
            if column.variant:
            # Add to variants the tokens as strings       
                for manuscript, tokens in column.tokens_per_witness.items():
                    token_strings = [token.token_string for token in tokens]
                    variants[witness_ind][manuscript] += ' '.join(token_strings)
    return variants