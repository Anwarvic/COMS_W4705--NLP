from count_cfg_freq import Counts
import json,  pickle
from collections import defaultdict




class pcfg:
	def __init__(self, parse_file):
		counter = Counts() 
		for l in open(parse_file):
			tree = json.loads(l)
			counter.count(tree)

		#N is 'Non-terminal'=> N[symbol] = count
		self.N = counter.nonterm
		#binary_R is 'binary Rule'  binary_R[symbol, y1, y2] = count
		self.binary_R = counter.binary
		#unary will be on this form=> unary[symbol, word] = count
		self.unary_R = counter.unary
		#V is 'vocabulary' and there are 245 words in it.
		self.V = counter.vocabulary  #245
		# pi[i, i, x] = probability
		#'pi' is a dictionary, 'i' is the index of the word in the sentence, 'x' is the non-terminal symbol
		#'pi[i, i, x]' = 0.03 where 0.03 is the probability of the word at 'i' being assigned to 'x'
		self.pi = {}
		#'bp' stands for 'back pointer' and it's a dictionary that maps the best rule and best_split to 
		#the binary table
		#'bp[i, i, x]' = [(x,word),i]
		self.bp = {}
		#binary_table is a dictionary that collects the binary rules derived from one symbol
		#binary_table['S'] =  [ ('NP', 'VP'), ('NP', 'VP+VERB'), ...]
		self.binary_table = defaultdict(set)
		self.initialize_binary_table()


	def initialize_binary_table(self):
		for sym, y1, y2 in self.binary_R:
			self.binary_table[sym].add( (y1, y2) )


	def process(self, sentence):
		"""
		this function is used to covert any word that are not in our vaocabulary into _RARE_. So, for example:
		>>> process("I care about the opera")
		I _RARE_ about the _RARE_
		"""
		assert type(sentence) == str
		output = []
		for word in sentence.strip().split(" "):
			if word not in self.V:
				output.append("_RARE_")
			else:
				output.append(word)
		return output


	def get_binary_probability(self, sym, y1, y2):
		return self.binary_R[sym, y1, y2] * 1. / self.N[sym]


	def get_unary_probability(self, sym, word):
		return self.unary_R[sym, word] * 1. / self.N[sym]


	def initialize_pi(self, sentence):
		assert type(sentence) == list
		for i, word in enumerate(sentence):
			for x in self.N.keys():
				self.pi[i, i, x] = self.get_unary_probability(x, word)
				self.bp[i, i, x] = [ (x, word), i ]



	#THIS FUNCTION I WASN'T ABLE TO IMPLEMENT, SO I STOLE IT FROM GITHUB!!!
	def cky(self, sentence):
		assert type(sentence) == str
		sentence = self.process(sentence)
		self.initialize_pi(sentence)

		# --------- End Initialization, Begin Algorithm ----------------
		
		#out_rules = set([])
		n = len(sentence)
		if n == 1:
			index = self.pi.values().index(max(self.pi.values()))
			return [self.pi.keys()[index][2].encode("ascii")]

		for step in range(0, n-1):
			for i in range(0, n-step-1):
				j = i + step + 1
				for X in self.N.keys():
					best_rule = ('', '', '')
					best_split = 0
					best_prob = 0.
					for s in range(i, j): #'s' is for 'split point'
						for Y, Z in self.binary_table[X]:
							test_prob = self.get_binary_probability(X, Y, Z) \
										* self.pi[i, s, Y] * self.pi[s+1, j, Z]

							if test_prob > best_prob:
								best_rule = (X,Y,Z)
								best_split = s
								best_prob = test_prob

					# if best_prob != 0.:
						# print best_rule, best_prob
						# out_rules.add(best_rule)
					self.pi[i, j, X] = best_prob
					self.bp[i, j, X] = [best_rule, best_split]
					# print best_prob

		# ----------- End Algorithm, Begin tree reconstruction. ---------------
		tree = self.construct_tree(self.bp, i=0, j=n-1, root=u'SBARQ')
		return tree


	def construct_tree(self, bp, i, j, root):
		try:
			rule, split = bp[i, j, root][0], bp[i, j, root][1]

			#using 'general rule' in case the root rule was corrupted
			if rule == ('', '', '') and split == 0:
				rule = ('SBARQ', 'SBARQ', '.')
				split = j-1
		except KeyError:
			print "KeyError HERE" 
			return None

		if len(rule) == 2:	#base case. 
			return [root, rule[1]]
		else:	#recursive step
			return [root,
					self.construct_tree(bp, i, split, rule[1]),
					self.construct_tree(bp, split+1, j, rule[2])]

	
	def	write_parse_tree(self, test_file, out_file):
		out = file(out_file, "w")

		line = 1
		for q in open(test_file):
			tree = self.cky(q)
			out.write(json.dumps(tree))
			out.write("\n")
			print line
			line +=1










if __name__ == "__main__":
	model = pcfg("data/parse_train_with_rare.dat")


	#parsing the whole 'parse_dev.dat' corpus takes about '115' seconds
	model.write_parse_tree(test_file="data/parse_dev.dat", \
							out_file="outputs/parse_dev.out" )
	print "DONE evaluating 'parse_dev.dat'"
	
	# d = model.cky("What other name were `` the Little Rascals << known as ?")
	# print model.bp
	# d = model.cky("How fast can a Corvette go ?")
	# print d
		
	"""
	-------------- To evaluate our model ---------------

	>>> python eval_parser.py data/parse_dev.key outputs/parse_dev.out

	      Type       Total   Precision      Recall     F1-Score
	===============================================================
	      ADJP          13     0.375        0.231        0.286
	      ADVP          20     0.400        0.100        0.160
	        NP        1081     0.627        0.657        0.642
	        PP         326     0.715        0.745        0.730
	       PRT           6     1.000        0.167        0.286
	        QP           2     0.000        0.000        0.000
	         S          45     0.500        0.178        0.262
	      SBAR          15     0.500        0.200        0.286
	     SBARQ         488     0.964        0.998        0.981
	        SQ         488     0.876        0.898        0.887
	        VP         305     0.524        0.328        0.403
	    WHADJP          43     0.796        0.907        0.848
	    WHADVP         125     0.960        0.968        0.964
	      WHNP         372     0.875        0.866        0.870
	      WHPP          10     1.000        0.600        0.750

	     total        3339     0.763        0.744        0.753

	"""
	#parsing the whole 'parse_test.dat' corpus takes about '100' seconds
	model.write_parse_tree(test_file="data/parse_test.dat", \
							out_file="outputs/parse_test.p2.out" )

	

