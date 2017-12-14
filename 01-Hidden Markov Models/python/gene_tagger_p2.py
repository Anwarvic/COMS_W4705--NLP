from collections import deque
from count_freqs import *
import pickle

def emission_value(word, tag):
	total_count = counter.ngram_counts[0][(tag,)]
	return counter.emission_counts[(word, tag)] / total_count

def transition_value(t1, t2, t3):
	return trigram_counts[(t1, t2, t3)] / bigram_counts[(t1, t2)]

def viterbi(t1, t2, w):
	O_value = emission_value(w, "O") * transition_value(t1, t2, "O")
	GENE_value = emission_value(w, "I-GENE") * transition_value(t1, t2, "I-GENE")
	if O_value > GENE_value:
		return "O"
	else:
		return "I-GENE"

def write_tags(input_file, keys, output):
	d = deque(["*", "*"], maxlen=2)
	with open(input_file, "r") as f:
		for line in f.readlines():
			word = line[:-1]
			if len(word) != 0:
				if word in GENE_words:
					tag = "I-GENE"
				elif word in O_words:
					tag = "O"
				elif word in keys:
					tag = viterbi(d[0], d[1], word)
				else:
					tag = viterbi(d[0], d[1], "_RARE_")
				output.write( "%s %s\n" %(word, tag) )
				d.append(tag)
			else:
				output.write("\n")
				d = deque(["*", "*"], maxlen=2)





if __name__ == "__main__":
	with open("data/rare_words.pickle", "r") as f:
		t = pickle.load(f)
		O_words = t[0]
		GENE_words = t[1]

	counter = Hmm(3)
	counter.read_counts(file("outputs/p1_count.txt","r"))
	bigram_counts = counter.ngram_counts[1]
	trigram_counts = counter.ngram_counts[2]
	keys=set()
	for k in counter.emission_counts.keys():
		keys.add(k[0])

	# FOR THE DEVELOPENT FILE
	write_tags("data/gene.dev", keys, file("outputs/gene_dev.p2.out", "w"))
	"""
	TO EVALUATE, RUN:
		>>> python eval_gene_tagger.py data/gene.key outputs/gene_dev.p2.out
	AND THE OUTPUT WILL BE:
		Found 524 GENEs. Expected 642 GENEs; Correct: 248.

        		 precision      recall          F1-Score
		GENE:    0.473282       0.386293        0.425386
	"""
	#FOR THE TEST FILE 'gene.test'
	write_tags("data/gene.test", keys, file("outputs/gene_test.p2.out", "w"))

