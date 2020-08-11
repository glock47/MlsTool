data_dir=../Arca/Data/CmmtSet
cmmts_dirs=`ls $data_dir`

for dir in $cmmts_dirs
do
	file=$data_dir/$dir/$dir.csv
	cp $file ./Data/CmmtSet/
done