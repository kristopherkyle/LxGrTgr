# Lexicogrammatical Tagger (LxGrTgr)
Note that LxGrTgr is currently being beta tested and should not be used in research. Once the beta testing concludes, this message will change.
## Quick Start Guide
LxGrTgr was developed using Spacy (version 3.4; en_core_web_trf model). Users will need to follow the instructions on [Spacy's website](https://spacy.io/usage) to download Spacy for your specific system and the en_core_web_trf model.

Once you have Spacy installed and have dowloaded the en_core_web_trf model, you can use LxGrTgr (in the future you will be able to download this from pypi using pip).

For now, ensure that your Python working directory is the same as the directory in which the LxGrTgr script is.

### Demo site
In addition to using the code below, a <a href="https://kristopherkyle.pythonanywhere.com/" target="_blank">demo web app</a> (which uses a faster but slightly less accurate NLP backend) is also available.

### Import LxGrTgr
First, import LxGrTgr:
```python
import LxGrTgr_05_27 as lxgr
```

### Tag Strings and Print Output 
Then, strings can be tagged and printed:

```python
sample1 = lxgr.tag("This is a very important opportunity that only comes once in a lifetime.")
lxgr.printer(sample1)
```
```
0 This this None pro dem sg None None None None None None DT nsubj 1
1 is be None vbmain be pres simple active None None None None VBZ ROOT 1
2 a a None dt art None None None None None None None DT det 5
3 very very rb+adjmod|advmod rb othr None None None None None None None RB advmod 4
4 important important attr+nn+premod jj attr None None None None None None None JJ amod 5
5 opportunity opportunity None nn None nom None None None None None None NN attr 1
6 that that None relpro relpro_that sg None None None None None None WDT nsubj 8
7 only only rb+advl rb advl ly None None None None None None RB advmod 8
8 comes come nn+finite+relcl vbmain vblex pres simple active nmod_cls thatcls rel None VBZ relcl 5
9 once once rb+advl rb advl None None None None None None None RB advmod 8
10 in in None in in_othr None None None None None None None IN prep 9
11 a a None dt art None None None None None None None DT det 12
12 lifetime lifetime None nn None None None None None None None None NN pobj 10
13 . . None None None None None None None None None None . punct 1
```

These commands can also be combined for efficiency's sake:
```python
lxgr.printer(lxgr.tag("This is a very important opportunity that only comes once in a lifetime."))
```

### Write Output to File
Output can also be written to a file:
```python
lxgr.writer("sample_results/sample1.tsv",sample1)
sample2 = lxgr.tag("I like pizza. I also enjoy eating it because it gives me a reason to drink beer.")
lxgr.writer("sample_results/sample2.tsv",sample2)
```
## Batch Processing Corpora
Corpora come in all shapes and sizes. By default LxGrTgr presumes that each corpus file is represented as a UTF-8 text file and that all corpus files are in the same folder/directory. 

### Step 1: Tag Corpus Files
To tag a corpus with LxGrTgr, simply use the `tagFolder()` function.

`tagFolder(targetDir,outputDir,suff = ".txt")`

`targetDir` is the folder/directory where your corpus files are. `outputDir` is the folder where the tagged versions of your corpus files will be written.

An additional optional argument (`suff`) can also be used. By default, `suff = ".txt"`. If your corpus filenames end in something other than ".txt", be sure to include the `suff` argument with the correct filename ending. 

```
lxgr.tagFolder("folderWithCorpusFiles/","folderWhereTaggedVersionsWillBeWritten/")
```
### Step 2: Check and Edit Tagged Corpus Files
Next, tagging should be checked and edited as appropriate.

### Step 3: Counting Tags
After checking and editing the tags in your corpus, it is time to get tag counts for each document in your corpus using the `countTagsFolder()` function.
```
countTagsFolder(targetDir,tagList = None,suff = ".txt")
```
By default, complexity tags are counted. The `countTagsFolder()` function returns a dictionary with filenames as keys and feature counts as values.

```
sampleCountDictionary = lxgr.countTagsFolder("folderWhereTaggedVersionsWereWritten/")
```
### Step 4: Writing Tag Counts to a File
The `writeCounts()` function can be used to write the results to a file. By default, counts are normed as the incidence per 10,000 words, though this can be changed using the `norming` argument. Raw counts can be obtained by including `normed = False`.

`writeCounts(outputD,outName, tagList = None, sep = "\t", normed = True,norming = 10000)`

If the default options are desired, the `writeCounts()` function only needs two arguments - a dictionary of filenames and index counts and a filename for the spreadsheet file:

```
lxgr.writeCounts(sampleCountDictionary,"sampleOutputFile.txt")
```


## Future Directions
Add more functions for random sampling and tag-fixing.

## Tag Descriptions
We are currently developing tag descriptions and detailed annotation guidelines for complexity features. <a href="https://lcr-ads-lab.github.io/LxGrTagger-Documentation/" target="_blank">Click here to access the document</a> (updated/revised weekly)

## License
<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.