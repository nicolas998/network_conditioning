#!/bin/sh
#$ -N I$name
#$ -j y
#$ -cwd
#$ -pe smp $nprocess
####$ -l mf=16G
#$ -q IFC

/bin/echo Running on host: `hostname`.
/bin/echo In directory: `pwd`
/bin/echo Starting on: `date`

mpirun -np $nprocess /Users/nicolas/executables/asynch/bin/asynch $global
python rec_fixer.py $rec_path