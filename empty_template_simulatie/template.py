# config file for contracting cell

import numpy as np
py_seed = None
strand_gen = 'orderly'
FA = True
network_seed = None


rng_seq = np.random.SeedSequence(py_seed)
rng = np.random.default_rng(rng_seq)
rng_network_seq = np.random.SeedSequence(network_seed)
rng_network = np.random.default_rng(rng_network_seq)

# CPM parameters
MC_its = 5000 # number of Monte Carlo iterations is set here
parfile = "parameterfiles/extensions.par"

box_size_x = 200   # make sure box_size_x is the same figure as sizex in the .par file
box_size_y = 200   # same for box_size_y and sizey
Lx = int(box_size_x/2)
Ly = int(box_size_y/2)

cpm_neighbours = 2   # make sure cpm_neighbours is same as neighbours in .par file



# CPM - ECM interaction parameters
sigma_boundary_r = 2  # determines annulus in which adhesion sites are generated
adhesions = 50
adhesion_annihilation_penalty = 0
adhesions_per_pixel_overflow = 1   # how many adhesion sites can cluster in 1 CPM pixel?
adhesions_per_pixel_overflow_penalty = 0
# when (nxp,nyp) is copied onto (nx,ny), determine what to to with beads at site (nxp,nyp)
extension_mechanism = 'lazy'   # 'uniform', 'mixed', or 'sticky'
#extension_mechanism = 'uniform'   # 'uniform', 'mixed', or 'sticky'
# determine how we select adhesion displacements
nbhd_selection = 'uniform'   # 'uniform', 'mixed', or 'gradient'



# ECM integration options
md_its = 100
md_init_its = 5000
md_dt = 0.001
md_kT = 0.01
md_seed = 125 # rng.integers()

overdamped = True # if True, neglect inertial term in Langevin equations, i.e. Brownian integration mode
viscosity = 10



# mechanical properties of ECM
spring_r0 = 6.25
spring_k = 200 #600

helix_angle = 0
bend_t0 = np.pi - 2 * helix_angle
bend_k = 200
angle_potential = "harmonic"  # keep at harmonic for now --- DeltaH doesn't incorporate 'cosinesq' potentials

crosslink_k = 200
crosslink_r0 = 1.6

prestrain_factor = 1



# parameters influencing topology of ECM
beads = 9
contour_length = spring_r0*beads
strands = 200


pos_x_dist = lambda : rng_network.uniform(-Lx,Lx)
pos_y_dist = lambda : rng_network.uniform(-Ly,Ly)
angle_dist = lambda : rng_network.uniform(0,np.pi*2)

crosslink_max_r = 3
crosslink_bin_size = 1/3
num_init_crosslinks = 300

def crosslink_r_dist(r):   # distribution of possible radii of a crosslinker
    if r <= crosslink_max_r:
        p = 2/crosslink_max_r - 2/crosslink_max_r**2 * r
    else:
        p = 0
    return p



# output parameters

storeprefix = './simulation_data/testing/run6'
ECM_draw = True
ECM_stride = 10  # draw ECM every md_stride Monte Carlo steps

ECM_write_canvas = True
ECM_write_canvas_late = False


log_results = True
log_stride = 50
log_filetype = 'feather' # 'json' or 'feather'
log_batch_stride = 2

walltime = None  # None or specify walltime in string format "HH:MM:SS"

FA_number_bonds = 500 # This needs to be high enough, >= number of adhesion sites
FA_k = 500
FA_r0 =0
FA_creation_prob = 1
extensiononly = True

# novikova storm parameters:
ns_gamma = 1
ns_phi_s = 4.02
ns_phi_c = 7.76
ns_N_tot = 390 
f_star = 1
d0 = 1
Nb = 390
N0 = 50
shareN = False

adhesions_dt = 0.001
adhesions_T = 1
delete_distance = -1 # <0 is off

cytostiffness = 0.1


gui = False
