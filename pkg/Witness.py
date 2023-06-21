import nltk
import re
from collatex import Collation, collate
from random import *
from textdistance import levenshtein, hamming

nltk.download('punkt')

################################################################ CLASS DEFINITIONS
#=============================================================== Witness     

class Witness:
    """
    This class creates object handling a witness for collatex
    """

    def __init__(self, verse_a:str, verse_b:str, manuscript_a:str, manuscript_b:str, chapter_a:str, chapter_b:str, verse_nb:str):
        """
        Create a witness containing the two different verses and all the chapter information
        """
        self.verse_a = verse_a
        self.verse_b = verse_b
        self.manuscript_a = manuscript_a
        self.manuscript_b = manuscript_b
        self.chapter_a = chapter_a
        self.chapter_b = chapter_b
        self.verse_nb = verse_nb

        self.variants_a = []
        self.variants_b = []
        self.alignment_table = None
        self.levenshtein = 0
        self.hamming = 0

    def cleanWitness(self):
        """
        This function clean the two verses of the witness
        """
        self.verse_a = clean_hebrew_punctuations(self.verse_a)
        self.verse_b = clean_hebrew_punctuations(self.verse_b)

    def collateVerse(self):
        """
        Perform the collation on the two verses of the witness
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
                    if (manuscript == 'A'):
                        self.variants_a.extend(token_strings)
                    else:
                        self.variants_b.extend(token_strings)


    def distance(self):
        """
        A method computing the levenstein and hamming distance between the verses
        """
        self.levenshtein = levenshtein("".join(self.variants_a), "".join(self.variants_b))
        self.hamming = hamming("".join(self.variants_a), "".join(self.variants_b))
    
    def getSVG(self):
        """
        Show the collation on the two verses of the witness as a svg
        Directly printed with Jupyter Notebook
        """
        collation = Collation()
        collation.add_plain_witness("A", self.verse_a)
        collation.add_plain_witness("B", self.verse_b)
        collate(collation, output='svg_simple')
    
    def getHTML(self):
        """
        Show the collation on the two verses of the witness as an html code
        Directly printed with Jupyter Notebook
        """
        collation = Collation()
        collation.add_plain_witness("A", self.verse_a)
        collation.add_plain_witness("B", self.verse_b)
        collate(collation, output='html')
    
    def getCSV(self):
        """
        Show the collation on the two verses of the witness as a n html code
        Need to ne printed
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
#=========================================================== clean_hebrew_punctuations

def clean_hebrew_punctuations(text:str) -> str:
    """
    Clean a text coming from an ancient hebrew manuscript
    """
    # Replace tab characters with spaces
    text = text.replace('\t', ' ')
    # Regex pattern for hebrew text excluding punctuation
    pattern = r'[^\u0591-\u05F4\uFB1D-\uFB4F ]|[\u05F3\u05F4\u05BE\u05C0\u05C3\u05C2\u05BD\u059F]'
    # Use re.sub() to replace matched characters with ''
    output_str = re.sub(pattern, '', text)
    return output_str