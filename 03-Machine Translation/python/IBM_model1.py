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
	

	ALSO, if the maximum number is less than '0.000004', it returns None.
	"""
	global start
	if start:
		length = len(original)
		if index > length:
			index = length
		start = False

	if tmp[0] < 0.000004:
		return None
	else:
		idx = original.index(tmp[0])
		if idx in range( (index - num) , (index + num+1) ):
			return idx
		else:
			return restrict(original, tmp[1:], index, num)



class IBM_model1():
	def __init__(self):
		# self.sp_count = defaultdict(int)   #won't use
		self.en_count = defaultdict(float)  #en_count['the'] = 1234
		self.en_sp_count = defaultdict(Counter) #en_sp_count['the']['le'] = 1234
		self.en_word_list = defaultdict(set) #en_word_list['the'] = ['le', 'moi', 'la', ...]
		self.delta = defaultdict(float) #is used just in 'EM_train' function


	def initialize(self, en_lines, sp_lines): #Takes around '12' seconds
		""" it initializes the following dictionaries:
		 -> en_count
		 -> en_word_list
		 -> en_sp_count: which os basically represents the parameter 't'


		"""
		assert type(en_lines) == list and type(sp_lines) == list
		print "Start Initializing: .",

		for idx in range(len(en_lines)):
			if (idx+1)%500 == 0:
				print ".",

			#'NULL' contains every single Spanish word (12002)
			for en in ("NULL "+en_lines[idx][:-1]).split(" "):
				self.en_count[en] += 1
				for sp in sp_lines[idx][:-1].split(" "):
					# self.sp_count[sp] += 1
					self.en_word_list[en].add(sp)
				
		for en in self.en_count.keys():
			for sp in self.en_word_list[en]:
				self.en_sp_count[en][sp] = 1. / len( self.en_word_list[en] )
		

	def t(self, en_word, sp_word):
		#calculated the 't' parameter given both the English word 'en_word' and 
		#the Spanish word 'sp_word'
		return self.en_sp_count[en_word][sp_word] / self.en_count[en_word]


	def calculate_delta(self, k, en_sentence, sp_index, sp_word):
		total = 0.
		for en in en_sentence:
			total += self.t(en, sp_word)
		for i, en in enumerate(en_sentence):
			self.delta[k, sp_index, i] = self.t(en, sp_word) / total


	def EM_train(self, en_corpus, sp_corpus):
		en_lines = read_file(en_corpus) #5401
		sp_lines = read_file(sp_corpus) #5401
		
		self.initialize(en_lines, sp_lines)

		print "\nStart Training:",
		for it in range(5):
			print "\n\tIteration %d: ." %(it+1),
			for idx in range(len(en_lines)):
				if (idx+1)%500 == 0: 
					print ".",

				sp_sentence = sp_lines[idx][:-1].split(" ")
				en_sentence = ("NULL "+en_lines[idx][:-1]).split(" ")
				for j, sp in enumerate(sp_sentence):
					self.calculate_delta(idx+1, en_sentence, j, sp)

					for i, en in enumerate(en_sentence):
						self.en_sp_count[en][sp] += self.delta[idx+1, j, i]
						self.en_count[en] += self.delta[idx+1, j, i]
			
		print "\nRecalculating Traslation Parameter: . . ."
		for en in self.en_count.keys():
			for sp in self.en_word_list[en]:
				self.en_sp_count[en][sp] = self.t(en, sp)


	def save(self, directory):
		#the initializing and training part takes a lot of time (320 seconds). So, I created
		#this function in order to save all member variables in a pickle file
		#to be read from later.
		with open(directory, "w") as fout:
			pickle.dump( (self.en_count, self.en_sp_count, self.en_word_list), fout )


	def read(self, pickle_file):
		#it's used to read the pickle file that contains the member variables of the model
		print "Reading Variables: . . ."
		with open(pickle_file, "r") as fin:
			_tuple = pickle.load(fin)
		self.en_count = _tuple[0]
		self.en_sp_count = _tuple[1]
		self.en_word_list = _tuple[2]


	def find_alignment(self, en_index, en_word, sp_sentence):
		"""
		This function is used to find Spanish word from the Spanish sentence 'sp_sentence' that gives 
		the maximum value of 't' with the english word 'en_word', and returns the index of the Spanish word

		# ------------------------- NOTE --------------------------------
		We should use 'sp_word' and 'en_sentence'. But, the 'dev.key' file was 
		written depending on the 'English' word alignment. So, I had to change the things around
		"""
		global start

		lst = [0.] # for the "NULL"
		for sp in sp_sentence.split(" "):
			lst.append( self.t(en_word, sp) )
		
		tmp = sorted(lst, reverse=True)
		start = True
		return restrict(lst, tmp, en_index, 12)


	def write_alignments(self, en_corpus, sp_corpus, out_file):
		"""This function finds the best alignment for every sentence in the corpus 'en_corpus' 
		with 'sp_corpus' and writes this alignment in the 'out_file'
		"""
		en_lines = read_file(en_corpus) #5401
		sp_lines = read_file(sp_corpus) #5401
		out = file(out_file, "w")

		print "Start Writing Alignments: .",
		for idx in range(len(en_lines)):
			if (idx+1)%50 == 0:
				print ".",

			for i, en in enumerate( en_lines[idx][:-1].split(" ") ):
				sp_index= self.find_alignment(i, en, sp_lines[idx][:-1])
				if sp_index != None:
					out.write("%d %d %d\n" %(idx+1, i+1, sp_index))
				
		out.close()

				








if __name__ == "__main__":
	mt = IBM_model1()
	mt.EM_train("data/corpus.en", "data/corpus.es")
	# mt.save("outputs/t_p1.pickle")

	#To evaluate
	# mt.read("outputs/t_p1.pickle")
	mt.write_alignments("data/dev.en", "data/dev.es", "outputs/p1_dev.out")
	"""
	-------------- To evaluate our model ---------------
	>>> python eval_alignment.py data/dev.key outputs/p1_dev.out
	      Type       Total   Precision      Recall     F1-Score
	===============================================================
	     total        5920     0.447        0.387        0.415
	"""

	#To test
	mt.write_alignments("data/test.en", "data/test.es", "outputs/alignment_test.p1.out")



	# ------------ THE FOLLOWING PART IS FOR 'P3' -------------------
	# mt = IBM_model1()
	# mt.EM_train("data/corpus.es", "data/corpus.en")
	# mt.save("outputs/t_p3.pickle")
	# mt.read("outputs/t_p3.pickle")
