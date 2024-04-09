"""Module that generates mathematical models"""
import numpy as np
import control

def mass3_spring2_damper2():
    """Returns a control.ss model of a dynamic system
    
    Here is the topology of the system:
                k1      k2
    Fs --> [m1] == [m2] == [m3] 
                b1      b2
    The input vector is u = [Fs].
    The state vector is x = [vm1 fk1 vm2 fk2 vm3].
    The output vector is y = [vm1 fm1     ].
    T
    """