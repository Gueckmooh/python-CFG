# import node
import sys

def static_var (varname, value):
  def decorate (func):
    setattr (func, varname, value)
    return func
  return decorate

@static_var ("seed", 0)
def name_cluster ():
  s = 'cluster%d' % name_cluster.seed
  name_cluster.seed += 1
  return s

def get_label (n):
  s = ''
  if n == 'eq':
    s = '=='
  elif n == 'ne':
    s = '!='
  elif n == 'ge':
    s = '>='
  elif n == 'gt':
    s = '>'
  elif n == 'lt':
    s = '<'
  elif n == 'le':
    s = '<='
  else:
    return ''
  return ' [label="%s"]' % (s)

def gen_dot_file (graph, node_map, filename):
  to_write = []
  write = sys.stdout.write
  print ("bla")
  # try:
  #   file = open (filename, "w")
  # except IOError:
  #   sys.stderr.write ("Could not open %s\n" % (filename))
  #   sys.exit (1)
  write ("digraph G {\n")
  for f in graph:
    write ("subgraph %s {\n" % (name_cluster ()))
    write ("    node [style=filled];\n")
    write ('    label = "%s";\n' % (f))
    write ("    color = blue;\n")
    gg = graph[f]
    for n in gg:
      lbls = set ([lbl[0] for lbl in gg[n]])
      if n != 'init':
        write ("    %s [shape=box];\n" % (n))
        write ("    %s [label=\"%s\"];\n" % (n, node_map[n].get_content ()))
        dests = node_map[n].get_dest_cond_map ()
        for d in lbls:
          if d != 'fini':
            if node_map[d].function != node_map[n].function:
              to_write.append ("    %s -> %s;\n")
            else:
              cond =dests[node_map[d].addr]
              write ("    %s -> %s%s;\n" % (n, d, get_label (cond)))
          else:
            to_write.append ("    %s -> %s;\n" % (n, 'end'))
      else:
        to_write.append ("    %s -> %s;\n" % ('start', list(lbls)[0]))
    write ('}\n')
    for v in to_write:
      write (v)
  write ('}')

# Local Variables:
# python-shell-interpreter: "python3.5"
# End:
