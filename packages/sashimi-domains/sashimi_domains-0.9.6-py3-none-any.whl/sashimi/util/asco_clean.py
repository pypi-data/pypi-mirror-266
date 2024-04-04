# Clean asco from asco_real.csv
import re

asco_raw = open("./ASCO_real.csv", encoding="utf-16").read()
r = re.compile(r"\n(?= \d+\| (?:.*\|){8} \d+\| \w+\n )", flags=re.S + re.X)
asco_list = r.split(asco_raw)
asco_errors = [(i, x) for i, x in enumerate(asco_list) if x.count("|") != 10]
print("Abstracts with data containing delimiters:", len(asco_errors))
# There are 46, manually fixable but we should be fine without them for now
asco_list = [x.split("|") for x in asco_list if x.count("|") == 10]

# Let's create a dict
from collections import OrderedDict

columns = asco_list.pop(0)
asco_dict = OrderedDict(
    (c, [asco_list[i][ic].strip() for i, s in enumerate(asco_list)])
    for ic, c in enumerate(columns)
)

# Feed dict to DataFrame
import pandas, lxml.html

asco = pandas.DataFrame(asco_dict, dtype=int)
# get the years from conference names
asco["year"] = asco.MeetingName.apply(lambda x: int(x.split()[0]))

# Clean up HTML from title and body
cleanhtml = (
    lambda x: " ".join(lxml.html.fromstring(x).itertext()).strip()
    if ((type(x) is str) and x)
    else x
)
text_data = [
    "Title",
    "Body",
    "Institutions",
    "AuthorsString",
    "FirstAuthor",
    "AbstractSubcategory",
    "AbstractCategory",
    "MeetingName",
]
for field in text_data:
    asco[field] = asco[field].transform(cleanhtml)

# Manual fixes
asco.loc[4924, "Title"] = re.sub("</?Sup>", " ", asco.loc[4924, "Title"])

# Export a clean vanilla CSV
asco.to_csv("./asco_clean.csv.gz", index=False, compression="gzip")
# Mark missing data as loading the csv will do that
asco = asco.applymap(lambda x: pandas.np.nan if x == "" else x)

# Make sure we're not losing anything to the CSV
assert asco.equals(pandas.read_csv("./asco_clean.csv.gz"))
