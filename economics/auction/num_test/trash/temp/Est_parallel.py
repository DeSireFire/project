# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 18:35:22 2018

@author: mgxgl
save the parallel running function

modify the private part--no
where mu_ai = a_1*i  ; var_ai = a_2*i 
remember the price should take log form

I should keep the setup
where mu_ai = a_1  ; var_ai = a_2

I just realied that my estimation moment has some problems 
modify the map_integ to take average inside the integ

#--- big modification ---#
I need to use (34) and (35) to do the estimation
To do this, I have to calculate the bidding function iteratively each time for each random vector 



"""

from functools import partial
from collections import defaultdict,OrderedDict
import time,datetime
import numpy as np
from Update_rule import Update_rule
from ENV import ENV
from Util import *
import copy
import scipy.stats as ss


def list_duplicates(seq):
    tally = defaultdict(list)
    for i,item in enumerate(seq):
        tally[item].append(i)
    return ((key,locs) for key,locs in tally.items() if len(locs)>=1)





def map_integ(price_v,x_signal_i,s_state,Update_bid,arg_data):
    i,bid,high_bid,low_bid=arg_data
    state=s_state[i]

    exp_value = Update_bid.bid_vector(x_signal_i[:,i],bid,state,price_v,i)
    # I just realized that I have to take integration inside 
    # like Hong and Shum 2003 SNLS, because x_signal is unkown and simulated. 
    # not like CT 2009 , their X can be observed

    exp_value_M = np.mean(exp_value)

    low_case  = low_bid  - exp_value_M
    high_case = high_bid - exp_value_M

    low_sum = np.square((low_case>0)*1*low_case)
    high_sum = np.square((high_case<0)*1*high_case)
    return (low_sum,high_sum)


def map_integ_new(price_v,x_signal_i,low_state,high_bound,Update_bid,arg_data):
    i,bid,high_bid,low_bid=arg_data
    # calculate lower bound
    exp_value1 = Update_bid.bid_vector_low(x_signal_i[:,i],bid,low_state[i],price_v,i)

    (exp_value2,w_n2) = Update_bid.bid_vector_high(x_signal_i[:,i],high_bound,price_v,i)

    # count the criterion
    low_case  = 1*(low_bid  <= exp_value1) # this lower bound should be one of the criterion
    # high_case = 1*(high_bid >= exp_value2)
    low_case=low_case.flatten()
    # question ~~~ how can I add w_n2
    final_w=w_n2*low_case
    
    return (exp_value2.flatten(),final_w)

def map_integ_final(arg_data):
    high_bid,low_bid,exp_value = arg_data
    exp_value_S= np.mean(exp_value)
    
    low_1     =  low_bid  - exp_value_S
    high_1    =  high_bid - exp_value_S
    low_sum = np.square((low_1>0)*1*low_1)
    high_sum = np.square((high_1<0)*1*high_1)
    return (low_sum,high_sum)

def para_fun_est(Theta,rng,xi_n,arg_data):
    tt,data_state,data_pos,price_v,pub_info=arg_data
    info_flag=pub_info[3]
    N        =int(pub_info[2])
    # finally I realized that my previous thought has big problem, what I want is actually the rank sequence not the sorted order. 
    # bug bug we should use np.argsort(data_state) not np.argsort(data_state)[::-1]
    # No no rank order !
    # ord_index=np.argsort(data_state)    # order the bidder's bidding value, highest has high order index! 
    #                                     # ord_index=np.argsort(data_state)[::-1] descedning order
    # rank_index=ss.rankdata(data_state)-1
    # wait still, I can use rank order to dervie the dropout price. 

    # order index to order from highest to lowest 
    ord_index=np.argsort(data_state)[::-1] 
    data_state=np.array(data_state)
    # index for generating the bidder identity make everyone the same
    iden_index=np.ones(N)
    info_v=np.ones(N)
    i_id=0
    if info_flag-1 >=0:
        info_v[info_flag] = 0
        if info_v[0] == 1:
            i_id = 0
        else:
            i_id = 1
    r     =pub_info[-1]

    
    Env=ENV(N, Theta)
    # argument for info_struct info_flag,ord_index,res
    para=Env.info_struct(info_v,iden_index,r)

    
    ladder=pub_info[0]
    Update_bid=Update_rule(para,r)

    

    # add whether it is informed or not informed  
    Update_bid.setup_para(i_id)
    
    # I think it is still the entry threshold not the final posting price as the lower bound
    X_bar = Update_bid.bound(r*np.ones([1,N]))
    # Why I need up, I do not need it 
    X_up = np.ones([1,N])*4
    x_signal=signal_DGP_est(para,rng,N,0,X_bar,X_up,xi_n)





    # construct lower price bound and upper price bound
    r_bar   = price_v[data_state[ord_index]]

    bid_low = r_bar
    bid_up  = (price_v[-1]+ladder)*np.ones(N)
    bid_v   = data_state[ord_index]
    # construct the posting activtity for lower and upper bound
    # high bound
    higher_bound = Update_bid.bound(r_bar)
    # sum_value=0

    # now I need to calculate empirical integ 
    # start = time.time()
    
    price_v=np.append(price_v,np.linspace(1,4,4)*ladder+price_v[-1])
    # lower bound 
    # re-order each bidder's bidding history
    bidder_bid_history=[data_pos[int(ord_index[i])] for i in range(len(ord_index))]
    

    low_state=np.zeros((N,N))

    # get the bidder's lower bound state for calculation
    for i in range(0,N):
        flag_select=np.ones(N)
        flag_select[i]=0
        select_flag=np.nonzero(flag_select)[0].tolist()

        low_state[i,0]=bid_v[i]
        
        temp_s=[]
        for j in select_flag:
            try:
                bid_post=bidder_bid_history[j][1]
            
                if bid_post[0] > bid_v[i]:
                    temp_s.append(0)
                else: 
                    temp_p=[x for x in bid_post if x < bid_v[i] ]
                    temp_p.sort()
                    temp_s.append(temp_p[-1])
            except Exception as e:
                print(e)
                print(data_pos)
                print(temp_p)
                print(bid_v[i])
                temp_s.append(0)
                print('this is number ',tt)
                input('wait for check')
                
        low_state[i,1:] = temp_s



    # start mapping for calculation
    map_func=partial(map_integ_new,price_v,x_signal,low_state,higher_bound,Update_bid)
    # i = 0.1.2.3... is the rank order for the participants!!!
    exp_value=list(map(map_func,zip(range(0,N),bid_v,bid_up,bid_low))) 
    exp_value2 =np.array([x[0] for x in exp_value])
    final_w    =np.array([x[1] for x in exp_value])
    final_w    = np.prod(final_w,axis=0)
    final_w    = final_w.astype(bool)
    # check whether it still has enough data satisfying the criterion
    # sum(final_w) >5
    
    exp_value2=exp_value2.T
    exp_value2=exp_value2[final_w,:]
    exp_value2=exp_value2.T
    if exp_value2.shape[1] <10:
        print('+++++++++++++++++++++++++')
        print('outlier! tt %d, # of bidders %d, # of x %d '%(tt,N,exp_value2.shape[1] ))
        print('posting bid :', end=' ')
        print(r_bar)
        print('+++++++++++++++++++++++++')
        return 100000
    #print(exp_value2.shape[1])
    object_value=list(map(map_integ_final,zip(bid_up,bid_low,exp_value2 )))
    low_part =np.array([x[0] for x in object_value])
    high_part=np.array([x[1] for x in object_value]) 
    #print(high_part)

    high_part[0]=0
    # sum together 
    # sum_value=np.sum(low_part,axis=0)**0.5 + np.sum(high_part,axis=0)**0.5
    low_part[1] =low_part[1]*N 
    high_part[1] = high_part[1] * N 
    sum_value = np.sum(low_part)/(2*N)+np.sum(high_part)/(2*N)
    norm_var=Theta['comm_var']+Theta['priv_var']+Theta['epsilon_var']
    final_value=np.sum(sum_value)/(norm_var**0.5)
    
    # end = time.time()
    # print('return auction {} with # of bidder {} and result final_value {} '.format(tt,N,final_value))    
    # print('time expenditure: {}'.format(end - start))
    return final_value    
