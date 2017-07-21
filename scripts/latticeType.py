import numpy as np
import subprocess

def equals(a, b, eps=0.5):
	if abs(a - b) <= eps:
		return True
	else:
		return False

def is90(a, eps=0.5):
	if abs(a - 90) <= eps:
		return True
	else:
		return False

def is120(a, eps=0.5):
	if abs(a - 120) <= eps:
		return True
	else:
		return False

def writeCrystfelCell(fname, latticeType, centering, uniqueAxisStr, uc):
	f = open(fname, 'w')
	f.write('CrystFEL unit cell file version 1.0\n')
	f.write('lattice_type = '+str(latticeType)+'\n')
	f.write('centering = '+str(centering)+'\n')
	f.write('unique_axis = '+str(uniqueAxisStr)+'\n')
	f.write('a = '+"{0:.2f}".format(float(uc[0]))+' A\n')
	f.write('b = '+"{0:.2f}".format(float(uc[1]))+' A\n')
	f.write('c = '+"{0:.2f}".format(float(uc[2]))+' A\n')
	f.write('al = '+"{0:.2f}".format(float(uc[3]))+' deg\n')
	f.write('be = '+"{0:.2f}".format(float(uc[4]))+' deg\n')
	f.write('ga = '+"{0:.2f}".format(float(uc[5]))+' deg\n')

nuc = np.load('bestNiggli.npy')

temp = str(nuc).split("[")[-1].split("]")[0]
temp = temp.split()
newTemp = ''
for i in temp:
	newTemp += i + ","

cmd = "python niggli.py " + newTemp
process = subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
nuc, err = process.communicate()
print "out: ", nuc
print "err: ", err

#la = niggliLattice[:,0]
#lb = niggliLattice[:,1]
#lc = niggliLattice[:,2]
#alpha = niggliLattice[:,3] / 180. * np.pi
#beta = niggliLattice[:,4]/ 180. * np.pi
#gamma = niggliLattice[:,5]/ 180. * np.pi
#Volume = la*lb*lc*np.sqrt(1+2.*np.cos(alpha)*np.cos(beta)*np.cos(gamma)-np.cos(alpha)**2-np.cos(beta)**2-np.cos(gamma)**2)

temp = str(nuc).split("(")[-1].split(")")[0].split(',')
(a,b,c,al,be,ga) = temp
a = round(float(a),2)
b = round(float(b),2)
c = round(float(c),2)
al = round(float(al),2)
be = round(float(be),2)
ga = round(float(ga),2)
nuc = np.array((a,b,c,al,be,ga))
uc = np.array((a,b,c,al,be,ga))
print "### in: ", nuc
axes = nuc[:3]
angles = nuc[3:]
numAxisSame = int(equals(a,b)) + int(equals(a,c)) + int(equals(b,c))
numNineties = len(np.where(abs(angles-90)<0.0001)[0])
print "num : ", numAxisSame, numNineties
uniqueAxisStr = '?'
latticeType = None

if 120 in angles:
	print "Trigonal or Hexagonal"
	latticeType = 'hexagonal'
	uniqueAxis = int(np.where(angles==120)[0])
elif numAxisSame == 3:
	latticeType = 'cubic'
elif numAxisSame == 2:
	latticeType = 'tetragonal'
	uniqueAxis = int(np.where(angles!=90)[0])
else:
	if numNineties == 3:
		latticeType = 'orthorhombic'
	elif numNineties == 2:
		latticeType = "monoclinic"
		uniqueAxisStr = 'b'
		uniqueAxis = int(np.where(abs(angles-90)>0.0001)[0])
		nonUniqueAxis = np.where(abs(angles-90)<0.0001)[0]
		print "ua: ", uniqueAxis, nonUniqueAxis
		print axes[np.array((nonUniqueAxis[0], uniqueAxis, nonUniqueAxis[1]))]
		print angles[np.array((nonUniqueAxis[0], uniqueAxis, nonUniqueAxis[1]))]
		uc[:3] = axes[np.array((nonUniqueAxis[0], uniqueAxis, nonUniqueAxis[1]))]
		uc[3:] = angles[np.array((nonUniqueAxis[0], uniqueAxis, nonUniqueAxis[1]))]
	else:
		latticeType = "triclinic"

uc = str(uc).split("[")[-1].split("]")[0].split()
centering = np.load('bestCentering.npy')
print "lattice type: ", latticeType
print "centering: ", centering
print "unique axis: ", uniqueAxisStr
print "unit cell: ", uc

writeCrystfelCell('sample.cell', latticeType, centering, uniqueAxisStr, uc)

exit()

temp = str(nuc).split("[")[-1].split("]")[0]
temp = temp.split()
newTemp = ''
for i in temp:
	newTemp += i + ","

print "### nuc: ", newTemp

cmd = "python niggli.py " + newTemp
process = subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
out, err = process.communicate()
print "out: ", out
print "err: ", err


#np.save('prelimNiggli.npy', nuc)


