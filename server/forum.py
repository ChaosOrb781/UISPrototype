class threadOverview:
  def __init__(self, id : str, username : str, header : str, date : str, privilege : int):
    self.id = id
    self.username = username
    self.header = header
    self.createddate = date
    self.annoucement = privilege != None and privilege > -1
    self.privilege = privilege

class post:
  def __init__(self, id : str, username : str, content : str, created : str, modified : str, processID : str, journalID : str, specialization : str, works_at : str):
    self.id = id
    self.username = username
    self.processID = processID
    self.journalID = journalID
    self.specialization = specialization
    self.works_at = works_at
    self.content = content
    self.createddate = created
    self.modifieddate = modified


class thread:
  def __init__(self, CPR : str, username : str, header : str, content : str, created : str, processID : str, journalID : str, specialization : str, works_at : str, posts, open):
    self.CPR = CPR
    self.username = username
    self.processID = processID
    self.journalID = journalID
    self.specialization = specialization
    self.works_at = works_at
    self.header = header
    self.content = content
    self.createddate = created
    self.posts = posts
    self.open = open