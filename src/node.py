def all_path_sat (dest):
  conds = set ([x[1] for x in dest])
  if 'al' in conds:
    return True
  elif 'gt' in conds and 'le' in conds:
    return True
  elif 'ge' in conds and 'lt' in conds:
    return True
  elif 'ne' in conds and 'eq' in conds:
    return True
  else:
    return False

class node:
  def __init__ (self, addr, name, body):
    """\
    node (addr, name, body)
      Takes its begin address, a name and a body
    """
    self.addr = addr
    self.name = name
    self.body = body
    self.dest = []
  def test (self):
    print (all_path_sat (self.dest))
  def __str__ (self):
    s = "%s: Node %s\n" % (self.addr, self.name)
    for x in self.body:
      s += "%s\n" % (x[1])
    s += "Destinations:\n"
    for x in self.dest:
      s += "%s (cond: %s)\n" % (x[0], x[1])
    return s
  def get_content (self):
    s = ''
    for x in self.body:
      s += "%s\\n" % (x[1])
    return s
  def add_dest (self, dest):
    if isinstance (dest, list):
      for v in dest:
        self.dest.append (v)
    else:
      self.dest.insert (len (self.dest), dest)
  def set_dest_if_empty (self):
    if not all_path_sat (self.dest):
      last = int (self.body[-1][0], 16)
      last += 4 + 4 * len(self.dest)
      last = "%x" % (last)
      self.dest.append ((last, 'al'))
  def get_dest (self):
    return [v[0] for v in self.dest]


# Local Variables:
# python-shell-interpreter: "python3.5"
# End:
