from PyNite import FEModel3D

def calc_shear_modulus(nu:float, E:float) -> float:
    """
    Returns the shear modulus calculated from 'nu' and 'E'
    """
    G = E / (2 * (1+nu))
    return G

def fe_model_ss_cant(
    w:float,
    b:float,
    a:float,
    E:float,
    I:float,
    A:float,
    J:float,
    nu:float,
    rho:float=1.,
)-> FEModel3D:
    
    """
    Returns a PyNite.FEModel3D model of a simply supported beam
    with a cantilever on one end.The beam is loaded with UDL.
    w - The magnitude of the distributed load
    b - The length of the backspan
    a - The length of the cantilever
    E - The elastic modulus of the beam material
    I - The moment of inertia of the beam section
    A - The cross-sectional area of the beam section
    J - The polar moment of inertia of the beam section
    nu - The Poisson's ratio of the beam material
    rho - The density of the beam material

    """
    model=FEModel3D()
    G=calc_shear_modulus(nu,E)
    model.add_material('default',E,G,nu,rho)
    model.add_node("N0",0,0,0)
    model.add_node("N1",b,0,0)
    model.add_node("N2",b+a,0,0)
    
    model.def_support("N0",True,True,True,True,True,False)
    model.def_support("N1",False,True,False,False,False,False)

    
    model.add_member("M0","N0","N2",'default',Iy=1.0,Iz=I,J=J,A=A)
    model.add_member_dist_load("M0","Fy",w1=w,w2=w)
    return model