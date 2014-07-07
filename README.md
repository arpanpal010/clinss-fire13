clinss-fire13
=============

Entry for [CL!NSS](http://users.dsic.upv.es/grupos/nle/clinss.html) task at [FIRE'13] (http://pan.webis.de/): Set-based Similarity Measurement and Ranking Model to Identify Cases of Journalistic Text Reuse.

Description
-----------
In our approach, we first convert the english text to phonetic hindi with Google Translate, and extract four word-groups from the text, namely the title, content, unique words in content and frequent words in the document. These four groups, along with their publication dates, are compared with each document in the hindi corpus and a weighted combination of these five individual similarity scores determines an overall amount of similarity between the english text and hindi text. The documents are ranked according to their final score, and a relevnce chart is prepared (qrel file) that can be checked with the provided perl script to check the accuracy of the system. 

Our shortpaper for the entry can be found [here](https://github.com/arpanpal010/clinss-fire13/blob/master/2013-clinss-Pal-Surrey.pdf?raw=true).

Please have a look at `config.py` before running any files. The corpus and testing texts are not included here, and can only be obtained from the [CL!NSS website] (http://users.dsic.upv.es/grupos/nle/clinss.html). Below is the folders hierarchy of the project, I like to keep all the documents in a single directory called `documents` and separate directories for training and testing, so this is my default configuration, if the folder structure changes, the relevant file locations in the config file (`config.py`), should be updated according to that.
```
(basedir)clinss-fire13/
    documents/
  	|	source-hindi/
  	|		//hindi-document-00001.txt...
  	|	testing/
  	|	|	results/ (dirs in here are auto created but this one still needs to be done manually)
  	|	|	|	datepassed/
  	|	|	|	detscore/
  	|	|	|	fqpassed/
  	|	|	|	prepscore/
  	|	|	|	titlepassed/
  	|	|	|	uqpassed/
  	|	|	|	wordpassed/
  	|	|	target-hindi/
  	|	|	|	//english-document-00001.txt... (translated hindi)
  	|	|	target-english/
  	|	|	|	//english-document-00001.txt... (originals)
  	|	training/
  	|	|	results/ (dirs in here are auto created but this one still needs to be done manually)
  	|	|	|	datepassed/
  	|	|	|	detscore/
  	|	|	|	fqpassed/
  	|	|	|	prepscore/
  	|	|	|	titlepassed/
  	|	|	|	uqpassed/
  	|	|	|	wordpassed/
  	|	|	target-hindi/
  	|	|	|	//english-document-00001.txt... (translated hindi)
  	|	|	target-english/
  	|	|	|	//english-document-00001.txt... (originals)
  	evaluation/
  	|	clinss12-en-hi.qrel
  	|	clinss12-eval.pl
  	|	clinss13.eval.pl
  	|	clinss13-en-hi.qrel
  	|	run-1-english-hindi-APal.txt
  	|	run-2-english-hindi-APal.txt
  	|	run-3-english-hindi-APal.txt
  	|	runcheck.sh
  	2013-clinss-Pal-Surrey.pdf
  	clinss-fire13.py.py
  	config.py
  	stopwords-hindi.txt
  	LICENSE
	README.md
```
