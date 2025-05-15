from __future__ import division
import sys

#import spacy #this is for if spaCy is used
import tkinter as tk
import tkinter.font
import tkinter.filedialog
import tkinter.constants
import queue
from tkinter import messagebox
import lxgrtgr as lxgr #double check this works
#from lxgrtgr import countTagsFolder,writeCounts

import os
import sys
import re
import platform
#import shutil
#import subprocess
import glob
import math
from collections import Counter
# try:
# 	import xml.etree.cElementTree as ET
# except ImportError:
# 	import xml.etree.ElementTree as ET

#V1.2 includes a number of lemmatization fixes
#v4 fixes a bug that excluded all upper-case words

###THIS IS NEW IN V1.3.py ###
from threading import Thread

#This creates a que in which the core TAALES program can communicate with the GUI
dataQueue = queue.Queue()

#This creates the message for the progress box (and puts it in the dataQueue)
progress = "...Waiting for Data to Process"
dataQueue.put(progress)

#Def1 is the core program; args is information passed to program
def start_thread(def1, arg1, arg2, arg3): 
	t = Thread(target=def1, args=(arg1, arg2, arg3))
	t.start()

#This allows for a packaged gui to find the resource files.
def resource_path(relative):
	if hasattr(sys, "_MEIPASS"):
		return os.path.join(sys._MEIPASS, relative)
	return os.path.join(relative)

#color = "#489D46"
color = "#A2AAAD"

prog_name = "LxGrTagger Tag Counter v0.67"

if platform.system() == "Darwin":
	system = "M"
	title_size = 16
	font_size = 14
	geom_size = "525x375"
elif platform.system() == "Windows":
	system = "W"
	title_size = 12
	font_size = 12
	geom_size = "525x475"
elif platform.system() == "Linux":
	system = "L"
	title_size = 14
	font_size = 12
	geom_size = "525x385"

def start_watcher(def2, count, folder):
	t2 = Thread(target=def2, args =(count,folder))
	t2.start()

class MyApp: #this is the class for the gui and the text analysis
	def __init__(self, parent):
				
		helv14= tkinter.font.Font(family= "Helvetica Neue", size=font_size)
		times14= tkinter.font.Font(family= "Lucida Grande", size=font_size)
		helv16= tkinter.font.Font(family= "Helvetica Neue", size = title_size, weight = "bold", slant = "italic")

				#This defines the GUI parent (ish)
		
		self.myParent = parent
		
		self.var_dict = {}
		
		#This creates the header text - Task:work with this to make more pretty!
		self.spacer1= tk.Label(parent, text= "Lexicogrammatical Tag Counter", font = helv16, background = color)
		self.spacer1.pack()
		
		#This creates a frame for the meat of the GUI
		self.thestuff= tk.Frame(parent, background =color)
		self.thestuff.pack()
		
		self.myContainer1= tk.Frame(self.thestuff, background = color)
		self.myContainer1.pack(side = tk.RIGHT, expand= tk.TRUE)
		self.instruct = tk.Button(self.myContainer1, text = "Instructions", justify = tk.LEFT)
		self.instruct.pack()
		self.instruct.bind("<Button-1>", self.instruct_mess)
				
		self.options_frame = tk.LabelFrame(self.myContainer1, text= "Norming", background = color)
		self.options_frame.pack(fill = tk.X,expand=tk.TRUE)
		
		#insert radiobutton here
		self.norm_var = tk.IntVar()
		self.norm_var.set(10000)
		self.lang_raw = tk.Radiobutton(self.options_frame, text="Raw", value = 0, variable=self.norm_var,background = color)
		self.lang_raw.grid(row=1,column=1, sticky = "W")
		self.lang_1k = tk.Radiobutton(self.options_frame, text="1k", value = 1000, variable=self.norm_var,background = color)
		self.lang_1k.grid(row=1,column=2, sticky = "W")
		self.lang_10k = tk.Radiobutton(self.options_frame, text="10k", value = 10000, variable=self.norm_var,background = color)
		self.lang_10k.grid(row=1,column=3, sticky = "W")
		self.lang_100k = tk.Radiobutton(self.options_frame, text="10k", value = 100000, variable=self.norm_var,background = color)
		self.lang_100k.grid(row=1,column=4, sticky = "W")
		self.lang_1mil = tk.Radiobutton(self.options_frame, text="100k", value = 1000000, variable=self.norm_var,background = color)
		self.lang_1mil.grid(row=1,column=5, sticky = "W")

		#self.lang_en.grid(row=1,column=1, sticky = "W")	
		self.var_dict["norm"] = self.norm_var

		self.options_frame2 = tk.LabelFrame(self.myContainer1, text= "Output", background = color)
		self.options_frame2.pack(fill = tk.X,expand=tk.TRUE)
		
		#insert radiobutton here
		self.outlist_var = tk.StringVar()
		self.outlist_var.set("cx")
		self.outl_cx = tk.Radiobutton(self.options_frame2, text="Complexity Tags", value = "cx", variable=self.outlist_var,background = color)
		self.outl_cx.grid(row=1,column=1, sticky = "W")
		self.outl_all = tk.Radiobutton(self.options_frame2, text="All Tags", value = "all", variable=self.outlist_var,background = color)
		self.outl_all.grid(row=1,column=2, sticky = "W")

		self.var_dict["outlist"] = self.outlist_var

		self.secondframe= tk.LabelFrame(self.myContainer1, text= "Count Tags in a Folder of Texts", background = color)
		self.secondframe.pack(fill = tk.X,expand=tk.TRUE) 
		
		
		#Creates default dirname so if statement in Process Texts can check to see
		#if a directory name has been chosen
		self.dirname = ""
		
		#This creates a label for the first program input (Input Directory)
		self.inputdirlabel =tk.LabelFrame(self.secondframe, height = "1", width= "45", padx = "4", text = "Your selected input folder:", background = color)
		self.inputdirlabel.pack(fill = tk.X)
		
		#Creates label that informs user which directory has been chosen
		directoryprompt = "(No Input Folder Chosen)"
		self.inputdirchosen = tk.Label(self.inputdirlabel, height= "1", width= "45", justify=tk.LEFT, padx = "4", anchor = tk.W, font= helv14, text = directoryprompt)
		self.inputdirchosen.pack(side = tk.LEFT)
		
		#This Places the first button under the instructions.
		self.button1 = tk.Button(self.inputdirlabel)
		self.button1.configure(text= "Select")
		self.button1.pack(side = tk.LEFT, padx = 5)
		
		#This tells the button what to do when clicked.	 Currently, only a left-click
		#makes the button do anything (e.g. <Button-1>). The second argument is a "def"
		#That is defined later in the program.
		self.button1.bind("<Button-1>", self.button1Click)
		#This creates the Output Directory button.
		
		self.outdirname = ""
	
		self.out_optframe = tk.LabelFrame(self.secondframe, height = "1", width= "45", padx = "4", text = "Output Options", background = color)
		self.out_optframe.pack()
		
		# self.ind_out_var = tk.BooleanVar()
		# self.ind_out = tk.Checkbutton(self.out_optframe, text="Individual Item Output", variable=self.ind_out_var,background = color)
		# self.ind_out.pack(side = tk.LEFT)	
		# self.ind_out.deselect()
		# self.var_dict["indout"] = self.ind_out_var
										
		#Creates a label for the second program input (Output Directory)
		self.outputdirlabel = tk.LabelFrame(self.secondframe, height = "1", width= "45", padx = "4", text = "Your selected output filename:", background = color)
		self.outputdirlabel.pack(fill = tk.X)
				
		#Creates a label that informs sure which directory has been chosen
		outdirectoryprompt = "(No Output Filename Chosen)"
		self.outputdirchosen = tk.Label(self.outputdirlabel, height= "1", width= "45", justify=tk.LEFT, padx = "4", anchor = tk.W, font= helv14, text = outdirectoryprompt)
		self.outputdirchosen.pack(side = tk.LEFT)
		
		self.button2 = tk.Button(self.outputdirlabel)
		self.button2["text"]= "Select"
		#This tells the button what to do if clicked.
		self.button2.bind("<Button-1>", self.button2Click)
		self.button2.pack(side = tk.LEFT, padx = 5)

		self.BottomSpace= tk.LabelFrame(self.secondframe, text = "Tag Texts", background = color)
		self.BottomSpace.pack()

		self.button3= tk.Button(self.BottomSpace)
		self.button3["text"] = "Process Texts"
		self.button3.bind("<Button-1>", self.runprogram)
		self.button3.pack()

		self.progresslabelframe = tk.LabelFrame(self.secondframe, text= "Program Status", background = color)
		self.progresslabelframe.pack(expand= tk.TRUE)
		
		self.progress= tk.Label(self.progresslabelframe, height= "1", width= "45", justify=tk.LEFT, padx = "4", anchor = tk.W, font= helv14, text=progress)
		self.progress.pack()
		
		self.poll(self.progress)

	def poll(self, function):
		
		self.myParent.after(10, self.poll, function)
		try:
			function.config(text = dataQueue.get(block=False))
			
		except queue.Empty:
			pass
	
	def instruct_mess(self, event):
		messagebox.showinfo("Instructions", "1. Choose the input folder (where your tag-checked files are)\n\n2. Choose the location where the count file should be written\n\n3. Press the 'Process Texts' button")

	def entry1Return(self,event):
		input= self.entry1.get()
		self.input2 = input + ".csv"
		self.filechosenchosen.config(text = self.input2)
		self.filechosenchosen.update_idletasks()
		
	#Following is an example of how we can update the information from users...
	def button1Click(self, event): #need to double check that this works on Windows.
		#import Tkinter, 
		if sys.version_info[0] == 2: 
			import tkFileDialog
			self.dirname = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Please select a directory')

		if sys.version_info[0] == 3:
			import tkinter.filedialog
			self.dirname = tkinter.filedialog.askdirectory(parent=root,initialdir="/",title='Please select a directory')
		
		self.displayinputtext = '.../'+self.dirname.split('/')[-1]
		self.inputdirchosen.config(text = self.displayinputtext)
		
		#newmsg= "Chosen"
		#self.inputdirchosen.config(text = newmsg)
		#self.inputdirchosen.update_idletasks()

	def button2Click(self, event):
		#self.outdirname = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Please select a directory')
		#if sys.version_info[0] == 2: self.outdirname = tkFileDialog.asksaveasfilename(parent=root, defaultextension = ".csv", initialfile = "results",title='Choose Output Filename')
		#if sys.version_info[0] == 3: self.outdirname = tkinter.filedialog.asksaveasfilename(parent=root, defaultextension = ".csv", initialfile = "results",title='Choose Output Filename')
		self.outdirname = tkinter.filedialog.asksaveasfilename(parent=root, defaultextension = ".tsv", initialfile = "results",title='Choose Output Filename')
		
		#print(self.outdirname)
		if self.outdirname == "":
			self.displayoutputtext = "(No Output Filename Chosen)"
		else: self.displayoutputtext = '.../' + self.outdirname.split('/')[-1]
		self.outputdirchosen.config(text = self.displayoutputtext)

	def runprogram(self, event):
		self.poll(self.progress)
		start_thread(main, self.dirname, self.outdirname, self.var_dict)

		
#### THIS IS BEGINNING OF PROGRAM ###			
def main(indir, outdir, var_dict):
	problem = False
	import tkinter.messagebox
	if indir == "":
		tkinter.messagebox.showinfo("Supply Information", "Choose Input Directory")
		problem = True
	if outdir == "":
		tkinter.messagebox.showinfo("Choose Output Directory", "Choose Output Directory")
		problem = True
	# if var_dict["lang"].get() not in ["english","spanish","korean"]:
	# 	tkinter.messagebox.showinfo("Choose Target Language", "Choose Target Language")
	# 	problem = True


	# print("check1",indir,outdir,var_dict)
	# print("check2", var_dict["lang"].get(),var_dict["indout"].get())
	if problem == False:
		dataQueue.put("Processing your files")
		#add tag lists
		CountDictionary = lxgr.countTagsFolder(indir)
		print(var_dict["norm"].get())
		if var_dict["norm"].get() == 0:
			lxgr.writeCounts(CountDictionary,outdir,normed = False)
		else:
			lxgr.writeCounts(CountDictionary,outdir,norming = var_dict["norm"].get())

		
		finishmessage = ("Your files have been processed")
		dataQueue.put(finishmessage)
		if system == "M":
			messagebox.showinfo("Finished!", "Your files have been tagged by the Lexicogrammatical Tagger.\n\n Now the real work begins!")

if __name__ == '__main__':		
	root = tk.Tk()
	root.wm_title(prog_name)
	root.configure(background = color)
	root.geometry(geom_size)
	myapp = MyApp(root)
	root.mainloop()