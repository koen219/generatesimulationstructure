!INIT
OUTFILE=${DATAFOLDER}/output.txt
mkdir $DATAFOLDER

cp template.par $PARFILE.par
cp template.py $PARFILE.py

!PARAMETERS

echo "storeprefix='${DATAFOLDER}'" >> ${PARFILE}.py
echo "parfile = '${PARFILE}.par'" >> ${PARFILE}.py

mv ${PARFILE}.py ${PARFILE}.par $CPM

cd $CPM

echo 'starting at: $(date)' >> $OUTFILE
python main.py $PARFILE.py &>> $OUTFILE
rm ${PARFILE}.py ${PARFILE}.par
echo 'Done at: $(date)' >> $OUTFILE
