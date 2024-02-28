# -*- coding: utf-8 -*-
"""
Created on Wed Feb 24 14:50:32 2021

Simple Class to format the crack case information for the RASSP .input file 


@author: Cade Wooten - 3321153
"""


class Crack_Case(object):

    # =============================================================================
    #   Constructor. Notice the default values for parameters that are not needed for every case
    #   TODO Not really sure if this is great way to set this up - will revisit
    # =============================================================================
    def __init__(self, code='', w='', t='', a_init='', c_init='', Rp='', Rm='', Rso='', a_fin='', c_fin='',
                 t2='', r='', e='', lt='', crack_control='ONED', dls='', num_blocks=50000):
        self.code = str(code)
        self.w = str(w)
        self.t = str(t)
        self.t2 = str(t2)
        self.r = str(r)
        self.e = str(e)
        self.lt = str(lt)

        self.a_init = str(a_init)
        self.a_fin = str(a_fin)
        self.c_init = str(c_init)
        self.c_fin = str(c_fin)
        self.Rp = str(Rp)
        self.Rm = str(Rm)
        self.Rso = str(Rso)
        self.crack_control = str(crack_control)
        self.num_blocks = str(num_blocks)

    # TODO add some logic for non standard crack cases!
    def input_file_format(self):
        return_string_list = []

        # Limits section
        return_string_list.append('LIMITS')

        return_string_list.append(self.c_init.rjust(10) + self.c_fin.rjust(10) +
                                  self.a_init.rjust(10) + self.a_fin.rjust(10) +
                                  self.Rp.rjust(10) + self.Rm.rjust(10))
        return_string_list.append(self.num_blocks)

        # Analysis section
        return_string_list.append('ANALYSIS')
        return_string_list.append('LOAD INTERACTION'.ljust(16) + 'YES'.rjust(8) +
                                  self.Rso.rjust(16))

        # Code section
        return_string_list.append(self.code.rjust(4) + self.crack_control.rjust(4) + self.w.rjust(12) +
                                  self.t.rjust(10) + self.r.rjust(10) +
                                  self.lt.rjust(5) + self.e.rjust(10))

        input_file_string = '\n'.join(return_string_list)

        return (input_file_string)
