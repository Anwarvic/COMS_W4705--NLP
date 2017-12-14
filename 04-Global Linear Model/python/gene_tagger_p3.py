"""
This file is the same as 'gene_tagger_p2.py', the only change is the 'g' function which 
gets the local features. I have added more features.
"""





#gWORDLEN:word:V -> 1 if word length = L and tag = V
#gPREV:word:V -> 1 if prevword == word, tag=V

from collections import defaultdict, deque


def update_dict(d1, d2):
	#add the key-value pairs of 'd2' to 'd1' and returns 'd1'
	#the difference between this function and 'update' is that we sum the values of the common key.
	for k, v in d2.iteritems():
		try:
			d1[k] += v
		except KeyError:
			d1[k] = v
	return d1	


def get_suffix(word, num):
	#returns the last 'num' letters of 'word'
	assert num >= 1
	return word[-num:]

def get_prefix(word, num):
	#returns the first 'num' letters of 'word'
	assert num >= 1
	return word[:num]


def get_case(word):
	"""	
	This function returns the case of the given word. So, for example:
	>>> get_case("Anwar")
	Upper
	>>> get_case("sami")
	Lower
	>>> get_case("2")
	None
	"""
	def special_case(word):
		#This function is used to return "upper" in the names like the following name:
		#McCagu
		for i in range(1, len(word)):
			if word[i].isupper() and word[i].lower()==word[i-1]:
				if word[0].isupper():
					return "Title"

		return "None"

	if word.islower():
		return "Lower"
	elif word.istitle():
		return "Title"
	elif word.isupper():
		return "Upper"
	else:
		return special_case(word)


def is_numeric(word):
	#returns True if the word contains a number
	numbers = "1234567890"
	for ch in word:
		if ch in numbers:
			return "True"
	return "False"












class GLM():
	def __init__(self):
		self.weight_vector = defaultdict(float)


	def read_dev_corpus(self, dev_file):
		"""This function is used to read 'gene.dev' and turn them into a list of sentences.
		So, the corpus will turn into
		[... , [Sequence analysis revealed significant differences between the 5 .], ...]
		
		"""
		with open(dev_file, "r") as fin:
			lines = fin.readlines()
		sentences = []
		sen = []
		for line in lines:
			if len(line) == 1:
				sentences.append(sen)
				sen = []
			else:
				sen.append(line.strip("\n"))
		
		return sentences


	def read_train_corpus(self, train_file):
		with open(train_file, "r") as fin:
			lines = fin.readlines()
		corpus = []
		sen = []
		for line in lines:
			if len(line) == 1:
				corpus.append(sen)
				sen = []
			else:
				t = tuple( line.strip("\n").split(" ") )
				sen.append(t)

		return corpus


	#Local Feature Function
	def g(self, h, t):
		assert len(h) == 4
		d = defaultdict(float)
		t2, t1, words, i = h[0], h[1], h[2], h[3]

		d["TAG:%s:%s" %(words[i], t)] += 1.
		d["TRIGRAM:%s:%s:%s" %(t2,t1,t)] += 1.
		for j in range(1, 4):
			d["PREFIX:%s:%d:%s" %(get_prefix(words[i], j), j, t)] += 1.
			d["SUFFIX:%s:%d:%s" %(get_suffix(words[i], j), j, t)] += 1.

		# d["CASE:%s:%s" %(get_case(words[i]), t)] += 1.
		d["NUM:%s:%s" %(is_numeric(words[i]), t)]

		return d


	def local_score(self, feature_vector):
		return sum( (self.weight_vector[key] * val for key, val in feature_vector.iteritems()) )


	def viterbi(self, sentence):
		pi = {}
		pi[0, '*', '*'] = 0
		out_tags = []
		d = deque(["*", "*"], maxlen=2)
		n = len(sentence)

		for k in range(1, n+1):
			t2, t1 = d[0], d[1]
			max_score = None

			for t in ["O", "I-GENE"]:
				h = (t2, t1, sentence, k-1) #history
				feature_vector = self.g(h, t)
				pi[k, t1, t] = pi[k-1, t2, t1] + self.local_score(feature_vector)
				if pi[k, t1, t] > max_score:
					max_score = pi[k, t1, t]
					winning_tag = t
			d.append(winning_tag)
			out_tags.append(winning_tag)

		return out_tags


	def f(self, sen, tags):
		tags.insert(0, '*')
		tags.insert(0, '*')
		global_vec = defaultdict(float)

		for i, word in enumerate(sen):
			i = i+2 #to skip the two '*' at the beginning
			t2, t1, t = tags[i-2], tags[i-1], tags[i]
			h = (t2, t1, sen, i-2) #history
			update_dict( global_vec, self.g(h, t) )

		return global_vec


	def update_weight_vector(self, pred_vec1, golden_vec):
		whole_keys = set(pred_vec1.keys()).union(golden_vec.keys())
		for k in whole_keys:
			self.weight_vector[k] = self.weight_vector[k] + golden_vec[k] - pred_vec1[k]


	def train(self, train_file):
		#Training takes around '500' seconds
		print "Training:",
		corpus = self.read_train_corpus(train_file)
		for i in xrange(5):
			print "\n\tItetration %d" %i,
			
			for j, sentence in enumerate(corpus):
				if (j%3000) == 0:
					print ".",
				words, golden_tags = [t[0] for t in sentence], [t[1] for t in sentence]
				pred_tags = self.viterbi(words)
				pred_feature_vector = self.f(words, pred_tags)
				gloden_feature_vector = self.f(words, golden_tags)
				self.update_weight_vector(pred_feature_vector, gloden_feature_vector)



	def save_weight_vector(self, save_file):
		fout = file(save_file, 'w')
		for k, v in self.weight_vector.iteritems():
			fout.write("%s %f\n" %(k, v))
		fout.close()


	def read_weight_vector(self, weight_file):
		weight_file = file(weight_file, "r")
		for line in weight_file.readlines():
			line = line.strip("\n").split(" ")
			self.weight_vector[line[0]] = float(line[1])

		weight_file.close()


	def write_tags(self, dev_file, out_file):
		print "Writting Tags . . ."
		fout = file(out_file, "w")
		sentences = self.read_dev_corpus(dev_file)
		for sen in sentences:
			tags = self.viterbi(sen)
			for i, tag in enumerate(tags):
				fout.write("%s %s\n" %(sen[i], tag))
			fout.write("\n")

		fout.close()





		




if __name__ == "__main__":
	model = GLM()
	# model.train('data/gene.train')
	# model.save_weight_vector("outputs/p3_tagger.model")
	model.read_weight_vector("outputs/p3_tagger.model")
	model.write_tags("data/gene.dev", "outputs/gene_dev.p3.out")
	


	"""
	TO EVALUATE, RUN:
	>>> python eval_gene_tagger.py data/gene.key outputs/gene_dev.p3.out
	Found 743 GENEs. Expected 642 GENEs; Correct: 277.

	         precision      recall          F1-Score
	GENE:    0.372813       0.431464        0.400000
	"""
	


	#FOR THE TEST FILE 'gene.test'
	model.write_tags("data/gene.dev", "outputs/gene_test.p3.out")
	



		
		


