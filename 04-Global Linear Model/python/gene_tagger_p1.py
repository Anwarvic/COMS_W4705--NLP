from collections import defaultdict, deque
# from itertools import product



class GLM():
	def __init__(self):
		#the weight_vector will be read from 'tag.model' file
		self.weight_vector = defaultdict(float)
		self.read_weight_vector("data/tag.model")



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


	def read_weight_vector(self, weight_file):
		#This function is used to read the 'tag.model' file and turn it into a dictionary like so:
		#weight_vector['TRIGRAM:O:I-GENE:O'] = 27.0
		weight_file = file(weight_file, "r")
		for line in weight_file.readlines():
			line = line.strip("\n").split(" ")
			self.weight_vector[line[0]] = float(line[1])

		weight_file.close()


	# def GEN(self, words, i):
	# 	tuple_list = list(product(["I-GENE", "O"], repeat=3))
	# 	history = [(t[0], t[1], words, i, t[2]) for t in tuple_list]
	# 	return history


	#Local Feature Function
	def g(self, h, t):
		assert len(h) == 4
		feature_vec = defaultdict(float)
		t2, t1, words, i = h[0], h[1], h[2], h[3]

		feature_vec["TAG:%s:%s" %(words[i], t)] += 1.
		feature_vec["TRIGRAM:%s:%s:%s" %(t2,t1,t)] += 1.
		return feature_vec


	def local_score(self, feature_vector):
		return sum( (self.weight_vector[key] * val for key, val in feature_vector.iteritems()) )


	def viterbi(self, sentence):
		pi = {}
		pi[0, '*', '*'] = 0
		out_tags = []
		d = deque(["*", "*"], maxlen=2)
		n = len(sentence)

		for k in range(1, n+1): #iterate over words of a sentence
			t2, t1 = d[0], d[1]
			max_score = None

			for t in ["O", "I-GENE"]:
				h = (t2, t1, sentence, k-1) #history
				feature_vector = self.g(h , t )
				pi[k, t1, t] = pi[k-1, t2, t1] + self.local_score(feature_vector)
				if pi[k, t1, t] > max_score:
					max_score = pi[k, t1, t]
					winning_tag = t
			d.append(winning_tag)
			out_tags.append(winning_tag)

		return out_tags


	def write_tags(self, dev_file, out_file):
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
	model.write_tags("data/gene.dev", "outputs/gene_dev.p1.out")
	"""
	TO EVALUATE, RUN:
	>>> python eval_gene_tagger.py data/gene.key outputs/gene_dev.p1.out
	Found 1691 GENEs. Expected 642 GENEs; Correct: 246.
	         precision      recall          F1-Score
	GENE:    0.145476       0.383178        0.210887
	"""
	#FOR THE TEST FILE 'gene.test'
	model.write_tags("data/gene.dev", "outputs/gene_test.p1.out")
	



		
		


