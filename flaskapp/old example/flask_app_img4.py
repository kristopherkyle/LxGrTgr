#this version works on kris' conda venv taaledflask
#need to make plotnine plots work again
#need radio button for language
#need radio button for index

import os

from flask import Flask, redirect, render_template, request, url_for
from pylats import lats #version 0.37
from taaled import ld #version 0.32
#import pre_process_04 as pp #import TAALED
import base64
from io import BytesIO
from matplotlib.figure import Figure
import numpy as np #used to get mean - could use lower overhead package
import seaborn as sns #for kde (density plots) seaborn makes pretty plot fairly easily

#template for making figures
# def figtest():
# 	# Generate the figure **without using pyplot**.
# 	fig = Figure()
# 	ax = fig.subplots()
# 	ax.plot([1, 2])
# 	# Save it to a temporary buffer.
# 	buf = BytesIO()
# 	fig.savefig(buf, format="png")
# 	# Embed the result in the html output.
# 	data = base64.b64encode(buf.getbuffer()).decode("'utf-8'")
# 	return(data)

#template for making plots for html with pure matplotlib
# def histogram(invals):
# 	fig = Figure() #this is needed instead of the default pyplots to export to html properly
# 	ax = fig.subplots()
# 	ax.hist(invals)
# 	#how to make a vline with matplotlib
# 	ax.vlines(np.mean(invals),0,1,transform=ax.get_xaxis_transform(), colors='r')
# 	buf = BytesIO()
# 	fig.savefig(buf, format="png")
# 	# Embed the result in the html output.
# 	data = base64.b64encode(buf.getbuffer()).decode("'utf-8'")
# 	return(data)

def kde(invals): #for density plots
	sns.set() #make palette pretty (seaborn defaults)
	fig = Figure()
	ax = fig.subplots()
	#ax.hist(invals)
	#how to make a vline with matplotlib
	sns.kdeplot(ax=ax, data = invals) #create kde (density) plot
	ax.vlines(np.mean(invals),0,1,transform=ax.get_xaxis_transform(), colors='r') #there might be a better way to do this with seaborn
	buf = BytesIO() #create buffer to save to
	fig.savefig(buf, format="png") #save figure to buffer
	# Embed the result in the html output.
	data = base64.b64encode(buf.getbuffer()).decode("'utf-8'") #get data for html plot
	return(data)

def freq_form(freql): #create string representation of sorted frequency list
	return(", ".join([x[0] + " (" + str(x[1]) + ")" for x in freql]))

def rundata(text):
	#print(text)
	outd = {}
	if len(text) == 0:
		outd["text"] = "No text entered!"
		outd["value"] = "n/a"
		outd["tokens"] = "n/a"
		outd["types"] = "n/a"
		
	else:
		tokenized = lats.Normalize(text, params = lats.ld_params_en_trf)
		output = ld.lexdiv(tokenized.toks)
		print(output)
		#output = pp.mattr(pp.normalize(pp.text2tok(request.form["contents"])))
		#outd["text"] = output.text
		outd["type_freq"] = freq_form(output.freqs)
		#outd["ntokens"] = output.ntokens
		#outd["ntypes"] = output.ntypes
		outd["value"] = output.mattr
		#outd["nwindows"] = output.nwindows
		#updated data visualization code:
		#outd["image"] = histogram(output.mattrs)
		outd["image"] = kde(output.mattrs)
	return(outd)


app = Flask(__name__)
@app.route('/', methods = ['GET', 'POST'])

def index():

	if request.method == "POST": #if we have data to work with
		processed = rundata(request.form["contents"]) #process data from form using the rundata() function
		return render_template("main_index9.html", items = [processed])
	else: #this is the landing page.

		return render_template("landing.html")


if __name__ == '__main__':
	app.run()


sample = """No. he bought a Christmas gift for his parents at the department store. he asked shopmaster, "Excuse me. How much this watch? Shopmaster said, " This is a service price for today.". " really?" he said. " please bring me a red watch please.". "Sure.", he said. Yes. I am going to the present for my family. I think my son want to play a computer game. kindly and gently computer game I bought for them. The computer game is very violence in today, but I don't like it. Yes. Maybe, my son believes a Santa Clause in today. But I think he take care of me about Christmas gift.
Hello. XXX02 speaking. Yes. would you go to watch the TV? Watch the movie? which do you like, "Sixth Sense" or "Gozzilla"? I'm, too. do you have lunch with me? what time is watching to movie? In today. I am going to be Shibuya. Do you know the Shibuya? we will met a Hachikomae. Do you know? so I will go to the Shibuya three o'clock, before Hachikomae. Yes. I like the watching the movie on video at home because the movie fee is very expensive in Japan. all my family go to watch movie, four members' fee is ten thousand yen. Very expensive.
. One day last week, my son met his uncle at a front of restaurant. Because my son's the birthday, my son's uncle bring to him famous restaurant in my town. and his uncle reserved the table in restaurant. waitress send to them restaurant's menu. His uncle said, "Do you have any drink?". "" my son said " I want the beer.". " really? I drink the wines", said his uncle. They are enjoy the dinner very well. My son's is very satisfy for today's dinner. his uncle pay for the dinner. And, eight o'clock, my son was came back. His son said, "Take care of yourself. Good-bye.". My son said, "Good-bye. Thank you.". My family likes a Italian restaurant. My family likes "Chanti" in Nishiazabu. Very famous Italian restaurant. The restaurant is very old restaurant in Japan. And the price more than any other restaurant in Tokyo. But, today, is very cheap for dinner in "Chanti". Interior? Simple. And the restaurant interior is a very simple, and very chic and very small. The service is very kindly and gently."""
# #Tests
# import mpld3

# print(lats.version)
# print(ld.version)
# sample = lats.Normalize(sample, params = lats.ld_params_en_trf)
# sample.toks
# #sample.text #error
# i = histogram(ldvals.mattrs)
# ldvals = ld.lexdiv(sample.toks)
# kde(ldvals.mattrs)
# fig = Figure()
# ax = fig.subplots()
# sns.kdeplot(ax=ax, data = ldvals.mattrs)
# buf = BytesIO()
# fig.savefig(buf, format="png")
# # Embed the result in the html output.
# data = base64.b64encode(buf.getbuffer()).decode("'utf-8'")
# data

# np.mean(ldvals.mattrs)
# test = mpld3.fig_to_html(ldvals.mattrplot)
# # mpld3.save_html(ldvals.mattrplot,"test.html") #this isn't working. May need to use matplotlib instead :()
# # ldvals.freqs
# ldvals.mattrs
# import matplotlib.pyplot as plt, mpld3
# plt.plot([3,1,4,1,5], 'ks-', mec='w', mew=5, ms=20)
# mpld3.show()
# tst = plt.figure()
# mpld3.fig_to_html(tst)


# # importing libraries
# import seaborn as sns
# df2 = sns.load_dataset('iris')
# sns.displot(a=ldvals.mattrs, color='green')
# fig = plt.figure()
# mpld3.fig_to_html(fig)
# mpld3.show()
# mpld3.fig_to_html(myviz)


# import matplotlib.pyplot as plt,mpld3
# from mpld3 import save_json, fig_to_html, plugins, save_html
# import numpy as np

# X = 'x'

# fig, ax = plt.subplots(1, 1, figsize=(8, 2))
# ecg = X
# fig = plt.figure()
# alt = np.arange(len(ecg))/125
# lines = ax.plot(alt,ecg)
# mpld3.plugins.connect(fig, mpld3.plugins.LineLabelTooltip(lines[0]))
# thisTest = mpld3.fig_to_html(fig)
# mpld3.save_html(fig,"test20220802.html")
# mpld3.show()

# #test from scratch
# import base64
# from io import BytesIO

# from matplotlib.figure import Figure


