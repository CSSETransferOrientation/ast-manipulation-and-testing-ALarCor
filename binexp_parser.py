#!/usr/bin/python3
import os
from os.path import join as osjoin

import unittest
from enum import Enum

# Use these to distinguish node types, note that you might want to further
# distinguish between the addition and multiplication operators
NodeType = Enum('BinOpNodeType', ['number', 'operator'])

class BinOpAst():
    """
    A somewhat quick and dirty structure to represent a binary operator AST.

    Reads input as a list of tokens in prefix notation, converts into internal representation,
    then can convert to prefix, postfix, or infix string output.
    """
    def __init__(self, prefix_list):
        """
        Initialize a binary operator AST from a given list in prefix notation.
        Destroys the list that is passed in.
        """
        self.val = prefix_list.pop(0)
        if self.val.isnumeric():
            self.type = NodeType.number
            self.left = False
            self.right = False
        else:
            self.type = NodeType.operator
            self.left = BinOpAst(prefix_list)
            self.right = BinOpAst(prefix_list)

    def __str__(self, indent=0):
        """
        Convert the binary tree printable string where indentation level indicates
        parent/child relationships
        """
        ilvl = '  '*indent
        left = '\n  ' + ilvl + self.left.__str__(indent+1) if self.left else ''
        right = '\n  ' + ilvl + self.right.__str__(indent+1) if self.right else ''
        return f"{ilvl}{self.val}{left}{right}"

    def __repr__(self):
        """Generate the repr from the string"""
        return str(self)

    def prefix_str(self):
        """
        Convert the BinOpAst to a prefix notation string.
        """
        match self.type:
            case NodeType.number:
                return self.val
            case NodeType.operator:
                return self.val + ' ' + self.left.prefix_str() + ' ' + self.right.prefix_str()

    def infix_str(self):
        """
        Convert the BinOpAst to a prefix notation string.
        """
        match self.type:
            case NodeType.number:
                return self.val
            case NodeType.operator:
                return '(' + self.left.infix_str() + ' ' + self.val + ' ' + self.right.infix_str() + ')'

    def postfix_str(self):
        """
        Convert the BinOpAst to a prefix notation string.
        """
        match self.type:
            case NodeType.number:
                return self.val
            case NodeType.operator:
                return self.left.postfix_str() + ' ' + self.right.postfix_str() + ' ' + self.val

    def additive_identity(self):
        """
        Reduce additive identities
        x + 0 = x
        """
        # ;;> This doesn't recur... 
        if self.type == NodeType.operator and self.val == '+':
            if self.left.type == NodeType.number and self.left.val == '0':
                return self.right
            if self.right.type == NodeType.number and self.right.val == '0':
                return self.left
        return self

    def multiplicative_identity(self):
        """
        Reduce multiplicative identities
        x * 1 = x
        """
        # ;;> This doesn't recur... 
        if self.type == NodeType.operator and self.val == '*':
            if self.left.type == NodeType.number and self.left.val == '1':
                return self.right
            if self.right.type == NodeType.number and self.right.val == '1':
                return self.left
        return self

    def mult_by_zero(self):
        """
        Reduce multiplication by zero
        x * 0 = 0
        """
        # ;;> This doesn't recur... 
        if self.type == NodeType.operator and self.val == '*':
            if self.left.type == NodeType.number and self.left.val == '0':
                return BinOpAst(['0'])
            if self.right.type == NodeType.number and self.right.val == '0':
                return BinOpAst(['0'])
        return self              

    def simplify_binops(self):
        """
        Simplify binary trees with the following:
        1) Additive identity, e.g. x + 0 = x
        2) Multiplicative identity, e.g. x * 1 = x
        3) Extra #1: Multiplication by 0, e.g. x * 0 = 0
        4) Extra #2: Constant folding, e.g. statically we can reduce 1 + 1 to 2, but not x + 1 to anything
        """
        # ;;> Ahhh, you were relying on simplify for the recursion... that doesn't match the spec but this does work
        self.left = self.left.simplify_binops() if self.left else None
        self.right = self.right.simplify_binops() if self.right else None
        self = self.additive_identity()
        self = self.multiplicative_identity()
        self = self.mult_by_zero()
        
        return self


if __name__ == "__main__":
    # Example tests (unittest can be more elaborate)
    tests = [
        (['+', '1', '+', '2', '0'], '+ 1 2'),
        (['+', '1', '*', '2', '1'], '+ 1 2'),
        (['*', '1', '*', '3', '1'], '3'),
        (['*', '1', '0'], '0'),
        (['+', '1', '*', '0', '1'], '1')
    ]

 # ;;> This does not use the file based testing required in the assignment!
    for test_input, expected_output in tests:
        ast = BinOpAst(test_input)
        simplified_ast = ast.simplify_binops()
        assert simplified_ast.prefix_str() == expected_output, f"Test failed for input {test_input}, got {simplified_ast.prefix_str()}"

    print("All tests passed.")
