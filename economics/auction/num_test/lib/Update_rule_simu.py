# -*- coding: utf-8 -*-
"""
Created on Sat Feb 09 10:48:00 2019

@author: xiaofeima

Use a new bidding function scripts to do the simulation

Because it is the simulation, I do not need to restrict the bidding price vector as some presumed 
finite vector. 
I can just use the ladder*t + reserve price to represent the bidding price  

### there could be three ways to update the expected value in each period 
1. only have lower bound 
2. add the upper bound -> treat next period as upper bound
3. add the upper bound -> treat bidder i's private signal as upper bound 

should add the incentive constraint for the informed bidders

"""

import numpy as np
from numpy.linalg import inv
from scipy.stats import norm
import warnings
import math,copy
from scipy.optimize import minimize
import scipy.stats as ss

class Update_rule:
    
    def __init__(self,para,res=0,rule_flag = 0):
        self.para      = para
        self.N         = para.N
        self.res       = res
        self.comm_var  = para.comm_var
        self.comm_mu   = para.comm_mu
        self.rule_flag = rule_flag

    def setup_para(self,i_id):
        '''
        Set up the parameters for the each bidder
        '''
        self.xi_mu        = self.para.xi_mu[i_id]
        self.xi_sigma2    = self.para.xi_sigma2[i_id] 
        self.vi_mu        = self.para.vi_mu[i_id]
        self.vi_sigma2    = self.para.vi_sigma2[i_id]
        self.MU           = self.para.MU[i_id]
        self.SIGMA2       = self.para.SIGMA2[i_id]
        self.xi_rival_mu  = self.para.xi_rival_mu[i_id]
        self.xi_rival_sigma2 = self.para.xi_rival_sigma2[i_id]
        self.vi_rival_mu     = self.para.vi_rival_mu[i_id]
        self.vi_rival_sigma2 = self.para.vi_rival_sigma2[i_id]   
        self.cov_istar       = self.para.cov_istar[i_id]

        # dimension
        #             
        self.MU              = self.MU.reshape(self.N,1)
        self.xi_rival_mu     = self.xi_rival_mu.reshape(self.N-1,1)
        self.xi_rival_sigma2 = self.xi_rival_sigma2.reshape(self.N-1,1)
        self.vi_rival_mu     = self.vi_rival_mu.reshape(self.N-1,1)
        self.vi_rival_sigma2 = self.vi_rival_sigma2.reshape(self.N-1,1)
        self.cov_istar       = self.cov_istar.reshape(self.N,1) 


    def bound(self, p_low):
        # still I have to calculate the signal recurisively
        ## all the rivals bidding price is known
        ## but first of all, I have to reorder the "dropout price" from second to last (ignore the first)
        ## the function who invoke the bound already define the i_id
        
        pre_MU    =self.MU.flatten()
        pre_SIGMA2=np.diag(self.SIGMA2)

        # Reorder p_k from second to last 
        ord_ind2=np.argsort(p_low[1:])[::-1]

        ori_ind=ss.rankdata(p_low[1:])
        ori_ind=ori_ind-1
        ori_ind=ori_ind.astype(int)

        p_k=np.append(p_low[0],p_low[1:][ord_ind2])
        p_k=p_k.reshape(p_k.size,1)

        # MU and SIGMA2
        post_SIGMA2=np.append(pre_SIGMA2[0],pre_SIGMA2[1:][ord_ind2])
        post_SIGMA2=np.ones([self.N,self.N])*self.comm_var + np.diag(post_SIGMA2)-np.eye(self.N)*self.comm_var
        Sigma_inv = inv(post_SIGMA2)
        MU = np.append(pre_MU[0],pre_MU[1:][ord_ind2])
        MU = MU.reshape(MU.size,1)

        # mu_k
        x_drop=np.zeros(self.N)

        # vi xi
        for k in range(self.N):
             
            mu_k = np.append(self.vi_mu, self.vi_rival_mu[ord_ind2])
            mu_k = mu_k[0:self.N-k]
            mu_k=mu_k.reshape(mu_k.size,1)
            
            l_k  = np.ones((self.N-k,1))
            
            Gamma_k = np.append(self.vi_sigma2 , self.vi_rival_sigma2[ord_ind2])
            Gamma_k = Gamma_k[0:self.N-k]
            Gamma_k = Gamma_k.reshape(Gamma_k.size,1)
            
            
            Delta_k =np.diag(np.append(self.vi_sigma2, self.vi_rival_sigma2[ord_ind2])-self.comm_var)+np.ones((self.N,self.N))*self.comm_var
            Delta_k=Delta_k[:,0:self.N-k].T
            
            
            Sigma_inv_k1 = Sigma_inv[0:self.N-k,:] # N-1+1 all the rest of the 


            AA_k = inv(Delta_k @ Sigma_inv_k1.T) @ l_k
            temp_diag=np.diag(Delta_k @ Sigma_inv @ Delta_k.T)
            temp_diag=temp_diag.reshape(temp_diag.size,1)
            
            CC_k = 0.5*inv(Delta_k @ Sigma_inv_k1.T) @ (Gamma_k - temp_diag + 2*mu_k -2* Delta_k @ Sigma_inv @ MU)

            if k>0:
                Sigma_inv_k2 = Sigma_inv[self.N-k:,:]
                DD_k = inv(Delta_k @ (Sigma_inv_k1.T)) @ (Delta_k @ (Sigma_inv_k2.T))
                x_d = x_drop[self.N-k:]
            else:
                DD_k = np.zeros([1,1])
                x_d = 0
            x_drop[self.N-k-1] = AA_k[-1]*np.log(p_k[self.N-k-1]) - np.dot( DD_k[-1,:],  x_d) - CC_k[-1]
        
        x_drop=np.append(x_drop[0],x_drop[1:][::-1][ori_ind])
        return x_drop.reshape(1,x_drop.size)


    def bound_simple(self, p_low):
        pre_MU    =self.MU.flatten()
        pre_SIGMA2=np.diag(self.SIGMA2)

        x_drop=np.zeros(self.N)
        # Reorder p_k from second to last 
        ord_ind2=np.argsort(p_low[1:])[::-1]

        ori_ind=ss.rankdata(p_low[1:])
        ori_ind=ori_ind-1
        ori_ind=ori_ind.astype(int)

        p_k=np.append(p_low[0],p_low[1:][ord_ind2])
        p_k=p_k.reshape(p_k.size,1)

        # MU and SIGMA2
        post_SIGMA2=np.append(pre_SIGMA2[0],pre_SIGMA2[1:][ord_ind2])
        post_SIGMA2=np.ones([self.N,self.N])*self.comm_var + np.diag(post_SIGMA2)-np.eye(self.N)*self.comm_var
        Sigma_inv = inv(post_SIGMA2)
        MU = np.append(pre_MU[0],pre_MU[1:][ord_ind2])
        MU = MU.reshape(MU.size,1)

        # mu_k
        
        mu_k = np.append(self.vi_mu, self.vi_rival_mu[ord_ind2])
        mu_k=mu_k.reshape(mu_k.size,1)
        
        l_k  = np.ones((self.N,1))
        
        Gamma_k = np.append(self.vi_sigma2, self.vi_rival_sigma2[ord_ind2])
        Gamma_k = Gamma_k.reshape(Gamma_k.size,1)
        
        Delta_k =np.diag(np.append(self.vi_sigma2, self.vi_rival_sigma2[ord_ind2])-self.comm_var)+np.ones((self.N,self.N))*self.comm_var
        
        AA_k = inv(Delta_k @ Sigma_inv.T) @ l_k
        temp_diag=np.diag(Delta_k @ Sigma_inv @ Delta_k.T)
        temp_diag=temp_diag.reshape(temp_diag.size,1)
        CC_k = 0.5*inv(Delta_k @ (Sigma_inv.T)) @ (Gamma_k-temp_diag + 2*mu_k -2* Delta_k@Sigma_inv@MU)

        x_drop = AA_k*np.log(p_k) - CC_k

        x_drop=np.append(x_drop[0],x_drop[1:][::-1][ori_ind])
        return x_drop

    def entry_threshold(self,res):
        # initial point for uninformed 
        mu_k = np.append(self.vi_mu, self.vi_rival_mu)
        mu_k=mu_k.reshape(mu_k.size,1)
        
        l_k  = np.ones((self.N,1))
        
        Gamma_k = np.append(self.vi_sigma2, self.vi_rival_sigma2)
        Gamma_k = Gamma_k.reshape(Gamma_k.size,1)
        
        Delta_k =np.diag(np.append(self.vi_sigma2, self.vi_rival_sigma2)-self.comm_var)+np.ones((self.N,self.N))*self.comm_var
        
        Sigma_inv = inv(self.SIGMA2)
        # Sigma_inv_k1 = Sigma_inv[0:self.N,:] # N-1+1 all the rest of the 
        MU        = self.MU
        AA_k = inv(Delta_k @ Sigma_inv.T) @ l_k
        temp_diag=np.diag(Delta_k @ Sigma_inv @ Delta_k.T)
        temp_diag=temp_diag.reshape(temp_diag.size,1)
        CC_k = 0.5*inv(Delta_k @ (Sigma_inv.T)) @ (Gamma_k-temp_diag + 2*mu_k -2* Delta_k@Sigma_inv@MU)

        x_drop = AA_k*np.log(res) - CC_k

        return x_drop.reshape(1,x_drop.size)

    def entry_threshold_info(self,res,info_index):
        x_ini=max(self.entry_threshold(res))
        X_r_est=minimize(self.thres_func,[x_ini,x_ini],args=(res,info_index))
        return X_r_est.x
    
    def thres_func(self,X_r,log_res,info_index):

        x_s=X_r[0]*np.ones([self.N,1])
        x_s[info_index]=X_r[1]

        # feasibility constraint
        eq1 = X_r[1] - log_res

        # feasibility constraint 
        mu_k = self.vi_mu
        # simga_i^2
        Gamma_k = self.vi_sigma2
        
        # cov i  Delta
        Delta_k =self.comm_var * np.ones(self.N)
        Delta_k[0] = self.vi_sigma2
        Delta_k=Delta_k.reshape(self.N,1)
        
        # sigma_inv
        Sigma_inv = inv(self.SIGMA2)        
        Sigma_inv_k1 = Sigma_inv[0:self.N,:]
        

        # the main 
        AA_k = Delta_k.T @ Sigma_inv_k1.T
        CC_k = 0.5*  (Gamma_k - Delta_k.T @ Sigma_inv @ Delta_k) + mu_k - Delta_k.T @Sigma_inv@self.MU
                    
        E_x0 = (AA_k @ x_s  + CC_k)
        # feasibliity constraint
        eq0  = E_x0 - log_res

        # incentive constraint 
        eq2 = X_r[1] - E_x0

        return (eq2 < 0)*eq2**2*10 + (eq1<0)*eq1**2 + (eq0)*eq0**2 



    def entry_simu_up(self,x_bar,up):
        # Constat part 
        Sigma_inv = inv(self.SIGMA2)
        COV_xvi   = self.cov_istar

        CC_i = self.vi_mu - self.MU.T @ Sigma_inv @ COV_xvi
        CC_i = CC_i.flatten()
        AA_coef =  Sigma_inv @ COV_xvi
        
        AA_i = AA_coef[0]
        AA_j = AA_coef[1:]
        Mu   = self.xi_rival_mu.flatten()
        Sigma= self.xi_rival_sigma2.flatten()**0.5
        
        a   = (x_bar[:self.N-1]-Mu)/(Sigma)

        X_j = Mu + Sigma * norm.pdf(a)/(1-norm.pdf(a))
        E_j = sum(AA_j.flatten()*X_j)

        # conditional variance var(v_i | x_i , x_j , x_q)
        # sigma_vi^2 , cov_xi_vi == sigma_vi^2 
        # at most for the variance 
        var_update = self.vi_sigma2 -COV_xvi.T @  Sigma_inv @  COV_xvi

        x_up=(1 / AA_i)* ( np.log(up) - (E_j+ CC_i+0.5*var_update.flatten()) ) 
        return x_up

    def real_info_bid(self,xi,bid_price):
        E_win_revenue = xi - np.log(bid_price)
        Pure_value    = np.exp(xi)
        flag = 1*(E_win_revenue>0)

        return [Pure_value,E_win_revenue,flag]

    def real_bid(self,xi,state_p,bid_price,no_flag,i_id):
        x_j_lower = self.bound_simple(state_p)
        x_j_lower = x_j_lower.flatten()[1:]

        Sigma_inv = inv(self.SIGMA2)

        # COV_xvi=np.append(self.vi_sigma2,np.ones(self.N-1)*self.comm_var) # old and possibly wrong implementation
        COV_xvi=self.cov_istar

        CC_i = self.vi_mu - self.MU.T @ Sigma_inv @ COV_xvi
        
        AA_coef =  Sigma_inv @ COV_xvi
        
        AA_i = AA_coef[0]
        AA_j = AA_coef[1:]

        # potential upper bound of the rivals
        if self.rule_flag ==0:
            x_j_upper = 5*np.ones(self.N-1)
        else :
            x_j_upper = self.bound_simple(bid_price)
            x_j_upper = x_j_upper.flatten()[1:]
            if self.rule_flag ==2:
                x_j_upper = ( 1*( x_j_lower < xi*np.ones(self.N-1) ) ) * xi + ( 1*( xi*np.ones(self.N-1) <= x_j_lower))* 5

        # prepare for the winning bid expectation : take expectation on x_j 
        # up + lower of the rivals
        try:
            E_j=AA_j.flatten()*self.truc_x(self.xi_rival_mu.flatten(),self.xi_rival_sigma2.flatten(),x_j_lower.flatten(),x_j_upper)
            E_j=np.sum(E_j*no_flag) 
        except Exception as e:
            print(e)            
            print(x_j_lower)
            print(x_j_upper)
            print('-------------------------')

        # conditional variance var(v_i | x_i , x_j , x_q)
        # sigma_vi^2 , cov_xi_vi == sigma_vi^2 
        # var_update = self.vi_sigma2 -2*AA_i*self.vi_sigma2 + AA_i*self.xi_sigma2*AA_i + E_j**2
        # modify the conditional variancce, a basic criterion is that conditional variance must be less than vi_sigma2 
        # I think I can just use the simple conditional variance formulat        
        var_update = self.vi_sigma2 - COV_xvi.T @  Sigma_inv @  COV_xvi

        # constant part 
        E_const = CC_i+0.5*var_update
        
        # total expected value
        try:
            E_win_revenue=E_j+E_const  + AA_i*xi - np.log(bid_price)
            assert not np.prod(np.iscomplex(E_win_revenue.flatten())), 'complex occurs!'
        except Exception as e:
            print('find the complex')
            print(E_win_revenue)
            print(var_update)
            print(x_j_lower)
            print(x_j_upper)
            print(E_j,E_const)
            print(AA_i,xi)
            print(bid_price)

            input('wait')
        Pure_value = np.exp(E_j+E_const + AA_i*xi) 
        
        flag = int(1*(E_win_revenue>0))
        # return pure value E_win and flag
        return [Pure_value.flatten(),E_win_revenue.flatten(),flag]

    # this can support vectorize
    def truc_x(self,Mu,Sigma,lower,upper):
        Sigma=Sigma**0.5
        
        a = (lower-Mu)/(Sigma)
        b = (upper-Mu)/(Sigma)
        
        temp_de = norm.cdf(b) - norm.cdf(a)+10**(-20)
        temp_no = norm.pdf(a) - norm.pdf(b)
        result = Mu+Sigma*(temp_no / temp_de)

        # if sum(upper) == -1:
        #     result = Mu + Sigma * norm.pdf( a)/(1-norm.pdf( a))
        #     # result = truncate(pd,lower,Inf);         
        # else:
        #     if lower == -1:
        #         result = Mu-Sigma*norm.pdf(b)/(1-norm.cdf(b))
        #     else:
        #         result = Mu+Sigma*(norm.pdf(a) - norm.pdf(b) ) /(norm.cdf(b) - norm.cdf(a))             
            
        return result


    def get_exp(self, x_s):

        # signal
        x_s = x_s.reshape(x_s.size,1)
        # info_struct=np.concatenate((self.xi_rival_mu,self.xi_rival_sigma2,self.vi_rival_mu,self.vi_rival_sigma2),axis=1)
        k=0
        # mu 
        mu_k = np.append(self.vi_mu, self.vi_rival_mu)
        mu_k = mu_k[0:self.N]
        mu_k=mu_k.reshape(mu_k.size,1)
        # l
        l_k  = np.ones((self.N,1))
        # gamma
        Gamma_k = np.append(self.vi_sigma2, self.vi_rival_sigma2)
        Gamma_k = Gamma_k[0:self.N]
        Gamma_k = Gamma_k.reshape(Gamma_k.size,1)
        
        # Delta
        Delta_k =self.vi_sigma2 * np.eye(self.N)+np.ones((self.N,self.N)) * self.comm_var - np.eye(self.N) * self.comm_var  
        Delta_k=Delta_k[:,0:self.N].T
        
        # sigma_inv
        Sigma_inv = inv(self.SIGMA2)        
        Sigma_inv_k1 = Sigma_inv[0:self.N,:]
            
        # the main 
        # AA_k = inv(Delta_k @ Sigma_inv_k1.T) @ l_k
        temp_diag=np.diag(Delta_k @ Sigma_inv @ Delta_k.T)
        temp_diag=temp_diag.reshape(temp_diag.size,1)
        CC_k = 0.5*  (Gamma_k-temp_diag + 2*mu_k -2* Delta_k@Sigma_inv@self.MU)
        AA_k = Delta_k.T @ Sigma_inv_k1.T                
        drop_price= np.exp(AA_k @ x_s  + CC_k)        

        drop_price=drop_price.flatten()  
        return drop_price

    

    '''
    HS replication
    '''

    def get_HS_drop_p(self, x_s):

        # signal
        x_s = x_s.reshape(x_s.size,1)
        # info_struct=np.concatenate((self.xi_rival_mu,self.xi_rival_sigma2,self.vi_rival_mu,self.vi_rival_sigma2),axis=1)
        # use 9 in Hong and Shum 2003
        x_drop=np.array([])
        drop_price_v=[]
        drop_price_round=[]
        for k in range(0,self.N):
            
            # mu_i 
            mu_k = self.vi_mu

            # simga_i^2
            Gamma_k = self.vi_sigma2
            

            # cov i  Delta
            Delta_k =self.comm_var * np.ones(self.N)
            Delta_k[self.N - 1 -k] = self.vi_sigma2
            Delta_k=Delta_k.reshape(self.N,1)
            
            # sigma_inv
            Sigma_inv = inv(self.SIGMA2)        
            Sigma_inv_k1 = Sigma_inv[0:self.N-k,:]
            

            # the main 
            AA_k = Delta_k.T @ Sigma_inv_k1.T
            CC_k = 0.5*  (Gamma_k - Delta_k.T @ Sigma_inv @ Delta_k) + mu_k - Delta_k.T @Sigma_inv@self.MU
                        
            if k>0:
                Sigma_inv_k2 = Sigma_inv[self.N-k:,:] 
                DD_k = (Delta_k.T @ (Sigma_inv_k2.T))
                drop_price= np.exp( AA_k @ x_s[:self.N - k] +DD_k @ x_drop +CC_k)
            else:
                
                drop_price= np.exp(AA_k @ x_s  + CC_k)

            x_drop=np.append(x_s[self.N-1 - k],x_drop)
            x_drop=x_drop.reshape(x_drop.size,1)
            drop_price=drop_price.flatten()
            drop_price_v=np.append(drop_price[-1],drop_price_v)
        
        return drop_price_v