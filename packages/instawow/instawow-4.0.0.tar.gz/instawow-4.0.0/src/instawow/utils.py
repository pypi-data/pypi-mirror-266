from __future__ import annotations

import asyncio
import importlib.resources
import os
import string
import sys
import time
from collections.abc import (
    Awaitable,
    Callable,
    Hashable,
    Iterable,
    Iterator,
    Sequence,
)
from contextlib import contextmanager
from functools import partial, wraps
from itertools import chain, groupby, islice, repeat
from pathlib import Path
from shutil import move
from tempfile import mkdtemp
from types import ModuleType
from typing import TYPE_CHECKING, Any, TypeVar, overload
from weakref import WeakValueDictionary

import attrs
from typing_extensions import ParamSpec

_T = TypeVar('_T')
_U = TypeVar('_U')
_THashable = TypeVar('_THashable', bound=Hashable)
_P = ParamSpec('_P')


if sys.version_info >= (3, 11):
    from enum import StrEnum as StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        @staticmethod
        def _generate_next_value_(name: str, start: int, count: int, last_values: list[object]):
            return name.lower()


if TYPE_CHECKING:
    fauxfrozen = attrs.frozen
else:
    fauxfrozen = partial(attrs.define, unsafe_hash=True)


def read_resource_as_text(package: ModuleType, resource: str, encoding: str = 'utf-8') -> str:
    return importlib.resources.files(package).joinpath(resource).read_text(encoding)


class TocReader:
    """Extracts key-value pairs from TOC files."""

    def __init__(self, contents: str) -> None:
        self.entries = {
            k: v
            for e in contents.splitlines()
            if e.startswith('##')
            for k, v in (map(str.strip, e.lstrip('#').partition(':')[::2]),)
            if k
        }

    def __getitem__(self, key: str | tuple[str, ...]) -> str | None:
        if isinstance(key, tuple):
            return next(filter(None, map(self.entries.get, key)), None)
        else:
            return self.entries.get(key)

    @classmethod
    def from_path(cls, path: Path) -> TocReader:
        return cls(path.read_text(encoding='utf-8-sig', errors='replace'))


def fill(it: Iterable[_T], fill: _T, length: int) -> Iterable[_T]:
    "Fill an iterable of specified length."
    return islice(chain(it, repeat(fill)), 0, length)


def bucketise(iterable: Iterable[_U], key: Callable[[_U], _T]) -> dict[_T, list[_U]]:
    "Place the elements of an iterable in a bucket according to ``key``."
    bucket = dict[_T, list[_U]]()

    for value in iterable:
        bucket.setdefault(key(value), []).append(value)

    return bucket


def chain_dict(
    keys: Iterable[_T], default: _U, *overrides: Iterable[tuple[_T, _U]]
) -> dict[_T, _U]:
    "Construct a dictionary from a series of two-tuple iterables with overlapping keys."
    return dict(chain(zip(keys, repeat(default)), *overrides))


def uniq(it: Iterable[_THashable]) -> list[_THashable]:
    "Deduplicate hashable items in an iterable maintaining insertion order."
    return list(dict.fromkeys(it))


def all_eq(it: Iterable[object]) -> bool:
    "Check that all elements of an iterable are equal."
    groups = groupby(it)
    return next(groups, True) and not next(groups, False)


def merge_intersecting_sets(it: Iterable[frozenset[_T]]) -> Iterator[frozenset[_T]]:
    "Recursively merge intersecting sets in a collection."
    many_sets = list(it)
    while many_sets:
        this_set = many_sets.pop(0)
        while True:
            for idx, other_set in enumerate(many_sets):
                if not this_set.isdisjoint(other_set):
                    this_set |= many_sets.pop(idx)
                    break
            else:
                break
        yield this_set


@overload
async def gather(it: Iterable[Awaitable[_U]], wrapper: None = None) -> list[_U]: ...


@overload
async def gather(
    it: Iterable[Awaitable[_U]],
    wrapper: Callable[[Awaitable[_U]], Awaitable[_T]],
) -> list[_T]: ...


async def gather(
    it: Iterable[Awaitable[object]], wrapper: Callable[..., Awaitable[object]] | None = None
) -> Sequence[object]:
    if wrapper is not None:
        it = map(wrapper, it)
    return await asyncio.gather(*it)


def run_in_thread(fn: Callable[_P, _U]) -> Callable[_P, Awaitable[_U]]:
    @wraps(fn)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs):
        return asyncio.to_thread(fn, *args, **kwargs)

    return wrapper


def tabulate(rows: Sequence[tuple[object, ...]], *, max_col_width: int = 60) -> str:
    "Produce an ASCII table from equal-length elements in a sequence."
    from textwrap import fill

    def apply_max_col_width(value: object):
        return fill(str(value), width=max_col_width, max_lines=1)

    def calc_resultant_col_widths(rows: Sequence[tuple[str, ...]]):
        cols = zip(*rows)
        return [max(map(len, c)) for c in cols]

    norm_rows = [tuple(apply_max_col_width(i) for i in r) for r in rows]
    head, *tail = norm_rows

    base_template = '  '.join(f'{{{{{{0}}{w}}}}}' for w in calc_resultant_col_widths(norm_rows))
    row_template = base_template.format(':<')
    table = '\n'.join(
        (
            base_template.format(':^').format(*head),
            base_template.format('0:-<').format(''),
            *(row_template.format(*r) for r in tail),
        )
    )
    return table


def trash(paths: Iterable[Path], *, dest: Path, missing_ok: bool = False) -> None:
    paths_iter = iter(paths)
    first_path = next(paths_iter, None)

    if first_path is None:
        return

    exc_classes = FileNotFoundError if missing_ok else ()

    parent_folder = mkdtemp(dir=dest, prefix=f'deleted-{first_path.name}-')

    for path in chain((first_path,), paths_iter):
        try:
            move(path, parent_folder)
        except exc_classes:
            pass


def shasum(*values: object) -> str:
    "Base-16-encode a string using SHA-256 truncated to 32 characters."
    from hashlib import sha256

    return sha256(''.join(map(str, filter(None, values))).encode()).hexdigest()[:32]


def is_file_uri(uri: str) -> bool:
    return uri.startswith('file://')


def file_uri_to_path(file_uri: str) -> str:
    "Convert a file URI to a path that works both on Windows and *nix."
    from urllib.parse import unquote

    unprefixed_path = unquote(file_uri.removeprefix('file://'))
    # A slash is prepended to the path even when there isn't one there
    # on Windows.  The ``Path`` instance will inherit from either
    # ``PurePosixPath`` or ``PureWindowsPath``; this will be a no-op on POSIX.
    if Path(unprefixed_path[1:]).drive:
        unprefixed_path = unprefixed_path[1:]
    return unprefixed_path


def as_plain_text_data_url(body: str = '') -> str:
    from urllib.parse import quote

    return f'data:,{quote(body)}'


def extract_byte_range_offset(content_range: str):
    return int(content_range.replace('bytes ', '').partition('-')[0])


def normalise_names(replace_delim: str) -> Callable[[str], str]:
    trans_table = str.maketrans(dict.fromkeys(string.punctuation, ' '))

    def normalise(value: str):
        return replace_delim.join(value.casefold().translate(trans_table).split())

    return normalise


slugify = normalise_names('-')


def reveal_folder(path: str | os.PathLike[str]) -> None:
    if sys.platform == 'win32':
        os.startfile(path, 'explore')
    else:
        import click

        click.launch(os.fspath(path), locate=True)


@contextmanager
def time_op(on_complete: Callable[[float], None]) -> Iterator[None]:
    start = time.perf_counter()
    yield
    on_complete(time.perf_counter() - start)


class WeakValueDefaultDictionary(WeakValueDictionary[_T, _U]):
    def __init__(self, default_factory: Callable[[], _U]) -> None:
        super().__init__()
        self.__default_factory = default_factory

    def __getitem__(self, key: _T) -> _U:
        try:
            return super().__getitem__(key)
        except KeyError:
            default = self[key] = self.__default_factory()
            return default


def add_exc_note(exc: BaseException, note: str) -> None:
    if sys.version_info >= (3, 11):
        exc.add_note(note)

    else:
        exc_without_notes: Any = exc

        if not hasattr(exc, '__notes__'):
            exc_without_notes.__notes__ = list[str]()
        exc_without_notes.__notes__.append(note)
