def convertString(s : str):
  return s.replace("&oslash;", "ø").replace("&Oslash;", "Ø").replace("&aelig;", "æ").replace("&Aelig;", "Æ").replace("&aring;", "å").replace("&aring;", "Å")