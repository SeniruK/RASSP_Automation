# -*- coding: utf-8 -*-
"""
Created on Mon Mar  1 13:54:15 2021

@author: ry219e
"""

import View
import tkinter as tk
# class vars_test(object):
#     def __init__(self, args):
        
#         for arg in args:
#             vars(self)[arg] = args[arg]
        
#     def set_args(self,args):
        
#         for arg in args:

#             vars(self)[arg] = args[arg]

root = tk.Tk()

mat_list = ['Material1', 'Material2', 'Material3']
args = {'mat_name_list':mat_list}

mat_view = View.Material_View(root, args)
mat_view.grid()

root.mainloop()

        
        
