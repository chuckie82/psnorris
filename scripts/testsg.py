from cctbx.sgtbx.bravais_types import tst_bravais_types
from cctbx import sgtbx
import sys
import cctbx.sgtbx.bravais_types as bravais_types

symbol = "P 1 21 1"
#space_group_info = sgtbx.space_group_info(symbol=symbol)
#print space_group_info
#print sgtbx.space_group_info(symbol=symbol).type()
#print sgtbx.space_group_info(symbol=symbol).type().number()
#print sgtbx.space_group_info(symbol=symbol).show_summary()

GC = bravais_types.bravais_lattice(number=sgtbx.space_group_info(symbol=symbol).type().number())
#print GC
print GC.crystal_system
print GC.centring_symbol

lookup_symbol = 'P 1 21 1'
convention = "Hall"
symbols = sgtbx.space_group_symbols(lookup_symbol, convention)
print "symbols: ", symbols 
print "1: ", symbols.number()
print "2: ", symbols.schoenflies()
print "3: ", symbols.hermann_mauguin()
print "4: ", symbols.extension()
q = symbols.qualifier()
print "q: ", q

if (q != ""):
  if (symbols.number() < 16):
    if (q[-1] in "123"):
      unique_axis = q[:-1]
      cell_choice = q[-1]
    else:
      unique_axis = q
      cell_choice = ""
    print "  Unique axis:", unique_axis
    if (cell_choice != ""):
      print "  Cell choice:", cell_choice
  else:
    print "  Relation to standard setting:", q
print "Hall symbol:", symbols.hall()#.strip()

if False:
  centric = ("P 1 2/m 1", "C 1 2/m 1")
  for symbol in centric:
    space_group_info = sgtbx.space_group_info(symbol=symbol)
    assert str(space_group_info) == symbol
    assert space_group_info.is_reference_setting()
  if True:
    space_group_numbers = []
    for symbol in centric:
      space_group_numbers.append(sgtbx.space_group_info(symbol=symbol).type().number())
      print "/* %s */ %d," % (
        symbol, sgtbx.space_group_info(symbol=symbol).type().number())
    tst_bravais_types(True, space_group_numbers)
  print "OK"
