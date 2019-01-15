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
  def __str__ (self):
    s = "%s: Node %s\n" % (self.addr, self.name)
    for x in self.body:
      s += "%s\n" % (x[1])
    s += "Destinations:\n"
    for x in self.dest:
      s += "%s\n" % (x)
    return s
  def add_dest (self, dest):
    if isinstance (dest, list):
      for v in dest:
        self.dest.insert (len (self.dest), v)
    else:
      self.dest.insert (len (self.dest), dest)
  def get_dest (self):
    return self.dest


# Local Variables:
# python-shell-interpreter: "python3.5"
# End:
