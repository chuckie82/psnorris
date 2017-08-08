from symmetryTools import symmetryMan
import h5py, sys, argparse

if __name__ == '__main__':
  # Input arguments
  parser = argparse.ArgumentParser(
    description='Run cctbx symmetry discovery. E.g. python discover_symmetry.py -e cxitut13 -r 10 --events selected_events.h5 --target target.phil'
  )
  parser.add_argument('-e', '--exp', help='Experiment ID e.g. cxitut13', required=True)
  parser.add_argument('-r', '--run', type=int, help='Run Number', required=True)
  parser.add_argument('-E', '--events', help='H5File containing selected event IDs')
  parser.add_argument('-N', '--n_events', default=500, help='No. of max events')
  parser.add_argument('-T', '--target', help='Target file for indexing', required=True)
  parser.add_argument('-o', '--output', default="symmetries", help='Path to output results')
  parser.add_argument('-q', '--queue', default="psanaq", help='Queuing system that supports bsub')
  parser.add_argument('-n', '--ncpus', default=12, type=int, help='No. of Cores')
  parser.add_argument('-C', '--custom', nargs='*', \
      help='Specify any valid arguments for cctbx.xfel.xtc_process. E.g. --custom format.cbf.invalid_pixel_mask=mask.pickle')
  args = parser.parse_args()
  # Get eventList
  eventList = None
  try:
    f=h5py.File(args.events,"r")
    eventList = f['likeli'][:args.n_events,0]
  except Exception as e:
    print "Error:", e
    print "No events found"
  print 'Found %d events'%(len(eventList))

  # Initialize 
  symMan = symmetryMan(args.exp, args.run, eventList, args.target, args.output,
      args.queue, args.ncpus)
  symMan.getSymmetryParameters(*args.custom)

