#!/home/nicolas/.conda/envs/hlmplay/bin/python 

from ifis_tools import auxiliar as aux 
import argparse
from datetime import datetime, timedelta
from string import Template 
import os 
import pandas as pd
import glob 

def create_project_folder(path, project_name):
    # Define the folder and subfolder names
    main_folder = path + project_name    

    # Check if the main folder exists
    if not os.path.exists(main_folder):
        # Create the main folder if it doesn't exist
        os.makedirs(main_folder)

    for sub_folder in ['dats','globals','states']:
        # Construct the subfolder path
        subfolder_path = os.path.join(main_folder, sub_folder)

        # Check if the subfolder exists
        if not os.path.exists(subfolder_path):
            # Create the subfolder if it doesn't exist
            os.makedirs(subfolder_path)


rain_products = {
    'MRMS':{'path':'/Dedicated/MRMS/HLM_plus_v202310/bin_mrms/'}
}

base_path = '/Users/nicolas/network_conditioning/local_data/ifis_config/base_data/'
out_path = '/Users/nicolas/network_conditioning/local_data/ifis_config/'

##################################################################################################
#Parse arguments to the program
parser = argparse.ArgumentParser(description='Creates a gbl file and its respective runfile')
parser.add_argument('project',type=str, help = 'Project name to set up'),
parser.add_argument('date1', type=str, 
                    help='Initial date (YYYY-MM-DD-HH:MM)')
parser.add_argument('date2', type=str, 
                    help='End date date (YYYY-MM-DD-HH:MM)')
#Forcing arguments
parser.add_argument('--product', type=str, help = 'rainfall product (only MRMS avaialable)', default = 'MRMS')
parser.add_argument('--rainType', type=str, default = '5')
parser.add_argument('--etType', type=str, default = '7')
parser.add_argument('--tempType', type=str, default = '0')
parser.add_argument('--soil_tempType', type=str, default = '0')
parser.add_argument('--rainFactor','-f', type=str, default='1')
parser.add_argument('--etPath', type=str, default='%sMODIS_mean_et.mon' % base_path)
parser.add_argument('--tempPath', type=str, default='/Dedicated/IFC/data_bin/hd_iowa/narr_tempC/')
parser.add_argument('--soil_tempPath', type=str, default='/Dedicated/IFC/data_bin/hd_iowa/narr_soil_temperature/')
parser.add_argument('--rainChunk', type=str, default = '10')
parser.add_argument('--etChunk', type=str, default = '')
parser.add_argument('--tempChunk', type=str, default = '10')
parser.add_argument('--soil_tempChunk', type=str, default = '10')
parser.add_argument('--rainStep', type=str, default = '60')
parser.add_argument('--etStep', type=str, default = '')
parser.add_argument('--tempStep', type=str, default = '1440')
parser.add_argument('--soil_tempStep', type=str, default = '1440')
parser.add_argument('--nglobal', type=str, default = '5')
parser.add_argument('--ndays','-n', type=int, default = 9999,
                    help='number of days to split the execution')
parser.add_argument('--yearly','-y', default = 0, type = int, help = 'if 1, starts and ends the simulation for each year')                    
parser.add_argument('--nproc','-p', default = 14, type = int, help = 'Number of processors to use')                    
parser.add_argument('--initial', type = str,default = '%sinitial.uini' % base_path,
                    help='Initial values (default = initial.uini')
parser.add_argument('--model','-m',type=str, default = '608',help='model to use 608 , 612 or 400')
parser.add_argument('--vo', type = str, default='0.33')
parser.add_argument('--lambda1', type = str, default='0.2')
parser.add_argument('--lambda2', type = str, default='-0.1')
parser.add_argument('--Hu', type = str, default='36')
parser.add_argument('--infil', type = str, default='1.9')
parser.add_argument('--perc', type = str, default='0.7')
parser.add_argument('--sup', type = str, default='3')
parser.add_argument('--sub', type = str, default='65')
parser.add_argument('--gw', type = str, default='167')
parser.add_argument('--meltf', type=str, default='5')
parser.add_argument('--tempth', type=str, default='0')
parser.add_argument('--frozengr', type=str, default='0')
parser.add_argument('--temprange', type=str, default='20')
parser.add_argument('--control', type=str, default='%sifis_usgs.sav' % base_path)
parser.add_argument('--prm', type=str, default='%sifis_iowa.prm' % base_path)
parser.add_argument('--rvr', type=str, default='%sifis_iowa.rvr' % base_path)
args = parser.parse_args()

#Create a folder for the project if it does not exists
create_project_folder(out_path, args.project)

#Reads the baseglobal file
f = open('%stemplates/baseglobal.gbl' % base_path,'r') 
t = f.readlines()
f.close()
globTemplate = Template(''.join(t))

#Reads the runfile 
f = open('%stemplates/baserun.sh' % base_path,'r')
t = f.readlines()
f.close()
runHeadTemp = Template(''.join(t[:-2]))
runBaseTemp = Template(t[-2])
runFixerTemp = Template(t[-1])

#Set the path to the prm and rvr files
prmFile = '%s%s' % (base_path, args.prm)
rvrFile = '%s%s' % (base_path, args.rvr)


#Sets the global parameters and the number of globals
params = args.tempth+' '+args.meltf+' '+args.frozengr+' '+args.temprange+' '+args.rainFactor
#args.nglobal = '4'

#Gets the intial and end date of the execution
date1 = datetime.strptime(args.date1,'%Y-%m-%d-%H:%M'),
date2 = datetime.strptime(args.date2,'%Y-%m-%d-%H:%M'),
dates = pd.date_range(date1[0], date2[0], freq = '1H', )
str_date1 = date1[0].strftime('%Y%m')
str_date2 = date2[0].strftime('%Y%m')

#sets the run file and the global file names
project_path = '%s%s/' % (out_path, args.project)
name_run = '%s%s/runhlm_%s_%s.sh' % (out_path, args.project, str_date1, str_date2)
name_gbl = 'g.gbl'

#Opens the run file to start writing on it
f_run = open(name_run,'w')
_name = '%s_%s' % (args.project, str_date1)
f_run.write(runHeadTemp.safe_substitute({'name':_name, 'nprocess': args.nproc}))
#f.close()

#Gets the slices to run the model
if args.yearly == 0:
    #Get the start and ending date of each year 
    starts = dates[((dates.month == 1) & (dates.day == 1) & (dates.hour == 0))]
    starts = starts.tolist()
    ends = dates[((dates.month == 12) & (dates.day == 31) & (dates.hour == 23))]
    ends = ends.tolist()
    if dates[0] != starts[0]:
        starts.insert(0, dates[0])
    if dates[-1] != ends[-1]:
        ends.append(dates[-1])
    #split the records into more if there are more 
    step = 24 * args.ndays
else:
    starts = date1[0].year
    ends = date2[0].year
    step = '%dd' % args.ndays
    step_n = int(args.ndays)
    

#Define the path to the rainfall 
rain_path = rain_products[args.product]['path']
    
#Initialize the counter of simulation periods    
periods = 1
#Starts writing global files 
gblDict = {}
initial = args.initial
if args.yearly == 0:
    #Sets globals for each year
    for start, end in zip(starts, ends):    
        #Get the starts and ends of the subperiods defined by the number of days 
        if step > 0 and step <= 8760:
            dates_2 = pd.date_range(start, end, freq = '1H')
            starts2 = dates_2[::step].tolist()
            ends2 = dates_2[step-1::step].tolist()
            ends2.append(dates_2[-1])
            freno = False
        else:
            starts2 = starts
            ends2 = ends
            freno = True
        #Uses the sub-dates to write gbl files 
        for s, e in zip(starts2, ends2):
            str_date1 = s.strftime('%Y%m%d%H')
            str_date2 = e.strftime('%Y%m%d%H')
            if os.path.splitext(initial)[-1] == '.uini':
                initialType = '1'
            elif os.path.splitext(initial)[-1] == '.rec':
                initialType = '2'
            
            #Sets forcing paths 
            if args.etType == '7':
                etPath = args.etPath
            else:
                etPath = args.etPath + args.region + '/' + start.year + '/'
            
            a ={'date1': s.strftime('%Y-%m-%d %H:%M'),
                'date2': e.strftime('%Y-%m-%d %H:%M'),
                'prmFile':prmFile,
                'rvrFile':rvrFile,
                'initialFile':initial,
                'initialType':initialType,
                'year': start.year,
                'unix1': aux.__datetime2unix__(s),
                'unix2': aux.__datetime2unix__(e),
                'str_date1':str_date1,
                'str_date2':str_date2,
                'datName':'%sdats/%s_%s.dat' % (project_path, str_date1, str_date2),  #project_path + 'dats/' +  + '_'+args.product + '_f' + args.rainFactor + '_'+ str_date1 + '_' + str_date2 + '.dat',
                'recFile': '%sstates/%s_%s.rec' % (project_path, str_date1, str_date2),#project_path + 'states/' + + '_'+args.product + '_f' + args.rainFactor + '_' + str_date1 + '_' + str_date2 + '.rec',
                'rainPath': rain_path + str(start.year) + '_v2/',
                'etPath': etPath,
                'tempPath': args.tempPath + '/' + str(start.year) + '/',
                'soil_tempPath': args.soil_tempPath + '/' + str(start.year) + '/',
                'rainType': args.rainType,
                'etType': args.etType,
                'tempType': args.tempType,
                'soil_tempType': args.soil_tempType,
                'rainStep':args.rainStep,
                'etStep':args.etStep,
                'tempStep':args.tempStep,
                'soil_tempStep':args.soil_tempStep,
                'rainChunk':args.rainChunk,
                'etChunk':args.etChunk,
                'tempChunk':args.tempChunk,
                'soil_tempChunk':args.soil_tempChunk,
                'nglobal': args.nglobal,
                'controlName':args.control,
                'scratch': '/nfsscratch/Users/nicolas/'
            }
            #if args.model == '400' or args.model == '612':
            a.update({'global_params': params})
            a.update({'model_uid': args.model})



            initial = '%sstates/%s_%s.rec' % (project_path, str_date1, str_date2) #project_path + 'states/' + '_'+args.product + '_f' + args.rainFactor + '_'+ str_date1 + '_' + str_date2 + '.rec'                        
            periods += 1
            shortgbl = '%sglobals/step_%s_%s.gbl' % (project_path, a['str_date1'], a['str_date2'])
            
            #Replace in the global template 
            glob = globTemplate.safe_substitute(a)
            f = open(shortgbl, 'w')
            f.writelines(glob)
            f.close()

            #Write the global name in the runfile 
            text = runBaseTemp.safe_substitute({'global':shortgbl, 'nprocess': args.nproc})
            f_run.write(text)
            
            #Write the rec_fixer in the runfile 
            #rec_path = '/Users/nicolas/2022_iowa_hd/hlm_region_'+args.region+'/states/'+ a['recFile']
            #text = runFixerTemp.safe_substitute({'rec_path':rec_path})
            #if args.model == '608':
            #    f_run.write(text)

        if freno:
            break
#Write the command that post-process the data 
cmd  = 'python3 /Users/nicolas/network_conditioning/codes/dats2parquet.py %sdats/ %ssim_flows.gzip -r' % (project_path, project_path)
f_run.write(cmd)
# #Erase dats and states 
# cmd  = 'rm %sdats/%s_%s_f%s*\n' % (project_path, watershed, args.product, args.rainFactor)
# f_run.write(cmd)
# cmd  = 'rm %sstates/%s_%s_f%s*\n' % (project_path, watershed, args.product, args.rainFactor)
# f_run.write(cmd)
# f_run.write('rm -r /nfsscratch/Users/nicolas/' + watershed + '_' + args.product + '/\n')

f_run.close()

