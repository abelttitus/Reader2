# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 22:37:10 2021

@author: abelt
"""

import tabula
import pandas as pd
import csv
from functools import reduce

def cont_nos(start,end):
    return(list(range(start,end+1)))

def blank_sl(sl_no_ranges):
    blanks=[]
    for j in range(len(sl_no_ranges)):
        blanks.append(cont_nos(sl_no_ranges[j][0],sl_no_ranges[j][1]))
    return list(reduce(lambda x,y:x+y,blanks))

def process_pdf(package,start_pg_no,end_pg_no,value_ind,file_name):
    # package="L110_EMACE"
    # file_name='ccdread/static/upload/L110_EMACE.pdf'
    save_file='ccdread/static/upload/'+package+"_"+"Component_list.csv"

    # start_pg_no=12
    # end_pg_no=15
    clist=[[' ',' ','','','','']]
    c_nos=84
    beg_of_doc=True
    # [top,left,bottom,width]
    #left and width no change

    box=[2.09,0,6.85,10.97] #top 2.10 bottom 6.89
    fc = 28.28*2.54
    for i in range(0, len(box)):
        box[i] *= fc

    # value_ind=3
    cid_ind=1

    box2=[1.87,0,7.0,10.97] #top 2.10 bottom 6.89
    fc = 28.28*2.54
    for i in range(0, len(box2)):
        box2[i] *= fc
    page_begin=True

    for page in range(start_pg_no,end_pg_no+1,1):
        if page_begin:
            table = tabula.read_pdf(file_name,pages=page,area=box)
            page_begin=False
        else:
            table = tabula.read_pdf(file_name,pages=page,area=box2)
        t1=table[0]
        sl_no=1
        for index,rows in t1.iterrows():
            row_data=[str(rows[0]),str(rows[1]),str(rows[2]),str(rows[3]),str(rows[4]),str(rows[5])]
            # break
            # if sl_no==8:
            #     break
            if '\uf06dF' not in row_data[value_ind]:  #Detect \uf06dF and replace with u
                if '\uf057' not in row_data[value_ind]: # Detect '\uf057 and replace with ohm
                    if 'μ' in row_data[value_ind] or 'Ω' in row_data[value_ind] or 'Ώ' in row_data[value_ind]: # Detect and replace mu, ohm symbols
                        val=list(row_data[value_ind])
                        for inde,elem in enumerate(val):
                            if elem=='μ':
                                val[inde]='u'
                            elif elem=='Ω':
                                val[inde]='ohm'
                            elif elem=='Ώ':
                                val[inde]='ohm'
                        row_data[value_ind]=''.join(val)
                else:
                    row_data[value_ind]=row_data[value_ind].replace('\uf057','ohm')
            else:
                row_data[value_ind]=row_data[value_ind].replace('\uf06dF','uF')
                
            if('nan' in row_data):   
                if row_data[0]=='nan': #if first col is nan, then its an append, else its a new row. Based on assumption that Sl No will not take another row
                    if (row_data[0]==row_data[1]==row_data[2]==row_data[3]==row_data[5]=='nan' and ('PPL' in row_data[4]) ) or (row_data[0]==row_data[1]==row_data[2]==row_data[3]==row_data[4]=='nan' and ('PPL' in row_data[5]) ): # Simply to avoid this condition, to find out PPL/A/B
                        a=5 # Simply run anything
                    else:
                        if len(clist)==0:   # Check if clist is empty, add a empty row for appending
                            clist.append(['','','','','',''])
                        for i in range(len(row_data)):    
                            if row_data[i]!='nan':
                                clist[-1][i]+=' '
                                clist[-1][i]+=row_data[i]
                else:                                                #New row
                    for ind,ele in enumerate(row_data):
                        if ele=='nan':
                            row_data[ind]=''
                    clist.append(row_data)
                    
            else:
                clist.append(row_data)
            sl_no=sl_no+1
        
    for j in range(len(clist)):
        if 'R' in clist[j][cid_ind]: # Check resistor
            if 'ohm' in clist[j][value_ind]:
                clist[j].append('ohm')
            elif 'K' in clist[j][value_ind]:
                clist[j].append('K ohm')
            elif 'E' in clist[j][value_ind]:
                clist[j].append('ohm')
        if 'C' in clist[j][cid_ind]:
            if 'uF' in clist[j][value_ind]:
                clist[j].append('uF')
            elif 'PF' in clist[j][value_ind]:
                clist[j].append('pF')
            elif 'nF' in clist[j][value_ind]:
                clist[j].append('nF')
            elif 'pF' in clist[j][value_ind]:
                clist[j].append('pF')
            elif 'pf' in clist[j][value_ind]:
                clist[j].append('pF')
        if 'L' in clist[j][cid_ind]:
            if 'uH' in clist[j][value_ind]:
                clist[j].append('uH')

    # Insert Table Headings
    if value_ind==3:
        clist.insert(0,['Sl No','Comp ID','Type/Style','Value','Mil Part No','PPL'])
    else:
        clist.insert(0,['Sl No','Comp ID','Value','Type/Style','Mil Part No','PPL'])
    #to excel #
    try:
        with open(save_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(clist)
    except:
        print("UTF Encoding performed")
        with open(save_file, "w", newline="",encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(clist)   
    
    return save_file