#%%
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.path as mpath
from shapely.geometry import Point,MultiPoint,LineString,MultiLineString,Polygon,MultiPolygon
from shapely.affinity import translate
from shapely.ops import unary_union
import igraph as ig

from elements import *
class System3D:
    def __init__(self, environment_material = Material('Air',[0,0,0,0,0,0]), 
                 boundary = [[-100,100],[-100,100],[-50,50]]):
        self.index = environment_material
        self.boundary = np.array(boundary)
        self.wavelengths = []
        self.layers = {}
        self.elements = {}
        self.sources = {}
        self.kpath = {}
        self.eid = 0
        self.pid = 0

    def add_source(self,z,shape,
                   options = {'fov':[-20,20,-15,15],
                              'wavelength_list':[0.525],
                              'fov_grid':(5,5),
                              'spatial_grid':(5,5),
                              'direct':1}):
        self.wavelengths += options['wavelength_list']
        shape = np.asarray(shape.exterior.xy).T if isinstance(shape, Polygon) else shape
        self.sources[self.eid] = Source(shape = shape, z = z, **options)
        self.eid += 1

    def add_element(self,z,element,shape,options):
        shape = np.asarray(shape.exterior.xy).T if isinstance(shape, Polygon) else np.asarray(shape)
        polygon = mpath.Path.circle(shape[:2], shape[2]) if shape.ndim == 1 else mpath.Path(shape)
        self.elements[self.eid] = (element(**options),polygon)
        if z in self.layers:
            self.layers[z] += [self.eid]
        else:
            self.layers.update({z : [self.eid]})
        self.eid += 1

    def add_path(self,config):
        self.kpath[self.pid] = {i:config[name] for i in self.elements 
                               for name in config.keys() if self.elements[i][0].name == name}
        self.pid += 1

    def draw(self,unique = False, extra_planes = []):
        import visualization as vis
        view3d = vis.Display3D(1200,900,far = 200)

        if self.sources:
            for sid in self.sources:
                vertices = np.column_stack((self.sources[sid].polygon.vertices, 
                                            self.sources[sid].z*np.ones(len(self.sources[sid].polygon.vertices))))
                source = vis.polygon(vertices[:-1],colors = [1.0, 0.6, 0.07, 1])
                source = vis.Buffer_obj(*source)
                view3d.add_obj(source)

        #draw rays
        if hasattr(self,'rays'):
            #[wavelength,kx,ky,kz,x0,y0,z0,x,y,z,eid]
            for wavelength in self.rays:
                if wavelength >0.6:
                    colors = [1,0,0]
                elif 0.5 < wavelength <= 0.6:
                    colors = [0,1,0]
                elif 0.4 < wavelength <= 0.5:
                    colors = [0,0,1]
                else:
                    colors = [0,0,0]
                rays = self.rays[wavelength]
                if unique:
                    rays = np.unique(rays,axis = 0)
                if rays.shape[1]>3:
                    rays= rays[:,4:10].reshape(-1,3).astype(np.float32)
                rays = vis.Buffer_rays(rays,colors = colors, width = 1)
                view3d.add_obj(rays)

        volume_surface = []
        #draw polygon
        for z in self.layers.keys():
            for ie in self.layers[z]:
                element_type = type(self.elements[ie][0]).__name__
                if element_type == 'Grating' or element_type == 'Receiver' or element_type == 'ColorFilter':
                    colors = [1, 0, 1, 0.2] if element_type == 'Grating' else [0,0,0,0]
                    vertices = np.column_stack((self.elements[ie][1].vertices, z*np.ones(len(self.elements[ie][1]))))
                    element = vis.polygon(vertices[:-1],colors = colors)
                    element = vis.Buffer_obj(*element,offset = True)
                    view3d.add_obj(element)
                elif element_type == 'Fresnel_loss':
                    volume_surface += [(z,ie)]
                else: 
                    pass
        #draw extra_planes
        for vertices in extra_planes:
            colors = [0, 0, 0, 0]
            element = vis.polygon(vertices[:-1],colors = colors)
            element = vis.Buffer_obj(*element,edge_color = [0.7,0.7,0.7],offset = True)
            view3d.add_obj(element)
        

        #draw volume
        for i in range(len(volume_surface)//2):
            zf,ief = volume_surface[2*i]
            zr,ier = volume_surface[2*i+1]
            front_vertices = np.column_stack((self.elements[ief][1].vertices, zf*np.ones(len(self.elements[ief][1]))))
            rear_vertices = np.column_stack((self.elements[ier][1].vertices, zr*np.ones(len(self.elements[ier][1]))))
            cube = vis.volume(front_vertices[:-1],rear_vertices[:-1],colors = [0.6,1,1,0.2])
            cube = vis.Buffer_obj(*cube)
            view3d.add_obj(cube)

        view3d.draw()

    def tracing(self, max_iter = 2):
        self.rays = {}
        if not self.sources:
            print('This system have not source')
            return
        source_krays =  np.vstack([self.sources[sid].launch() for sid in self.sources]) #[wavelength,kx,ky,kz,x,y,z]
        source_krays = np.hstack((source_krays, np.zeros((source_krays.shape[0], 4)))) #Expand 4 columns to place [x,y,z,eid]
        #[wavelength,kx,ky,kz,x0,y0,z0,x,y,z,eid]
        for wavelength in self.wavelengths:
            self.rays[wavelength] = []
            kpath = self.kpath if self.kpath else [-1]
            for path_i in kpath:
                krays = source_krays[source_krays[:,0] == wavelength]
                if path_i != -1:
                    for eid in kpath[path_i]:
                        self.elements[eid][0].diffract_order = kpath[path_i][eid]
                for _ in range(max_iter):
                    #Rays propagate to next surface
                    index = np.sqrt(np.sum(krays[:,1:4]**2,axis = 1))
                    direction_cosine = krays[:,1:4]/index[:,np.newaxis]
                    delta_z = np.asarray(list(self.layers.keys()))-krays[:,6:7]
                    step = delta_z/direction_cosine[:,-1:]
                    step = np.min(np.where(step > 0, step, np.inf), axis=1)
                    alive = np.isfinite(step)
                    krays = krays[alive]
                    step = direction_cosine[alive]*step[alive,np.newaxis]
                    krays[:,7:10] = np.round(krays[:,4:7] + step, 4)

                    #Rays interact with elements
                    next_krays = []
                    z_list = set(krays[:,-2])
                    for zl in z_list:
                        hitting = krays[:,-2] == zl
                        hit_rays = krays[hitting]
                        krays = krays[~hitting]

                        for eid in self.layers[zl]:
                            hit = self.elements[eid][1].contains_points(hit_rays[:,7:9],radius=1E-3)
                            if np.any(hit):
                                hit_rays[hit,-1] = eid
                                self.rays[wavelength] += [hit_rays[hit]] 
                                next_krays += [self.elements[eid][0].launched(hit_rays[hit])]
                                hit_rays = hit_rays[~hit]
                        if hit_rays.size != 0:
                            next_krays += [hit_rays]

                    if len(next_krays) != 0:
                        krays = np.vstack(next_krays)
                        krays[:,4:7] = krays[:,7:10]
                    else:
                        break
            if self.rays[wavelength]:
                self.rays[wavelength] = np.vstack(self.rays[wavelength])

    def generate_graph(self,type = 'graph',end_eid = None):
        if not hasattr(self,'rays'):
            print('Without rays in the system')
            return
        
        self.graph = {}
        self.linegraph = {}
        source_krays =  np.vstack([self.sources[sid].launch() for sid in self.sources]) #[wavelength,kx,ky,kz,x,y,z]
        for wavelength in self.wavelengths:
            self.graph[wavelength] = []
            #[wavelength,kx,ky,kz,x0,y0,z0,x,y,z,eid]
            self.rays[wavelength] =  np.unique(self.rays[wavelength],axis = 0)
            srays = source_krays[source_krays[:,0] == wavelength]
            vertices = np.unique(self.rays[wavelength][:,7:],axis = 0)
            nodes_name = [f'({x:.4f},{y:.4f},{z:.4f})' for x,y,z in vertices[:,:-1]]
            nodes_eid = vertices[:,-1].tolist()
            nodes_xyz = vertices[:,:-1].tolist()
            edges = [(f'({x0:.4f},{y0:.4f},{z0:.4f})' , f'({x:.4f},{y:.4f},{z:.4f})') for x0,y0,z0,x,y,z in self.rays[wavelength][:,4:10]]
            edges_k = self.rays[wavelength][:,1:4].tolist()

            DG = ig.Graph(directed=True ,graph_attrs = {'wavelength': wavelength})
            DG.add_vertices([f'({x:.4f},{y:.4f},{z:.4f})' for x,y,z in srays[:,4:7]],
                            {'eid':0,
                             'xyz': srays[:,4:7].tolist()})
            
            DG.add_vertices(nodes_name,{'eid':nodes_eid,'xyz':nodes_xyz})
            DG.add_edges(edges,{'k': edges_k})
            # simply graph: Remove paths that don't reach the final element(receiver).
            if end_eid is None:
                end_eid = self.eid-1
            valid_nodes = [DG.subcomponent(vs, mode='in') for vs in DG.vs.select(eid=end_eid).indices]
            DG = DG.induced_subgraph(set.union(*map(set,valid_nodes))) if valid_nodes else ig.Graph(directed=True)
            #To separate independent graph
            DG_list = [DG.subgraph([vs.index] + DG.subcomponent(DG.es[i].target,mode='out'))
                       for vs in DG.vs if vs['eid'] == 0 for i in DG.incident(vs.index, mode='out')]
            for DG in DG_list:
                scc = DG.connected_components(mode="strong")
                back_edge = [tuple(edge[::-1]) for edge in scc if len(edge) == 2]
                DG.delete_edges(back_edge)
                self.graph[wavelength] += [DG]
        if type == 'linegraph':
            for wavelength in self.wavelengths:
                self.linegraph[wavelength] = []
                for DG in self.graph[wavelength]:
                    LG = DG.linegraph()
                    LG_tuples = np.asarray(LG.get_edgelist())
                    kin = DG.es[LG_tuples[:,0]]['k']
                    kout= DG.es[LG_tuples[:,1]]['k']

                    DG_tuples = np.asarray(DG.get_edgelist())
                    node_id = DG_tuples[LG_tuples[:,0],1]
                    eid = DG.vs[node_id]['eid']
                    xyz = DG.vs[node_id]['xyz']
                    # exyz = (np.asarray(DG.vs[DG_tuples[:,0]]['xyz'])+np.asarray(DG.vs[DG_tuples[:,1]]['xyz']))/2
                    # eeid = DG.vs[DG_tuples[:,0]]['eid']
                    # LG.vs.set_attribute_values('xyz',exyz)
                    # LG.vs.set_attribute_values('eid',eeid)
                    for key_values in [('wavelength',0.525),('kin',kin),('kout',kout),('eid',eid),('xyz',xyz)]:
                        LG.es.set_attribute_values(*key_values)
                    self.linegraph[wavelength] += [LG]
            
    def draw_graph(self,graph_index,edge_width = 1, node_size = 80, arrow = False, show_index = False, label_size = 12):
        import matplotlib.patches as patches
        if not hasattr(self,'graph'):
            return
        DG = self.graph[0.525][graph_index]
        label = [str(i) for i in DG.vs.indices]
        eid = DG.vs['eid']
        coords = np.asarray(DG.vs['xyz'])[:,:2]
        name_eid = {i: self.elements[i][0].name for i in self.elements}
        name_sid = {i: self.sources[i].name for i in self.sources}
        name_id = name_eid | name_sid

        cmap = plt.get_cmap('tab20', len(set(eid)))
        colors = [cmap(i /len(set(eid))) for i in eid]
        eid_colors = {name_id[e]: cmap(i / len(set(eid)))[:3] for i, e in enumerate(set(eid))}

        fig, ax = plt.subplots()
        for z in self.layers:
            for element_id in self.layers[z]:
                patch = patches.PathPatch(self.elements[element_id][1], facecolor='none', lw=1)
                ax.add_patch(patch)

        # draw edges
        for edge in DG.es:
            src, tgt = edge.tuple
            if arrow:
                ax.annotate("", xy=coords[tgt], xytext=coords[src],
                            arrowprops=dict(arrowstyle="->", color='black', lw=1.5, alpha=0.7),
                            fontsize=label_size)
            else:
                ax.plot([coords[src,0], coords[tgt,0]],[coords[src,1], coords[tgt,1]],
                        color='black', linewidth=edge_width)


        # draw nodes
        ax.scatter(coords[:,0],coords[:,1],
                color=colors, s=node_size, edgecolor='black')

        legend_patches = [patches.Patch(color=color, label=f'{e}') for e, color in eid_colors.items()]
        ax.legend(handles=legend_patches, loc='upper right',shadow = True)

        if show_index:
            for i, (x, y) in enumerate(coords):
                ax.text(x, y, label[i], fontsize=label_size, ha='center', va='center')

        ax.set_aspect('equal')
        plt.show()

    def interaction_info(self):
        if hasattr(self,'linegraph') and not hasattr(self,'interaction'):
            wl,kix,kiy,kiz,kox,koy,koz,eid = [],[],[],[],[],[],[],[]
            for wavelength in self.wavelengths:
                for graph in self.linegraph[wavelength]:
                    wl += graph.es.get_attribute_values('wavelength')
                    kix += graph.es.get_attribute_values('kin_x')
                    kiy += graph.es.get_attribute_values('kin_y')
                    kiz += graph.es.get_attribute_values('kin_z')
                    kox += graph.es.get_attribute_values('kout_x')
                    koy += graph.es.get_attribute_values('kout_y')
                    koz += graph.es.get_attribute_values('kout_z')
                    eid += graph.es.get_attribute_values('eid')
            interactions = np.unique(np.vstack((wl,kix,kiy,kiz,kox,koy,koz,eid)),axis = 1).T
            
            self.interactions = {}
            for eid in self.elements:
                if type(self.elements[eid][0]) == Grating:
                    interaction = interactions[interactions[:,7]==eid]
                    diff_order = self.elements[eid][0].diffract_order
                    diff_order = np.unique(np.vstack(list(diff_order.values()))[:,1:],axis = 0)
                    dkxy = (interaction[:,4:6]-interaction[:,1:3])/interaction[:,:1]
                    diection = np.vstack((np.where(interaction[:,3]>=0,1,-1),np.where(interaction[:,6]>=0,1,-1))).T
                    order_gv = diff_order[:,-2:] @ self.elements[eid][0].g_vectors
                    order_i = np.argmin(np.sum(np.abs(dkxy[:,np.newaxis]-order_gv),axis = 2),axis = 1)
                    self.interactions[eid] = np.hstack((interaction,diection,diff_order[order_i]))

    def max_area(self,border = 5):
        all_shape = np.vstack([self.elements[i][1].vertices for i in self.elements])
        xmax,ymax = np.max(all_shape,axis = 0)
        xmin,ymin = np.min(all_shape,axis = 0)
        max_area = [[xmax+border,ymax+border],[xmax+border,ymin-border],
                   [xmin-border,ymin-border],[xmin-border,ymax+border],
                   [xmax+border,ymax+border]]
        return max_area

# %%
class K_domain:
    def __init__(self,substrate_material ,surrounding_material = Material('Air',[0,0,0,0,0,0])):
        self.index = surrounding_material,substrate_material
        self.sequences = {}
        self.elements = {}
        self.eid = 0
        self.sid = 0

    def set_source(self,options = {'fov':[-20,20,-15,15],
                                   'wavelength_list':[0.525],
                                   'fov_grid':(5,5)}):
        self.wavelengths = options['wavelength_list']
        options['spatial_grid'] = (1,1)
        self.source = Source(**options)

    def add_element(self,element,options):
        options['index'] = self.index
        if element.__name__ == 'Grating':
            self.eid += 1
            self.elements[self.eid] = element(**options)

    def add_sequence(self,sequence):
        # sequence = [[eid, order],...]
        # e.g. [[1, [0, 1]], [2, [0, 1]], [3, [0, 1]]]=> ray tracing through elements 1=>2=>3 at orders 0 and 1
        if len(sequence)<=3:
            self.sequences[self.sid] = sequence
            self.sid += 1

    def elements_info(self):
        for eid in self.elements:
            print(eid,self.elements[eid].name)

    def tracing(self,sid_list = None):
        if hasattr(self,'source'):
            self.k_out = {}
            sid_list = sid_list if sid_list else self.sequences.keys()
            k_in = self.source.launch()[:,:4]
            for sid in sid_list:
                self.k_out[sid] = [k_in]
                for i,(eid,order) in enumerate(self.sequences[sid]):
                    idx = 0 if i==2 else 1
                    k_in = self.elements[eid].launched_k(k_in, order, idx)
                    self.k_out[sid] += [k_in]
                self.k_out[sid] = np.array(self.k_out[sid])

    def draw(self,sid_list = None):
        fig, ax = plt.subplots()

        sid_list = sid_list if sid_list else self.sequences.keys()
        wavelength_list = []
        for sid in sid_list:
            kray = self.k_out[sid]
            for k in kray:
                colors= np.zeros((k.shape[0],3))
                colors[k[:,0]>0.6] = [1,0,0]
                colors[np.all((0.6>=k[:,0],k[:,0]>0.5),axis = 0)] = [0,1,0]
                colors[0.5>=k[:,0]] = [0,0,1]

                wavelength_list += [k[:,0]]
                ax.scatter(k[:,1],k[:,2], s=5, c=colors)

        inner_r = np.average([self.index[0](wl) for wl in np.unique(wavelength_list)])
        inner_circle = plt.Circle((0, 0), inner_r, color='k', fill=False, linewidth=2)
        ax.add_artist(inner_circle)
        outer_r = np.average([self.index[1](wl) for wl in np.unique(wavelength_list)])
        outer_circle = plt.Circle((0, 0), outer_r, color='k', fill=False, linewidth=2)
        ax.add_artist(outer_circle)

        ax.set_xlim(-np.ceil(outer_r), np.ceil(outer_r))
        ax.set_ylim(-np.ceil(outer_r) ,np.ceil(outer_r))
        ax.set_aspect('equal', 'box')
        plt.grid(True)
        plt.show()

    def report(self):
        for item,index in zip(['surrounding_material','substrate_material'],self.index):
            print(f'{item}:\n name: {index.name},\n coefficient: {index.coefficient}')
        print('source')
        print(f' wavelength: {self.source.wavelength_list}')
        print(f' Hfov: {self.source.fov[:2]}, Vfov: {self.source.fov[-2:]}')
        print(f' fov grid: {self.source.fgrid}')
        print('elements')
        for eid in self.elements:
            print(f'{eid}, {self.elements[eid].__class__.__name__}\n name: {self.elements[eid].name},', end = ' ')
            for i,period in enumerate(self.elements[eid].periods):
                print(f'period{i+1}: {period}', end = ',')
            print()
        print('k-path') 
        for sid in self.sequences:
            print(' ',self.sequences[sid])

class System_2D:
    def __init__(self,kdomain,boundary = [[-100,100],[-100,100]]):
        self.kd = kdomain
        self.boundary = np.array(boundary)
        self.lmax = np.sqrt((self.boundary[0,1]-self.boundary[0,0])**2+(self.boundary[1,1]-self.boundary[1,0])**2)
          
    def set_eyebox(self,relief,shape, euler_angles = ()):
        self.active_oc = {}
        self.eyebox = Point(shape[:2]).buffer(shape[2]) if np.asarray(shape).ndim == 1 else Polygon(shape)
        self.relief = np.round(relief,4)
        if euler_angles:
            points = np.asarray(self.eyebox.exterior.coords.xy)
            points = np.vstack((points,relief*np.ones_like(points[0]))).T
            points = System_2D.euler_rotate(points, euler_angles)
            self.relief = np.round(points[np.argmin(np.abs(points[:,2])),2],4) #Effective eye-relief
            delta_z = points[:,2]-self.relief
            m = delta_z/self.kd.k_out[0][3,:,3:4]
            dxdy = self.kd.k_out[0][3,:,np.newaxis,1:3]*m[:,:,np.newaxis]
            points = points[np.newaxis,:,:2]-dxdy
            self.eyebox = unary_union([Polygon(p) for p in points]).convex_hull #Effective Projected eyebox

        for sid in self.kd.sequences.keys():
            m = self.relief/self.kd.k_out[sid][3,:,3]
            dxdy = self.kd.k_out[sid][3,:,1:3]
            self.active_oc[sid] = [translate(self.eyebox,xoff=-m[i]*dxdy[i,0], yoff=-m[i]*dxdy[i,1]) if not np.isnan(m[i]) else Polygon()  
                                    for i in range(len(m))]
                 
    def set_input(self,shape):
        self.ic_beam = {}
        shape = np.asarray(shape)
        for sid in self.kd.sequences.keys():
            dxdy = self.kd.k_out[sid][1,:,1:3]
            m =  self.lmax/np.sqrt(np.sum(dxdy**2,axis = 1))
            phi = np.arctan2(self.kd.k_out[sid][1,:,2],self.kd.k_out[sid][1,:,1])
            # Circular IC
            if shape.ndim == 1:
                self.ic = Point(shape[:2]).buffer(shape[2])
                p0 = np.vstack((shape[2]*np.cos(phi-np.pi/2)+shape[0],shape[2]*np.sin(phi-np.pi/2)+shape[1])).T
                p1 = np.vstack((shape[2]*np.cos(phi+np.pi/2)+shape[0],shape[2]*np.sin(phi+np.pi/2)+shape[1])).T
            # Non-Circular IC (Polygon)
            else:
                self.ic = Polygon(shape)
                center = np.average(shape[:-1], axis = 0)
                v0 = np.vstack((np.cos(phi-np.pi/2),np.sin(phi-np.pi/2))).T
                v1 = np.vstack((np.cos(phi+np.pi/2),np.sin(phi+np.pi/2))).T
                n_vector = v1-v0
                p_vector = shape-center
                l = p_vector.dot(n_vector.T)
                min_i = np.argmin(l,axis = 0)
                max_i = np.argmax(l,axis = 0)
                p0 = shape[min_i]
                p1 = shape[max_i]

            p2 = p1 + m[:,np.newaxis]*dxdy
            p3 = p0 + m[:,np.newaxis]*dxdy
            if len(set([self.kd.sequences[i][0][0] for i in self.kd.sequences])) == 1 :
                self.ic_beam[sid] = [Polygon([p0[i],p1[i],p2[i],p3[i]]).union(self.ic) for i in range(len(m))]
            else:
                self.ic_beam[sid] = [Polygon([p0[i],p1[i],p2[i],p3[i]]).difference(self.ic) for i in range(len(m))]

    def estimate(self):
        self.oc_area = {}
        self.epe_area = {}
        self.oc_beam = {}
        self.functional_area = {}
        self.element_area = {}
        self.test_area = {}
        for sid in self.kd.sequences.keys():
            active_oc = self.active_oc[sid]
            ic_beam = self.ic_beam[sid]
            self.oc_area[sid] = []
            self.epe_area[sid] = []
            self.oc_beam[sid] = []
            self.functional_area[sid] = []
            self.test_area[sid] = []
            for fid in range(len(active_oc)):
                diff_polygon = active_oc[fid].difference(ic_beam[fid]) 
                diff_polygon = (diff_polygon 
                                if isinstance(diff_polygon, MultiPolygon) else MultiPolygon([diff_polygon])
                                if isinstance(diff_polygon, Polygon) else MultiPolygon())
                inter_polygon = active_oc[fid].intersection(ic_beam[fid])
                inter_polygon = inter_polygon if isinstance(inter_polygon, Polygon) else Polygon()
                oc_beam_end = MultiPolygon(list(diff_polygon.geoms)+[inter_polygon])
                dxdy = self.kd.k_out[sid][2,fid,1:3]
                m = self.lmax/np.sqrt(np.sum(dxdy**2))
                oc_beam_start = translate(oc_beam_end, xoff=-m*dxdy[0], yoff=-m*dxdy[1])
                oc_beam = [MultiPoint(list(s.exterior.coords)+list(e.exterior.coords)).convex_hull
                           for s, e in zip(oc_beam_start.geoms, oc_beam_end.geoms)]
                inter_epe = ic_beam[fid].intersection(oc_beam,1E-9)

                oc_area,epe_area = [],[]
                for epe_a,oc_a in zip(inter_epe,oc_beam_end.geoms):
                    if isinstance(epe_a, Polygon) and not epe_a.is_empty and epe_a.area > 1E-9:
                        oc_area += [oc_a]
                        epe_area += [epe_a]

                epe_area = unary_union(epe_area) or Polygon()
                oc_area = unary_union(oc_area) or Polygon()
                epe_b = translate(epe_area, xoff=m*dxdy[0], yoff=m*dxdy[1])
                oc_beam = MultiPoint(list(epe_area.exterior.coords)+list(epe_b.exterior.coords)).convex_hull or Polygon()
                oc_area = oc_area.intersection(oc_beam)

                self.oc_beam[sid] += [oc_beam]
                self.epe_area[sid] += [epe_area]
                self.oc_area[sid] += [oc_area]

        for sid in self.kd.sequences.keys():
            self.functional_area[sid] = [self.ic,
                                         unary_union(self.epe_area[sid]).convex_hull,
                                         unary_union(self.oc_area[sid]).convex_hull]
            #element layout
            for i,elem in enumerate(self.kd.sequences[sid]):
                eid = elem[0]
                if eid not in self.element_area:
                    self.element_area[eid] = self.functional_area[sid][i]
                else:
                    self.element_area[eid] = self.element_area[eid].union(self.functional_area[sid][i])

        self.eyebox_area = np.asarray([unary_union([self.oc_area[sid][fid] for sid in self.kd.sequences]).area 
                                       for fid in range(len(self.kd.k_out[0][0]))])

    def check(self,sid = None,wid = 0):
        wavelength_shape = len(self.kd.source.wavelength_list)
        fov_shape = self.kd.source.fgrid
        eyebox_area = self.eyebox_area if sid == None else np.array([oc_a.area for oc_a in self.oc_area[sid]])
        res = (eyebox_area/self.eyebox.area)
        report = np.where(res<0.5)
        res = res.reshape((*fov_shape,wavelength_shape))
        plt.imshow(res[:,:,wid].T, origin = 'lower', extent = self.kd.source.fov, vmin=0, vmax = 1)
        plt.show()
        return report
        
    def draw(self,sid = None,fid = None):
        fig, ax = plt.subplots()
        ax.plot(*self.ic.exterior.xy,'k')
        ax.plot(*self.eyebox.exterior.xy,'k',ls = '--')
        xmin,xmax = min(self.eyebox.exterior.xy[0]),max(self.eyebox.exterior.xy[0])
        ymin,ymax = min(self.eyebox.exterior.xy[1]),max(self.eyebox.exterior.xy[1])
        for eid in self.kd.elements.keys():
            if not self.element_area[eid].is_empty:
                xy = self.element_area[eid].exterior.xy
                ax.fill(*xy, alpha=0.5, edgecolor='black', linewidth=2)
                xmin = min(xy[0]) if min(xy[0])<xmin else xmin
                xmax = max(xy[0]) if max(xy[0])>xmax else xmax
                ymin = min(xy[1]) if min(xy[1])<ymin else ymin
                ymax = max(xy[1]) if max(xy[1])>ymax else ymax

        if sid != None and fid != None:
            epe_area = self.epe_area[sid][fid] if not self.epe_area[sid][fid].is_empty else Polygon()
            oc_area = self.oc_area[sid][fid] if not self.oc_area[sid][fid].is_empty else Polygon()
            ax.fill(*epe_area.exterior.xy, alpha=0.5, color = 'black',edgecolor='black', linewidth=2)
            ax.fill(*oc_area.exterior.xy, alpha=0.5, color = 'black', edgecolor='black', linewidth=2)

            ax.plot(*self.ic_beam[sid][fid].exterior.xy, color = 'k',linewidth=1)
            ax.plot(*self.oc_beam[sid][fid].exterior.xy, color = 'k',linewidth=1)
            ax.plot(*self.active_oc[sid][fid].exterior.xy, color = 'r',linewidth=1, ls = '--')

        ax.set_xlim(xmin-0.1*(xmax-xmin),xmax+0.1*(xmax-xmin))
        ax.set_ylim(ymin-0.1*(ymax-ymin),ymax+0.1*(ymax-ymin))
        plt.gca().set_aspect('equal')
        plt.show()

    def export(self,file_name = 'element_shape.npz'):
        shape_array = {}
        for eid in self.element_area:
            shape_array[str(eid)] = np.asarray(self.element_area[eid].exterior.xy).T
        np.savez(file_name, **shape_array)

    @staticmethod
    def max_distance_pair(lines):
        line_pair = ()
        lines = lines.geoms
        max_distance = 0
        for i in range(len(lines)):
            for j in range(i + 1, len(lines)):
                line1,line2 = lines[i],lines[j]
                distance = line1.distance(line2)
                if distance > max_distance:
                    max_distance = distance
                    line_pair = (line1, line2)
        return MultiLineString(line_pair)

    @staticmethod   
    def euler_rotate(points, angles_deg, rotation_order='zyx'):
        '''
        angles_deg = (alpha, beta, gamma)
        orcer: "zyx" mean is new_P=Rz.Ry.Rx.P'
        '''
        angles_rad = np.deg2rad(angles_deg)
        center = (np.max(points,axis = 0)+np.min(points,axis = 0))/2
        points = points-center
        R = np.eye(3)

        order_map = {'x': 0, 'y': 1, 'z': 2}
        order = [order_map[axis] for axis in rotation_order]
        for axis, theta in zip(order, angles_rad[order]):
            c, s = np.cos(theta), np.sin(theta)
            if axis == 0: #x
                R_axis = np.array([[1, 0, 0],[0, c, -s],[0, s, c]])
            elif axis == 1: #y
                R_axis = np.array([[c, 0, s],[0, 1, 0],[-s, 0, c]])
            elif axis == 2: #z
                R_axis = np.array([[c, -s, 0],[s, c, 0],[0, 0, 1]])
            else:
                raise ValueError("the formula of order is wrong")
            R = R_axis @ R
        rotated_points = points @ R.T
        rotated_points += center
        return rotated_points    

