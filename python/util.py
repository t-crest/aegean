#! /usr/bin/env python3

def findTag(x,s):
    tags = list(x)
    for i in range(0,len(tags)):
        if tags[i].tag == s:
            return tags[i]
