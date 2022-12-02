# Lexicogrammatical Tagger (LxGrTgr)

## Quick Start Guide
LxGrTgr was developed using Spacy (version 3.4; en_core_web_trf model). Users will need to follow the instructions on [Spacy's website](https://spacy.io/usage) to download Spacy for your specific system and the en_core_web_trf model.

Once you have Spacy installed and have dowloaded the en_core_web_trf model, you can use LxGrTgr (in the future you will be able to download this from pypi using pip).

For now, ensure that your Python working directory is the same as the directory in which the LxGrTgr script is. 

### Import LxGrTgr
First, import LxGrTgr:
```python
import LxGrTgr_01 as lxgr
```

### Tag Strings and Print Output 
Then, strings can be tagged and printed:

```python
sample1 = lxgr.tag("This is a very important opportunity that only comes once in a lifetime.")
lxgr.printer(sample1)
```
```
0 This this pro dem sg None None None None None None DT PRON nsubj 1
1 is be vbmain be pres simple active None None None None VBZ AUX ROOT 1
2 a a dt art None None None None None None None DT DET det 5
3 very very rb othr None None None None None None None RB ADV advmod 4
4 important important jj attr None None None None None None None JJ ADJ amod 5
5 opportunity opportunity nn None nom None None None None None None NN NOUN attr 1
6 that that relpro relpro_that sg None None None None None None WDT PRON nsubj 8
7 only only rb advl ly None None None None None None RB ADV advmod 8
8 comes come vbmain vblex pres simple active nmod_cls thatcls None None VBZ VERB relcl 5
9 once once rb advl None None None None None None None RB ADV advmod 8
10 in in in in_othr None None None None None None None IN ADP prep 9
11 a a dt art None None None None None None None DT DET det 12
12 lifetime lifetime nn None None None None None None None None NN NOUN pobj 10
13 . . None None None None None None None None None . PUNCT punct 1
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

## Future Directions
insert things here

## Tag Descriptions
insert things here

## License
<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.