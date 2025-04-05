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
version = "0.0.5.65.1"
version_notes = "0.0.5.65.1 - Minor bug fix"

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
from spacy.tokens import Doc
from spacy.language import Language
#nlp = spacy.load("en_core_web_sm") #load model
print("Loading Transformer Model")
nlp = spacy.load("en_core_web_trf")  #load model
print("Transformer Model Successfully Loaded")
nlp.max_length = 1728483 #allow more characters to be processed than default. This allows longer documents to be processed. This may need to be made longer.

#the following is only used when attempting to align outputs

class WhitespaceTokenizer(object):
	def __init__(self, vocab):
		self.vocab = vocab

	def __call__(self, text):
		words = text.split(' ')
		# All tokens 'own' a subsequent space character in this tokenizer
		spaces = [True] * len(words)
		return Doc(self.vocab, words=words, spaces=spaces)

#nlp.tokenizer = WhitespaceTokenizer(nlp.vocab) #force pre-existing tokenization

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
		self.head = spacyToken.head.text #.text #text of head
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

### Classes and functions for using Gold Conllu Data
class spacyIshHead():
	def __init__(self):
		self.text = None
		self.i = None
		self.dep_ = None

class spacyIshToken():
	def __init__(self, tokenList): 
		self.i = int(tokenList[0]) #will have to add this from position in sentence
		self.text = tokenList[1] #raw text
		self.lemma_ = tokenList[2].lower() #lowered lemma form
		self.pos_ = None #need to add this
		self.tag_ = tokenList[3] #penn tag
		self.dep_ = tokenList[6] #dependency relation (based on CLEAR tagset)
		self.head = spacyIshHead() #.text #text of head
		self.head.i = int(tokenList[5])
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

class spacyDocIsh():
	def __init__(self):
		self.sents = []

def processConllu(inputString):
	outList = spacyDocIsh()
	for sent in inputString.split("\n\n"):
		#print(sent)
		ignoreSent = False
		sentList = []
		#sentObj = spacyDocIsh()
		tokens = sent.split("\n")
		if len(tokens) < 2: #skip sentences that have only one token
			continue
		for token in tokens:
			#print(token)
			tokInfo = token.split("\t")
			sentList.append(spacyIshToken(tokInfo))
	#iterate back through and add additional info
		#print([[x.text,x.head.i] for x in sentList])
		for token in sentList:
			if token.tag_ in ["XX"]:
				ignoreSent = True
			#print(token.head.i)
			token.head.text = sentList[token.head.i-1].text
			token.head.dep_ = sentList[token.head.i-1].dep_
		if ignoreSent == False:
			outList.sents.append(sentList)
	return(outList)
#####

### Linguistic Analysis Functions ###
def makeNone(sent,tokenidx): #make None
	sent[tokenidx].lxgrtag = None
	sent[tokenidx].cxtag = None
	sent[tokenidx].cat1 = None
	sent[tokenidx].cat3 = None
	sent[tokenidx].cat4 = None
	sent[tokenidx].cat5 = None
	sent[tokenidx].cat6 = None
	sent[tokenidx].cat7 = None
	sent[tokenidx].cat8 = None


def nGramForward(token,sent,n,lowered = True):
	if len(sent[token.idx+1:]) < n:
		return([x.word.lower() for x in sent[token.idx:]])
	elif lowered == True:
		return(" ".join([x.word.lower() for x in sent[token.idx:token.idx+n]]))
	else:
		return(" ".join([x.word.lower() for x in sent[token.idx:token.idx+n]]))

def nGramMiddle(token,sent,behind,ahead,lowered = True): #finish this
	
	if len(sent[:token.idx]) < behind or len(sent[token.idx+1:]) < ahead:
		return(token.word.lower())
	elif lowered == True:
		return(" ".join([x.word.lower() for x in sent[token.idx-behind:token.idx+1+ahead]]))
	else:
		return(" ".join([x.word.lower() for x in sent[token.idx-behind:token.idx+1+ahead]]))

def nGramMiddleBe(token,sent,behind,ahead,lowered = True): #finish this
	
	if len(sent[:token.idx]) < behind or len(sent[token.idx+1:]) < ahead:
		return(token.word.lower())
	elif lowered == True:
		tokL = sent[token.idx-behind:token.idx+1+ahead]
		return(" ".join([tokL[0].lemma.lower()]+[x.word.lower() for x in tokL[1:]]))
	else:
		return(" ".join([tokL[0].lemma]+[x.word for x in tokL[1:]]))

def multiWordPrepositions(token,sent):
	#two-word seqs
	mltWrdPrepPrep = ['as for', 'but for', 'except for', 'save for', 'as from', 'as of', 'out of', 'depending on', 'according to', 'as to', 'on to', 'up to', 'along with', 'on to', 'up to']
	mltWrdAdvmodPrep = ['apart from', 'aside from', 'away from', 'ahead of', 'inside of', 'instead of', 'irrespective of', 'outside of', 'regardless of', 'close to', 'contrary to', 'next to', 'opposite to', 'owing to','preliminary to', 'preparatory to','previous to', 'prior to', 'relative to', 'subsequent to', 'together with', 'back to'] #advmod
	mltWrdAcompPrep = ['devoid of', 'exclusive of', 'void of'] #maybe JJ + Prep?
	mltWrdPcompPrep = ['because of', 'due to']
	mltWrdAdvclsPrep = ['exclusive of', 'owing to'] #these are in both lists
	mltWrdNpadvmodPrep = ['thanks to']
	mltWrdAmodPrep = ['such as']
	mltWrdAdvmodQuantmod = ['upwards of'] # advmod+quantmod
	#add "of course"?

	#Three-word seqs
	#mltWrdPrpThree = ['as far as', 'as well as', 'in exchange for', 'in return for', 'as distinct from', 'by means of', 'by virtue of', 'by way of', 'for lack of', 'for want of', 'in aid of', 'in back of', 'in case of', 'in charge of', 'in consequence of', 'in favour of', 'in front of', 'in lieu of', 'in light of', 'in need of', 'in place of', 'in respect of', 'in search of', 'in spite of',  'in terms of', 'in view of', 'on account of', 'on behalf of', 'on grounds of', 'on top of', 'as opposed to', 'by reference to', 'in addition to', 'in contrast to', 'in reference to', 'in regard to', 'in relation to', 'with regard to', 'with reference to', 'with respect to',  'at variance with', 'in accordance with', 'in comparison with', 'in compliance with',  'in conformity with', 'in contact with', 'in line with', 'as a result of', 'at the expense of', 'for the sake of', 'in the case of', 'in the event of', 'in the light of', 'on the grounds of',  'on the ground of', 'on the part of', 'with the exception of', 'at the back of', 'in the middle of',  'as well as', 'by means of', 'in addition to', 'in front of', 'in spite of','with regard to']
	mltWrdPrpThreeAdvmodAdvmodMark = ['as far as'] #can be used as mw prep or mw subordinator
	#mltWrdPrpThreeAdvmodAdvmodcc = ['as well as'] #skipping this one for now. Functions as a coordinator?
	mltWrdPrpThreeMarkAdvclPrep = ['as opposed to'] #
	#mltWrdPrpThreePrepAmodPrep = ['as distinct from'] #same pattern as below
	mltWrdPrpThreePrepPobjPrep = ['as distinct from','in exchange for', 'in return for', 'by means of', 'by virtue of', 'by way of', 'for lack of', 'for want of', 'in aid of', 'in back of', 'in case of', 'in charge of', 'in consequence of', 'in favour of', 'in front of', 'in lieu of', 'in light of', 'in need of', 'in place of', 'in respect of', 'in search of', 'in spite of', 'in terms of', 'in view of', 'on account of', 'on behalf of', 'on grounds of', 'on top of', 'by reference to', 'in addition to', 'in contrast to', 'in reference to', 'in regard to', 'in relation to', 'with regard to', 'with reference to', 'with respect to', 'at variance with', 'in accordance with', 'in comparison with', 'in compliance with', 'in conformity with', 'in contact with', 'in line with']
	mltWrdPrpFourPrepDetPobjPrep = ['as a result of', 'at the expense of', 'for the sake of', 'in the case of', 'in the event of', 'in the light of', 'on the grounds of', 'on the ground of', 'on the part of', 'with the exception of', 'at the back of', 'in the middle of']

	if token.deprel == "prep":
		if nGramForward(token,sent,2) in mltWrdPrepPrep: #deal with two-word multiword prepositions first
			if sent[token.idx+1].deprel in ["prep"]:
				sent[token.idx+1].headidx = token.headidx #change dependency structure
			token.lxgrtag = "inphrsl"
			token.deprel = "goeswith"
			token.headidx = token.idx+1

	
	if token.deprel == "advmod":
		if nGramForward(token,sent,2) in mltWrdAdvmodPrep: #deal with two-word multiword prepositions first
			if sent[token.idx+1].deprel in ["prep"] and token.headidx != sent[token.idx+1].idx:
				sent[token.idx+1].headidx = token.headidx #change dependency structure if advmod is not the dep of the prep
			if sent[token.idx+1].deprel in ["cc"]:
				sent[token.idx+1].cxtag = "in+advl" #change dependency structure if advmod is not the dep of the prep			
			token.lxgrtag = "inphrsl"
			token.cat1 = None
			token.deprel = "goeswith"
			token.headidx = token.idx+1

		if nGramForward(token,sent,2) in mltWrdAdvmodQuantmod: #deal with two-word multiword prepositions first
			if sent[token.idx+1].deprel in ["quantmod"]:
				sent[token.idx+1].headidx = sent[sent[token.idx+1].headidx].idx #change dependency structure
			token.lxgrtag = "inphrsl"
			token.cat1 = None
			token.deprel = "goeswith"
			token.headidx = token.idx+1
			sent[token.idx+1].deprel = "prep"
			sent[token.idx+1].cxtag = "in+advl"


	if token.deprel in ["acomp","oprd"]:
		if nGramForward(token,sent,2) in mltWrdAcompPrep: #deal with two-word multiword prepositions first
			if sent[token.idx+1].deprel in ["prep"] and token.headidx != sent[token.idx+1].idx:
				sent[token.idx+1].headidx = token.headidx #change dependency structure if advmod is not the dep of the prep
			token.lxgrtag = "inphrsl"
			token.cat1 = None
			token.deprel = "goeswith"
			token.headidx = token.idx+1


	if token.deprel == "pcomp":
		if nGramForward(token,sent,2) in mltWrdPcompPrep: #deal with two-word multiword prepositions first
			if sent[token.idx+1].deprel in ["prep"] and token.headidx != sent[token.idx+1].idx:
				sent[token.idx+1].headidx = token.headidx #change dependency structure if advmod is not the dep of the prep
			token.lxgrtag = "inphrsl"
			token.cat1 = None
			token.deprel = "goeswith"
			token.headidx = token.idx+1


	if token.deprel == "advlcls":
		if nGramForward(token,sent,2) in mltWrdAdvclsPrep: #deal with two-word multiword prepositions first
			if sent[token.idx+1].deprel in ["prep"] and token.headidx != sent[token.idx+1].idx:
				sent[token.idx+1].headidx = token.headidx #change dependency structure if advmod is not the dep of the prep
			token.lxgrtag = "inphrsl"
			token.cat1 = None
			token.deprel = "goeswith"
			token.headidx = token.idx+1


	if token.deprel == "amod":
		if nGramForward(token,sent,2) in mltWrdAmodPrep: #deal with two-word multiword prepositions first
			if sent[token.idx+1].deprel in ["prep"] and token.headidx != sent[token.idx+1].idx:
				sent[token.idx+1].headidx = token.headidx #change dependency structure if advmod is not the dep of the prep
			token.lxgrtag = "inphrsl"
			token.cat1 = None
			token.deprel = "goeswith"
			token.headidx = token.idx+1


	if token.deprel == "npadvmod":
		if nGramForward(token,sent,2) in mltWrdNpadvmodPrep: #deal with two-word multiword prepositions first
			if sent[token.idx+1].deprel in ["prep"] and token.headidx != sent[token.idx+1].idx:
				sent[token.idx+1].headidx = token.headidx #change dependency structure if advmod is not the dep of the prep
			token.lxgrtag = "inphrsl"
			token.cat1 = None
			token.deprel = "goeswith"
			token.headidx = token.idx+1


	if token.deprel == "npadvmod":
		if nGramForward(token,sent,2) in mltWrdNpadvmodPrep: #deal with two-word multiword prepositions first
			if sent[token.idx+1].deprel in ["prep"] and token.headidx != sent[token.idx+1].idx:
				sent[token.idx+1].headidx = token.headidx #change dependency structure if advmod is not the dep of the prep
			token.lxgrtag = "inphrsl"
			token.cat1 = None
			token.deprel = "goeswith"
			token.headidx = token.idx+1

	
	if nGramMiddle(token,sent,2,0) in mltWrdPrpThreeAdvmodAdvmodMark: #"as far as - subordinator"
		if token.deprel == "mark":
			#adjust phrase, etc.
			sent[token.headidx].headidx = sent[token.idx-1].headidx #adjust head idx of clause to appropriate location
			#adjust first word
			sent[token.idx-2].lxgrtag = "csphrsl"
			# sent[token.idx-2].cat1 = None
			sent[token.idx-2].headidx = token.idx
			sent[token.idx-2].deprel = "goeswith"
			# sent[token.idx-2].cxtag = None
			#adjust second word
			sent[token.idx-1].lxgrtag = "csphrsl"
			sent[token.idx-1].cat1 = None
			sent[token.idx-1].headidx = token.idx
			sent[token.idx-1].deprel = "goeswith"
			sent[token.idx-1].cxtag = None
			#adjust third word
			# token.lxgrtag = "in"
			# token.cat1 = None
			# token.deprel = "prep"
		if token.deprel == "prep": #used as preposition
			token.headidx = sent[token.idx-1].headidx #assign head to appropriate location
			sent[token.idx-2].lxgrtag = "inphrsl"
			# sent[token.idx-2].cat1 = None
			sent[token.idx-2].headidx = token.idx
			sent[token.idx-2].deprel = "goeswith"
			# sent[token.idx-2].cxtag = None
			#adjust second word
			sent[token.idx-1].lxgrtag = "inphrsl"
			# sent[token.idx-1].cat1 = None
			sent[token.idx-1].headidx = token.idx
			sent[token.idx-1].deprel = "goeswith"
			# sent[token.idx-1].cxtag = None
			#adjust third word
			# token.lxgrtag = "in"
			# token.cat1 = None
			# token.deprel = "prep"
	if nGramMiddle(token,sent,2,0) in mltWrdPrpThreeMarkAdvclPrep:
		token.headidx = sent[token.idx-1].headidx #assign head to appropriate location
		makeNone(sent,token.idx-1)
		sent[token.idx-1].headidx = token.idx
		sent[token.idx-1].lxgrtag = "inphrsl"
		sent[token.idx-1].deprel = "goeswith"
		# makeNone(sent,token.idx-2)
		sent[token.idx-2].headidx = token.idx
		sent[token.idx-2].lxgrtag = "inphrsl"
		sent[token.idx-2].deprel = "goeswith"

	if nGramMiddle(token,sent,2,0) in mltWrdPrpThreePrepPobjPrep:
		token.headidx = sent[token.idx-2].headidx #assign head to appropriate location
		# makeNone(sent,token.idx-1)
		sent[token.idx-1].headidx = token.idx
		sent[token.idx-1].lxgrtag = "inphrsl"
		sent[token.idx-1].deprel = "goeswith"
		# makeNone(sent,token.idx-2)
		sent[token.idx-2].headidx = token.idx
		sent[token.idx-2].lxgrtag = "inphrsl"
		sent[token.idx-2].deprel = "goeswith"

	if nGramMiddle(token,sent,3,0) in mltWrdPrpFourPrepDetPobjPrep:
		token.headidx = sent[token.idx-3].headidx #assign head to appropriate location
		# makeNone(sent,token.idx-1)
		sent[token.idx-1].headidx = token.idx
		sent[token.idx-1].lxgrtag = "inphrsl"
		sent[token.idx-1].deprel = "goeswith"
		# makeNone(sent,token.idx-2)
		sent[token.idx-2].headidx = token.idx
		sent[token.idx-2].lxgrtag = "inphrsl"
		sent[token.idx-2].deprel = "goeswith"
		
		sent[token.idx-3].headidx = token.idx
		sent[token.idx-3].lxgrtag = "inphrsl"
		sent[token.idx-3].deprel = "goeswith"

def multiWordSubordinators(token,sent):
	if token.deprel in ["mark"] and nGramMiddle(sent[token.idx],sent,1,0) in ["as if","as though","so that","in that"]:
		sent[token.idx-1].deprel = "goeswith"
		sent[token.idx-1].cat1  = "csphrsl"

	elif token.deprel in ["advcl"] and nGramMiddle(sent[token.headidx],sent,1,1) in ["as soon as"]: #not working right yet.
		#token.cat5 = "advlcls"
		middleWordLoc = token.headidx
		#token.deprel = "advcl"
		sent[middleWordLoc+1].headidx = token.idx
		sent[middleWordLoc+1].deprel = "mark"
		sent[middleWordLoc].lxgrtag  = "cs"
		sent[middleWordLoc].deprel = "goeswith"
		sent[middleWordLoc].headidx = middleWordLoc+1
		sent[middleWordLoc].cat1  = "csphrsl"
		sent[middleWordLoc-1].cat1  = "csphrsl"
		sent[middleWordLoc-1].deprel = "goeswith"
		sent[middleWordLoc-1].headidx = middleWordLoc+1
		token.headidx = sent[middleWordLoc].headidx


	elif token.xpos[:2] in ["VB","MD"] and token.deprel not in ["amod","acomp","aux","auxpass","prep"]: #added "MD" to account for sentences such as "I think I probably could"; added "prep" to avoid multi-word prepositions
		if token.deprel in ["acl"]:
			if sent[token.headidx].deprel in ["pobj"]:
				# print(nGramMiddle(sent[token.headidx],sent,1,0))
				# print(nGramMiddle(sent[token.headidx],sent,1,1))
				if nGramMiddle(sent[token.headidx],sent,1,0) in ["in case"]: #multiword adverbial
					#token.cat5 = "advlcls"
					lastWordLoc = token.headidx
					token.deprel = "advcl"
					token.headidx = sent[lastWordLoc-1].headidx #change head to appropriate location
					sent[lastWordLoc].lxgrtag  = "cs"
					sent[lastWordLoc].cat1  = "csphrsl"
					sent[lastWordLoc].deprel = "mark"
					sent[lastWordLoc].headidx = token.idx
					sent[lastWordLoc-1].deprel = "goeswith"
					sent[lastWordLoc-1].headidx = lastWordLoc
					sent[lastWordLoc-1].cat1  = "csphrsl"

				elif nGramMiddle(sent[token.headidx],sent,1,1) in ["on condition that","in order that"]:
					#token.cat5 = "advlcls"
					middleWordLoc = token.headidx
					token.deprel = "advcl"
					token.headidx = sent[middleWordLoc-1].headidx
					sent[middleWordLoc+1].headidx = token.idx
					sent[middleWordLoc+1].deprel = "mark"
					sent[middleWordLoc].lxgrtag  = "cs"
					sent[middleWordLoc].deprel = "goeswith"
					sent[middleWordLoc].headidx = middleWordLoc+1
					sent[middleWordLoc].cat1  = "csphrsl"
					sent[middleWordLoc-1].cat1  = "csphrsl"
					sent[middleWordLoc-1].deprel = "goeswith"
					sent[middleWordLoc-1].headidx = middleWordLoc+1
				
				elif nGramMiddle(sent[token.headidx],sent,1,1) in ["in order to"]: #multiword "to phrs"
					middleWordLoc = token.headidx
					token.deprel = "advcl"
					token.headidx = sent[middleWordLoc-1].headidx
					sent[middleWordLoc-1].cat1  = "tophrs"
					sent[middleWordLoc-1].headidx = middleWordLoc+1
					sent[middleWordLoc-1].deprel = "goeswith"
					sent[middleWordLoc].cat1  = "tophrs"
					sent[middleWordLoc].headidx = middleWordLoc+1
					sent[middleWordLoc].deprel = "goeswith"

				### Kris Start Here!!! ###
				elif nGramMiddle(sent[token.headidx],sent,2,1) in ["on the condition that","in the event that"]:
					thirdWordLoc = token.headidx
					token.deprel = "advcl"
					token.headidx = sent[thirdWordLoc-2].headidx
					sent[thirdWordLoc+1].headidx = token.idx
					sent[thirdWordLoc+1].deprel = "mark"
					sent[thirdWordLoc].lxgrtag  = "cs"
					sent[thirdWordLoc].deprel = "goeswith"
					sent[thirdWordLoc].headidx = thirdWordLoc+1
					sent[thirdWordLoc].cat1  = "csphrsl"
					sent[thirdWordLoc-1].cat1  = "csphrsl"
					sent[thirdWordLoc-1].deprel = "goeswith"
					sent[thirdWordLoc-1].headidx = thirdWordLoc+1
					sent[thirdWordLoc-2].cat1  = "csphrsl"
					sent[thirdWordLoc-2].deprel = "goeswith"
					sent[thirdWordLoc-2].headidx = thirdWordLoc+1

				#elif nGramMiddle(sent[token.headidx],sent,1,1) in ["as soon as"]:


def reassignHeads(headidxOld,headidxNew,sent):
	for token in sent:
		if token.headidx == headidxOld and token.deprel not in ["goeswith"]:
			token.headidx = headidxNew

def semiModalAdjust(token,sent): #adjust tags based on semi-modals
	if token.deprel in ["xcomp","advcl"]:
		if nGramMiddle(sent[token.headidx],sent,1,1) in ["have got to", "had got to"] or nGramMiddleBe(sent[token.headidx],sent,1,1) in ["be supposed to","be going to"]:
			oldHead = token.headidx
			newHead = token.idx
			token.headidx = sent[oldHead].headidx #reassign head to previous modal head
			token.deprel = sent[oldHead].deprel #reassign head to previous modal head
			sent[oldHead].deprel = "goeswith"
			sent[oldHead].xpos = "MD"
			sent[oldHead].headidx = oldHead+1
			sent[oldHead+1].deprel = "aux"
			sent[oldHead+1].xpos = "MD"
			sent[oldHead-1].deprel = "goeswith"
			sent[oldHead-1].xpos = "MD"
			sent[oldHead-1].headidx = oldHead+1
			reassignHeads(oldHead,newHead,sent) #reassign other heads from modal to main verb

		elif nGramMiddleBe(sent[token.headidx],sent,1,1) in ["be about to"]:
			oldHeadBe = token.headidx-1
			oldHeadAbout = token.headidx
			newHead = token.idx
			token.headidx = sent[oldHeadBe].headidx #reassign head to previous modal head
			token.deprel = sent[oldHeadBe].deprel #reassign head to previous modal head
			sent[oldHeadAbout].deprel = "goeswith"
			sent[oldHeadAbout].xpos = "MD"
			sent[oldHeadAbout].headidx = oldHeadAbout+1
			sent[oldHeadAbout+1].deprel = "aux"
			sent[oldHeadAbout+1].xpos = "MD"
			sent[oldHeadAbout-1].deprel = "goeswith"
			sent[oldHeadAbout-1].xpos = "MD"
			sent[oldHeadAbout-1].headidx = oldHeadAbout+1
			reassignHeads(oldHeadBe,newHead,sent) #reassign other heads from modal to main verb

		elif nGramMiddle(sent[token.headidx],sent,0,1) in ["have to","had to","got to", "ought to","got ta","gon na","used to"] and nGramMiddleBe(sent[token.headidx],sent,1,1) not in ["be used to"]: #and sent[token.headidx].deprel not in "goeswith"
			oldHead = token.headidx
			newHead = token.idx
			token.headidx = sent[oldHead].headidx #reassign head to previous modal head
			token.deprel = sent[oldHead].deprel #reassign head to previous modal head
			sent[oldHead].deprel = "goeswith"
			sent[oldHead].xpos = "MD"
			sent[oldHead].headidx = oldHead+1
			sent[oldHead+1].deprel = "aux"
			sent[oldHead+1].xpos = "MD"
			reassignHeads(oldHead,newHead,sent) #reassign other heads from modal to main verb

def multiWordAdverbs(token,sent):#much more work/validation needed here
	mwrbrb = ["sort of","kind of"]
	if token.xpos == "RB" and nGramMiddle(sent[token.idx],sent,0,1) in mwrbrb:
		sent[token.idx].xpos = "GW"
		sent[token.idx].lxgrtag = "rbphrsl"
		sent[token.idx].deprel = "goeswith"

def multiWordLinkingAdverbs(token,sent):
	#Lists from Longman Grammar (pp. 558-559, pp. 875-879)
	multiWordLinkingAdverbsPrepTwo = ["for another", "in addition", "in sum", "by comparison", "in conclusion", "for example", "for instance", "in contrast"]
	multiWordLinkingAdverbsPrepThree = ["for one thing", "for another thing","in other words","on the contrary", "in any case", "at any rate", "by the way"]
	multiWordLinkingAdverbsPrepThreeLast = ["in spite of"]
	multiWordLinkingAdverbsPrepFour = ["in the first place", "in the second place", "by the same token", "on the other hand"]
	multiWordLinkingAdverbsAdvmodTwo = ["after all"]
	multiWordLinkingAdverbsAdvmodThree = ["first of all"]
	multiWordLinkingAdverbsNpadvmod = ["all in all"]
	multiWordLinkingAdverbsAdvclTwo = ["to summarize","to conclude"]
	multiWordLinkingAdverbsAdvclThree = ["to begin with"]
	multiWordLinkingAdverbXcomp = ["which is to say"]

	if token.deprel in ["xcomp"] and nGramMiddle(sent[token.idx],sent,3,0) in multiWordLinkingAdverbXcomp:
			sent[token.idx - 3].xpos = "RB"
			sent[token.idx - 3].lxgrtag = "rb"
			sent[token.idx - 3].cat1 = "link"
			sent[token.idx- 3].deprel = "advmod"
			sent[token.idx- 3].headidx = sent[token.idx - 2].headidx #the dependency structure ends up being a bit weird on this one.

			sent[token.idx - 2].xpos = "GW"
			sent[token.idx - 2].lxgrtag = "lnkphrsl"
			sent[token.idx - 2].deprel = "goeswith"
			sent[token.idx - 2].headidx = token.idx-3

			sent[token.idx - 1].xpos = "GW"
			sent[token.idx - 1].lxgrtag = "lnkphrsl"
			sent[token.idx - 1].deprel = "goeswith"
			sent[token.idx - 1].headidx = token.idx-3

			sent[token.idx].xpos = "GW"
			sent[token.idx].lxgrtag = "lnkphrsl"
			sent[token.idx].deprel = "goeswith"
			sent[token.idx].headidx = token.idx-3


	if token.deprel in ["npadvmod"] and nGramMiddle(sent[token.idx],sent,1,1) in multiWordLinkingAdverbsNpadvmod:
			sent[token.idx -1].xpos = "RB"
			sent[token.idx -1].lxgrtag = "rb"
			sent[token.idx -1].cat1 = "link"
			sent[token.idx-1].deprel = "advmod"
			sent[token.idx-1].headidx = token.headidx

			sent[token.idx].xpos = "GW"
			sent[token.idx].lxgrtag = "lnkphrsl"
			sent[token.idx].deprel = "goeswith"
			sent[token.idx].headidx = token.idx-1

			sent[token.idx + 1].xpos = "GW"
			sent[token.idx + 1].lxgrtag = "lnkphrsl"
			sent[token.idx + 1].deprel = "goeswith"
			sent[token.idx + 1].headidx = token.idx-1


	if token.deprel in ["advmod"]:
		if nGramMiddle(sent[token.idx],sent,0,2) in multiWordLinkingAdverbsAdvmodThree:
			sent[token.idx].xpos = "RB"
			sent[token.idx].lxgrtag = "rb"
			sent[token.idx].cat1 = "link"
			sent[token.idx].deprel = "advmod"

			sent[token.idx + 1].xpos = "GW"
			sent[token.idx + 1].lxgrtag = "lnkphrsl"
			sent[token.idx + 1].deprel = "goeswith"
			sent[token.idx + 1].headidx = token.idx

			sent[token.idx + 2].xpos = "GW"
			sent[token.idx + 2].lxgrtag = "lnkphrsl"
			sent[token.idx + 2].deprel = "goeswith"
			sent[token.idx + 2].headidx = token.idx

		elif nGramMiddle(sent[token.idx],sent,0,1) in multiWordLinkingAdverbsAdvmodTwo:
			sent[token.idx].xpos = "RB"
			sent[token.idx].lxgrtag = "rb"
			sent[token.idx].cat1 = "link"
			sent[token.idx].deprel = "advmod"
			sent[token.idx].headidx = sent[token.idx + 1].headidx

			sent[token.idx + 1].xpos = "GW"
			sent[token.idx + 1].lxgrtag = "lnkphrsl"
			sent[token.idx + 1].deprel = "goeswith"
			sent[token.idx + 1].headidx = token.idx

	if token.deprel in ["advcl"]:
		if nGramMiddle(sent[token.idx],sent,1,1) in multiWordLinkingAdverbsAdvclThree:
			sent[token.idx -1].xpos = "RB"
			sent[token.idx -1].lxgrtag = "rb"
			sent[token.idx -1].cat1 = "link"
			sent[token.idx-1].deprel = "advmod"
			sent[token.idx-1].headidx = token.headidx

			sent[token.idx].xpos = "GW"
			sent[token.idx].lxgrtag = "lnkphrsl"
			sent[token.idx].deprel = "goeswith"
			sent[token.idx].headidx = token.idx-1

			sent[token.idx + 1].xpos = "GW"
			sent[token.idx + 1].lxgrtag = "lnkphrsl"
			sent[token.idx + 1].deprel = "goeswith"
			sent[token.idx + 1].headidx = token.idx-1
		
		elif nGramMiddle(sent[token.idx],sent,1,0) in multiWordLinkingAdverbsAdvclTwo:
			sent[token.idx -1].xpos = "RB"
			sent[token.idx -1].lxgrtag = "rb"
			sent[token.idx -1].cat1 = "link"
			sent[token.idx-1].deprel = "advmod"
			sent[token.idx-1].headidx = token.headidx

			sent[token.idx].xpos = "GW"
			sent[token.idx].lxgrtag = "lnkphrsl"
			sent[token.idx].deprel = "goeswith"
			sent[token.idx].headidx = token.idx-1

	if token.xpos in ["IN"] and sent[token.headidx].xpos[:2] in ["VB"]:
		if nGramMiddle(sent[token.idx],sent,0,3) in multiWordLinkingAdverbsPrepFour:
			sent[token.idx].xpos = "RB"
			sent[token.idx].lxgrtag = "rb"
			sent[token.idx].cat1 = "link"
			sent[token.idx].deprel = "advmod"

			sent[token.idx + 1].xpos = "GW"
			sent[token.idx + 1].lxgrtag = "lnkphrsl"
			sent[token.idx + 1].deprel = "goeswith"
			sent[token.idx + 1].headidx = token.idx

			sent[token.idx + 2].xpos = "GW"
			sent[token.idx + 2].lxgrtag = "lnkphrsl"
			sent[token.idx + 2].deprel = "goeswith"
			sent[token.idx + 2].headidx = token.idx

			sent[token.idx + 3].xpos = "GW"
			sent[token.idx + 3].lxgrtag = "lnkphrsl"
			sent[token.idx + 3].deprel = "goeswith"
			sent[token.idx + 3].headidx = token.idx

		if nGramMiddle(sent[token.idx],sent,0,2) in multiWordLinkingAdverbsPrepThree:
			sent[token.idx].xpos = "RB"
			sent[token.idx].lxgrtag = "rb"
			sent[token.idx].cat1 = "link"
			sent[token.idx].deprel = "advmod"

			sent[token.idx + 1].xpos = "GW"
			sent[token.idx + 1].lxgrtag = "lnkphrsl"
			sent[token.idx + 1].deprel = "goeswith"
			sent[token.idx + 1].headidx = token.idx

			sent[token.idx + 2].xpos = "GW"
			sent[token.idx + 2].lxgrtag = "lnkphrsl"
			sent[token.idx + 2].deprel = "goeswith"
			sent[token.idx + 2].headidx = token.idx

		if nGramMiddle(sent[token.idx],sent,2,0) in multiWordLinkingAdverbsPrepThreeLast:
			sent[token.idx -2].xpos = "RB"
			sent[token.idx -2].lxgrtag = "rb"
			sent[token.idx -2].cat1 = "link"
			sent[token.idx-2].deprel = "advmod"
			sent[token.idx-2].headidx = token.headidx

			sent[token.idx - 1].xpos = "GW"
			sent[token.idx - 1].lxgrtag = "lnkphrsl"
			sent[token.idx - 1].deprel = "goeswith"
			sent[token.idx - 1].headidx = token.idx-2

			sent[token.idx].xpos = "GW"
			sent[token.idx].lxgrtag = "lnkphrsl"
			sent[token.idx].deprel = "goeswith"
			sent[token.idx].headidx = token.idx-2

		if nGramMiddle(sent[token.idx],sent,0,1) in multiWordLinkingAdverbsPrepTwo:
			sent[token.idx].xpos = "RB"
			sent[token.idx].lxgrtag = "rb"
			sent[token.idx].cat1 = "link"
			sent[token.idx].deprel = "advmod"

			sent[token.idx +1].xpos = "GW"
			sent[token.idx + 1].lxgrtag = "lnkphrsl"
			sent[token.idx + 1].deprel = "goeswith"
			sent[token.idx + 1].headidx = token.idx




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
	#linking = ["so","then","though","anyway","however","thus","therefore","e.g.","i.e.","first","finally","furthermore","hence","nevertheless","rather","yet"] 
	linking  = ["secondly", "thirdly", "lastly", "altogether", "overall", "namely", "ie", "therefore", "thus", "however", "alternatively", "incidentally", "next", "further", "likewise", "moreover", "i.e.", "e.g.", "consequently", "anyway", "conversely", "instead", "anyhow", "besides", "nevertheless"] #from Longman Grammar pp. 558-559, pp. 875-879; previous list also included "though","finally","furthermore","hence", "rather"
	linkingIfFirst = ["now", "similarly","yet","still","also","so","then","first","second"]
	if token.deprel == "advmod":
		token.lxgrtag = "rb"
		#print(token.word)
		if token.word[-2:].lower() == "ly":
			token.cat2 = "ly"
		if token.deprel == "advmod" and sent[token.headidx].xpos[:2] == "VB":
			if token.word.lower() in linkingIfFirst and token.idx in [0]: #check words that are linking adverbs if they occur at the beginning of a sentence.
				token.cat1 = "link"
			elif token.word.lower() in linking:# updated list and code on 2025-02-21 previously: and token.idx < token.headidx: #if the word can be a linking adverb and occurs before the main verb:
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
	if token.deprel in ["npadvmod"] and token.word.lower() in ["yesterday","tomorrow"]: #added on 2025-02-21;updated on 2025-03-07
		token.lxgrtag = "rb"
		token.deprel = "advmod"
		token.xpos = "RB"
		token.upos = "ADV"

	#deal with multiword wh-subordinators
	if token.word.lower() in ["well"] and len([x.word for x in sent if x.cat1 in ["comp_wh"] and x.headidx == token.idx]) > 0:
		token.lxgrtag = None
		token.cat1 = None

def verbInfo(token,sent): #this is to help solve a problem with conjugated verb phrases
	cat2 = None
	#this is an ordered list of POS tags for the main verb and auxs represented in the VP
	if token.xpos[:2] in ["VB","MD"] and token.deprel not in ["amod","acomp","aux","auxpass","prep"]:
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
	if token.xpos[:2] in ["VB","MD"] and token.deprel not in ["amod","acomp","aux","auxpass","prep"]: #added "MD" to account for sentences such as "I think I probably could"; added "prep" to avoid multi-word prepositions
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
		if token.deprel in ["ccomp","csubj","xcomp"]: 
			token.cat5 = "compcls"
		elif token.deprel in ["pcomp"]: #deal with some multi-word adverbs
			#print(nGramForward(sent[token.headidx],sent,2))
			if nGramForward(sent[token.headidx],sent,2) in ["provided that","except that","save that"]:
				token.cat5 = "advlcls"
				sent[token.headidx].lxgrtag  = "cs"
				sent[token.headidx].cat1  = "csphrsl"
				sent[token.headidx+1].lxgrtag  = "csphrsl" #convert to 
				sent[token.headidx+1].cat1  = "csphrsl"
				sent[token.headidx+1].cxtag = None
			else:
				token.cat5 = "compcls"
		elif token.deprel == "advcl":
			if sent[token.headidx].xpos[:2] in ["JJ"]:
				token.cat5 = "jmod_cls"
			else:
				token.cat5 = "advlcls"
		elif token.deprel in ["relcl"]:
			token.cat5 = "nmod_cls"
		elif token.deprel in ["acl"]: #updated 2024-10-01
			if sent[token.headidx].xpos[:2] in ["NN","PR"]:
			#if sent[token.headidx].upos in ["NOUN","PROPN","PRON"]:
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
			conjDepList = [x.idx for x in sent if x.headidx == token.idx and x.deprel in ["conj"] and verbInfo(x,sent) in ["nonfinite"]]

			if len([x.word.lower() for x in sent if x.headidx == token.idx and x.deprel in ["nsubj","nsubjpass","advmod","attr","dep"] and x.xpos in ["WDT","WP", "WP$", "WRB"] and x.word.lower() != "that"]) > 0: #note that "dep" might cause issues. added on 2024-10-03
				token.cat6 = "whcls"
			######
			# catch "wh" words that are attached to another verb in the verb phrase [updated on 20241028]
			elif len([x.word.lower() for x in sent if x.headidx == token.idx and x.deprel in ["mark"] and x.xpos in ["IN"] and x.word.lower() in ["whether"]]) > 0: #added on 2024-11-19
				token.cat6 = "whcls"

			elif len(conjDepList) > 0:
				if len([x.word.lower() for x in sent if x.headidx == conjDepList[-1] and x.deprel in ["nsubj","nsubjpass","advmod","attr","dep"] and x.xpos in ["WDT","WP", "WP$", "WRB"] and x.word.lower() != "that"]) > 0:
					token.cat6 = "whcls"
			######
		if token.cat2 == "nonfinite":
			### to clause ###
			if "to" in [x.word.lower() for x in sent if x.headidx == token.idx and x.idx < token.idx and x.xpos == "TO"]: # and sent[x.idx-1].lemma not in ["order"] #and sent[x.idx-1].lemma not in ["seem","have","need","want","order"] Doug didn't like these as semi-modals - kept in "order" to catch "in order to"
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
		
		if token.cat6 in ["ingcls"] and token.deprel in ["pobj"]: #added 2025-02-02
			token.cat7 = "incomp"

		if token.cat5 == "nmod_cls": #finish fixing this
			if token.deprel == "relcl":
				token.cat7 = "rel"
			elif token.deprel in ["acl"]:
				if sent[token.headidx].xpos[:2] in ["NN","PR"]: #this may be too restrictive; updated 20241220 [avoided upos]
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
			elif mark not in ["that","whether"]:
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
				token.cat8 = "compdel" #this needs to be more restrictive

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
	#also, the use of the word "here" as a demonstrative pronoun may need to be addressed. They are tagged as adverbs by spacy.
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
	if token.deprel == "prep" and token.lxgrtag not in ["inphrsl"]: #ignore first word in phrasal prepositions
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
	#TODO: Add categories for multiword subordinators here
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

	if token.word.lower() in ["when"] and token.deprel == "advmod" and sent[token.headidx].deprel == "advcl": #added 2025-02-04 - may need to edit
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
			if sent[sent[token.headidx].headidx].xpos[:2] in ["NN","PR"]: #this may be too restrictive; updated 20241001
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
	if token.cat7 in ["vcomp"] and token.cat2 not in ["nonfinite"]: 
		if token.idx > token.headidx or token.deprel in ["csubj"]: #if a finite clause comes after the verb OR is a clausal subject, updated on 2025-02-09
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
	
	if token.cat6 in ["tocls"] and token.deprel in ["xcomp","csubj"]: #may need more refining; csubj added 2025-02-09
		if sent[token.headidx].xpos[:2] in ["VB"]: #updated 2024-10-08
			token.cxtag = "tocls+vcomp"
		elif sent[token.headidx].xpos[:2] in ["NN"]: #need to further test this
			token.cxtag = "tocls+rel" 

	if token.cat6 in ["ingcls"] and token.deprel in ["xcomp","csubj"]: #csubj added 2025-02-09
		if sent[token.headidx].xpos[:2] in ["VB"]: #updated 2024-10-08
			token.cxtag = "ingcls+vcomp"
		elif sent[token.headidx].xpos[:2] in ["NN"]: #need to further test this
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
			if token.xpos in ["NNP","NNPS"] or sent[token.headidx].xpos in ["NNP","NNPS"]: #consider constraining NNP + NN*; constrained on 2025-02-09
				nnpremod = False #this is a dummy/unused variable
			else:
				if len(token.word) > 1: #added on 2025-01-02
					token.cxtag = "nn+npremod" 
	elif token.deprel in ["conj"] and token.xpos in ["JJ","VBN"] and sent[token.headidx].cxtag == "attr+npremod":
		token.cat1 = "attr"
		token.cxtag = "attr+npremod"
	#To-Do: add code to catch coordinated premodifying adjective phrases (they form a chain of "conj" relations)
	if token.lxgrtag in ["in"] and token.headdeprel not in ["npadvmod"]: #the "and" statement is an attempt to avoid constructions such as "bit by bit" and "sentence to sentence" being counted here 
		if token.idx > token.headidx and token.cat1 in ["nmod"]:
			if token.lemma == "of" and token.idx >= 1 and sent[token.idx-1].lxgrtag not in ["inphrsl"]:
				token.cxtag = "of+npostmod"
			else:
				token.cxtag = "in+npostmod"
		if token.cat1 in ["jcomp"]:
			if sent[token.headidx].xpos in ["JJR"] and token.lemma == "than":
				#token.cxtag = None
				token.cxtag = "in+comparative" #may remove this one (not in documentation)
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

def coordinatedClauseAdjust(token,sent): #deal with coordinate clauses and wh-words in coordinated VPs
	#deal with coordinated clauses
	if token.lxgrtag in ["vbmain"] and token.deprel in ["conj"] and token.cat2 not in ["nonfinite"]:
		if sent[token.headidx].cxtag in ["thatcls+vcomp","whcls+vcomp"]: #may need to extend this...
			token.cxtag = sent[token.headidx].cxtag
			token.cat5 = sent[token.headidx].cat5
			token.cat8 = sent[token.headidx].cat8

def cxLastPass(token,sent):
	if token.lxgrtag in ["rb"] and token.cat1 in ["othr"]:
		if sent[token.headidx].cxtag in ["in+advl"]:
			token.cxtag = "rb+advl"


#############################

#### These functions use the previous functions to conduct tagging and tallying of lexicogramamtical features ###


# test = processConllu(open('/Users/kristopherkyle/Desktop/Programming/Corpora/dep_parse_onto/bc-cctv-00-cctv_0000.parse.dep').read().strip())
# for token in test[0].sents:
# 	print(token.text, token.lemma_)

# structTest = nlp("This is a sample text.")
# for token in structTest:
# 	print(token.head)
def preprocess(text,conllu = False): #takes raw text, processes with spacy, then outputs a list of sentences filled with tokenObjects
	sentCounter = 0
	output = []
	if conllu == True:
		doc = processConllu(text)
	else:
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

def tag(input,conllu = False): #tags :)
	sents = []
	if isinstance(input,str) == True:
		input = preprocess(input,conllu)
	for sent in input:
	#for sent in preprocess(sstring):
		for token in sent.tokens:
			#print(token.idx,token.word,token.lemma,token.deprel,token.headidx)
			#deal with multiword units first
			multiWordPrepositions(token,sent.tokens)
			multiWordSubordinators(token,sent.tokens)
			semiModalAdjust(token,sent.tokens)
			multiWordAdverbs(token,sent.tokens)
			multiWordLinkingAdverbs(token,sent.tokens)

		
		for token in sent.tokens:
			if token.deprel in ["goeswith"]:
				continue
			if token.cat1 in ["link"]:
				continue
			else:
				personal_pronouns(token)
				advanced_pronoun(token,sent.tokens)
				adverbs(token,sent.tokens)
				adjectives(token)
				nouns(token)
				verbs(token,sent.tokens)
				#multiWordPrepositions(token,sent.tokens) 
				prepositions(token,sent.tokens)
				coordinators(token,sent.tokens)
				subordinators(token,sent.tokens)
				determiners(token)
				that_wh(token,sent.tokens)
				complexity(token,sent.tokens)
				# semiModalAdjust(token,sent.tokens)
				coordinatedClauseAdjust(token,sent.tokens)
		for token in sent.tokens:
			if token.deprel in ["goeswith"]:
				continue
			cxLastPass(token,sent.tokens)
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
			if len(token) < 1:
				continue
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
		skipSent = False
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
				if info[3] == "XX":
					skipSent = True
				#no upos :(
				tokObj.deprel = info[6]
				if tokObj.deprel == "root":
					tokObj.headidx = tokObj.idx
				else:
					tokObj.headidx = int(info[5])-1
				
				sentObj.tokens.append(tokObj)
		if skipSent == False:
			outl.append(sentObj)
	return(outl)

### Work on 20241219-20 ###
#printer(tag(open('/Users/kristopherkyle/Desktop/Programming/Corpora/dep_parse_onto/bc-cctv-00-cctv_0000.parse.dep').read().strip(),conllu = True))
def tagConlluFolder(loFnames):
	folderOutput = []
	for fname in loFnames:
		print(fname.split("/")[-1])
		fileOutput = tag(open(fname).read().strip(),conllu = True)
		#printer(fileOutput,verbose = True)
		folderOutput = folderOutput + fileOutput
	return(folderOutput)

def sentTokCount(procConllu):
	nsents = 0
	ntokens = 0
	for sent in procConllu:
		nsents +=1
		for token in sent.tokens:
			ntokens += 1
	print(nsents,ntokens)

def iobConvert(procConllu):
	outL = [] #list of sents
	for sent in procConllu:
		sentL = []
		for token in sent.tokens:
			tokenL = []
			tokenL.append(token.word)
			tokenL.append(token.xpos)
			if token.cxtag in ["None",None]:
				tokenL.append("O")
			else:
				tokenL.append("I-"+token.cxtag)
			sentL.append("|".join(tokenL))
		outL.append(" ".join(sentL))
	return(outL)

def writeIOB(loSentStr,writeLoc,nSamps = False, splits = [.8,.1,.1],rSeed = 1234):
	random.seed = rSeed
	random.shuffle(loSentStr)
	if nSamps != False:
		targetSents = loSentStr[:nSamps]
	else:
		targetSents = loSentStr
	nsents = len(targetSents)
	train = targetSents[:int(nsents*splits[0])]
	dev = targetSents[int(nsents*splits[0]):int(nsents*(splits[0]+splits[1]))]
	test = targetSents[int(nsents*(splits[0]+splits[1])):]

	print("train:",len(train),"sents")
	print("dev:",len(dev),"sents")
	print("test:",len(test),"sents")

	with open(writeLoc +"train.iob", "w") as f:
		f.write("\n".join(train))
	with open(writeLoc +"dev.iob", "w") as f:
		f.write("\n".join(dev))
	with open(writeLoc +"test.iob", "w") as f:
		f.write("\n".join(test))

# work on 2025-02-21
### test selection of single-word linking adverbs
# printer(tag("First, I ate pizza, then I drank beer."),verbose = True)
# printer(tag("I want the first one."),verbose = True)
# printer(tag("Now, I am not sure, but I think I would like to eat pizza."),verbose = True)
# printer(tag("I would like to eat pizza now."),verbose = True)
# printer(tag("Similarly, she loves pizza."),verbose = True)
# printer(tag("I haven't been there yet. Yet, I would like to go."),verbose = True)
# printer(tag("Still, I would like to go climbing. I still like climbing."),verbose = True)
# printer(tag("I will buy the next round of beers."),verbose = True)
# printer(tag("He went to work, however, and tried to concentrate."),verbose = True)
# printer(tag("He went to work however he could."),verbose = True) #this construction is a bit weird, and "however" is tagged as part of an adverbial clause. But, it is not caught by lxgrtagger
# printer(tag("I ate pizza so I could have power."),verbose = True) #"so" was tagged as subordinator (appropriately)
### Single word items seem to be working correctly

### Test two-word prep-based linking adverbials
# printer(tag("In addition, I like pizza. For another, I like beer."),verbose = True)
# printer(tag("By comparison, I like pizza. In conclusion, I like beer."),verbose = True)

# ### Test three-word prep-based linking adverbials
# printer(tag("For one thing, I like pizza. On the contrary, I like beer."),verbose = True)
# printer(tag("At any rate, I like pizza. By the way, I like beer."),verbose = True)
# printer(tag("In spite of that, they like pizza. They like pizza in spite of the risks."),verbose = True)

### Test four-word prep-based linking adverbials
# printer(tag("By the same token, I like pizza. In the first place, I like beer."),verbose = True)
# printer(tag("On the other hand, I like pizza. In the second place, I like beer."),verbose = True)

#test other cases
# ["first of all"] #advmod
# 0 First first None rb link None None None None None None None RB advmod 5
# 1 of of None in in_othr None None None None None None None IN prep 0
# 2 all all None None None None None None None None None None DT pobj 1
# ["after all"] #advmod advmod
# 0 After after rb+jjrbmod rb othr None None None None None None None RB advmod 1
# 1 all all rb+advl rb advl None None None None None None None RB advmod 4
# ["all in all"] #npadvmod
# 0 All all None rb othr None None None None None None None DT advmod 1
# 1 in in None None None None None None None None None None IN npadvmod 5
# 2 all all None rb othr None None None None None None None DT advmod 1
#["to summarize","to conclude"] #advcl
# 0 To to None to None None None None None None None None TO aux 1
# 1 summarize summarize tocls+advl vbmain vblex nonfinite simple active advlcls tocls None None VB advcl 4
#["to begin with"] #advcl
# 0 To to None to None None None None None None None None TO aux 1
# 1 begin begin tocls+advl vbmain prepv nonfinite simple active advlcls tocls None None VB advcl 5
# 2 with with None rb prtcle None None None None None None None IN prt 1
# ["which is to say"] #xcomp
# 0 Which which None None None None None None None None None None WDT nsubj 1
# 1 is be None vbmain be pres simple active None None None None VBZ ROOT 1
# 2 to to None to None None None None None None None None TO aux 3
# 3 say say tocls+vcomp vbmain vblex nonfinite simple active compcls tocls vcomp None VB xcomp 1

# printer(tag("First of all, I like pizza. After all, I like beer."),verbose = True)
# printer(tag("I like beer after all."),verbose = True)

# printer(tag("All in all, I like pizza. To summarize, I like beer."),verbose = True)
# printer(tag("To begin with, I like pizza. Which is to say, I like beer."),verbose = True)
# printer(tag("I like beer, which is to say, I am human."),verbose = True)




# work on 2025-02-09
#nn+npremod
# printer(tag("The President car is here."), verbose=True) #correct


## csubjs:
# printer(tag("Winning the game is why I am here."), verbose=True) #correct
# printer(tag("To climb is to live."), verbose=True) #correct
# printer(tag("he survived the fall suprised everyone."), verbose=True) #correct
# # printer(tag("How he returned shocked the world."), verbose=True) #correct
# printer(tag("well these are identical, the only difference is that, they have a different number."), verbose=True) #correct


# Work on 2025-02-03
# printer(tag("I sort of like this."), verbose=True) #correct
# printer(tag("A colored pencil is a sort of pencil"), verbose=True) #correct

# printer(tag("i pretty much used it sort of like a model"),verbose = True) #correct
# printer(tag("I kind of like this."), verbose=True) #correct
# printer(tag("people who write about music sort of continually have to cover every base"), verbose=True) #correct
# #correct:
# printer(tag("these continuous models can get increasingly complex to try and describe, the sort of average kinds of effects that are going on and so on"), verbose=True)
# #incorrect due to parser error (sort of assigned as dep of NN, not JJ)
# printer(tag("i steer clear of definitions i don't even know what i want i'm inconsistent, you know i take from a lot of different sources i create a lot of different kinds of work, and in fact he's an artist that ranges from, a kind of photo-realism, in this painting based on a photograph, to complete sort of abstract paintings"), verbose=True)

# #as soon as
# printer(tag("I will come as soon as I am finished"),verbose = True) #fixed
# printer(tag("I will come when I am finished"),verbose = True) 

# #work on 2025-01-16
# processedConllu = tagConlluFolder(glob.glob('/Users/kristopherkyle/Desktop/Programming/Corpora/dep_parse_onto/*.parse.dep'))
# #Need to assign root head to itself (currently 0|-1)
# sentTokCount(processedConllu)
# processedConlluIob = iobConvert(processedConllu)
# processedConlluIob[0]
# len(processedConlluIob) #134739
# #test with 10k sents
# # import random
# # #write 10k Sample
# # writeIOB(processedConlluIob,'/Users/kristopherkyle/Desktop/Programming/TrainLxGrTgr/LxGr-10k-TRF-20241231/assets/',nSamps = 10000)
# #write full (134k) Sample
# writeIOB(processedConlluIob,'/Users/kristopherkyle/Desktop/Programming/TrainLxGrTgr/LxGr134k-TRF-20250116-059/assets/')

# #work on 2024-12-31
# processedConllu = tagConlluFolder(glob.glob('/Users/kristopherkyle/Desktop/Programming/Corpora/dep_parse_onto/*.parse.dep'))
# #Need to assign root head to itself (currently 0|-1)
# sentTokCount(processedConllu)
# processedConlluIob = iobConvert(processedConllu)
# processedConlluIob[0]
# len(processedConlluIob) #134739
# #test with 10k sents
# import random
# #write 10k Sample
# writeIOB(processedConlluIob,'/Users/kristopherkyle/Desktop/Programming/TrainLxGrTgr/LxGr-10k-TRF-20241231/assets/',nSamps = 10000)
# #write full (134k) Sample
# writeIOB(processedConlluIob,'/Users/kristopherkyle/Desktop/Programming/TrainLxGrTgr/LxGr134k-TRF-20241231/assets/')


# printer([processedConllu[0]],verbose = True)
# print(processedConllu[0])



#test conll
#conllLoS = tag(readConll("sample_conll/bc-cctv-00-cctv_0000.parse.dep"))
#printer(conllLoS[:3])

### Tests on 2024-11-12 (sents from Hakyung)
# printer(tag("As far as we know, the meeting is still scheduled for tomorrow."), verbose=True)
# printer(tag("The meeting is still scheduled for tomorrow, as far as we know."), verbose=True)
# printer(tag("I am going as far as Dallas."), verbose=True)

### Not implemented ###
# printer(tag("He contributed his ideas, as well as his time, to the project."), verbose=True) #not sure I agree with this one - it is functioning as a conjunction? = "and"; or perhaps it is analogous to "in addition to"
### ###

# printer(tag("The policy was implemented as opposed to being optional."), verbose=True)
# printer(tag("The policy was implemented instead of being optional."), verbose=True)
# printer(tag("The concept is valuable as distinct from its execution."), verbose=True)
# printer(tag("The representation of space is necessary in order to be aware of things as distinct from ourselves and from each other"), verbose=True)

# printer(tag("They offered extra services in exchange for a higher fee."), verbose=True)
# printer(tag("She did the extra work in return for a day off."), verbose=True)
# printer(tag("He built the structure by means of recycled materials."), verbose=True)
# printer(tag("By virtue of her experience, she was appointed as the team lead."), verbose=True)
# printer(tag("They traveled by way of several small towns."), verbose=True)
# printer(tag("For lack of better options, we chose this route."), verbose=True)
# printer(tag("For want of attention, the project stalled."), verbose=True)
# printer(tag("The charity event was held in aid of local hospitals."), verbose=True)
# printer(tag("They stored extra supplies in back of the main building."), verbose=True)
# printer(tag("In case of rain, the event will be held indoors."), verbose=True)
# printer(tag("She took control in charge of the emergency response."), verbose=True)
# printer(tag("In consequence of the new policy, many changes were implemented."), verbose=True)
# printer(tag("The proposal was accepted in favor of further negotiations."), verbose=True)
# printer(tag("The statue stands prominently in front of the building."), verbose=True)
# printer(tag("He accepted a gift in lieu of cash payment."), verbose=True)
# printer(tag("The decision was made in light of recent findings."), verbose=True)
# printer(tag("The organization was created in need of a better system."), verbose=True)
# printer(tag("She took on new responsibilities in place of a promotion."), verbose=True)
# printer(tag("The discussion focused on recent updates in respect of regulations."), verbose=True)
# printer(tag("They went hiking in search of beautiful landscapes."), verbose=True)
# printer(tag("She proceeded with the plan in spite of objections."), verbose=True)
# printer(tag("The contract is specified in terms of annual renewals."), verbose=True)
# printer(tag("The initiative was undertaken in view of the growing demand."), verbose=True)
# printer(tag("The meeting was canceled on account of bad weather."), verbose=True)
# printer(tag("She spoke passionately on behalf of her colleagues."), verbose=True)
# printer(tag("The project was halted on grounds of safety concerns."), verbose=True)
# printer(tag("The supplies were stacked on top of each other."), verbose=True)
# printer(tag("They evaluated the project by reference to past results."), verbose=True)
# printer(tag("The speech was inspiring in addition to being informative."), verbose=True)
# printer(tag("The report was clear in contrast to the vague instructions."), verbose=True)
# printer(tag("The decision was made in reference to previous cases."), verbose=True)
# printer(tag("The new guidelines were created in regard to ethical standards."), verbose=True)
# printer(tag("She considered the proposal in relation to the company's mission."), verbose=True)
# printer(tag("They proceeded with the project with regard to potential risks."), verbose=True)
# printer(tag("The updates were made with reference to customer feedback."), verbose=True)
# printer(tag("The team made adjustments with respect to new requirements."), verbose=True)
# printer(tag("The results are at variance with initial predictions."), verbose=True)
# printer(tag("Their actions are in accordance with the agreement."), verbose=True)
# printer(tag("They analyzed the results in comparison with the previous data."), verbose=True)
# printer(tag("The product was tested in compliance with industry standards."), verbose=True)
# printer(tag("The design was created in conformity with company guidelines."), verbose=True)
# printer(tag("The company remains in contact with its partners."), verbose=True)
# printer(tag("Their decisions are in line with company policies."), verbose=True)
# printer(tag("The delay occurred as a result of unforeseen circumstances."), verbose=True)
# printer(tag("He made sacrifices at the expense of his personal life."), verbose=True)
# printer(tag("They moved abroad for the sake of their children’s education."), verbose=True)
# printer(tag("The document was revised in the case of any errors."), verbose=True)
# printer(tag("They activated the backup plan in the event of an emergency."), verbose=True)
# printer(tag("The rules were reconsidered in the light of recent developments."), verbose=True)
# printer(tag("He was dismissed on the grounds of misconduct."), verbose=True)
# printer(tag("The issues were discussed on the ground of common interest."), verbose=True)
# printer(tag("The meeting was arranged on the part of senior management."), verbose=True)
# printer(tag("All employees attended with the exception of the manager."), verbose=True)
# printer(tag("There is a park at the back of the office building."), verbose=True)
# printer(tag("They gathered in the middle of the plaza."), verbose=True)

### Tests on 2024-11-06 (multi-word infinitives)
# #fixed:
# printer(tag("You don't have to live under the same laws as a foreigner in order to trade with him."),verbose = True) #spacy tags mark+mark #not a problem
# #works, but may need to clean up phrasal bits (TO DO)
# printer(tag("Each has the job of writing his chapter so as to make the novel being constructed the best it can be."),verbose = True) #spacy tags mark+mark #not a problem

### Tests on 2024-11-06 tests on multi-word adverbials

#minor issues (change tag to cs) Done
# printer(tag("He acted as if I owed him."),verbose = True) #spacy tags mark+mark #not a problem
# printer(tag("He acted as though I owed him."),verbose = True) #spacy tags mark+mark
# printer(tag("I came to the party so that I could eat pizza."),verbose = True) #spacy tags mark+mark
# printer(tag("I was fortunate in that I had friends."),verbose = True) #spacy tags mark+mark
#fixed:
# printer(tag("Even though he loved pizza, he couldn't stay."),verbose = True) #spacy tags advmod+mark
# printer(tag("The artist painted the scene such that it appeared almost lifelike in the dim light."),verbose = True) #spacy tags amod+mark
# printer(tag("I will eat some pizza as long as it has pepperoni."),verbose = True) #spacy tags advmod+advmod+mark
# printer(tag("He couldn't stay even though he loved pizza."),verbose = True) #spacy tags advmod+mark

#causes problem with clause type identification (Fixed)
# printer(tag("In case you didn't hear, I like pizza."),verbose = True) #spacy tags prep+pobj #introduces "acl"
# printer(tag("If you didn't hear, I like pizza."),verbose = True) #spacy tags prep+pobj #introduces "acl"

# printer(tag("In case I die, bury me with pizza."),verbose = True) #spacy tags prep+pobj
# printer(tag("I like pizza, in case you didn't hear."),verbose = True) #spacy tags prep+pobj
# printer(tag("I came to the party in order that I could eat pizza."),verbose = True) #spacy tags prep+pobj+mark #introduces "acl"
# printer(tag("In the event that they run out of pizza, I am leaving."),verbose = True) #spacy tags prep+det+pobj+mark #introduces "acl"
# printer(tag("I will come to the event on condition that there is pizza."),verbose = True) #spacy tags prep+pobj+mark #introduces "acl"
# printer(tag("I will come to the event on the condition that there is pizza."),verbose = True) #spacy tags prep+pobj+mark #introduces "acl"

#pcomp (fixed)
# printer(tag("I will come to the event provided that there is pizza."),verbose = True) #spacy tags prep+mark #introduces "pcomp"
# printer(tag("I wanted to go, except that they didn't have pizza."),verbose = True) #spacy tags prep+mark #introduces "pcomp"
# printer(tag("The house was perfectly quiet, save that the wind occasionally rattled the windows."),verbose = True) #spacy tags prep+mark #introduces "pcomp"

# #not quite sure (TO DO)
# printer(tag("I will eat pizza rather than go to the event."),verbose = True) #spacy tags advmod+cc
# printer(tag("But that he was poor, he would travel extensively."),verbose = True) #spacy tags cc+mark

## "That" is an issue: ##

###
# printer(tag("As far as we know, the meeting is still scheduled for tomorrow."),verbose = True) #spacy tags as amod+prep

### Tests on 2024-11-05 two-word prepositions
# printer(tag("I love delicious foods such as pizza."),verbose = True) #spacy tags as amod+prep
# printer(tag("As for Jack, he will eat pizza."),verbose = True) #spacy tags as prep+prep
# printer(tag("He would die but for pizza."),verbose = True) #spacy tags as prep+prep
# printer(tag("The pizza will be done as of this evening."),verbose = True) #spacy tags as prep+prep
# printer(tag("Except for pizza, there is nothing good in this world."),verbose = True) #spacy tags as prep+prep
# printer(tag("Save for pizza, there is nothing good in this world."),verbose = True) #spacy tags as prep+prep
# printer(tag("Apart from pizza, there is nothing good in this world."),verbose = True) #spacy tags as advmod+prep
# printer(tag("There is nothing good in this world apart from pizza."),verbose = True) #spacy tags as advmod+prep
# printer(tag("There is nothing good in this world apart from pizza."),verbose = True) #spacy tags as advmod+prep
# printer(tag("Aside from pizza, there is nothing good in this world."),verbose = True) #spacy tags as advmod+prep
# printer(tag("The pizza was identified as from Italy."),verbose = True) #spacy tags as prep+prep
# printer(tag("He came away from the pizza."),verbose = True) #spacy tags as advmod+prep
# printer(tag("He finished ahead of the pack."),verbose = True) #spacy tags as advmod+prep
# printer(tag("He survived because of the pizza."),verbose = True) #spacy tags as pcomp+prep
# printer(tag("Because of the pizza he survived."),verbose = True) #spacy tags as pcomp+prep
# printer(tag("The pizza was devoid of pepperoni."),verbose = True) #spacy tags as acomp+prep
# printer(tag("This pizza was delicious, exclusive of the anchovies."),verbose = True) #spacy tags as acomp + prep
# printer(tag("Exclusive of the anchovies, I like this pizza."),verbose = True) #spacy tags as advcls + prep (wrong)
# printer(tag("The pizza will be ready inside of an hour."),verbose = True) #spacy tags as advmod+prep
# printer(tag("Instead of salad, please give me pizza."),verbose = True) #spacy tags as advmod+prep
# printer(tag("Please give me pizza instead of salad."),verbose = True) #spacy tags as advmod+cc
# printer(tag("Irrespective of the type, please give me pizza."),verbose = True) #spacy tags as advmod+prep
# printer(tag("Please give me pizza irrespective of the type."),verbose = True) #spacy tags as advmod+prep
# printer(tag("The pizza came out of the oven."),verbose = True) #spacy tags as prep+prep
# printer(tag("They saw the pizza outside of the store"),verbose = True) #spacy tags as advmod+prep
# printer(tag("I want to eat pizza regardless of its origins."),verbose = True) #spacy tags as advmod+prep
# printer(tag("We have spent upwards of three thousand dollars on this project."),verbose = True) #spacy tags as advmod+quantmod
# printer(tag("We have spent upwards of three dollars on this project."),verbose = True) #spacy tags as advmod+quantmod
# printer(tag("The pizza was void of any vegetables."),verbose = True) #spacy tags as acomp+prep
# printer(tag("He was found void of any vegetables."),verbose = True) #spacy tags as acomp+prep
# printer(tag("Depending on the outcome of the election, I might eat pizza."),verbose = True) #spacy tags as prep+prep
# printer(tag("According to Tom, we will never find an answer."),verbose = True)#spacy tags as prep+prep
# printer(tag("As to the solution, I have no idea."),verbose = True) #spacy tags as prep+prep
# printer(tag("I found some ranch dressing close to the pizza."),verbose = True) #spacy tags as advmod+prep
# printer(tag("Contrary to popular opinion, I don't eat very much pizza."),verbose = True) #spacy tags as advmod+prep
# printer(tag("Due to its deliciousness, I eat a lot of pizza."),verbose = True) #spacy tags as advmod+prep
# printer(tag("I live next to a pizza shop."),verbose = True) #spacy tags as advmod+prep
# printer(tag("We have transitioned on to the next project."),verbose = True) #spacy tags as prep+prep
# printer(tag("I live opposite to a pizza shop."),verbose = True) #spacy tags as advmod+prep
# printer(tag("Owing to its nutritional density, I eat pizza every day."),verbose = True) #spacy tags as advlcls+prep
# printer(tag("Preliminary to moving on, we need to eat pizza."),verbose = True) #spacy tags as advmod+prep
# printer(tag("Previous to moving on, we need to eat pizza."),verbose = True) #spacy tags as advmod+prep
# printer(tag("Prior to moving on, we need to eat pizza."),verbose = True) #spacy tags as advmod+prep
# printer(tag("Relative to lasagna, pizza is healthy."),verbose = True) #spacy tags as advmod+prep
# printer(tag("Subsequent to moving on, we need to eat pizza."),verbose = True) #spacy tags as advmod+prep
# printer(tag("Thanks to the award, we now have money."),verbose = True) #spacy tags as prep+prep
# printer(tag("The decision is up to the pizza monarch."),verbose = True) #spacy tags as prep+prep
# printer(tag("I like pizza along with beer."),verbose = True) #spacy tags as prep+prep
# printer(tag("I like pizza together with beer."),verbose = True) #spacy tags as advmod+prep
# printer(tag("Let's go back to the start."),verbose = True) #spacy tags as advmod+prep

# # Three word
# printer(tag("As far as Boston there is great scenery."),verbose = True) #doesn't work



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
# "gon na" causes issues - future development could iron out these bugs[fixed in version 05_51]
# printer(tag("He said that they have to try."),verbose = True)
# printer(tag("He said that they had to try."),verbose = True)
# printer(tag("He said that they got to try."),verbose = True)
#printer(tag("He said that they ought to try."),verbose = True)
# printer(tag("He said that they should try."),verbose = True)
# printer(tag("He said that they ought to have tried."),verbose = True)

# printer(tag("He said that they are gonna try"),verbose = True)
# printer(tag("He said that they gotta try"),verbose = True)

#three-word modals
# printer(tag("He said that they have got to try."),verbose = True)
# printer(tag("He said that they had got to try."),verbose = True)

#be three-word modals
# printer(tag("He said that he was supposed to try."),verbose = True)
# printer(tag("He said that he was going to try."),verbose = True)
# printer(tag("He said that he was about to try."),verbose = True)
# printer(tag("He said that they used to try."),verbose = True)



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
