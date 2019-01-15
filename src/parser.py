#!/usr/bin/env python3.5
import re
import subprocess
# import node

CROSS_TARGET="arm-none-eabi-"

def static_var (varname, value):
  def decorate (func):
    setattr (func, varname, value)
    return func
  return decorate

def read_function (filename, funcname):
  command = "%sobjdump -d %s" % (CROSS_TARGET, filename)
  command = command.split ()
  p = subprocess.Popen (command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = p.communicate ()
  p.kill ()
  command = "awk  -v  RS=  /^[[:xdigit:]]+ <%s>\:/" % (funcname)
  command = command.split ('  ')
  p = subprocess.Popen (command, stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE)
  out, err = p.communicate (out)
  p.kill ()
  out = out.decode ("utf-8").split ("\n")
  out.remove ("")
  return out

def clean_whitespaces (s):
  s = re.sub (r'\s+', ' ', s)
  s = re.sub (r'\s\Z', '', s)
  return s

def split_line (line):
  to_match = r'([a-f0-9]+)\:\s+[0-9a-f]+\s+([^;<]+)(.*)'
  regex = re.compile (to_match)
  s = regex.search (line)
  return tuple (clean_whitespaces(x) for x in s.groups ())

def split_function (function):
  new_function = [split_line (x) for x in function[1:]]
  return new_function

def get_target (jmp):
  addr, instr, comm = jmp
  if comm == "":
    return ()
  to_match = r'<([^+]+)\+0x([0-9a-f]+)>'
  regex = re.compile (to_match)
  s = regex.search (comm)
  return s.groups()

def is_jump (stm):
  addr, instr, comm = stm
  to_match = r'(b[a-z]*) ([0-9a-f]+|lr)'
  regex = re.compile (to_match)
  s = regex.search (instr)
  if s != None:
    return True
  else:
    return False

@static_var ("seed", 0)
def gen_node_name ():
  name = 'n_%d' % (gen_node_name.seed)
  gen_node_name.seed += 1
  return name

def cut (function):
  f = function[::-1]
  dests = []
  for pouet in range (5):
    for v in f[::-1]:
      print (v)
    print ()
    for i in range (len (f)):
      if is_jump (f[i]):
        if i == 0:
          v = f[0]
          f = f[1:]
          t = get_target (v)
          if t == ():
            dests.insert (len (dests), 'ret')
          else:
            fun, off = t
            dests.insert (len (dests), off)
          print (dests)
          break
        else:
          a = f[:i]
          f = f[i:]
          n = node (a[::-1][0][0], gen_node_name (), a[::-1])
          n.add_dest (dests)
          dests = []
          print (n)
          break

def test ():
  filename = "/home/brignone/Documents/Cours/M2/WCET/CFG-python/tests/example1.o"
  function = read_function (filename, "main")
  f = split_function (function)
  # for v in f:
  #   print (v)
  #   is_jump (v)
  cut (f)

# Local Variables:
# python-shell-interpreter: "python3.5"
# End:
