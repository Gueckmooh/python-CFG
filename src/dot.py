# import node
import sys

def gen_dot_file (graph, node_map, filename):
  write = sys.stdout.write
  print ("bla")
  try:
    file = open (filename, "w")
  except IOError:
    sys.stderr.write ("Could not open %s\n" % (filename))
    sys.exit (1)
  file.write ("digraph G {\n")
  for n in graph:
    lbls = set ([lbl[0] for lbl in graph[n]])
    if n != 'init':
      file.write ("    %s [shape=box];\n" % (n))
      file.write ("    %s [label=\"%s\"];\n" % (n, node_map[n].get_content ()))
      for d in lbls:
        file.write ("    %s -> %s\n" % (n, d))
    else:
        file.write ("    %s -> %s\n" % (n, list(lbls)[0]))
  file.write ('}')

# Local Variables:
# python-shell-interpreter: "python3.5"
# End:
