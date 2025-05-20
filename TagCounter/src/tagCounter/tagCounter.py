#tag counter
import glob #for finding all filenames in a folder
import os #for making folders
from random import sample #for random samples
import re #for regulat expressions
#from importlib_resources import files #for opening package files - need to include in package dependencies
import math
from pathlib import Path #windows + mac compatibility

def countTagsFile(fname,tagList = None): 
	if tagList == None:
		tagList = ["finitecls+advl","thatcls+vcomp","whcls+vcomp","finitecls+rel","thatcls+ncomp","thatcls+jcomp","xtrapos+thatcls+jcomp","whcls+incomp","tocls+advl","ingcls+advl","edcls+advl","tocls+vcomp","tocls+ncomp","ingcls+vcomp","edcls+rel","ingcls+rel","tocls+rel","tocls+jcomp","xtrapos+tocls+jcomp","ingcls+incomp","rb+advl","in+advl","attr+npremod","nn+npremod","of+npostmod","in+npostmod","appos+npostmod","in+jcomp","rb+jjrbmod"]
	outd = {"ntokens":0}
	ignored = []
	for tag in tagList:
		outd[tag] = 0
	sents = open(Path(fname), encoding = "utf-8", errors = "ignore").read().strip().split("\n\n")
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
	targetDir = Path(targetDir)
	# if targetDir[-1] != "/":
	# 	targetDir = Path(targetDir + "/")
	fnames = list(targetDir.glob("*" + suff))
	#fnames = glob.glob(targetDir + "*" + suff) #get all filenames
	for fname in fnames:
		simpleName = Path(fname).name
		#simpleName = fname.split("/")[-1]
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
	outf = open(Path(outName),"w",encoding = "utf-8")
	outf.write("\n".join(outL))
	outf.flush()
	outf.close()
	print("Finished writing output to",outName)