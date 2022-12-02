import os

from flask import Flask, redirect, render_template, request, url_for

import LxGrTgr_01 as lxgr

version = ".01" 

def rundata(text):
	#print(text)
	if len(text) == 0:
		output = None
	else:
		output = [item for sublist in lxgr.tag(text) for item in sublist] #make output a flat list
		for x in output:
			for tag in [x.lxgrtag,x.cat1,x.cat2,x.cat3,x.cat4,x.cat5,x.cat6,x.cat7,x.cat8]:
				if tag == None:
					tag = ""
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


