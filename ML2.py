#%%
from elements import *
from system import *
import time
#%%
Air_coefficient = [0,0,0,0,0,0]   #1.9
Air = Material('Air',Air_coefficient)
n2 = Material('n2',[2**2-1,0,0,0,0,0])

kdom = K_domain(n2)
kdom.set_source({'fov':[-20,20,-20,20],
                 'wavelength_list':[0.525],
                 'fov_grid':(11,11)})
#Doe1
kdom.add_element(Grating,{'name': 'G1',
                          'periods': [[0.350,-151]]})
#Doe2
kdom.add_element(Grating,{'name': 'G2',
                          'periods': [[0.350,89]]})
#Doe3
kdom.add_element(Grating,{'name': 'G3',
                          'periods': [[0.350,-31]]})

kdom.add_sequence([[1,[1,0]],
                   [2,[1,0]],
                   [3,[1,0]]])
kdom.add_sequence([[1,[1,0]],
                   [3,[1,0]],
                   [2,[1,0]]])

kdom.report()
kdom.tracing()
kdom.draw()

#%%
#%matplotlib qt5
eye_relief = 20
eyebox_shape = [[6,6],[-6,6],[-6,-6],[6,-6],[6,6]]
IC_shape = [38,18.33,1]

s2d = System_2D(kdom)
s2d.set_eyebox(eye_relief,eyebox_shape)
s2d.set_input(IC_shape)
s2d.estimate()
s2d.draw()
res = s2d.check(wid = 0)

#%%
s3d = System3D()
s3d.add_source(0,[38,18.33,0],
               {'fov':[-20,-20,20,20],
                'wavelength_list':[0.525],
                'fov_grid':(1,1),
                'spatial_grid':(1,1),
                'direct':1})
#Doe1
s3d.add_element(0.6,Grating,s2d.element_area[1],
                {'name': 'G1',
                 'periods': kdom.elements[1].periods,
                 'index':[n2,Air]})
#Doe2
s3d.add_element(0.6,Grating,s2d.element_area[2].convex_hull,
                {'name': 'G2',
                 'periods': kdom.elements[2].periods,
                 'index':[n2,Air], 
                 'mode': 'T&TIR'})
#Doe3
s3d.add_element(0.1,Grating,s2d.element_area[3].convex_hull,
                {'name': 'G3',
                 'periods': kdom.elements[3].periods,
                 'index':[Air,n2],
                 'mode': 'T&TIR'})

waveguide_shape = s3d.max_area()
#Surface1
s3d.add_element(0.1,Fresnel_loss,waveguide_shape,
                {'name': 'S1',
                 'index':[Air,n2]})
#Surface2
s3d.add_element(0.6,Fresnel_loss,waveguide_shape,
                {'name': 'S2',
                 'index':[n2,Air]})

#Eyebox
s3d.add_element(-20,Receiver,s2d.eyebox,
                      {'name': 'R1',})

# s3d.add_element(20,Receiver,s2d.eyebox,
#                       {'name': 'eyeglow',})

s3d.add_path({'G1':{1:[[-1,1,0],[-1,0,0]]},
              'G2':{1:[[-1,0,0],[-1,1,0]]},
              'G3':{-1:[[1,0,0],[1,1,0],[1,-1,0],[-1,0,0]]}})

s3d.add_path({'G1':{1:[[-1,1,0],[-1,0,0]]},
              'G2':{1:[[-1,0,0],[-1,1,0],[-1,-1,0]]},
              'G3':{-1:[[1,0,0],[-1,1,0]]}})


# %%
s3d.tracing(max_iter = 300)
s3d.draw()
# %%
t0 = time.time()
s3d.generate_graph()
print(time.time()-t0)
# %%
s3d.draw_graph(0)
# %%
