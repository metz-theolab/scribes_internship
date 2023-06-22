##################################################################################################
#                                                                                                #
# Package created by Mayank Mishra, Prunelle Daudré--Treuil and Shehenaz Hossain                 #
# For the Ben Sira variant analysis Project for the NLP Master of the Lorraine University (2023) #
# Under the supervision of J.S. Ray and S.Robert                                                 #
#                                                                                                #
##################################################################################################

def subdataframe_extractor(df, filename):
    """
    Create subdataframes for all manuscripts
    """
    df_update = df[["Manuscript A", "Chapter A","Manuscript B", "Chapter B","Verse A", "Verse B", "Variant A", "Variant B"]]
    df_sub = df_update[(df_update['Manuscript A'] == filename) | (df_update['Manuscript B'] == filename)]
    return df_sub

def subdataframe_enhancer(df, filename):
    """
    Refining the subdataframes to fit our requirements
    """
    df = subdataframe_extractor(df, filename)
    idx = (df['Manuscript B'] == filename)
    df.loc[idx,['Verse A','Verse B']] = df.loc[idx,['Verse B', 'Verse A']].values
    df.loc[idx,['Variant A','Variant B']] = df.loc[idx,['Variant B','Variant A']].values
    df.loc[idx,['Chapter A','Chapter B']] = df.loc[idx,['Chapter B','Chapter A']].values
    df.loc[idx,['Manuscript A','Manuscript B']] = df.loc[idx,['Manuscript B','Manuscript A']].values

    return df

def avg_word_len(df):
    """
    Calculate average word length of variants
    """
    word_count = 0
    sum = 0
    for list in df['Variant A']:
        for word in list:
            word_count = word_count+1
            sum = sum + len(word)

    avg_variant_length_a = sum/word_count    

    return avg_variant_length_a

def exact_match_per(df):
    """
    Number of times the two witnesses are exactly same
    """
    exact_count = 0
    for text1, text2 in zip(df['Verse A'],df['Verse B']):
        if text1 == text2:
            exact_count = exact_count + 1
   
    perc_exact= (exact_count/len(df['Verse A']))*100
    return perc_exact

def word_addition_per(df):
    """
    Calculating how many times there is a word addition
    """
    add_count = 0
    for list in df['Variant B']:
        if len(list) == 0:    
            add_count = add_count+1

    perc_add = (add_count/len(df['Variant B']))*100
    return perc_add

def word_deletion_per(df):
    """
    Calculating word deletions 
    """
    add_count = 0
    for list in df['Variant A']:
        if len(list) == 0:    
            add_count = add_count+1

    perc_add = (add_count/len(df['Variant A']))*100
    return perc_add

def word_repitition_per(df):
    """
    Calculating dittos/repititions of words in witnessess of a manuscript
    """
    count = 0
    for sent in df['Verse A']:
        for i in range(len(sent.split())-1):
            if sent.split()[i] == sent.split()[i+1]:
                count = count+1 

    perc_rep = (count/len(df['Verse A']))*100
    return perc_rep  

def inversion_per(df):
    """
    Calculating percentage of inversions in the manuscript
    """
    for text1, text2 in zip(df['Verse A'], df['Verse B']):

        set1 = set(text1.split())
        set2 = set(text2.split())
        count = 0
        if (set1 == set2) and (len(text1.split()) == len(text2.split())): 
            # check if the sentences have same words and no repeating words
            if text1.split() != text2.split(): # check for inversion if not exact matches
                for i in range(len(text1.split())-2): 
                    if text1.split()[i] == text2.split()[i+1] and text1.split()[i+1] == text2.split()[i]: #check for near inversion when consecutive words are inverted
                        count = count+1

    if count > 0:
        perc_inv = (count/len(df['Verse A']))*100
        return perc_inv   
    return 0
            



