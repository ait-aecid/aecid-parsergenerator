"""This file holds the sample configuration parameters for the mainlog file.
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

input_file = 'data/in/mainlog' # Path to input log file
tree_file = 'data/out/tree.txt' # Path to output parser in tree format
parser_file = 'data/out/GeneratedParserModel.py' # Path to output parser for AMiner
templates_file = 'data/out/logTemplates.txt' # Path to output list of templates
time_stamp_length = 19 # Length of time stamp at beginning of log file that will be removed; set to -1 for no timestamp
theta1 = 0.05 # Threshold for branches [0, 1]
theta2 = 0.99 # Threshold for single child nodes [0, 1]
theta3 = 0.1 # threshold for multiple child nodes [0, 1]
theta4 = 0.0001 # Threshold for optional nodes [0, 1]
theta5 = 0.0001 # Threshold for nodes with few lines [0, 1]
theta6 = 0.001 # Threshold for optional nodes in branches [0, 1]
damping = 0.1 # Factor to increase thresholds for higher tree depths [-inf, inf]
merge_similarity = 0.8 # Minimum similarity threshold to merge similar branches [0, 1]
delimiters = [' ', '=', '<', '>'] # Delimiters for tokenizing log lines [list of single characters]
force_branch = [] # Parser tree depths where all branches are generated for all tokens, starts with 0 and also counts delimiters [list of integers]
force_var = [] # Parser tree depths where all tokens are merged to variable, starts with 0 and also counts delimiters [list of integers]
element_list_similarity = 0.66  # Minimum similarity for to lists to be merged [0, 1]
visualize = True # Produce graphical visualization [True, False]
visualization_file = 'data/out/visualization.pdf' # Path to visualization, [*.png, *.pdf]
