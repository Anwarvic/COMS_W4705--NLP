# -*- coding: utf-8 -*-
from collections import defaultdict, Counter
import pickle


def read_file(in_file):
	#this function is used to read a file, save its lines into a list
	#and close it 
	fin = file(in_file, "r")
	lst = fin.readlines()
	fin.close()
	return lst


start = True
def restrict(original, tmp, index, num):
	"""This function is used to return the index of the maximum number in a 
	list 'original'	that is near to the number 'index' by a certain number 'num'. 'tmp' is a ascending sorted copy of 'original'

	So, for example
	>>>lst = [1, 3, 8, 9, 5]
	>>>tmp = sorted(list, reverse=True)
	>>>restrict(lst, tmp, 1, 2)
	3  #index of '9'
	>>>
	>>>restrict(lst, tmp, 1, 1)
	2 #index of '8'
	>>>restrict(lst, tmp, 1, 0)
	1 #the index of the number itself
	

	ALSO, if the maximum number is less than '0.0000000001', it returns None.
	"""
	global start
	if start:
		length = len(original)
		if index > length:
			index = length
		start = False
	if tmp[0] < 0.0000000001:
		return None
	else:
		idx = original.index(tmp[0])
		if idx in range( (index - num) , (index + num+1) ):
			return idx
		else:
			return restrict(original, tmp[1:], index, num)



class IBM_model2():

	def __init__(self):
		self.en_count = defaultdict(float) #en_count['the'] = 1234
		self.en_sp_count = defaultdict(Counter) #en_sp_count['the']['le'] = 1234
		self.length_c = defaultdict(float) #length_c[6, 7]=3
		self.c = defaultdict(float) #c[1, 2, 6, 7] = 2
		self.delta = defaultdict(float) #is used just in 'EM_train' function


	def initialize(self, en_lines, sp_lines, t_file): #Takes around '35' seconds
		""" it initializes the following dictionaries by reading the file 't_file':
		 -> en_count
		 -> en_sp_count: which os basically represents the parameter 't'
		
		and also initializes these:
		 -> length_c
		 -> c
		 BTW, c stands for 'count'
		 """
		assert type(en_lines) == list and type(sp_lines) == list
		print "Reading Variables: . . ."
		with open(t_file, "r") as fin:
			_tuple = pickle.load(fin)
		assert len(_tuple) == 3
		self.en_count = _tuple[0]
		self.en_sp_count = _tuple[1]

		print "Start Initializing:",
		for idx in range(len(en_lines)): #5401
			if (idx+1)%500 == 0:
				print ".",
			
			en_sentence = ("NULL "+en_lines[idx][:-1]).split(" ")
			sp_sentence = sp_lines[idx][:-1].split(" ")
			en_length, sp_length = len(en_sentence), len(sp_sentence)
			self.length_c[en_length, sp_length] += 1 
			for i, en in enumerate(en_sentence):
				for j, sp in enumerate(sp_sentence):
					self.c[i, j, en_length, sp_length] = 1. / (en_length+1.)


	def t(self, en_word, sp_word):
		#calculated the 't' parameter given both the English word 'en_word' and 
		#the Spanish word 'sp_word'
		return self.en_sp_count[en_word][sp_word] / self.en_count[en_word]


	def q(self, i, j, en_length, sp_length):
		#calculated the 'q' parameter given both the English sentence length 'en_length' and 
		#the Spanish sentence length 'sp_length'. 
		try:
			return self.c[i, j, en_length, sp_length] / self.length_c[en_length, sp_length]
		except ZeroDivisionError:
			return 0


	def calculate_delta(self, k, en_sentence, sp_index, sp_word, sp_length):
		total = 0.
		en_length = len(en_sentence)
		for i, en in enumerate(en_sentence):
			total += ( self.q(i, sp_index, en_length, sp_length) * self.t(en, sp_word) )

		for i, en in enumerate(en_sentence):
			self.delta[k, sp_index, i] = ( self.q(i, sp_index, en_length, sp_length)*self.t(en, sp_word) ) / total


	def EM_train(self, en_corpus, sp_corpus, t_file):
		en_lines = read_file(en_corpus) #5401
		sp_lines = read_file(sp_corpus) #5401
		
		self.initialize(en_lines, sp_lines, t_file)

		print "\nStart Training:",
		for it in range(5):
			print "\n\tIteration %d: ." %(it+1),
			for idx in range(len(en_lines)):
				if (idx+1)%500 == 0: print ".",

				sp_sentence = sp_lines[idx][:-1].split(" ")
				en_sentence = ("NULL "+en_lines[idx][:-1]).split(" ")
				sp_length = len(sp_sentence)
				en_length = len(en_sentence)

				for j, sp in enumerate(sp_sentence):
					self.calculate_delta(idx+1, en_sentence, j, sp, sp_length)
					for i, en in enumerate(en_sentence):
						self.en_sp_count[en][sp] += self.delta[idx+1, j, i]
						self.en_count[en] += self.delta[idx+1, sp, en]
						self.length_c[en_length, sp_length] += self.delta[idx+1, j, i]
						self.c[i, j, en_length, sp_length] += self.delta[idx+1, j, i]

		#recalculate 't'
		print "\nRecalculating Traslation Parameter: . . ."
		for en in self.en_count.keys():
			for sp in self.en_sp_count[en].keys():
				self.en_sp_count[en][sp] = self.t(en, sp)

		#recalculate 'q'
		print "Recalculating Distortion Parameter: . . ."
		for i, j, en_length, sp_length in self.c.keys():
			self.c[i, j, en_length, sp_length] = self.q(i, j, en_length, sp_length)
					

	def save(self, directory):
		#the initializing and training part takes a lot of time (400 seconds). So, I created
		#this function in order to save all member variables in a pickle file
		#to be read from.
		with open(directory, "w") as fout:
			pickle.dump( (self.en_count, self.en_sp_count, self.length_c, self.c), fout )


	def read(self, pickle_file):
		#it's used to read the pickle file that contains the member variables of the model
		print "Reading Variables: . . ."
		with open(pickle_file, "r") as fin:
			_tuple = pickle.load(fin)
		assert len(_tuple) == 4
		self.en_count = _tuple[0]
		self.en_sp_count = _tuple[1]
		self.length_c = _tuple[2]
		self.c = _tuple[3]


	def find_alignment(self, en_sentence, sp_index, sp_word, sp_length):
		"""
		This function is used to find Spanish word from the Spanish sentence 'sp_sentence' that gives 
		the maximum value of 't' with the english word 'en_word', and returns the index of the Spanish word
		"""
		global start
		lst = []

		en_sentence = ("NULL "+en_sentence).split(" ")
		en_length = len(en_sentence)
		for i, en in enumerate(en_sentence):
			lst.append( self.t(en, sp_word) * self.q(i, sp_index, en_length, sp_length) )
		tmp = sorted(lst, reverse=True)
		start = True
		return restrict(lst, tmp, sp_index, 12)


	def write_alignments(self, en_corpus, sp_corpus, out_file):
		"""This function finds the best alignment for every sentence in the corpus 'en_corpus' 
		with 'sp_corpus' and writes this alignment in the 'out_file'
		"""
		en_lines = read_file(en_corpus) #200
		sp_lines = read_file(sp_corpus) #200
		out = file(out_file, "w")

		print "Start Writing Alignments: .",
		for idx in range(len(en_lines)):
			if (idx+1)%50 == 0:
				print ".", 
			sp_sentence = sp_lines[idx][:-1].split(" ")
			sp_length = len(sp_sentence)
			for j, sp in enumerate( sp_sentence ):
				en_index = self.find_alignment(en_lines[idx][:-1], j, sp, sp_length )
				if en_index != None:
					out.write("%d %d %d\n" %(idx+1, en_index, j+1))
		out.close()

	def calculate_prob(self, en_text, sp_text):
		#This function will be used for 'p3'
		en_text = en_text.strip("\n").split(" ")
		sp_text = sp_text.strip("\n").split(" ")
		en_length = len(en_text)
		sp_length = len(sp_text)

		prob = 1.
		for i, en in enumerate(en_text):
			for j, sp in enumerate(sp_text):
				prob *= ( self.q(i, j, en_length, sp_length) * self.t(en, sp) )
		return prob




if __name__ == "__main__":
	mt = IBM_model2()
	mt.EM_train("data/corpus.en", "data/corpus.es", "outputs/t_p1.pickle")
	# mt.save("outputs/en_sp_p2.pickle")

	#To evaluate
	# mt.read("outputs/en_sp_p2.pickle")
	mt.write_alignments("data/dev.en", "data/dev.es", "outputs/p2_dev.out")



	"""
	-------------- To evaluate our model ---------------
	>>> python eval_alignment.py data/dev.key outputs/p2_dev.out
	      Type       Total   Precision      Recall     F1-Score
	===============================================================
	     total        5920     0.480        0.434        0.456
	"""


	#To test
	mt.write_alignments("data/test.en", "data/test.es", "outputs/alignment_test.p2.out")



	
	# ------------ THE FOLLOWING PART IS FOR 'P3' -------------------
	# mt = IBM_model2()
	# sp_en_model.EM_train("data/corpus.es", "data/corpus.en", "outputs/t_p3.pickle")
	# sp_en_model.save("outputs/sp_en_p3.pickle")
	# mt.read("outputs/sp_en_p3.pickle")
	# mt.write_alignments("data/dev.es", "data/dev.en", "outputs/p2_inv_dev.out")
	# mt.write_alignments("data/test.es", "data/test.en", "outputs/alignment_inv_test.p2.out")


	