import os 
import glob 

#Fisrt two letter refer to the hillslope param, then each letter pair is 
#the forcing and how it was added.
directory = 'hlm_config/run_files/'  
runfile_path = 'hlm_config/run_files/master_runfile.sh'  # replace with the path where you want to save the master runfile

#products = ['MRMS','IFC','EtI','EtM']
#products = ['IFCA','MRMS','IFC']
products = ['EtIra','EtMra']

#factors = [0.7,0.8,0.9,1.1,1.2,1.3]
#factors = [0.95,0.98,0.99,1.01,1.02,1.05]
#factors = [0.75,0.85,1.4]
#factors = [0.6,1.15,1.25,1.35,1.4]
#factors = [0.6,0.65,0.7,0.75,0.8,0.85,0.9,0.95,0.98,0.99,1.0,1.01,1.02,1.05,1.1,1.15,1.2,1.25,1.3,1.35,1.4]
#factors = [1.45,1.5,1.55,1.6,1.65,1.7,1.8,1.9,2.0]
#factors = [0.55,0.5,0.45,0.4,0.35,0.3,0.25,0.2,0.15,0.1,1.75,1.85,1.95]
factors = [2.5,3,3.5,4]
factors = [1]

if __name__ == '__main__':
    #Iterate through the watershed names 
    for watershed in [14,]:#range(1, 14):
        if watershed < 10:
            wat_name = '0%d' % watershed
        else:
            wat_name = '%d' % watershed
        #Create the run for every case using 
        for product in products:
            for factor in factors:
                #Create the run name 
                name = 'python set_global_files.py %s %s 2015-05-01-00:00 2020-12-31-23:00 -f %.2f -n 60 --region %s' % (wat_name, product, factor, region)
                os.system(name)    

    # with open(runfile_path, 'w') as f:
    #     f.write('#!/bin/bash\n')
    #     f.write('\n\n')
    #     f.write('# Submit multiple jubs\n')
    #     for filename in os.listdir(directory):
    #         if filename.endswith('.sh') and not filename.startswith('master'):
    #             f.write('qsub '+ filename + '\n')
    
    # #Create the master runfile 
    # list_run = glob.glob('hlm_config/run_files/*')
    # f = open('hlm_config/run_files/master.sh','w')
    # f.write('#!/bin/bash\n')
    # f.write('\n\n')
    # f.write('# Submit multiple jubs\n')
    # for file in list_run:
        
    #!/bin/bash
    