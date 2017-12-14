#! /usr/bin/python

__author__="Daniel Bauer <bauer@cs.columbia.edu>"
__date__ ="$Sep 12, 2011"

import sys
import re
from collections import defaultdict
import math
import pickle

"""
Count n-gram frequencies in a data file and write counts to
stdout. 

VERY IMPORTANT NOTE:
 -> I changes this script in order to run it from the sublime text and 
    not have to run it from the console

Before getting into the functions in this script, let's first explain how the training files words:
 - first, the train file is 'gene.train'.
 - the file has around 400,000 lines, each line takes the format of one word per line with word 
   and tag separated by space and '\n' separates sentences. 
 - The tag is either "O" for Other or "I-GENE".
 - So, a sentence like "Pharmacologic aspects of neonatal hyperbilirubinemia ." is written in the file 
   like:
    Pharmacologic O
    aspects O
    of O
    neonatal I-GENE
    hyperbilirubinemia O
    . O
 - After each sentence there is an intentional blank line.



In this script there are 3 functions let's dicuss them:
 - simple_conll_corpus_iterator():
   This function takes a file and returns a generator of tuples, each tuple is (word, tag). 
   It iterates over the whole file line by line. So, if the line is:
   >>> "comparison O"
   it returns
   >>> ('Comparison', 'O')

- sentence_iterator():
  This function takes a generator of tuples, the output from the simple_conll_corpus_iterator() function,
  and turns it into another generator but consists of lists. Each list has a number of tuples in it
  like this:
  [('Pharmacologic', 'O'), ('aspects', 'O'), ('of', 'O'), ('neonatal', 'O'), ('hyperbilirubinemia', 'O'), ('.', 'O')]

- get_ngrams():
  This function takes two arguments, the generator from sentence_iterator() function, and a number.
  This number determines the type of the language model we are using, so if n=2, then we will have a bigram
  if n=3, then it's a trigram.
  It iterates over the senteces and put (None, '*') at the start and (None, 'STOP') at the end. So, 
  if the sentence is:
  >>> [('Pharmacologic', 'O'), ('aspects', 'O'), ('of', 'O'), ('neonatal', 'O'), ('hyperbilirubinemia', 'O'), ('.', 'O')]
  It returns if we are using bigram:
  >>> [(None, '*'), ('Pharmacologic', 'O'), ('aspects', 'O'), ('of', 'O'), ('neonatal', 'O'), ('hyperbilirubinemia', 'O'), ('.', 'O'), (None, 'STOP')]
  It returns if we are using trigram:
  >>> [(None, '*'), (None, '*'), ('Pharmacologic', 'O'), ('aspects', 'O'), ('of', 'O'), ('neonatal', 'O'), ('hyperbilirubinemia', 'O'), ('.', 'O'), (None, 'STOP')]


According to the HMM() class, it has three variables:
 - n:
   it is the number of language model you are using. If (n=1), then it's just a unigram; if (n=3), then it's a unigram, bigrama 
   and trigram.
 
 - emission_counts:
   which is a dictionary with default value of 0, it contains the count of every word with its tag like:
      * ('AT', 'O'): 43
      * ('AT', 'I-GENE'): 8
      * ('untransfected', 'O'): 1
 
 - ngram_counts:
   is a list of dictionaries, each has the total count of tags in the corresponding language model. Like:
      * ngram_counts[1]:
         -> ('I-GENE',): 41072
         -> ('O',): 345128
      * ngram_counts[2]:
         -> ('I-GENE', 'I-GENE'): 24435
         -> ('O', 'I-GENE'): 15888
      * ngram_counts[1]:
         -> ('I-GENE', 'O', 'STOP'): 1813
         -> ('*', 'O', 'STOP'): 3

And it has these member functions:
 - train():
   this function takes a training file as an input and fills the previous counts (n, emission_counts, ngram_counts).

 - write_counts():
   this function takes a file as an input, and writes the  counts (n, emission_counts, ngram_counts)
   in a readable way. like
   >>>('untransfected', 'O'): 1
   becomes 1 WORDTAG O untransfected. And
   >>> ('*', 'O', 'I-GENE'): 593
   becomes 593 3-GRAM * O I-GENE

 - read_counts():
   this function takes a file as an input, this file should be the output of the write_counts() function.
   And from this file, it fills the counts which are (n, emission_counts, ngram_counts)

"""

def simple_conll_corpus_iterator(corpus_file):
    """
    Get an iterator object over the corpus file. The elements of the
    iterator contain (word, ne_tag) tuples. Blank lines, indicating
    sentence boundaries return (None, None).
    """
    l = corpus_file.readline()
    while l:
        line = l.strip()
        if line: # Nonempty line
            # Extract information from line.
            # Each line has the format
            # word pos_tag phrase_tag ne_tag
            fields = line.split(" ")
            ne_tag = fields[-1]
            #phrase_tag = fields[-2] #Unused
            #pos_tag = fields[-3] #Unused
            word = " ".join(fields[:-1])
            yield word, ne_tag
        else: # Empty line
            yield (None, None)                        
        l = corpus_file.readline()


no_lines = 0
def sentence_iterator(corpus_iterator):
    """
    Return an iterator object that yields one sentence at a time.
    Sentences are represented as lists of (word, ne_tag) tuples.
    """
    current_sentence = [] #Buffer for the current sentence
    for l in corpus_iterator:
      no_lines += 1          
      if l==(None, None):
          if current_sentence:  #Reached the end of a sentence
              yield current_sentence
              current_sentence = [] #Reset buffer
          else: # Got empty input stream
              sys.stderr.write("WARNING: Got empty input file/stream.\n")
              raise StopIteration
      else:
          current_sentence.append(l) #Add token to the buffer

    if current_sentence: # If the last line was blank, we're done
        yield current_sentence  #Otherwise when there is no more token
                                # in the stream return the last sentence.

def get_ngrams(sent_iterator, n):
    """
    Get a generator that returns n-grams over the entire corpus,
    respecting sentence boundaries and inserting boundary tokens.
    Sent_iterator is a generator object whose elements are lists
    of tokens.
    """
    for sent in sent_iterator:
         #Add boundary symbols to the sentence
         w_boundary = (n-1) * [(None, "*")]
         w_boundary.extend(sent)
         w_boundary.append((None, "STOP"))
         #Then extract n-grams
         ngrams = (tuple(w_boundary[i:i+n]) for i in xrange(len(w_boundary)-n+1))
         for n_gram in ngrams: #Return one n-gram at a time
            yield n_gram        

def use_rare_words(corpus_file):
    """
    Get an iterator object over the corpus file. The elements of the
    iterator contain (word, ne_tag) tuples. Blank lines, indicating
    sentence boundaries return (None, None).
    """
    with open("data/rare_words.pickle", "r") as f:
        t = pickle.load(f)
        rare_words = t[0].union(t[1])

    l = corpus_file.readline()
    while l:
        line = l.strip()
        if line: # Nonempty line
            # Extract information from line.
            # Each line has the format
            # word pos_tag phrase_tag ne_tag
            fields = line.split(" ")
            ne_tag = fields[-1]
            #phrase_tag = fields[-2] #Unused
            #pos_tag = fields[-3] #Unused
            word = " ".join(fields[:-1])
            if word in rare_words:
                yield "_RARE_", ne_tag
            else:
                yield word, ne_tag
        else: # Empty line
            yield (None, None)                        

        l = corpus_file.readline()


def has_digit(word):
    #Returns True if the given word has at least one number in it.
    match = re.search(r"[0-9]", word)
    if match:
        return True
    return False


def classify(word):
    """
    Puts the given word into one of four groups:
      -> '_NUM_': The word is rare and contains at least one numeric characters.
      -> '_ALLCAP_': The word is rare and consists entirely of capitalized letters.
      -> '_LASTCAP_': The word is rare, not all capitals, and ends with a capital letter.
      -> '_RARE_' The word is rare and does not fit in the other classes.  
    """
    word = word.strip()
    if has_digit(word):
        return "_NUM_"
    elif word.isupper():
        return "_ALLCAP_"
    elif word[-1].isupper():
        return "_LASTCAP_"
    else:
        return "_RARE_"


def use_rare_groups(corpus_file):
    """
    Get an iterator object over the corpus file. The elements of the
    iterator contain (word, ne_tag) tuples. Blank lines, indicating
    sentence boundaries return (None, None).
    """
    with open("data/rare_words.pickle", "r") as f:
        t = pickle.load(f)
        rare_words = t[0].union(t[1])
    l = corpus_file.readline()
    while l:
        line = l.strip()
        if line: # Nonempty line
            # Extract information from line.
            # Each line has the format
            # word pos_tag phrase_tag ne_tag
            fields = line.split(" ")
            ne_tag = fields[-1]
            #phrase_tag = fields[-2] #Unused
            #pos_tag = fields[-3] #Unused
            word = " ".join(fields[:-1])
            if word in rare_words:
                yield classify(word), ne_tag
            else:
                yield word, ne_tag
        else: # Empty line
            yield (None, None)                        
        l = corpus_file.readline()







##################################################################################################
class Hmm(object):
    """
    Stores counts for n-grams and emissions. 
    """
    def __init__(self, n=3):
        assert n>=2, "Expecting n>=2."
        self.n = n
        self.emission_counts = defaultdict(int)
        self.ngram_counts = [defaultdict(int) for i in xrange(self.n)]
        self.all_states = set()

    def train(self, corpus_file, RARE = False, GROUP=False):
        """
        Count n-gram frequencies and emission probabilities from a corpus file.
        """
        if RARE:
            ngram_iterator = \
                get_ngrams(sentence_iterator(use_rare_words(corpus_file)), self.n)
        elif GROUP:
            ngram_iterator = \
                get_ngrams(sentence_iterator(use_rare_groups(corpus_file)), self.n)
        else:
            ngram_iterator = \
                get_ngrams(sentence_iterator(simple_conll_corpus_iterator(corpus_file)), self.n)

        for ngram in ngram_iterator:
            #Sanity check: n-gram we get from the corpus stream needs to have the right length
            assert len(ngram) == self.n, "ngram in stream is %i, expected %i" % (len(ngram, self.n))

            tagsonly = tuple([ne_tag for word, ne_tag in ngram]) #retrieve only the tags            
            for i in xrange(2, self.n+1): #Count NE-tag 2-grams..n-grams
                self.ngram_counts[i-1][tagsonly[-i:]] += 1
            
            if ngram[-1][0] is not None: # If this is not the last word in a sentence
                self.ngram_counts[0][tagsonly[-1:]] += 1 # count 1-gram
                self.emission_counts[ngram[-1]] += 1 # and emission frequencies

            # Need to count a single n-1-gram of sentence start symbols per sentence
            if ngram[-2][0] is None: # this is the first n-gram in a sentence
                self.ngram_counts[self.n - 2][tuple((self.n - 1) * ["*"])] += 1

    def write_counts(self, output, printngrams=[1,2,3]):
        """
        Writes counts to the output file object.
        Format:

        """
        # First write counts for emissions
        for word, ne_tag in self.emission_counts:            
            output.write("%i WORDTAG %s %s\n" %(self.emission_counts[(word, ne_tag)], ne_tag, word))


        # Then write counts for all ngrams
        for n in printngrams:            
            for ngram in self.ngram_counts[n-1]:
                ngramstr = " ".join(ngram)
                output.write("%i %i-GRAM %s\n" %(self.ngram_counts[n-1][ngram], n, ngramstr))

    def read_counts(self, corpusfile):
        self.n = 3
        self.emission_counts = defaultdict(int)
        self.ngram_counts = [defaultdict(int) for i in xrange(self.n)]
        self.all_states = set()

        for line in corpusfile:
            parts = line.strip().split(" ")
            count = float(parts[0])
            if parts[1] == "WORDTAG":
                ne_tag = parts[2]
                word = parts[3]
                self.emission_counts[(word, ne_tag)] = count
                self.all_states.add(ne_tag)
            elif parts[1].endswith("GRAM"):
                n = int(parts[1].replace("-GRAM",""))
                ngram = tuple(parts[2:])
                self.ngram_counts[n-1][ngram] = count
                




if __name__ == "__main__": sentence_iterator(use_rare_words(corpus_file)
