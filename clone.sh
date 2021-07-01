

TaskNum=$1
Process=40

ProcNum=$[TaskNum/Process]
for((Num=0;Num<$Process;Num+=1));  
do
	Start=$[Num*ProcNum]
	End=$[Start+ProcNum]

	python collect.py -s clone -b $Start -e $End &	
done





