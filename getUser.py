import os

username        = str(os.environ.get("USER"))
inituser        = str(os.environ.get("USER")[0])
uid             = int(os.getuid())
workdir         = "user" if "user" in os.environ.get('PWD') else "work"
