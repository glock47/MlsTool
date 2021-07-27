

Action=$1
TaskNum=277
Process=4
FileName="ApiSniffer"

# sniffer
echo $Action
if [ "$Action" == "sniffer" ]; then
	rm -rf Data/StatData/ApiSniffer*
	
	ProcNum=$[TaskNum/Process]
	for((Num=0;Num<$Process;Num+=1));  
	do
		Start=$[Num*ProcNum]
		End=$[Start+ProcNum]
		Name=$FileName"$Num"
		
		echo "python collect.py -s apisniffer -b $Start -e $End -f $Name -d"
		./collect.py -s apisniffer -b $Start -e $End -f $Name &
	done
	echo "Sniffer all Done!"
else
    FileList=`ls Data/StatData/ApiSniffer*`
    Output="Data/StatData/ApiSniffer.csv"
    for file in $FileList; 
    do
   		if [ $Output == $file ]; then
   			continue
   		fi
   		
   		echo "Process $file"
   		cat $file >> $Output
   		rm -rf $file
    done
    echo "All Done!"
fi




