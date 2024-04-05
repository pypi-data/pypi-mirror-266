#!/bin/python3

'''
    A regular expression builder that manages cross-pattern references
        and allows for easy runtime mutability by default
    The main interface is `PatternComposer`
'''

#> Imports
import re
import itertools
from types import SimpleNamespace
from collections import abc as cabc
#</Imports

#> Header >/
__all__ = ('PatternComposeException', 'exceptions',
           'REFPATT_PATT', 'get_refpatt_parts', 'compile_refpatt',
           'PatternComposer')

def _tostr(v: str | bytes) -> str:
    if isinstance(v, str): return v
    return v.decode()

# Exceptions
exceptions = SimpleNamespace()

## Top-exception
class PatternComposeException(Exception):
    '''
        Base exception for this module
        Note that subclassing this class will automatically add
            the exception to the module level `exceptions` namespace,
            although this behaviour can be suppressed by passing `anonymous=True`
    '''
    __slots__ = ()

    @classmethod
    def __init_subclass__(cls, *, anonymous: bool = False):
        if anonymous: return
        setattr(exceptions, cls.__name__, cls)
exceptions.PatternComposeException = PatternComposeException

## Sub-exceptions
class PatternExistsError(PatternComposeException):
    '''For when a pattern already exists and won't be replaced'''
    __slots__ = ()
del PatternExistsError
class PatternNotFoundError(PatternComposeException, KeyError):
    '''For when a referenced pattern is missing'''
    __slots__ = ()
del PatternNotFoundError
class RequiredPatternError(PatternComposeException):
    '''For when an attempt was made to remove a pattern that other patterns depended on'''
    __slots__ = ()
del RequiredPatternError
class IncompletePatternError(PatternComposeException):
    '''For when a pattern needs to be complete, but isn't'''
    __Slots__ = ()
del IncompletePatternError

# "Reference"-pattern matching
REFPATT_PATT = re.compile(r'\(\?~([\w\d\.]+?)\)')

def get_refpatt_parts(patt: str | bytes, *, refpatt_patt: re.Pattern = REFPATT_PATT) -> tuple[str, ...]:
    '''Finds all of the "reference"-pattern part names in `patt`'''
    if (parts := refpatt_patt.findall(patt)):
        return tuple(map(_tostr, parts))
    return tuple()
def compile_refpatt(patt: str | bytes, patts: dict[str, str | bytes], *, allow_partial: bool = False,
                    refpatt_patt: re.Pattern = REFPATT_PATT) -> str | bytes:
    '''
        Replaces all "reference"-pattern parts in `patt` with their values in `patts`
        If `allow_partial`, then any missing patterns will be ignored and will be left in
    '''
    def comp(m: re.Match) -> str | bytes:
        p = m.group(1)
        ipatt = patts.get(_tostr(p), None)
        if ipatt is None:
            if allow_partial: return m.group(0)
            raise exceptions.PatternNotFoundError(f'Detected missing referenced pattern near {patt!r}: {p!r}')
        return compile_refpatt(ipatt, patts, allow_partial=allow_partial, refpatt_patt=refpatt_patt)
    return refpatt_patt.sub(comp, patt)

# Composer
class PatternComposer:
    '''
        Provides methods and state required to manage "reference"-patterns
            Use `.add()` or `.add_multi()` to add new patterns,
            `.remove()` to remove patterns,
            and the "getitem" (`[]`, `__getitem__()`) protocol to get complete patterns (as strings/bytes)
        Note that, even in bytes_mode, names are expected to be strings (and will be translated to strings)
        The default (pseudo-pattern) for "reference"-patterns is `(?~<name>)`,
            this will be used for the following examples:
          - `ex0`: `((?~ex1)) | ((?~ex2)) | ((?~ex3))` -> `(abc) | (bc) | (bcd)`
          - `ex1`: `a(?~ex2)`                          -> `abc`
          - `ex2`: `bc`                                -> `bc`
          - `ex3`: `(?~ex2)d`                          -> `bcd`
    '''
    __slots__ = ('bytes_mode', 'patterns', 'references', 'compiled', 'refpatt_patt')

    bytes_mode: bool
    patterns: dict[str, str | bytes]
    references: dict[str, frozenset[str]]
    compiled: dict[str, str | bytes]
    refpatt_patt: re.Pattern

    def __init__(self, *, bytes_mode: bool = False, refpatt_patt: re.Pattern = REFPATT_PATT):
        self.bytes_mode = bytes_mode
        self.patterns = {}
        self.references = {}
        self.compiled = {}
        self.refpatt_patt = re.compile(refpatt_patt.pattern.encode(),
                                       flags=refpatt_patt.flags & ~re.UNICODE) if bytes_mode else refpatt_patt

    def _chk_type(self, val: str | bytes) -> bool:
        if self.bytes_mode:
            return isinstance(val, bytes)
        return isinstance(val, str)
    def _fail_type(self, val: str | bytes, msg: str) -> None:
        if not self._chk_type(val): raise TypeError(msg)

    def find_referrers(self, name: str | bytes) -> cabc.Generator[str, None, None]:
        '''Yields each referrer that refers to `name`'''
        name = _tostr(name)
        for refr,refd in self.references.items():
            if name in refd: yield refr
    def find_referrers_recursive(self, name: str | bytes, *, _store: set[str] | None = None) -> frozenset[str] | None:
        '''
            Returns a `frozenset` of each referrer that refers to name,
                and each referrer that refers to each of those
        '''
        name = _tostr(name)
        top = _store is None
        if top: _store = set()
        for refr in self.find_referrers(name):
            _store.add(refr)
            self.find_referrers_recursive(refr, _store=_store)
        if top: return frozenset(_store)
        return None

    def is_complete(self, name: str | bytes, *, recurse: bool = True) -> bool | None:
        '''
            If `name` is missing, returns `None`
            Otherwise, returns whether or not `name`'s references are satisfied,
                as well as if each of its references' references are satisfied recursively if `recurse`
        '''
        name = _tostr(name)
        if name not in self.references: return None
        if self.references[name] - self.patterns.keys(): return False
        return (not recurse) or all(map(self.is_complete, self.references[name]))
    def list_incomplete(self) -> frozenset[str | bytes]:
        '''
            Returns a `frozenset` of all patterns that are missing references
                Uses the `recursive` mode of `.is_complete()`
        '''
        return frozenset(itertools.filterfalse(self.is_complete, self.patterns.keys()))

    def update(self, name: str | bytes, *, update_referrers: bool = True, ignore_missing: bool = False) -> None:
        '''
            Updates (compiles) the pattern `name`
            Updates referrers as well if `update_referrers`,
                passing them along with name to `.multiupdate()` for better efficiency
        '''
        name = _tostr(name)
        if name not in self.patterns:
            if ignore_missing: return
            raise exceptions.PatternNotFoundError(f'Cannot update non-existing pattern {name!r}')
        if update_referrers and (referrers := self.find_referrers(name)):
            return self.multiupdate(name, *referrers)
        self.compiled[name] = compile_refpatt(self.patterns[name], self.patterns, allow_partial=True, refpatt_patt=self.refpatt_patt)
    def multiupdate(self, *names: str | bytes, update_referrers: bool = True, ignore_missing: bool = False) -> None:
        '''
            Updates all patterns in `names`
            More efficient than `.update()` as it avoids recursively updating
                referrers multiple times (if `update_referrers`)
        '''
        if not names: return frozenset()
        names = frozenset(map(_tostr, names))
        if (not ignore_missing) and (missing := (names - self.patterns.keys())):
            e = exceptions.PatternNotFoundError(f'Cannot update {len(missing)} non-existing pattern(s)')
            e.add_note(f'Missing patterns: {(b", " if self.bytes_mode else ", ").join(missing)}')
            raise e
        referrers = frozenset.union(*map(self.find_referrers_recursive, names)) - names
        for name in itertools.chain(names, referrers):
            self.update(name, update_referrers=False)

    def add(self, name: str | bytes, patt: str | bytes, *, replace: bool = False) -> None:
        '''
            Adds a single pattern `patt` with name `name`,
                populating its references and compiling it
            If a pattern already exists, and not `replace`, then `exceptions.PatternExistsError` is raised
        '''
        name = _tostr(name)
        self._fail_type(patt, f'Incorrect type for patt: {patt!r}')
        if (not replace) and (patt in self.patterns):
            raise exceptions.PatternExistsError(f'Cannot replace an existing pattern {name!r}')
        self.patterns[name] = patt
        self.references[name] = frozenset(get_refpatt_parts(patt, refpatt_patt=self.refpatt_patt))
        self.update(name)
    def multiadd(self, patts: dict[str | bytes, str | bytes], *, replace: bool = False) -> None:
        '''
            Adds multiple patterns
                More efficient than multiple calls to `.add()`, as it uses `.multiupdate()`
                    and waits to execute updates until all patterns have been added
            If any patterns already exist, and not `replace`, then `exceptions.PatternExistsError` is raised
        '''
        if (not replace) and (exists := (patts.keys() & self.patterns.keys())):
            e = exceptions.PatternExistsError(f'Cannot replace {len(exists)} existing pattern(s)')
            e.add_note(f'Existing patterns: {(b", " if self.bytes_mode else ", ").join(exists)}')
            raise e
        for n,p in patts.items():
            self._fail_type(patt, f'Incorrect type for pattern in patts for {name!r}: {patt!r}')
        for n,p in patts.items():
            n = _tostr(name)
            self.patterns[n] = p
            self.references[n] = frozenset(get_refpatt_parts(p))
        self.multiupdate(*patts.keys())

    def remove(self, name: str | bytes, *, update_referrers: bool | None = True, ignore_missing: bool = False) -> None:
        '''
            Removes a pattern
            If `update_referrers` is `None`, referrers are ignored;
                other falsey values will cause an `exceptions.RequiredPatternError` to be raised if referrers are present
        '''
        name = _tostr(name)
        if name not in self.patterns:
            if ignore_missing: return
            raise exceptions.PatternNotFoundError(f'Cannot remove non-existing pattern {name!r}')
        referrers = frozenset(self.find_referrers(name))
        del self.patterns[name]
        del self.references[name]
        del self.compiled[name]
        if (not referrers) or (update_referrers is None): return
        if not update_referrers:
            e = exceptions.RequiredPatternError(f'Cannot remove pattern {name!r}, as there are other patterns that refer to it')
            e.add_note(f'Referrers: {(b", " if self.bytes_mode else ", ").join(map(repr, referrers))}')
            raise e
        self.multiupdate(*referrers)

    def __getitem__(self, name: str | bytes) -> str | bytes:
        name = _tostr(name)
        if name not in self.references:
            raise exceptions.PatternNotFoundError(f'Pattern {name} does not exist')
        if (missing := (self.references[name] - self.patterns.keys())):
            e = exceptions.IncompletePatternError(f'Pattern {name} is incomplete')
            e.add_note(f'Missing patterns: {(b", " if self.bytes_mode else ", ").join(missing)}')
            raise e
        return self.compiled[name]
