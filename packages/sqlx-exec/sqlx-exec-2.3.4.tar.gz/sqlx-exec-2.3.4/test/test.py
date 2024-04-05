from typing import Collection, Sequence

t = ('1', '2')
print(isinstance(t, Collection), isinstance(t, Sequence))
# True True
l = ['1', '2']
print(isinstance(l, Collection), isinstance(l, Sequence))
# True True
s = set(l)
print(isinstance(s, Collection), isinstance(s, Sequence))
# True False
s = 'hello'
print(isinstance(s, Collection), isinstance(s, Sequence))
# True True

import executor
from config import MYSQL

executor.init_db(**MYSQL)
