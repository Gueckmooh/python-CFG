#!/usr/bin/env python3.5
import re
import subprocess

CROSS_TARGET="arm-none-eabi-"

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
  to_match = r'<([^+]+)'
  regex = re.compile (to_match)
  s = regex.search (comm)
  return s.groups()[0]

def is_jump (stm):
  addr, instr, comm = stm
  to_match = r'(b[a-z]*) ([0-9a-f]+)'
  regex = re.compile (to_match)
  s = regex.search (instr)
  if s != None:
    return True
  else:
    return False

def test ():
  filename = "/home/brignone/Documents/Cours/M2/WCET/CFG-python/tests/example1.o"
  function = read_function (filename, "main")
  f = split_function (function)
  for v in f:
    is_jump (v)


# Local Variables:
# python-shell-interpreter: "python3.5"
# End:
