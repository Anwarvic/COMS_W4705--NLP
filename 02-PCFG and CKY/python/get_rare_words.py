import pickle


with open("outputs/cfg.counts") as f:
	tag_word_tuple = set([])
	just_word = set([])
	for line in f.readlines():
		line = line.split(" ")
		if len(line) == 4 and int(line[0]) < 5:
			t = (line[-2], line[-1][:-1])
			tag_word_tuple.add(t)
			just_word.add(line[-1][:-1])


# print len(tag_word_tuple) #3815

pickle.dump([tag_word_tuple, just_word], open("data/rare_words.pickle", "w") )

