# /bin/python3

import re, os

filename = "neoplasms_meshmajor_journal_eng_1990_2014.xml"
outfilename = filename + ".clean"
r_amp = re.compile(r"&(?!#?[a-z0-9]+;)")
r_nbsp = re.compile(r"&nbsp;")
with open(filename) as x:
    if os.path.exists(outfilename):
        raise Exception("Aborted: would overwrite an existing file")
    with open(outfilename, "w") as y:
        for line in x:
            y.write(r_nbsp.sub(" ", r_amp.sub("&amp;", line)))
