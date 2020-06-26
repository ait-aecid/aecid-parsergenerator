"""This file holds the configuration parameters of the AECID-parsergenerator.

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
theta6 = 0.001  # Threshold for optional nodes in branches.
damping = 0.0
merge_similarity = 0.7
delimiters = [' ', '=']
force_branch = []
force_var = []
# Threshold for the similarity of the subtrees. If the calculated similarity exceeds the threshold, the subtrees are merged
merge_subtrees_min_similarity = 0.45
subtree_min_height = 10  # Number of the minimal height of the found subtrees. Mind the delimiters!
element_list_similarity = 0.66  # Minimal similarity for two lists to be considered of the same origin
# Optional visualization settings:
visualize = True
visualization_file = 'data/out/visualization.png'
