'''
@ 2022, Copyright AVIS Engine
'''
# Utils for AVISEngine Class
import base64
import cv2
import numpy as np
from PIL import Image
import io


__author__ = "Amirmohammad Zarif"
__email__ = "amirmohammadzarif@avisengine.com"

def stringToImage(base64_string):
    '''
    Converts Base64 String to Image

    Parameters
    ----------
    base64_string : str
        base64 image data to be converted
    '''
    imgdata = base64.b64decode(base64_string)
    return Image.open(io.BytesIO(imgdata))

def BGRtoRGB(image):
    '''
    Converts PIL Image to an RGB image(technically a numpy array) that's compatible with opencv
    '''
    return cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)

def KMPSearch(pat, txt):
    '''
    Knuth-Morris-Pratt(KMP) Algorithm : Efficient Search Algorithm to search for a pattern in a string.
    
    Parameters
    ----------
        pat: str
            Pattern to be searched for

        txt: str
            Text to search in
    '''
    M = len(pat)
    N = len(txt)
  
    # create lps[] that will hold the longest prefix suffix 
    # values for pattern
    lps = [0] * M
    j = 0 # index for pat[]

    # Preprocess the pattern (calculate lps[] array)
    computeLPS(pat, M, lps)
  
    i = 0 # Index for txt[]
    while i < N:
        if pat[j] == txt[i]:
            i += 1
            j += 1
  
        if j == M:
            return (i-j)
            
  
        # Mismatch after j matches
        elif i < N and pat[j] != txt[i]:
            # Do not match lps[0..lps[j-1]] characters.
            if j != 0:
                j = lps[j-1]
            else:
                i += 1
    return -1
  
def computeLPS(pat, M, lps):
    '''
    Computing the LPS
    '''
    len = 0 # length of the previous longest prefix suffix
  
    lps[0] # lps[0] is always 0
    i = 1
  
    # The loop calculates lps[i] for i = 1 to M-1
    while i < M:
        if pat[i]== pat[len]:
            len += 1
            lps[i] = len
            i += 1
        else:
            # To search step.
            if len != 0:
                len = lps[len-1]
            else:
                lps[i] = 0
                i += 1