data1 = [{"name": "String 1"}, {"name": "String 4"}]
data2 = [{"name": "String 1"}, {"name": "String 2"}, {"name": "String 3"}]

import itertools

r1 = list(itertools.filterfalse(lambda x: x in data1, data2))
r2 = list(itertools.filterfalse(lambda x: x in data2, data1))

print(r1)
print(r2)
