"""
Runs pointless on a given mtz file, and prints most likely spacegroups
"""
import subprocess
import pandas as pd
from lxml import etree

mtz_in = '/reg/d/psdm/mfx/mfxlt3017/scratch/yoon82/mfxlt3017_ponan-mbs-day2-120.mtz'
xml_out = mtz_in.split('.mtz')[0]+'.xml'

# Run pointless
cmd = 'pointless hklin '+mtz_in+' xmlout '+xml_out
print cmd
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
out, err = process.communicate()

# Parse pointless output
tree = etree.parse(xml_out)
lstKey = []
lstValue = []
for p in tree.iter() :
    lstKey.append(tree.getpath(p).replace("/",".")[1:])
    lstValue.append(p.text)

df = pd.DataFrame({'key' : lstKey, 'value' : lstValue})
df2=df.set_index("key",drop=False)
print "Most likely spacegroup (>= 0.04)"
probThresh = 0.04
counter = 1
while 1:
    candidate = 'POINTLESS.SpacegroupList.Spacegroup['+str(counter)+']'
    if candidate in df2.index:
        prob = float(df2.loc[".".join((candidate,'TotalProb'))].value)
        if prob >= probThresh:
            sgName = df2.loc[".".join((candidate,'SpacegroupName'))].value.strip()
            sgNum = int(df2.loc[".".join((candidate,'SGnumber'))].value)
            print "######"
            print "TotalProb:", prob
            print "SpacegroupName:", sgName
            print "SGnumber:", sgNum
    else:
        break
    counter += 1


