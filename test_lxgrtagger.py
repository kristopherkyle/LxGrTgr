#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import LxGrTgr_04 as lxgr

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
