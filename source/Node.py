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

    # This method makes a deep copy of 
    def deep_copy(self, end_node):
        new_end_node = None
        new_node = Node(self.optional_node_pairs, self.merge_tuple)

        if self.is_list:
            new_node.element = []
            new_node.element.extend(self.element)
        else:
            new_node.element = self.element

        new_node.is_list = self.is_list
        new_node.is_variable = self.is_variable
        new_node.occurrence = self.occurrence
        new_node.end = self.end
        new_node.theta1 = self.theta1
        new_node.ending_lines = self.ending_lines
        new_node.datatype = []
        new_node.datatype.extend(self.datatype)

        if self != end_node:
            for child in self.children:
                if new_end_node == None:
                    [new_child, new_end_node] = child.deep_copy(end_node)
                    new_node.children.append(new_child)
                else:
                    new_node.children.append(child.deep_copy(end_node)[0])

            for child in new_node.children:
                child.parent = new_node

        else:
            new_end_node = new_node

        return [new_node, new_end_node]

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

    # Sorts the subtree_list in ascending order
    def subtree_height(self):
        if len(self.children) == 0:
            return 0
        else:
            return max(child.subtree_height() for child in self.children) + 1

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
                    self.children[i].merge_similar_paths_enhanced(node.children[j], False)
                    if self.children[i] == '§' and self.children[i].datatype != node.children[j].datatype:
                        self.children[i].datatype = [typ for typ in self.children[i].datatype if typ in node.children[j].datatype]
                    i += 1
                    j += 1

                # Match one node if possible
                elif self.children[i].element > node.children[j].element:  # Match one child of self
                    # Match the node with a variable if present
                    if node.children[-1].is_variable:
                        self.children[i].merge_similar_paths_enhanced(node.children[-1], False)
                        self.children[i].datatype = [typ for typ in node.children[j].datatype if typ in node.children[-1].datatype]
                        i += 1
                    else:
                        i += 1

                else:  # Match one child of the node
                    # Match the node with a variable if present
                    if self.children[-1].is_variable:
                        self.children[-1].merge_similar_paths_enhanced(node.children[j], False)
                        self.children[-1].datatype = [typ for typ in node.children[j].datatype if typ in node.children[-1].datatype]
                        j += 1
                    else:
                        self.children.append(node.children[j])
                        node.children[j].parent = self
                        j += 1

            # Match remaining nodes
            while j < len(node.children):
                if self.children[-1].is_variable:
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
                    i += 1
                    j += 1
                # Match one node if possible

                elif self.children[i].element > node.children[j].element:  # Match one child of self
                    # Match the node with a variable if present
                    if node.children[-1].is_variable:
                        return_list.extend(self.children[i].get_path_similarities_enhanced(node.children[-1], False, delimiters))
                        i += 1
                    else:
                        return_list.extend([0] * self.children[i].get_number_of_following_nodes())
                        i += 1
                else:  # Match one child of the node
                    # Match the node with a variable if present
                    if self.children[-1].is_variable:
                        return_list.extend(self.children[-1].get_path_similarities_enhanced(node.children[j], False, delimiters))
                        j += 1
                    else:
                        return_list.extend([0] * node.children[j].get_number_of_following_nodes())
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

    # This function matches the parser of self with the parser of the note and returns a list of the matched nodes with a similarity score
    def get_subtree_match(self, node, delimiters):
        # Dictionary with the strings of the nodes as keys and a list of the paths to the nodes in the form [[0], [0,0,0], ...]
        element_list_1 = self.get_elements([0], delimiters)
        element_list_2 = node.get_elements([1], delimiters)

        # Match the entries with appear once in both trees
        element_list = {}
        for key in element_list_1:
            if key in element_list_2 and len(element_list_1[key]) == 1 and len(element_list_2[key]) == 1:
                element_list[key] = [[element_list_1[key][0], element_list_2[key][0]]]

        # Make a consistent set of the element_list
        previous_matches = self.match_parser_nodes({}, element_list)

        # Match the other elements of the element_list_1 and element_list_2, in the order of the smallest path list sizes
        for i in range(2, 1+max(max([0] + [len(element_list_1[k]) for k in element_list_1]),
                                max([0] + [len(element_list_2[k]) for k in element_list_2]))):
            element_list = {}
            # Find the keys, where the the smaller list is of size i, or i elements in one list and one in the other and
            # add the pairings of the path combinations.
            for key in element_list_1:
                if len(element_list_1[key]) == i and key in element_list_2 and (
                        len(element_list_2[key]) == 1 or len(element_list_2[key]) >= i):
                    element_list[key] = []
                    for j in range(len(element_list_2[key])):
                        element_list[key] += [[element_list_1[key][k], element_list_2[key][j]] for k in range(len(element_list_1[key]))]
            for key in element_list_2:
                if len(element_list_2[key]) == i and key in element_list_1 and (
                        len(element_list_1[key]) == 1 or len(element_list_1[key]) > i):
                    element_list[key] = []
                    for j in range(len(element_list_1[key])):
                        element_list[key] += [[element_list_1[key][j], element_list_2[key][k]] for k in range(len(element_list_2[key]))]

            # Match the new element_list with the consistent set previous_matches and make it consistent
            previous_matches = self.match_parser_nodes(previous_matches, element_list)

        return [previous_matches, sum([len(previous_matches[x]) for x in previous_matches])/max(1, min(sum(
                [len(element_list_1[x]) for x in element_list_1]), sum([len(element_list_2[x]) for x in element_list_2])))]

    # This function returns a Dictionary with the elements of the nodes as keys and a list of the paths to the nodes
    def get_elements(self, previous_path, delimiters):
        element_list = {} # Dictionary with the elements of the nodes as keys and a list of the paths to the nodes

        # Add the element of the node if it is no delimiter
        if str(self.element) not in delimiters and not self.is_variable:
            element_list = {str(self.element): [previous_path]}

        # Add the elements of the following nodes to the element_list
        for i in range(len(self.children)):
            element_list_2 = self.children[i].get_elements(previous_path+[i], delimiters)
            for key in element_list_2:
                if key in element_list:
                    element_list[key] += element_list_2[key]
                else:
                    element_list[key] = element_list_2[key]

        return element_list

    # This function gets a consistent set of matches of two trees and a set of new matches.
    # The function returns a consistent set of matches which includes the previous matches and the highest number of possible matches,
    # such that the set stays consistent
    def match_parser_nodes(self, previous_matches, new_matches):
        # Check if new matches are inconsistent to existing ones
        keys = list(new_matches.keys())
        if previous_matches != {}:
            for i in range(len(keys)-1, -1, -1):
                for i_1 in range(len(new_matches[keys[i]])-1, -1, -1):
                    break_2 = False
                    for key_2 in previous_matches:
                        if break_2:
                            break_2 = False
                            break
                        for i_2 in range(len(previous_matches[key_2])-1, -1, -1):
                            if not self.is_consistent(new_matches[keys[i]][i_1], previous_matches[key_2][i_2]):
                                del new_matches[keys[i]][i_1]
                                break_2 = True
                                break
                if new_matches[keys[i]] == []:
                    del new_matches[keys[i]]
                    del keys[i]

        # Check if new matches are inconsistent to each other
        inconsistent_matches = []
        for i in range(len(keys)):
            for j in range(i, len(keys)):
                for i_2 in range(len(new_matches[keys[i]])):
                    for j_2 in range(len(new_matches[keys[j]])):
                        if not self.is_consistent(new_matches[keys[i]][i_2], new_matches[keys[j]][j_2]):
                            inconsistent_matches.append([i, j, i_2, j_2])

        # Find minimal Indices so that every element is included at least once in every set
        inconsistent_items = []
        while len(inconsistent_matches) != 0:
            count_list = [[0 for j in range(len(new_matches[keys[i]]))] for i in range(len(keys))]
            for i in range(len(inconsistent_matches)):
                count_list[inconsistent_matches[i][0]][inconsistent_matches[i][2]] += 1
                count_list[inconsistent_matches[i][1]][inconsistent_matches[i][3]] += 1

            # This section searches for a item to remove from the inconsistent_matches and takes the length of the mismatching into account
            # ([[0],[1]] < [[0,1],[1,1,1,1,1,1,1,1,1]])
            max_count = 0
            tmp_index = 0
            tmp_index_2 = 0
            for i in range(len(count_list)):
                for i_2 in range(len(count_list[i])):
                    if count_list[i][i_2] > max_count:
                        max_count = count_list[i][i_2]
                        tmp_index = i
                        tmp_index_2 = i_2
                    elif count_list[i][i_2] == max_count and \
                            abs(len(new_matches[keys[i]][i_2][0])-len(new_matches[keys[i]][i_2][1])) > \
                            abs(len(new_matches[keys[tmp_index]][tmp_index_2][0])-len(new_matches[keys[tmp_index]][tmp_index_2][1])):
                        tmp_index = i
                        tmp_index_2 = i_2
                    elif count_list[i][i_2] == max_count and \
                            abs(len(new_matches[keys[i]][i_2][0])-len(new_matches[keys[i]][i_2][1])) == \
                            abs(len(new_matches[keys[tmp_index]][tmp_index_2][0])-len(new_matches[keys[tmp_index]][tmp_index_2][1])) and \
                            max(len(new_matches[keys[i]][i_2][0]), len(new_matches[keys[i]][i_2][1])) > \
                            max(len(new_matches[keys[tmp_index]][tmp_index_2][0]), len(new_matches[keys[tmp_index]][tmp_index_2][1])):
                        tmp_index = i
                        tmp_index_2 = i_2
            inconsistent_items.append([tmp_index, tmp_index_2])

            inconsistent_matches = [match for match in inconsistent_matches if (
                    (match[0] != inconsistent_items[-1][0] or match[2] != inconsistent_items[-1][1]) and
                    (match[1] != inconsistent_items[-1][0] or match[3] != inconsistent_items[-1][1]))]

        inconsistent_items.sort(key = lambda x: x[1], reverse = True)

        for i in range(len(inconsistent_items)):
            del new_matches[keys[inconsistent_items[i][0]]][inconsistent_items[i][1]]

        for key in new_matches:
            if key in previous_matches:
                previous_matches[key] += new_matches[key]
            elif len(new_matches[key]) != 0:
                previous_matches[key] = new_matches[key]

        return previous_matches

    # This method matches the lists of all list nodes
    def match_lists(self, min_similarity):
        nodes = self.get_list_nodes()  # Get all nodes which have a list as elements
        value_list = []  # List of the values of the element_lists
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

    # This function merges nodes if the following branches are simmilar
    def merge_similar_branches(self, delimiters, merge_subtrees_min_similarity):
        for j in range(len(self.children)-1,-1,-1):
            for i in range(len(self.children)-1,j,-1):
                [matches, similarity] = self.children[i].get_subtree_match(self.children[j], delimiters)
                if similarity >= merge_subtrees_min_similarity:
                    self.children[j].merge_subtree_matches(self.children[i], matches, [0], [1])
                    del self.children[i]
            if len(self.children[j].children) > 0:
                self.children[j].merge_similar_branches(delimiters, merge_subtrees_min_similarity)

    # This function merges the node self with node. The set of the matches includes the matched nodes in the subtrees.
    def merge_subtree_matches(self, node, matches, pos_0, pos_1, first_merge = True):
        # Get the pairs without the element-values
        if type(matches) == dict:
            new_previous_matches = []
            for key in matches:
                new_previous_matches += matches[key]
            matches = new_previous_matches
            matches.sort()

        if matches == []:
            self.merge_subtrees(node)

        else: # matches != []
            [next_matches, next_Subtrees] = self.next_matches(matches, pos_0, pos_1)

            for i in range(len(next_matches)):
                self.merge_to_single_path(node, next_matches[i], next_matches, pos_0, pos_1)
                self.follow_path(next_matches[i][0][len(pos_0):]).merge_subtree_matches(
                        node.follow_path(next_matches[i][1][len(pos_1):]), next_Subtrees[i], next_matches[i][0], next_matches[i][1],
                        first_merge = False)

            if first_merge:
                # Merge end_nodes and adding the optional nodes of node to self
                for tupple in self.merge_tuple:

                    if tupple[1] in tupple[0].children:
                        tupple[1].merge_node(tupple[4])

                        [new_node, new_end_node] = tupple[2].deep_copy(tupple[3])
                        tupple[2] = new_node
                        tupple[3] = new_end_node

                        # Check cases that can appear if the paths are not disjunkt
                        if tupple[2] not in tupple[0].children:
                            tupple[3].children = [tupple[1]]
                            tupple[1].parent = tupple[3]
                        else:
                            tupple[3].children.append(tupple[1])
                            tupple[1].parent = tupple[3]

                        del tupple[0].children[tupple[0].children.index(tupple[1])]

                        if tupple[2] not in tupple[0].children:
                            tupple[0].children.append(tupple[2])
                            tupple[2].parent = tupple[0]

                        # Check if the optional part is already present in optional_node_pairs
                        if [tupple[2], tupple[1]] not in self.optional_node_pairs:
                            node.optional_node_pairs.append([tupple[2], tupple[1]])
                self.merge_tuple.clear()

        return

    # This method merges two nodes without matches and merges the variable nodes if present.
    def merge_subtrees(self, node):
        self.merge_node(node)

        if len(self.children) == 0:
            self.end = True

        for i in range(len(node.children)):
            if node.children[i].is_variable:
                contains_variable = False
                for child in self.children:
                    if child.is_variable:
                        contains_variable = True
                        child.merge_subtrees(node.children[i])
                        break
                if not contains_variable:
                    self.children.append(node.children[i])
                    node.children[i].parent = self
            elif len(self.children) == 1 and len(node.children) == 1 and self.children[0].element == node.children[0].element:
                self.children[0].merge_subtrees(node.children[0])
            else:
                self.children.append(node.children[i])
                node.children[i].parent = self

    # This method returns a list, which contains the next matches and the corresponding matches in their subtrees
    def next_matches(self, matches, pos_0, pos_1):

        if len(matches) == 0 or len(matches) == 1 and matches[0][0] == pos_0:
            return [[], []]

        if matches[0][0] == pos_0:
            del matches[0]

        next_matches = [matches[0]] # Next matches
        next_Subtrees = [[]] # List of the subtrees of the nodes to the next matches

        for i in range(1,len(matches)):
            if next_matches[-1][0] != matches[i][0][:len(next_matches[-1][0])]:
                next_matches.append(matches[i])
                next_Subtrees.append([])
            else:
                next_Subtrees[-1].append(matches[i])

        return [next_matches, next_Subtrees]

    # This method returns the successor node, which is reached after following the path
    def follow_path(self, path):
        node = self
        for i in range(len(path)):
            node = node.children[path[i]]
        return node

    # This method merges two paths into one and adds the additional branches
    def merge_to_single_path(self, node, pair, next_matches, pos_0, pos_1):

        # Merge nodes
        self.merge_node(node)

        # Add not matched branch children of node to self
        for i in range(len(node.children)):
            if not any(pos_1+[i] == pos[1][:len(pos_1)+1] for pos in next_matches) and node.children[i] not in self.children:
                if node.children[i].is_variable:
                    contains_variable = False
                    for child in self.children:
                        if child.is_variable:
                            contains_variable = True
                            child.merge_subtrees(node.children[i])
                            break
                    if not contains_variable:
                        self.children.append(node.children[i])
                        node.children[i].parent = self

                else:
                    self.children.append(node.children[i])
                    node.children[i].parent = self

        tmp_self = self
        tmp_node = node

        for i in range(min(len(pair[0])-len(pos_0), len(pair[1])-len(pos_1))-1):
            tmp_self = tmp_self.follow_path([pair[0][len(pos_0)+i]])
            tmp_node = tmp_node.follow_path([pair[1][len(pos_1)+i]])

            # Merge the nodes because they lie on the matched path
            tmp_self.merge_node(tmp_node)

            # Add not matched branch children
            for j in range(len(tmp_node.children)):
                if not any(pair[1][:len(pos_1)+i+1]+[j] == tmp_pos[1][:len(pos_1)+i+2] for tmp_pos in next_matches) and \
                        tmp_node.children[j] not in tmp_self.children:

                    if tmp_node.children[j].is_variable:
                        contains_variable = False
                        for child in tmp_self.children:
                            if child.is_variable:
                                contains_variable = True
                                child.merge_subtrees(tmp_node.children[j])
                                break
                        if not contains_variable:
                            tmp_self.children.append(tmp_node.children[j])
                            tmp_node.children[j].parent = tmp_self

                    else:
                        tmp_self.children.append(tmp_node.children[j])
                        tmp_node.children[j].parent = tmp_self

        if len(pair[0])-len(pos_0) < len(pair[1])-len(pos_1):
            # Appending the tupple of certain nodes to be able to later insert the optional part into the parser
            self.merge_tuple.append([self.follow_path(pair[0][len(pos_0):-1]), self.follow_path(pair[0][len(pos_0):]), \
                                     node.follow_path(pair[1][len(pos_1):len(pos_1)+len(pair[0])-len(pos_0)]),
                                     node.follow_path(pair[1][len(pos_1):-1]), node.follow_path(pair[1][len(pos_1):])])

        elif len(pair[0])-len(pos_0) > len(pair[1])-len(pos_1):
            if [self.follow_path(pair[0][len(pos_0):len(pos_0)+len(pair[1])-len(pos_1)]), self.follow_path(pair[0][len(pos_0):])] \
                    not in self.optional_node_pairs:
                self.optional_node_pairs.append([self.follow_path(pair[0][len(pos_0):len(pos_0)+len(pair[1])-len(pos_1)]),
                                                 self.follow_path(pair[0][len(pos_0):])])

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

    # This function finds subtrees in the parser and return the IDs of the root nodes
    # Parseretrees with multiple parents are not supported (Remove matched_subtree_indices + Save number of includions in subtrees)
    def get_subtrees(self, min_height):
        subtree_list = [node for node in self.get_leaves()]
        tmp_dict = {}

        tmp_index = 0
        tmp_list = [] # List of the list elements
        tmp_node_list = [] # List of the corresponding nodes
        for i in range(len(subtree_list)):
            if type(subtree_list[i].element) == list:
                if subtree_list[i].element in tmp_list:
                    tmp_node_list[tmp_list.index(subtree_list[i].element)].append(i)
                else:
                    tmp_list.append(subtree_list[i].element)
                    tmp_node_list.append([i])
            else:
                if subtree_list[i].element in tmp_dict:
                    tmp_dict[subtree_list[i].element].append(i)
                else:
                    tmp_dict[subtree_list[i].element] = [i]

        # List of roots of equal subtrees
        subtree_list = [[subtree_list[k] for k in tmp_dict[key]] for key in tmp_dict] + [
                [subtree_list[k] for k in tmp_node_list[k_2]] for k_2 in range(len(tmp_node_list))]
        height_list = [0, len(subtree_list)]

        while True:
            for i in range(height_list[-2], height_list[-1]):
                # List of the indices of the subtreetypes, which have already been matched
                matched_subtree_indices = []
                for j in range(len(subtree_list[i])):

                    # Check if the subtree has already been matched
                    if j in matched_subtree_indices:
                        continue

                    children_index = []
                    all_children_matched = True
                    for child in subtree_list[i][j].parent.children:
                        if child == subtree_list[i][j]:
                            children_index.append(i)
                            continue

                        child_match = False
                        for i_2 in range(height_list[-1]):
                            if child in subtree_list[i_2]:
                                child_match = True
                                children_index.append(i_2)
                                break

                        if not child_match:
                            all_children_matched = False
                            break

                    # Search for another subtree, which is equal to the indiced subtree of self.parent
                    if all_children_matched:
                                
                        indices_list = [] # List of the indices, which are used to remove the other matched subtrees
                        parents_list = [subtree_list[i][j].parent] # List of the parents of matched subtrees

                        for j_2 in range(j+1, len(subtree_list[i])):
                            # Check if the subtree has already been matched
                            if j_2 in matched_subtree_indices:
                                continue

                            if subtree_list[i][j].parent.element == subtree_list[i][j_2].parent.element and \
                                    len(subtree_list[i][j].parent.children) == len(subtree_list[i][j_2].parent.children):
                                all_children_matched = True

                                # Checks if the children are the same subtrees. This works because the braches are ordered
                                for i_2 in range(len(subtree_list[i][j_2].parent.children)):
                                    if subtree_list[i][j_2].parent.children[i_2] == subtree_list[i][j_2]:
                                        continue
                                    elif subtree_list[i][j_2].parent.children[i_2] in subtree_list[children_index[i_2]]:
                                        continue
                                    else:
                                        all_children_matched = False
                                        break

                                # If the subtree matches the reference, add the neighbors to the indices_list
                                if all_children_matched:
                                    parents_list.append(subtree_list[i][j_2].parent)
                                    matched_subtree_indices.append(j_2)

                                    for i_2 in range(len(subtree_list[i][j_2].parent.children)):
                                        if i != children_index[i_2]:
                                            indices_list.append([children_index[i_2],subtree_list[children_index[i_2]].index(
                                                    subtree_list[i][j_2].parent.children[i_2])])

                        if len(parents_list) > 1:
                            matched_subtree_indices.append(j)

                            # check if the node is an variable and updates the datatype
                            if parents_list[0].is_variable:
                                tmp_list = [typ for typ in parents_list[0].datatype if all(
                                        typ in parents_list[k].datatype for k in range(1,len(parents_list)))]
                                for k in range(len(parents_list)):
                                    parents_list[k].datatype = tmp_list

                            if any(parents_list[k].end for k in range(len(parents_list))):
                                for k in range(len(parents_list)):
                                    parents_list[k].end = True

                            # Add the neighbors of the first subtree into the indices_list
                            for i_2 in range(len(subtree_list[i][j].parent.children)):
                                if i != children_index[i_2]:
                                    indices_list.append([children_index[i_2],subtree_list[children_index[i_2]].index(
                                            subtree_list[i][j].parent.children[i_2])])

                            indices_list.sort(reverse = True)
                            for pair in indices_list:
                                del subtree_list[pair[0]][pair[1]]
                            subtree_list.append(parents_list)

                if len(matched_subtree_indices) > 1:
                    # Remove the matched subtrees of the current subtree
                    matched_subtree_indices.sort(reverse = True)
                    for j in matched_subtree_indices:
                        del subtree_list[i][j]

            # Track the height of the subtrees
            height_list.append(len(subtree_list))
            # Check if new subtrees were found, or if the number of subtrees has not increased
            if height_list[-1] == height_list[-2]:
                break

        if min_height < len(height_list):
            for k in range(len(subtree_list)-1,-1,-1):
                if len(subtree_list[k]) < 2 or k < height_list[min_height]:
                    del subtree_list[k]
        else:
            # No Subtree has the minimum height
            subtree_list = []

        # Add the subtrees for the optional elements
        for pair in self.optional_node_pairs:
            if not any(pair[1] in subtree for subtree in subtree_list):
                subtree_list.append([pair[1]])

        return subtree_list

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
            return_string += '\t' * depth + 'subtree_' + str(subtree_number) + ',\n'
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
                        return_string = return_string[:-2] + '])]),\n'  # Closing first_match and AnyMatch
                    else:
                        return_string = return_string[:-2] + ']),\n'  # Closing AnyMatch
                return return_string
            elif self.is_variable:
                return_string += '\t' * depth + variable_parser_model

                if any(self == pair[0] for pair in self.optional_node_pairs):
                    if self.element is not None and len(self.children) == 1:
                        return_string = return_string[:-2] + '])]),\n'  # Closing first_match and AnyMatch
                    else:
                        return_string = return_string[:-2] + ']),\n'  # Closing AnyMatch
                return return_string
            else:
                id1.value += 1
                self.ID = id1.value
                return_string += '\t' * depth + 'FixedDataModelElement(\'fixed' + str(id1.value) + '\', b\'' + self.element + '\'),\n'

                if any(self == pair[0] for pair in self.optional_node_pairs):
                    if self.element is not None and len(self.children) == 1:
                        return_string = return_string[:-2] + '])]),\n'  # Closing first_match and AnyMatch
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
                return_string += '\t' * depth + 'FixedWordlistDataModelElement(\'fixed' + str(id1.value) + '\', ' + str(
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
                    return_string = return_string[:-2] + '])]),\n'  # Closing first_match and AnyMatch
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
                    return_string = return_string[:-2] + '])]),\n'  # Closing first_match and AnyMatch
                else:
                    return_string = return_string[:-2] + ']),\n'  # Closing AnyMatch

            return return_string

    # this method returns the assigning of the subtrees for the AMiner
    def write_config_subtrees(self, ID, subtree_list):

        self.sort_subtrees(subtree_list)

        returnString = ''
        if subtree_list != []:
            returnString += '\n'
            for i in range(len(subtree_list)):
                # [:-2] removes comma following last ModelElement and tabulator preceding first ModelElement
                returnString += '\tsubtree_' + str(i) + ' = ' + 'SequenceModelElement(\'sequence' + str(ID.value) + '\', [\n' \
                        + subtree_list[i][0].write_config(2, ID, subtree_list, ignore_first_subtree = True)[:-2] + '])\n\n' 
        return returnString

    # Sorts the subtree_list in ascending order
    def sort_subtrees(self, subtree_list):
        subtree_list.sort(key=lambda x: x[0].subtree_height())
        return

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
