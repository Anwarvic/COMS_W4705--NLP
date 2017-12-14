#! /usr/bin/python

import sys, json, pprint



class Node: 
  def __init__(self, name): self.name = name 
  def __repr__(self): return self.name

def format_tree(tree):
  #Convert a tree with strings, to one with nodes.
  
  tree[0] = Node(tree[0])
  if len(tree) == 2: 
    tree[1] = Node(tree[1])
  elif len(tree) == 3: 
    format_tree(tree[1])
    format_tree(tree[2])

def pretty_print_tree(tree):
  format_tree(tree)
  print pprint.pformat(tree)

def main(parse_file):
  for l in open(parse_file):
    pretty_print_tree(json.loads(l))
    





if __name__ == "__main__": 
  main("data/parse_train.dat")


