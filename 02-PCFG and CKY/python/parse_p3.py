from parse_p2 import pcfg
from copy import deepcopy
from collections import defaultdict





if __name__ == "__main__":
	ver_model = pcfg("data/parse_train_vert_with_rare.dat")


	#parsing the whole 'parse_dev.dat' corpus takes about '210' seconds
	ver_model.write_parse_tree(test_file="data/parse_dev.dat", \
							out_file="outputs/parse_dev.p3.out" )
	
	print "DONE evaluating 'parse_dev.dat'"
	"""
	--------------------- To evaluate our model --------------------

	>>> python eval_parser.py data/parse_dev.key outputs/parse_dev.p3.out

	      Type       Total   Precision      Recall     F1-Score
	===============================================================
	      ADJP          13     0.231        0.231        0.231
	      ADVP          20     0.692        0.450        0.545
	        NP        1081     0.733        0.628        0.677
	        PP         326     0.743        0.684        0.712
	       PRT           6     0.286        0.333        0.308
	        QP           2     0.000        0.000        0.000
	         S          45     0.542        0.289        0.377
	      SBAR          15     0.500        0.333        0.400
	     SBARQ         488     0.545        0.998        0.705
	        SQ         488     0.827        0.754        0.789
	        VP         305     0.479        0.341        0.398
	    WHADJP          43     0.912        0.721        0.805
	    WHADVP         125     0.935        0.800        0.862
	      WHNP         372     0.942        0.823        0.878
	      WHPP          10     0.800        0.400        0.533

	     total        3339     0.702        0.699        0.701

	"""
	#parsing the whole 'parse_test.dat' corpus takes about '190' seconds
	ver_model.write_parse_tree(test_file="data/parse_test.dat", \
							out_file="outputs/parse_test.p3.out" )