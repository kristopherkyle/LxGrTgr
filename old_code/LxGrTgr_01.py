#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 11:47:46 2020

@author: kkyle2

This script is loosely based on TAASSC 2.0.0.58, which was used in Kyle et al. 2021a,b.
The data for those publications were processed using 
- TAASSC 2.0.0.58 (see https://github.com/kristopherkyle/TAASSC)
- Python version 3.7.3
- spaCy version 2.1.8
- spaCy `en_core_web_sm` model version 2.1.0.

This version of the code is part of a project designed to:
a) make a more user-friendly interface (including a python package, and online tool, and a desktop tool)
b) ensure that the tags are as accurate as possible

License:
The Lexicogrammatical Tagger
    Copyright (C) 2022  Kristopher Kyle and Douglas Biber [and others?]

This program is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)

See https://creativecommons.org/licenses/by-nc-sa/4.0/ for a summary of the license (and a link to the full license).

"""
### imports ####################################
version = "0.0.1"
version_notes = "0.0.1 - Built on 2.1.17; Tags follow discussions with Doug, Randi, and Jesse (with a few tweaks)."


import glob #for finding all filenames in a folder
import os #for making folders
# from xml.dom import minidom #for pretty printing
# import xml.etree.ElementTree as ET #for xml parsing
from random import sample #for random samples
import re #for regulat expressions
#from lexical_diversity import lex_div as ld #for lexical diversity. Should probably upgrade to TAALED

### spacy
import spacy #base NLP
#nlp = spacy.load("en_core_web_sm") #load model
nlp = spacy.load("en_core_web_trf")  #load model
nlp.max_length = 1728483 #allow more characters to be processed than default. This allows longer documents to be processed. This may need to be made longer.
######################################################

### Load lists, etc. #################################

nominal_stop = open("lists_LGR/nom_stop_list_edited.txt").read().split("\n") # created based on frequently occuring nouns with [potential] nominalizer suffixes in TMLE + T2KSWAL
prepVerbList = open("lists_LGR/prepVerbList.txt").read().split("\n") # From LGSWE; currently ignored in favor of OntoNotes classifications
phrasalVerbList = open("lists_LGR/phrasalVerbList.txt").read().split("\n") # From LGSWE
##########################################

### Utility Functions ####################
def safe_divide(numerator,denominator):
	if float(denominator) == 0.0:
		return(0.0)
	else:
		return(numerator/denominator)
		
###########################################

#### other functions ###
# def prettify(elem):
# 	"""Return a pretty-printed XML string for the Element.
# 	"""
# 	rough_string = ET.tostring(elem, 'utf-8')
# 	reparsed = minidom.parseString(rough_string)
# 	return(reparsed.toprettyxml(indent="    "))

###########################################
class tokenInfo():	
	def __init__(self, spacyToken): 
		self.idx = None #will have to add this from position in sentence
		self.word = spacyToken.text #raw text
		self.lemma = spacyToken.lemma_.lower() #lowered lemma form
		self.upos = spacyToken.pos_ #Universal part of speech
		self.xpos = spacyToken.tag_ #penn tag
		self.deprel = spacyToken.dep_ #dependency relation (based on CLEAR tagset)
		self.head = spacyToken.head#.text #text of head
		self.headidx = spacyToken.head.i #id of head
		self.children = spacyToken.children
		self.lxgrtag = None #main tag
		self.cat1 = None #additional tag (based on tag schema)
		self.cat2 = None #additional tag (based on tag schema)
		self.cat3 = None #additional tag (based on tag schema)
		self.cat4 = None #additional tag (based on tag schema)
		self.cat5 = None #additional tag (based on tag schema)
		self.cat6 = None #additional tag (based on tag schema)
		self.cat7 = None #additional tag (based on tag schema)
		self.cat8 = None #additional tag (based on tag schema)
		self.cat9 = None #additional tag (based on tag schema)
		self.semtag = None #additional tag (based on tag schema)

### Linguistic Analysis Functions ###
def nouns(token,nominalStopList = nominal_stop): #revised 2022-11-22; This is probably overly greedy. It was filtered using frequent candidates in T2KSWAL and TMLE
	if token.upos in ["NOUN", "PROPN"]:
		token.lxgrtag = "nn"
		if token.xpos in ["NNS","NNPS"]:
			token.cat1 = "pl"
		nominalSuff = ["al","cy","ee","er","or","ry","ant","ent","dom","ing","ity","ure","age","ese","ess","ful","ism","ist","ite","let","als","ees","ers","ors","ate","ance","ence","ment","ness","tion","ship","ette","hood","cies","ries","ants","ents","doms","ings","ages","fuls","isms","ists","ites","lets","eses","ates","ician","ities","ances","ences","ments","tions","ships","esses","ettes","hoods","nesses"]
		#the titles list is incomplete
		titles = ["mr","mr.","mister","ms","ms.", "miss","mrs","mrs.","missus","mistress","dr","dr.","doctor","professor"]
		#note that zero derivation is not included
		#stop list comes from list derived from manual analysis of tagged T2KSWAL + TMLE 
		nominalization = False
		for suff in nominalSuff:
			if len(token.word) > len(suff): #make sure word token is at least one character longer than suffix
				if token.word.lower()[0-len(suff):] == suff:
					nominalization = True
					break
		if token.upos == "PROPN":
			if token.word.lower() in titles:
				token.cat2 = "title"
			else:
				token.cat2 = "proper"
		elif nominalization == True:
			token.cat2 = "nom"
		#section for cat3:
		if token.deprel in ["compound","nmod"]:
			token.cat3 = "npremod"
		elif token.deprel == "appos":
			token.cat3 = "nappos"
		elif token.deprel == "poss":
			token.cat3 = "sgen"

def adjectives(token):	#2022-11-22
	if token .deprel in ["acomp","amod"]:
		token.lxgrtag = "jj"
		if token.deprel == "acomp": 
			token.cat1 = "pred"
		elif token.deprel == "amod":
			token.cat1 = "attr"
		#gerundial or participial?
		if token.xpos == "VBG": #we may have to rely on morphology here.
			token.cat2 = "ing"
		elif token.xpos == "VBN":
			token.cat2 = "ed"

#if token.pos_ == "ADV" or token.dep_ in ["npadvmod","advmod", "intj"] #double check the effects of this line (from previous iteration)
def adverbs(token,sent): #2022-11-22; tagged on adverb
	#this list needs to be more robust - taken from Table 10.17, page 879 LGSWE
	#will need to deal with prepositional linking adverbials elsewhere
	linking = ["so","then","though","anyway","however","thus","therefore","e.g.","i.e.","first","finally","furthermore","hence","nevertheless","rather","yet"] 
	if token.deprel == "advmod":
		token.lxgrtag = "rb"
		#print(token.word)
		if token.word[-2:].lower() == "ly":
			token.cat2 = "ly"
		if token.deprel == "advmod" and token.head.pos_ in ["VERB","AUX"]: #note that copular verbs get "AUX"
			if token.word.lower() in linking and token.idx < token.head.i: #if the word can be alinking adverb and occurs before the main verb:
				token.cat1 = "link"
			else:
				token.cat1 = "advl"
		elif token.deprel == "advmod" and token.head.dep_ == "acomp":
			token.cat1 = "adjmod"

		#split aux section:
		for tkn in sent:
			if tkn.headidx == token.headidx:
				if tkn.deprel == "aux" and tkn.idx < token.idx:
					if token.idx < token.headidx and token.head.pos_ == "VERB":
						token.cat3 = "splaux"
						break
	if token.deprel == "prt" and token.head.i < token.idx: #check for particles, make sure they aren't infinitive "to"
		token.lxgrtag = "rb"
		token.cat1 = "prtcle"
	if token.lxgrtag == "rb" and token.cat1 == None:
		token.cat1 = "othr"

def verbs(token,sent): #need to add spearate tags for tense/aspect and passives
	that0_list = "check consider ensure illustrate fear say assume understand hold appreciate insist feel reveal indicate wish decide express follow suggest saw direct pray observe record imagine see think show confirm ask meant acknowledge recognize need accept contend come maintain believe claim verify demonstrate learn hope thought reflect deduce prove find deny wrote read repeat remember admit adds advise compute reach trust yield state describe realize expect mean report know stress note told held explain hear gather establish suppose found use fancy submit doubt felt".split(" ")
	
	#don't tag verbs functioning as adjectives as verbs; only tag main verbs
	if token.upos in ["VERB","AUX"] and token.deprel not in ["amod","acomp","aux","auxpass"]: 
		token.lxgrtag = "vbmain"
		if token.lemma == "be": #need to add "+ NP" frames; need to deal with negation. This is kind of a mess
			if token.idx +2 <= sent[-1].idx and " ".join([token.lemma,sent[token.idx + 1].word.lower(),sent[token.idx + 2].word.lower()]) in prepVerbList:
				token.cat1 = "prepv"
			else:
				token.cat1 = "be"
		elif token.idx +1 <= sent[-1].idx and " ".join([token.lemma,sent[token.idx + 1].word.lower()]) in prepVerbList: #need to add "+ NP" frames
			token.cat1 = "prepv"
		#need to add phrasal verbs
		elif "prt" in [x.deprel for x in sent if x.headidx == token.idx]:
			token.cat1 = "phrsv"
		else:
			token.cat1 = "vblex"
		
		#this is an ordered list of POS tags for the main verb and auxs represented in the VP
		vp_pos = [x.xpos for x in sent if (x.headidx == token.idx and x.deprel in ["aux","auxpass"]) or x.idx == token.idx]
		#print(vp_pos)
		if "MD" in vp_pos:
			token.cat2 = "vp_w_modal"
		elif "VBZ" in vp_pos:
			token.cat2 = "pres"
		elif "VBP" in vp_pos:
			token.cat2 = "pres"
		elif "VBD" in vp_pos:
			token.cat2 = "past"
		else:
			token.cat2 = "nonfinite" #probably need more testing here
	
		### aspect analysis ###
		aux_text = [x.lemma.lower() for x in sent if (x.headidx == token.idx and x.deprel in ["aux"])]
		if "have" in aux_text:
			if token.xpos == "VBG":
				token.cat3 = "perfprog"
			else:
				token.cat3 = "perf"
		elif token.xpos == "VBG" and "be" in aux_text:
			token.cat3 = "prog"
		else:
			token.cat3 = "simple"
		
		### voice analysis ####
		pass_deps =  [x.deprel for x in sent if x.headidx == token.idx]
		if "auxpass" in pass_deps:
			if "agent" in pass_deps:
				token.cat4 = "pasv_by"
			else:
				token.cat4 = "pasv_agls"
		else:
			token.cat4 = "active"

		### cat5 analysis
		if token.deprel in ["ccomp","csubj"]: #may need to add dependent relations here ("csubj"?)
			token.cat5 = "compcls"
		elif token.deprel == "advcl":
			token.cat5 = "advlcls"
		elif token.deprel in ["relcl","acl"]:
			token.cat5 = "nmod_cls"
		# elif sent[token.headidx].upos in ["NOUN","PROPN","PRON"]:
		# 	token.cat5 = "nmod_cls"

		#####################
		### cat6 analysis ###
		#####################

		### that ###
		if "that" in [x.word.lower() for x in sent if x.word.lower() == "that" and x.headidx == token.idx and x.deprel in ["mark","nsubj"]]:
			if token.cat5 in ["compcls","nmod_cls"]:
				token.cat6 = "thatcls"
		
		### wh clause: ###
		if token.cat5 in ["compcls","nmod_cls","advlcls"]:
			if len([x.word.lower() for x in sent if x.headidx == token.idx and x.deprel in ["nsubj","advmod","attr"] and x.xpos in ["WDT","WP", "WP$", "WRB"] and x.word.lower() != "that"]) > 0:
				token.cat6 = "whcls"
		
		if token.cat2 == "nonfinite":
			### to clause ###
			if "to" in [x.word.lower() for x in sent if x.headidx == token.idx and x.idx < token.idx and x.upos == "PART"]:
				token.cat6 = "tocls" #probably needs more work
			### ing clause ###
			if token.xpos == "VBG":
				token.cat6 = "ingcls"
			
		### ed clause ###
		if token.xpos == "VBN" and token.cat4 == "active":
			token.cat6 = "edcls"


		#####################
		### cat7 analysis ###
		#####################
		if token.cat5 == "compcls":
			if sent[token.headidx].upos in ["VERB","AUX"] and token.idx != token.headidx:
				token.cat7 = "vcomp"
			elif sent[token.headidx].upos == "ADJ":
				token.cat7 = "jcomp"
			elif sent[token.headidx].upos in ["NOUN","PROPN","PRON"]:
				token.cat7 = "ncomp"
			elif token.deprel == "pcomp":
				token.cat7 = "incomp"
		
		markL = [x.word.lower() for x in sent if x.headidx == token.idx and x.deprel == "mark"] #list of subordinators
		if len(markL) != 0:
			mark = markL[0]

			if mark == "because":
				token.cat7 = "causative"
			elif mark in ["if","unless"]:
				token.cat7 = "conditional"
			elif mark in ["though","although","while"]:
				token.cat7 = "concessive"
			elif mark != "that":
				token.cat7 = "other_advl"

		######################
		### cat 8 analysis ###
		######################

		### relativizer deletion ###
		if token.cat5 == "nmod_cls" and token.cat6 not in ["tocls"]:
			if "dobj" in [x.deprel for x in sent if x.headidx == token.idx and x.idx < token.idx]: 
				if len([x.deprel for x in sent if x.headidx == token.idx and x.idx < token.idx and token.word.lower() not in ["that","who","which", "what","how","where","why","when","whose","whom","whomever"]]) == 0:
					token.cat8 = "reldel"
			elif len ([x.word.lower() for x in sent if x.headidx == token.idx and x.deprel == "nsubj" and x.word.lower() in ["that","who","which","what","how","where","why","when","whose","whom","whomever"]]) == 0:
				token.cat6 = "reldel"
		
		### complementizer deletion ###
		if token.cat5 == "compcls" and token.cat6 not in ["tocls","ingcls","thatcls","whcls"]:
			token.cat6 = "compdel"

	### aux analysis ####
	if token.deprel in ["aux","auxpass"]: #check for auxilliaries
		if token.word.lower() == "to":
			token.lxgrtag = "to"
		else:
			token.lxgrtag = "vbaux"
		
			if token.xpos == "MD":
				token.cat1 = "mod"
				if token.word.lower() in "can may might could".split(" "):
					token.cat2 = "pos"
				elif token.word.lower() in "ought must should".split(" "):
					token.cat2 = "nec"
				elif token.word.lower() in "will would shall".split(" "):
					token.cat2 = "prd"

def personal_pronouns(token): #updated 2022-11-02
	#NOTE: Spacy tags "our" and "my" as determiners - run with out tags

	pp1 = "i we us me ourselves myself".split(" ") # previously tagged as pronouns "our my your thy thine their his her".split()
	pp2 = "you yourself ya thee".split(" ")
	pp3 = "he she they them him themselves himself herself it".split(" ") #no "it" following Biber et al., 2004
	pp_sg = "i me myself you ya thee he she his her him himself herself it".split(" ")
	pp_pl = "us ourselves they them themselves".split() #not sure how we want to deal with "they"
	
	pp_all = pp1+pp2+pp3 #+pp3_it
	
	if token.word.lower() in pp_all:
		token.lxgrtag = "pro"
	if token.word.lower() in pp1:
		token.cat1 = "1st"
	elif token.word.lower() in pp2:
		token.cat1 = "2nd"
	elif token.word.lower() in pp3:
		token.cat1 = "3rd"
	if token.word.lower() in pp_sg:
		token.cat2 = "sg"
	elif token.word.lower() in pp_pl:
		token.cat1 = "pl"


def advanced_pronoun(token,sent):	#updated 2022-11-02
	demonstrative_list = ["this","that","these","those"]
	sg = ["this","that"]
	pl = ["these","those", "ones"]

	indefinite_l = "everybody everyone everything somebody someone something anybody anyone anything nobody noone none nothing one ones".split(" ")
	indef_pl = "ones" #double check this 
	#note that "one" captures "no one"
	#indefinite list from Longman grammar pp. 352-355
	
	if token.word.lower() in indefinite_l and token.deprel in ["nsubj","nsubjpass","dobj","pobj"]:
		token.lxgrtag = "pro"
		token.cat1 = "other" #consider changing to "indefinite"
		
		if token.word.lower() in indef_pl:
			token.cat2 = "pl"
		else:
			token.cat2 = "sg"

	#determining whether demonstrative pronouns are actually being used as demonstrative can be tricky using spacy:
	elif token.word.lower() in demonstrative_list and token.deprel in ["nsubj","nsubjpass","dobj","pobj"]: 
		if token.deprel == "advmod":
			token.lxgrtag = "pro"
			token.cat1 = "dem"
			if token.word.lower() in sg:
				token.cat2 = "sg"
			else:
				token.cat2 = "pl"

		elif token.idx + 1 < len(sent) and sent[token.idx + 1].word.lower() in ["who",".","!","?",":"]:
			token.lxgrtag = "pro"
			token.cat1 = "dem"
			if token.word.lower() in sg:
				token.cat2 = "sg"
			else:
				token.cat2 = "pl"
		
		elif token.deprel == "nsubjpass":
			token.lxgrtag = "pro"
			token.cat1 = "dem"
			if token.word.lower() in sg:
				token.cat2 = "sg"
			else:
				token.cat2 = "pl"

		elif token.deprel == "pobj":
			token.lxgrtag = "pro"
			token.cat1 = "dem"
			if token.word.lower() in sg:
				token.cat2 = "sg"
			else:
				token.cat2 = "pl"
				
		elif token.deprel in ["nsubj","dobj"]:
			token.lxgrtag = "pro"
			token.cat1 = "dem"
			if token.word.lower() in sg:
				token.cat2 = "sg"
			else:
				token.cat2 = "pl"

def prepositions(token,sent):
	if token.deprel == "prep":
		token.lxgrtag = "in"
		if sent[token.headidx].upos in ["VERB","AUX"]:
			token.cat1 = "advl"
		elif sent[token.headidx].upos in ["NOUN","PROPN","PRON"]:
			token.cat1 = "nmod"
		elif sent[token.headidx].upos == "ADJ":
			token.cat1 = "jcomp"
		else:
			token.cat1 = "in_othr"

def coordinators(token,sent): #takes spacy's definition of "cc"
	if token.deprel == "cc":
		token.lxgrtag = "cc"
		if sent[token.headidx].upos in ["NOUN", "ADJ", "ADV", "PRON", "PROPN", "PART"]:
			token.cat1 = "phrs"
		elif sent[token.headidx].upos in ["VERB","AUX"]:
			ccl = [x.idx for x in sent if x.deprel == "conj" and x.headidx == token.headidx] #and len([y.deprel for y in sent if y.headidx == sent[token.headidx].headidx and y.deprel in ["nsubj","csubj"]]) > 0 ]) != 0:
			if token.idx == 0: #sentence initial ccs
				token.cat1 = "cls"
			elif len (ccl) > 0 and len([x for x in sent if x.headidx == ccl[0] and x.deprel in ["csubj","nsubj"]]) > 0:
				token.cat1 = "cls"
			else:
				token.cat1 = "phrs"

def subordinators(token):
	if token.deprel == "mark" and token.word.lower() not in ["that", "which","who","whom","whose","what","how","where","why","when"]:
		token.lxgrtag = "cs"
		if token.word.lower() == "because":
			token.cat1 = "cos" #causitive
		elif token.word.lower() in ["if","unless"]:
			token.cat1 = "cnd" #conditional
		elif token.word.lower() in ["though","although","while"]:
			token.cat1 = "con" #concessive
		else:
			token.cat1 = "cs_othr"

def determiners(token):
	demonstrative_list = ["this","that","these","those"]
	if token.deprel == "det":
		token.lxgrtag = "dt"
		if token.word.lower() in demonstrative_list:
			token.cat1 = "dt_dem"
		if token.word.lower() in ["a","the"]:
			token.cat1 = "art"
	if token.deprel == "poss":
		token.lxgrtag = "dt"
		token.cat1 = "poss"

def that_wh(token,sent):
	if token.word.lower() == "that" and token.deprel in ["nsubj","mark"]:

		if sent[token.headidx].deprel in ["relcl","acl"]:
			token.lxgrtag = "relpro"
			token.cat1 = "relpro_that"
		if sent[token.headidx].deprel  in ["ccomp","csubj"]:
			token.lxgrtag = "comp"
			token.cat1 = "comp_that"
	
	if token.word.lower() in ["which","who","whom","whose","what","how","where","why","when"] and token.deprel in ["nsubj","mark","attr"]:
		if sent[token.headidx].deprel in ["relcl","acl"]:
			token.lxgrtag = "relpro"
			token.cat1 = "relpro_wh"
		if sent[token.headidx].deprel  in ["ccomp","csubj"]:
			token.lxgrtag = "comp"
			token.cat1 = "comp_wh"

#############################

#### These functions use the previous functions to conduct tagging and tallying of lexicogramamtical features ###

def preprocess(text): #takes raw text, processes with spacy, then outputs a list of sentences filled with tokenObjects
	output = []
	doc = nlp(text)
	for sent in doc.sents:
		sentl = []
		sidx = 0 #within sentence idx
		firstWord = True #check for first word
		for token in sent:
			#print(token.idx)
			if firstWord == True: #check for first word in sentence
				sstartidx = token.i #set to document position of first token in sentence
				firstWord = False
			#print(sstartidx)
			tok = tokenInfo(token)
			tok.idx = sidx
			tok.headidx = tok.headidx - sstartidx #adjust heads from document position to sentence position
			sidx += 1
			sentl.append(tok)
		output.append(sentl)
	return(output)

def tag(sstring): #tags :)
	sents = []
	for sent in preprocess(sstring):
		for token in sent:
			personal_pronouns(token)
			advanced_pronoun(token,sent)
			adverbs(token,sent)
			adjectives(token)
			nouns(token)
			verbs(token,sent)
			prepositions(token,sent)
			coordinators(token,sent)
			subordinators(token)
			determiners(token)
			that_wh(token,sent)
		sents.append(sent)
	return(sents)

def printer(loToks):
	for sent in loToks:
		for token in sent:
			print(token.idx, token.word, token.lemma, token.lxgrtag, token.cat1,token.cat2,token.cat3, token.cat4, token.cat5, token.cat6, token.cat7, token.cat8, token.xpos, token.upos, token.deprel,token.headidx)

def writer(outname,loToks,joiner = "\t"):
	outf = open(outname,"w")
	docout = []
	for sent in loToks:
		sentout = []
		for token in sent:
			tokenout = []
			items = [token.idx,token.word,token.lemma,token.lxgrtag, token.cat1,token.cat2,token.cat3, token.cat4, token.cat5, token.cat6, token.cat7, token.cat8, token.xpos, token.upos, token.deprel,token.headidx]
			for item in items:
				if item == None:
					tokenout.append("")
				else:
					tokenout.append(str(item))
			sentout.append(joiner.join(tokenout))
		docout.append("\n".join(sentout))

	outf.write("\n\n".join(docout))
	outf.flush()
	outf.close()