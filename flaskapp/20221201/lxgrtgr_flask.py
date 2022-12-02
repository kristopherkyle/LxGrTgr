import os

from flask import Flask, redirect, render_template, request, url_for

import LxGrTgr_01 as lxgr

version = ".02" 

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

def rundata(text):
	#print(text)
	if len(text) == 0:
		output = None
	else:
		output = []
		tagged =  lxgr.tag(text)
		for sent in tagged:
			for token in sent:
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


