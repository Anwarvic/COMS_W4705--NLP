import numpy as np


def read_file(in_file):
	#this function is used to read a file, save its lines into a list
	#and close it 
	fin = file(in_file, "r")
	lst = fin.readlines()
	fin.close()
	return lst


def get_alignments(align_file, reverse=False):
	"""
	this function takes a pickle file as an input, and returns a list of alignments 
	for each sentence.
	So, given these lines:
	1 1 1 
	1 5 6
	2 3 2
	2 7 9
	...

	It should return:
	[ 
	  [(1,1), (5,6)] 
	  [(3,2), (7,9)]
	  ...
	]
	If 'reverse=True', then each tuple will be reversed, in other words (1,5) will be (5,1)
	"""
	with open(align_file, "r") as fin:
		lines = fin.readlines()
	out_lst= []
	sen_num = 1
	lst = []
	for l in lines:
		nums = l.strip("\n").split(" ")
		if reverse:
			t = (int(nums[2]), int(nums[1]))
		else:
			t = (int(nums[1]), int(nums[2]))

		if int(nums[0]) == int(sen_num):
			lst.append(t)
		else:
			sen_num =  int(nums[0])
			out_lst.append(lst)
			lst=[]
	out_lst.append(lst)
	return out_lst


def get_sentence_len(en_corpus, sp_corpus):
	"""
	This function reads two files 'en_corpus' and 'sp_corpus', and returns 
	a list of tuples, each tuple. The first number of the tuple represents the
	length of the 'en_corpus' file, and the second represents the 'sp_corpus' file.

	The output list will look like this:
	[ (15, 20)
	  (23, 27)
	  ...
	]
	This means that the first sentence of the first file contains '15' words, and the first sentence of the second file contains '20' words. 
	"""
	output = []
	en = read_file(en_corpus)
	sp = read_file(sp_corpus)

	for i in range(len(en)):
		output.append( (len(en[i].strip("\n").split(" ")),
			            len(sp[i].strip("\n").split(" ")) ) )
	return output


def has_neighbor(mat, t):
	"""
	This function takes alignment matrix 'mat' and tuple 't', and finds if the 
	tuple has any neighbors (adjacent or diagonal tuples) that has a value of one.
	If the 't' is the o, then the neighbors are the x's while . is NOT consider as a 
	neighbor.
							x  .  x
							x  o  x
							x  .  x
	"""
	t0, t1 = t
	for i in [-1, 0, 1]:
		for j in [-1, 1]:
			if t0+i <0 or t1+j<0:
				continue
			else:
				try:
					if mat[t0+i, t1+j]==1:
						return True
				except IndexError:
					continue
	return False


def rebuild(mat, tuple_lst):
	#This function is going to take each tuple out of the 'tuple_lst' and consider it as
	#matrix coordinates, and change the value at these corrdinates from 0 to 1
	for t1, t2 in tuple_lst:
		mat[t1-1,t2-1] = 1


def apply_heurestic(en, inv_en, sen_len):
	align_matrix = np.zeros(sen_len)

	#find intersection
	inter = sorted(en.intersection(inv_en))
	rebuild(align_matrix, inter)

	#find the (union difference the intersection)
	the_rest = sorted(en.symmetric_difference(inv_en), key=lambda x:x[1])
	for t in the_rest:
		if has_neighbor(align_matrix, t):
			inter.append(t)

	return inter



def write_alignment(counter, tuple_lst, out_file):
	with open(out_file, "a") as fout:
		for t in tuple_lst:
			fout.write( "%d %d %d\n" %(counter+1, t[0], t[1]) )










if __name__ == "__main__":
	en_sp_align = get_alignments("outputs/p2_dev.out")
	sp_en_align = get_alignments("outputs/p2_inv_dev.out", reverse=True)
	max_list = get_sentence_len("data/dev.en", "data/dev.es")

	open("outputs/p3_dev.out", 'w').close() #clears the output file if exists
	for i in range(len(en_sp_align)):
		en = set(en_sp_align[i])
		inv_en = set(sp_en_align[i])
		sen_len = max_list[i]
	
		golden_align = apply_heurestic(en, inv_en, sen_len)
	
		write_alignment(i, golden_align, "outputs/p3_dev.out")


	"""
	-------------- To evaluate our model ---------------
	>>> python eval_alignment.py data/dev.key outputs/p3_dev.out
	      Type       Total   Precision      Recall     F1-Score
	===============================================================
	     total        5920     0.728        0.350        0.473
	"""



	#To test
	en_sp_align = get_alignments("outputs/alignment_test.p2.out")
	sp_en_align = get_alignments("outputs/alignment_inv_test.p2.out", reverse=True)
	max_list = get_sentence_len("data/test.en", "data/test.es")

	open("outputs/alignment_test.p3.out", 'w').close()#clear the output file if exists
	for i in range(len(en_sp_align)):
		en = set(en_sp_align[i])
		inv_en = set(sp_en_align[i])
		sen_len = max_list[i]
	
		golden_align = apply_heurestic(en, inv_en, sen_len)
	
		write_alignment(i, golden_align, "outputs/alignment_test.p3.out")

	

