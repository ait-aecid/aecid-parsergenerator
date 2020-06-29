"""This file contains a class that describes a node of the parsing tree and 
provides methods to build a parser tree.

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

from collections import Counter
from dateutil.parser import parse as datetimeparse
import base64
import binascii
import socket


class Node:
    def __init__(self, optional_node_pairs=None, merge_tuple=None):
        if optional_node_pairs is None:
            optional_node_pairs = []
        if merge_tuple is None:
            merge_tuple = []
        self.element = None
        self.is_list = False  # If this is True, then self.element is a list
        self.is_variable = False
        self.parent = None
        self.occurrence = 0
        self.end = False
        self.children = []
        self.theta1 = 0
        self.ending_lines = 0
        self.datatype = ['string', 'integer', 'float', 'ipaddress']  # , 'datetime', 'base64', 'hex']
        self.ending_line_numbers = []  # Used for evaluation
        self.ID = 1
        self.optional_node_pairs = optional_node_pairs  # List of the First and the last
        self.merge_tuple = merge_tuple  # List of nodes, which are inserted into the branch after the matching has happened

    # This method returns a textual representation of the parser tree, with additional node information (line occurrences, end node, theta)
    def to_string(self, depth):
        return_string = ''

        numberstring = ''
        if len(self.ending_line_numbers) > 0:
            numberstring = ' EndingLineNumbers = ['
            for ending_linenumber in self.ending_line_numbers:
                numberstring += str(ending_linenumber) + ','
            numberstring += ']'

        if self.element is None:
            return_string += 'root (' + str(self.occurrence) + ')\n'
        else:
            if self.is_list:
                if self.end:
                    return_string += ' ' * depth + '- ' + str(self.element) + ' (' + str(self.occurrence) + ') - End (' + str(
                        self.ending_lines) + ') - Theta=' + str(self.theta1) + numberstring + '\n'
                else:
                    return_string += ' ' * depth + '- ' + str(self.element) + ' (' + str(self.occurrence) + ') - Theta=' + str(
                        self.theta1) + numberstring + '\n'
            else:
                if self.end:
                    return_string += ' ' * depth + '- ' + self.element + ' (' + str(self.occurrence) + ') - End (' + str(
                        self.ending_lines) + ') - Theta=' + str(self.theta1) + numberstring + '\n'
                else:
                    return_string += ' ' * depth + '- ' + self.element + ' (' + str(self.occurrence) + ') - Theta=' + str(
                        self.theta1) + numberstring + '\n'

        for child in self.children:
            return_string += child.to_string(depth + 1)

        return return_string

    # This method returns the total amount of nodes in the parser tree
    def count_nodes(self):
        if len(self.children) == 0:
            return 1
        elif len(self.children) == 1:
            return 1 + self.children[0].count_nodes()
        else:
            sum1 = 0
            for child in self.children:
                sum1 += child.count_nodes()
            return 1 + sum1

    # This method returns the total amount of leaves in the parser tree
    def count_leaves(self):
        if len(self.children) == 0:
            return 1
        elif len(self.children) == 1:
            return self.children[0].count_leaves()
        else:
            sum1 = 0
            for child in self.children:
                sum1 += child.count_leaves()
            return sum1

    # This method returns the total amount of variable nodes in the parser tree
    def count_variables(self):
        val = 0
        if self.is_variable:
            val = 1

        if len(self.children) == 0:
            return val
        elif len(self.children) == 1:
            return val + self.children[0].count_variables()
        else:
            sum1 = 0
            for child in self.children:
                sum1 += child.count_variables()
            return val + sum1

    # This method returns the total amount of fixed nodes in the parser tree
    def count_fixed(self):
        val = 0
        if not self.is_variable:
            val = 1

        if len(self.children) == 0:
            return val
        elif len(self.children) == 1:
            return val + self.children[0].count_variables()
        else:
            sum1 = 0
            for child in self.children:
                sum1 += child.count_variables()
            return val + sum1

    # This method returns the total amount of log lines that end in one of the leaves, i.e., all parsing log lines except the ones ending
    # before optional elements
    def count_leave_occurrences(self):
        if len(self.children) == 0:
            return self.occurrence
        elif len(self.children) == 1:
            return self.children[0].count_leave_occurrences()
        else:
            sum1 = 0
            for child in self.children:
                sum1 += child.count_leave_occurrences()
            return sum1

    # This method returns the total amount of log lines that end before optional elements, i.e., all parsing log lines except the ones
    # ending at a leave
    def count_optional_occurrences(self):
        if len(self.children) == 0:
            return 0  # Leave can never be optional
        elif len(self.children) == 1:
            if self.end:
                return self.ending_lines + self.children[0].count_optional_occurrences()
            else:
                return self.children[0].count_optional_occurrences()
        else:
            sum1 = 0
            for child in self.children:
                sum1 += child.count_optional_occurrences()

            if self.end:
                return self.ending_lines + sum1
            else:
                return sum1

    # This method returns an array of all node datatypes. A counter could be used to aggregate the result
    def count_datatypes(self):
        if self.is_variable:
            if 'ipaddress' in self.datatype:
                this_datatype = 'ipaddress'
            elif 'base64' in self.datatype:
                this_datatype = 'base64'
            elif 'hex' in self.datatype:
                this_datatype = 'hex'
            elif 'datetime' in self.datatype:
                this_datatype = 'datetime'
            elif 'integer' in self.datatype:
                this_datatype = 'integer'
            elif 'float' in self.datatype:
                this_datatype = 'float'
            else:
                this_datatype = 'string'
        else:
            this_datatype = 'fix'

        if len(self.children) == 0:
            return [this_datatype]
        elif len(self.children) == 1:
            child_datatypes = []
            child_datatypes.extend(self.children[0].count_datatypes())
            child_datatypes.append(this_datatype)
            return child_datatypes
        else:
            child_datatypes = []
            for child in self.children:
                child_datatypes.extend(child.count_datatypes())

            child_datatypes.append(this_datatype)
            return child_datatypes

    # This method aggregates two subsequent fixed nodes in order to reduce the overall amount of nodes and tree complexity
    def aggregate_sequences(self, subtree_list=None):
        if subtree_list is None:
            subtree_list = []
        if len(self.children) == 0:
            return
        elif len(self.children) == 1:
            child = self.children[0]
            if self.element is not None and not self.is_variable and not self.is_list and not self.end and not child.is_variable and\
                    not child.is_list and not any(
                    child in subtree for subtree in subtree_list) and not any(child in pair for pair in self.optional_node_pairs):
                # Merge following node into this node
                self.element = str(self.element) + str(child.element)
                self.children = child.children
                child.parent = None
                self.end = child.end
                self.ending_lines = child.ending_lines
                self.ending_line_numbers = child.ending_line_numbers
                for childchild in child.children:
                    childchild.parent = self
                self.aggregate_sequences(subtree_list)
            else:
                child.aggregate_sequences(subtree_list)
        else:
            for child in self.children:
                child.aggregate_sequences(subtree_list)

    # This method returns all edges of the parser tree
    def get_node_connections(self):
        if len(self.children) == 0:
            return []
        elif len(self.children) == 1:
            child = self.children[0]
            connection = (self.ID, child.ID)
            child_connections = child.get_node_connections()
            child_connections.append(connection)
            return child_connections
        else:
            connection_list = []
            for child in self.children:
                connection = (self.ID, child.ID)
                connection_list.append(connection)
                child_connections = child.get_node_connections()
                if child_connections is not None:
                    connection_list.extend(child_connections)
            return connection_list

    # This method retruns all leave nodes
    def get_leaves(self):
        if len(self.children) == 0:
            return [self]
        elif len(self.children) == 1:
            return self.children[0].get_leaves()
        else:
            node_list = []
            for child in self.children:
                node_list += child.get_leaves()
            return node_list

    # This method sorts the children after each branch in order to avoid AMiner issues regarding subset path elements
    def sort_children(self):
        if self.is_list:
            self.element.sort(key=lambda x: len(x), reverse=True)

        if len(self.children) == 0:
            return
        elif len(self.children) == 1:
            child = self.children[0]
            child.sort_children()
            return
        else:
            variable_index = -1
            for i in range(len(self.children)):
                if self.children[i].is_variable:
                    variable_index = i
                    break

            if variable_index != -1:
                # Sort the intern lists of nodes with listelements
                for child in self.children:
                    if child.is_list:
                        child.element = sorted(child.element, key=lambda x: (len(x), x), reverse=True)
                # Sort the children
                sorted_children1 = sorted((child for child in self.children if not child.is_variable and not child.is_list),
                                          key=lambda x: (len(x.element), x.element), reverse=True)
                sorted_children2 = sorted((child for child in self.children if not child.is_variable and child.is_list),
                                          key=lambda x: (len(x.element[0]), x.element[0]), reverse=True)
                self.children = sorted_children1 + sorted_children2 + [self.children[variable_index]]
            else:
                # Sort the intern lists of nodes with listelements
                for child in self.children:
                    if child.is_list:
                        child.element = sorted(child.element, key=lambda x: (len(x), x), reverse=True)
                # Sort the children
                sorted_children1 = sorted((child for child in self.children if not child.is_list),
                                          key=lambda x: (len(x.element), x.element), reverse=True)
                sorted_children2 = sorted((child for child in self.children if child.is_list),
                                          key=lambda x: (len(x.element[0]), x.element[0]), reverse=True)
                self.children = sorted_children1 + sorted_children2

            for child in self.children:
                child.sort_children()
            return

    # This method tries to replaces branches with lists in order to simplify the tree
    def insert_lists(self):
        if len(self.children) == 0:
            return
        elif len(self.children) == 1:
            self.children[0].insert_lists()
            return
        else:
            all_children_equal = True
            compare_child = self.children[0]
            for i in range(1, len(self.children)):
                if not compare_child.is_path_identical(self.children[i], True):
                    # Note that with this criteria, all branches must be equal to create a list. For future work, this could be extended to
                    # only some equal branches
                    all_children_equal = False
                    break

            if all_children_equal:
                # Insert a list instead of a branch
                for i in range(1, len(self.children)):
                    compare_child.merge_node(self.children[i])
                    compare_child.merge_paths(self.children[i])
                self.children = [compare_child]

            for child in self.children:
                child.insert_lists()
            return

    # This method returns a alphabet of all nodes, referenced by their IDs
    def get_node_mappings(self):
        if len(self.children) == 0:
            dictionary = {self.ID: self}
            return dictionary
        elif len(self.children) == 1:
            child = self.children[0]
            dictionary = child.get_node_mappings()
            dictionary.update({self.ID: self})
            return dictionary
        else:
            dictionary = {self.ID: self}
            for child in self.children:
                dictionary.update(child.get_node_mappings())
            return dictionary

    # This method merges two equal paths
    def merge_paths(self, node):
        self.occurrence += node.occurrence
        self.ending_lines += node.ending_lines
        # self.ending_line_numbers.extend(node.ending_line_numbers) # For Evaluation, comment out if not needed

        # Because of previous checks done by other methods, the paths are equal, i.e., they have the same number of children
        if len(self.children) == 0:
            return None
        elif len(self.children) == 1:
            return self.children[0].merge_paths(node.children[0])
        elif len(self.children) > 1:
            for i in range(0, len(self.children)):
                self.children[i].merge_paths(node.children[i])
            return

    # This method checks whether two paths are equal
    def is_path_identical(self, node, initial):
        # The sibling nodes will be transformed into a list, therefore the elements must be equal except in the initial step
        if (initial or self.element == node.element) and self.is_variable == node.is_variable and self.end == node.end and len(
                self.children) == len(node.children) and self.datatype == node.datatype:
            if len(self.children) == 0:
                return True
            elif len(self.children) == 1:
                return self.children[0].is_path_identical(node.children[0], False)
            elif len(self.children) > 1:
                result = True
                for i in range(0, len(self.children)):
                    result = result and self.children[i].is_path_identical(node.children[i], False)
                    # Requires that all branches were sorted before! (e.g., by calling sorted_children)
                return result
        else:
            return False

    # This method inserts variables when nodes are followed by mostly identical paths
    def insert_variables(self, min_similarity, delimiters, depth, force_branch):
        if len(self.children) == 0:
            # Leave node; do nothing
            return
        elif len(self.children) == 1:
            # Only one child exists; no need to insert variable
            child = self.children[0]
            child.insert_variables(min_similarity, delimiters, depth + 1, force_branch)
            return
        else:
            if depth not in force_branch:
                # Multiple children exist; try to insert variable if they are similar
                all_children_similar = True
                compare_child = self.children[0]
                for i in range(1, len(self.children)):
                    similarities = compare_child.get_path_similarities_enhanced(self.children[i], True, delimiters)
                    similarity = 0
                    if len(similarities) > 0:
                        similarity = sum(similarities) / float(len(similarities))
                    if similarity < min_similarity or any((c in self.children[i].element) for c in delimiters):
                        # Consecutive delimiters are merged during tree building, requires this kind of check
                        # Note that with this criteria, all branches must be similar to insert a variable. For future work, this could be
                        # extended to only some similar branches
                        all_children_similar = False
                        break

                # Never insert a variable when delimiters are involved
                if all_children_similar: # and compare_child.element not in delimiters:
                    # Insert a variable instead of a branch
                    compare_child.element = '§'
                    compare_child.is_variable = True
                    for i in range(1, len(self.children)):
                        compare_child.datatype = [typ for typ in compare_child.datatype if typ in self.children[i].datatype]
                        compare_child.merge_similar_paths_enhanced(self.children[i], True)
                    self.children = [compare_child]

            for child in self.children:
                child.insert_variables(min_similarity, delimiters, depth + 1, force_branch)
            return

    # This method merges two similar paths
    def merge_similar_paths(self, node, initial):
        self.occurrence += node.occurrence
        self.ending_lines += node.ending_lines

        if len(node.children) == 0:
            if len(self.children) != 0:
                self.end = True
        elif len(self.children) == 0:
            if len(node.children) != 0:
                self.end = True
                self.children = node.children
                for node in node.children:
                    node.parent = self
        elif len(self.children) == 1:
            self_child = self.children[0]
            contains_variable = False
            for node_child in node.children:
                if node_child.is_variable:
                    contains_variable = True
                    break

            if contains_variable:
                self_child.datatype = ['string']
                self_child.is_variable = True
                self_child.element = '§'
                for node_child in node.children:
                    self_child.merge_similar_paths(node_child, False)
                self.children = [self_child]
            else:
                for node_child in node.children:
                    if self_child.element == node_child.element:
                        if self_child.datatype != node_child.datatype:
                            self_child.datatype = ['string']
                        self_child.merge_similar_paths(node_child, False)
                    else:
                        self.children.append(node_child)
                        node_child.parent = self
        elif len(self.children) > 1:
            contains_variable = False
            for node_child in node.children:
                if node_child.is_variable:
                    contains_variable = True
                    break
            for self_child in self.children:
                if self_child.is_variable:
                    contains_variable = True
                    break

            if contains_variable:
                result_child = self.children[0]
                result_child.datatype = ['string']
                result_child.is_variable = True
                result_child.element = '§'
                for node_child in node.children:
                    result_child.merge_similar_paths(node_child, False)
                for i in range(1, len(self.children)):
                    result_child.merge_similar_paths(self.children[i], False)
                self.children = [result_child]
            else:
                node_childs_to_be_added = node.children[:]
                for i in range(0, len(self.children)):
                    self_child = self.children[i]
                    for j in range(0, len(node.children)):
                        node_child = node.children[j]
                        if self_child.element == node_child.element:
                            if self_child.datatype != node_child.datatype:
                                self_child.datatype = ['string']
                            self_child.merge_similar_paths(node_child, False)
                            node_childs_to_be_added.remove(node_child)
                            break
                self.children.extend(node_childs_to_be_added)
                for node_child in node_childs_to_be_added:
                    node_child.parent = self

    # This method merges two similar paths
    def merge_similar_paths_enhanced(self, node, initial):
        self.occurrence += node.occurrence
        self.ending_lines += node.ending_lines

        if node.end:
            self.end = True

        if len(node.children) == 0:
            if len(self.children) != 0:
                self.end = True
        elif len(self.children) == 0:
            if len(node.children) != 0:
                self.end = True
                self.children.extend(node.children)
                for child in node.children:
                    child.parent = self
        else:
            i = 0
            j = 0
            while i < len(self.children) and j < len(node.children):
                # Elements match
                if self.children[i].element == node.children[j].element:
                    # print('Match ' + str(self.children[i].element) + ' with ' + str(node.children[j].element))
                    self.children[i].merge_similar_paths_enhanced(node.children[j], False)
                    if self.children[i] == '§' and self.children[i].datatype != node.children[j].datatype:
                        self.children[i].datatype = [typ for typ in self.children[i].datatype if typ in node.children[j].datatype]
                    i += 1
                    j += 1

                # Match one node if possible
                elif self.children[i].element > node.children[j].element:  # Match one child of self
                    # Match the node with a variable if present
                    # print('Cannot1 match ' + str(self.children[i].element))
                    if node.children[-1].is_variable:
                        # print('Match with Variable')
                        self.children[i].merge_similar_paths_enhanced(node.children[-1], False)
                        self.children[i].datatype = [typ for typ in node.children[j].datatype if typ in node.children[-1].datatype]
                        i += 1
                    else:
                        i += 1

                else:  # Match one child of the node
                    # print('Cannot2 match ' + str(node.children[j].element))
                    # Match the node with a variable if present
                    if self.children[-1].is_variable:
                        # print('Match with Variable')
                        self.children[-1].merge_similar_paths_enhanced(node.children[j], False)
                        self.children[-1].datatype = [typ for typ in node.children[j].datatype if typ in node.children[-1].datatype]
                        j += 1
                    else:
                        self.children.append(node.children[j])
                        node.children[j].parent = self
                        j += 1

            # Match remaining nodes
            while j < len(node.children):
                # print('Match remaining node: ' + str(node.children[j].element))
                if self.children[-1].is_variable:
                    # print('Match with Variable')
                    self.children[-1].merge_similar_paths_enhanced(node.children[j], False)
                    self.children[-1].datatype = [typ for typ in node.children[j].datatype if typ in node.children[-1].datatype]
                    j += 1
                else:
                    self.children.append(node.children[j])
                    node.children[j].parent = self
                    j += 1

    # This method checks whether two paths are similar
    def get_path_similarities(self, node, initial, delimiters):
        # Initialize return_list with 1 causes that branches at the end of paths without any children always collapse to a variable
        if initial:
            return_list = [1]
        else:
            return_list = []

        if len(node.children) == 0:
            pass
        elif len(self.children) == 0:
            pass
        elif len(self.children) == 1:
            for node_child in node.children:
                return_list.extend(self.children[0].get_path_similarities(node_child, False, delimiters))
        elif len(self.children) > 1:
            last_index = -1
            for i in range(0, len(self.children)):
                if i < len(node.children):
                    return_list.extend(self.children[i].get_path_similarities(node.children[i], False, delimiters))
                    # Requires that all branches were sorted before! (e.g., by calling sorted_children)
                else:
                    return_list.extend([0] * self.children[i].get_number_of_following_nodes())
                last_index = i

            for i in range(last_index + 1, len(node.children)):
                return_list.extend([0] * node.children[i].get_number_of_following_nodes())

        # Since it is a branch, the initial elements will never match. Neither add 0 or 1 in that case
        if not initial:
            if self.is_variable or node.is_variable:
                # Variables that match with fixed elements or other variables do not say much about the similarity.
                # Neither add 0 or 1 in that case
                pass
            elif any((c in self.element) for c in delimiters):
                # Delimiters often match randomly. Neither add 0 or 1 in that case
                pass
            elif self.element == node.element:
                return_list.append(1)
            else:
                return_list.append(0)

        return return_list

    # This method checks whether two paths are similar
    def get_path_similarities_enhanced(self, node, initial, delimiters):
        # Initialize return_list with 1 causes that branches at the end of paths without any children always collapse to a variable
        if initial:
            return_list = [1]
        else:
            return_list = []

        if len(node.children) == 0:
            pass
        elif len(self.children) == 0:
            pass
        elif len(self.children) == 1:
            for node_child in node.children:
                return_list.extend(self.children[0].get_path_similarities_enhanced(node_child, False, delimiters))
        elif len(self.children) > 1:
            i = 0
            j = 0

            while i < len(self.children) and j < len(node.children):
                # Elements match
                if self.children[i].element == node.children[j].element:
                    return_list.extend(self.children[i].get_path_similarities_enhanced(node.children[j], False, delimiters))
                    # print('Match')
                    # print(i, j, self.children[i].element, node.children[j].element)
                    i += 1
                    j += 1
                # Match one node if possible

                elif self.children[i].element > node.children[j].element:  # Match one child of self
                    # Match the node with a variable if present
                    if node.children[-1].is_variable:
                        return_list.extend(self.children[i].get_path_similarities_enhanced(node.children[-1], False, delimiters))
                        # print('Match')
                        # print(i, j, self.children[i].element, node.children[-1].element)
                        i += 1
                    else:
                        return_list.extend([0] * self.children[i].get_number_of_following_nodes())
                        # print('Mismatch')
                        # print(i,j,self.children[i].element)
                        i += 1
                else:  # Match one child of the node
                    # Match the node with a variable if present
                    if self.children[-1].is_variable:
                        return_list.extend(self.children[-1].get_path_similarities_enhanced(node.children[j], False, delimiters))
                        # print('Match')
                        # print(i, j, self.children[-1].element, node.children[j].element)
                        j += 1
                    else:
                        return_list.extend([0] * node.children[j].get_number_of_following_nodes())
                        # print('Mismatch')
                        # print(i,j,node.children[j].element)
                        j += 1

        # Since it is a branch, the initial elements will never match. Neither add 0 or 1 in that case
        if not initial:
            if self.is_variable or node.is_variable:
                # Variables that match with fixed elements or other variables do not say much about the similarity.
                # Neither add 0 or 1 in that case
                pass
            elif any((c in self.element) for c in delimiters):
                # Delimiters often match randomly. Neither add 0 or 1 in that case
                pass
            elif self.element == node.element:
                return_list.append(1)
            else:
                return_list.append(0)

        return return_list

    # This method matches the lists of all list nodes
    def match_lists(self, min_similarity):
        nodes = self.get_list_nodes()  # Get all nodes which have a list as elements
        value_list = []  # List of the values of the elementlists
        indices_list = []  # List of the assigned indices of the value_list

        # initialises and merges the value- and indices_list
        for i in range(len(nodes)):
            for j in range(len(value_list)):
                if len([True for element in nodes[i].element if element in value_list[j]]) / min(len(nodes[i].element), len(
                        value_list[j])) > min_similarity:
                    indices_list.append(j)
                    for element in nodes[i].element:
                        if element not in value_list[j]:
                            value_list[j].append(element)
                    break

            # Add new values if they do not fit with any previous one
            if len(indices_list) < i + 1:
                indices_list.append(len(value_list))
                value_list.append(nodes[i].element)

        # Check if the value lists can be further merged together
        not_stable_indices = list(range(len(value_list)))
        while len(not_stable_indices) > 0:
            is_stable = True
            for i in range(1, len(value_list)):
                if i != not_stable_indices[0] and type(value_list[i]) is list and len(
                        [True for element in value_list[i] if element in value_list[not_stable_indices[0]]]) / min(
                        len(value_list[i]), len(value_list[not_stable_indices[0]])) > min_similarity:
                    # Extend the values
                    for element in value_list[i]:
                        if element not in value_list[not_stable_indices[0]]:
                            value_list[not_stable_indices[0]].append(element)

                    is_stable = False
                    value_list[i] = not_stable_indices[0]
                    if i in not_stable_indices:
                        del not_stable_indices[not_stable_indices.index(i)]
                    break
            if is_stable:
                del not_stable_indices[0]

        # Assign the new expanded lists
        for i in range(len(nodes)):
            index = indices_list[i]
            while type(value_list[index]) != list:
                index = value_list[index]
            nodes[i].element = value_list[index]

    # This method returns a list of the nodes, which are lists
    def get_list_nodes(self):
        node_list = []

        if self.is_list:
            node_list = [self]

        for child in self.children:
            node_list += child.get_list_nodes()

        return node_list

    # This function checks if the the two pairs would result in a incosistency if both would be matched.
    # Inconsistencies are pairings, which would result in a violation of the predecessor-successor like [[1], [0,1]], [[1,1], [0]]
    def is_consistent(self, pair1, pair2):
        # Cases one entry is equal
        if pair1[0] == pair2[0]:
            if pair1[1] == pair2[1]:
                return True
            else:
                return False
        elif pair1[0] == pair2[1]:
            if pair1[1] == pair2[0]:
                return True
            else:
                return False
        elif pair1[1] == pair2[0]:
            if pair1[0] == pair2[1]:
                return True
            else:
                return False
        elif pair1[1] == pair2[1]:
            if pair1[0] == pair2[0]:
                return True
            else:
                return False

        # Cases the list includes a predecessor/successor of pair1[0]
        elif pair1[0][:len(pair2[0])] == pair2[0]:
            if pair1[1][:len(pair2[1])] == pair2[1]:
                return True
            else:
                return False
        elif pair1[0][:len(pair2[1])] == pair2[1]:
            if pair1[1][:len(pair2[0])] == pair2[0]:
                return True
            else:
                return False
        elif pair1[0] == pair2[0][:len(pair1[0])]:
            if pair1[1] == pair2[1][:len(pair1[1])]:
                return True
            else:
                return False
        elif pair1[0] == pair2[1][:len(pair1[0])]:
            if pair1[1] == pair2[0][:len(pair1[1])]:
                return True
            else:
                return False

        # Cases the list includes a predecessor/successor of pair1[1] but not of pair[0]
        elif pair1[1] == pair2[0][:len(pair1[1])] or pair1[1] == pair2[1][:len(pair1[1])] or pair1[1][:len(pair2[0])] == pair2[0] or pair1[
            1][:len(pair2[1])] == pair2[1]:
            return False

        # No found predecessor/successor relation
        else:
            return True

    # This method changes the attributes of self to allow matching of both self and node
    def merge_node(self, node):
        self.datatype = [typ for typ in self.datatype if typ in node.datatype]

        # Updating variable/list element
        if node.is_variable and not self.is_variable:
            self.is_variable = True
            self.element = '§'
        elif not self.is_variable:
            if self.is_list and node.is_list:
                self.element.extend([element for element in node.element if element not in self.element])
            elif not self.is_list and node.is_list:
                self.is_list = True
                if self.element not in node.element:
                    node.element.append(self.element)
                self.element = node.element
            elif self.is_list and not node.is_list:
                if node.element not in self.element:
                    self.element.append(node.element)
            elif node.element != self.element:
                self.is_list = True
                self.element = [self.element, node.element]

        # Update line end
        if not self.end and node.end:
            self.end = True

        # Update optional node endings
        if any(node in pair for pair in self.optional_node_pairs):
            for i in range(len(self.optional_node_pairs)):
                if node == self.optional_node_pairs[i][0]:
                    self.optional_node_pairs[i][0] = self
                if node == self.optional_node_pairs[i][1]:
                    self.optional_node_pairs[i][1] = self

    def get_number_of_following_nodes(self):
        if len(self.children) == 0:
            return 1
        elif len(self.children) == 1:
            return self.children[0].get_number_of_following_nodes() + 1
        else:
            sum1 = 0
            for child in self.children:
                sum1 += child.get_number_of_following_nodes()
            return sum1 + 1

    def get_clusters(self):
        if len(self.children) == 0:
            return [self.ending_line_numbers]
        elif len(self.children) == 1:
            child = self.children[0]
            lists = child.get_clusters()

            if self.end is True:
                lists.extend([self.ending_line_numbers])

            return lists
        else:
            lists = []
            for child in self.children:
                lists.extend(child.get_clusters())
            return lists

    def get_templates(self, string):
        if self.element is not None:
            new_string = string + str(self.element)
        else:
            new_string = ''

        if len(self.children) == 0:
            return [new_string]
        elif len(self.children) == 1:
            child = self.children[0]
            list1 = []

            if self.end is True:
                list1.append(new_string)

            list1.extend(child.get_templates(new_string))
            return list1
        else:
            list1 = []
            for child in self.children:
                list1.extend(child.get_templates(new_string))
            return list1

    # This method builds the parser tree recursively
    def build_tree(self, depth, log_line_dict, delimiters, theta1, theta2, theta3, theta4, theta5, theta6, damping, force_branch,
                   force_var):
        # Theta1 is increased in every recursion, however, should be limited. If theta1 > 0.5, only 1 child would be possible
        theta1 = min(theta1, 0.49)

        self.theta1 = theta1  # Store theta1 for every node, this information is printed in the textual tree

        # End the recursion if all lines end at this node
        if len(log_line_dict) == 0:
            self.end = False
            return

        # Check for multiple consecutive delimiters and combine them
        delimiter_flag = False
        for log_line_id in log_line_dict:
            log_line = log_line_dict[log_line_id]
            if depth < len(log_line.words):
                if log_line.words[depth] in delimiters:
                    more_delimiters = True
                    delimiter_flag = True
                    while more_delimiters:
                        if depth < len(log_line.words) - 1:
                            if log_line.words[depth + 1] in delimiters:
                                log_line.words[depth] += log_line.words[depth + 1]
                                del log_line.words[depth + 1]
                            else:
                                more_delimiters = False
                        else:
                            more_delimiters = False

        words = []
        list1 = []
        list_failed_elem = []  # List of the log lines, which do not end and are not in list
        # Assemble a list of words of all log lines that pass over this node
        for log_line_id in log_line_dict:
            log_line = log_line_dict[log_line_id]
            if depth < len(log_line.words):
                words.append(log_line.words[depth])

        counter = Counter(words)

        sum_frequency = 0
        sum_frequency2 = 0  # Sum of the frequency of log lines, which did not surpass theta1
        max_count = -1
        for elem in counter:
            max_count = max(max_count, counter[elem])
            # Determine the potential succeeding nodes, i.e., words that make up a high fraction of all words
            if counter[elem] / float(len(log_line_dict)) >= theta1 or depth in force_branch:
                sum_frequency += counter[elem]  # sum_frequency is needed in Case 3
                list1.append(elem)
            else:
                sum_frequency2 += counter[elem]
                list_failed_elem.append(elem)

        new_node = Node(self.optional_node_pairs, self.merge_tuple)
        new_node.determine_datatype(words)
        special_datatype = False
        if depth not in force_branch:  # Branches can be forced also on special data types
            for dt in new_node.datatype:
                if dt in ['integer', 'float', 'datetime', 'ipaddress', 'base64', 'hex']:
                    special_datatype = True

        # Always do a variable if all branches are unique, i.e., max_count == 1
        # Also, never do a variable for delimiters
        if not delimiter_flag and (len(list1) == 0 or special_datatype or depth in force_var):
            # Case 1
            new_node.element = '§'
            new_node.is_variable = True
            new_node.parent = self
            self.children.append(new_node)
            new_dict = {}
            ending_lines = 0
            # Determine log lines passing to next node(s) that will be analyzed in the next recursion
            for log_line_id in log_line_dict:
                log_line = log_line_dict[log_line_id]
                if depth < len(log_line.words) - 1:
                    new_dict[log_line_id] = log_line  # Log line has more words, give it to next node
                elif depth == len(log_line.words) - 1:
                    ending_lines += 1
                    # Log line ends at this node
                    # new_node.ending_line_numbers.append(log_line_id)
                    # For Evaluation, comment out if not needed
            # It is a variable node, so all log lines received from parent node in previous step occur here
            new_node.occurrence = len(log_line_dict)
            if ending_lines / float(self.occurrence) >= theta4:
                new_node.end = True
                new_node.ending_lines = ending_lines
            if depth not in force_branch and len(new_dict) / float(self.occurrence) < theta5:
                # If almost all lines stop, do not make a subsequent node. This is accomplished by clearing the dict, i.e.,
                # no lines are passed to the next node
                new_dict = {}
            if new_node.occurrence != 0:
                new_node.theta1 = self.theta1 * (1 + (1 - new_node.occurrence / float(self.occurrence)) * damping)
            new_node.build_tree(depth + 1, new_dict, delimiters, new_node.theta1, theta2, theta3, theta4, theta5, theta6, damping,
                                force_branch, force_var)
        elif len(list1) == 1:
            # Case 2
            if counter[list1[0]] / float(len(log_line_dict)) >= theta2 or delimiter_flag == True:
                # Case 2 a)
                new_node.element = list1[0]
                new_node.parent = self
                self.children.append(new_node)
                new_dict = {}
                occurrences = 0
                ending_lines = 0
                for log_line_id in log_line_dict:
                    log_line = log_line_dict[log_line_id]
                    if log_line.words[depth] == list1[0]:
                        occurrences += 1
                        if depth < len(log_line.words) - 1:
                            new_dict[log_line_id] = log_line
                        elif depth == len(log_line.words) - 1:
                            ending_lines += 1
                            # new_node.ending_line_numbers.append(log_line_id)
                            # For Evaluation, comment out if not needed
                new_node.occurrence = occurrences
                if ending_lines / float(self.occurrence) >= theta4:
                    new_node.end = True
                    new_node.ending_lines = ending_lines
                if depth not in force_branch and len(new_dict) / float(self.occurrence) < theta5:
                    # If almost all lines stop, do not make a subsequent node. This is accomplished by clearing the dict, i.e.,
                    # no lines are passed to the next node
                    new_dict = {}
                if new_node.occurrence != 0:
                    new_node.theta1 = self.theta1 * (1 + (1 - new_node.occurrence / float(self.occurrence)) * damping)
                new_node.build_tree(depth + 1, new_dict, delimiters, new_node.theta1, theta2, theta3, theta4, theta5, theta6, damping,
                                    force_branch, force_var)

                if sum_frequency2 / float(len(log_line_dict)) >= theta6 and list_failed_elem[0] not in delimiters:
                    # Adding a variable node at the end of the children
                    new_node = Node(self.optional_node_pairs, self.merge_tuple)
                    new_node.determine_datatype(list_failed_elem)
                    new_node.element = '§'
                    new_node.is_variable = True
                    new_node.parent = self
                    self.children.append(new_node)
                    new_dict = {}
                    occurrences = 0
                    ending_lines = 0
                    for log_line_id in log_line_dict:
                        log_line = log_line_dict[log_line_id]
                        if len(log_line.words) > depth and log_line.words[depth] in list_failed_elem:
                            occurrences += 1
                            if depth < len(log_line.words) - 1:
                                new_dict[log_line_id] = log_line
                            elif depth == len(log_line.words) - 1:
                                ending_lines += 1
                                # new_node.ending_line_numbers.append(log_line_id)
                                # For Evaluation, comment out if not needed
                    new_node.occurrence = sum_frequency2
                    if ending_lines / float(self.occurrence) >= theta4:
                        new_node.end = True
                        new_node.ending_lines = ending_lines
                    if depth not in force_branch and len(new_dict) / float(self.occurrence) < theta5:
                        # If almost all lines stop, do not make a subsequent node. This is accomplished by clearing the dict, i.e.,
                        # no lines are passed to the next node
                        new_dict = {}
                    if new_node.occurrence != 0:
                        new_node.theta1 = self.theta1 * (1 + (1 - new_node.occurrence / float(self.occurrence)) * damping)
                    new_node.build_tree(depth + 1, new_dict, delimiters, new_node.theta1, theta2, theta3, theta4, theta5, theta6, damping,
                                        force_branch, force_var)
            else:
                # Case 2 b)
                new_node.element = '§'
                new_node.is_variable = True
                new_node.parent = self
                self.children.append(new_node)
                new_dict = {}
                ending_lines = 0
                for log_line_id in log_line_dict:
                    log_line = log_line_dict[log_line_id]
                    if depth < len(log_line.words) - 1:
                        new_dict[log_line_id] = log_line
                    elif depth == len(log_line.words) - 1:
                        ending_lines += 1
                new_node.occurrence = len(log_line_dict)
                if ending_lines / float(self.occurrence) >= theta4:
                    new_node.end = True
                    new_node.ending_lines = ending_lines
                if depth not in force_branch and len(new_dict) / float(self.occurrence) < theta5:
                    # If almost all lines stop, do not make a subsequent node. This is accomplished by clearing the dict, i.e.,
                    # no lines are passed to the next node
                    new_dict = {}
                if new_node.occurrence != 0:
                    new_node.theta1 = self.theta1 * (1 + (1 - new_node.occurrence / float(self.occurrence)) * damping)
                new_node.build_tree(depth + 1, new_dict, delimiters, new_node.theta1, theta2, theta3, theta4, theta5, theta6, damping,
                                    force_branch, force_var)
        elif len(list1) > 1:
            # Case 3
            if sum_frequency / float(len(log_line_dict)) > theta3 or delimiter_flag:
                # Case 3 a)
                for element in list1:
                    new_node = Node(self.optional_node_pairs, self.merge_tuple)
                    new_node.datatype = ['string']
                    new_node.element = element
                    new_node.parent = self
                    new_dict = {}
                    occurrences = 0
                    ending_lines = 0
                    for log_line_id in log_line_dict:
                        log_line = log_line_dict[log_line_id]
                        if len(log_line.words) > depth and log_line.words[depth] == element:
                            occurrences += 1
                            if depth < len(log_line.words) - 1:
                                new_dict[log_line_id] = log_line
                            elif depth == len(log_line.words) - 1:
                                ending_lines += 1
                    new_node.occurrence = occurrences
                    self.children.append(new_node)
                    if ending_lines / float(self.occurrence) >= theta4:
                        new_node.end = True
                        new_node.ending_lines = ending_lines
                    if depth not in force_branch and len(new_dict) / float(self.occurrence) < theta5:
                        # If almost all lines stop, do not make a subsequent node. This is accomplished by clearing the dict, i.e.,
                        # no lines are passed to the next node
                        new_dict = {}
                    if new_node.occurrence != 0:
                        new_node.theta1 = self.theta1 * (1 + (1 - new_node.occurrence / float(self.occurrence)) * damping)
                    new_node.build_tree(depth + 1, new_dict, delimiters, new_node.theta1, theta2, theta3, theta4, theta5, theta6, damping,
                                        force_branch, force_var)

                if sum_frequency2 / float(len(log_line_dict)) >= theta6 and list_failed_elem[0] not in delimiters:
                    # Adding a variable node at the end of the children
                    new_node = Node(self.optional_node_pairs, self.merge_tuple)
                    new_node.determine_datatype(list_failed_elem)
                    new_node.element = '§'
                    new_node.is_variable = True
                    new_node.parent = self
                    self.children.append(new_node)
                    new_dict = {}
                    occurrences = 0
                    ending_lines = 0
                    for log_line_id in log_line_dict:
                        log_line = log_line_dict[log_line_id]
                        if len(log_line.words) > depth and log_line.words[depth] in list_failed_elem:
                            occurrences += 1
                            if depth < len(log_line.words) - 1:
                                new_dict[log_line_id] = log_line
                            elif depth == len(log_line.words) - 1:
                                ending_lines += 1
                    new_node.occurrence = sum_frequency2
                    if ending_lines / float(self.occurrence) >= theta4:
                        new_node.end = True
                        new_node.ending_lines = ending_lines
                    if depth not in force_branch and len(new_dict) / float(self.occurrence) < theta5:
                        # If almost all lines stop, do not make a subsequent node. This is accomplished by clearing the dict, i.e.,
                        # no lines are passed to the next node
                        new_dict = {}
                    if new_node.occurrence != 0:
                        new_node.theta1 = self.theta1 * (1 + (1 - new_node.occurrence / float(self.occurrence)) * damping)
                    new_node.build_tree(depth + 1, new_dict, delimiters, new_node.theta1, theta2, theta3, theta4, theta5, theta6, damping,
                                        force_branch, force_var)
            else:
                # Case 3 b)
                new_node.element = '§'
                new_node.is_variable = True
                new_node.parent = self
                self.children.append(new_node)
                new_dict = {}
                ending_lines = 0
                for log_line_id in log_line_dict:
                    log_line = log_line_dict[log_line_id]
                    if depth < len(log_line.words) - 1:
                        new_dict[log_line_id] = log_line
                    elif depth == len(log_line.words) - 1:
                        ending_lines += 1
                new_node.occurrence = len(log_line_dict)
                if ending_lines / float(self.occurrence) >= theta4:
                    new_node.end = True
                    new_node.ending_lines = ending_lines
                if depth not in force_branch and len(new_dict) / float(self.occurrence) < theta5:
                    # If almost all lines stop, do not make a subsequent node. This is accomplished by clearing the dict, i.e.,
                    # no lines are passed to the next node
                    new_dict = {}
                if new_node.occurrence != 0:
                    new_node.theta1 = self.theta1 * (1 + (1 - new_node.occurrence / float(self.occurrence)) * damping)
                new_node.build_tree(depth + 1, new_dict, delimiters, new_node.theta1, theta2, theta3, theta4, theta5, theta6, damping,
                                    force_branch, force_var)

    # This method returns the parser model for the AMiner
    def write_config(self, depth, id1, subtree_list=None, ignore_first_subtree=False):
        # Insert a subtree if the node is root of any of the subtrees
        if subtree_list is None:
            subtree_list = []
        return_string = ''

        if not ignore_first_subtree and (
                any(self in subtree for subtree in subtree_list) or any(self == pair[1] for pair in self.optional_node_pairs)):
            subtree_number = next((i for i in range(len(subtree_list)) if self in subtree_list[i]), None)
            return_string += '\t' * depth + 'sub_tree' + str(subtree_number) + ',\n'
            return return_string

        if any(self == pair[0] for pair in self.optional_node_pairs):
            id1.value += 1
            return_string += '\t' * depth + 'AnyMatchModelElement(\'anymatch' + str(id1.value) + '\', [\n'
            depth += 1
            used_nodes = []
            for i in range(len(self.optional_node_pairs)):
                if self == self.optional_node_pairs[i][0] and self.optional_node_pairs[i][1] not in used_nodes:
                    return_string += self.optional_node_pairs[i][1].write_config(depth, id1, subtree_list)
                    used_nodes.append(self.optional_node_pairs[i][1])
            if self.element is not None and len(self.children) == 1:
                return_string += '\t' * depth + 'SequenceModelElement(\'sequence' + str(id1.value) + '\', [\n'
                depth += 1

        # Escape the escape characters
        if self.element is not None:
            if self.is_list:
                agg_elements = '['
                for elem in self.element:
                    agg_elements += 'b\'' + elem.replace('\\', '\\\\').replace('\'', '\\\'') + '\', '
                agg_elements = agg_elements[:-2]
                agg_elements += ']'
            else:
                self.element = self.element.replace('\\', '\\\\').replace('\'', '\\\'')

        # Delimited or VariableByte Datamodels should only be used when necessary, use more specific elements if possible
        variable_parser_model = 'var'
        if self.is_variable:
            id1.value += 1
            self.ID = id1.value
            if 'ipaddress' in self.datatype:
                variable_parser_model = 'IpAddressDataModelElement(\'ipaddress' + str(id1.value) + '\'),\n'
            elif 'integer' in self.datatype:
                if self.parent is not None and type(self.parent) != list and self.parent.parent is not None and type(
                        self.parent.parent) != list and self.parent.element == ':' and 'ipaddress' in self.parent.parent.datatype:
                    variable_parser_model = 'DecimalIntegerValueModelElement(\'port' + str(id1.value) + '\'),\n'
                else:
                    variable_parser_model = 'DecimalIntegerValueModelElement(\'integer' + str(
                        id1.value) + '\', value_sign_type=DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),\n'
            elif 'base64' in self.datatype:
                variable_parser_model = 'Base64StringModelElement(\'base64encoded' + str(id1.value) + '\'),\n'
            elif 'hex' in self.datatype:
                variable_parser_model = 'HexStringModelElement(\'hexstring' + str(id1.value) + '\'),\n'
            elif 'datetime' in self.datatype:
                variable_parser_model = 'DateTimeModelElement(\'datetime' + str(id1.value) + '\'),\n'
            elif 'float' in self.datatype:
                variable_parser_model = 'DecimalFloatValueModelElement(\'float' + str(
                id1.value) + '\', value_sign_type=DecimalFloatValueModelElement.SIGN_TYPE_OPTIONAL),\n'
            else:
                variable_parser_model = 'VariableByteDataModelElement(\'string' + str(id1.value) + '\', alphabet),\n'

        if len(self.children) == 0:
            # Node is a leaf node, return node info and do nothing else
            if self.element is None:
                pass
            elif self.is_list:
                id1.value += 1
                self.ID = id1.value
                return_string += '\t' * depth + 'FixedWordlistDataModelElement(\'fixed' + str(id1.value) + '\', ' + str(
                    agg_elements) + '),\n'

                if any(self == pair[0] for pair in self.optional_node_pairs):
                    if self.element is not None and len(self.children) == 1:
                        return_string = return_string[:-2] + '])]),\n'  # Closing FirstMatch and AnyMatch
                    else:
                        return_string = return_string[:-2] + ']),\n'  # Closing AnyMatch
                return return_string
            elif self.is_variable:
                return_string += '\t' * depth + variable_parser_model

                if any(self == pair[0] for pair in self.optional_node_pairs):
                    if self.element is not None and len(self.children) == 1:
                        return_string = return_string[:-2] + '])]),\n'  # Closing FirstMatch and AnyMatch
                    else:
                        return_string = return_string[:-2] + ']),\n'  # Closing AnyMatch
                return return_string
            else:
                id1.value += 1
                self.ID = id1.value
                return_string += '\t' * depth + 'FixedDataModelElement(\'fixed' + str(id1.value) + '\', b\'' + self.element + '\'),\n'

                if any(self == pair[0] for pair in self.optional_node_pairs):
                    if self.element is not None and len(self.children) == 1:
                        return_string = return_string[:-2] + '])]),\n'  # Closing FirstMatch and AnyMatch
                    else:
                        return_string = return_string[:-2] + ']),\n'  # Closing AnyMatch
                return return_string
        elif len(self.children) == 1:
            # Node has exactly 1 child

            # Start a new sequence
            if self.element is None:
                id1.value += 1
                return_string += '\t' * depth + 'SequenceModelElement(\'sequence' + str(id1.value) + '\', [\n'
                depth += 1

            if self.element is None:
                pass
            elif self.is_list:
                id1.value += 1
                self.ID = id1.value
                return_string += '\t' * depth + 'FixedWordlistDataModelElement(\'fixed' + str(id1.value) + 'b\', ' + str(
                    agg_elements) + '),\n'
            elif self.is_variable:
                return_string += '\t' * depth + variable_parser_model
            else:
                id1.value += 1
                self.ID = id1.value
                return_string += '\t' * depth + 'FixedDataModelElement(\'fixed' + str(id1.value) + '\', b\'' + self.element + '\'),\n'

            # If this is an end node, put everything that follows in an optional element
            if self.end and self.element is not None:
                id1.value += 1
                return_string += '\t' * depth + 'OptionalMatchModelElement(\'optional' + str(id1.value) + '\', \n'
                depth += 1
                id1.value += 1
                return_string += '\t' * depth + 'SequenceModelElement(\'sequence' + str(id1.value) + '\', [\n'
                depth += 1

            return_string += self.children[0].write_config(depth, id1, subtree_list)

            # End Optional Element
            if self.end and self.element is not None:
                return_string = return_string[:-2] + '])),\n'

            # End the sequence
            if self.element is None:
                return_string = return_string[:-2] + ']),\n'  # [:-2] removes newline and comma following last ModelElement

            if any(self == pair[0] for pair in self.optional_node_pairs):
                if self.element is not None and len(self.children) == 1:
                    return_string = return_string[:-2] + '])]),\n'  # Closing FirstMatch and AnyMatch
                else:
                    return_string = return_string[:-2] + ']),\n'  # Closing AnyMatch

            return return_string
        else:
            # Node has > 1 children
            # Note that its not possible that one of the children is a wildcard - there would be no branch then

            if self.element is None:
                pass
            elif self.is_list:
                id1.value += 1
                self.ID = id1.value
                return_string += '\t' * depth + 'FixedWordlistDataModelElement(\'fixed' + str(id1.value) + '\', ' + str(
                    self.element) + '),\n'
            elif self.is_variable:
                return_string += '\t' * depth + variable_parser_model
            else:
                id1.value += 1
                self.ID = id1.value
                return_string += '\t' * depth + 'FixedDataModelElement(\'fixed' + str(id1.value) + '\', b\'' + self.element + '\'),\n'
            # If this is an end node, put everything that follows in an optional element
            if self.end and self.element is not None:
                id1.value += 1
                return_string += '\t' * depth + 'OptionalMatchModelElement(\'optional' + str(id1.value) + '\', \n'
                depth += 1
                id1.value += 1
                return_string += '\t' * depth + 'SequenceModelElement(\'sequence' + str(id1.value) + '\', [\n'
                depth += 1

            # Get info about all children through recursion
            id1.value += 1
            return_string += '\t' * depth + 'FirstMatchModelElement(\'firstmatch' + str(id1.value) + '\', [\n'
            for child in self.children:
                if self.element is None or len(child.children) > 0:
                    id1.value += 1
                    depth += 1
                    return_string += '\t' * depth + 'SequenceModelElement(\'sequence' + str(id1.value) + '\', [\n'

                return_string += child.write_config(depth + 1, id1, subtree_list)

                if self.element is None or len(child.children) > 0:
                    return_string = return_string[:-2] + ']),\n'  # [:-2] removes newline and comma following last ModelElement
                    depth -= 1

            return_string = return_string[:-2] + ']),\n'  # [:-2] removes newline and comma following last ModelElement

            # End Optional Element
            if self.end and self.element is not None:
                return_string = return_string[:-2] + '])),\n'

            if any(self == pair[0] for pair in self.optional_node_pairs):
                if self.element is not None and len(self.children) == 1:
                    return_string = return_string[:-2] + '])]),\n'  # Closing FirstMatch and AnyMatch
                else:
                    return_string = return_string[:-2] + ']),\n'  # Closing AnyMatch

            return return_string

    # this method returns the assigning of the subtrees for the AMiner
    def write_config_subtrees(self, id1, subtree_list):

        self.sort_subtrees(subtree_list)

        return_string = ''
        if subtree_list:
            for i in range(len(subtree_list)):
                return_string += '\tsub_tree' + str(i) + ' = ' + 'SequenceModelElement(\'sequence' + str(id1.value) + '\', [\n' + \
                                 subtree_list[i][0].write_config(2, id1, subtree_list, ignore_first_subtree=True)[:-2] + '])\n\n'
                # [:-2] removes comma following last ModelElement and tabulator preceding first ModelElement

        return return_string + '\n'

    # Sorts the subtree_list in ascending order
    def sort_subtrees(self, subtree_list):
        subtree_list.sort(key=lambda x: x[0].subtree_height())

    # This method checks whether the words occurring at a node have a specific data type
    def determine_datatype(self, words):
        for elem in words:
            if 'float' in self.datatype and not Node.is_float(self, elem):
                self.datatype.remove('float')

            if 'integer' in self.datatype and not Node.is_integer(self, elem):
                self.datatype.remove('integer')

            if 'hex' in self.datatype and not Node.is_hex(self, elem):
                self.datatype.remove('hex')

            if 'datetime' in self.datatype and not Node.is_datetime(self, elem):
                self.datatype.remove('datetime')

            if 'base64' in self.datatype and not Node.is_base64(self, elem):
                self.datatype.remove('base64')

            if 'ipaddress' in self.datatype and not Node.is_ipaddress(self, elem):
                self.datatype.remove('ipaddress')

    def check_consistency(self):
        for child in self.children:
            if child.parent != self or not child.check_consistency():
                return False
        return True

    def update_parents(self):
        for child in self.children:
            child.update_parents()
            if child.parent != self:
                child.parent = self

    def is_float(self, s):
        try:
            if not s[-1:].isdigit():
                return False
            float(s)
            return s.replace('.', '').isdigit()
        except ValueError:
            return False

    def is_integer(self, s):
        try:
            int(s)
            if s[0] == '-':
                s = s[1:]
            return s.isdigit()
        except ValueError:
            return False

    def is_hex(self, s):
        try:
            int(s, 16)
            return True
        except ValueError:
            return False

    def is_datetime(self, s):
        try:
            datetimeparse(s)
            if ':' in s:
                return True
        except ValueError:
            return False
        except OverflowError:
            return False
        return False

    def is_base64(self, s):
        try:
            base64.decodestring(s)
            return True
        except binascii.Error:
            return False

    def is_ipaddress(self, s):
        try:
            socket.inet_pton(socket.AF_INET, s)
            return True
        except socket.error:
            try:
                socket.inet_pton(socket.AF_INET6, s)
                return True
            except socket.error:
                return False

    def __str__(self):
        """Get a string representation of this match element excluding
        the children"""
        return self.to_string(0)[1:]
