# -*- coding: utf-8 -*-
"""
Created on Sat Mar 23 16:46:54 2024

@author: Yvonne
"""
from prob_model import GaussianModel
from data import Data
from sd_bocpd import SDBocpd,Hazard
    
mean0      = 0    # The prior mean on the mean parameter.
var0       = 3000000    # The prior variance for mean parameter.
varx       = 3000000    # The known variance of the data.
init_var   = 3000000
init_cor   = 0.1
parameters = [0, 0.01, 0.9, init_cor, 10000000]

# mean0      = 0    # The prior mean on the mean parameter.
# var0       = 1    # The prior variance for mean parameter.
# varx       = 1    # The known variance of the data.
# init_var   = 1
# init_cor   = 0.1
# parameters = [0, 0.01, 0.9, init_cor, 1]
d          = 1/2
q          = 0 #the sd-bocpd model
file_name  = "AAPL_2012-06-21_aggr_180.csv"

data = Data(data_type =  "real",file_name  = "AAPL_2012-06-21_aggr_180.csv")
final_data = data.update_data()
# print(final_cps)
T = len(final_data)
hazard = Hazard(T,1/100)

model  = GaussianModel(mean0, var0, varx, parameters,q, init_cor)

sdb = SDBocpd(T,d,q)
run_length_posterior, most_likely_cps = sdb.bocpd(final_data, model, hazard)
 