from __future__ import annotations

import random
from typing import Mapping

import numpy as np


def auto_str(cls):
    def __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join(f'{k}={v}' for k, v in vars(self).items() if v is not None)
        )

    cls.__str__ = __str__
    return cls


class StaticHashable:

    def __init__(self, hash_obj, **kwargs) -> None:
        super(StaticHashable, self).__init__(**kwargs)
        self.hash = hash(hash_obj)

    def __hash__(self) -> int:
        return self.hash

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and self.hash == o.hash


class FrozenDict(Mapping):

    def __init__(self, *args, **kwargs):
        self._d = dict(*args, **kwargs)
        self._hash = None

    def __iter__(self):
        return iter(self._d)

    def __len__(self):
        return len(self._d)

    def __getitem__(self, key):
        return self._d[key]

    def __hash__(self):
        if self._hash is None:
            self._hash = hash(tuple(sorted(self._d.items())))
        return self._hash

    def __str__(self):
        return str(self._d)

    def __repr__(self) -> str:
        return repr(self._d)


def permuted(seq):
    ret = list(seq)
    random.shuffle(ret)
    return ret


def weighed_permutation(elements, weights):
    length = len(elements)
    shuffled_indices = np.random.choice(np.arange(length), size=(length,), replace=False, p=weights)
    return [elements[i] for i in shuffled_indices]
