#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Setup
import scipy
from scipy import special 
import math

N= 32 # Number of Teams at event 
R= range(1, 33, 1) # Event Rank

P = 0 #Pick order in alliance selection from 1 to 16, where 1 is the first pick of the first aliance and 16 is the second pick of the first alliance. 
#If Allaince Captain or not picked set P to 0. P can aproximated by R-6 for R>8, but this can be higly inaccurate 
F = 0 #Elim Finish from 1st through 4th or lower or set to 0 if N/A

W = 0# How many 5 point awards won, if ten point award enter 2 and 1.6 for 8 point awards


# In[2]:


#Math and Logic
a= 1.07 # Constant, do not change
A = 0# Alliance Selction points, starts at 0, do not change
E = 0# Elimination points, starts at 0, do not change
if F == 1 or F == 2:
    E = (3-f)*10
if F == 3:
    E = 13
if F == 4:
    E = 7
if F > 5 or F == 0:
    E = 0   


# In[3]:


#print block
if E > 0 and P == 0:
    print ("Currently not accounting for back up teams as that is not a valid strategy, please set P to a non zero value")
print ("Assuming ",N," Teams"," Pick Order =",P, ",Elim finish=",F,",and equivalent of", W,"'5' points awards won.\n", "The only variable that changes is qualification rank.\n","This is ovbiously innacurate for alliance capatains outside of their specifc rank.")
for r in R:
    if r <= 8:
        P = 0
        A = 17-r

        
    if r >8 and P > 0:
        A = 17-P
       
        
    if r > 8 and P == 0:
        A = 0

    InvERF = scipy.special.erfinv((N-(2*r)+2)/(a*N)) #Table 11-5 math
    Clause2 = (10/scipy.special.erfinv(1/a)) #Table 11-5 math
    DRP = math.ceil(InvERF*Clause2+12)+A#+E+(5*W) #Table 11-5 math
    
    print ("For rank=",r,",DRP=",DRP)


# In[ ]:




