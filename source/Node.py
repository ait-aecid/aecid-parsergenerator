#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This class describes a node of the parsing tree"""
from collections import Counter
from dateutil.parser import parse as datetimeparse
import base64
import binascii
import socket
import PGConfig

class Node:
    def __init__(self, optionalNodePairs = [], mergeTupple = []):
        self.element = None
        self.isList = False # If this is True, then self.element is a list
        self.isVariable = False
        self.parent = None
        self.occurrence = 0
        self.end = False
        self.children = []
        self.theta1 = 0
        self.endingLines = 0
        self.datatype = ['string', 'integer', 'float', 'ipaddress'] #, 'datetime', 'base64', 'hex']
        self.endingLineNumbers = [] # Used for evaluation
        self.ID = 1
        self.optionalNodePairs = optionalNodePairs # List of the First and the last
        self.mergeTupple = mergeTupple # List of nodes, which are inserted into the branch after the matching has happened

    # This method makes a deep copy of 
    def deepCopy(self, endNode):
        newEndNode = None
        newNode = Node(self.optionalNodePairs, self.mergeTupple)

        if self.isList:
            newNode.element = []
            newNode.element.extend(self.element)
        else:
            newNode.element = self.element

        newNode.isList = self.isList
        newNode.isVariable = self.isVariable
        newNode.occurrence = self.occurrence
        newNode.end = self.end
        newNode.theta1 = self.theta1
        newNode.endingLines = self.endingLines
        newNode.datatype = []
        newNode.datatype.extend(self.datatype)

        if self != endNode:
            for child in self.children:
                if newEndNode == None:
                    [newChild, newEndNode] = child.deepCopy(endNode)
                    newNode.children.append(newChild)
                else:
                    newNode.children.append(child.deepCopy(endNode)[0])

            for child in newNode.children:
                child.parent = newNode

        else:
            newEndNode = newNode

        return [newNode, newEndNode]

    # This method returns a textual representation of the parser tree, with additional node information (line occurrences, end node, theta)
    def toString(self, depth):
        returnString = ''

        numberstring = ''
        if len(self.endingLineNumbers) > 0:
            numberstring = ' EndingLineNumbers = ['
            for endingLinenumber in self.endingLineNumbers:
                numberstring += str(endingLinenumber) + ','
            numberstring += ']'

        if self.element == None:
            returnString += 'root (' + str(self.occurrence) + ')\n'
        else:
            if self.isList == True:
                if self.end == True:
                    returnString += ' ' * depth + '- ' + str(self.element) + ' (' + str(self.occurrence) + ') - End (' + str(self.endingLines) + ') - Theta=' + str(self.theta1)  + numberstring + '\n'
                else:
                    returnString += ' ' * depth + '- ' + str(self.element) + ' (' + str(self.occurrence) + ') - Theta=' + str(self.theta1)  + numberstring + '\n'
            else:
                if self.end == True:
                    returnString += ' ' * depth + '- ' + self.element + ' (' + str(self.occurrence) + ') - End (' + str(self.endingLines) + ') - Theta=' + str(self.theta1)  + numberstring + '\n'
                else:
                    returnString += ' ' * depth + '- ' + self.element + ' (' + str(self.occurrence) + ') - Theta=' + str(self.theta1)  + numberstring + '\n'

        for child in self.children:
            returnString += child.toString(depth + 1)

        return returnString

    # This method returns the total amount of nodes in the parser tree
    def countNodes(self):
        if len(self.children) == 0:
            return 1
        elif len(self.children) == 1:
            return 1 + self.children[0].countNodes()
        else:
            sum = 0
            for child in self.children:
                sum += child.countNodes()
            return 1 + sum

    # This method returns the total amount of leaves in the parser tree
    def countLeaves(self):
        if len(self.children) == 0:
            return 1
        elif len(self.children) == 1:
            return self.children[0].countLeaves()
        else:
            sum = 0
            for child in self.children:
                sum += child.countLeaves()
            return sum

    # This method returns the total amount of variable nodes in the parser tree
    def countVariables(self):
        val = 0
        if self.isVariable == True:
            val = 1

        if len(self.children) == 0:
            return val
        elif len(self.children) == 1:
            return val + self.children[0].countVariables()
        else:
            sum = 0
            for child in self.children:
                sum += child.countVariables()
            return val + sum

    # This method returns the total amount of fixed nodes in the parser tree
    def countFixed(self):
        val = 0
        if self.isVariable == False:
            val = 1

        if len(self.children) == 0:
            return val
        elif len(self.children) == 1:
            return val + self.children[0].countVariables()
        else:
            sum = 0
            for child in self.children:
                sum += child.countVariables()
            return val + sum

    # This method returns the total amount of log lines that end in one of the leaves, i.e., all parsing log lines except the ones ending before optional elements
    def countLeaveOccurrences(self):
        if len(self.children) == 0:
            return self.occurrence
        elif len(self.children) == 1:
            return self.children[0].countLeaveOccurrences()
        else:
            sum = 0
            for child in self.children:
                sum += child.countLeaveOccurrences()
            return sum

    # This method returns the total amount of log lines that end before optional elements, i.e., all parsing log lines except the ones ending at a leave
    def countOptionalOccurrences(self):
        if len(self.children) == 0:
            return 0 # Leave can never be optional
        elif len(self.children) == 1:
            if self.end == True:
                return self.endingLines + self.children[0].countOptionalOccurrences()
            else:
                return self.children[0].countOptionalOccurrences()
        else:
            sum = 0
            for child in self.children:
                sum += child.countOptionalOccurrences()

            if self.end == True:
                return self.endingLines + sum
            else:
                return sum

    # This method returns an array of all node datatypes. A counter could be used to aggregate the result
    def countDatatypes(self):
        if self.isVariable == True:
            if 'ipaddress' in self.datatype:
                thisDatatype = 'ipaddress'
            elif 'base64' in self.datatype:
                thisDatatype = 'base64'
            elif 'hex' in self.datatype:
                thisDatatype = 'hex'
            elif 'datetime' in self.datatype:
                thisDatatype = 'datetime'
            elif 'integer' in self.datatype:
                thisDatatype = 'integer'
            elif 'float' in self.datatype:
                thisDatatype = 'float'
            else:
                thisDatatype = 'string'
        else:
            thisDatatype = 'fix'

        if len(self.children) == 0:
            return [thisDatatype]
        elif len(self.children) == 1:
            childDatatypes = []
            childDatatypes.extend(self.children[0].countDatatypes())
            childDatatypes.append(thisDatatype)
            return childDatatypes
        else:
            childDatatypes = []
            for child in self.children:
                childDatatypes.extend(child.countDatatypes())

            childDatatypes.append(thisDatatype)
            return childDatatypes

    # Sorts the subtreeList in ascending order
    def subtreeHeight(self):
        if len(self.children) == 0:
            return 0
        else:
            return max(child.subtreeHeight() for child in self.children) + 1

    # This method aggregates two subsequent fixed nodes in order to reduce the overall amount of nodes and tree complexity
    def aggregateSequences(self, subtreeList = []):
        if len(self.children) == 0:
            return
        elif len(self.children) == 1:
            child = self.children[0]
            if self.element is not None and not self.isVariable and not self.isList and not self.end and not child.isVariable and not child.isList and \
                    not any(child in subtree for subtree in subtreeList) and not any(child in pair for pair in self.optionalNodePairs):
                # Merge following node into this node
                self.element = str(self.element) + str(child.element)
                self.children = child.children
                child.parent = None
                self.end = child.end
                self.endingLines = child.endingLines
                self.endingLineNumbers = child.endingLineNumbers
                for childchild in child.children:
                    childchild.parent = self
                self.aggregateSequences(subtreeList)
            else:
                child.aggregateSequences(subtreeList)
        else:
            for child in self.children:
                child.aggregateSequences(subtreeList)

    # This method returns a dictionary of all nodes, referenced by their IDs
    def getNodeMappings(self):
        if len(self.children) == 0:
            dict = {self.ID : self}
            return dict
        elif len(self.children) == 1:
            child = self.children[0]
            dict = child.getNodeMappings()
            dict.update({self.ID : self})
            return dict
        else:
            dict = {self.ID: self}
            for child in self.children:
                dict.update(child.getNodeMappings())
            return dict

    # This method returns all edges of the parser tree
    def getNodeConnections(self):
        if len(self.children) == 0:
            return []
        elif len(self.children) == 1:
            child = self.children[0]
            connection = (self.ID, child.ID)
            childConnections = child.getNodeConnections()
            childConnections.append(connection)
            return childConnections
        else:
            connectionList = []
            for child in self.children:
                connection = (self.ID, child.ID)
                connectionList.append(connection)
                childConnections = child.getNodeConnections()
                if childConnections is not None:
                    connectionList.extend(childConnections)
            return connectionList

    # This method retruns all leave nodes
    def getLeaves(self):
        if len(self.children) == 0:
            return [self]
        elif len(self.children) == 1:
            return self.children[0].getLeaves()
        else:
            nodeList = []
            for child in self.children:
                nodeList += child.getLeaves()
            return nodeList

    # This method sorts the children after each branch in order to avoid AMiner issues regarding subset path elements
    def sortChildren(self):
        if self.isList:
            self.element.sort(key = lambda x: len(x), reverse=True)

        if len(self.children) == 0:
            return
        elif len(self.children) == 1:
            child = self.children[0]
            child.sortChildren()
            return
        else:
            sortedChildren = []
            variableIndex = -1
            for i in range(len(self.children)):
                if self.children[i].isVariable:
                    variableIndex = i
                    break

            if variableIndex != -1:
                # Sort the intern lists of nodes with listelements
                for child in self.children:
                    if child.isList:
                        child.element = sorted(child.element, key = lambda x: (len(x), x), reverse=True)
                # Sort the children
                sortedChildren1 = sorted((child for child in self.children if not child.isVariable and not child.isList), key = lambda x: (len(x.element), x.element), reverse=True)
                sortedChildren2 = sorted((child for child in self.children if not child.isVariable and child.isList), key = lambda x: (len(x.element[0]), x.element[0]), reverse=True)
                self.children = sortedChildren1+sortedChildren2+[self.children[variableIndex]]
            else:
                # Sort the intern lists of nodes with listelements
                for child in self.children:
                    if child.isList:
                        child.element = sorted(child.element, key = lambda x: (len(x), x), reverse=True)
                # Sort the children
                sortedChildren1 = sorted((child for child in self.children if not child.isList), key = lambda x: (len(x.element), x.element), reverse=True)
                sortedChildren2 = sorted((child for child in self.children if child.isList), key = lambda x: (len(x.element[0]), x.element[0]), reverse=True)
                self.children = sortedChildren1 + sortedChildren2

            for child in self.children:
                child.sortChildren()
            return

    # This method tries to replaces branches with lists in order to simplify the tree
    def insertLists(self):
        if len(self.children) == 0:
            return
        elif len(self.children) == 1:
            self.children[0].insertLists()
            return
        else:
            allChildrenEqual = True
            compareChild = self.children[0]
            for i in range(1, len(self.children)):
                if compareChild.isPathIdentical(self.children[i], True) == False:
                    # Note that with this criteria, all branches must be equal to create a list. For future work, this could be extended to only some equal branches
                    allChildrenEqual = False
                    break

            if allChildrenEqual == True:
                # Insert a list instead of a branch
                for i in range(1, len(self.children)):
                    compareChild.mergeNode(self.children[i])
                    compareChild.mergePaths(self.children[i])
                self.children = [compareChild]

            for child in self.children:
                child.insertLists()
            return

    # This method merges two equal paths
    def mergePaths(self, node):
        self.occurrence += node.occurrence
        self.endingLines += node.endingLines
        #self.endingLineNumbers.extend(node.endingLineNumbers) # For Evaluation, comment out if not needed

        # Because of previous checks done by other methods, the paths are equal, i.e., they have the same number of children
        if len(self.children) == 0:
            return
        elif len(self.children) == 1:
            return self.children[0].mergePaths(node.children[0])
        elif len(self.children) > 1:
            for i in range(0, len(self.children)):
                self.children[i].mergePaths(node.children[i])
            return

    # This method checks whether two paths are equal
    def isPathIdentical(self, node, initial):
        # The sibling nodes will be transformed into a list, therefore the elements must be equal except in the initial step
        if (initial == True or self.element == node.element) and self.isVariable == node.isVariable and self.end == node.end and len(self.children) == len(node.children) and self.datatype == node.datatype:
            if len(self.children) == 0:
                return True
            elif len(self.children) == 1:
                return self.children[0].isPathIdentical(node.children[0], False)
            elif len(self.children) > 1:
                result = True
                for i in range(0, len(self.children)):
                    result = result and self.children[i].isPathIdentical(node.children[i], False) # Requires that all branches were sorted before! (e.g., by calling sortedChildren)
                return result
        else:
            return False

    # This method inserts variables when nodes are followed by mostly identical paths
    def insertVariables(self, minSimilarity, delimiters, depth, forceBranch):
        if len(self.children) == 0:
            # Leave node; do nothing
            return
        elif len(self.children) == 1:
            # Only one child exists; no need to insert variable
            child = self.children[0]
            child.insertVariables(minSimilarity, delimiters, depth+1, forceBranch)
            return
        else:
            if depth not in forceBranch:
                # Multiple children exist; try to insert variable if they are similar
                allChildrenSimilar = True
                compareChild = self.children[0]
                for i in range(1, len(self.children)):
                    similarities = compareChild.getPathSimilaritiesEnhanced(self.children[i], True, delimiters)
                    similarity = 0
                    if len(similarities) > 0:
                        similarity = sum(similarities) / float(len(similarities))
                    #print(similarity)
                    #print('~ Compute ~')
                    #for template in compareChild.getTemplates(''):
                    #    print(' ' + template)
                    #print('~ with ~')
                    #for template in self.children[i].getTemplates(''):
                    #    print(' ' + template)
                    #print(str(sum(similarities)) + '/' + str(len(similarities)) + '=' + str(similarity))
                    # Never insert a variable when delimiters are involved
                    #print(str(self.children[i].datatype) + str(self.children[i].element))
                    #if self.parent is not None and self.parent.parent is not None and self.parent.parent.parent is not None and self.parent.parent.parent.element == 'msg':
                    #    print(similarity)
                    #    for template in compareChild.getTemplates(''):
                    #        print(' ' + template)
                    #        print('~ with ~')
                    #    for template in self.children[i].getTemplates(''):
                    #        print(' ' + template)
                    if similarity < minSimilarity or any((c in self.children[i].element) for c in delimiters): # Consecutive delimiters are merged during tree building, requires this kind of check
                        # Note that with this criteria, all branches must be similar to insert a variable. For future work, this could be extended to only some similar branches
                        allChildrenSimilar = False
                        break

                # Never insert a variable when delimiters are involved
                if allChildrenSimilar == True:# and compareChild.element not in delimiters:
                    # Insert a variable instead of a branch
                    print('~ The following loglines are similar ~')
                    for template in self.getTemplates(''):
                        print(' ' + template)
                    compareChild.element = '§'
                    compareChild.isVariable = True
                    for i in range(1, len(self.children)):
                        print('~ The following loglines are merged ~')
                        print(compareChild.getTemplates(''))
                        print(self.children[i].getTemplates(''))
                        compareChild.datatype = [typ for typ in compareChild.datatype if typ in self.children[i].datatype]
                        compareChild.mergeSimilarPathsEnhanced(self.children[i], True)
                    self.children = [compareChild]

            for child in self.children:
                child.insertVariables(minSimilarity, delimiters, depth+1, forceBranch)
            return

    # This method merges two similar paths
    def mergeSimilarPaths(self, node, initial):
        #print('Merging ' + str(self.element) + ' with ' + str(node.element))

        # Nodes cannot simply be merged when one of the children is a variable, because this would mix variable and fixed elements after branch.
        # Stop merging propagation and wait until similarities of children are computed in next iteration of insertVariables
        # This did not work, the node.children branch was lost !!!
        #if initial == False:
        #    for child in self.children:
        #        if child.isVariable == True:
        #            return
        #    for child in node.children:
        #        if child.isVariable == True:
        #            return

        self.occurrence += node.occurrence
        self.endingLines += node.endingLines
        #self.endingLineNumbers.extend(node.endingLineNumbers) # For Evaluation, comment out if not needed

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
            selfChild = self.children[0]
            containsVariable = False
            for nodeChild in node.children:
                if nodeChild.isVariable:
                    containsVariable = True
                    break

            if containsVariable == True:
                selfChild.datatype = ['string'] # TODO can be improved
                selfChild.isVariable = True
                selfChild.element = '§'
                for nodeChild in node.children:
                    selfChild.mergeSimilarPaths(nodeChild, False)
                self.children = [selfChild]
            else:
                for nodeChild in node.children:
                    if selfChild.element == nodeChild.element:# or selfChild.isVariable or nodeChild.isVariable: # In order to avoid branches between variable and fixed children, fixed are always converted to variables in that case
                        if selfChild.datatype != nodeChild.datatype:
                            selfChild.datatype = ['string']
                        #if selfChild.isVariable != nodeChild.isVariable:
                        #    selfChild.isVariable = True
                        #    selfChild.element = '§'
                            #nodeChild.isVariable = True
                            #nodeChild.element = '§'
                        selfChild.mergeSimilarPaths(nodeChild, False)
                    else:
                        self.children.append(nodeChild)
                        nodeChild.parent = self
        elif len(self.children) > 1:
            containsVariable = False
            for nodeChild in node.children:
                if nodeChild.isVariable:
                    containsVariable = True
                    break
            for selfChild in self.children:
                if selfChild.isVariable:
                    containsVariable = True
                    break

            if containsVariable == True:
                resultChild = self.children[0]
                resultChild.datatype = ['string'] # TODO can be improved
                resultChild.isVariable = True
                resultChild.element = '§'
                for nodeChild in node.children:
                    resultChild.mergeSimilarPaths(nodeChild, False)
                for i in range(1, len(self.children)):
                    resultChild.mergeSimilarPaths(self.children[i], False)
                self.children = [resultChild]
            else:
                nodeChildsToBeAdded = node.children[:]
                for i in range(0, len(self.children)):
                    selfChild = self.children[i]
                    for j in range(0, len(node.children)):
                        nodeChild = node.children[j]
                        if selfChild.element == nodeChild.element:# or selfChild.isVariable or nodeChild.isVariable: # In order to avoid branches between variable and fixed children, fixed are always converted to variables in that case
                            if selfChild.datatype != nodeChild.datatype:
                                selfChild.datatype = ['string']
                            #if selfChild.isVariable != nodeChild.isVariable:
                            #    selfChild.isVariable = True
                            #    selfChild.element = '§'
                                #nodeChild.isVariable = True
                                #nodeChild.element = '§'
                            selfChild.mergeSimilarPaths(nodeChild, False)
                            #if nodeChild in nodeChildsToBeAdded: # Needs to be checked because of converting fixed to variable after branches enables that nodeChild fits more than once
                            nodeChildsToBeAdded.remove(nodeChild)
                            break
                self.children.extend(nodeChildsToBeAdded)
                for nodeChild in nodeChildsToBeAdded:
                    nodeChild.parent = self

    # This method merges two similar paths
    def mergeSimilarPathsEnhanced(self, node, initial):
        #print('Merging ' + str(self.element) + ' with ' + str(node.element))

        # Nodes cannot simply be merged when one of the children is a variable, because this would mix variable and fixed elements after branch.
        # Stop merging propagation and wait until similarities of children are computed in next iteration of insertVariables
        # This did not work, the node.children branch was lost !!!
        #if initial == False:
        #    for child in self.children:
        #        if child.isVariable == True:
        #            return
        #    for child in node.children:
        #        if child.isVariable == True:
        #            return

        self.occurrence += node.occurrence
        self.endingLines += node.endingLines
        #self.endingLineNumbers.extend(node.endingLineNumbers) # For Evaluation, comment out if not needed

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
            if True: # Enhancement
                i = 0
                j = 0
                while i < len(self.children) and j < len(node.children):
                    # Elements match
                    if self.children[i].element == node.children[j].element:
                        # print('Match ' + str(self.children[i].element) + ' with ' + str(node.children[j].element))
                        self.children[i].mergeSimilarPathsEnhanced(node.children[j], False)
                        if self.children[i] == '§' and self.children[i].datatype != node.children[j].datatype:
                            self.children[i].datatype = [typ for typ in self.children[i].datatype if typ in node.children[j].datatype]
                        i += 1
                        j += 1

                    # Match one node if possible
                    elif self.children[i].element > node.children[j].element: # Match one child of self
                        # Match the node with a variable if present
                        # print('Cannot1 match ' + str(self.children[i].element))
                        if node.children[-1].isVariable == True:
                            # print('Match with Variable')
                            self.children[i].mergeSimilarPathsEnhanced(node.children[-1], False)
                            self.children[i].datatype = [typ for typ in node.children[j].datatype if typ in node.children[-1].datatype]
                            i += 1
                        else:
                            i += 1

                    else: # Match one child of the node
                        # print('Cannot2 match ' + str(node.children[j].element))
                        # Match the node with a variable if present
                        if self.children[-1].isVariable == True:
                            # print('Match with Variable')
                            self.children[-1].mergeSimilarPathsEnhanced(node.children[j], False)
                            self.children[-1].datatype = [typ for typ in node.children[j].datatype if typ in node.children[-1].datatype]
                            j += 1
                        else:
                            self.children.append(node.children[j])
                            node.children[j].parent = self
                            j += 1

                # Match remaining nodes
                while j < len(node.children):
                    # print('Match remaining node: ' + str(node.children[j].element))
                    if self.children[-1].isVariable == True:
                        # print('Match with Variable')
                        self.children[-1].mergeSimilarPathsEnhanced(node.children[j], False)
                        self.children[-1].datatype = [typ for typ in node.children[j].datatype if typ in node.children[-1].datatype]
                        j += 1
                    else:
                        self.children.append(node.children[j])
                        node.children[j].parent = self
                        j += 1

            else: # Original implementation
                containsVariable = False
                for nodeChild in node.children:
                    if nodeChild.isVariable:
                        containsVariable = True
                        break
                for selfChild in self.children:
                    if selfChild.isVariable:
                        containsVariable = True
                        break

                if containsVariable == True:
                    resultChild = self.children[0]
                    resultChild.datatype = ['string'] # TODO can be improved
                    resultChild.isVariable = True
                    resultChild.element = '§'
                    for nodeChild in node.children:
                        resultChild.mergeSimilarPaths(nodeChild, False)
                    for i in range(1, len(self.children)):
                        resultChild.mergeSimilarPaths(self.children[i], False)
                    self.children = [resultChild]
                else:
                    nodeChildsToBeAdded = node.children[:]
                    for i in range(0, len(self.children)):
                        selfChild = self.children[i]
                        for j in range(0, len(node.children)):
                            nodeChild = node.children[j]
                            if selfChild.element == nodeChild.element:# or selfChild.isVariable or nodeChild.isVariable: # In order to avoid branches between variable and fixed children, fixed are always converted to variables in that case
                                if selfChild.datatype != nodeChild.datatype:
                                    selfChild.datatype = ['string']
                                #if selfChild.isVariable != nodeChild.isVariable:
                                #    selfChild.isVariable = True
                                #    selfChild.element = '§'
                                    #nodeChild.isVariable = True
                                    #nodeChild.element = '§'
                                selfChild.mergeSimilarPaths(nodeChild, False)
                                #if nodeChild in nodeChildsToBeAdded: # Needs to be checked because of converting fixed to variable after branches enables that nodeChild fits more than once
                                nodeChildsToBeAdded.remove(nodeChild)
                                break
                    self.children.extend(nodeChildsToBeAdded)
                    for nodeChild in nodeChildsToBeAdded:
                        nodeChild.parent = self

            # print('Merging ' + str(self.element) + ' with ' + str(node.element))
            # print('Children: %s'%[child.element for child in self.children])

    # This method checks whether two paths are similar
    def getPathSimilarities(self, node, initial, delimiters):
        # Initialize returnList with 1 causes that branches at the end of paths without any children always collapse to a variable
        if initial == True:
            returnList = [1]
        else:
            returnList = []

        if len(node.children) == 0:
            pass
            # If self branch still has some remaining nodes, add these as mismatches
            #for child in self.children:
            #    returnList.extend([0] * child.getNumberOfFollowingNodes())
        elif len(self.children) == 0:
            pass
            # If node branch still has some remaining nodes, add these as mismatches
            #for child in node.children:
            #    returnList.extend([0] * child.getNumberOfFollowingNodes())
        elif len(self.children) == 1:
            for nodeChild in node.children:
                returnList.extend(self.children[0].getPathSimilarities(nodeChild, False, delimiters))
        elif len(self.children) > 1:
            lastIndex = -1
            for i in range(0, len(self.children)):
                if i < len(node.children):
                    returnList.extend(self.children[i].getPathSimilarities(node.children[i], False, delimiters)) # Requires that all branches were sorted before! (e.g., by calling sortedChildren)
                else:
                    returnList.extend([0] * self.children[i].getNumberOfFollowingNodes())
                lastIndex = i

            for i in range(lastIndex + 1, len(node.children)):
                returnList.extend([0] * node.children[i].getNumberOfFollowingNodes())

        # Since it is a branch, the initial elements will never match. Neither add 0 or 1 in that case
        if initial != True:
            if self.isVariable == True or node.isVariable == True:
                # Variables that match with fixed elements or other variables do not say much about the similarity. Neither add 0 or 1 in that case
                pass
            elif any((c in self.element) for c in delimiters):
                # Delimiters often match randomly. Neither add 0 or 1 in that case
                pass
            elif self.element == node.element:
                returnList.append(1)
            else:
                returnList.append(0)

        return returnList

    # This method checks whether two paths are similar
    def getPathSimilaritiesEnhanced(self, node, initial, delimiters):
        # Initialize returnList with 1 causes that branches at the end of paths without any children always collapse to a variable
        if initial == True:
            returnList = [1]
        else:
            returnList = []
        # print([child.element for child in self.children])
        # print([child.element for child in node.children])

        if len(node.children) == 0:
            pass
            # If self branch still has some remaining nodes, add these as mismatches
            #for child in self.children:
            #    returnList.extend([0] * child.getNumberOfFollowingNodes())
        elif len(self.children) == 0:
            pass
            # If node branch still has some remaining nodes, add these as mismatches
            #for child in node.children:
            #    returnList.extend([0] * child.getNumberOfFollowingNodes())
        elif len(self.children) == 1:
            for nodeChild in node.children:
                returnList.extend(self.children[0].getPathSimilaritiesEnhanced(nodeChild, False, delimiters))
        elif len(self.children) > 1:
            if True: # Enhancement
                i = 0
                j = 0

                while i < len(self.children) and j < len(node.children):
                    # Elements match
                    if self.children[i].element == node.children[j].element:
                        returnList.extend(self.children[i].getPathSimilaritiesEnhanced(node.children[j], False, delimiters))
                        #print('Match')
                        #print(i, j, self.children[i].element, node.children[j].element)
                        i += 1
                        j += 1
                    # Match one node if possible

                    elif self.children[i].element > node.children[j].element: # Match one child of self
                        # Match the node with a variable if present
                        if node.children[-1].isVariable == True:
                            returnList.extend(self.children[i].getPathSimilaritiesEnhanced(node.children[-1], False, delimiters))
                            #print('Match')
                            #print(i, j, self.children[i].element, node.children[-1].element)
                            i += 1
                        else:
                            returnList.extend([0] * self.children[i].getNumberOfFollowingNodes())
                            #print('Mismatch')
                            #print(i,j,self.children[i].element)
                            i += 1
                    else: # Match one child of the node
                        # Match the node with a variable if present
                        if self.children[-1].isVariable == True:
                            returnList.extend(self.children[-1].getPathSimilaritiesEnhanced(node.children[j], False, delimiters))
                            #print('Match')
                            #print(i, j, self.children[-1].element, node.children[j].element)
                            j += 1
                        else:
                            returnList.extend([0] * node.children[j].getNumberOfFollowingNodes())
                            #print('Mismatch')
                            #print(i,j,node.children[j].element)
                            j += 1

            else: # original implementation of getPathSimilarities
                lastIndex = -1

                for i in range(0, len(self.children)):
                    if i < len(node.children):
                        returnList.extend(self.children[i].getPathSimilaritiesEnhanced(node.children[i], False, delimiters)) # Requires that all branches were sorted before! (e.g., by calling sortChildren)
                    else:
                        returnList.extend([0] * self.children[i].getNumberOfFollowingNodes())
                    lastIndex = i

                for i in range(lastIndex + 1, len(node.children)):
                    returnList.extend([0] * node.children[i].getNumberOfFollowingNodes())

        # Since it is a branch, the initial elements will never match. Neither add 0 or 1 in that case
        if initial != True:
            if self.isVariable == True or node.isVariable == True:
                # Variables that match with fixed elements or other variables do not say much about the similarity. Neither add 0 or 1 in that case
                pass
            elif any((c in self.element) for c in delimiters):
                # Delimiters often match randomly. Neither add 0 or 1 in that case
                pass
            elif self.element == node.element:
                returnList.append(1)
            else:
                returnList.append(0)

        return returnList

    # This function matches the parser of self with the parser of the note and returns a list of the matched nodes with a similarity score
    def getSubtreeMatch(self, node, delimiters):
        debugMode = False
        elementList1 = self.getElements([0], delimiters) # Dictionary with the elements of the nodes as keys and a list of the paths to the nodes
        elementList2 = node.getElements([1], delimiters)

        if debugMode:
            print('NewSubtreeMatch:')
            print(elementList1)
            print(elementList2)
        # Matching of the entries with one match in both trees
        elementList = {}
        for key in elementList1:
            if key in elementList2 and len(elementList1[key]) == 1 and len(elementList2[key]) == 1:
                elementList[key] = [[elementList1[key][0], elementList2[key][0]]]

        previousMatches = self.matchParserNodes({}, elementList)
        if debugMode:
            print('Result: %s'%previousMatches)

        for i in range(2, 1+max(max([len(elementList1[k]) for k in elementList1]), max([len(elementList2[k]) for k in elementList2]))):
            elementList = {}
            for key in elementList1:
                if len(elementList1[key]) == i and key in elementList2 and (len(elementList2[key]) == 1 or len(elementList2[key]) >= i):
                    elementList[key] = []
                    for j in range(len(elementList2[key])):
                        elementList[key] += [[elementList1[key][k], elementList2[key][j]] for k in range(len(elementList1[key]))]
            for key in elementList2:
                if len(elementList2[key]) == i and key in elementList1 and (len(elementList1[key]) == 1 or len(elementList1[key]) > i):
                    elementList[key] = []
                    for j in range(len(elementList1[key])):
                        elementList[key] += [[elementList1[key][j], elementList2[key][k]] for k in range(len(elementList2[key]))]

            previousMatches = self.matchParserNodes(previousMatches, elementList)

        return [previousMatches, sum([len(previousMatches[x]) for x in previousMatches])/min(sum([len(elementList1[x]) for x in elementList1]), sum([len(elementList2[x]) for x in elementList2]))]

    # This function returns a Dictionary with the elements of the nodes as keys and a list of the paths to the nodes
    def getElements(self, previousPath, delimiters):
        elementList = {} # Dictionary with the elements of the nodes as keys and a list of the paths to the nodes

        if str(self.element) not in delimiters and not self.isVariable: # Add the element of the node if it is no delimiter
            elementList = {str(self.element): [previousPath]}

        for i in range(len(self.children)): # Add the elements of the following nodes to the elementList
            elementList2 = self.children[i].getElements(previousPath+[i], delimiters)
            for key in elementList2:
                if key in elementList:
                    elementList[key] += elementList2[key]
                else:
                    elementList[key] = elementList2[key]

        return elementList

    # This function gets a consistent set of matches of two trees and a set of possible matches.
    # The function returns a consistent set of matches which includes the previous  matches and the highest number of possible matches, such that the set stays consistent
    def matchParserNodes(self, previousMatches, newMatches):
        debugMode = False
        if debugMode:
            print('Match:')
            print('previousMatches: %s'%previousMatches)
            print('newMatches: %s'%newMatches)
        # Check if new matches are inconsistent to existing ones
        keys = list(newMatches.keys())
        if previousMatches != {}:
            for i in range(len(keys)-1, -1, -1):
                for i1 in range(len(newMatches[keys[i]])-1, -1, -1):
                    break2 = False
                    for key2 in previousMatches:
                        if break2:
                            break2 = False
                            break
                        for i2 in range(len(previousMatches[key2])-1, -1, -1):
                            if not self.isConsistent(newMatches[keys[i]][i1], previousMatches[key2][i2]):
                                del newMatches[keys[i]][i1]
                                break2 = True
                                break
                if newMatches[keys[i]] == []:
                    del newMatches[keys[i]]
                    del keys[i]

        # Check if new matches are inconsistent to each other
        inconsistentMatches = []
        for i in range(len(keys)):
            for j in range(i,len(keys)):
                for i2 in range(len(newMatches[keys[i]])):
                    for j2 in range(len(newMatches[keys[j]])):
                        if debugMode and False:
                            print('Is %s consistent with %s\n%s'%(newMatches[keys[i]][i2], newMatches[keys[j]][j2], self.isConsistent(newMatches[keys[i]][i2], newMatches[keys[j]][j2])))
                        if not self.isConsistent(newMatches[keys[i]][i2], newMatches[keys[j]][j2]):
                            inconsistentMatches.append([i,j,i2,j2])

        # Find minimal Indices so that every element is included at least once in every set
        inconsistentItems = []
        while len(inconsistentMatches) != 0:
            countList = [[0 for j in range(len(newMatches[keys[i]]))] for i in range(len(keys))]
            for i in range(len(inconsistentMatches)):
                countList[inconsistentMatches[i][0]][inconsistentMatches[i][2]] += 1
                countList[inconsistentMatches[i][1]][inconsistentMatches[i][3]] += 1

            # This section searches for a item to remove from the inconsistentMatches and takes the length of the mismatching into account ([[0],[1]] < [[0,1],[1,1,1,1,1,1,1,1,1]])
            maxCount = 0
            tmpIndex = 0
            tmpIndex2 = 0
            for i in range(len(countList)):
                for i2 in range(len(countList[i])):
                    if countList[i][i2] > maxCount:
                        maxCount = countList[i][i2]
                        tmpIndex = i
                        tmpIndex2 = i2
                    elif countList[i][i2] == maxCount and \
                            abs(len(newMatches[keys[i]][i2][0])-len(newMatches[keys[i]][i2][1])) > \
                            abs(len(newMatches[keys[tmpIndex]][tmpIndex2][0])-len(newMatches[keys[tmpIndex]][tmpIndex2][1])):
                        tmpIndex = i
                        tmpIndex2 = i2
                    elif countList[i][i2] == maxCount and \
                            abs(len(newMatches[keys[i]][i2][0])-len(newMatches[keys[i]][i2][1])) == \
                            abs(len(newMatches[keys[tmpIndex]][tmpIndex2][0])-len(newMatches[keys[tmpIndex]][tmpIndex2][1])) and \
                            max(len(newMatches[keys[i]][i2][0]), len(newMatches[keys[i]][i2][1])) > \
                            max(len(newMatches[keys[tmpIndex]][tmpIndex2][0]), len(newMatches[keys[tmpIndex]][tmpIndex2][1])):
                        tmpIndex = i
                        tmpIndex2 = i2
            inconsistentItems.append([tmpIndex, tmpIndex2])

            inconsistentMatches = [match for match in inconsistentMatches if ((match[0] != inconsistentItems[-1][0] or match[2] != inconsistentItems[-1][1]) and \
                    (match[1] != inconsistentItems[-1][0] or match[3] != inconsistentItems[-1][1]))]

        inconsistentItems.sort(key = lambda x: x[1], reverse = True)

        for i in range(len(inconsistentItems)):
            del newMatches[keys[inconsistentItems[i][0]]][inconsistentItems[i][1]]

        for key in newMatches:
            if key in previousMatches:
                previousMatches[key] += newMatches[key]
            elif len(newMatches[key]) != 0:
                previousMatches[key] = newMatches[key]

        return previousMatches

    # This method matches the lists of all list nodes
    def matchLists(self, minSimilarity):
        debugMode = False

        nodes = self.getListNodes() # Get all nodes which have a list as elements
        valueList = [] # List of the values of the elementlists
        indicesList = [] # List of the assigned indices of the valueList

        # initialises and merges the value- and indicesList
        for i in range(len(nodes)):
            for j in range(len(valueList)):
                if len([True for element in nodes[i].element if element in valueList[j]]) / min(len(nodes[i].element), len(valueList[j])) > minSimilarity:
                    if debugMode:
                        print('Merge list %s with list %s'%(nodes[i].element, valueList[j]))

                    indicesList.append(j)
                    for element in nodes[i].element:
                        if element not in valueList[j]:
                            valueList[j].append(element)

                    if debugMode:
                        print('Result: %s'%(valueList[j]))
                    break

            # Add new values if they do not fit with any previous one
            if len(indicesList) < i+1:
                indicesList.append(len(valueList))
                valueList.append(nodes[i].element)

        if debugMode:
            print('IndicesList: %s'%indicesList)
            print('ValueList: %s'%valueList)

        # Check if the value lists can be further merged together
        notStableIndices = list(range(len(valueList)))
        while len(notStableIndices) > 0:
            if debugMode:
                print('notStableIndices: %s'%notStableIndices)

            isStable = True
            for i in range(1, len(valueList)):
                if i != notStableIndices[0] and type(valueList[i]) == list and \
                        len([True for element in valueList[i] if element in valueList[notStableIndices[0]]]) / min(len(valueList[i]), len(valueList[notStableIndices[0]])) > minSimilarity:
                    if debugMode:
                        print('Merge list %s with list %s'%(valueList[notStableIndices[0]], valueList[i]))

                    # Extend the values
                    for element in valueList[i]:
                        if element not in valueList[notStableIndices[0]]:
                            valueList[notStableIndices[0]].append(element)

                    isStable = False
                    valueList[i] = notStableIndices[0]
                    if i in notStableIndices:
                        del notStableIndices[notStableIndices.index(i)]
                    break

            if isStable:
                del notStableIndices[0]

        if debugMode:
            print('IndicesList after merging: %s'%indicesList)
            print('ValueList: %s'%valueList)

        # Assign the new expanded lists
        for i in range(len(nodes)):
            index = indicesList[i]
            while type(valueList[index]) != list:
                index = valueList[index]
            nodes[i].element = valueList[index]

        return

    # This method returns a list of the nodes, which are lists
    def getListNodes(self):
        nodeList = []

        if self.isList:
            nodeList = [self]

        for child in self.children:
            nodeList += child.getListNodes()

        return nodeList

    # This function checks if the the two pairs would result in a incosistency if both would be matched.
    # Inconsistencies are pairings, which would result in a violation of the predecessor-successor like [[1], [0,1]], [[1,1], [0]]
    def isConsistent(self, pair1, pair2):

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
        elif pair1[1] == pair2[0][:len(pair1[1])] or pair1[1] == pair2[1][:len(pair1[1])] or \
                pair1[1][:len(pair2[0])] == pair2[0] or pair1[1][:len(pair2[1])] == pair2[1]:
            return False

        # No found predecessor/successorrelation
        else:
            return True

    # This function merges the node self with node. The set of the matches includes the matched nodes in the subtrees.
    def mergeSubtreeMatches(self, node, matches, pos0, pos1, firstMerge = True):
        debugMode = False

        # Get the pairs without the element-values
        if type(matches) == dict:
            newPreviousMatches = []
            for key in matches:
                newPreviousMatches += matches[key]
            matches = newPreviousMatches
            matches.sort()

        if matches == []:
            self.mergeSubtrees(node)

        else: # matches != []
            [nextMatches, nextSubtrees] = self.nextMatches(matches, pos0, pos1)
            if debugMode:
                print('nextMatches: %s \nnextSubtrees: %s'%(nextMatches, nextSubtrees))

            for i in range(len(nextMatches)):
                if debugMode:
                    print('\n\n\n')
                    print('Follow the path %s from node %s'%(nextMatches[i][0][len(pos0):], self.element))
                    print('Element 1:', self.element)
                    print('Element 2:', node.element)
                    print('Path 1:', nextMatches[i][0], pos0)
                    print('Path 2:', nextMatches[i][1], pos1)

                self.mergeToSinglePath(node, nextMatches[i], nextMatches, pos0, pos1)

                self.followPath(nextMatches[i][0][len(pos0):]).mergeSubtreeMatches(node.followPath(nextMatches[i][1][len(pos1):]), nextSubtrees[i], nextMatches[i][0], nextMatches[i][1], firstMerge = False)

            if firstMerge:
                # Merge endnodes and adding the optional nodes of node to self
                for tupple in self.mergeTupple:
                    if debugMode:
                        print('Tupple:')
                        print('0\n', tupple[0])
                        print('1\n', tupple[1])
                        print('2\n', tupple[2])
                        print('3\n', tupple[3])
                        print('4\n', tupple[4])

                    if tupple[1] in tupple[0].children:
                        tupple[1].mergeNode(tupple[4])

                        [newNode, newEndNode] = tupple[2].deepCopy(tupple[3])
                        tupple[2] = newNode
                        tupple[3] = newEndNode

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

                        # Check if the optional part is already present in optionalNodePairs
                        if [tupple[2], tupple[1]] not in self.optionalNodePairs:
                            node.optionalNodePairs.append([tupple[2], tupple[1]])
                self.mergeTupple.clear()

        return

    # This method merges two nodes, without matches and merges the variable nodes if present.
    def mergeSubtrees(self, node):
        self.mergeNode(node)

        if len(self.children) == 0:
            self.end = True

        for i in range(len(node.children)):
            if node.children[i].isVariable:
                containsVariable = False
                for child in self.children:
                    if child.isVariable:
                        containsVariable = True
                        child.mergeSubtrees(node.children[i])
                        break
                if not containsVariable:
                    self.children.append(node.children[i])
                    node.children[i].parent = self
            else:
                self.children.append(node.children[i])
                node.children[i].parent = self

    # This method returns a list, which contains the next matches and the corresponding matches in their subtrees
    def nextMatches(self, matches, pos0, pos1):

        if len(matches) == 0 or len(matches) == 1 and matches[0][0] == pos0:
            return [[], []]

        if matches[0][0] == pos0:
            del matches[0]

        nextMatches = [matches[0]] # Next matches
        nextSubtrees = [[]] # List of the subtrees of the nodes to the next matches

        for i in range(1,len(matches)):
            if nextMatches[-1][0] != matches[i][0][:len(nextMatches[-1][0])]:
                nextMatches.append(matches[i])
                nextSubtrees.append([])
            else:
                nextSubtrees[-1].append(matches[i])

        return [nextMatches, nextSubtrees]

    # This method returns the successor node, which is reached after following the path
    def followPath(self, path):
        node = self
        for i in range(len(path)):
            node = node.children[path[i]]
        return node

    # This method merges two paths into one and adds the additional branches
    def mergeToSinglePath(self, node, pair, nextMatches, pos0, pos1):
        debugMode = False

        # Merge nodes
        self.mergeNode(node)

        # Add not matched branch children of node to self
        for i in range(len(node.children)):
            if not any(pos1+[i] == pos[1][:len(pos1)+1] for pos in nextMatches) and node.children[i] not in self.children:
                if debugMode:
                    print('Added branch: %s (Path: %s)'%(node.children[i].element, pos1+[i]))

                if node.children[i].isVariable:
                    containsVariable = False
                    for child in self.children:
                        if child.isVariable:
                            containsVariable = True
                            child.mergeSubtrees(node.children[i])
                            break
                    if not containsVariable:
                        self.children.append(node.children[i])
                        node.children[i].parent = self
                            
                else:
                    self.children.append(node.children[i])
                    node.children[i].parent = self

        tmpSelf = self
        tmpNode = node

        for i in range(min(len(pair[0])-len(pos0), len(pair[1])-len(pos1))-1):
            tmpSelf = tmpSelf.followPath([pair[0][len(pos0)+i]])
            tmpNode = tmpNode.followPath([pair[1][len(pos1)+i]])
            if debugMode:
                print('Match %s with %s'%(tmpSelf.element, tmpNode.element))

            # Merge the nodes because they lie on the matched path
            # print('%s-%s'%(tmpSelf.element, tmpNode.element))
            tmpSelf.mergeNode(tmpNode)

            # Add not matched branch children
            for j in range(len(tmpNode.children)):
                if not any(pair[1][:len(pos1)+i+1]+[j] == tmpPos[1][:len(pos1)+i+2] for tmpPos in nextMatches) and tmpNode.children[j] not in tmpSelf.children:
                    if debugMode:
                        print('Added branch: %s (Path: %s)'%(tmpNode.children[j].element, pair[1][:len(pos1)+i+1]+[j]))

                    if tmpNode.children[j].isVariable:
                        containsVariable = False
                        for child in tmpSelf.children:
                            if child.isVariable:
                                containsVariable = True
                                child.mergeSubtrees(tmpNode.children[j])
                                break
                        if not containsVariable:
                            tmpSelf.children.append(tmpNode.children[j])
                            tmpNode.children[j].parent = tmpSelf

                    else:
                        tmpSelf.children.append(tmpNode.children[j])
                        tmpNode.children[j].parent = tmpSelf

        if len(pair[0])-len(pos0) < len(pair[1])-len(pos1):
            if debugMode:
                print('Add nodes of node to self and make them optional')
                print(len(pair[1]), len(pos1), len(pair[0]), len(pos0))
                print(pair[1][len(pos1):len(pos1)+len(pair[0])-len(pos0)], len(pair[1][len(pos1):len(pos1)+len(pair[0])-len(pos0)]))
                print(pair[1][len(pos1):], len(pair[1][len(pos1):]))
                print('Last unmatched: %s - %s'%(str(node.followPath(pair[1][len(pos1):len(pos1)+len(pair[0])-len(pos0)-2]).element) + \
                        str(node.followPath(pair[1][len(pos1):len(pos1)+len(pair[0])-len(pos0)-1]).element), \
                        str(self.followPath(pair[0][len(pos0):-2]).element) + str(self.followPath(pair[0][len(pos0):-1]).element)))
                print('Optional elements: %s'%[node.followPath(pair[1][len(pos1):i]).element for i in range(len(pos1)+len(pair[0])-len(pos0), len(pair[1]))])
                print('First optional element: %s'%node.followPath(pair[1][len(pos1):len(pos1)+len(pair[0])-len(pos0)]).element)
                print('Next Matched: %s - %s'%(node.followPath(pair[1][len(pos1):]).element, self.followPath(pair[0][len(pos0):]).element))

            # Appending the tupple of certain nodes to be able to later insert the optional part into the parser
            self.mergeTupple.append([self.followPath(pair[0][len(pos0):-1]), self.followPath(pair[0][len(pos0):]), \
                    node.followPath(pair[1][len(pos1):len(pos1)+len(pair[0])-len(pos0)]), node.followPath(pair[1][len(pos1):-1]), node.followPath(pair[1][len(pos1):])])

        elif len(pair[0])-len(pos0) > len(pair[1])-len(pos1):
            if debugMode:
                print('Make nodes of self optional')
                print(len(pair[0]), len(pos0), len(pair[1]), len(pos1))
                print(pair[0][len(pos0):len(pos0)+len(pair[1])-len(pos1)], len(pair[0][len(pos0):len(pos0)+len(pair[1])-len(pos1)]))
                print(pair[0][len(pos0):], len(pair[0][len(pos0):]))

            if [self.followPath(pair[0][len(pos0):len(pos0)+len(pair[1])-len(pos1)]), self.followPath(pair[0][len(pos0):])] not in self.optionalNodePairs:
                self.optionalNodePairs.append([self.followPath(pair[0][len(pos0):len(pos0)+len(pair[1])-len(pos1)]), self.followPath(pair[0][len(pos0):])])

    # This method changes the attributes of self to allow matching of both self and node
    def mergeNode(self, node):
        self.datatype = [typ for typ in self.datatype if typ in node.datatype]

        # Updating variable/list element
        if node.isVariable and not self.isVariable:
            self.isVariable = True
            self.element = '§'
        elif not self.isVariable:
            if self.isList and node.isList:
                self.element.extend([element for element in node.element if element not in self.element])
            elif not self.isList and node.isList:
                self.isList = True
                if self.element not in node.element:
                    node.element.append(self.element)
                self.element = node.element
            elif self.isList and not node.isList:
                if node.element not in self.element:
                    self.element.append(node.element)
            elif node.element != self.element:
                self.isList = True
                self.element = [self.element, node.element]

        # Update line end
        if not self.end and node.end:
            self.end = True

        # Update optional node endings
        if any(node in pair for pair in self.optionalNodePairs):
            for i in range(len(self.optionalNodePairs)):
                if node == self.optionalNodePairs[i][0]:
                    self.optionalNodePairs[i][0] = self
                if node == self.optionalNodePairs[i][1]:
                    self.optionalNodePairs[i][1] = self

    # This function finds subtrees in the parser and return the IDs of the root nodes
    # Parseretrees with multiple parents are not supported (Remove matchedSubtreeIndices + Save number of includions in subtrees)
    def getSubtrees(self, minHeight):
        debugMode = False
        subtreeList = [node for node in self.getLeaves()]
        tmpDict = {}

        tmpIndex = 0
        tmpList = [] # List of the list elements
        tmpNodeList = [] # List of the corresponding nodes
        for i in range(len(subtreeList)):
            if type(subtreeList[i].element) == list:
                if subtreeList[i].element in tmpList:
                    tmpNodeList[tmpList.index(subtreeList[i].element)].append(i)
                else:
                    tmpList.append(subtreeList[i].element)
                    tmpNodeList.append([i])
            else:
                if subtreeList[i].element in tmpDict:
                    tmpDict[subtreeList[i].element].append(i)
                else:
                    tmpDict[subtreeList[i].element] = [i]

        subtreeList = [[subtreeList[k] for k in tmpDict[key]] for key in tmpDict] + [[subtreeList[k] for k in tmpNodeList[k2]] for k2 in range(len(tmpNodeList))] # List of roots of equal subtrees
        heightList = [0, len(subtreeList)]

        if debugMode:
            print([[str(subtree[k].parent.element)+str(subtree[k].element) for k in range(len(subtree))] for subtree in subtreeList])

        while True:
            for i in range(heightList[-2], heightList[-1]):
                matchedSubtreeIndices = [] # List of the indices of the subtreetypes, which have already been matched
                for j in range(len(subtreeList[i])):

                    # Check if the subtree has already been matched
                    if j in matchedSubtreeIndices:
                        continue

                    if debugMode and subtreeList[i][j].parent.parent.element != None:
                        print('Try to match: %s of %s'%(str(subtreeList[i][j].element), str(subtreeList[i][j].parent.parent.element)+str(subtreeList[i][j].parent.element)+str(subtreeList[i][j].element)))

                    childrenIndex = []
                    allChildrenMatched = True
                    for child in subtreeList[i][j].parent.children:
                        if child == subtreeList[i][j]:
                            childrenIndex.append(i)
                            continue

                        childMatch = False
                        for i2 in range(heightList[-1]):
                            if child in subtreeList[i2]:
                                childMatch = True
                                childrenIndex.append(i2)
                                break

                        if not childMatch:
                            allChildrenMatched = False
                            break

                    if not allChildrenMatched:
                        if debugMode:
                            print('At least one child could not be matched')
                    # Search for another subtree, which is equal to the indiced subtree of self.parent
                    if allChildrenMatched:
                        if debugMode:
                            print('Try to find a similar subtree')
                        firstMatch = True
                                
                        indicesList = [] # List of the indices, which are used to remove the other matched subtrees
                        parentsList = [subtreeList[i][j].parent] # List of the parents of matched subtrees

                        for j2 in range(j+1, len(subtreeList[i])):
                            # Check if the subtree has already been matched
                            if j2 in matchedSubtreeIndices:
                                continue

                            if subtreeList[i][j].parent.element == subtreeList[i][j2].parent.element and len(subtreeList[i][j].parent.children) == len(subtreeList[i][j2].parent.children):
                                allChildrenMatched = True

                                if debugMode:
                                    print('Check if all children are equal to the reference children')
                                # Checks if the children are the same subtrees. This works because the braches are ordered
                                for i2 in range(len(subtreeList[i][j2].parent.children)):
                                    if subtreeList[i][j2].parent.children[i2] == subtreeList[i][j2]:
                                        continue
                                    elif subtreeList[i][j2].parent.children[i2] in subtreeList[childrenIndex[i2]]:
                                        continue
                                    else:
                                        allChildrenMatched = False
                                        break

                                # If the subtree matches the reference, add the neighbors to the indicesList
                                if allChildrenMatched:
                                    parentsList.append(subtreeList[i][j2].parent)
                                    matchedSubtreeIndices.append(j2)

                                    for i2 in range(len(subtreeList[i][j2].parent.children)):
                                        if debugMode:
                                            print('Check if children is in the same subtreeList as the other')
                                        if i != childrenIndex[i2]:
                                            indicesList.append([childrenIndex[i2],subtreeList[childrenIndex[i2]].index(subtreeList[i][j2].parent.children[i2])])
                                            #print('Add 1: %s'%[childrenIndex[i2],subtreeList[childrenIndex[i2]].index(subtreeList[i][j2].parent.children[i2])])

                        if len(parentsList) > 1:
                            if debugMode:
                                print('ParentList: %s'%[str(parentsList[k].parent.element)+str(parentsList[k].element) for k in range(len(parentsList))])
                            matchedSubtreeIndices.append(j)

                            # check if the node is an variable and updates the datatype
                            if parentsList[0].isVariable:
                                tmpList = [typ for typ in parentsList[0].datatype if all(typ in parentsList[k].datatype for k in range(1,len(parentsList)))]
                                for k in range(len(parentsList)):
                                    parentsList[k].datatype = tmpList

                            if any(parentsList[k].end for k in range(len(parentsList))):
                                for k in range(len(parentsList)):
                                    parentsList[k].end = True

                            # Add the neighbors of the first subtree into the indicesList
                            for i2 in range(len(subtreeList[i][j].parent.children)):
                                if i != childrenIndex[i2]:
                                    indicesList.append([childrenIndex[i2],subtreeList[childrenIndex[i2]].index(subtreeList[i][j].parent.children[i2])])
                                    #print('Add 2: %s'%[childrenIndex[i2],subtreeList[childrenIndex[i2]].index(subtreeList[i][j].parent.children[i2])])

                            indicesList.sort(reverse = True)
                            if debugMode:
                                print('Remove the children from the indicesList')
                                print([[str(subtree[k].parent.element)+str(subtree[k].element) for k in range(len(subtree))] for subtree in subtreeList])
                                print(indicesList)
                                print(len(subtreeList))
                            #print(indicesList)
                            for pair in indicesList:
                                del subtreeList[pair[0]][pair[1]]
                            if debugMode:
                                print([[str(subtree[k].parent.element)+str(subtree[k].element) for k in range(len(subtree))] for subtree in subtreeList])

                                print('Add the subtrees to the subtree-list')
                            subtreeList.append(parentsList)
                            if debugMode:
                                print([[str(subtree[k].parent.element)+str(subtree[k].element) for k in range(len(subtree))] for subtree in subtreeList])

                if len(matchedSubtreeIndices) > 1:
                    # Remove the matched subtrees of the current subtree
                    matchedSubtreeIndices.sort(reverse = True)
                    if debugMode:
                        print('Remove the children from the current subtreeList')
                        print([[str(subtree[k].parent.element)+str(subtree[k].element) for k in range(len(subtree))] for subtree in subtreeList])
                        print(i, matchedSubtreeIndices)
                    for j in matchedSubtreeIndices:
                        del subtreeList[i][j]
                    if debugMode:
                        print([[str(subtree[k].parent.element)+str(subtree[k].element) for k in range(len(subtree))] for subtree in subtreeList])

            # Track the height of the subtrees
            heightList.append(len(subtreeList))
            # Check if new subtrees were found, or if the number of subtrees has not increased
            if heightList[-1] == heightList[-2]:
                break

        if debugMode:
            print('Delete subtrees with a smaller height/subtrees with less than two entries')
        if minHeight < len(heightList):
            for k in range(len(subtreeList)-1,-1,-1):
                if len(subtreeList[k]) < 2 or k < heightList[minHeight]:
                    del subtreeList[k]
        else:
            # No Subtree has the minimum height
            subtreeList = []

        # Add the subtrees for the optional elements
        for pair in self.optionalNodePairs:
            if not any(pair[1] in subtree for subtree in subtreeList):
                subtreeList.append([pair[1]])

        if debugMode:
            print('Return subtreeNodes')
            print([[str(subtree[k].parent.element)+str(subtree[k].element) for k in range(len(subtree))] for subtree in subtreeList])
        
        return subtreeList

    def getNumberOfFollowingNodes(self):
        if len(self.children) == 0:
            return 1
        elif len(self.children) == 1:
            return self.children[0].getNumberOfFollowingNodes() + 1
        else:
            sum = 0
            for child in self.children:
                sum += child.getNumberOfFollowingNodes()
            return sum + 1

    def getClusters(self):
        if len(self.children) == 0:
            return [self.endingLineNumbers]
        elif len(self.children) == 1:
            child = self.children[0]
            lists = child.getClusters()

            if self.end is True:
                lists.extend([self.endingLineNumbers])

            return lists
        else:
            lists = []
            for child in self.children:
                lists.extend(child.getClusters())
            return lists

    def getTemplates(self, string):
        if self.element is not None:
            newString = string + str(self.element)
        else:
            newString = ''

        if len(self.children) == 0:
            return [newString]
        elif len(self.children) == 1:
            child = self.children[0]
            list = []

            if self.end is True:
                list.append(newString)

            list.extend(child.getTemplates(newString))
            return list
        else:
            list = []
            for child in self.children:
                list.extend(child.getTemplates(newString))
            return list

    # This method builds the parser tree recursively
    def buildTree(self, depth, log_line_dict, delimiters, theta1, theta2, theta3, theta4, theta5, theta6, damping, forceBranch, forceVar):
        # Theta1 is increased in every recursion, however, should be limited. If theta1 > 0.5, only 1 child would be possible
        theta1 = min(theta1, 0.49)

        self.theta1 = theta1 # Store theta1 for every node, this information is printed in the textual tree

        # End the recursion if all lines end at this node
        if len(log_line_dict) == 0:
            self.end = False
            return

        # Check for multiple consecutive delimiters and combine them
        delimiterFlag = False
        for log_line_id in log_line_dict:
            log_line = log_line_dict[log_line_id]
            if depth < len(log_line.words):
                if log_line.words[depth] in delimiters:
                    moreDelimiters = True
                    delimiterFlag = True
                    while moreDelimiters == True:
                        if depth < len(log_line.words) - 1:
                            if log_line.words[depth + 1] in delimiters:
                                log_line.words[depth] += log_line.words[depth + 1]
                                del log_line.words[depth + 1]
                            else:
                                moreDelimiters = False
                        else:
                            moreDelimiters = False

        words = []
        list = []
        listFailedElem = [] # List of the log lines, which do not end and are not in list
        # Assemble a list of words of all log lines that pass over this node
        for log_line_id in log_line_dict:
            log_line = log_line_dict[log_line_id]
            if depth < len(log_line.words):
                words.append(log_line.words[depth])

        counter = Counter(words)

        sumFrequency = 0
        sumFrequency2 = 0 # Sum of the frequency of log lines, which did not surpass theta1
        maxCount = -1
        for elem in counter:
            maxCount = max(maxCount, counter[elem])
            # Determine the potential succeeding nodes, i.e., words that make up a high fraction of all words
            if counter[elem] / float(len(log_line_dict)) >= theta1 or depth in forceBranch:
                sumFrequency += counter[elem] # sumFrequency is needed in Case 3
                list.append(elem)
            else:
                sumFrequency2 += counter[elem]
                listFailedElem.append(elem)

        newNode = Node(self.optionalNodePairs, self.mergeTupple)
        newNode.determine_datatype(words)
        specialDatatype = False
        if depth not in forceBranch: # Branches can be forced also on special data types
            for dt in newNode.datatype:
                if dt in ['integer', 'float', 'datetime', 'ipaddress', 'base64', 'hex']:
                    specialDatatype = True

        # Always do a variable if all branches are unique, i.e., maxCount == 1
        # Also, never do a variable for delimiters
        if delimiterFlag == False and (len(list) == 0 or specialDatatype or depth in forceVar):
            # Case 1
            newNode.element = '§'
            newNode.isVariable = True
            newNode.parent = self
            self.children.append(newNode)
            new_dict = {}
            endingLines = 0
            # Determine log lines passing to next node(s) that will be analyzed in the next recursion
            for log_line_id in log_line_dict:
                log_line = log_line_dict[log_line_id]
                if depth < len(log_line.words) - 1:
                    new_dict[log_line_id] = log_line # Log line has more words, give it to next node
                elif depth == len(log_line.words) - 1:
                    endingLines += 1 # Log line ends at this node
                    #newNode.endingLineNumbers.append(log_line_id) # For Evaluation, comment out if not needed
            newNode.occurrence = len(log_line_dict) # It is a variable node, so all log lines received from parent node in previous step occur here
            if endingLines / float(self.occurrence) >= theta4:
                newNode.end = True
                newNode.endingLines = endingLines
            if depth not in forceBranch and len(new_dict) / float(self.occurrence) < theta5: # If almost all lines stop, do not make a subsequent node. This is accomplished by clearing the dict, i.e., no lines are passed to the next node
                new_dict = {}
            if newNode.occurrence != 0:
                newNode.theta1 = self.theta1 * (1 + (1 - newNode.occurrence / float(self.occurrence)) * damping)
            newNode.buildTree(depth + 1, new_dict, delimiters, newNode.theta1, theta2, theta3, theta4, theta5, theta6, damping, forceBranch, forceVar)
        elif len(list) == 1:
            # Case 2
            if counter[list[0]] / float(len(log_line_dict)) >= theta2 or delimiterFlag == True:
                # Case 2 a)
                newNode.element = list[0]
                newNode.parent = self
                self.children.append(newNode)
                new_dict = {}
                occurrences = 0
                endingLines = 0
                for log_line_id in log_line_dict:
                    log_line = log_line_dict[log_line_id]
                    if log_line.words[depth] == list[0]:
                        occurrences += 1
                        if depth < len(log_line.words) - 1:
                            new_dict[log_line_id] = log_line
                        elif depth == len(log_line.words) - 1:
                            endingLines += 1
                            #newNode.endingLineNumbers.append(log_line_id) # For Evaluation, comment out if not needed
                newNode.occurrence = occurrences
                if endingLines / float(self.occurrence) >= theta4:
                    newNode.end = True
                    newNode.endingLines = endingLines
                if depth not in forceBranch and len(new_dict) / float(self.occurrence) < theta5:  # If almost all lines stop, do not make a subsequent node. This is accomplished by clearing the dict, i.e., no lines are passed to the next node
                    new_dict = {}
                if newNode.occurrence != 0:
                    newNode.theta1 = self.theta1 * (1 + (1 - newNode.occurrence / float(self.occurrence)) * damping)
                newNode.buildTree(depth + 1, new_dict, delimiters, newNode.theta1, theta2, theta3, theta4, theta5, theta6, damping, forceBranch, forceVar)
                
                if sumFrequency2 / float(len(log_line_dict)) >= theta6 and listFailedElem[0] not in delimiters: # Adding a variable node at the end of the children
                    newNode = Node(self.optionalNodePairs, self.mergeTupple)
                    newNode.determine_datatype(listFailedElem)
                    newNode.element = '§'
                    newNode.isVariable = True
                    newNode.parent = self
                    self.children.append(newNode)
                    new_dict = {}
                    occurrences = 0
                    endingLines = 0
                    for log_line_id in log_line_dict:
                        log_line = log_line_dict[log_line_id]
                        if len(log_line.words) > depth and log_line.words[depth] in listFailedElem:
                            occurrences += 1
                            if depth < len(log_line.words) - 1:
                                new_dict[log_line_id] = log_line
                            elif depth == len(log_line.words) - 1:
                                endingLines += 1
                                #newNode.endingLineNumbers.append(log_line_id) # For Evaluation, comment out if not needed
                    newNode.occurrence = sumFrequency2
                    if endingLines / float(self.occurrence) >= theta4:
                        newNode.end = True
                        newNode.endingLines = endingLines
                    if depth not in forceBranch and len(new_dict) / float(self.occurrence) < theta5:  # If almost all lines stop, do not make a subsequent node. This is accomplished by clearing the dict, i.e., no lines are passed to the next node
                        new_dict = {}
                    if newNode.occurrence != 0:
                        newNode.theta1 = self.theta1 * (1 + (1 - newNode.occurrence / float(self.occurrence)) * damping)
                    newNode.buildTree(depth + 1, new_dict, delimiters, newNode.theta1, theta2, theta3, theta4, theta5, theta6, damping, forceBranch, forceVar)
            else:
                # Case 2 b)
                newNode.element = '§'
                newNode.isVariable = True
                newNode.parent = self
                self.children.append(newNode)
                new_dict = {}
                endingLines = 0
                for log_line_id in log_line_dict:
                    log_line = log_line_dict[log_line_id]
                    if depth < len(log_line.words) - 1:
                        new_dict[log_line_id] = log_line
                    elif depth == len(log_line.words) - 1:
                        endingLines += 1
                        #newNode.endingLineNumbers.append(log_line_id) # For Evaluation, comment out if not needed
                newNode.occurrence = len(log_line_dict)
                if endingLines / float(self.occurrence) >= theta4:
                    newNode.end = True
                    newNode.endingLines = endingLines
                if depth not in forceBranch and len(new_dict) / float(self.occurrence) < theta5:  # If almost all lines stop, do not make a subsequent node. This is accomplished by clearing the dict, i.e., no lines are passed to the next node
                    new_dict = {}
                if newNode.occurrence != 0:
                    newNode.theta1 = self.theta1 * (1 + (1 - newNode.occurrence / float(self.occurrence)) * damping)
                newNode.buildTree(depth + 1, new_dict, delimiters, newNode.theta1, theta2, theta3, theta4, theta5, theta6, damping, forceBranch, forceVar)
        elif len(list) > 1:
            # Case 3
            if sumFrequency / float(len(log_line_dict)) > theta3 or delimiterFlag == True:
                # Case 3 a)
                for element in list:
                    newNode = Node(self.optionalNodePairs, self.mergeTupple)
                    newNode.datatype = ['string']
                    newNode.element = element
                    newNode.parent = self
                    new_dict = {}
                    occurrences = 0
                    endingLines = 0
                    for log_line_id in log_line_dict:
                        log_line = log_line_dict[log_line_id]
                        if len(log_line.words) > depth and log_line.words[depth] == element:
                            occurrences += 1
                            if depth < len(log_line.words) - 1:
                                new_dict[log_line_id] = log_line
                            elif depth == len(log_line.words) - 1:
                                endingLines += 1
                                #newNode.endingLineNumbers.append(log_line_id) # For Evaluation, comment out if not needed
                    newNode.occurrence = occurrences
                    #if newNode.occurrence == 1:
                    #    continue
                    self.children.append(newNode)
                    if endingLines / float(self.occurrence) >= theta4:
                        newNode.end = True
                        newNode.endingLines = endingLines
                    if depth not in forceBranch and len(new_dict) / float(self.occurrence) < theta5:  # If almost all lines stop, do not make a subsequent node. This is accomplished by clearing the dict, i.e., no lines are passed to the next node
                        new_dict = {}
                    if newNode.occurrence != 0:
                        newNode.theta1 = self.theta1 * (1 + (1 - newNode.occurrence / float(self.occurrence)) * damping)
                    newNode.buildTree(depth + 1, new_dict, delimiters, newNode.theta1, theta2, theta3, theta4, theta5, theta6, damping, forceBranch, forceVar)

                if sumFrequency2 / float(len(log_line_dict)) >= theta6 and listFailedElem[0] not in delimiters: # Adding a variable node at the end of the children
                    newNode = Node(self.optionalNodePairs, self.mergeTupple)
                    newNode.determine_datatype(listFailedElem)
                    newNode.element = '§'
                    newNode.isVariable = True
                    newNode.parent = self
                    self.children.append(newNode)
                    new_dict = {}
                    occurrences = 0
                    endingLines = 0
                    for log_line_id in log_line_dict:
                        log_line = log_line_dict[log_line_id]
                        if len(log_line.words) > depth and log_line.words[depth] in listFailedElem:
                            occurrences += 1
                            if depth < len(log_line.words) - 1:
                                new_dict[log_line_id] = log_line
                            elif depth == len(log_line.words) - 1:
                                endingLines += 1
                                #newNode.endingLineNumbers.append(log_line_id) # For Evaluation, comment out if not needed
                    newNode.occurrence = sumFrequency2
                    if endingLines / float(self.occurrence) >= theta4:
                        newNode.end = True
                        newNode.endingLines = endingLines
                    if depth not in forceBranch and len(new_dict) / float(self.occurrence) < theta5:  # If almost all lines stop, do not make a subsequent node. This is accomplished by clearing the dict, i.e., no lines are passed to the next node
                        new_dict = {}
                    if newNode.occurrence != 0:
                        newNode.theta1 = self.theta1 * (1 + (1 - newNode.occurrence / float(self.occurrence)) * damping)
                    newNode.buildTree(depth + 1, new_dict, delimiters, newNode.theta1, theta2, theta3, theta4, theta5, theta6, damping, forceBranch, forceVar)
            else:
                # Case 3 b)
                newNode.element = '§'
                newNode.isVariable = True
                newNode.parent = self
                self.children.append(newNode)
                new_dict = {}
                endingLines = 0
                for log_line_id in log_line_dict:
                    log_line = log_line_dict[log_line_id]
                    if depth < len(log_line.words) - 1:
                        new_dict[log_line_id] = log_line
                    elif depth == len(log_line.words) - 1:
                        endingLines += 1
                        #newNode.endingLineNumbers.append(log_line_id) # For Evaluation, comment out if not needed
                newNode.occurrence = len(log_line_dict)
                if endingLines / float(self.occurrence) >= theta4:
                    newNode.end = True
                    newNode.endingLines = endingLines
                if depth not in forceBranch and len(new_dict) / float(self.occurrence) < theta5:  # If almost all lines stop, do not make a subsequent node. This is accomplished by clearing the dict, i.e., no lines are passed to the next node
                    new_dict = {}
                if newNode.occurrence != 0:
                    newNode.theta1 = self.theta1 * (1 + (1 - newNode.occurrence / float(self.occurrence)) * damping)
                newNode.buildTree(depth + 1, new_dict, delimiters, newNode.theta1, theta2, theta3, theta4, theta5, theta6, damping, forceBranch, forceVar)

    # This method returns the parser model for the AMiner
    def writeConfig(self, depth, ID, subtreeList = [], ignoreFirstSubtree = False):
        # Insert a subtree if the node is root of any of the subtrees
        returnString = ''

        if not ignoreFirstSubtree and (any(self in subtree for subtree in subtreeList) or any(self == pair[1] for pair in self.optionalNodePairs)):
            subtreeNumber = next((i for i in range(len(subtreeList)) if self in subtreeList[i]), None)
            returnString += '\t' * depth + 'subTree' + str(subtreeNumber) + ',\n'
            return returnString

        if any(self == pair[0] for pair in self.optionalNodePairs):
            ID.value += 1
            returnString += '\t' * depth + 'AnyMatchModelElement(\'anymatch' + str(ID.value) + '\', [\n'
            depth += 1
            usedNodes = []
            for i in range(len(self.optionalNodePairs)):
                if self == self.optionalNodePairs[i][0] and self.optionalNodePairs[i][1] not in usedNodes:
                    returnString += self.optionalNodePairs[i][1].writeConfig(depth, ID, subtreeList)
                    usedNodes.append(self.optionalNodePairs[i][1])
            if self.element != None and len(self.children) == 1:
                returnString += '\t' * depth + 'SequenceModelElement(\'sequence' + str(ID.value) + '\', [\n'
                depth += 1

        # Escape the escape characters
        if self.element is not None:
            if self.isList == True:
                aggElements = '['
                for elem in self.element:
                    aggElements += 'b\'' + elem.replace('\\', '\\\\').replace('\'', '\\\'') + '\', '
                aggElements = aggElements[:-2]
                aggElements += ']'
            else:
                self.element = self.element.replace('\\', '\\\\').replace('\'', '\\\'')

        # Delimited or VariableByte Datamodels should only be used when necessary, use more specific elements if possible
        variableParserModel = 'var'
        if self.isVariable == True:
            ID.value += 1
            self.ID = ID.value
            if 'ipaddress' in self.datatype:
                variableParserModel = 'IpAddressDataModelElement(\'ipaddress' + str(ID.value) + '\'),\n'
            elif 'integer' in self.datatype:
                if self.parent is not None and type(self.parent) != list and self.parent.parent is not None and type(self.parent.parent) != list and \
                        self.parent.element == ':' and 'ipaddress' in self.parent.parent.datatype:
                    variableParserModel = 'DecimalIntegerValueModelElement(\'port' + str(ID.value) + '\'),\n'
                else:
                    variableParserModel = 'DecimalIntegerValueModelElement(\'integer' + str(ID.value) + '\', valueSignType = DecimalIntegerValueModelElement.SIGN_TYPE_OPTIONAL),\n'
            elif 'base64' in self.datatype:
                variableParserModel = 'Base64StringModelElement(\'base64encoded' + str(ID.value) + '\'),\n'
            elif 'hex' in self.datatype:
                variableParserModel = 'HexStringModelElement(\'hexstring' + str(ID.value) + '\'),\n'
            elif 'datetime' in self.datatype:
                variableParserModel = 'DateTimeModelElement(\'datetime' + str(ID.value) + '\'),\n'
            elif 'float' in self.datatype:
                variableParserModel = 'DecimalFloatValueModelElement(\'float' + str(ID.value) + '\'),\n'
            else:
                variableParserModel = 'VariableByteDataModelElement(\'string' + str(ID.value) + '\', dict),\n'


        if len(self.children) == 0:
            # Node is a leaf node, return node info and do nothing else
            if self.element is None:
                pass
            elif self.isList == True:
                ID.value += 1
                self.ID = ID.value
                returnString += '\t' * depth + 'FixedWordlistDataModelElement(\'fixed' + str(ID.value) + '\', ' + str(aggElements) + '),\n'

                if any(self == pair[0] for pair in self.optionalNodePairs):
                    if self.element != None and len(self.children) == 1:
                        returnString = returnString[:-2] + '])]),\n' # Closing FirstMatch and AnyMatch
                    else:
                        returnString = returnString[:-2] + ']),\n' # Closing AnyMatch
                return returnString
            elif self.isVariable == True:
                returnString += '\t' * depth + variableParserModel

                if any(self == pair[0] for pair in self.optionalNodePairs):
                    if self.element != None and len(self.children) == 1:
                        returnString = returnString[:-2] + '])]),\n' # Closing FirstMatch and AnyMatch
                    else:
                        returnString = returnString[:-2] + ']),\n' # Closing AnyMatch
                return returnString
            else:
                ID.value += 1
                self.ID = ID.value
                returnString += '\t' * depth + 'FixedDataModelElement(\'fixed' + str(ID.value) + '\', b\'' + self.element + '\'),\n'

                if any(self == pair[0] for pair in self.optionalNodePairs):
                    if self.element != None and len(self.children) == 1:
                        returnString = returnString[:-2] + '])]),\n' # Closing FirstMatch and AnyMatch
                    else:
                        returnString = returnString[:-2] + ']),\n' # Closing AnyMatch
                return returnString
        elif len(self.children) == 1:
            # Node has exactly 1 child

            # Start a new sequence
            if self.element is None:
                ID.value += 1
                returnString += '\t' * depth + 'SequenceModelElement(\'sequence' + str(ID.value) + '\', [\n'
                depth += 1

            if self.element is None:
                pass
            elif self.isList == True:
                ID.value += 1
                self.ID = ID.value
                returnString += '\t' * depth + 'FixedWordlistDataModelElement(\'fixed' + str(ID.value) + 'b\', ' + str(aggElements) + '),\n'
            elif self.isVariable == True:
                returnString += '\t' * depth + variableParserModel
            else:
                ID.value += 1
                self.ID = ID.value
                returnString += '\t' * depth + 'FixedDataModelElement(\'fixed' + str(ID.value) + '\', b\'' + self.element + '\'),\n'

            # If this is an end node, put everything that follows in an optional element
            if self.end == True and self.element is not None:
                ID.value += 1
                returnString += '\t' * depth + 'OptionalMatchModelElement(\'optional' + str(ID.value) + '\', \n'
                depth += 1
                ID.value += 1
                returnString += '\t' * depth + 'SequenceModelElement(\'sequence' + str(ID.value) + '\', [\n'
                depth += 1

            returnString += self.children[0].writeConfig(depth, ID, subtreeList)

            # End Optional Element
            if self.end == True and self.element is not None:
                returnString = returnString[:-2] + '])),\n'

            # End the sequence
            if self.element is None:
                returnString = returnString[:-2] + ']),\n' # [:-2] removes newline and comma following last ModelElement

            if any(self == pair[0] for pair in self.optionalNodePairs):
                if self.element != None and len(self.children) == 1:
                    returnString = returnString[:-2] + '])]),\n' # Closing FirstMatch and AnyMatch
                else:
                    returnString = returnString[:-2] + ']),\n' # Closing AnyMatch

            return returnString
        else:
            # Node has > 1 children
            # Note that its not possible that one of the children is a wildcard - there would be no branch then

            if self.element is None:
                pass
            elif self.isList == True:
                ID.value += 1
                self.ID = ID.value
                returnString += '\t' * depth + 'FixedWordlistDataModelElement(\'fixed' + str(ID.value) + '\', ' + str(self.element) + '),\n'
            elif self.isVariable == True:
                returnString += '\t' * depth + variableParserModel
            else:
                ID.value += 1
                self.ID = ID.value
                returnString += '\t' * depth + 'FixedDataModelElement(\'fixed' + str(ID.value) + '\', b\'' + self.element + '\'),\n'
            # If this is an end node, put everything that follows in an optional element
            if self.end == True and self.element is not None:
                ID.value += 1
                returnString += '\t' * depth + 'OptionalMatchModelElement(\'optional' + str(ID.value) + '\', \n'
                depth += 1
                ID.value += 1
                returnString += '\t' * depth + 'SequenceModelElement(\'sequence' + str(ID.value) + '\', [\n'
                depth += 1

            # Get info about all children through recursion
            ID.value += 1
            returnString += '\t' * depth + 'FirstMatchModelElement(\'firstmatch' + str(ID.value) + '\', [\n'
            for child in self.children:
                if self.element is None or len(child.children) > 0:
                    ID.value += 1
                    depth += 1
                    returnString += '\t' * depth + 'SequenceModelElement(\'sequence' + str(ID.value) + '\', [\n'

                returnString += child.writeConfig(depth + 1, ID, subtreeList)

                if self.element is None or len(child.children) > 0:
                    returnString = returnString[:-2] + ']),\n'  # [:-2] removes newline and comma following last ModelElement
                    depth -= 1

            returnString = returnString[:-2] + ']),\n' # [:-2] removes newline and comma following last ModelElement

            # End Optional Element
            if self.end == True and self.element is not None:
                returnString = returnString[:-2] + '])),\n'

            if any(self == pair[0] for pair in self.optionalNodePairs):
                if self.element != None and len(self.children) == 1:
                    returnString = returnString[:-2] + '])]),\n' # Closing FirstMatch and AnyMatch
                else:
                    returnString = returnString[:-2] + ']),\n' # Closing AnyMatch

            return returnString

    # this method returns the assigning of the subtrees for the AMiner
    def writeConfigSubtrees(self, ID, subtreeList):

        self.sortSubtrees(subtreeList)

        returnString = ''
        if subtreeList != []:
            for i in range(len(subtreeList)):
                returnString += '\tsubTree' + str(i) + ' = ' + 'SequenceModelElement(\'sequence' + str(ID.value) + '\', [\n' \
                        + subtreeList[i][0].writeConfig(2, ID, subtreeList, ignoreFirstSubtree = True)[:-2] + '])\n\n' # [:-2] removes comma following last ModelElement and tabulator preceding first ModelElement

        return returnString + '\n'

    # Sorts the subtreeList in ascending order
    def sortSubtrees(self, subtreeList):
        subtreeList.sort(key=lambda x: x[0].subtreeHeight())
        return

    # This method checks whether the words occurring at a node have a specific data type
    def determine_datatype(self, words):
        for elem in words:
            if 'float' in self.datatype and Node.is_float(self, elem) == False:
                self.datatype.remove('float')

            if 'integer' in self.datatype and Node.is_integer(self, elem) == False:
                self.datatype.remove('integer')

            if 'hex' in self.datatype and Node.is_hex(self, elem) == False:
                self.datatype.remove('hex')

            if 'datetime' in self.datatype and Node.is_datetime(self, elem) == False:
                self.datatype.remove('datetime')

            if 'base64' in self.datatype and Node.is_base64(self, elem) == False:
                self.datatype.remove('base64')

            if 'ipaddress' in self.datatype and Node.is_ipaddress(self, elem) == False:
                self.datatype.remove('ipaddress')

    def checkConsistency(self):
        for child in self.children:
            if child.parent != self or not child.checkConsistency():
                if False and child.parent != self:
                    print(self)
                return False
        return True

    def updateParents(self):
        for child in self.children:
            child.updateParents()
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
        return self.toString(0)[1:]
        