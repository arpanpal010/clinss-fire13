filepath=`readlink -f $0`;
rootdir=${filepath%/*};
for line in $rootdir/run*
do
echo "FILE:$line"
perl $rootdir/clinss13.eval.pl $rootdir/clinss13-en-hi.qrel $line 0
echo "-"
done

