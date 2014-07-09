clinss-fire13
=============

Entry for [CL!NSS](http://users.dsic.upv.es/grupos/nle/clinss.html) task at [FIRE'13] (http://pan.webis.de/): Set-based Similarity Measurement and Ranking Model to Identify Cases of Journalistic Text Reuse.

Description
-----------
In our approach, we first convert the english text to hindi with Google Translate, and extract four word-groups from the text, namely the **title**, **content**, **unique words** in content and **frequent words** in the document. These four groups, along with their **publication dates**, are compared with each document in the hindi corpus and a weighted combination of these five individual similarity scores determines an overall amount of similarity between the english text and hindi text. The documents are ranked according to their final score, and a relevance table is prepared that can be checked with the provided perl script and qrel file to check the accuracy of the system.

We scored *NDCG@1 - 0.6600*, *NDCG@5 - 0.5579*, *NDCG@10 - 0.5604*. 

So there's definite room for improvement, but this system is made mainly to be merely a filtration process to determine a list of potential candidates that can be checked by more resource heavy processes. Our paper for the entry can be found [here](https://github.com/arpanpal010/clinss-fire13/blob/master/2013-clinss-Pal-Surrey.pdf?raw=true).

Documents
---------
Please note that the corpus and testing texts are not included here, and can only be obtained from the [CL!NSS] (http://users.dsic.upv.es/grupos/nle/clinss.html) website. Below is the folder hierarchy of the project, I like to keep all the documents in a single directory called **documents** and separate directories for training and testing, so this is my default configuration, if the folder structure changes, the relevant file locations in the config file (**config.py**), should be updated accordingly.

```
(basedir)clinss-fire13/
    documents/
  	|	source-hindi/
  	|	|	//hindi-document-00001.txt...
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

Configuration
--------------
After getting documents from the [CLINSS](http://users.dsic.upv.es/grupos/nle/clinss.html) website and the translations from any translator service that does english-to-hindi, please have a look at `config.py` first before running any files. The basic configuration needed are..

`mode` = _"training"_ or _"testing"_

`testlist` = _['date', 'title', 'word', 'uq', 'fq']_  
(The tests that are to be done when batch processing. default=all).

`datethreshold` = _8_  
(If the source document is published within the threshold window (in days), it is considered a candidate)

`titlethreshold` = _0.01_  
(If the title of the source document compared with the title of the target document, has similarity score greater than the threshold value, it is considered a candidate)

`wordthreshold` = _0.05_  
(If the content of the source document compared with the content of the target document, has similarity score greater than the threshold value, it is considered a candidate)

`uqthreshold` = _1_  
(The most number of ocurance of a word to make it a unique word in the document. Words with higher frequency are discarded.)

`uqcheckthreshold` = _0.02_  
(If the unique content of the source document compared with the unique content of the target document, has similarity score greater than the threshold value, it is considered a candidate)

`fqthreshold` = _20_  
(The number of most frequent words to consider. The words with frequency=1 are discarded)

`fqcheckthreshold` = _0.02_  
(If the unique content of the source document compared with the unique content of the target document, has similarity score greater than the threshold value, it is considered a candidate)

`datehit` = _2.0_  
(Score considered when the source document has passed the publication date check.)

`datemiss` = _1.0_  
(Score considered when the source document has failed the publication date check.)

`considerdocsthreshold` = _50_  
(The number of documents considered when generating runs, 50 is the maximum considered by the evaluation perlscript.)

The values set here are just default values to start the system, you may need to tweak them for some time to get the setting that works best. Check out the other configuration option to fine tune the system. You can also create your own, and if that works out for the better, don't hesitate to send me a pull request.
