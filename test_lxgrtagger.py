#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import LxGrTgr_05_41 as lxgr

#create sample object, then print it
sample1 = lxgr.tag("This is a very important opportunity that only comes once in a lifetime.")
lxgr.printer(sample1)

#or:
lxgr.printer(lxgr.tag("This is a very important opportunity that only comes once in a lifetime."))
lxgr.printer(lxgr.tag("I want to eat pizza."))

#we can also write a tagged string to file:
lxgr.writer("sample_results/sample1.tsv",sample1)

sample2 = lxgr.tag("I like pizza. I also enjoy eating it because it gives me a reason to drink beer.")
lxgr.printer(sample2)
lxgr.writer("sample_results/sample2.tsv",sample2)

import os
os.chdir("/Users/kristopherkyle/Desktop/Programming/GitHub/LCR-ADS-Lab/LxGrTgr/")

import LxGrTgr_05_65_4 as lxgr
tagList = ["finitecls+advl","thatcls+vcomp","whcls+vcomp","finitecls+rel","thatcls+ncomp","thatcls+jcomp","xtrapos+thatcls+jcomp","whcls+incomp","tocls+advl","ingcls+advl","edcls+advl","tocls+vcomp","tocls+ncomp","ingcls+vcomp","edcls+rel","ingcls+rel","tocls+rel","tocls+jcomp","xtrapos+tocls+jcomp","ingcls+incomp","rb+advl","in+advl","attr+npremod","nn+npremod","of+npostmod","in+npostmod","appos+npostmod","in+jcomp","rb+jjrbmod"]
lxgr.tagFolder("/Users/kristopherkyle/Desktop/books for LxGrTgr",'/Users/kristopherkyle/Desktop/lxgrOutput')
countD = lxgr.countTagsFolder('/Users/kristopherkyle/Desktop/lxgrOutput/',tagList)
lxgr.writeCounts(countD,'/Users/kristopherkyle/Desktop/lxgrOutput/results.tsv')