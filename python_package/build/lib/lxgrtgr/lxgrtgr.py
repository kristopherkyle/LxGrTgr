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
version = "0.0.5.46"
version_notes = "0.0.5.46 - work on thatcls+vcomp and whcls+vcomp - coordinated verb phrases and multi-word wh-complementizers"

# 0.0.5.9 - update jj+that+jcomp definition, check verb_+_wh [seems OK], update "xtrapos+jj+that+compcls"
# 0.0.5.10 - update Make adverbial clauses ("finite_advl_cls")more general - narrow later
# "0.0.5.35 - add semi-modals"
import glob #for finding all filenames in a folder
import os #for making folders
# from xml.dom import minidom #for pretty printing
# import xml.etree.ElementTree as ET #for xml parsing
from random import sample #for random samples
import re #for regulat expressions
from importlib_resources import files #for opening package files - need to include in package dependencies

### spacy
print("Importing Spacy")
import spacy #base NLP
print("Spacy Successfully Loaded")
# from spacy.tokens import Doc
# from spacy.language import Language
#nlp = spacy.load("en_core_web_sm") #load model
print("Loading Transformer Model")
nlp = spacy.load("en_core_web_trf")  #load model
print("Transformer Model Successfully Loaded")
nlp.max_length = 1728483 #allow more characters to be processed than default. This allows longer documents to be processed. This may need to be made longer.

#the following is only used when attempting to align outputs

# class WhitespaceTokenizer(object):
# 	def __init__(self, vocab):
# 		self.vocab = vocab

# 	def __call__(self, text):
# 		words = text.split(' ')
# 		# All tokens 'own' a subsequent space character in this tokenizer
# 		spaces = [True] * len(words)
# 		return Doc(self.vocab, words=words, spaces=spaces)

# nlp.tokenizer = WhitespaceTokenizer(nlp.vocab) #force pre-existing tokenization

######################################################

### Load lists, etc. #################################
# nominal_stop = files('lists_LGR').joinpath('nom_stop_list_edited.txt').read_text().strip().split("\n")
# prepVerbList = files('lists_LGR').joinpath('prepVerbList.txt').read_text().strip().split("\n")

# for Python package:
nominal_stop = files('lxgrtgr').joinpath('nom_stop_list_edited.txt').read_text().strip().split("\n")
prepVerbList = files('lxgrtgr').joinpath('prepVerbList.txt').read_text().strip().split("\n")

# for web access and pc access:
# os.chdir('/Users/kristopherkyle/Desktop/Programming/GitHub/LCR-ADS-Lab/LxGrTgr/')
# nominal_stop = open("lists_LGR/nom_stop_list_edited.txt").read().split("\n") # created based on frequently occuring nouns with [potential] nominalizer suffixes in TMLE + T2KSWAL
# prepVerbList = open("lists_LGR/prepVerbList.txt").read().split("\n") # From LGSWE; currently ignored in favor of OntoNotes classifications
#phrasalVerbList = open("lists_LGR/phrasalVerbList.txt").read().split("\n") # From LGSWE
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
		self.headdeprel = spacyToken.head.dep_
		#self.children = spacyToken.children
		self.cxtag = None #Biber et al's complexity tags
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

class tokenBlank(): #empty token to fill
	def __init__(self): 
		self.idx = None #will have to add this from position in sentence
		self.word = None #raw text
		self.lemma = None #lowered lemma form
		self.upos = None #Universal part of speech
		self.xpos = None #penn tag
		self.deprel = None #dependency relation (based on CLEAR tagset)
		self.head = None#.text #text of head
		self.headidx = None #id of head
		self.headdeprel = None
		#self.children =None
		self.cxtag = None #Biber et al's complexity tags
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

class sentBlank():
	def __init__(self):
		self.meta = []
		self.tokens = []

### Linguistic Analysis Functions ###
def nouns(token,nominalStopList = nominal_stop): #revised 2022-11-22; This is probably overly greedy. It was filtered using frequent candidates in T2KSWAL and TMLE
	if token.xpos[:2] == "NN":
	#if token.upos in ["NOUN", "PROPN"]:
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
		if token.xpos[:3] == "NNP":
		#if token.upos == "PROPN":
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
		#To Do: Add code to catch coordinated adjectives (spacy represents this as a "conj" chain)
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
		if token.deprel == "advmod" and sent[token.headidx].xpos[:2] == "VB":
			if token.word.lower() in linking and token.idx < token.headidx: #if the word can be a linking adverb and occurs before the main verb:
				token.cat1 = "link"
			else:
				token.cat1 = "advl"
		elif token.deprel == "advmod" and  sent[token.headidx].deprel in ["acomp","amod"]: #amod added 20240710
			token.cat1 = "adjmod"
		#need to add additional criteria for "advl" here, but also need to exclude multi-word adverbs
		
		#split aux section:
		for tkn in sent:
			if tkn.headidx == token.headidx:
				if tkn.deprel == "aux" and tkn.idx < token.idx:
					if token.idx < token.headidx and sent[token.headidx].xpos[:2] == "VB":
						token.cat3 = "splaux"
						break
	if token.deprel == "prt" and token.headidx < token.idx: #check for particles, make sure they aren't infinitive "to"
		token.lxgrtag = "rb"
		token.cat1 = "prtcle"
	if token.lxgrtag == "rb" and token.cat1 == None:
		token.cat1 = "othr"
	#deal with multiword wh-subordinators
	if token.word.lower() in ["well"] and len([x.word for x in sent if x.cat1 in ["comp_wh"] and x.headidx == token.idx]) > 0:
		token.lxgrtag = None
		token.cat1 = None

def verbInfo(token,sent): #this is to help solve a problem with conjugated verb phrases
	cat2 = None
	#this is an ordered list of POS tags for the main verb and auxs represented in the VP
	if token.xpos[:2] in ["VB","MD"] and token.deprel not in ["amod","acomp","aux","auxpass"]:
		vp_pos = [x.xpos for x in sent if (x.headidx == token.idx and x.deprel in ["aux","auxpass"]) or x.idx == token.idx]
		#print(vp_pos)
		if "MD" in vp_pos:
			cat2 = "vp_w_modal"
		elif "VBZ" in vp_pos:
			cat2 = "pres"
		elif "VBP" in vp_pos:
			cat2 = "pres"
		elif "VBD" in vp_pos:
			cat2 = "past"
		elif len([x.word.lower() for x in sent if x.headidx == token.idx and x.deprel in ["nsubj","nsubjpass"]]) > 0 and token.xpos == "VBN":
			cat2 = "past" #if a seeming -ed clause has a subject, count it as finite
		else:
			cat2 = "nonfinite" #probably need more testing here
	return(cat2)

def verbs(token,sent): #need to add spearate tags for tense/aspect and passives
	that0_list = "check consider ensure illustrate fear say assume understand hold appreciate insist feel reveal indicate wish decide express follow suggest saw direct pray observe record imagine see think show confirm ask meant acknowledge recognize need accept contend come maintain believe claim verify demonstrate learn hope thought reflect deduce prove find deny wrote read repeat remember admit adds advise compute reach trust yield state describe realize expect mean report know stress note told held explain hear gather establish suppose found use fancy submit doubt felt".split(" ")
	
	#don't tag verbs functioning as adjectives as verbs; only tag main verbs
	if token.xpos[:2] in ["VB","MD"] and token.deprel not in ["amod","acomp","aux","auxpass"]: #added "MD" to account for sentences such as "I think I probably could"
	#if token.upos in ["VERB","AUX"] and token.deprel not in ["amod","acomp","aux","auxpass"]: 
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
		elif len([x.word.lower() for x in sent if x.headidx == token.idx and x.deprel in ["nsubj","nsubjpass"]]) > 0 and token.xpos == "VBN":
			token.cat2 = "past" #if a seeming -ed clause has a subject, count it as finite
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
		if token.deprel in ["ccomp","csubj","pcomp","xcomp"]: 
			token.cat5 = "compcls"
		elif token.deprel == "advcl":
			if sent[token.headidx].xpos[:2] in ["JJ"]:
				token.cat5 = "jmod_cls"
			else:
				token.cat5 = "advlcls"
		elif token.deprel in ["relcl"]:
			token.cat5 = "nmod_cls"
		elif token.deprel in ["acl"]: #updated 2024-10-01
			if sent[token.headidx].upos in ["NOUN","PROPN","PRON"]:
				token.cat5 = "nmod_cls"
			elif sent[token.headidx].xpos[:2] in ["JJ"]:
				token.cat5 = "jmod_cls"
		# elif sent[token.headidx].upos in ["NOUN","PROPN","PRON"]:
		# 	token.cat5 = "nmod_cls"

		#####################
		### cat6 analysis ###
		#####################

		### that ###
		if "that" in [x.word.lower() for x in sent if x.word.lower() == "that" and x.headidx == token.idx and x.deprel in ["mark","nsubj","nsubjpass"]]:
			if token.cat5 in ["nmod_cls"]:
				token.cat6 = "thatcls"

		if "that" in [x.word.lower() for x in sent if x.word.lower() == "that" and x.headidx == token.idx and x.deprel == "mark"]:
			if token.cat5 in ["compcls","jmod_cls"]:
				token.cat6 = "thatcls"

		### wh clause: ###
		if token.cat5 in ["compcls","nmod_cls","advlcls"]:
			if len([x.word.lower() for x in sent if x.headidx == token.idx and x.deprel in ["nsubj","nsubjpass","advmod","attr","dep"] and x.xpos in ["WDT","WP", "WP$", "WRB"] and x.word.lower() != "that"]) > 0: #note that "dep" might cause issues. added on 2024-10-03
				token.cat6 = "whcls"
			######
			# catch "wh" words that are attached to another verb in the verb phrase [updated on 20241028]
			conjDepList = [x.idx for x in sent if x.headidx == token.idx and x.deprel in ["conj"] and verbInfo(x,sent) in ["nonfinite"]]
			if len(conjDepList) > 0:
				if len([x.word.lower() for x in sent if x.headidx == conjDepList[-1] and x.deprel in ["nsubj","nsubjpass","advmod","attr","dep"] and x.xpos in ["WDT","WP", "WP$", "WRB"] and x.word.lower() != "that"]) > 0:
					token.cat6 = "whcls"
			######
		if token.cat2 == "nonfinite":
			### to clause ###
			if "to" in [x.word.lower() for x in sent if x.headidx == token.idx and x.idx < token.idx and x.xpos == "TO" and sent[x.idx-1].lemma not in ["order"]]: #and sent[x.idx-1].lemma not in ["seem","have","need","want","order"] Doug didn't like these as semi-modals - kept in "order" to catch "in order to"
			#if "to" in [x.word.lower() for x in sent if x.headidx == token.idx and x.idx < token.idx and x.upos == "PART"]:
				token.cat6 = "tocls" #probably needs more work
			### ing clause ###
			if token.xpos == "VBG":
				token.cat6 = "ingcls"
			
		### ed clause ###
		if token.xpos == "VBN" and token.cat4 == "active" and token.cat3 != "perf" and token.cat2 == "nonfinite":
			prevTok = sent[token.idx - 1]
			if prevTok.headidx == token.idx and prevTok.xpos == "VBG":
				token.cat6 = "ingcls"
			else:
				token.cat6 = "edcls"


		#####################
		### cat7 analysis ###
		#####################
		if token.cat5 == "compcls":
			if sent[token.headidx].xpos[:2] == "VB" and token.idx != token.headidx:
			#if sent[token.headidx].upos in ["VERB","AUX"] and token.idx != token.headidx:
				token.cat7 = "vcomp"
			elif sent[token.headidx].xpos[:2] == "JJ":
				if "so" in [x.word.lower() for x in sent if x.headidx == token.headidx and x.idx < token.idx]:
				# if token.headidx > 0 and sent[token.headidx-1].word.lower() in ["so"]:
					token.cat7 = "jcomp+comparative"
				else:
					token.cat7 = "jcomp"

			elif sent[token.headidx].xpos in ["NN","NNS","NNP","NNPS","PRP"]:
			#elif sent[token.headidx].upos in ["NOUN","PROPN","PRON"]:
				token.cat7 = "ncomp"
			elif token.deprel == "pcomp":
				token.cat7 = "incomp"
		
		if token.cat5 == "nmod_cls": #finish fixing this
			if token.deprel == "relcl":
				token.cat7 = "rel"
			elif token.deprel in ["acl"]:
				if sent[token.headidx].upos in ["NOUN","PROPN","PRON"]: #this may be too restrictive; updated 20241001
					token.cat7 = "ncomp"
		if token.cat5 in ["jmod_cls"] and sent[token.headidx].xpos[:2] == "JJ":
			if "so" in [x.word.lower for x in sent if x.headidx == token.headidx and x.idx < token.idx]:
			# if token.headidx > 0 and sent[token.headidx-1].word.lower() in ["so"]:
				token.cat7 = "jcomp+comparative"
			else:
				token.cat7 = "jcomp"
		
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
				#print(token.word,[x.deprel for x in sent if x.headidx == token.idx and x.idx < token.idx and x.word.lower() in ["that","who","which", "what","how","where","why","when","whose","whom","whomever"]])
				if len([x.deprel for x in sent if x.headidx == token.idx and x.idx < token.idx and x.word.lower() in ["that","who","which", "what","how","where","why","when","whose","whom","whomever"]]) == 0:
					token.cat8 = "reldel"
			#this next part is causing problems, because it gives a "0" more often that intended. need to revise it
			elif len ([x.word.lower() for x in sent if x.headidx == token.idx and x.deprel in ["nsubj","nsubjpass"]]) > 0: #if there is a subject
				if len([x.word.lower() for x in sent if x.headidx == token.idx and x.word.lower() in ["that","who","which","what","how","where","why","when","whose","whom","whomever"]]) == 0:
					token.cat8 = "reldel"
			# elif len ([x.word.lower() for x in sent if x.headidx == token.idx and x.deprel in ["nsubj","nsubjpass"] and x.word.lower() in ["that","who","which","what","how","where","why","when","whose","whom","whomever"]]) == 0:
			# 	token.cat8 = "reldel"
		
		### complementizer deletion ###
		if token.cat5 == "compcls" and token.cat6 not in ["tocls","ingcls","thatcls","whcls"]:
			quote = False
			question = False
			quote_scope = [int(x.idx) for x in sent if x.headidx == token.headidx and x.xpos in ['``']]
			if len(quote_scope) >= 2: #maybe add category for quoted speech
				quote_scope_idxl = list(range(quote_scope[0],quote_scope[1]))
				if int(token.idx) in quote_scope_idxl and int(token.headidx) in quote_scope_idxl:
					quote = False 
				else:
					quote = True
			elif len(quote_scope) == 1:
				dep_scope_idxl = list(range(int(token.headidx),int(token.idx)))
				if quote_scope[0] in dep_scope_idxl:
					quote = True
			#have/do question syntax
			clausedeps = [x for x in sent if x.headidx == token.idx]
			for indx,x in enumerate(clausedeps):
				if x.deprel == "aux" and x.lemma in ["have","do"]:
					if indx + 1 < len(clausedeps):
						if clausedeps[indx+1].deprel in ["nsubj","nsubjpass"]:
							question = True


			# if "?" not in [x.word for x in sent] and sent[token.headidx].lemma not in ["say"]: #add category for questions? 
			# 	question = True
			if quote == False and question == False:
				token.cat8 = "compdel"

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
		if token.xpos[:2] not in ["VB"]:
			token.lxgrtag = "in"
		if sent[token.headidx].xpos[:2] == "VB":
		#if sent[token.headidx].upos in ["VERB","AUX"]:
			token.cat1 = "advl"
		elif sent[token.headidx].xpos in ["NN","NNS","NNP","NNPS","PRP"]:
		#elif sent[token.headidx].upos in ["NOUN","PROPN","PRON"]:
			token.cat1 = "nmod"
		elif sent[token.headidx].xpos in ["CD","DT","JJ","JJS"] and sent[token.headidx].deprel in ["nsubj","nsubjpass","dobj","pobj"]: #may need to refine this
			token.cat1 = "nmod"
		elif sent[token.headidx].xpos[:2] == "JJ":
		#elif sent[token.headidx].upos == "ADJ":
			token.cat1 = "jcomp"
		else:
			token.cat1 = "in_othr"

def coordinators(token,sent): #takes spacy's definition of "cc"
	if token.deprel == "cc":
		token.lxgrtag = "cc"
		if sent[token.headidx].xpos[:2] in ["NN", "JJ", "RB", "PR", "RP"]:
		#if sent[token.headidx].upos in ["NOUN", "ADJ", "ADV", "PRON", "PROPN", "PART"]:
			token.cat1 = "phrs"
		elif sent[token.headidx].xpos[:2] == "VB":
		#elif sent[token.headidx].upos in ["VERB","AUX"]:
			ccl = [x.idx for x in sent if x.deprel == "conj" and x.headidx == token.headidx] #and len([y.deprel for y in sent if y.headidx == sent[token.headidx].headidx and y.deprel in ["nsubj","csubj"]]) > 0 ]) != 0:
			if token.idx == 0: #sentence initial ccs
				token.cat1 = "cls"
			elif len (ccl) > 0 and len([x for x in sent if x.headidx == ccl[0] and x.deprel in ["csubj","nsubj"]]) > 0:
				token.cat1 = "cls"
			else:
				token.cat1 = "phrs"

def subordinators(token,sent):
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
	if token.word.lower() == "that" and token.deprel == "mark" and sent[token.headidx].deprel == "advcl":
		#print("found it!!")
		token.lxgrtag = "cs"
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

def that_wh(token,sent): #tweaked version
	if token.word.lower() == "that" and token.deprel in ["nsubj","nsubjpass","mark"]:

		if sent[token.headidx].deprel in ["relcl"]: #updated 20241001
			token.lxgrtag = "relpro"
			token.cat1 = "relpro_that"
		elif sent[token.headidx].deprel in ["acl"]: #updated 20241001
			if sent[sent[token.headidx].headidx].upos in ["NOUN","PROPN","PRON"]: #this may be too restrictive; updated 20241001
				token.lxgrtag = "relpro"
				token.cat1 = "relpro_that"
			elif sent[sent[token.headidx].headidx].xpos[:2] == "JJ": #updated 20241001
				token.lxgrtag = "comp"
				token.cat1 = "comp_that"
			#sent[token.headidx].cat8 = None
		elif sent[token.headidx].deprel in ["ccomp","csubj"] and token.deprel == "mark":
			token.lxgrtag = "comp"
			token.cat1 = "comp_that"
			#sent[token.headidx].cat8 = None
	
	if token.word.lower() in ["which","who","whom","whose","what","how","where","why","when"] and token.deprel in ["nsubj","nsubjpass","mark","attr"]:
		if sent[token.headidx].deprel in ["relcl","acl"]:
			token.lxgrtag = "relpro"
			token.cat1 = "relpro_wh"
			#sent[token.headidx].cat8 = None
	elif token.word.lower() in ["which","who","whom","whose","what","how","where","why","when"] and token.deprel in ["nsubj","nsubjpass","mark","attr","advmod","dobj"]:
		if sent[token.headidx].deprel in ["ccomp","csubj","pcomp"]:
			sent[token.headidx].cat6 = "whcls"
			token.lxgrtag = "comp"
			token.cat1 = "comp_wh"
		elif sent[token.headidx].deprel in ["advmod"] and sent[token.headidx].deprel in ["advmod"] and sent[token.headidx].word.lower() in ["well"]:
			sent[sent[token.headidx].headidx].cat6 = "whcls"
			token.lxgrtag = "comp"
			token.cat1 = "comp_wh"
			# sent[token.headidx].lxgrtag = None #do not treat "well" as adverb
			# sent[token.headidx].cat1 = None #do not treat "well" as adverb



			#sent[token.headidx].cat8 = None

def complexity(token,sent):
	# will return to speciic types of advcl in a future version
	# if token.cat7 in ["conditional","causative","concessive"]:
	# 	token.cxtag = "cnd|cos|con+cls" #this name can be changed
	if token.cat5 in ["advlcls"] and token.cat2 not in ["nonfinite"]:
		token.cxtag = "finitecls+advl"
	if token.cat7 in ["vcomp"] and token.idx > token.headidx and token.cat2 not in ["nonfinite"]: #if a finite clause comes after the verb 
		if token.cat6 in ["thatcls"]: #Verb + that complement clause
			token.cxtag = "thatcls+vcomp" #this name can be changed
		elif token.cat8 in ["compdel"]: #Verb + that complement clause (with deletion)
			token.cxtag = "thatcls+vcomp" #this name can be changed
		elif token.cat6 in ["whcls"]: #verb + Wh clause
			token.cxtag = "whcls+vcomp"
	
	#updated 2024-02-14
	if token.cxtag in ["thatcls+vcomp","whcls+vcomp"] and sent[token.headidx].lemma == "be" and "acomp" in [x.deprel for x in sent if x.headidx == token.headidx] and "it" in [x.lemma for x in sent if x.headidx == token.headidx and x.deprel in ["nsubj","nsubjpass"]]:	#could be simpler/clearer to also identify "it" as the nsubject	
		token.cxtag = "xtrapos+thatcls+jcomp"
		token.cat7 = "jcomp"
	
	if token.cat5 in ["nmod_cls"] and token.cat2 not in ["nonfinite"]: #this may need to be more restrictive
		if token.cat7 in ["rel"]:
			token.cxtag = "finitecls+rel" #verb + finite relative clause
		if token.cat7 in ["ncomp"]:
			if token.cat6 in ["thatcls"]:
				token.cxtag = "thatcls+ncomp" #verb + finite complement clause
			elif token.cat8 in ["compdel"]:
				token.cxtag = "thatcls+ncomp" #verb + finite complement clause
	
	if token.cat5 in ["compcls","acl","jmod_cls"] and token.cat7 in ["jcomp"] and token.idx > token.headidx:
		if token.cxtag != "xtrapos+thatcls+jcomp":
			if token.cat6 in ["thatcls"]:
				token.cxtag = "thatcls+jcomp"
			elif token.cat8 in ["compdel"]:
				token.cxtag = "thatcls+jcomp"
		
	
	if token.cat7 in ["incomp"] and token.cat6 in ["whcls"]:
		token.cxtag = "whcls+incomp" #Preposition + wh complement clause
	
	if token.cat5 in ["advlcls"] and token.cat6 in ["tocls"]:
		token.cxtag = "tocls+advl"

	if token.cat5 in ["advlcls"] and token.cat6 in ["ingcls"]:
		token.cxtag = "ingcls+advl"

	if token.cat5 in ["advlcls"] and token.cat6 in ["edcls"]:
		token.cxtag = "edcls+advl"

	if token.cat1 in ["advl"] and token.cat6 in ["edcls"]:
		token.cxtag = "edcls+advl"
	
	if token.cat6 in ["tocls"] and token.deprel in ["xcomp"]: #may need more refining
		if sent[token.headidx].upos in ["VERB"]: #updated 2024-10-08
			token.cxtag = "tocls+vcomp"
		elif sent[token.headidx].upos in ["NOUN"]: #need to further test this
			token.cxtag = "tocls+rel" 

	if token.cat6 in ["ingcls"] and token.deprel in ["xcomp"]:
		if sent[token.headidx].upos in ["VERB"]: #updated 2024-10-08
			token.cxtag = "ingcls+vcomp"
		elif sent[token.headidx].upos in ["NOUN"]: #need to further test this
			token.cxtag = "ingcls+rel"
	
	if token.cat5 in ["nmod_cls"] and token.cat6 in ["edcls"] and token.cat7 in ["rel","ncomp"]:
		token.cxtag = "edcls+rel"

	if token.cat5 in ["nmod_cls"] and token.cat6 in ["ingcls"] and token.cat7 in ["rel","ncomp"]:
		token.cxtag = "ingcls+rel"

	if token.cat5 in ["nmod_cls"] and token.cat6 in ["tocls"] and token.cat7 in ["rel"]:
		token.cxtag = "tocls+rel"

	if token.cat5 in ["nmod_cls"] and token.cat6 in ["tocls"] and token.cat7 in ["ncomp"]:
		token.cxtag = "tocls+ncomp"
	
	if token.cat5 in ["compcls"] and token.cat6 in ["tocls"]: 
			if token.cat7 in ["jcomp", "vcomp"] and sent[token.headidx].lemma == "be" and "acomp" in [x.deprel for x in sent if x.headidx == token.headidx] and "it" in [x.lemma for x in sent if x.headidx == token.headidx and x.deprel in ["nsubj","nsubjpass"]]: #the "jcomp" might not be necessary
				token.cxtag = "xtrapos+tocls+jcomp"
			elif token.cat7 in ["jcomp"]:
				token.cxtag = "tocls+jcomp"

	if token.cat6 in ["ingcls"] and token.cat7 in ["incomp"]:
		token.cxtag = "ingcls+incomp"
	
	if token.cat1 in ["advl"]:
		if token.lxgrtag in ["in"]:
			token.cxtag = "in+advl"
		elif token.lxgrtag in ["rb"] and token.xpos not in ["WRB"]:
			token.cxtag = "rb+advl"
	
	#print(token.idx, token.cat1, token.headidx, sent[token.headidx].lxgrtag)
	if sent[token.headidx].xpos[:2] == "NN":
		if token.cat1 in ["attr"] and token.idx < token.headidx:
			token.cxtag = "attr+npremod"
		if token.cat3 in ["npremod"]:
			if token.xpos in ["NNP","NNPS"] and sent[token.headidx].xpos in ["NNP","NNPS"]:
				nnpremod = False #this is a dummy/unused variable
			else:
				token.cxtag = "nn+npremod" #this tag is probably redundant
	elif token.deprel in ["conj"] and token.xpos in ["JJ","VBN"] and sent[token.headidx].cxtag == "attr+npremod":
		token.cat1 = "attr"
		token.cxtag = "attr+npremod"
	#To-Do: add code to catch coordinated premodifying adjective phrases (they form a chain of "conj" relations)
	if token.lxgrtag in ["in"] and token.headdeprel not in ["npadvmod"]: #the "and" statement is an attempt to avoid constructions such as "bit by bit" and "sentence to sentence" being counted here 
		if token.idx > token.headidx and token.cat1 in ["nmod"]:
			if token.lemma == "of":
				token.cxtag = "of+npostmod"
			else:
				token.cxtag = "in+npostmod"
		if token.cat1 in ["jcomp"]:
			if sent[token.headidx].xpos in ["JJR"] and token.lemma == "than":
				token.cxtag = "in+comparative" #not currently used anywhere
			else:
				token.cxtag = "in+jcomp"
	
	citations = ["figure", "table", "p", "pp", "p.", "pp.","page"] #this will probbaly need to be further refined
	excludeNNP = False
	if token.xpos in ["NNP","NNPS"] and sent[token.headidx].xpos in ["NNP","NNPS"]:
		excludeNNP = True #exclude city, state, but not "his son, Jack, "
	if token.lxgrtag in ["nn"] and token.cat3 in ["nappos"]:
		if token.lemma not in citations and sent[token.headidx].lemma not in citations and excludeNNP == False:
			token.cxtag = "appos+npostmod"
	
	if token.lxgrtag in ["rb"] and token.lemma not in ["as","how"]: #"as" to avoid comparatives;"how" to avoid "WH" words. May need to add others.
		if token.cat1 in ["adjmod"]: 
			token.cxtag = "rb+jjrbmod"
		if sent[token.headidx].xpos in ["RB","RBR","JJ","CD"] and token.deprel in ["advmod"]: 
			token.cxtag = "rb+jjrbmod"
	if token.cat3 in ["sgen"]: #added in v 05_08
		token.cxtag = "s+gen"

def changeToModal(token,sent,targetidx = 2):
	sent[token.idx-targetidx].lxgrtag = "vbaux" #change main tag
	sent[token.idx-targetidx].cat1 = "semimod" #change cat1 tag
	token.cxtag = sent[token.idx-targetidx].cxtag #reassign cxtag
	token.cat2 = "vp_w_modal" #reassign category tag
	token.cat3 = sent[token.idx-targetidx].cat3 #reassign category tag
	#token.cat4 = sent[token.idx-targetidx].cat4 #reassign category tag
	token.cat5 = sent[token.idx-targetidx].cat5 #reassign category tag
	token.cat6 = sent[token.idx-targetidx].cat6 #reassign category tag
	token.cat7 = sent[token.idx-targetidx].cat7 #reassign category tag
	token.cat8 = sent[token.idx-targetidx].cat8 #reassign category tag
	
	#deal with complementizer deletion issues
	if token.cat8 == "compdel":
		if "that" in [x.word.lower() for x in sent if x.word.lower() == "that" and x.headidx == token.idx and x.deprel in ["mark","nsubj","nsubjpass"]]:
			if token.cat5 in ["nmod_cls"]:
				token.cat6 = "thatcls"
				token.cat8 = None

		if "that" in [x.word.lower() for x in sent if x.word.lower() == "that" and x.headidx == token.idx and x.deprel == "mark"]:
			if token.cat5 in ["compcls","jmod_cls"]:
				token.cat6 = "thatcls"
				token.cat8 = None

		### wh clause: ###
		if token.cat5 in ["compcls","nmod_cls","advlcls"]:
			if len([x.word.lower() for x in sent if x.headidx == token.idx and x.deprel in ["nsubj","nsubjpass","advmod","attr","dep","dobj"] and x.xpos in ["WDT","WP", "WP$", "WRB"] and x.word.lower() != "that"]) > 0: #note that "dep" might cause issues. added on 2024-10-03
				token.cat6 = "whcls"
				token.cat8 = None
		
		if token.cat7 in ["vcomp"]:
			if token.cat6 == "whcls":
				token.cxtag = "whcls+vcomp"
			elif token.cat6 == "thatcls":
				token.cxtag = "thatcls+vcomp"
	#add cat8?
	sent[token.idx-targetidx].cxtag = None #clean up old tags
	sent[token.idx-targetidx].cat2 = None #clean up old tags
	sent[token.idx-targetidx].cat3 = None #clean up old tags
	sent[token.idx-targetidx].cat4 = None #clean up old tags
	sent[token.idx-targetidx].cat5 = None #clean up old tags
	sent[token.idx-targetidx].cat6 = None #clean up old tags
	sent[token.idx-targetidx].cat7 = None #clean up old tags
	sent[token.idx-targetidx].cat8 = None #clean up old tags

def semiModalAdjust(token,sent): #adjust tags based on semi-modals
	if token.lxgrtag in ["vbmain"]:
		passive = False
		threeWord = False
		semiModalL = ["have to","had to","got to", "ought to"]
		# already treated by spacy as modal: ["got ta","gon na"]
		# "gon na" causes issues - future development could iron out these bugs
		semiModalThreeL = ["have got to", "had got to"]
		semModalBeL = ["be supposed to","be going to"]
		semModalAboutTo = ["be about to"]
		semModalUsedTo = ["used to"]
		#Need to add rules to deal with passive constructions
		if token.idx >=1 and sent[token.idx-1].lemma == "be" and sent[token.idx-1].deprel in ["auxpass"]:
			passive = True
			if token.idx >= 4:
				modTestL = sent[token.idx-4:token.idx-1]
				modTestStr = " ".join([x.word.lower() for x in modTestL])
				modTestBeStr = " ".join([modTestL[0].lemma.lower(),modTestL[1].word.lower(),modTestL[2].word.lower()])
				if modTestStr in semiModalThreeL: #make adjustments
					threeWord = True
					changeToModal(token,sent,3) #make changes
				elif modTestBeStr in semModalBeL:
					threeWord = True
					changeToModal(token,sent,3) #make changes
				elif modTestBeStr in semModalAboutTo:
					threeWord = True
					changeToModal(token,sent,4) #make changes
				elif " ".join(modTestBeStr.split(" ")[1:]) in semModalUsedTo and modTestBeStr.split(" ")[0] not in ["be"]:
					threeWord = True
					changeToModal(token,sent,3) #make changes
			if token.idx >= 3 and threeWord == False:
				modTestL = sent[token.idx-3:token.idx]
				modTestStr = " ".join([x.word.lower() for x in modTestL])
				if modTestStr in semiModalL: #make adjustments
					changeToModal(token,sent,3)
		if passive == False:
		#test longer sequences before shorter ones:
			if token.idx >= 3:
				modTestL = sent[token.idx-3:token.idx]
				modTestStr = " ".join([x.word.lower() for x in modTestL])
				modTestBeStr = " ".join([modTestL[0].lemma.lower(),modTestL[1].word.lower(),modTestL[2].word.lower()])
				if modTestStr in semiModalThreeL: #make adjustments
					threeWord = True
					changeToModal(token,sent) #make changes
				elif modTestBeStr in semModalBeL:
					threeWord = True
					changeToModal(token,sent) #make changes
				elif modTestBeStr in semModalAboutTo:
					threeWord = True
					changeToModal(token,sent,3) #make changes
				elif " ".join(modTestBeStr.split(" ")[1:]) in semModalUsedTo and modTestBeStr.split(" ")[0] not in ["be"]:
					threeWord = True
					changeToModal(token,sent,2) #make changes

			if token.idx >= 2 and threeWord == False:
				modTestL = sent[token.idx-2:token.idx]
				modTestStr = " ".join([x.word.lower() for x in modTestL])
				if modTestStr in semiModalL: #make adjustments
					changeToModal(token,sent)
		#add code to fix missing "wh" or "that complementizer?"
			#TO DO: need to fix "gonna"

def coordinatedClauseAdjust(token,sent): #deal with coordinate clauses and wh-words in coordinated VPs
	#deal with coordinated clauses
	if token.lxgrtag in ["vbmain"] and token.deprel in ["conj"] and token.cat2 not in ["nonfinite"]:
		if sent[token.headidx].cxtag in ["thatcls+vcomp","whcls+vcomp"]: #may need to extend this...
			token.cxtag = sent[token.headidx].cxtag
			token.cat5 = sent[token.headidx].cat5
			token.cat8 = sent[token.headidx].cat8



#############################

#### These functions use the previous functions to conduct tagging and tallying of lexicogramamtical features ###

def preprocess(text): #takes raw text, processes with spacy, then outputs a list of sentences filled with tokenObjects
	sentCounter = 0
	output = []
	doc = nlp(text)
	for sent in doc.sents:
		sentObj = sentBlank() #blank sentence object
		sentObj.meta.append("#sentid = " + str(sentCounter))
		#sentl = []
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
			sentObj.tokens.append(tok)
			#sentl.append(tok)
		output.append(sentObj)
		sentCounter += 1
	return(output)

def tag(input): #tags :)
	sents = []
	if isinstance(input,str) == True:
		input = preprocess(input)
	for sent in input:
	#for sent in preprocess(sstring):
		for token in sent.tokens:
			#print(token.idx,token.word,token.lemma,token.deprel,token.headidx)
			personal_pronouns(token)
			advanced_pronoun(token,sent.tokens)
			adverbs(token,sent.tokens)
			adjectives(token)
			nouns(token)
			verbs(token,sent.tokens)
			prepositions(token,sent.tokens)
			coordinators(token,sent.tokens)
			subordinators(token,sent.tokens)
			determiners(token)
			that_wh(token,sent.tokens)
			complexity(token,sent.tokens)
			semiModalAdjust(token,sent.tokens)
			coordinatedClauseAdjust(token,sent.tokens)
		sents.append(sent)
	return(sents)

def printer(loToks, verbose = False): 
	for sentidx, sent in enumerate(loToks):
		for x in sent.meta:
			print(x)
		for token in sent.tokens:
			if verbose == True:
				print(token.idx, token.word, token.lemma, token.cxtag, token.lxgrtag, token.cat1,token.cat2,token.cat3, token.cat4, token.cat5, token.cat6, token.cat7, token.cat8, token.xpos, token.deprel,token.headidx)
			else:
				print(token.idx, token.word, token.lemma, token.cxtag)
			#print(token.idx, token.word, token.lemma, token.lxgrtag, token.cat1,token.cat2,token.cat3, token.cat4, token.cat5, token.cat6, token.cat7, token.cat8, token.xpos, token.upos, token.deprel,token.headidx)
		#print(sentidx,len(loToks))
		if sentidx +1 != len(loToks):
			print("\n")

def writer(outname,loToks,joiner = "\t"):
	outf = open(outname,"w")
	docout = []
	for sent in loToks:
		sentout = []
		for x in sent.meta:
			sentout.append(x) #add metadata
		for token in sent.tokens:
			#fix formatting issue
			if token.word in ["\n","\t"]:
				token.word = ""
			if token.lemma in ["\n","\t"]:
				token.lemma = ""
			tokenout = []
			items = [token.idx,token.word,token.lemma,token.cxtag, token.lxgrtag, token.cat1,token.cat2,token.cat3, token.cat4, token.cat5, token.cat6, token.cat7, token.cat8, token.xpos, token.deprel,token.headidx]
			#items = [token.idx,token.word,token.lemma,token.lxgrtag, token.cat1,token.cat2,token.cat3, token.cat4, token.cat5, token.cat6, token.cat7, token.cat8, token.xpos, token.upos, token.deprel,token.headidx]
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

#consider allowing for targetDir to be a list or a directory name
def tagFolder(targetDir,outputDir,suff = ".txt"): #need to add this to lxgrtgr
	if targetDir[-1] != "/":
		targetDir = targetDir + "/"
	if outputDir[-1] != "/":
		outputDir = outputDir + "/"
	print("Tagging all",suff, "files in",targetDir)
	fnames = glob.glob(targetDir + "*" + ".txt")
	for fname in fnames:
		simpleName = fname.split("/")[-1]
		print("Processing", simpleName)
		tagged_sents = tag(open(fname,encoding = "utf-8", errors = "ignore").read().strip())
		writer(outputDir + simpleName.replace(suff,"_tagged"+suff),tagged_sents)
	print("Your files have been tagged. It is time to check the output!")

def countTagsFile(fname,tagList = None): 
	if tagList == None:
		tagList = ["finitecls+advl","thatcls+vcomp","whcls+vcomp","finitecls+rel","thatcls+ncomp","thatcls+jcomp","xtrapos+thatcls+jcomp","whcls+incomp","tocls+advl","ingcls+advl","edcls+advl","tocls+vcomp","tocls+ncomp","ingcls+vcomp","edcls+rel","ingcls+rel","tocls+rel","tocls+jcomp","xtrapos+tocls+jcomp","ingcls+incomp","rb+advl","in+advl","attr+npremod","nn+npremod","of+npostmod","in+npostmod","appos+npostmod","in+jcomp","rb+jjrbmod"]
	outd = {"ntokens":0}
	ignored = []
	for tag in tagList:
		outd[tag] = 0
	sents = open(fname, encoding = "utf-8", errors = "ignore").read().strip().split("\n\n")
	for sent in sents:
		for token in sent.split("\n"):
			if token[0] == "#":
				continue
			elif len(token.split("\t")) < 15:
				continue
			else:
				for tag in token.split("\t")[3:13]:
					if tag in outd:
						outd[tag] += 1
					elif tag not in [""] and tag not in ignored:
						ignored.append(tag)
					else:
						continue
				if token.split("\t")[14] not in ["punct"]:
					outd["ntokens"] += 1
	#print(ignored)
	return(outd)

#consider making this either a list or a directory
def countTagsFolder(targetDir,tagList = None,suff = ".txt"): #need to add this to lxgrtgr
	folderD = {}
	if targetDir[-1] != "/":
		targetDir = targetDir + "/"
	fnames = glob.glob(targetDir + "*" + suff) #get all filenames
	for fname in fnames:
		simpleName = fname.split("/")[-1]
		print("Processing", simpleName)
		folderD[simpleName] = countTagsFile(fname,tagList)
	return(folderD)

def writeCounts(outputD,outName, tagList = None, sep = "\t", normed = True,norming = 10000): #defaults to normed counts (per 10,000 tokens)
	if tagList == None:
		tagList = ["finitecls+advl","thatcls+vcomp","whcls+vcomp","finitecls+rel","thatcls+ncomp","thatcls+jcomp","xtrapos+thatcls+jcomp","whcls+incomp","tocls+advl","ingcls+advl","edcls+advl","tocls+vcomp","tocls+ncomp","ingcls+vcomp","edcls+rel","ingcls+rel","tocls+rel","tocls+jcomp","xtrapos+tocls+jcomp","ingcls+incomp","rb+advl","in+advl","attr+npremod","nn+npremod","of+npostmod","in+npostmod","appos+npostmod","in+jcomp","rb+jjrbmod"]
	header = ["filename","ntokens"] + tagList
	outL = [sep.join(header)]
	for fname in outputD:
		row = [fname,str(outputD[fname]["ntokens"])]
		for tag in tagList:
			if tag not in outputD[fname]:
				row.append("n/a")
			else:
				if normed == True:
					row.append(str(outputD[fname][tag]/outputD[fname]["ntokens"]*norming)) #str value
				else:
					row.append(str(outputD[fname][tag]))
		outL.append(sep.join(row))
	outf = open(outName,"w")
	outf.write("\n".join(outL))
	outf.flush()
	outf.close()
	print("Finished writing output to",outName)

def readConll(fname):
	outl = [] #list of sentObjs
	sents = open(fname,errors = "ignore").read().strip().split("\n\n")
	for sent in sents:
		sentObj = sentBlank() #create sentence object instance

		for token in sent.split("\n"):
			if token[0] == "#":
				sentObj.meta.append(token)
				continue
			else:
				tokObj = tokenBlank() #create token object instance
				info = token.split("\t") #presumes tab-delimited file
				tokObj.idx = int(info[0])-1
				tokObj.word = info[1]
				tokObj.lemma = info[2].lower()
				tokObj.xpos = info[3]
				#no upos :(
				tokObj.deprel = info[6]
				if tokObj.deprel == "root":
					tokObj.headidx = tokObj.idx
				else:
					tokObj.headidx = int(info[5])-1
				
				sentObj.tokens.append(tokObj)
		outl.append(sentObj)
	return(outl)

#test conll
#conllLoS = tag(readConll("sample_conll/bc-cctv-00-cctv_0000.parse.dep"))
#printer(conllLoS[:3])

### Tests on 2024-10-28
#printer(tag("But you can see how you can simulate and see what the expected payment is."),verbose = True)
# printer(tag("Can you see how incredibly well they have done?"),verbose = True)
# printer(tag("Can you see how they have done?"),verbose = True)


### Tests on 2024-10-16
# printer(tag("He tried as if he would never try again."),verbose = True)

# printer(tag("They were fierce spinsters who said 'no' on principle before they knew what they were going to be asked."),verbose = True)
# printer(tag("He knew what they were up to."),verbose = True)
# printer(tag("'maman, do you think the Little Lord Jesus heard me?'"),verbose = True)
# printer(tag("It was clear that the amendment was going to be defeated."),verbose = True)
# printer(tag("I'm going to help her, it will be so much fun."),verbose = True)
# print(list(range(3,6)))

### Tests on 2024-10-15
# printer(tag("In the process of discovering simple, complex, and end-stopped cells in the cortex, Hubel observed something."),verbose = True)
# printer(tag("In my first life, I ate pizza."),verbose = True)
# printer(tag("Most of these are mine."),verbose = True)
# printer(tag("Many of these are mine."),verbose = True)
# printer(tag("Some of these are mine."),verbose = True)
# printer(tag("If this were solely a lifetime exchange, how much of that gain would be recognized?"),verbose = True)
# printer(tag("The numbers verify that almost three times as much is spent on youth."),verbose = True)

### Tests on 2024-10-09
# printer(tag("But it is a reminder just how blinkered abortionists can be, on the one hand, and of how determined pro-abortionists are to convince women to talk about their abortions."),verbose = True)
# printer(tag("It's crazy to try that."),verbose = True)
# printer(tag("It is evident that the Marxist perspective has been an enormous intellectual and political force."),verbose = True)
# printer(tag("I am sad that the Marxist perspective has been an enormous intellectual and political force."),verbose = True)

# ### Tests on 2024-10-08
# printer(tag("matter seeing those problems again, and that's just one, one set of problems."),verbose = True)

# ### Tests on 2024-10-03
# #v37
# printer(tag("If you want to work with something big, that's okay."),verbose = True)
# printer(tag("I'm going to help her, it will be so much fun."),verbose = True)
# printer(tag("keep in mind that we are going to talk about is very much in flux in what people believe."),verbose = True)

#v36
# printer(tag("So we need to make sure that we understand."),verbose = True)

# printer(tag("He was so hungry that he ate a cow."),verbose = True) #works
# printer(tag("He was so immensely hungry that he ate a cow."),verbose = True)#works

# printer(tag("He stayed in the lobby through almost all the voting, but returned at the last minute when it was clear the amendment was going to be defeated."),verbose = True)
# printer(tag("He stayed in the lobby through almost all the voting, but returned at the last minute when it was clear the amendment was going to die."),verbose = True)

### Tests on 2024-10-01
#printer(tag("They can generally accumulate enough that it never becomes an issue ."),verbose = True)

### Tests on 2024-09-25+26
#two-word semi-modals
#semiModalL = ["have to","had to","got to", "ought to"]
# already treated by spacy as modal: ["got ta","gon na"]
#moved "about to" to "BE about to"
# "gon na" causes issues - future development could iron out these bugs
# printer(tag("He said that they have to try."),verbose = True)
# printer(tag("He said that they had to try."),verbose = True)
# printer(tag("He said that they got to try."),verbose = True)
# printer(tag("He said that they ought to try."),verbose = True)
# printer(tag("He said that they are gonna try"),verbose = True)
# #three-word modals
# printer(tag("He said that they have got to try."),verbose = True)
# printer(tag("He said that they had got to try."),verbose = True)

# #be three-word modals
# #semModalBeL = ["be supposed to","be going to","be about to"]
# printer(tag("He said that he was supposed to try."),verbose = True)
# printer(tag("He said that he was going to try."),verbose = True)
# printer(tag("He said that he was about to try."),verbose = True)
# printer(tag("He said that that they used to try."),verbose = True)



### update 2024-02-08 v0.5.9
#jj+that+jcomp  - add rule to ensure that jj is before jcomp
# printer(tag("so, first of all X, X could be two, right?")) #no tag (this is correct)
# printer(tag("We’re happy that the hunger strike has ended.")) #tagged correctly

#printer(tag("She won't narc on me, because she prides herself on being a gangster"))

### Noun complement clauses versus finite relative clauses
# noun+finite+relcl
# printer(tag("We have many beginning students who have had no previous college science courses in our program.")) #noun+finite+relcl from LGSWE pp.604-606
# printer(tag("They had seen a footpath which disappeared in a landscape of fields and trees")) #noun+finite+relcl from LGSWE pp.604-606
# printer(tag("The goat, which had slid about during the transfer, regarded him with bright-eyed perspicacity.")) #noun+finite+relcl from LGSWE pp.604-606
# printer(tag("Peter reached out for the well-thumbed report that lay behind him on the cupboard top.")) #noun+finite+relcl From LGSWE pp.644-645
# # noun+that+ncomp
# printer(tag("Other semiconductor stocks eased following an industry trade group's report that its leading indicator fell in September.")) #nn+that+ncomp From LGSWE pp.644-645
# printer(tag("There were also rumors that Ford had now taken its stake up to the maximum 15 per cent allowed.")) #nn+that+ncomp From LGSWE pp.644-645
# printer(tag("These figures lead to an expectation that the main application area would be in the ofice environments.")) #nn+that+ncomp From LGSWE pp.644-645
# printer(tag("It was a pleasing thought, that I might soon be moving in more exalted circles.")) #incorrectly tagged by Spacy - head is main verb, not noun complement From LGSWE pp.644-646
# printer(tag("Clinton's second allegation, that there has been collusion between the security forces and Protestant para-military groups, is based on a very few isolated cases.")) #noun+that+ncomp From LGSWE pp.644-646
# printer(tag("The recognition that a text may set up its own secondary norms leads to a further conclusion, that features of language within that text may depart from the norms of the text itself")) #nn+that+ncomp From LGSWE pp.644-646

### Initial Samples/tests ###
# printer(tag("We will see those impacts fairly quickly.")) # rb+adjmod|advmod
# printer(tag("That cat was surprisingly fast.")) # rb+adjmod|advmod
# printer(tag("I’d be happy with just one.")) # in+jcomp
# printer(tag("James Klein, president of the American Benefits Council, was kind.")) # nn+nappos
# printer(tag("Overall scores were computed by averaging the scores for male and female students.")) #in+post+nmod
# printer(tag("McKenna wrote about the origins of human language")) #of+gen+post+nmod
# printer(tag("The aviation security committee has convened.")) #nn+npremod 
# printer(tag("He is away for fighter pilot training")) #nn+npremod 
# printer(tag("These are the conventional practices."))#attr+nn+premod 
# printer(tag("I suffered an emotional injury")) #attr+nn+premod 
# printer(tag("Alright, we'll talk to you in the morning.")) #in+advl
# printer(tag("I raved about it afterwards.")) #rb+advl
# printer(tag("The formula for calculating the effective resistance is complicated.")) #ingcls+incomp
# printer(tag("It was important to obtain customer feedback.")) #xtrapos+jj+tocls+jcomp
# printer(tag("I was happy to do it.")) #jj+tocls+jcomp
# printer(tag("The project is part of a massive plan to complete the section of road.")) #n+tocls+ncomp
# printer(tag("You’re the best person to ask.")) #nn+tocls+relcl 
# printer(tag("Elevated levels are treated with a diet consisting of low cholesterol foods.")) #nn+ingcls+relcl
# printer(tag("This is a phrase that is used in the recruitment industry.")) #nn+finite+relcl #comparison check
# printer(tag("This is a phrase used in the recruitment industry.")) #nn+edcls+relcl
# printer(tag("I like watching the traffic go by.")) #vb+ingcls
# printer(tag("I really want to fix this room up.")) #vb+tocls
# printer(tag("Based on estimates of the number of unidentified species, other studies put the sum total in the millions.")) #advlcls+edcls
# printer(tag("Considering mammals' level of physical development, the diversity of this species is astounding.")) #advlcls+ingcls
# printer(tag("Sections of fixed cells were examined to verify this hypothesis.")) # advlcls+tocls+purpose
# printer(tag("To verify this hypothesis, sections of fixed cells were examined.")) # advlcls+tocls+purpose
# printer(tag("I’ll offer a suggestion for what we should do.")) #in+wh+incomp
# printer(tag("It is evident that the virus formation is related to the cytoplasmic inclusions.")) #xtrapos+jj+that+compcls #spacy mistags this as a verb complement [fixed 2024-02-14]
# printer(tag("We’re happy that the hunger strike has ended.")) #jj+that+jcomp
# printer(tag("The fact that no tracer particles were found indicates that these areas are not a pathway.")) #nn+that+ncomp
# printer(tag("We need to account for the experimental error that could result from using cloze tests.")) #nn+finite+relcl
# printer(tag("I don’t know how they do it.")) #verb+wh+vcomp
# printer(tag("yeah, I think I probably could")) #vb+that+vcomp 
# printer(tag("I would hope that we can have more control over them.")) #vb+that+compcls
# printer(tag("Well, if I stay here, I'll have to leave early in the morning.")) #cnd-cos-cn
# printer(tag("She won't narc on me, because she prides herself on being a gangster.")) #cnd-cos-cn



# printer(tag("They believe that the minimum wage could threaten their jobs."))
# printer(tag("They believe that is wrong.")) #my own example. "That" is correct in v .05
# printer(tag("The more important point, he said, was that his party had voted with the Government more often in the last decade than in the previous one."))
# printer(tag("Understanding how a planet generates and gets rid of heat is essential if we are to understand how the planet works.")) #how isn't right - parsing error for head of "how"
# printer(tag("I don't know how they did that."))