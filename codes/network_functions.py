import geopandas as gp 
import numpy as np 
import pandas as pd 

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
    parents_name = ['us%d' % i for i in range(1,11)]
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
                f.write('\n\n')            
            f.write('\n')
        f.close()