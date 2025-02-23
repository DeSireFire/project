# -*- coding: utf-8 -*-
"""
Created on Sun Oct 14 20:45:58 2018

@author: xiaofeima
This script is aimed at analyzing the priority people behavior.
The objetive here is to find some evidence for asymmetric information

"""


# package 
import sqlite3
import pandas as pd
import numpy as np
import time, re,copy
import matplotlib.pyplot as plt
from scipy import stats

#load the data
store_path="E:/auction/"

graph_path = "E:/Dropbox/academic/ideas/IO field/justice auction/draft/pic/"

con = sqlite3.connect(store_path+"auction_info_house.sqlite")

PATH_output="E:/github/Project/economics/auction/test/"

df_1_s = pd.read_csv(PATH_output+"sample1_df.csv", sep='\t', encoding='utf-8')
df_2_s = pd.read_csv(PATH_output+"sample2_df.csv", sep='\t', encoding='utf-8')
df_1_s['p_ratio']=df_1_s['win_bid']/df_1_s['reserve_price']
df_2_s['p_ratio']=df_2_s['win_bid']/df_2_s['reserve_price']

df_1_s['freq_norm'] = (df_1_s['bid_freq']-df_1_s['bid_freq'].mean())/df_1_s['bid_freq'].std()
df_2_s['freq_norm'] = (df_2_s['bid_freq']-df_1_s['bid_freq'].mean())/df_2_s['bid_freq'].std()

df_1_s['dist_volatility'] = (df_1_s['dist_high']-df_1_s['dist_high'].mean())/df_1_s['dist_high'].std()
df_2_s['dist_volatility'] = (df_2_s['dist_high']-df_2_s['dist_high'].mean())/df_2_s['dist_high'].std()


# get rid of extreme case 
tail1=df_1_s['num_bidder'].quantile(.99)
df_1_s=df_1_s.loc[df_1_s['num_bidder']<20,]

tail1=df_1_s['resev_proxy'].quantile(.99)
df_1_s=df_1_s.loc[df_1_s['resev_proxy']<tail1,]

tail1=df_1_s['win_bid'].quantile(.99)
df_1_s=df_1_s.loc[df_1_s['win_bid']<tail1,]



# get the distribution between priority people and non-priority people
pri_group1 = df_1_s.groupby("priority_people")
pri_group2 = df_2_s.groupby("priority_people")

# graph for number of bidder
plt.subplot(121) 
graph_1=pri_group1.num_bidder.plot.density(xlim=[0,30],legend=True)
plt.margins(0.02)
plt.xlabel("number of bidder")
plt.title("First Time Auction")
plt.grid(True)
# save the graph independent
#fig=graph_1[0].get_figure()
#fig.savefig(graph_path+"priori_numbidder_1.png")


plt.subplot(122) 
graph_2=pri_group2.num_bidder.plot.density(ind=[1,2,3,4,5,6,7,8,9,10],legend=True)
plt.xlabel("number of bidder")
plt.title("Second  Time Auction")
plt.margins(0.02)
plt.grid(True)
plt.subplots_adjust(bottom=0.25, top=0.75,hspace=0.2,wspace=0.5,left=0.05, right=1.2)
plt.show()




'''
first time auction : priority vs no priority 
number of bidders ECDF and PDF
'''
plt.subplot(121) 
xx1 = np.sort(pri_group1.get_group(0)['num_bidder'])
yy1 = np.arange(1,len(xx1)+1)/len(xx1)
xx2 = np.sort(pri_group1.get_group(1)['num_bidder'])
yy2 = np.arange(1,len(xx2)+1)/len(xx2)
_ = plt.plot(xx1,yy1,marker=".", linestyle = "none",label = "without priority")
_ = plt.plot(xx2,yy2,marker=".", linestyle = "none",label = "with priority")
_ = plt.xlabel("number of bidder")
_ = plt.ylabel("Empirical CDF")
_ = plt.title("Number of bidder")
_ = plt.margins(0.02)
_ = plt.legend(loc='upper left')
_ = plt.grid(True)


plt.subplot(122) 
x1 = np.arange(1, 30, 1)
density1 = stats.kde.gaussian_kde(xx1)
x2 = np.arange(1, 18, 1)
density2 = stats.kde.gaussian_kde(xx2)
__ = plt.plot(x1,density1(x1),label = "without priority")
__ = plt.plot(x2,density2(x2),label = "with priority")
_ = plt.xlabel("number of bidder")
_ = plt.ylabel("Density")
_ = plt.legend(loc='upper right')
_ = plt.margins(0.02)
_ = plt.grid(True)
plt.subplots_adjust(bottom=0.25, top=0.75,hspace=0.2,wspace=0.5,left=0.05, right=1.2)
plt.show()
# save the graph independent
#fig=graph_2[0].get_figure()
#fig.savefig(graph_path+"priori_numbidder_2.png")


'''
----------------------------------------------------
'''

# graph for reserve proxy
plt.subplot(121) 
graph_1=pri_group1.p_ratio.plot.density(xlim=[0,2],legend=True)
plt.margins(0.02)
plt.xlabel("winning price / reserve price")
plt.title("First Time Auction")
plt.grid(True)
# save the graph independent
#fig=graph_1[0].get_figure()
#fig.savefig(graph_path+"priori_rese_proxy_1.png")

plt.subplot(122)
graph_2=pri_group2.p_ratio.plot.density(xlim=[0,2],legend=True)
plt.xlabel("winning price / reserve price")
plt.title("Second  Time Auction")
plt.margins(0.02)
plt.grid(True)
plt.subplots_adjust(bottom=0.25, top=0.75,hspace=0.2,wspace=0.5,left=0.05, right=1.2)
plt.show()
# save the graph independent
#fig=graph_2[0].get_figure()
#fig.savefig(graph_path+"priori_rese_proxy_2.png")


# graph for bidding spread
plt.subplot(121) 
graph_1=pri_group1.dist_high.plot.density(xlim=[0,100],legend=True)
plt.title("Bid Spread Without Normalization")
plt.margins(0.02)
plt.grid(True)
# save the graph independent
#fig=graph_1[0].get_figure()
#fig.savefig(graph_path+"priori_bid_spread.png")

#plt.subplot(122)
#graph_1=pri_group1.dist_volatility.plot.density(xlim=[-2,3],legend=True)
#plt.title("Bid Spread With Normalization")
#plt.margins(0.02)
#plt.grid(True)

plt.subplot(122)
xx1 = np.sort(pri_group1.get_group(0)['dist_volatility'])
density1 = stats.kde.gaussian_kde(xx1)
xx2 = np.sort(pri_group1.get_group(1)['dist_volatility'])
density2 = stats.kde.gaussian_kde(xx2)
x1 = np.arange(-2, 2, 0.01)
x2 = np.arange(-2, 2, 0.01)
_ = plt.plot(x1,density1(x1),label = "without priority")
_ = plt.plot(x2,density2(x2),label = "with priority")
#_ = plt.xlabel("dist_volatility")
plt.title("Bid Spread With Normalization")
plt.margins(0.02)
_ = plt.legend(loc='upper right')
plt.grid(True)




# save the graph independent
#fig=graph_1[0].get_figure()
#fig.savefig(graph_path+"priori_bid_spread.png")

plt.subplots_adjust(bottom=0.25, top=0.75,hspace=0.2,wspace=0.5,left=0.05, right=1.2)
plt.show()


'''
first time auction : priority vs no priority 
reserve proxy + winning bid 

'''
plt.subplot(121) 
xx1 = np.sort(pri_group1.get_group(0)['p_ratio'])
density1 = stats.kde.gaussian_kde(xx1)
xx2 = np.sort(pri_group1.get_group(1)['p_ratio'])
density2 = stats.kde.gaussian_kde(xx2)

x1 = np.arange(0.75, 3, 0.01)
x2 = np.arange(0.75, 3, 0.01)

_ = plt.plot(x1,density1(x1),label = "without priority")
_ = plt.plot(x2,density2(x2),label = "with priority")
_ = plt.xlabel("winning price / reserve price")
_ = plt.ylabel("Density")
_ = plt.margins(0.02)
_ = plt.legend(loc='upper right')
_ = plt.grid(True)


plt.subplot(122) 
xx1 = np.sort(pri_group1.get_group(0)['resev_proxy'])
density1 = stats.kde.gaussian_kde(xx1)
xx2 = np.sort(pri_group1.get_group(1)['resev_proxy'])
density2 = stats.kde.gaussian_kde(xx2)


x1 = np.arange(0, xx1.max(), 0.01)
x2 = np.arange(0, xx2.max(), 0.01)

__ = plt.plot(x1,density1(x1),label = "without priority")
__ = plt.plot(x2,density2(x2),label = "with priority")
_ = plt.xlabel("winning price / reserve price -1 ")
_ = plt.ylabel("Density")
_ = plt.legend(loc='upper right')
plt.title("Winning Premium")
_ = plt.margins(0.02)
_ = plt.grid(True)
plt.subplots_adjust(bottom=0.25, top=0.75,hspace=0.2,wspace=0.5,left=0.05, right=1.2)
plt.show()


'''
------------------------------------------------------
'''

# bid_freq 
plt.subplot(121) 
graph_1=pri_group1.bid_freq.plot.density(xlim=[0,200],legend=True)
plt.title("Bid Frequency Without Normalization")
plt.margins(0.02)
plt.grid(True)


plt.subplot(122)

xx1 = np.sort(pri_group1.get_group(0)['freq_norm'])
density1 = stats.kde.gaussian_kde(xx1)
xx2 = np.sort(pri_group1.get_group(1)['freq_norm'])
density2 = stats.kde.gaussian_kde(xx2)

x1 = np.arange(-1, 1, 0.01)
x2 = np.arange(-1, 1, 0.01)

__ = plt.plot(x1,density1(x1),label = "without priority")
__ = plt.plot(x2,density2(x2),label = "with priority")
_ = plt.ylabel("Density")
_ = plt.legend(loc='upper right')
#graph_1=pri_group1.freq_norm.plot.density(xlim=[0,200],legend=True)
plt.title("Bid Frequency With Normalization")
#_ = plt.xlabel("normalized bid frequency ")
plt.margins(0.02)
plt.grid(True)
plt.subplots_adjust(bottom=0.25, top=0.75,hspace=0.2,wspace=0.5,left=0.05, right=1.2)
plt.show()

# save the graph independent
#fig=graph_1[0].get_figure()
#fig.savefig(graph_path+"priori_bid_freq.png")





'''
-------------------------------------------------------------------------------
pic2 
-------------------------------------------------------------------------------
'''


'''
# of auctions w.r.t. # of bidders
hist 
and density
density=True or False
'''

group_freq1=df_1_s.groupby(['num_bidder','priority_people'])
max_bin=df_1_s.loc[df_1_s['priority_people']==1,'num_bidder'].max()
bins = np.linspace( min(group_freq1.num_bidder.min()), max_bin, 40)

z1=df_1_s.loc[df_1_s['priority_people']==0,'num_bidder']
z2=df_1_s.loc[df_1_s['priority_people']==1,'num_bidder']

plt.hist((z1,z2),bins,density=True, label=['without priority bidder', 'with priority bidder'])
p=plt.gca()
p.set_xlabel('the number of bidders')
p.set_ylabel('density')
p.set_title("Number of Auctions with/without Prority Bidder")
p.legend()
p.grid(True)


'''
winning price distribution

'''
pri_group1 = df_1_s.groupby("priority_people")
#temp_df=pri_group1.get_group(0)['p_ratio']
#temp_df=np.log(pri_group1.get_group(0)['p_ratio'])
temp_df=pri_group1.get_group(0)
temp_df=temp_df.loc[temp_df['p_res_eva']>.95,'p_ratio']
xx1 = np.sort(temp_df)
density1 = stats.kde.gaussian_kde(xx1)

#temp_df=pri_group1.get_group(1)['p_ratio']
#temp_df=np.log(pri_group1.get_group(1)['p_ratio'])
temp_df=pri_group1.get_group(1)
temp_df=temp_df.loc[temp_df['p_res_eva']<0.95,'p_ratio']
xx2 = np.sort(temp_df)
density2 = stats.kde.gaussian_kde(xx2)

#x1 = np.arange(0.75, 3, 0.01)
#x2 = np.arange(0.75, 3, 0.01)

x1 = np.arange(0.7, 3, 0.01)
x2 = np.arange(0.7, 3, 0.01)


_ = plt.plot(x1,density1(x1),label = "without priority")
_ = plt.plot(x2,density2(x2),label = "with priority")
_ = plt.xlabel("winning price / reserve price")
_ = plt.ylabel("Density")
_ = plt.title("Distribution of Winning Bid with/without Prority Bidder")
_ = plt.margins(0.02)
_ = plt.legend(loc='upper right')
_ = plt.grid(True)



# fix the number of bidders
group_freq1=df_1_s.groupby(['num_bidder','priority_people'])
group_freq2=df_2_s.groupby(['num_bidder','priority_people'])

df1_freq=group_freq1.p_ratio.mean()
df1_temp=group_freq1.bid_freq.count()
df1_temp=df1_temp.rename('num_auction')
df1_freq=pd.concat([df1_freq, df1_temp], axis=1)
df1_freq=df1_freq.reset_index()
df1_freq=df1_freq[df1_freq['num_bidder']<16]
#df1_freq=df1_freq[df1_freq['num_bidder']!=16]

w = 0.3
x1=np.array(df1_freq.loc[df1_freq['priority_people']==0,'num_bidder'])
y1=np.array(df1_freq.loc[df1_freq['priority_people']==0,'p_ratio'])
x2=np.array(df1_freq.loc[df1_freq['priority_people']==1,'num_bidder'])
y2=np.array(df1_freq.loc[df1_freq['priority_people']==1,'p_ratio'])

plt.bar(x1-0.5*w, y1,width=w,align='center',label="with priority bidder")
plt.bar(x2+0.5*w, y2,width=w,align='center',label="without priority bidder")
plt.autoscale(tight=True)
plt.ylim([1,2.4])
plt.xlim([1,25])
plt.ylabel('win bid / reserve price')
plt.title('Average Winning Bid with/without Prority Bidder')
plt.xlabel('the number of bidders')
plt.grid(True)


'''
bidding frequency : 
    fix the number of bidders 
    fix the priority bidders 
    
'''

group_freq1=df_1_s.groupby(['num_bidder','priority_people'])
group_freq2=df_2_s.groupby(['num_bidder','priority_people'])

df1_freq=group_freq1.bid_freq.mean()
df1_temp=group_freq1.bid_freq.count()
df1_temp=df1_temp.rename('num_auction')
df1_freq=pd.concat([df1_freq, df1_temp], axis=1)
df1_freq=df1_freq.reset_index()
df1_freq=df1_freq[df1_freq['num_bidder']<18]
df1_freq=df1_freq[df1_freq['bid_freq']<300]


x1=np.array(df1_freq.loc[df1_freq['priority_people']==0,'num_bidder'])
y1=np.array(df1_freq.loc[df1_freq['priority_people']==0,'bid_freq'])
z1=np.array(df1_freq.loc[df1_freq['priority_people']==0,'num_auction'])
plt.stem(x1,y1,color='#1f77b4')
plt.scatter(x1, y1,color='#1f77b4', s=z1, alpha=1,label='without priority')
#p=plt.gca()
#for i,text in enumerate(z1):
#    p.annotate(text, (x1[i], y1[i]+5))
#p.set_ylim(0, 150)
#p.set_xlabel('auctions given the number of bidders')
#p.set_ylabel('average bidding frequency')
#p.set_title("Average Bidding Frequncy Without Prority Bidder")
#

x2=np.array(df1_freq.loc[df1_freq['priority_people']==1,'num_bidder'])
y2=np.array(df1_freq.loc[df1_freq['priority_people']==1,'bid_freq'])
z2=np.array(df1_freq.loc[df1_freq['priority_people']==1,'num_auction'])
markerline, stemlines, baseline =plt.stem(x2+0.3,y2,markerfmt='')
plt.setp(stemlines, color='#ff7f0e', linewidth=1)
plt.setp(markerline, color='#ff7f0e', linewidth=0)
plt.scatter(x2+0.33, y2,color='#ff7f0e', s=z2, alpha=1,label='with priority')
p=plt.gca()
#for i,text in enumerate(z2):
#    p.annotate(text, (x2[i], y2[i]+4))
p.set_ylim(0, 150)
_ = plt.legend(loc='upper right')
p.set_xlabel('auctions given the number of bidders')
p.set_ylabel('average bidding frequency')
p.set_title("Average Bidding Frequncy With/Without Prority Bidder")
p.grid(True)


'''
winning price w.r.t. number of bidders

'''
tail=df_1_s['bid_freq'].quantile(0.95)
df_1_s=df_1_s[df_1_s['bid_freq']<tail]

df_1_s=df_1_s[df_1_s['num_bidder']<18]

pri_group1 = df_1_s.groupby("priority_people")

xx1 = np.sort(pri_group1.get_group(0)['bid_freq'])
density1 = stats.kde.gaussian_kde(xx1)
xx2 = np.sort(pri_group1.get_group(1)['bid_freq'])
density2 = stats.kde.gaussian_kde(xx2)

# this is for bidding frequency
x1 = np.arange(0, 120, 1)
x2 = np.arange(0, 120, 1)

_ = plt.plot(x1,density1(x1),label = "without priority")
_ = plt.plot(x2,density2(x2),label = "with priority")
_ = plt.xlabel("bidding times")
_ = plt.ylabel("Density")
_ = plt.title("Distribution of Bid Frequency with/without Prority Bidder")
_ = plt.margins(0.02)
_ = plt.legend(loc='upper right')
_ = plt.grid(True)







'''
bidding spread 
average bidding distance among the bidders 

'''
pri_group1 = df_1_s.groupby("priority_people")

xx1 = np.sort(pri_group1.get_group(0)['dist_high'])
tail=np.percentile(xx1,99)
xx1 = xx1[xx1<tail]
density1 = stats.kde.gaussian_kde(xx1)
xx2 = np.sort(pri_group1.get_group(1)['dist_high'])
tail=np.percentile(xx2,99)
xx2 = xx2[xx2<tail]
density2 = stats.kde.gaussian_kde(xx2)


x1 = np.arange(0, 110, 1)
x2 = np.arange(0, 110, 1)



_ = plt.plot(x1,density1(x1),label = "without priority")
_ = plt.plot(x2,density2(x2),label = "with priority")
_ = plt.xlabel("average bidding distance among the bidders ")
_ = plt.ylabel("density")
_ = plt.title("Distribution of Bidding Distance with/without Prority Bidder")
_ = plt.margins(0.02)
_ = plt.legend(loc='upper right')
_ = plt.grid(True)


