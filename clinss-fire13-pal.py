#!/usr/bin/python
# -*- coding: UTF-8 -*-

#Set-based Similarity Measurement and Ranking Model to Identify Cases of Journalistic Text Reuse.
#Entry for CL!NSS task at FIRE'13.

#Description:
#In our approach, we first convert the english text to phonetic hindi with Google Translate, and extract four word-groups from the text, 
#namely the title, content, unique words in content and frequent words in the document. These four groups, along with their publication dates, 
#are compared with each document in the hindi corpus and a weighted combination of these five individual similarity scores determines an overall
#amount of similarity between the english text and hindi text. The documents are ranked according to their final score, and a relevnce chart is
#prepared (qrel file) that can be checked with the provided perl script to check the accuracy of the system.

#Final score: NDCG@1 : 0.6600, NDCG@5 : 0.5579, NDCG@10 : 0.5604

import config
import os, re, math, datetime, time
from collections import Counter

#-----------------------------------------------------------------------
#configuration
#-----------------------------------------------------------------------
if __name__=="__main__": #define and assign variables
	
	#configurations moved to config.py
	print "config.py OK" if config.selfcheck() else ""
	#gather and sort doclists
	targetlist=os.listdir(config.targetdir) #english documents in hindi
	transtarlist=os.listdir(config.transcache)#translated targetlist
	sourcelist=os.listdir(config.sourcedir)#hindi documents
	targetlist.sort() #4understanding
	transtarlist.sort()
	sourcelist.sort()

#-----------------------------------------------------------------------
#functions
#-----------------------------------------------------------------------

def filetocontent(docpath): #takes path and returns list of stripped content strings 0=title, 1=date, 2=content
	#print docpath
	file=open(docpath, 'rb')
	doctext=file.read() #.decode("utf-8")
	file.close()
	#stripping each tag data to string
	doctitle=''.join(re.findall(r"<title>(.+)</title>",doctext))
	docdate=''.join(re.findall(r"<date>(.+)</date>",doctext))
	#doccontent=''.join(re.findall(r"<content>(.+)</content>",doctext)) #doesn't work...WHY?
	doccontent=doctext.replace('<story>', '').replace('</story>', '').replace("<title>", '').replace("</title>", '').replace("<date>", '').replace("</date>", '').replace("<content>", '').replace("</content>", '').replace(doctitle, '').replace(docdate, '')
	#print docdate, doctitle, doccontent #4debug
	return doctitle, docdate, doccontent

def datediff(tardatestring, srcdatestring): #calculates date difference
	date_format="%d-%m-%Y"
	tardate=datetime.datetime.strptime(tardatestring, date_format).date()
	srcdate=datetime.datetime.strptime(srcdatestring, date_format).date()
	return abs((tardate-srcdate).days)

def wordify(doccontent): #word extractor
	content=''
	stoppers=['.', '?', '!', ',', ';', ':', '\n', '\"']
	for char in doccontent: #removing stop characters
		if char in stoppers:
			char=' '
		content+=(char)
	wordlist=content.split(' ')
	
	file=open(config.stopwords, 'rb')
	stopwordslist=file.read().split("\n")
	file.close()
	
	for word in wordlist: #removing stopwords
		if word in stopwordslist:
			wordlist.remove(word)
	while '' in wordlist: #removing blanks
		wordlist.remove('')
	return wordlist

def getuqwords(docpath='', wordlist=''): #return list of words which have the freqency less than uqthreshold - unique words - uniquely identifies document
	if docpath: contentwords=Counter(wordify(filetocontent(docpath)[2]))
	if wordlist: contentwords=Counter(wordlist)
	uqlist=[]
	for word in contentwords:
		if contentwords[word] <=config.uqthreshold:
			uqlist.append(word)
	return uqlist

def getfqwords(docpath='', wordlist=''): #return list of most frequent words - subjective words
	if docpath: contentwords=Counter(wordify(filetocontent(docpath)[2]))
	if wordlist: contentwords=Counter(wordlist)
	#print contentwords
	fqlist=[]
	maxfreqwords=contentwords.most_common(config.fqthreshold) #[0][1] #getting the max frequency of word in doc
	#print maxfreqwords
	for word in maxfreqwords:
		if contentwords[word[0]]>=2:  #discarding words which only occur once
			fqlist.append(word[0])
	return fqlist

def gettopdocs(tardoc, resdir): #returns a list of top possible candidates from prepscores/, list length = considerdocsthreshold
	file=open(os.path.join(config.resultsdir, resdir, tardoc), 'rb') #default resdir="prepscore/"
	doclist=file.read().split("\n")
	file.close()
	while '' in doclist:
		doclist.remove('')
	if len(doclist) < config.considerdocsthreshold:
		return doclist
	else:
		return doclist[0:config.considerdocsthreshold]

def setsim(tarwordlist, srcwordlist): #set based similarity measure
	#tarwords=wordify(tarstring)
	#srcwords=wordify(srcstring)
	commonwords=len(list(set(tarwordlist) & set(srcwordlist)))
	totalwords=len(list(set(tarwordlist) | set(srcwordlist)))
	return [commonwords, len(tarwordlist), len(srcwordlist), totalwords]

#-----------------------------------------------------------------------
#similarity checks
#-----------------------------------------------------------------------

def datechecker(): #generates list of srcdocs that have the date below date threshold in resultsdir/datepassed/
	if not os.path.exists(config.datedir): #auto-create if not exists
		os.makedirs(config.datedir)
	for tardoc in targetlist:
		doclist=[]
		string=''
		tardate=filetocontent(os.path.join(config.targetdir, tardoc))[1] #read date from target
		for srcpath in sourcelist: #read date from source files and compare with target, add to doclist if published after/around target publication (value under threshold) 
			print "Checking Pub-Dates "+tardoc+" against "+srcpath
			srcdate=filetocontent(os.path.join(config.sourcedir, srcpath))[1]
			diff=datediff(tardate, srcdate)
			#if diff <= datethreshold:
			doclist.append([diff, srcpath])
		doclist.sort()
		for doc in doclist:
			string+=str(doc[0])+","+doc[1]+"\n"
		file=open(os.path.join(config.datedir, tardoc), 'wb')
		file.write(string)
		file.close()
	
def titlechecker(): #get title, split words, if len(common words)>threshold then write in resultsdir/titlepassed/ [no folder auto create] 
	if not os.path.exists(config.titledir): #auto-create if not exists
		os.makedirs(config.titledir)
	for tardoc in targetlist:
		scorelist=[]
		string=''
		tartitle=filetocontent(os.path.join(config.transcache, tardoc))[0] #titles in hindi from transcache
		tartitlewords=wordify(tartitle) #tartitle.split(" ")

		for srcpath in sourcelist:#datepasseddocs:
			print "Checking Titles "+tardoc+" against "+srcpath
			srctitle=filetocontent(os.path.join(config.sourcedir, srcpath))[0]
			srctitlewords=wordify(srctitle)
			commonwords=len(list(set(tartitlewords) & set(srctitlewords)))
			totalwords=len(list(set(tartitlewords) | set(srctitlewords)))
			scorelist.append([commonwords, len(tartitlewords), len(srctitlewords), totalwords, srcpath])
		
		scorelist.sort(reverse=True)
		for score in scorelist: #preparing the result in a single string
			#string+=str(score[0])+','+str(score[1])+','+str(score[2])+','+score[3]+"\n" #last element is doc no.
			string+=str(score[0])+','+str(score[1])+','+str(score[2])+','+str(score[3])+','+score[4]+"\n"
		
		#writing file
		file=open(os.path.join(config.titledir, tardoc), 'wb')
		file.write(string)
		file.close()

def wordchecker(): #get content, split words, if len(common words)>threshold then write in resultsdir/wordpassed/ [no folder auto create] 
	if not os.path.exists(config.worddir): #auto-create if not exists
		os.makedirs(config.worddir)
	for tardoc in targetlist:
		scorelist=[]
		string=''
		tarcontent=filetocontent(os.path.join(config.transcache, tardoc))[2] #titles in hindi from transcache
		tarcontentwords=wordify(tarcontent)
		
		for srcpath in sourcelist:#datepasseddocs:
			print "Checking Content "+tardoc+" against "+srcpath
			srccontent=filetocontent(os.path.join(config.sourcedir, srcpath))[2]
			srccontentwords=wordify(srccontent)
			commonwords=len(list(set(tarcontentwords) & set(srccontentwords)))
			totalwords=len(list(set(tarcontentwords) | set(srccontentwords)))
			#commonpart=(float(commonwords)/len(tarcontentwords))
			#if commonwords >= commonwordthreshold:
			scorelist.append([commonwords, len(tarcontentwords), len(srccontentwords), totalwords, srcpath])
		
		scorelist.sort(reverse=True)
		for score in scorelist:
			string+=str(score[0])+','+str(score[1])+','+str(score[2])+','+str(score[3])+','+score[4]+"\n"
		
		file=open(os.path.join(config.worddir, tardoc), 'wb')
		file.write(string)
		file.close()

def checkuqwords():
	if not os.path.exists(config.uqdir): #auto-create if not exists
		os.makedirs(config.uqdir)
	for tardoc in targetlist:
		scorelist=[]
		string=''
		taruq=getuqwords(docpath=os.path.join(config.transcache, tardoc))
		#srclist=gettopdocs(tardoc, "prepscore/")
	
		for srcpath in sourcelist:#sourcelist:#datepasseddocs:
			#srcpath=line.split('=')[1].replace('\n', '')
			print "Checking UQContent "+tardoc+" against "+srcpath
			srcuq=getuqwords(docpath=os.path.join(config.sourcedir, srcpath))
			commonwords=len(list(set(taruq) & set(srcuq)))
			totalwords=len(list(set(taruq) | set(srcuq)))
			scorelist.append([commonwords, len(taruq), len(srcuq), totalwords, srcpath])

		scorelist.sort(reverse=True)
		#scorelist.sort(key=operator.itemgetter(0), reverse=True)
		for score in scorelist:
			string+=str(score[0])+','+str(score[1])+','+str(score[2])+','+str(score[3])+','+score[4]+"\n"

		file=open(os.path.join(config.uqdir, tardoc), 'wb')
		file.write(string)
		file.close()

def checkfqwords():
	if not os.path.exists(config.fqdir): #auto-create if not exists
		os.makedirs(config.fqdir)
	for tardoc in targetlist:
		scorelist=[]
		string=''
		tarfq=getfqwords(docpath=os.path.join(config.transcache, tardoc))
		#srclist=gettopdocs(tardoc, "prepscore/")
	
		for srcpath in sourcelist:#sourcelist:#datepasseddocs:
			#srcpath=line.split('=')[1].replace('\n', '')
			print "Checking FQContent "+tardoc+" against "+srcpath
			srcfq=getfqwords(docpath=os.path.join(config.sourcedir, srcpath))
			commonwords=len(list(set(tarfq) & set(srcfq)))
			totalwords=len(list(set(tarfq) | set(srcfq)))
			scorelist.append([commonwords, len(tarfq), len(srcfq), totalwords, srcpath])

		scorelist.sort(reverse=True)
		for score in scorelist:
			string+=str(score[0])+','+str(score[1])+','+str(score[2])+','+str(score[3])+','+score[4]+"\n"

		file=open(os.path.join(config.fqdir, tardoc), 'wb')
		file.write(string)
		file.close()

def batch_process_tests(tardoclist=transtarlist, srcdoclist=sourcelist):
	print "batch processing documents..."
	for tardoc in tardoclist: #targetlist:
		datelist=[]
		titlelist=[]
		wordlist=[]
		uqlist=[]
		fqlist=[]
		
		#preprocess tardoc
		tartitle, tardate, tarcontent=filetocontent(os.path.join(config.transcache, tardoc))
		
		tartitlewords=wordify(tartitle)
		tarcontentwords=wordify(tarcontent)
		taruqwords=getuqwords(wordlist=tarcontentwords)
		tarfqwords=getfqwords(wordlist=tarcontentwords)
		#print tartitle, tardate, tarcontent
				
		for srcdoc in srcdoclist:
			print "CHECKING: D/T/W/U/F - "+tardoc+" vs "+srcdoc
			
			#preprocess srcdoc
			srctitle, srcdate, srccontent=filetocontent(os.path.join(config.sourcedir, srcdoc))
		
			srctitlewords=wordify(srctitle)
			srccontentwords=wordify(srccontent)
			srcuqwords=getuqwords(wordlist=srccontentwords)
			srcfqwords=getfqwords(wordlist=srccontentwords)
			
			if 'date' in config.testlist:
				#datecheck
				#print "DATECHECK: "+tardoc+" vs "+srcdoc
				diff=datediff(tardate, srcdate)
				datelist.append([diff, srcdoc])
				#print [diff, srcdoc]
			
			if 'title' in config.testlist:
				#titlecheck
				#print "TITLECHECK: "+tardoc+" vs "+srcdoc
				tcommonwords, ttarwords, tsrcwords, ttotalwords=setsim(tartitlewords, srctitlewords)
				titlelist.append([tcommonwords, ttarwords, tsrcwords, ttotalwords, srcdoc])
				#print [commonwords, tarwords, srcwords, totalwords, srcdoc]
			
			if 'word' in config.testlist:
				#wordcheck
				#print "WORDCHECK: "+tardoc+" vs "+srcdoc
				wcommonwords, wtarwords, wsrcwords, wtotalwords=setsim(tarcontentwords, srccontentwords)
				wordlist.append([wcommonwords, wtarwords, wsrcwords, wtotalwords, srcdoc])
				#print [commonwords, tarwords, srcwords, totalwords, srcdoc]
				
			if 'uq' in config.testlist:
				#uqcheck
				#print "UQCHECK: "+tardoc+" vs "+srcdoc
				ucommonwords, utarwords, usrcwords, utotalwords=setsim(taruqwords, srcuqwords)
				uqlist.append([ucommonwords, utarwords, usrcwords, utotalwords, srcdoc])
				#print [commonwords, tarwords, srcwords, totalwords, srcdoc]
			
			if 'fq' in config.testlist:
				#fqcheck
				#print "FQCHECK: "+tardoc+" vs "+srcdoc
				fcommonwords, ftarwords, fsrcwords, ftotalwords=setsim(tarfqwords, srcfqwords)
				fqlist.append([fcommonwords, ftarwords, fsrcwords, ftotalwords, srcdoc])
				#print [commonwords, tarwords, srcwords, totalwords, srcdoc]
		
		#writing results
		if 'date' in config.testlist:
			if not os.path.exists(config.datedir): #auto-create if not exists
				os.makedirs(config.datedir)
			string=''
			datelist.sort()
			for datedoc in datelist:
				string+=str(datedoc[0])+","+datedoc[1]+"\n"
			file=open(os.path.join(config.datedir, tardoc), 'wb')
			file.write(string)
			file.close()
		
		if 'title' in config.testlist:
			if not os.path.exists(config.titledir): #auto-create if not exists
				os.makedirs(config.titledir)			
			string=''
			titlelist.sort(reverse=True)
			for titledoc in titlelist:
				string+=str(titledoc[0])+","+str(titledoc[1])+","+str(titledoc[2])+","+str(titledoc[3])+","+titledoc[4]+"\n"
			file=open(os.path.join(config.titledir, tardoc), 'wb')
			file.write(string)
			file.close()
		
		if 'word' in config.testlist:
			if not os.path.exists(config.worddir): #auto-create if not exists
				os.makedirs(config.worddir)	
			string=''
			wordlist.sort(reverse=True)
			for worddoc in wordlist:
				string+=str(worddoc[0])+","+str(worddoc[1])+","+str(worddoc[2])+","+str(worddoc[3])+","+worddoc[4]+"\n"
			file=open(os.path.join(config.worddir, tardoc), 'wb')
			file.write(string)
			file.close()
		
		if 'uq' in config.testlist:
			if not os.path.exists(config.uqdir): #auto-create if not exists
				os.makedirs(config.uqdir)	
			string=''
			uqlist.sort(reverse=True)
			for uqdoc in uqlist:
				string+=str(uqdoc[0])+","+str(uqdoc[1])+","+str(uqdoc[2])+","+str(uqdoc[3])+","+uqdoc[4]+"\n"
			file=open(os.path.join(config.uqdir, tardoc), 'wb')
			file.write(string)
			file.close()
		
		if 'fq' in config.testlist:
			if not os.path.exists(config.fqdir): #auto-create if not exists
				os.makedirs(config.fqdir)	
			string=''
			fqlist.sort(reverse=True)
			for fqdoc in fqlist:
				string+=str(fqdoc[0])+","+str(fqdoc[1])+","+str(fqdoc[2])+","+str(fqdoc[3])+","+fqdoc[4]+"\n"
			file=open(os.path.join(config.fqdir, tardoc), 'wb')
			file.write(string)
			file.close()	

#-----------------------------------------------------------------------
#scoring and generating op
#-----------------------------------------------------------------------

def prepscore(): #read datecheck, titlecheck and wordcheck op, for each doc in wordcheck if exists in titlecheck, wordscore * titlescore else wordscore 
	if not os.path.exists(config.prepscoredir): #auto-create if not exists
		os.makedirs(config.prepscoredir)	
	print "Computing Prep scores..."
	for tardoc in targetlist:
		print "Computing Prep scores for "+tardoc
		datedoclist=[] #lists to contain the scores and doclists per test
		datescorelist=[]
		
		titledoclist=[]
		titlescorelist=[]
		
		worddoclist=[]
		wordscorelist=[]
		
		uqdoclist=[]
		uqscorelist=[]
		
		fqdoclist=[]
		fqscorelist=[]
		
		totaldoclist=[]
		scorelist=[]
		
		string='' #to write results
		
		#datecheck
		file=open(os.path.join(config.datedir, tardoc), 'rb') #reading list of files published under datethreshold
		datepasseddocs=file.readlines()
		file.close()
		
		if datepasseddocs != '':
			for line in datepasseddocs:
				score, doc= line.split(',')
				if int(score) <=config.datethreshold:
					datedoclist.append(doc)
					datescorelist.append(int(score))
		
		#titlecheck
		file=open(os.path.join(config.titledir, tardoc), 'rb') #reading list of files that have a title similarity score > 0
		titlepasseddocs=file.readlines()
		file.close()
		
		if titlepasseddocs != '':
			for line in titlepasseddocs:
				commonwords, titlewords, srcwords, totalwords, doc= line.split(',')
				score=float(commonwords)/float(totalwords)
				#score=2.0*float(commonwords)/(float(titlewords)+float(srcwords)) #Dice
				if score >= config.titlethreshold:
					titledoclist.append(doc)
					titlescorelist.append(score)
		
		#wordcheck
		file=open(os.path.join(config.worddir, tardoc), 'rb') #reading list of files that have a common word score > 0
		wordpasseddocs=file.readlines()
		file.close()
		
		if wordpasseddocs != '':
			for line in wordpasseddocs:
				commonwords, titlewords, srcwords, totalwords, doc= line.split(',')
				score=float(commonwords)/float(totalwords) #Jaccard=aNb/aUb
				#score=2.0*float(commonwords)/(float(titlewords)+float(srcwords)) #Dice=2*aNb/a+b
				if score >= config.wordthreshold:
					worddoclist.append(doc)
					wordscorelist.append(score)
		
		#uqcheck
		file=open(os.path.join(config.uqdir, tardoc), 'rb') #reading list of files that have a unique common word score > 0
		uqpasseddocs=file.readlines()
		file.close()
		
		if uqpasseddocs != '':
			for line in uqpasseddocs:
				commonwords, titlewords, srcwords, totalwords, doc= line.split(',')
				score=float(commonwords)/float(totalwords) #Jaccard=aNb/aUb
				#score=2.0*float(commonwords)/(float(titlewords)+float(srcwords)) #Dice=2*aNb/a+b
				if score >= config.uqcheckthreshold:
					uqdoclist.append(doc)
					uqscorelist.append(score)
		
		#fqcheck
		file=open(os.path.join(config.fqdir, tardoc), 'rb') #reading list of files that have a frequent common word score > 0
		fqpasseddocs=file.readlines()
		file.close()
		
		if fqpasseddocs != '':
			for line in fqpasseddocs:
				commonwords, titlewords, srcwords, totalwords, doc= line.split(',')
				score=float(commonwords)/float(totalwords) #Jaccard=aNb/aUb
				#score=2.0*float(commonwords)/(float(titlewords)+float(srcwords)) #Dice=2*aNb/a+b
				if score >= config.fqcheckthreshold:
					fqdoclist.append(doc)
					fqscorelist.append(score)
		
		#combining the scores
		#totaldoclist=list(set(datedoclist) | set(titledoclist) | set(worddoclist) | set(uqdoclist) | set(fqdoclist))
		totaldoclist=list(set(titledoclist) & set(worddoclist) & set(uqdoclist) & set(fqdoclist))
		#totaldoclist=list((set(titledoclist) | set(worddoclist)) & (set(uqdoclist) | set(fqdoclist)))
		
		for line in totaldoclist:
			if line in datedoclist:
				datescore= config.datehit #+float(1)/(int(datescorelist[datedoclist.index(line)])+0.999999) #datehit
			else:					#tweaks
				datescore= config.datemiss
			if line in titledoclist:
				titlescore= float(titlescorelist[titledoclist.index(line)])
			#else:					#tweaks
			#	titlescore=config.titlemiss
			if line in worddoclist:
				wordscore= float(wordscorelist[worddoclist.index(line)])
			#else:					#tweaks
			#	wordscore=config.wordmiss
			if line in uqdoclist:
				uqscore= float(uqscorelist[uqdoclist.index(line)])
			#else:					#tweaks
			#	uqscore=config.uqmiss
			if line in fqdoclist:
				fqscore= float(fqscorelist[fqdoclist.index(line)])
			#else:					#tweaks
			#	fqscore=config.fqmiss
			
			#twscore=titlescore+wordscore
			#ufscore=uqscore+fqscore
			#score=(titlescore+wordscore+datescore+uqscore+fqscore)/len(totaldoclist) # multiplied for normalizing the values
			score=(titlescore*0.16+wordscore*0.25+datescore*0.04+uqscore*0.24+fqscore*0.31)/len(totaldoclist)*10 # multiplied by their own accuracy@50 to get weighted average
			if score>0.0:
				#scorelist.append([score,line])
				scorelist.append([score, titlescore, wordscore, uqscore, fqscore, datescore, line])
				
		scorelist.sort(reverse=True)
		for score in scorelist:
			#string+=str(score[0])+'='+score[1] #+"\n"
			string+=str(score[0])+","+str(score[1])+","+str(score[2])+","+str(score[3])+","+str(score[4])+","+str(score[5])+","+score[6] #+"\n"
		
		#writing file	
		file=open(os.path.join(config.prepscoredir, tardoc), 'wb') #resfile
		file.write(string)
		file.close()

def detscore(): #mainly for tinkering/filtering with document scores and various thresholds and quick generating scores from /prepscore/ 
	if not os.path.exists(config.detscoredir): #auto-create if not exists
		os.makedirs(config.detscoredir)
	print "Computing Detailed scores..."
	for tardoc in targetlist:
		print "Computing Detailed scores for "+tardoc
		
		scorelist=[]
		string=''
		
		file=open(os.path.join(config.prepscoredir, tardoc), 'rb') #reading list of files published under datethreshold
		checkpasseddocs=file.readlines()
		file.close()
		
		for line in checkpasseddocs:
			score, tscore, wscore, uscore, fscore, dscore, doc=line.split(',')
			if tscore > config.titlethreshold and wscore > config.wordthreshold and uscore > config.uqcheckthreshold and fscore > config.fqcheckthreshold:
				#newscore=(float(tscore)*0.1605+float(wscore)*0.2009+float(uscore)*0.2476+float(fscore)*0.3193+float(dscore)*0.0408)/len(checkpasseddocs)
				newscore=(float(tscore)*0.16+float(wscore)*0.20+float(uscore)*0.24+float(fscore)*0.31+float(dscore)*0.04)/len(checkpasseddocs)
				if newscore> 0.0:
					scorelist.append([newscore, doc])
			
		scorelist.sort(reverse=True)
		
		for score in scorelist:
			string+=str(score[0])+','+score[1] #+"\n"
		
		file=open(os.path.join(config.detscoredir, tardoc), 'wb') #reading list of files published under datethreshold
		file.write(string)
		file.close()

def genqrel(resdir): #to generate the clinss format run file
	if not os.path.exists(config.rundir): #auto-create if not exists
		os.makedirs(config.rundir)
	string=''
	for tardoc in targetlist:
		doclist=[]
		print "Preparing QREL output for "+tardoc
		#file=open(resultsdir+resdir+tardoc, 'rb') #reading list of files published under datethreshold
		doclist=gettopdocs(tardoc, resdir) #file.readlines()
		#file.close()
		if doclist != '':
			for line in doclist:
				values= line.split(',')
				string+=tardoc+' Q0 '+values[len(values)-1].replace('\n', '')+' '+str(doclist.index(line)+1)+' '+str(float(values[0]))+"\n"
	print "Generating runfile for /resultdir/"+resdir+"in "+config.rundir+"/run-"+resdir+"-"+time.strftime("%Y%m%d%H%M%S")+".qrel"
	file=open(os.path.join(config.rundir, "run-"+resdir+"-"+time.strftime("%Y%m%d%H%M%S")+".qrel"), 'wb') #resfile
	file.write(string)
	file.close()			

#-----------------------------------------------------------------------
#runs
#-----------------------------------------------------------------------

if __name__=="__main__":
	#pre-process - generating list of documents for each check
	#datechecker()

	#candidate selection
	#titlechecker()
	#wordchecker()
	#checkuqwords()
	#checkfqwords()
	
	#all 5 tests at once - less IO ops
	batch_process_tests()

	#combining scores
	prepscore()
	detscore()

	#generating runfile
	genqrel("prepscore")
	genqrel("detscore")
