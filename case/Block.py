#%%
from elements import *
from system import *
import time
#%%
Air_coefficient = [0,0,0,0,0,0]
LASF46B_coefficient = [2.17988922,0.306495184,1.56882437,0.012580538,0.056719137,105.316538]    #1.9
Air = Material('Air',Air_coefficient)
LASF46B = Material('LASF46B',LASF46B_coefficient)

#%%
s3d = System3D()
s3d.add_source(0,[0,0,1],
               {'fov':[-20,20,-15,15],
                'wavelength_list':[0.525],
                'fov_grid':(5,5),
                'spatial_grid':(5,5)})

#Surface1
s3d.add_element(10,Fresnel_loss,[[10,10],[-10,10],[-10,-10],[10,-10],[10,10]],
                {'name': 'S1_g',
                 'index':[Air,LASF46B]})
#Surface2
s3d.add_element(20,Fresnel_loss,[[10,10],[-10,10],[-10,-10],[10,-10],[10,10]],
                {'name': 'S2_g',
                 'index':[LASF46B,Air]})
#-------------------------------------------------------------------
#Eyebox
s3d.add_element(30,Receiver,[[10,10],[-10,10],[-10,-10],[10,-10],[10,10]],
                      {'name': 'R1',})

# %%
t0 = time.time()
s3d.tracing(max_iter = 300)
print(time.time()-t0)
s3d.draw()

# %%
t0 = time.time()
s3d.generate_graph()
print(time.time()-t0)
# %%
s3d.draw_graph(0)
# %%
