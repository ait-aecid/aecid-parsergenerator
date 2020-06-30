"""This is the main program of the AECID-parsergenerator (AECID-PG). The
script analyzes log files and generates a parser model for the logdata-
anomaly-miner. Configuration parameters are located in PGConfig.py

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

__authors__ = ["Markus Wurzenberger", "Max Landauer", "Wolfgang Hotwagner",
               "Ernst Leierzopf", "Roman Fiedler", "Georg Hoeld"]
__contact__ = "aecid@ait.ac.at"
__copyright__ = "Copyright 2020, AIT Austrian Institute of Technology GmbH"
__credits__ = ["Florian Skopik"]
__date__ = "2020/06/26"
__deprecated__ = False
__email__ = "aecid@ait.ac.at"
__license__ = "GPLv3"
__maintainer__ = "Markus Wurzenberger"
__status__ = "Production"
__version__ = "0.0.1"

from source import LogLine, Node, GlobalID
import PGConfig
from collections import Counter


# Function that draws the graph in a hierarchical structure
def hierarchy_pos(G, root, levels=None, width=1., height=1.):
    """If there is a cycle that is reachable from root, then this will see infinite recursion.
       G: the graph
       root: the root node
       levels: a alphabet
               key: level number (starting from 0)
               value: number of nodes in this level
       width: horizontal space allocated for drawing
       height: vertical space allocated for drawing"""
    TOTAL = "total"
    CURRENT = "current"

    def make_levels(levels, node=root, current_level=0, parent=None):
        """Compute the number of nodes for each level
        """
        if current_level not in levels:
            levels[current_level] = {TOTAL: 0, CURRENT: 0}
        levels[current_level][TOTAL] += 1
        neighbors = G.neighbors(node)
        if parent is not None:
            neighbors.remove(parent)
        for neighbor in neighbors:
            levels = make_levels(levels, neighbor, current_level + 1, node)
        return levels

    def make_pos(pos, levels, node=root, current_level=0, parent=None, vert_loc=0):
        dx = 1 / levels[current_level][TOTAL]
        left = dx / 2
        pos[node] = ((left + dx * levels[current_level][CURRENT]) * width, vert_loc)
        levels[current_level][CURRENT] += 1
        neighbors = G.neighbors(node)
        if parent is not None:
            neighbors.remove(parent)
        for neighbor in neighbors:
            pos = make_pos(pos, neighbor, current_level + 1, node, vert_loc - vert_gap)
        return pos

    if levels is None:
        levels = make_levels({})
    else:
        levels = {l: {TOTAL: levels[l], CURRENT: 0} for l in levels}
    vert_gap = height / (max([l for l in levels]) + 1)
    return make_pos({}, levels)


# import log data and preprocess
input_file = PGConfig.input_file
delimiters = PGConfig.delimiters
time_stamp_length = PGConfig.time_stamp_length
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
        # line = re.sub(r'".*?"', '§', line)

        # Split at delimiters, but make delimiters also words
        word = ''
        words = []
        for c in line[time_stamp_length + 1:]:
            if c in delimiters:
                # Start new word
                if word != '':
                    words.append(word)
                words.append(c)
                word = ''
            else:
                word += c

        if word != '':
            words.append(word)

        log_line = LogLine.LogLine(line_id, line[0:time_stamp_length], line[time_stamp_length + 1:], words)
        line_id += 1
        log_line_dict[line_id] = log_line
        log_line_list.append(log_line)
        counter += 1
f.close()

print('Total amount of log lines read: ' + str(counter))

print('Build tree')
# Create root node for the tree
root = Node.Node()
root.occurrence = len(log_line_dict)
# Build tree recursively
root.build_tree(0, log_line_dict, delimiters, PGConfig.theta1, PGConfig.theta2, PGConfig.theta3, PGConfig.theta4, PGConfig.theta5,
                PGConfig.theta6, PGConfig.damping, PGConfig.force_branch, PGConfig.force_var)

# Sort fixed elements after branches because the AMiner takes the wrong path if elements are subsets of each other
print('Sort branches')
root.sort_children()

# Insert variables when branches are followed by similar paths
print('Refine tree by aggregating similar paths')
root.insert_variables(PGConfig.merge_similarity, delimiters, 0, PGConfig.force_branch)

# Create lists instead of branches if following paths are equal
print('Replace equal branches with lists')
root.insert_lists()

# Compares the element lists and expands them to enable a bigger coverage of values
print('Match list elements')
root.match_lists(PGConfig.element_list_similarity)

# Sort fixed elements after branches because the AMiner takes the wrong path if elements are subsets of each other
print('Sort branches')
root.sort_children()

# Reduce tree complexity by grouping subsequent fixed nodes into single nodes
print('Aggregate fixed word elements')
root.aggregate_sequences()

# Print Tree in textual form using Depth First Search
print('Store tree')
with open(PGConfig.tree_file, 'wb') as file:
    file.write(root.to_string(0).encode())

# Store clusters
lists = root.get_clusters()
print('Store ' + str(len(lists)) + ' clusters')

with open(str(PGConfig.templates_file), 'wb') as file:
    for template in root.get_templates(''):
        file.write((template + '\n').encode())

# Create id1
ID = GlobalID.GlobalID()

# Print some relevant tree information
print('Nodes: ' + str(root.count_nodes()))

print('Leave occurrences sum: ' + str(root.count_leave_occurrences()))

print('Optional occurrences sum: ' + str(root.count_optional_occurrences()))

counter = Counter(root.count_datatypes())
print('Datatypes: ' + str(counter))

# Build a alphabet of all characters except delimiters for the parser
alphabet = ''
for i in range(32, 127):
    alphabet += chr(i)

for delimiter in delimiters:
    alphabet = alphabet.replace(delimiter, '')
alphabet = alphabet.replace('\\', '\\\\')
alphabet = alphabet.replace('\'', '\\\'')

# Write config file using Depth First Search
print('Write parser')
config = '"""This module defines a generated parser model."""\n'
config += '\n'
config += 'from aminer.parsing import AnyByteDataModelElement\n'
config += 'from aminer.parsing import Base64StringModelElement\n'
config += 'from aminer.parsing import DateTimeModelElement\n'
config += 'from aminer.parsing import DecimalFloatValueModelElement\n'
config += 'from aminer.parsing import DecimalIntegerValueModelElement\n'
config += 'from aminer.parsing import FirstMatchModelElement\n'
config += 'from aminer.parsing import FixedDataModelElement\n'
config += 'from aminer.parsing import FixedWordlistDataModelElement\n'
config += 'from aminer.parsing import HexStringModelElement\n'
config += 'from aminer.parsing import IpAddressDataModelElement\n'
config += 'from aminer.parsing import OptionalMatchModelElement\n'
config += 'from aminer.parsing import SequenceModelElement\n'
config += 'from aminer.parsing import VariableByteDataModelElement\n'
config += '\n'
config += 'def get_model():\n'
config += '\talphabet = b\'' + alphabet + '\'\n'
config += '\tmodel = ' + root.write_config(1, ID)[1:-2] + '\n\n'
# [1:-2] removes newline and comma following last ModelElement and tabulator preceding first ModelElement
config += '\treturn model'

with open(PGConfig.parser_file, 'wb') as file:
    file.write(config.encode())

print('Parser done')

if PGConfig.visualize is True:
    import networkx as nx
    from networkx.drawing.nx_agraph import graphviz_layout
    import matplotlib.pyplot as plt

    # from graphviz import Source

    # Use networkx to plot a graphical overview of the tree
    print('Print tree as network')

    G = nx.DiGraph()
    node_connections = sorted(root.get_node_connections(), key=lambda tup: tup[1])
    G.add_edges_from(node_connections)

    mappings = root.get_node_mappings()
    mappings = dict(sorted(mappings.items()))
    mappings.update({1: root})
    
    labels = {}
    colors = []
    label_nodes = True
    for entry in mappings:
        if mappings[entry].element == '§':
            if label_nodes:
                labels[entry] = ''
            else:
                labels[entry] = str(mappings[entry].ID)

            special_datatype = False
            for dt in mappings[entry].datatype:
                if dt in ['integer', 'float', 'datetime', 'ipaddress', 'base64', 'hex']:
                    special_datatype = True

            if special_datatype:
                colors.append('lightblue')
            else:
                colors.append('lightblue')
        else:
            if label_nodes:
                labels[entry] = mappings[entry].element
            else:
                labels[entry] = str(mappings[entry].ID)

            if mappings[entry].end:
                if mappings[entry].is_list:
                    colors.append('darkgreen')
                else:
                    colors.append('green')
            else:
                if mappings[entry].is_list:
                    colors.append('darkred')
                else:
                    colors.append('lightsalmon')

    pos = graphviz_layout(G, prog='dot')

    # FOR EXIM
    colors[0] = 'lime'
    for entry in labels:
      if labels[entry] is not None and not isinstance(labels[entry], list) and labels[entry] != '':
        labels[entry] = '"' + labels[entry] + '"'
    #labels[1] = 'root'
    #labels[2] = '"Start queue\nrun: pid="'
    #labels[3] = 'pid'
    #labels[5] = '"End queue\nrun: pid="'
    #labels[6] = 'pid'
    #labels[8] = 'id'
    #labels[12] = 'name'
    #labels[14] = 'mail'
    #labels[19] = 'R'
    #labels[23] = 'mail'
    #labels[25] = 'U'
    #labels[27] = 'S'
    #labels[31] = 'id'
    # END EXIM

    labels[1] = 'root'
    labels[4] = '"USER_AUTH\nmsg=audit("'
    labels[14] = '" msg=\\\\\\\'op=PAM:\nauthentication acct="'
    labels[16] = '" exe="/usr/lib/\ndovecot/auth"\nhostname="'
    labels[20] = '" terminal=dovecot\nres=success\\\\\\\'"'
    labels[22] = '"USER_ACCT\nmsg=audit("'
    labels[32] = '" msg=\\\\\\\'op=PAM:\naccounting acct="'
    labels[34] = '" exe="/usr/lib/\ndovecot/auth"\nhostname="'
    labels[38] = '" terminal=dovecot\nres=success\\\\\\\'"'
    labels[40] = '"PROCTITLE\nmsg=audit("'
    labels[45] = '"SOCKADDR\nmsg=audit("'
    labels[50] = '"SYSCALL\nmsg=audit("'
    labels[52] = '"): arch=c000003e\nsyscall="'
    labels[90] = '" tty=(none)\nses="'
    labels[98] = '"EXECVE\nmsg=audit("'
    labels[108] = '"PATH\nmsg=audit("'

    plt.figure(1,figsize=(12,18)) 
    nx.draw(G, pos=pos, node_color=colors, labels=labels, node_size=400, font_size=12, width=0.5, arrowsize=5, with_labels=True)
    # A = to_agraph(G)
    # A.layout('dot')
    # A.draw(PGConfig.visualization_file)
    # s = Source.from_file(PGConfig.visualization_file)
    # s.view()
    plt.savefig(PGConfig.visualization_file, dpi=1000)
