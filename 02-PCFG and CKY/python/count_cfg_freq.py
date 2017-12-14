#! /usr/bin/python

__author__="Alexander Rush <srush@csail.mit.edu>"
__date__ ="$Sep 12, 2012"

import sys, json
from collections import Counter




class Counts:
  def __init__(self):
    self.unary = Counter()
    self.binary = Counter()
    self.nonterm = Counter()
    self.vocabulary = set([])

  def count(self, tree):
    """
    Count the frequencies of non-terminals and rules in the tree.
    """
    if isinstance(tree, basestring): return

    # Count the non-terminal symbol. 
    symbol = tree[0]
    self.nonterm[symbol] += 1
    
    if len(tree) == 3:
      # It is a binary rule.
      y1, y2 = (tree[1][0], tree[2][0])
      key = (symbol, y1, y2)
      self.binary[(symbol, y1, y2)] += 1
      
      # Recursively count the children.
      self.count(tree[1])
      self.count(tree[2])
    elif len(tree) == 2:
      # It is a unary rule.
      y1 = tree[1]
      self.vocabulary.add(y1)
      key = (symbol, y1)
      self.unary[key] += 1

  def show(self, outfile):
    outfile = file("outputs/parse_train.counts.out", "w")
    for symbol, count in self.nonterm.iteritems():
      outfile.write( "%d NONTERMINAL %s\n" %(count, symbol) )

    for (sym, word), count in self.unary.iteritems():    
      outfile.write( "%d UNARYRULE %s %s\n" %(count, sym, word) )

    for (sym, y1, y2), count in self.binary.iteritems():
      outfile.write("%d BINARYRULE %s %s %s\n" %(count, sym, y1, y2))

def main(parse_file, out_file=None):
  counter = Counts() 
  for l in open(parse_file):
    t = json.loads(l)
    counter.count(t)

  counter.show(out_file)


def draft():  #DELETE THIS WHEN FINISHED THIS ASSIGNMENT
  counter = Counts() 
  for l in open("data/parse_train_with_rare.dat"):
    t = json.loads(l)
    counter.count(t)
  print counter.nonterm.keys()
     


if __name__ == "__main__": 
  #writes the 'count' output in a file
  #To begin with..
  # main("data/parse_train.dat", "outputs/cfg.counts")


  #This is for p1
  # main("data/parse_train_with_rare.dat", "outputs/parse_train.counts.out")
  draft()

  




  
