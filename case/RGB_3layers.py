#%%
from elements import *
from system import *
import time
#%%
Air_coefficient = [0,0,0,0,0,0]
LASF46B_coefficient = [2.17988922,0.306495184,1.56882437,0.012580538,0.056719137,105.316538]    #1.9
Air = Material('Air',Air_coefficient)
LASF46B = Material('LASF46B',LASF46B_coefficient)

kdom = K_domain(LASF46B)
kdom.set_source({'fov':[-20,20,-15,15],
                 'wavelength_list':[0.525],
                 'fov_grid':(11,11)})
#Doe1
kdom.add_element(Grating,{'name': 'G1',
                          'periods': [[0.3795,11]]})
#Doe2
kdom.add_element(Grating,{'name': 'G2',
                          'periods': [[0.2772,-122.2]]})
#Doe3
kdom.add_element(Grating,{'name': 'G3',
                          'periods': [[0.3795,104.6]]})

kdom.add_sequence([[1,[1,0]],
                   [2,[1,0]],
                   [3,[1,0]]])

#kdom.report()
kdom.tracing()
kdom.draw()
#%%
kdom_b = K_domain(LASF46B)
kdom_b.set_source({'fov':[-20,20,-15,15],
                 'wavelength_list':[0.455],
                 'fov_grid':(11,11)})
#Doe1
kdom_b.add_element(Grating,{'name': 'G1',
                          'periods': [[0.3289,11]]})
#Doe2
kdom_b.add_element(Grating,{'name': 'G2',
                          'periods': [[0.24023,-122.2]]})
#Doe3
kdom_b.add_element(Grating,{'name': 'G3',
                          'periods': [[0.3289,104.6]]})

kdom_b.add_sequence([[1,[1,0]],
                     [2,[1,0]],
                     [3,[1,0]]])

#kdom_b.report()
kdom_b.tracing()
kdom_b.draw()

#%%
kdom_r = K_domain(LASF46B)
kdom_r.set_source({'fov':[-20,20,-15,15],
                 'wavelength_list':[0.625],
                 'fov_grid':(11,11)})
#Doe1
kdom_r.add_element(Grating,{'name': 'G1',
                          'periods': [[0.4518,11]]})
#Doe2
kdom_r.add_element(Grating,{'name': 'G2',
                          'periods': [[0.330,-122.2]]})
#Doe3
kdom_r.add_element(Grating,{'name': 'G3',
                          'periods': [[0.4518,104.6]]})

kdom_r.add_sequence([[1,[1,0]],
                     [2,[1,0]],
                     [3,[1,0]]])

#kdom_r.report()
kdom_r.tracing()
kdom_r.draw()
#%%
#%matplotlib qt5
r = 0.5
R = r+r/np.cos(30/180*np.pi)
eye_relief = 20
eyebox_shape = [[6,4.5],[-6,4.5],[-6,-4.5],[6,-4.5],[6,4.5]]
IC_shape = [-38,13,R]

s2d = System_2D(kdom)
s2d.set_eyebox(eye_relief,eyebox_shape)
s2d.set_input(IC_shape)
s2d.estimate()
s2d.draw()
res = s2d.check(wid = 0)

#%%
s3d = System3D()
s3d.add_source(0,[-38,13+r/np.cos(30/180*np.pi),0.36],
               {'fov':[-20,20,-15,15],
                'wavelength_list':[0.525],
                'fov_grid':(5,5),
                'spatial_grid':(5,5)})
#Doe1
s3d.add_element(0.6,Grating,[-38,13+r/np.cos(30/180*np.pi),0.5],
                {'name': 'G1_g',
                 'periods': kdom.elements[1].periods,
                 'index':[LASF46B,Air]})
#Doe2
s3d.add_element(0.6,Grating,s2d.element_area[2],
                {'name': 'G2_g',
                 'periods': kdom.elements[2].periods,
                 'index':[LASF46B,Air], 
                 'mode': 'T&TIR'})
#Doe3
s3d.add_element(0.6,Grating,s2d.element_area[3],
                {'name': 'G3_g',
                 'periods': kdom.elements[3].periods,
                 'index':[LASF46B,Air],
                 'mode': 'T&TIR'})

# s3d.add_element(0.61,ColorFilter,[-38,13+r/np.cos(30/180*np.pi),0.6],
#                 {'name': 'filter_g',
#                  'stop_wavelength':0.525})

waveguide_shape = s3d.max_area()
#Surface1
s3d.add_element(0.1,Fresnel_loss,waveguide_shape,
                {'name': 'S1_g',
                 'index':[Air,LASF46B]})
#Surface2
s3d.add_element(0.6,Fresnel_loss,waveguide_shape,
                {'name': 'S2_g',
                 'index':[LASF46B,Air]})

#-----------------------------B_layer-----------------------------
s3d.add_source(0.65,[-38+r,13-r*np.tan(30/180*np.pi),0.36],
               {'fov':[-20,20,-15,15],
                'wavelength_list':[0.455],
                'fov_grid':(5,5),
                'spatial_grid':(5,5)})
#Doe1
s3d.add_element(1.2,Grating,[-38+r,13-r*np.tan(30/180*np.pi),0.5],
                {'name': 'G1_b',
                 'periods': kdom_b.elements[1].periods,
                 'index':[LASF46B,Air]})
#Doe2
s3d.add_element(1.2,Grating,s2d.element_area[2],
                {'name': 'G2_b',
                 'periods': kdom_b.elements[2].periods,
                 'index':[LASF46B,Air], 
                 'mode': 'T&TIR'})
#Doe3
s3d.add_element(1.2,Grating,s2d.element_area[3],
                {'name': 'G3_b',
                 'periods': kdom_b.elements[3].periods,
                 'index':[LASF46B,Air],
                 'mode': 'T&TIR'})

# s3d.add_element(1.25,ColorFilter,[-38+r,13-r*np.tan(30/180*np.pi),0.51],
#                 {'name': 'filter_b',
#                  'stop_wavelength':0.455})

#Surface1
s3d.add_element(0.7,Fresnel_loss,waveguide_shape,
                {'name': 'S1_b',
                 'index':[Air,LASF46B]})
#Surface2
s3d.add_element(1.2,Fresnel_loss,waveguide_shape,
                {'name': 'S2_b',
                 'index':[LASF46B,Air]})

#-----------------------------R_layer-----------------------------
s3d.add_source(1.25,[-38-r,13-r*np.tan(30/180*np.pi),0.36],
               {'fov':[-20,20,-15,15],
                'wavelength_list':[0.625],
                'fov_grid':(5,5),
                'spatial_grid':(5,5)})
#Doe1
s3d.add_element(1.8,Grating,[-38-r,13-r*np.tan(30/180*np.pi),0.5],
                {'name': 'G1_r',
                 'periods': kdom_r.elements[1].periods,
                 'index':[LASF46B,Air]})
#Doe2
s3d.add_element(1.8,Grating,s2d.element_area[2],
                {'name': 'G2_r',
                 'periods': kdom_r.elements[2].periods,
                 'index':[LASF46B,Air], 
                 'mode': 'T&TIR'})
#Doe3
s3d.add_element(1.8,Grating,s2d.element_area[3],
                {'name': 'G3_r',
                 'periods': kdom_r.elements[3].periods,
                 'index':[LASF46B,Air],
                 'mode': 'T&TIR'})

#Surface1
s3d.add_element(1.3,Fresnel_loss,waveguide_shape,
                {'name': 'S1_r',
                 'index':[Air,LASF46B]})
#Surface2
s3d.add_element(1.8,Fresnel_loss,waveguide_shape,
                {'name': 'S2_r',
                 'index':[LASF46B,Air]})
#-------------------------------------------------------------------

#Eyebox
s3d.add_element(-20,Receiver,s2d.eyebox,
                      {'name': 'R1',})

s3d.add_path({'G1_g':{1:[[-1,1,0],[-1,0,0]]},
              'G2_g':{1:[[-1,0,0],[-1,1,0],[-1,-1,0]]},
              'G3_g':{1:[[-1,0,0],[-1,1,0]]},
              'G1_b':{},
              'G2_b':{1:[[1,0,0]],-1:[[-1,0,0]]},
              'G3_b':{1:[[1,0,0]],-1:[[-1,0,0]]},
              'G1_r':{},
              'G2_r':{1:[[1,0,0]],-1:[[-1,0,0]]},
              'G3_r':{1:[[1,0,0]],-1:[[-1,0,0]]}})

s3d.add_path({'G1_g':{},
              'G2_g':{1:[[1,0,0]],-1:[[-1,0,0]]},
              'G3_g':{1:[[1,0,0]],-1:[[-1,0,0]]},
              'G1_b':{1:[[-1,1,0],[-1,0,0]]},
              'G2_b':{1:[[-1,0,0],[-1,1,0],[-1,-1,0]]},
              'G3_b':{1:[[-1,0,0],[-1,1,0]]},
              'G1_r':{},
              'G2_r':{1:[[1,0,0]],-1:[[-1,0,0]]},
              'G3_r':{1:[[1,0,0]],-1:[[-1,0,0]]}})

s3d.add_path({'G1_g':{},
              'G2_g':{1:[[1,0,0]],-1:[[-1,0,0]]},
              'G3_g':{1:[[1,0,0]],-1:[[-1,0,0]]},
              'G1_b':{},
              'G2_b':{1:[[1,0,0]],-1:[[-1,0,0]]},
              'G3_b':{1:[[1,0,0]],-1:[[-1,0,0]]},
              'G1_r':{1:[[-1,1,0],[-1,0,0]]},
              'G2_r':{1:[[-1,0,0],[-1,1,0],[-1,-1,0]]},
              'G3_r':{1:[[-1,0,0],[-1,1,0]]}})

# %%
t0 = time.time()
s3d.tracing(max_iter = 300)
print(time.time()-t0)
s3d.draw()

# %%
