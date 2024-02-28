# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 13:53:57 2021

@author: ry219e
"""

import tkinter as tk
import Controller, View

root = tk.Tk()
root.title("RASSP Automation")

controller = Controller.Controller()

mat_view = View.Material_View(master=root)
input_view = View.Input_View(master=root)

controller.bind_mat_view(mat_view)
controller.bind_input_view(input_view)

root.mainloop()
