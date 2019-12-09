#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 18:24:37 2019

@author: malrawi



input1 = torch.randn(5, 7)
input2 = torch.randn(5, 7)


dist_mat = cdist(input1.numpy(), input2.numpy(), metric='cosine')
print(dist_mat)

xx= cosine_distance_torch(input1, input2, 2.4)
print(xx)
yy = cosine_similarity_n_space(input1.numpy(), input2.numpy(), dist_batch_size=10000)
print(yy)

https://stackoverflow.com/questions/40900608/cosine-similarity-on-large-sparse-matrix-with-numpy



"""

import torch

def cosine_distance_torch(x1, x2=None, eps=1e-8):
    x2 = x1 if x2 is None else x2
    w1 = x1.norm(p=2, dim=1, keepdim=True)
    w2 = w1 if x2 is x1 else x2.norm(p=2, dim=1, keepdim=True)
    return 1 - torch.mm(x1, x2.t()) / (w1 * w2.t()).clamp(min=eps)


def cosine_similarity_n_space(m1=None, m2=None, dist_batch_size=100):
    NoneType = type(None)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    if type(m1) != torch.Tensor: # only numpy conversion supported
        m1 = torch.from_numpy(m1).float()
    if type(m2) != torch.Tensor and type(m2)!=NoneType:
        m2 = torch.from_numpy(m2).float() # m2 could be None
        
    m2 = m1 if m2 is None else m2
    assert m1.shape[1] == m2.shape[1]
    
    result = torch.zeros([1, m2.shape[0]])
    
    for row_i in range(0, int(m1.shape[0] / dist_batch_size) + 1):
        start = row_i * dist_batch_size
        end = min([(row_i + 1) * dist_batch_size, m1.shape[0]])
        if end <= start:
            break # cause I'm too lazy to elegantly handle edge cases
        rows = m1[start: end] 
        # sim = cosine_similarity(rows, m2) # rows is O(1) size        
        sim = cosine_distance_torch(rows.to(device), m2.to(device))
        
        result = torch.cat( (result, sim.cpu()), 0)
        
               
    result = result[1:, :] # deleting the first row, as it was used for setting the size only
    del sim
    return result.numpy() # return 1 - ret # should be used with sklearn cosine_similarity

