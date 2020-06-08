input_file = 'data/in/audit.log'
tree_file = 'data/out/tree.txt'
parser_file = 'data/out/GeneratedParserModel.py'
templates_file = 'data/out/logTemplates.txt'
time_stamp_length = -1
theta1 = 0.1
theta2 = 0.9
theta3 = 0.9
theta4 = 0.0001
theta5 = 0.0001
theta6 = 0.001 # Threshold for optional nodes in branches. 
damping = 0.0
merge_similarity = 0.7
delimiters = [' ', '=']
forceBranch = []
forceVar = []
mergeSubtreesMinSimilarity = 0.45 # Threshold for the similarity of the subtrees. If the calculated similarity exceeds the threshold, the subtrees are merged
subtreeMinHeight = 1 # Number of the minimal height of the found subtrees. Mind the delimiters!
elementListSimilarity = 0.66 # Minimal similarity for two lists to be considdered of the same origin
# Optional:
visualize = False
visualization_file = 'data/out/visualization.png'
