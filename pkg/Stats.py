import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def inversion(df):
    """
    This function returns the number of inversion in the manuscripts
    """
    inv = df['Inversion'].value_counts().to_string()
    return inv

def no_variation_per(df):
    """
    Number of times the two witnesses are exactly same
    """
    ret = ""
    for man in df['Manuscript A'].unique():
        tmp = df[df['Manuscript A'] == man]
        exact_count = ((tmp['Verse A'] == tmp['Verse B'])).sum()
        perc_exact= (exact_count/len(tmp['Verse A']))*100
        ret +=f'Percent of exact matches in the {man} compared to other manuscripts = {perc_exact}\n' 
    return ret
