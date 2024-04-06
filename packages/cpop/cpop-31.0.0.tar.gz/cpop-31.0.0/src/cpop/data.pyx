# cython: language_level=3

from collections.abc import Mapping
from cpython cimport dict
from cython cimport pint
from cpython.ref cimport PyObject


cdef frozenset DICT_ATTRS = frozenset(dir(dict))

cdef class NamespaceDict(dict[str, object]):
    def __getattr__(self, key: str):
        if key.startswith("__") and key.endswith("__"):
            self.__getattribute__(key)
        try:
            return self[key]
        except KeyError as e:
            raise AttributeError(e)

    def __setattr__(self, key: str, value: object):
        if isinstance(value, dict):
            value = NamespaceDict(value)
        self[key] = value


cdef class MultidictCache:
    cdef dict[str, object] _cache
    cdef list[dict[str, object]] _base_dicts
    cdef dict[str, list[str]] _split_cache

    def __init__(self, base_dicts=None):
        if base_dicts is None:
            base_dicts = []
        self._base_dicts = base_dicts
        self._cache = dict[str, object]()
        self._split_cache = dict[str, list[str]]()

    cpdef _clear(self):
        self._cache.clear()
        self._split_cache.clear()

    def __getitem__(self, key:str):
        if key in self._cache:
            return self._cache[key]

        if key not in self._split_cache:
            self._split_cache[key] = key.split('.')

        parts = self._split_cache[key]
        for base_dict in self._base_dicts:
            finder = base_dict
            try:
                for part in parts:
                    finder = finder[part]
                self._cache[key] = finder
                return finder
            except KeyError:
                continue

        raise KeyError(f"Item '{key}' not found in any base dictionary")

    def __iter__(self):
        return iter({k for base_dict in self._base_dicts for k in base_dict})

    def __contains__(self, item):
        return any(item in base_dict for base_dict in self._base_dicts)

cdef class ImmutableNamespaceDict:
    cdef readonly dict __data

    def __init__(self, data=None):
        if isinstance(data, ImmutableNamespaceDict):
            self.__data = data.__data
        elif isinstance(data, dict):
            self.__data = {key: freeze(value) for key, value in data.items()}
        else:
            self.__data = {}

    def __getitem__(self, key):
        try:
            return self.__data[key]
        except KeyError:
            return ImmutableNamespaceDict()

    def __getattr__(self, key):
        if key in self.__data:
            return self.__data[key]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")

    def __setattr__(self, key, value):
        if key == '_ImmutableNamespaceDict__data':
            object.__setattr__(self, key, value)
        else:
            raise TypeError("ImmutableNamespaceDict does not support attribute assignment")

    def __setitem__(self, key, value):
        raise TypeError("ImmutableNamespaceDict does not support item assignment")

    def __call__(self):
        return unfreeze(self.__data)

    def __len__(self):
        return len(self.__data)

    def __iter__(self):
        return iter(self.__data)

    def __bool__(self):
        return bool(self.__data)

    def __contains__(self, key):
        return key in self.__data

    def __repr__(self):
        return f"{self.__data}"

    def __eq__(self, other):
        if isinstance(other, ImmutableNamespaceDict):
            return self.__data == other.__data
        elif isinstance(other, dict):
            return self.__data == other
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def keys(self):
        return self.__data.keys()

    def values(self):
        return self.__data.values()

    def items(self):
        return self.__data.items()

    def get(self, key, default=None):
        return self.__data.get(key, default)

    def copy(self):
        return unfreeze(self.__data)


def freeze(data):
    if isinstance(data, ImmutableNamespaceDict):
        return data
    elif isinstance(data, dict):
        return ImmutableNamespaceDict({key: freeze(value) for key, value in data.items()})
    elif isinstance(data, list):
        return tuple(freeze(value) for value in data)
    elif isinstance(data, set):
        return frozenset(freeze(value) for value in data)
    else:
        return data

def unfreeze(data):
    if isinstance(data, ImmutableNamespaceDict):
        return {key: unfreeze(value) for key, value in data.items()}
    elif isinstance(data, frozenset):
        return {unfreeze(value) for value in data}
    elif isinstance(data, tuple):
        return [unfreeze(value) for value in data]
    else:
        return data


cpdef update(dest, upd, bint recursive_update=True, bint merge_lists=False):
    """
    Recursive version of the default dict.update

    Merges upd recursively into dest

    If recursive_update=False, will use the classic dict.update, or fall back
    on a manual merge (helpful for non-dict types like FunctionWrapper)

    If merge_lists=True, will aggregate list object types instead of replace.
    The list in ``upd`` is added to the list in ``dest``, so the resulting list
    is ``dest[key] + upd[key]``. This behavior is only activated when
    recursive_update=True. By default merge_lists=False.
    """
    cdef:
        list keys = list(upd.keys())
        object key, val, dest_subkey

    if recursive_update:
        for key in keys:
            val = upd[key]
            dest_subkey = dest.get(key, None)
            if isinstance(dest_subkey, Mapping) and isinstance(val, Mapping):
                ret = update(dest_subkey, val, merge_lists=merge_lists)
                dest[key] = ret
            elif isinstance(dest_subkey, list) and isinstance(val, list) and merge_lists:
                merged = dest_subkey[:]
                merged.extend([x for x in val if x not in merged])
                dest[key] = merged
            else:
                dest[key] = upd[key]
    else:
        for key in keys:
            dest[key] = upd[key]
    return dest
