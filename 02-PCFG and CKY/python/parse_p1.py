import pickle
import json


def update_tree_with_rare(tree):
	if isinstance(tree, basestring):
		#tree can NOT be a string
		return
	
	if len(tree) == 3:
		# It is a binary rule.. Recursively count the children.
		update_tree_with_rare(tree[1])
		update_tree_with_rare(tree[2])
	
	elif len(tree) == 2:
		# It is a unary rule.
		if (tree[0], tree[1]) in tag_word_tuple:
			tree[1] = tree[1].replace(tree[1], "_RARE_")
	return tree



if __name__ == "__main__":
	lst = pickle.load(file("data/rare_words.pickle", "r"))
	tag_word_tuple = lst[0]
	# rare_words = lst[1]
	
	#for 'p2'
	out_file = file("data/parse_train_with_rare.dat", "w")
	for l in open("data/parse_train.dat", "r"):
		tree = json.loads(l)
		out_file.write(json.dumps(update_tree_with_rare(tree)) )
		out_file.write("\n")

	#for 'p3'
	out_file = file("data/parse_train_vert_with_rare.dat", "w")
	for l in open("data/parse_train_vert.dat", "r"):
		tree = json.loads(l)
		out_file.write(json.dumps(update_tree_with_rare(tree)) )
		out_file.write("\n")
		




