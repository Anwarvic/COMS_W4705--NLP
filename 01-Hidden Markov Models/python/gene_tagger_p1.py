from count_freqs import *
import pickle
from get_rare_words import get_most_tag

def emission_value(word, tag):
	total_count = counter.ngram_counts[0][(tag,)]
	return counter.emission_counts[(word, tag)] / total_count

def return_tag(d, keys, word):
	if word == "":
		return ""
	elif word in GENE_words:
		return "I-GENE"
	elif word in O_words:
		return "O"
	elif word in keys:
		O_value = emission_value(word, "O")
		GENE_value = emission_value(word, "I-GENE")
		if O_value > GENE_value:
			return "O"
		else:
			return "I-GENE"
	else:
		return "O"

def write_tags(input_file, d, keys, output):
	with open(input_file, "r") as f:
		for line in f.readlines():
			word = line[:-1]
			output.write( "%s %s\n" %(word, return_tag(d, keys, word)) )


if __name__ == "__main__":
	with open("data/rare_words.pickle", "r") as f:
		t = pickle.load(f)
		O_words = t[0]
		GENE_words = t[1]

	counter = Hmm(3)
	counter.read_counts(file("outputs/p1_count.txt","r"))

	keys=set()
	for k in counter.emission_counts.keys():
		keys.add(k[0])
	
	# FOR THE DEVELOPENT FILE
	write_tags("data/gene.dev",counter.emission_counts, keys, file("outputs/gene_dev.p1.out", "w"))
	"""
	TO EVALUATE, RUN:
		>>> python eval_gene_tagger.py data/gene.key outputs/gene_dev.p1.out
	AND THE OUTPUT WILL BE:
		Found 1667 GENEs. Expected 642 GENEs; Correct: 293.

	    	     precision      recall          F1-Score
		GENE:    0.175765       0.456386        0.253790
	"""
	#FOR THE TEST FILE 'gene.test'
	write_tags("data/gene.test",counter.emission_counts, keys, file("outputs/gene_test.p1.out", "w"))

