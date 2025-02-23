# -*- coding: utf-8 -*-
"""
Created on Sun Nov 11 13:29:54 2018

@author: mgxgl
This is for the simulation part 
There exist two part, first simulate a large space for updating rule and set it 
as default.
then each time when the price path chagnes, I use interpolate method to calculate 
sub space for update rule which hopefully could acceralate the calculation speed

 

"""

import numpy as np
from Update_rule import Update_rule
from scipy.interpolate import interpn
from ENV import ENV 
import copy


para_dict={
        "comm_mu":10,
        "priv_mu":1,
        "epsilon_mu":0,
        "comm_var":0.8,
        "priv_var":1.2,
        "epsilon_var":0.8,
        }




class Simu:
    def __init__(self,rng_seed=123,dict_para=para_dict):


        self.rng       =np.random.RandomState(rng_seed)
                
        self.comm_mu   =dict_para['comm_mu']
        self.priv_mu   =dict_para['priv_mu']
        self.noise_mu  =dict_para['epsilon_mu']
        self.comm_var  =dict_para['comm_var']
        self.priv_var  =dict_para['priv_var']
        self.noise_var =dict_para['epsilon_var']
        self.dict_para =dict_para

        
        

        
        
    def signal_DGP(self,flag_ID=0,flag_mode=0):
        g_m = -1 + (1+1)*self.rng.rand() 
        # common value in public
        
        if flag_mode == 0 :
            # fix pub_mu and randomize r 
            pub_mu = self.comm_mu
            r =  0.8 + 0.15*self.rng.rand() 
        elif flag_mode == 1:
            # fix the r and randomize pub_mu
            pub_mu = self.comm_mu + g_m                 
            r =  0.8
        else: 
            # randomize everything
            pub_mu = self.comm_mu + g_m
            r =  0.8 + 0.1*self.rng.rand() 
        
        MU     = self.info_para.MU
        SIGMA2 = self.info_para.SIGMA2
        
        
        x_signal=self.rng.multivariate_normal(MU.flatten(),SIGMA2)
        
        
        
        if flag_ID==1:
            
            info_index=1
        else:
            info_index=0

        
        
        
        return [pub_mu,x_signal,r,info_index]
    
    
    def interp_update_rule(self,N,E_update_rule,T_p_old,T_p_new,xi_v_old,xi_v_new):
        # given the large bidding function result, I interp current simulation 
        # bidding function
        # possibly abbandon in the future
        
        interp_mesh = np.array(np.meshgrid(xi_v_new, T_p_new,T_p_new,T_p_new))
        interp_points = np.rollaxis(interp_mesh, 0, 5).reshape((interp_mesh/(1+N), 1+N))
        
        
        return interpn((xi_v_old,T_p_old,T_p_old,T_p_old), E_update_rule, interp_points)
    
    
    def Data_simu(self,N,SS,T_end,info_flag=0,flag_mode=0):
        # functions for simulating the bidding path given the numebr of simualted times
        
        # initilize the updating rule 
        Env       =ENV(N, self.dict_para)
        if info_flag==0:
            self.info_para  =Env.Uninform()
        else:
            self.info_para  =Env.Info_ID()
            
        Update_bid=Update_rule(self.info_para)
        
        data_act=np.ones((SS,T_end),dtype=int)*(-1)  # bidding path 
        pub_info=np.zeros((SS,4))
        data_state=np.zeros((SS,N),dtype=int)  # current posting bid position for each bidder
        data_bid_freq=np.zeros((SS,N)) # each bidders bidding times 
        data_win=np.zeros((SS,1))
        freq_i  =np.zeros((SS,1))    # total bidding frequency
        freq_div_i=np.zeros((SS,1))
        freq_dis_i = np.zeros((SS,1)) # std of each bidder's biddingfrqeucy 
        num_i = np.zeros((SS,1),dtype=int)  # number of bidders in each auction
        diff_i = np.zeros((SS,1))  # std of highest bidding price (price)
        diff_pos_i = np.zeros((SS,1))  # std of highest bidding price (position)

        # Active_flag=np.ones(N)
        for s in range(0,SS):
            
            [pub_mu,x_signal, reserve,info_index]=self.signal_DGP(info_flag,flag_mode)
            pub_info[s,:]=[pub_mu, reserve,N,info_index]
            
            price_v = np.linspace(reserve*pub_mu,pub_mu*1.1, T_end-10)
            price_v=np.append(price_v,np.linspace(1.12*pub_mu,pub_mu*1.8, 5))
            price_v=np.append(price_v,np.linspace(1.85*pub_mu,pub_mu*2.5,5))
            
            self.T_p=price_v
            
            State = np.zeros(N,dtype=int)
            Active= np.ones(N,dtype=int)
            
            
            for t in range(0,T_end):
                
                if t == 0: 
                    curr_bidder=int(np.argmax(x_signal))
                    data_act[s,t] = curr_bidder
                    State[curr_bidder]=State[curr_bidder]+1
                else:
                    
                    for i in range(0,N):
                        temp_state=copy.deepcopy(State)
                        
                        ii = int(temp_state[i])
                        temp_state=np.delete(temp_state,i)

                        ss_state = [ii]
                        ss_state = ss_state + temp_state.tolist()
               
                        bid = max(ss_state)+1
                        result = Update_bid.real_bid(x_signal[i],bid,ss_state,price_v)
                        
                        Active[i] = result[2]
                        
                        
                    if sum(Active) ==1:
                        index=np.nonzero(Active)[0].tolist()
                        
                        posting=data_act[s,t-1]
                        if index == posting:
                            data_act[s,t:] = int(-1)
                        else:
                            curr_bidder      = int(index[0])
                            data_act[s,t]    = int(curr_bidder)
                            State[curr_bidder] = bid
                            data_act[s,t+1:] = int(-1)
                        
                        break
                    else :
                        if sum(Active) == 0:
                            data_act[s,t:] = int(-1)
                            break
                        
                        
                        
                        posting=data_act[s,t-1]
                        index=np.nonzero(Active)[0].tolist()
                        if posting in index :
                            index.remove(posting)
                           
                       
                       
                        curr_bidder   = self.rng.choice(index,size=1) 
                        data_act[s,t] = int(curr_bidder)
                        State[curr_bidder] = bid
           
        
            # final state
            # notice there exist mismatch between data act and state 
            # state is right data act need to add 1 
            data_state[s,:]=State
            
            # calculate the bidding frequency for each bidders 
            unique, counts = np.unique(data_act[s,:], return_counts=True)
            a=zip(unique,counts) 
            for ele in a:
                if ele[0] != -1:
                    data_bid_freq[s,int(ele[0])]=ele[1]
                else:
                    continue
            
            
            # calculate the real bidding number 
            temp_freq   =np.array([x for x in data_bid_freq[s,:] if x > 0])
            freq_i[s]   =sum(temp_freq)
            temp_freq   =temp_freq/ freq_i[s]
            freq_dis_i[s]=np.std(temp_freq)
            # check the bidding frequency difference among the bidders fix the 
            
            comb=np.array(np.meshgrid(temp_freq, temp_freq)).T.reshape(-1,2)
            #comb=np.array(np.meshgrid(data_bid_freq[s,:], data_bid_freq[s,:])).T.reshape(-1,2)
            v=abs(comb[:,0]-comb[:,1])
            freq_div_i[s]=np.sum(v)

            
            
            # winning
            data_win[s]=price_v[int(max(State))] / (pub_mu*reserve)
            
            # std of posting price difference by position
#            diff_i[s]=np.std(max(State)-State)
            # std of posting price difference by price
            
            temp_diff=np.array([price_v[int(x)] for x in State])
            temp_diff=data_win[s]-temp_diff/(pub_mu*reserve)
            diff_i[s]=np.std(temp_diff)
            
            
            
            diff_pos_i[s]=np.std((max(State)-State))/max(State)
            
            
            # find real bidding bidders
            num_i[s]  =int(sum((State>0)*1))
            pub_info[s,2]=num_i[s]
            

        
        data_dict={
                'data_act':data_act,
                'pub_info':pub_info,
                'data_state':data_state,
                'data_bid_freq':data_bid_freq,
                'data_win':data_win,
                'freq_div_i':freq_div_i,
                'num_i':num_i,
                'diff_i':diff_i,
                'freq_dis_i':freq_dis_i,
                "freq_i":freq_i,
                'diff_pos_i':diff_pos_i,
                }
        

        return data_struct(data_dict)
    
            
class data_struct:
    def __init__(self,data_dict):
        self.data_dict=data_dict
        
    @property 
    def data_act(self):
        '''
        return data_act
        '''
        return self.data_dict['data_act']

    @property 
    def pub_info(self):
        '''
        return pub_info
        '''
        return self.data_dict['pub_info']

    @property 
    def data_state(self):
        '''
        return data_state
        '''
        return self.data_dict['data_state']

    @property 
    def data_bid_freq(self):
        '''
        return data_bid_freq
        '''
        return self.data_dict['data_bid_freq']

    @property 
    def data_win(self):
        '''
        return data_win
        '''
        return self.data_dict['data_win']
    
    @property 
    def data_win2(self):
        '''
        return data_win2
        '''
        return np.square(self.data_dict['data_win']-np.mean(self.data_dict['data_win']))

    @property 
    def freq_div_i(self):
        '''
        return freq_div_i
        '''
        return self.data_dict['freq_div_i']


    @property 
    def freq_div_i2(self):
        '''
        return freq_div_i2
        '''
        return np.square(self.data_dict['freq_div_i']-np.mean(self.data_dict['freq_div_i']))

    @property 
    def num_i(self):
        '''
        return num_i
        '''
        return self.data_dict['num_i']
    
    
    @property 
    def num_i2(self):
        '''
        return num_i2 
        '''
        return np.square(self.data_dict['num_i']-np.mean(self.data_dict['num_i']))
        
    
    @property 
    def diff_i(self):
        '''
        return diff_i
        '''
        return self.data_dict['diff_i']
        
    @property 
    def diff_i2(self):
        '''
        return diff_i2
        '''
        return np.square(self.data_dict['diff_i']-np.mean(self.data_dict['diff_i']))
    
    @property
    def diff_pos_i(self):
        '''
        return freq_i
        '''
        return self.data_dict['diff_pos_i']
    
    @property
    def diff_pos_i2(self):
        '''
        return freq_i2
        '''
        return np.square(self.data_dict['diff_pos_i']-np.mean(self.data_dict['diff_pos_i']))

    
    @property
    def freq_dis_i(self):
        '''
        return freq_distance_i
        '''
        return self.data_dict['freq_dis_i']
    
    @property
    def freq_dis_i2(self):
        '''
        return freq_distance_i2
        '''
        return np.square(self.data_dict['freq_dis_i']-np.mean(self.data_dict['freq_dis_i']))
    
    @property
    def freq_i(self):
        '''
        return freq_i
        '''
        return self.data_dict['freq_i']
    
    @property
    def freq_i2(self):
        '''
        return freq_i2
        '''
        return np.square(self.data_dict['freq_i']-np.mean(self.data_dict['freq_i']))