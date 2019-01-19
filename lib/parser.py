#!/usr/bin/env python3.5

import re
import subprocess
import __main__ as main
if hasattr(main, '__file__'):
  from lib.node import node
  from lib.dot import *

CROSS_TARGET="arm-none-eabi-"
main_begin = '0'

external_functions = set ()
functions_to_parse = set ()
functions_parsed = set ()
begin_map = {}

def static_var (varname, value):
  def decorate (func):
    setattr (func, varname, value)
    return func
  return decorate

def cleanup_function (function):
  newfun = []
  regex = re.compile(r'(.word|@plt>:)')
  for i in function:
    s = regex.search (i)
    if s != None:
      if s.groups ()[0] == '@plt>:':
        return []
    else:
      newfun.append (i)
  return newfun

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

def get_target (jmp, funcname):
  addr, instr, comm = jmp
  if comm == "":
    return ()
  to_match = r'<([^+]+)(\+0x([0-9a-f]+)|)>'
  regex = re.compile (to_match)
  s = regex.search (comm)
  f = s.groups()[0]
  if f != funcname:
    return (f, '0')
  else:
    to_match = r'(b([a-z]*)) ([0-9a-f]+|lr)'
    regex = re.compile (to_match)
    s = regex.search (instr)
    addr = s.groups()[2]
    return (f, addr)

def is_jump (stm):
  addr, instr, comm = stm
  to_match = r'(b([a-z]*)) ([0-9a-f]+|lr)'
  regex = re.compile (to_match)
  s = regex.search (instr)
  if s != None:
    cond = 'al'
    if not s.groups()[1] in ("", "x", 'l'):
      cond = s.groups()[1]
    elif s.groups()[1] == 'l':
      cond = 'call'
    return cond
  else:
    return None

def is_call (stm):
  if not is_jump (stm):
    return False
  addr, instr, comm = stm
  to_match = r'(bl) ([0-9a-f]+|lr)'
  regex = re.compile (to_match)
  s = regex.search (instr)
  return s != None

@static_var ("seed", 0)
def gen_node_name ():
  name = 'n_%d' % (gen_node_name.seed)
  gen_node_name.seed += 1
  return name

def cut_firstpass (function, funcname):
  global functions_parsed
  global functions_to_parse
  targets = set ()
  for v in function:
    if is_jump (v):
      t = get_target (v, funcname)
      if t != ():
        if t[0] == funcname:
          targets.add (t[1])
        else:
          if not t[0] in functions_parsed:
            functions_to_parse.add (t[0])
  return targets

def cut (function, funcname):
  global begin_map
  targets = cut_firstpass (function, funcname)
  nodes = []
  f = function[::-1]
  dests = []
  while len (f) != 0:
    for i in range (len (f)):
      if is_jump (f[i]) and not is_call (f[i]):
        if i == 0:
          stm = f[i]
          v = f[0]
          f = f[1:]
          t = get_target (v, funcname)
          if t == ():
            dests.append (('ret', is_jump(stm)))
          else:
            fun, off = t
            if fun == funcname:
              dests.append ((off, is_jump(stm)))
            else:
              dests.append ((fun, is_jump(stm)))
          break
        else:
          a = f[:i]
          f = f[i:]
          n = node (a[::-1][0][0], gen_node_name (), a[::-1], funcname)
          n.add_dest (dests)
          dests = []
          nodes.append (n)
          break

      elif is_call (f[i]): # If there is a function call
        if i != 0:
          a = f[:i]
          n = node (a[::-1][0][0], gen_node_name (), a[::-1], funcname)
          n.add_dest (dests)
          nodes.append (n)
          dests = []
        t = get_target (f[i], funcname)
        fun, off = t
        dests.append ((fun, "call"))
        addr, instr, comm = f[i]
        f[i] = (addr, 'call %s' % (re.sub (r'@plt', '', fun)), comm)
        if i != 0:
          f = f[i:]
        break;

      elif i == len (f) - 1: # no jumps found
        n = node (f[::-1][0][0], gen_node_name (), f[::-1], funcname)
        n.add_dest (dests)
        f = []
        nodes.append (n)
        begin_map[funcname] = n
        break

      elif f[i][0] in targets: # We jump to this block
        a = f[:i+1]
        f = f[i+1:]
        n = node (a[::-1][0][0], gen_node_name (), a[::-1], funcname)
        n.add_dest (dests)
        dests = []
        nodes.append (n)
        break
  return nodes

def create_graph (nodes):
  graph = {}
  for n in nodes:
    funcname = n.function
    name = n.name
    t = []
    for d in n.get_dest ():
      if d == 'ret':
        t.append (('fini', None))
      else:
        for m in nodes:
          if m.addr == d:
            t.append ((m.name, m))
    if funcname in set ([x for x in graph]):
      graph[funcname][name] = t
    else:
      graph[funcname] = {name:t}
  name = 'init'
  t = []
  for d in n.get_dest ():
    for m in nodes:
      if m.addr == main_begin:
        t.append ((m.name, m))
  if funcname in set ([x for x in graph]):
    graph[funcname][name] = t
  else:
    graph[funcname] = {name:t}
  return graph

def make_cfg (input_name, output_name):
  global functions_to_parse
  global functions_parsed
  global main_begin
  global external_functions
  filename = input_name
  functions_to_parse.add ('main')
  cfg = {}
  gnode_map = {}
  while len (functions_to_parse) != 0:
    funcname = list(functions_to_parse)[0]
    functions_to_parse.remove (funcname)
    functions_parsed.add (funcname)
    function = read_function (filename, funcname)
    function = cleanup_function (function)
    f = split_function (function)
    if f == []:
      external_functions.add (funcname)
      continue
    main_begin = f[0][0]
    nodes = cut (f, funcname)
    for n in nodes:
      n.set_dest_if_empty ()
    g = create_graph (nodes)
    cfg = {**cfg, **g}
    node_map = {}
    for n in nodes:
      node_map[n.name] = n
    gnode_map = {**gnode_map, **node_map}
  for n in gnode_map:
    ret = gnode_map[n].fix_call (begin_map, external_functions)
    if ret != None:
      for v in ret[2]:
        cfg[ret[0]][ret[1]].append (v)
  gen_dot_file (cfg, gnode_map, output_name)



def make_one_cfg (input_name, output_name, function_name):
  global main_begin
  global external_functions
  filename = input_name
  cfg = {}
  gnode_map = {}
  funcname = function_name
  function = read_function (filename, funcname)
  function = cleanup_function (function)
  f = split_function (function)
  main_begin = f[0][0]
  nodes = cut (f, funcname)
  for n in nodes:
    n.set_dest_if_empty ()
  g = create_graph (nodes)
  cfg = {**cfg, **g}
  node_map = {}
  for n in nodes:
    node_map[n.name] = n
  gnode_map = {**gnode_map, **node_map}
  gen_dot_file (cfg, gnode_map, output_name, funcname)

def test ():
  global functions_to_parse
  global functions_parsed
  global begin_map
  global external_functions
  functions_to_parse = set ()
  functions_parsed = set ()
  begin_map = {}
  external_functions = set ()
  make_cfg ("/home/brignone/Documents/Cours/M2/WCET/CFG-python/tests/example5", "")



# Local Variables:
# python-shell-interpreter: "python3.5"
# End:
