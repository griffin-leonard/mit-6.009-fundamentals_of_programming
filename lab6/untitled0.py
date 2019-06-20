#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 22:39:57 2019

@author: griffinl
"""

l = [['a', 'b', 'c'], ['a', 'b'], ['g', 'h', 'r', 'w']]
def permu(lists, prefix=''):
     if not lists:
          print(prefix)
          return
     first = lists[0]
     rest = lists[1:]
     for letter in first:
          permu(rest, prefix + letter)
#permu(l)
result = []
def _getPerms(l, path=[]):
    """ Get all permutations from a list of a list. Used as a helper 
    function for query. """
    global result
    if not l:
        result.append(path)
        return
    for item in l[0]:
        _getPerms(l[1:], path+[item])
_getPerms(l)
print(result)