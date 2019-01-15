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
  to_match = r'(b([a-z]*)) ([0-9a-f]+|lr)'
  regex = re.compile (to_match)
  s = regex.search (instr)
  if s != None:
    cond = 'al'
    if not s.groups()[1] in ("", "x"):
      cond = s.groups()[1]
    print (stm)
    print (cond)
    return cond
  else:
    return None

@static_var ("seed", 0)
def gen_node_name ():
  name = 'n_%d' % (gen_node_name.seed)
  gen_node_name.seed += 1
  return name

def cut_firstpass (function):
  targets = set ()
  for v in function:
    if is_jump (v):
      t = get_target (v)
      if t != ():
        targets.add (t[1])
  print (targets)
  return targets

def cut (function):
  targets = cut_firstpass (function)
  nodes = []
  f = function[::-1]
  dests = []
  while len (f) != 0:
    for i in range (len (f)):
      if is_jump (f[i]):
        if i == 0:
          stm = f[i]
          v = f[0]
          f = f[1:]
          t = get_target (v)
          if t == ():
            print (is_jump(stm))
            dests.insert (len (dests), ('ret', is_jump(stm)))
          else:
            fun, off = t
            dests.insert (len (dests), (off, is_jump(stm)))
          break
        else:
          a = f[:i]
          f = f[i:]
          n = node (a[::-1][0][0], gen_node_name (), a[::-1])
          n.add_dest (dests)
          dests = []
          nodes.append (n)
          break
      elif i == len (f) - 1: # no jumps found
        n = node (f[::-1][0][0], gen_node_name (), f[::-1])
        n.add_dest (dests)
        f = []
        nodes.append (n)
        break
      elif f[i][0] in targets:
        print (f[i])
        a = f[:i+1]
        f = f[i+1:]
        n = node (a[::-1][0][0], gen_node_name (), a[::-1])
        n.add_dest (dests)
        dests = []
        nodes.append (n)
        break
  return nodes

def create_graph (nodes):
  graph = {}
  for n in nodes:
    name = n.name
    t = []
    for d in n.get_dest ():
      for m in nodes:
        if m.addr == d:
          t.append ((m.name, m))
    graph[name] = t
  return graph

def test ():
  filename = "/home/brignone/Documents/Cours/M2/WCET/CFG-python/tests/example1.o"
  function = read_function (filename, "main")
  f = split_function (function)
  # for v in f:
  #   print (v)
  #   is_jump (v)
  nodes = cut (f)
  for n in nodes:
    print (n)
  g = create_graph (nodes)
  print (g)
# Local Variables:
# python-shell-interpreter: "python3.5"
# End:
