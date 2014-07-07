#!/usr/bin/perl -w
# Copyright (C) 2012 Parth Gupta All rights reserved.


# This script evaluates the NDCG@k for the supplied runs according to the relevance judgement (qrel). 
# The script is developed for the purpose to evaluate the runs submitted to CL!NSS track at FIRE 2012. 
#
# http://www.dsic.upv.es/grupos/nle/clinss.html
#
# For more details anout NDCG measure see [1] and [2].
#
# Author: Parth Gupta, email: pgupta@dsic.upv.es
#
# References
# [1] Kalervo Järvelin, Jaana Kekäläinen: Cumulated gain-based evaluation of IR techniques. ACM Trans. Inf. Syst. 20(4): 422-446 (2002)
# [2] http://en.wikipedia.org/wiki/Discounted_cumulative_gain 

if ( @ARGV != 3 ) {
	die "\nInsufficient/Improper Arguments.\n\nUsage:\nperl clinss12-eval-try.pl <qrelFile> <runFile> <verbose> \n\n\nOptions\n<verbose>\t0\tPrints only average (over all the queries)\n\t\t1\tPrints querywise scores\n\t\t2\tPrints querywise ranklist and corresponding gold ranklist\n\n";
}


# The list of "n" to be considered in evaluation
my @N = (1,2,3,4,5,10,20);

# Path to the Qrel File
$QRELS = $ARGV[0];

# Path to the Run File
$RUN = $ARGV[1];

# 0 if only average to be printed
# 1 if results for all the queries required
$verbose = $ARGV[2];

# If some Queries are not needed in the evaluation
# then include in the list in the following manner.
# = ("xyz", 1, 
#    "abc", 1);
# and so on.. 
my %extopic = ("english-document-00046.txt",1);

my @avg;

my $j = 0;
foreach(@N) {
	$avg[$j]=0;
	$j++;
}

my %topiclist = ();
my %runlist = ();



# Read qrels file and store in hash
open (QRELS) || die "$0: cannot open \"$QRELS\": !$\n";
while (<QRELS>) {
	chomp($_);
	my @cols = split(/ /);
 	$topic = $cols[0];
 	$docno = $cols[2];
 	$rel = $cols[3];
 	# stores only non-zero relevance
	if($rel>0) {
  		$topics->{$topic}->{$docno} = $rel;
	}
 }

# Read the run file and store it in the hash
open (RUN) || die "$0: cannot open \"$QRELS\": !$\n";
while (<RUN>) {
	chomp($_);
	my @cols = split(/ /);
 	$topic = $cols[0];
 	$docno = $cols[2];
 	$rank = $cols[3];

  	$rel = 0;
  	if(exists $topics->{$topic}->{$docno}) {
		$rel = $topics->{$topic}->{$docno};
	}
  	$runlist->{$topic}->{$rank} = $rel;
 }

 
 my @ranklist;
 my %scores;
 
 print "Query\t\t\t\t";
 foreach(@N) {
 	print "\tNDCG\@$_";
 }
 print "\n";
 my $total = 0;

	for my $k1 ( sort keys %$topics) {
		       print "Topic: $k1\n" if $verbose>=2;
		if(!exists $extopic{$k1}) {
			$total++; 
			if(exists $runlist->{$k1}) {
				@ranklist=();
				for my $k2 ( sort{$a <=> $b}  keys  %{$runlist->{ $k1 }} ) {
					$ranklist[int($k2)] = $runlist->{$k1}->{$k2};
#            				print "$k1\t$k2\t$runlist->{ $k1 }->{ $k2 }\n";
				}
				$ranklist[0]=0;
   			
#   				for my $k2 ( sort{$a <=> $b}  keys  %{$topics->{ $k1 }} ) {
#       				$tlist[int($k2)] = $topics->{$k1}->{$k2};
#           				print "$k1\t$k2\t$topics->{ $k1 }->{ $k2 }\n";
#				}
				@tlist = values %{$topics->{$k1}};
				@ilist = sort { $b <=> $a } @tlist;
#   				print "@ranklist\n";
  				my @printRanklist = @ranklist[1 .. $#ranklist];
				print "Your Ranklist: @printRanklist\n" if $verbose>=2;
   				print "Gold Ranklist: @ilist\n" if $verbose>=2;
				@result = getdcg();
  
				if(scalar(@result)>1) {
					print "$k1\t" if $verbose>=1;
					my $j=0;
					foreach(@result) {
						print "\t" if $verbose>=1;
						printf '%.4f',$_ if $verbose>=1;
						$avg[$j]+=$_;
						$j++;
					}
					print "\n" if $verbose>=1;
				}
			}	
     		
			
		}	
	}
	print "average scores\t\t\t";
	foreach(@avg) {
		print "\t";
		printf '%.4f',($_/$total);
	}
	print "\n";

# Subroutine to compute DCG for the specified ranklist
sub getdcg {
	my $count = 0;
	my @result;
	foreach(@N) {
		$dcg=0;
   		$idcg=0;
   		# gains for the ranklist
   		if(defined($ranklist[1])) {
   			$dcg += int($ranklist[1]);
   
   			for($i=2; $i<=$_; $i++) {
   				if(defined($ranklist[$i])) {
					$dcg += (($ranklist[$i]==0) ? 0 : ($ranklist[$i]/(log($i)/log(2))));
				}
   			}
   
   		# ideal gains
#   		@ilist = sort { $b <=> $a } @ranklist;
		if(defined($ilist[0])) {
			$idcg += int($ilist[0]);
		}
   		for($i=1; $i< $_; $i++) {
   			if(defined($ilist[$i])) {
				$idcg += (($ilist[$i]==0)  ? 0 : ($ilist[$i]/(log($i+1)/log(2))));
			}
   		}
   		$result[$count] = ($idcg==0) ? 0 : ($dcg/$idcg);
   		$count++;
		}
	}
	return @result;
}
