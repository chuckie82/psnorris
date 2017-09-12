import subprocess, sys, json, io, os

def grepThis(outDir, searchString, filePattern):
  cmd = 'grep "'+searchString+'" '+outDir+'/stdout/'+filePattern+' |wc -l'
  process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
  out, err = process.communicate()
  return int(out.strip())

if __name__ == "__main__":
  # extract integration summary
  outDir = sys.argv[1]
  countTotal = grepThis(outDir, 'Processing shot', 'log_rank*.out')
  countMisses = grepThis(outDir, 'Not enough spots to index', 'log_rank*.out')
  countFailedIndex = grepThis(outDir, 'Sorry: No suitable indexing solution found', 'error_rank*.out')
  countIntegrated = countTotal - countMisses - countFailedIndex
  # create json file
  try:
    to_unicode = unicode
  except NameError:
    to_unicode = str
  data = {"Total processed": countTotal,
      "Not enough spots": countMisses,
      "Failed index": countFailedIndex,
      "Integrated": countIntegrated}
  # get runNo and trialNo
  outDirPatterns = outDir.split('/')
  with io.open(outDirPatterns[-2]+'_'+outDirPatterns[-1]+'_integration.json','w',encoding='utf8') as outfile:
    str_ = json.dumps(data, 
        indent=4, sort_keys=True,
        separators=(',', ': '), ensure_ascii=False)
    outfile.write(to_unicode(str_))
  print "Integration summary json created with this content:"
  print data 
  
