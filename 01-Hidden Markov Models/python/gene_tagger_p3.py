from count_freqs import classify, Hmm
from collections import deque

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
				if word in keys:
					tag = viterbi(d[0], d[1], word)
				else:
					tag = viterbi(d[0], d[1], classify(word))
				output.write( "%s %s\n" %(word, tag) )
				d.append(tag)
			else:
				output.write("\n")
				d = deque(["*", "*"], maxlen=2)





if __name__ == "__main__":
	counter = Hmm(3)
	counter.read_counts(file("outputs/p3_count.txt","r"))
	bigram_counts = counter.ngram_counts[1]
	trigram_counts = counter.ngram_counts[2]

	keys=set()
	for k in counter.emission_counts.keys():
		keys.add(k[0])

	# FOR THE DEVELOPENT FILE
	write_tags("data/gene.dev", keys, file("outputs/gene_dev.p3.out", "w"))
	"""
	TO EVALUATE, RUN:
		>>> python eval_gene_tagger.py data/gene.key outputs/gene_dev.p3.out
	AND THE OUTPUT WILL BE:
		Found 404 GENEs. Expected 642 GENEs; Correct: 214.

        		 precision      recall          F1-Score
		GENE:    0.529703       0.333333        0.409178 
	"""
	#FOR THE TEST FILE 'gene.test'
	write_tags("data/gene.test", keys, file("outputs/gene_test.p3.out", "w"))


