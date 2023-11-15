import geopandas as gp 
import numpy as np 
import pandas as pd 
import json 

def binary2multiple_parents(net, max_nparents = 10, remove_lenght_zero = True, reset_index = True):
    '''This function takes as an argument "n" a GeoDataFrame describing the network obtained by TauDEM
    It returns the same dat with added np: number of parents, and us1...to us10 the upstream parents, 
    with this we can avoid using null links in HLM
    Parameters:
    - max_nparents is the total number of new parents
    - remove_lenght_zero (true), removes the links with StraightL==0
    - reset_index (false), the function makes LINKNO the index at the beggining, it brings them back to normal after end'''
    #Set index, and creates the numparents field and the fileds for the upstream parents
    net.set_index('LINKNO', inplace = True)
    net['np'] = 0
    for i in range(1,11):
        net['us%d' % i] = -1

    #Iterate through links
    for lid in net.index:

        #Gets the link downstream
        ld = net.loc[lid, 'DSLINKNO']

        #check if is not an outlet of the region or if it has lenght>0
        if ld > -1 and net.loc[lid, 'StraightL'] > 0:

            #Checks if the links downstream has no lenght
            if net.loc[ld,'StraightL'] == 0:
                #If has no length, iterates until reaching a link that has lenght
                flag = True
                while flag:
                    #Next lid downstream
                    ld = net.loc[ld, 'DSLINKNO']
                    if ld == -1: 
                        #Finish if reach an outlet
                        flag = False
                    elif net.loc[ld,'StraightL'] > 0:
                        #Finish if finds a lid with lenght>0
                        flag  = False

            if ld > -1:
                #Updates the number of parents 
                net.loc[ld, 'np']+=1

                #Add the parent
                nparent = net.loc[ld, 'np']
                net.loc[ld, 'us%d' % nparent] = lid
    if remove_lenght_zero:
        net = net[net.StraightL>0]
    if reset_index:
        net.reset_index(inplace = True)
    return net


def get_subwatershed(net, link):
    '''Extracts the network corresponding to the watershed upstream of a link, the net has to be obtained via 
    the binary2multiple_parents function.'''
    #List of links that belong to the network
    lids = [link]
    #Iterate over the increasing list of links
    for lid in lids:
        #Find the total number of parents
        nparents = net.loc[lid,'np']
        #Append the parents if the nparents >0
        if nparents>0:
            #Parents list
            lista = ['us%d' % i for i in range(1,nparents+1)]
            #Appending parents
            lids.extend(net.loc[lid,lista].values.tolist())
    #Final subnet
    return net.loc[lids]

def hlm_write_rvr(net, path):
    '''Takes a network that has been proccessed with remove_virtual_links.py and extracts the rvr 
    file required for HLM at the designed path'''
    parents_name = ['us%d' % i for i in range(1,net.np.max()+1)]
    with open(path,'w',newline='\n') as f:
        f.write('%d\n' % net.shape[0])
        f.write('\n')
        for link in net.index:
            f.write('%d\n' % link)
            if net.loc[link,'us1'] == -1:
                f.write('0\n')
            else:
                parents = net.loc[link, parents_name].values
                parents = parents[parents > 0]
                f.write('%d ' % parents.size)
                for parent in parents:
                    f.write('%d ' % parent)
                f.write('\n')            
            f.write('\n')
        f.close()
        
def hlm_load_prm_configs(path = '/home/nicolas/hpchome/network_conditioning/codes/model_prm_config.json'):
    with open(path,'r') as f:
        model_prm = json.load(f)
    return model_prm

def hlm_write_prm(net, path, lid = None, model='608', modprm = None, min_area = 0.01):
    '''Writes a prm file to a path using a table with the network (net) and 
    the model parameters (if constant) using codes/model_prm_config.json
    for distributed parameters set a list of parameters represented in the network 
    table (not implemented)'''
    #Loads the dict with the model parameters for the constant case
    if modprm is None:
        modprm = hlm_load_prm_configs()
    #Test if there will be a subnet
    if lid is not None:
        net = get_subwatershed(net, lid)
    #Compute the basic attributes of hill area, upstream area, and length    
    net['area_km'] = net['area']/1e6
    net.loc[net['area_km'] < min_area, 'area_km'] = 0.01
    net['area_up_km'] = net['DSContArea'] / 1e6
    net['length_km'] = net['Length']/1000
    net.loc[net['length_km'] < min_area, 'length_km'] = 0.01
    #Writes down the file 
    with open(path, 'w') as f:
        f.write('%d\n\n' % net.shape[0])
        for lid in net.index:
            f.write('%d\n' % lid)
            f.write('%.4f %.4f %.4f ' % tuple(net.loc[lid,['area_up_km', 'length_km','area_km']].values.tolist()))
            if model is not None:
                f.write('%s' % modprm[model][0])
            f.write('\n\n')
            
def get_lids_downstream(lid, net):
    '''Function that gets the list of downstream segments given a linkid'''
    #Define list of lids 
    lids_down = []
    while lid > 0:
        lids_down.append(lid)
        lid = net.loc[lid, 'ds']
    return lids_down


def get_lids_upstream(lid, net, max_length = 1500):
    '''Function to get the upstream segments of a given lid along the main channel.
    Stop when the accumulated length is above the max_length'''
    #Define local variables 
    length = net.Length.values
    area = net.DSContArea.values
    lids = net.index.values
    ds = net.ds.values
    tot_lenght = length[np.where(lid == lid)[0]]
    lids_up = []
    flag = True
    while flag:
        up = np.where(ds == lid)[0]
        if up.size > 0:
            pos = up[np.argmax(area[up])]
            lid = lids[pos]
            tot_lenght += length[pos]
            lids_up.append(lid)
        else:
            flag = False            
        if tot_lenght > max_length:
            flag = False
    return lids_up