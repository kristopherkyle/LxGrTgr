import os

from flask import Flask, redirect, render_template, request, url_for

import LxGrTgr_05_63 as lxgr

version = ".0563"

class sampleTok():	
	def __init__(self): 
		self.idx = "" 
		self.word = ""
		self.lemma = ""
		self.upos = ""
		self.xpos = ""
		self.deprel = ""
		self.head = ""
		self.headidx = ""
		self.children = ""
		self.cxtag = ""
		self.lxgrtag = ""
		self.cat1 = ""
		self.cat2 = ""
		self.cat3 = ""
		self.cat4 = ""
		self.cat5 = ""
		self.cat6 = ""
		self.cat7 = ""
		self.cat8 = ""
		self.cat9 = ""

def simplify_output(tokObj):
	if tokObj.cxtag == None:
		tokObj.cxtag = ""
	if tokObj.lxgrtag == None:
		tokObj.lxgrtag = ""
	if tokObj.cat1 == None:
		tokObj.cat1 = ""
	if tokObj.cat2 == None:
		tokObj.cat2 = ""
	if tokObj.cat3 == None:
		tokObj.cat3 = ""
	if tokObj.cat4 == None:
		tokObj.cat4 = ""
	if tokObj.cat5 == None:
		tokObj.cat5 = ""
	if tokObj.cat6 == None:
		tokObj.cat6 = ""
	if tokObj.cat7 == None:
		tokObj.cat7 = ""
	if tokObj.cat8 == None:
		tokObj.cat8 = ""
	return(tokObj)

def rundata(text):
	#print(text)
	if len(text) == 0:
		output = None
	else:
		output = []
		tagged =  lxgr.tag(text)
		for sent in tagged:
			for token in sent.tokens:
				token = simplify_output(token)
				output.append(token)
			bufferTok = sampleTok()
			output.append(bufferTok)
	return(output)


app = Flask(__name__)
@app.route('/', methods = ['GET', 'POST'])

def index():

	if request.method == "POST": #if we have data to work with
		processed = rundata(request.form["contents"]) #process data from form using the rundata() function
		if processed == None:
			return render_template("landing.html")
		else:
			return render_template("rendered.html", items = processed) #previously items = [processed]
	else: #this is the landing page.

		return render_template("landing.html")


if __name__ == '__main__':
	app.run()


