#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os, sys
#configuration file for clinss-fire13.py

#---------------------------------------------
#parameters
#---------------------------------------------
global mode
mode="testing" #training / testing

global testlist #in case of batch processing, which tests to do
testlist=['date', 'title', 'word', 'uq', 'fq']

#threshold values (applied when scoring to filter docs above threshold, not when computing similarity, i.e check once and reuse)
global datethreshold
datethreshold=8 #maximum window (days) to consider if published news is relevant to target

global titlethreshold
titlethreshold=0.0 #0.0 #0.06 #amount of common words in titles #using Jaccard

global wordthreshold
wordthreshold=0.05#0.05 #0.11 #amount ratio of common words in content #using Jaccard

global uqthreshold
uqthreshold=1 #how many occurences in doc to consider a word unique

global uqcheckthreshold
uqcheckthreshold=0.01#0.01 #minimum score to consider a hit #using Jaccard

global fqthreshold
fqthreshold=20 #how many most freqent words to consider

global fqcheckthreshold
fqcheckthreshold=0.02#0.02 #minimum score to consider a hit #using Jaccard

#default score values when running prepscore()
global datehit
datehit=2.0

global datemiss
datemiss=1.0

#global titlemiss
#titlemiss=0.05

#global wordmiss
#wordmiss=0.05

#global uqmiss
#uqmiss=0.01

#global fqmiss
#fqmiss=0.01
	
#detailed
global considerdocsthreshold
considerdocsthreshold=50 #25 #100 #number of docs to be processed in phase2 #max 50 bcoz NDCG considers max 50 lines

#global qrelthreshold
#qrelthreshold=25 #number of docs to be considered when generating the run file

#---------------------------------------------
#directories
#---------------------------------------------
global basedir
basedir= "/home/arch/scrap/clinss-fire13" #main project dir, all files will be read, written in here

global documentsroot
documentsroot=os.path.join(basedir, "documents") #all documents are kept here
#dir for the runs
global rundir
rundir=os.path.join(basedir, "evaluation") #run files (qrel-formatted .txt) generated in this folder

global stopwords
stopwords=os.path.join(basedir, "stopwords-hindi.txt") #list of hindi stopwords from "http://members.unine.ch/jacques.savoy/clef/hindiST.txt"

global sourcedir
global targetdir
global transcache
global resultsdir

#training/testing
if mode=="training":
	#training folders
	sourcedir= os.path.join(documentsroot, "source-hindi") #dir to keep the hindi corpus in
	targetdir=os.path.join(documentsroot, "training", "target-english") #location of target files in english e.g /documents/english-test
	transcache=os.path.join(documentsroot, "training", "target-hindi") #location of translated target files in hindi
	resultsdir=os.path.join(documentsroot, "training", "results") #results go in this folder
elif mode=="testing":
	#testing folders
	sourcedir= os.path.join(documentsroot, "source-hindi") #dir to keep the hindi corpus in
	targetdir=os.path.join(documentsroot, "testing", "target-english") #location of target files in english
	transcache=os.path.join(documentsroot, "testing", "target-hindi") #location of translated target files in hindi		
	resultsdir=os.path.join(documentsroot, "testing", "results") #results go in this folder
else:		
	print "Invalid mode. Exiting..."
	sys.exit(0)

#similartiy check dirs
global datedir
global titledir
global worddir
global uqdir
global fqdir

#dir for combining results
global prepscoredir
global detscoredir

#only after initing resultdir can these be set #no need to check exist coz auto-create
datedir=os.path.join(resultsdir, "datepassed") #datechecker() passed items are written here under their compared-target-filenames
titledir=os.path.join(resultsdir, "titlepassed") #titlechecker()
worddir=os.path.join(resultsdir, "wordpassed") #wordchecker()
uqdir=os.path.join(resultsdir, "uqpassed")#uqcheck()
fqdir=os.path.join(resultsdir, "fqpassed") #fqcheck()
prepscoredir=os.path.join(resultsdir, "prepscore") #after each test, scores of items are written here under their test-dir/compared-target-filenames e.g datedir/english-document-0001.txt contains all the source filenames that passed the test against english-document-0001.txt
detscoredir=os.path.join(resultsdir, "detscore") #final scores of items are written here under their compared-target-filenames

def selfcheck(): #check and print if all files exist else exit
	#checkfiles
	files_required=basedir, stopwords, sourcedir, targetdir, transcache, resultsdir, rundir  #dirs/files required before processing starts others are created when running
	fl=False
	for item in files_required:
		if os.path.exists(item):
			#print "Found", item
			pass #quiet
		else:
			print "Cannot find", item
			fl=True
	if fl:
		print "\nCannot run without files/dirs in proper place.\nPlease recheck directory structure in config.py"
		sys.exit(0)
	return True
