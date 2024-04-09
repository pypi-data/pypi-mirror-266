import collections
import functools
import operator
import os
import sys
import tempfile
import uuid
import click
import concurrent.futures
import contextlib
import re

def identity(a0, *args):
    return (a0,) + args if args else a0

@functools.cache
def where(program, require=True):
    possible_extensions = ['']
    if sys.platform == "win32" and not program.lower().endswith(".exe"):
        possible_extensions += [".exe", ".py"]

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, _ = os.path.split(program)
    if fpath:
        if is_exe(program):
            return [program]
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            for ext in possible_extensions:
                exe_file = os.path.join(path, program+ext)
                if is_exe(exe_file):
                    if sys.platform == "win32" and ext == '.py':
                        return ['python3', exe_file]
                    return [exe_file]
    if require:
        click.secho(f"error: cannot find executable '{program}'", fg='red', bold=True, err=True)
        sys.exit(1)
    return []

def require_exe(exe):
    where(exe, require=True)

def random_filename(ext='.bin', prefix=''):
    return prefix+uuid.uuid4().hex + ext

@contextlib.contextmanager
def temp_with_content(content, dir=None, suffix=None):
    fd, path = tempfile.mkstemp(dir=dir, suffix=suffix)
    try:
        with os.fdopen(fd, 'wb') as tmp:
            tmp.write(content.encode('utf-8'))
            tmp.flush()
        yield path
    finally:
        os.remove(path)

def parallel(lst, func, progressbar=None, show_pos=False, max_workers=None, item_count=None, keep_input=True):
    f = (lambda x: (x, func(x))) if keep_input else func
    max_workers = max_workers or os.cpu_count() or 4
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers or os.cpu_count() or 4) as executor:
        with contextlib.ExitStack() as c:
            if max_workers == 1:
                items = map(f, lst)
            else:
                items = executor.map(f, lst)
            if progressbar is not None:
                try:
                    item_count = item_count or len(lst)
                except:
                    pass
                items = c.enter_context(click.progressbar(items, length=item_count, label=progressbar, show_pos=show_pos, file=sys.stderr))
            for item in items:
                yield item

def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(_nsre, s)]

def flatten(iter):
    if isinstance(iter, collections.abc.Iterable) and not isinstance(iter, (tuple, dict)):
        for e in iter:
            yield from flatten(e)
    else:
        yield iter

def group_by(key, seq):
    return dict(functools.reduce(lambda grp, val: grp[key(val)].append(val) or grp, seq, collections.defaultdict(list)))

def order(iter, ordered_keys, key=identity):
    head, rest = partition(iter, lambda e: key(e) in ordered_keys)
    head.sort(key=lambda e: ordered_keys.index(key(e)))
    return head + rest

def get_in(obj, *keys):
    for k in keys:
        v = None
        try:
            v = operator.itemgetter(k)(obj)
        except (TypeError, KeyError):
            pass
        if v is None:
            return None
        obj = v
    return obj

def sget_in(obj, *keys):
    r = get_in(obj, *keys)
    if r is None:
        return ''
    return str(r)

def unique(lst, key=None, group=False):
    seen = {}
    out = []
    if key is None:
        key = lambda *x: x
    for x in lst:
        k = key(x)
        if not group:
            if k in seen:
                continue
            out.append(k)
        else:
            if k in seen:
                out[seen[k]][1].append(x)
            else:
                out.append((key(x), [x]),)
                seen[key(x)] = len(out)-1
    return out

def partition(iter, pred):
    t, f = [], []
    for e in iter:
        (t if pred(e) else f).append(e)
    return t, f

def sliding_window(iterable, n=3):
    iterable = iter(iterable)
    window = collections.deque(maxlen=n)
    try:
        for i in range(n):
            window.append(next(iterable))
    except StopIteration:
        pass
    yield list(window)
    for e in iterable:
        window.append(e)
        yield list(window)
    while len(window) > 1:
        window.popleft()
        yield list(window)

def sizeof_fmt(num, suffix='B'):
    num = float(num)
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def timestamp_fmt(s, short=False):
    m, s = divmod(s, 60)
    h, m = divmod(int(m), 60)
    h = f'{h}:' if h or not short else ''
    return f'{h}{int(m):02d}:{s:05.2f}'

def sizeof_parse(file_size):
    suffixes = {
        'b': 1,
        'k': 1024,
        'm': 1024 ** 2,
        'g': 1024 ** 3,
        't': 1024 ** 4,
        'p': 1024 ** 5,
    }
    size = float(file_size[:-1] or file_size)
    suffix = file_size[-1:].lower()
    if suffix in suffixes:
        return int(size * suffixes[suffix])
    else:
        return int(file_size)

def safe_filename(s):
    s = re.sub(r'(\w)(: +)', r'\1 - ', s)
    for c in '/\\:':
        s = s.replace(c, '-')
    s = s.replace('"', "'")
    for c in '?<>|*':
        s = s.replace(c, '_')
    return s.strip()

def remap_linear(val: float, in_range=(0,1), out_range=(0,1)) -> float:
    in_min, in_max = sorted(in_range)
    out_min, out_max = sorted(out_range)
    if in_max == in_min or out_max == out_min:
        raise ValueError("Invalid range")
    if val < in_min or val > in_max:
        raise ValueError(f"Value {val} is outside the input range {in_range}")
    in_range_span, out_range_span = in_max - in_min, out_max - out_min
    normalized_val = (val - in_min) / in_range_span
    if (in_range[0] > in_range[1] and out_range[0] < out_range[1]) or \
       (in_range[0] < in_range[1] and out_range[0] > out_range[1]):
        normalized_val = 1 - normalized_val
    return out_min + (normalized_val * out_range_span)

def remap_point2point(val, *points):
    for (p1, p2) in sliding_window(points, 2):
        p_min, p_max = sorted([p1[0], p2[0]])
        if p_min <= val <= p_max:
            return remap_linear(val, (p1[0], p2[0]), (p1[1], p2[1]))
    raise ValueError()

def common_dir(paths):
    if not paths:
        return None
    abspaths = list(os.path.abspath(p) for p in paths)
    if len(abspaths) > 1:
        return os.path.commonpath(abspaths)
    return os.path.dirname(abspaths[0])

class log(object):
    @staticmethod
    def fatal(s, err=True):
        click.secho('error: ', fg='red', bold=True, nl=False, err=err)
        click.secho(s, fg='red', err=err)
        sys.exit(1)

    @staticmethod
    def warn(s, err=True):
        click.secho('warning: ', fg='yellow', bold=True, nl=False, err=err)
        click.secho(s, fg='yellow', err=err)

    @staticmethod
    def info(s, err=True):
        click.secho(s, fg='green', err=err)

    @staticmethod
    def info2(*s, fg='bright_green', bold=True, err=True, nl=True):
        for i, p in enumerate(s):
            click.secho(p, nl=False, fg=fg, bold=bold, err=err) if i % 2 else click.echo(p, nl=False, err=err)
        if nl:
            click.echo(err=err)

def print_csv(src, delimiter=',', err=False):
    import csv
    import unicodedata
    r = csv.reader(unicodedata.normalize('NFC', src).split('\n'), delimiter=delimiter)
    lines = list(r)
    if not lines or not lines[0]:
        return
    col_w = [max(len(r[c]) for r in lines) for c in range(len(lines[0]))]
    for r in lines:
        click.echo(' '.join(s.ljust(w+1) if i == 0 else s.rjust(w+2) for i, (s, w) in enumerate(zip(r, col_w))), err=err)

def read_until(r, sentinel=b'\x0A', max_len=64):
    buf = bytearray()
    while True:
        b = r.read(1)
        buf.extend(b)
        if b == sentinel:
            return buf
        if (max_len or 0) > 0 and len(buf) > max_len:
            return

def fs_expand(paths, allowed_ext=None, recursive=False):
    recursive_paths = []
    for p in paths:
        if p.startswith('./') or p.startswith('.\\'):
            p = p[2:]
        if os.path.isfile(p):
            yield p
        elif os.path.isdir(p):
            for f in os.listdir(p):
                _, ext = os.path.splitext(f)
                if not f.startswith('.'):
                    path = os.path.join(p, f) if p != '.' else f
                    if os.path.isfile(path) and (allowed_ext is None or ext in allowed_ext):
                        yield path
                    elif recursive and os.path.isdir(path):
                        recursive_paths.append(path)
    if recursive and recursive_paths:
        yield from fs_expand(recursive_paths, allowed_ext=allowed_ext, recursive=recursive)

class MIME(object):
    AUDIO = {
        '.aac': 'audio/aac',
        '.aif': 'audio/aiff',
        '.aifc': 'audio/aiff',
        '.aiff': 'audio/aiff',
        '.alac': 'audio/mp4',
        '.ape': 'audio/ape',
        '.flac': 'audio/flac',
        '.m4a': 'audio/mp4a-latm',
        '.m4b': 'audio/mp4a-latm',
        '.mka': 'audio/x-matroska',
        '.mp3': 'audio/mpeg',
        '.mp4': 'audio/mp4',
        '.mpc': 'audio/x-musepack',
        '.oga': 'audio/ogg',
        '.ogg': 'audio/ogg',
        '.opus': 'audio/ogg',
        '.wav': 'audio/vnd.wav',
        '.webm': 'audio/webm',
        '.wma': 'audio/x-ms-wma',
    }
    VIDEO = {
        '.3gp': 'video/3gpp',
        '.avi': 'video/x-msvideo',
        '.flv': 'video/x-flv',
        '.m4v': 'video/mp4',
        '.mkv': 'video/x-matroska',
        '.mov': 'video/quicktime',
        '.mp4': 'video/mp4',
        '.mpeg': 'video/mpeg',
        '.ogv': 'video/ogg',
        '.qt': 'video/quicktime',
        '.ts': 'video/mp2t',
        '.webm': 'video/webm',
        '.wmv': 'video/x-ms-wmv',
    }
    IMAGE = {
        '.avif': 'image/avif',
        '.bmp': 'image/bmp',
        '.gif': 'image/gif',
        '.ico': 'image/x-icon',
        '.jpeg': 'image/jpeg',
        '.jpg': 'image/jpeg',
        '.png': 'image/png',
        '.svg': 'image/svg+xml',
        '.tif': 'image/tiff',
        '.tiff': 'image/tiff',
        '.webp': 'image/webp',
    }
