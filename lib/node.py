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

  def __init__ (self, addr, name, body, function):
    """\
    node (addr, name, body)
      Takes its begin address, a name and a body
    """
    self.addr = addr
    self.name = name
    self.body = body
    self.function = function
    self.dest = []

  def __str__ (self):
    s = "%s: Node %s\n" % (self.addr, self.name)
    if isinstance (self.body, list):
      for x in self.body:
        s += "%s\n" % (x[1])
    else:
      s += "%s\n" % (self.body[1])
    s += "Destinations:\n"
    for x in self.dest:
      s += "%s (cond: %s)\n" % (x[0], x[1])
    return s

  def get_content (self):
    s = ''
    if isinstance (self.body, list):
      for x in self.body:
        s += "%s\\n" % (x[1])
    else:
      s += "%s\\n" % (self.body[1])
    return s

  def add_dest (self, dest):
    if isinstance (dest, list):
      for v in dest:
        self.dest.append (v)
    else:
      self.dest.append (dest)

  def set_dest_if_empty (self):
    if not all_path_sat (self.dest):
      d2 = []
      for x in self.dest:
        if x[1] != 'call':
          d2.append (x)
      last = int (self.body[-1][0], 16)
      last += 4 + 4 * len(d2)
      last = "%x" % (last)
      self.dest.append ((last, 'al'))

  def get_dest (self):
    return [v[0] for v in self.dest]

  def get_dest_cond_map (self):
    ret = {}
    for v in self.dest:
      ret[v[0]] = v[1]
    return ret

  def fix_call (self, begin_map, external_functions):
    to_insert = []
    while True:
      cont = False
      for v in self.dest:
        if v[1] == 'call':
          if v[0] in external_functions:
            self.dest.remove (v)
            cont = True
            self.dest.append ((v[0], 'extern'))
            to_insert.append (("extern", v[0]))
          else:
            self.dest.remove (v)
            cont = True
            self.dest.append ((begin_map[v[0]].addr, 'al'))
            to_insert.append ((begin_map[v[0]].name, begin_map[v[0]]))
      if not cont:
        break
    if to_insert != []:
      return (self.function, self.name,
              to_insert)


# Local Variables:
# python-shell-interpreter: "python3.5"
# End:
