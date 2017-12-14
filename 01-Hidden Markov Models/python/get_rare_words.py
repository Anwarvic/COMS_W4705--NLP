from count_freqs import Hmm
import sys
import pickle

# for the following three functions:
# d MUST be a dictionary that has keys as a tuple on this form ('string', 'string') which is 'emission_counts' of course

def get_max_value(d, word):
	"""
	This function returns the max value for a given word. So, for example
	>>> get_max_value(counter.emission_counts, 'AT')
	43
	Because we have in the emission_counts dictionary two values for 'AT', one for each tag:
	  * ('AT', 'O'): 43
      * ('AT', 'I-GENE'): 8
	"""
	v1 = d[(word, 'O')]
	v2  = d[(word, 'I-GENE')]
	if v1 > v2:
		return v1
	else:
		return v2

def get_most_tag(d, word):
	"""
	This function returns the tag for a given word that has the most values. So, for example
	>>> get_most_tag(counter.emission_counts, 'AT')
	O
	Because we have in the emission_counts dictionary two values for 'AT', one for each tag:
	  * ('AT', 'O'): 43
      * ('AT', 'I-GENE'): 8
	"""
	v1 = d[(word, 'O')]
	v2  = d[(word, 'I-GENE')]
	if v1 > v2:
		return "O"
	else:
		return "I-GENE"

def get_rare_words(d):	
	temp_d = d.copy()
	O_words, GENE_words = set(), set()

	for key, value in d.iteritems():
		if value < 5 and get_max_value(temp_d, key[0]) < 5:
			if get_most_tag(temp_d, key[0]) == "O":
				O_words.add(key[0])
			else:
				GENE_words.add(key[0])

	return (O_words, GENE_words)

if __name__ == "__main__":
	counter = Hmm(3)
	counter.train(file("data/gene.train","r"), RARE=False)
	# print counter.emission_counts
	rare_words = get_rare_words(counter.emission_counts)
	# print len(rare_words[0]) #O_words = 19034
	# print len(rare_words[1]) #GENE_words = 6231

	with open("data/rare_words.pickle", "wb") as f:
		pickle.dump(rare_words, f)




