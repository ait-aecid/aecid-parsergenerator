#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import re
import LogLine, Node, GlobalID
from collections import Counter
# import networkx as nx
import numpy as np
# from networkx.drawing.nx_agraph import write_dot, graphviz_layout
# import matplotlib.pyplot as plt
import PGConfig
import os

# Function that draws the graph in a hierarchical structure
def hierarchy_pos(G, root, levels=None, width=1., height=1.):
    '''If there is a cycle that is reachable from root, then this will see infinite recursion.
       G: the graph
       root: the root node
       levels: a dictionary
               key: level number (starting from 0)
               value: number of nodes in this level
       width: horizontal space allocated for drawing
       height: vertical space allocated for drawing'''
    TOTAL = "total"
    CURRENT = "current"
    def make_levels(levels, node=root, currentLevel=0, parent=None):
        """Compute the number of nodes for each level
        """
        if not currentLevel in levels:
            levels[currentLevel] = {TOTAL : 0, CURRENT : 0}
        levels[currentLevel][TOTAL] += 1
        neighbors = G.neighbors(node)
        if parent is not None:
            neighbors.remove(parent)
        for neighbor in neighbors:
            levels =  make_levels(levels, neighbor, currentLevel + 1, node)
        return levels

    def make_pos(pos, node=root, currentLevel=0, parent=None, vert_loc=0):
        dx = 1/levels[currentLevel][TOTAL]
        left = dx/2
        pos[node] = ((left + dx*levels[currentLevel][CURRENT])*width, vert_loc)
        levels[currentLevel][CURRENT] += 1
        neighbors = G.neighbors(node)
        if parent is not None:
            neighbors.remove(parent)
        for neighbor in neighbors:
            pos = make_pos(pos, neighbor, currentLevel + 1, node, vert_loc-vert_gap)
        return pos
    if levels is None:
        levels = make_levels({})
    else:
        levels = {l:{TOTAL: levels[l], CURRENT:0} for l in levels}
    vert_gap = height / (max([l for l in levels])+1)
    return make_pos({})

# import log data and preprocess
input_file = PGConfig.input_file
delimiters = PGConfig.delimiters
time_stamp_length = PGConfig.time_stamp_length #15
line_id = 0
log_line_list = []
log_line_unedited_list = []
log_line_dict = {}

print('Import ' + str(input_file) + '!')

counter = 0
with open(input_file) as f:
    for line in f:
        if (line_id + 1) % 100000 == 0:
            print(str(line_id + 1) + ' lines have been imported!')

        if len(line) < 2:
            # Do not process empty log lines
            continue

        # Remove characters that should not occur in log data. According to RFC3164 only ascii code symbols 32-126
        # should occur in log data.
        line = ''.join([x for x in line if (31 < ord(x) < 127 or ord(x) == 9)])
        line = line.strip(' \t\n\r')
        log_line_unedited_list.append(line)

        # Replace text in "" with wildcards
        #line = re.sub(r'".*?"', '§', line)

        # Split at delimiters, but make delimiters also words
        word = ''
        words = []
        for c in line[time_stamp_length+1:]:
            if c in delimiters:
                # Start new word
                if word is not '':
                    words.append(word)
                words.append(c)
                word = ''
            else:
                word += c

        if word is not '':
            words.append(word)

        log_line = LogLine.LogLine(line_id, line[0:time_stamp_length], line[time_stamp_length+1:], words)
        line_id += 1
        log_line_dict[line_id] = log_line
        log_line_list.append(log_line)
        counter += 1
f.close()

print('Total amount of log lines read: ' + str(counter))

# Print Log File without special characters and annoying line feeds
#print 'Print log file'
#with open('data/out/logfile_clean.txt', 'wb') as file:
#    for line in log_line_unedited_list:
#        text = line + '\n'
#        file.write(text)
#f.close()

print('Build tree')
# Create root node for the tree
root = Node.Node()
root.occurrence = len(log_line_dict)
# Build tree recursively
root.buildTree(0, log_line_dict, delimiters, PGConfig.theta1, PGConfig.theta2, PGConfig.theta3, PGConfig.theta4, PGConfig.theta5, PGConfig.theta6, PGConfig.damping, PGConfig.forceBranch, PGConfig.forceVar)

# Sort fixed elements after branches because the AMiner takes the wrong path if elements are subsets of each other
print('Sort branches')
root.sortChildren()

subtreeList = []

# Insert variables when branches are followed by similar paths
if False: # Works, but not with other refine tree method
    print('Refine tree by aggregating similar paths')
    root.insertVariablesAndLists(PGConfig.merge_similarity, delimiters, 0, PGConfig.forceBranch)
    # root.insertVariables(PGConfig.merge_similarity, delimiters, 0, PGConfig.forceBranch)

if True: # Works
    print('Refine tree by aggregating similar paths')
    for j in range(len(root.children)-1,-1,-1):
        for i in range(j+1,len(root.children)):
            #print(i,j)
            #print('Match: %s'%root.children[i].getSubtreeMatch(root.children[j], delimiters))
            [previousMatches, similarity] = root.children[i].getSubtreeMatch(root.children[j], delimiters)
            # print('Result getSubtreeMatch: %s, %s'%(previousMatches, similarity))
            if similarity >= PGConfig.mergeSubtreesMinSimilarity:
                print('Merge subtrees: %s - %s'%(root.children[i].element, root.children[j].element))
                root.children[i].mergeSubtreeMatches(root.children[j], previousMatches, [0], [1])
                del root.children[j]

# Create lists instead of branches if following paths are equal
print('Replace equal branches with lists')
root.insertLists()

# Compares the element lists and expands them to enable a bigger coverage of values
if True: # Works
    print('Match list elements')
    root.matchLists(PGConfig.elementListSimilarity)

# Get a list which includes the nodes of common subtrees
if True: # Works
    print('Getting the list of subtrees')
    subtreeList = root.getSubtrees(PGConfig.subtreeMinHeight)

# Sort fixed elements after branches because the AMiner takes the wrong path if elements are subsets of each other
print('Sort branches')
root.sortChildren()

# Reduce tree complexity by grouping subsequent fixed nodes into single nodes
print('Aggregate fixed word elements')
root.aggregateSequences(subtreeList)

# Print Tree in textual form using Depth First Search
print('Store tree')
with open(PGConfig.tree_file, 'wb') as file:
    file.write(root.toString(0).encode())

# Store clusters
lists = root.getClusters()
print('Store ' + str(len(lists)) + ' clusters')

fileList = os.listdir(PGConfig.resultsDir)
for fileName in fileList:
    os.remove(PGConfig.resultsDir + fileName)

templateID = 0
for list in lists:
    templateID += 1
    with open(str(PGConfig.resultsDir) + 'template' + str(templateID) + '.txt', 'wb') as file:
        for lineID in list:
            file.write((str(lineID) + '\n').encode())

with open(str(PGConfig.resultsDir) + 'logTemplates.txt', 'wb') as file:
    for template in root.getTemplates(''):
        file.write((template + '\n').encode())

# Create ID
ID = GlobalID.GlobalID()

# Print some relevant tree information
print('Nodes: ' + str(root.countNodes()))

print('Leave occurrences sum: ' + str(root.countLeaveOccurrences()))

print('Optional occurrences sum: ' + str(root.countOptionalOccurrences()))

counter = Counter(root.countDatatypes())
print('Datatypes: ' + str(counter))

# Build a dictionary of all characters except delimiters for the parser
dictionary = ''
for i in range(32, 127):
    dictionary += chr(i)

for delimiter in delimiters:
    dictionary = dictionary.replace(delimiter, '')
dictionary = dictionary.replace('\\', '\\\\')
dictionary = dictionary.replace('\'', '\\\'')

# Write config file using Depth First Search
print('Write parser')
config = '"""This module defines a generated parser model."""\n'
config += '\n'
config += 'from aminer.parsing import AnyByteDataModelElement\n'
config += 'from aminer.parsing import AnyMatchModelElement\n'
config += 'from aminer.parsing import Base64StringModelElement\n'
config += 'from aminer.parsing import DateTimeModelElement\n'
config += 'from aminer.parsing import DecimalFloatValueModelElement\n'
config += 'from aminer.parsing import DecimalIntegerValueModelElement\n'
config += 'from aminer.parsing import DelimitedDataModelElement\n'
config += 'from aminer.parsing import FirstMatchModelElement\n'
config += 'from aminer.parsing import FixedDataModelElement\n'
config += 'from aminer.parsing import FixedWordlistDataModelElement\n'
config += 'from aminer.parsing import HexStringModelElement\n'
config += 'from aminer.parsing import IpAddressDataModelElement\n'
config += 'from aminer.parsing import OptionalMatchModelElement\n'
config += 'from aminer.parsing import SequenceModelElement\n'
config += 'from aminer.parsing import VariableByteDataModelElement\n'
config += '\n'
config += 'def getModel():\n'
config += '\tdict = b\'' + dictionary + '\'\n\n'
config += root.writeConfigSubtrees(ID, subtreeList) # Adding the subtrees to the config
config += '\tmodel = ' + root.writeConfig(1, ID, subtreeList)[1:-2] + '\n\n' # [1:-2] removes newline and comma following last ModelElement and tabulator preceding first ModelElement
config += '\treturn model'

with open(PGConfig.parser_file, 'wb') as file:
    file.write(config.encode())

print('Parser done')

# Use networkx to plot a graphical overview of the tree
#print('Print tree as network')

#G = nx.DiGraph()
#G.add_edges_from(root.getNodeConnections())

#mappings = root.getNodeMappings()
#mappings.update({1 : root})

#labels = {}
#colors = []
#labelNodes = False
#for entry in mappings:
#    if mappings[entry].element == '§':
#        if labelNodes == True:
#            labels[entry] = ''
#        else:
#            labels[entry] = str(mappings[entry].ID)

#        specialDatatype = False
#        for dt in mappings[entry].datatype:
#            if dt in ['integer', 'float', 'datetime', 'ipaddress', 'base64', 'hex']:
#                specialDatatype = True

#        if specialDatatype == True:
#            colors.append('lightblue')
#        else:
#            colors.append('blue')
#    else:
#        if labelNodes == True:
#            labels[entry] = mappings[entry].element
#        else:
#            labels[entry] = str(mappings[entry].ID)

#        if mappings[entry].end == True:
#            if mappings[entry].isList == True:
#                colors.append('darkgreen')
#            else:
#                colors.append('green')
#        else:
#            if mappings[entry].isList == True:
#                colors.append('darkred')
#            else:
#                colors.append('red')

#pos = graphviz_layout(G, prog='dot')
#nx.draw(G, pos=pos, node_color=colors, labels=labels, node_size=30, font_size=2, width=0.3, arrowsize=2, with_labels=True)
#plt.show()
