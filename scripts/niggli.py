from cctbx import uctbx
from cctbx import crystal
import sys
# "51.79917778,  101.64778571,   54.06718876,   90.34,           67.2690814,    89.3"
uc  =  uctbx.unit_cell( sys.argv[1] )
xs  = crystal.symmetry(uc, "P1")
#print 'BEFORE', xs.unit_cell().parameters()
cbop_prim = xs.change_of_basis_op_to_niggli_cell()
xs1 = xs.change_basis(cbop_prim)
print xs1.unit_cell().parameters()

