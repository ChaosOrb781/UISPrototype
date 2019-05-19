class threadOverview:
  def __init__(self, username : str, header : str, date : str):
    self.username = username
    self.header = header
    self.createddate = date

class post:
  def __init__(self, id : str, threadid : str, username : str, specialization : str, works_at : str, content : str, created : str, modified : str):
    self.id = id
    self.threadid = threadid
    self.username = username
    self.specialization = specialization
    self.works_at = works_at
    self.content = content
    self.createddate = created
    self.modifieddate = modified


class thread:
  def __init__(self, id : str, username : str, processID : str, journalID : str, specialization : str, works_at : str, header : str, content : str, created : str, posts):
    self.id = id
    self.username = username
    self.processID = processID
    self.journalID = journalID
    self.specialization = specialization
    self.works_at = works_at
    self.header = header
    self.content = content
    self.createddate = created
    self.posts = posts