#!/usr/bin/env python3.5

from lib.parser import make_cfg, make_one_cfg
import sys
import getopt
import textwrap
prgname = sys.argv[0]

def usage (retval):
  if retval == 0:
    message = textwrap.dedent ("""\
    Usage: %s [options]...
    Mandatory arguments to long options are mandatory
    for short options too.
    Options:
      -h, --help               Display this information.
    """ % prgname)
    print (message)
    sys.exit (retval)
  else:
    message = textwrap.dedent ("""\
    Try '%s --help' for more information.\
    """ % (prgname))
    print (message)
    sys.exit (retval)


# Command line arguments parsing

output_name = ''
input_name = ''
only_f = None

def parse_command ():
  global output_name
  global input_name
  global only_f
  optlist, args = getopt.getopt (sys.argv[1:], "ho:",[
    'help', 'output=', 'only='
  ])
  for o, a in optlist:
    if o in ('-h', '--help'):
      usage (0)
    elif o in ('-o', '--output'):
      output_name = a
    elif o == '--only':
      only_f = a
  if len (args) == 0:
    usage (1)
  input_name = args[0]

parse_command ()

if input_name == '':
  usage (1)

if not only_f:
  make_cfg (input_name, output_name)
else:
  make_one_cfg (input_name, output_name, only_f)
