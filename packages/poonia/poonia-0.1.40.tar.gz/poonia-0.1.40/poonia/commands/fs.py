#!/usr/bin/env python3
import codecs
import fnmatch
import functools
import glob
from collections import defaultdict, namedtuple
import datetime
import hashlib
import json
import math
import random
import shutil
import subprocess
import time
import unicodedata
import uuid
import click
import os
import sys
import re
from poonia.text import RegexSub
from poonia.utils import log
from poonia import utils


@click.group(help="File tools")
def fs(): pass

def pglob(pattern, recurse=False):
    matches = []
    if recurse:
        for root, dirnames, filenames in os.walk('.', topdown=False):
            for filename in fnmatch.filter(filenames, pattern):
                m = os.path.join(root, filename)
                if os.path.isfile(m):
                    matches.append(m)
    else:
        for fn in glob.glob(pattern):
            matches.append(fn)
    return matches

def print_to_rename(changed):
    for src, dst in changed:
        directory_path, filename = os.path.split(src)
        click.secho(directory_path+os.path.sep, fg='blue', nl=False)
        click.secho(filename, bold=True, fg='bright_red', nl=False)
        click.secho(' -> ', nl=False)
        click.secho(dst, bold=True, fg='bright_green', nl=True)

def mangle_filename(filename):
    digits = ''.join(random.choice('abcdef0123456789') for _ in range(6))
    return f'tmp{digits}.{filename}'

def rename_ops_order(pairs):
    if len(set(pairs.values())) < len(pairs):
        return None
    existing = set(pairs.keys())
    ops = []
    opsLen = -1
    todo = list((k,v) for k,v in pairs.items() if k!=v)
    while len(ops) != opsLen:
        opsLen = len(ops)
        skipped = []
        for pre, post in todo:
            if post in existing:
                skipped.append((pre, post))
                continue
            existing.remove(pre)
            existing.add(post)
            ops.append((pre, post))
        todo = skipped
        if len(ops) == opsLen and len(todo) > 0:
            (pre, post), todo = todo[0], todo[1:]
            mangled = mangle_filename(pre)
            ops.append((pre, mangled))
            todo.append((mangled, post))
            existing.add(mangled)
            existing.remove(pre)
    if not skipped:
        return ops


@fs.command(help='Rename files/directories inside a text editor')
@click.argument('paths', nargs=-1, type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('-d', '--rename-dirs', is_flag=True)
@click.option('--re', 'regex', help='text replace with regex', nargs=2)
@click.option('--rex', 'regex_eval', help='eval expression with regex', nargs=2)
@click.option('--hidden', '-H', help='include hidden files', is_flag=True)
@click.option('--by-length', help='sort by name length', is_flag=True)
def rename(paths, rename_dirs, regex, regex_eval, hidden, by_length):
    basename = os.path.basename
    def dirname(p): return os.path.split(p)[0]
    if not paths:
        paths = ['.']
    objects = []
    for path in paths:
        all = sorted([f for f in os.listdir(path) if hidden or not f.startswith('.')], key=utils.natural_sort_key)
        objects.extend(os.path.join(path, base) for base in all)
    if by_length:
        objects.sort(key=lambda x: len(os.path.basename(x)), reverse=True)
    dirs, files = utils.partition(objects, os.path.isdir)

    to_rename = dirs if rename_dirs else files
    original = '\n'.join(basename(path) for path in to_rename)
    renamed = ''
    if regex or regex_eval:
        match, replacement, eval = (regex[0], regex[1], False) if regex else (regex_eval[0], regex_eval[1], True)
        try:
            renamed = RegexSub.sub(match, replacement, original, evaluate=eval)
        except (IndexError, SyntaxError) as e:
            utils.log.fatal(e)
    else:
        renamed = click.edit(original)
        if renamed:
            renamed = renamed.rstrip()

    if (not renamed or renamed == original):
        log.fatal('nothing''s changed')

    renamed = renamed.split('\n')

    if (len(renamed) != len(to_rename)):
        log.fatal('wrong number of rows')

    ops = []
    for d, pairs in utils.group_by(lambda x: dirname(x[0]), zip(to_rename, renamed)).items():
        renameMap = dict((basename(k),v) for k,v in pairs)
        dirOps = rename_ops_order(renameMap)
        if dirOps is None:
            utils.log.fatal('rename conflict')
        ops += list((os.path.join(d, k), os.path.join(d, v)) for k,v in dirOps)

    changed = [(a, b) for a, b in zip(to_rename, renamed) if basename(a) != b]
    print_to_rename(changed)
    click.confirm(f'Do you want to rename {len(changed)} files?', abort=True)

    with click.progressbar(ops, label='Renaming') as ops:
        for a, b in ops:
            os.rename(a, b)
    click.secho('Objects has been renamed!', fg='green', bold=True)


def hasext(fn, ext):
    _, fileext = os.path.splitext(fn)
    return fileext.lstrip('.').lower() in ext


@fs.command(help='Delete files without pair')
@click.option('-e', '--extensions', type=str, default='jpg,rw2', show_default=True)
def pairdel(extensions):
    extensions = set(e.lower() for e in extensions.split(','))
    files = [f for f in os.listdir('.') if os.path.isfile(
        f) and hasext(f, extensions)]
    filext = defaultdict(set)
    for fn in files:
        name, ext = os.path.splitext(fn)
        filext[name].add(ext)
    todelete = []
    for fn, fes in filext.items():
        accept = True
        for e in extensions:
            if not any(hasext(fn+fe, [e]) for fe in fes):
                accept = False
        if not accept:
            todelete.append([fn, fes])

    total_bytes = 0
    filenames_to_delete = []
    for fn, fes in sorted(todelete):
        for a in [fn+fe for fe in fes]:
            filenames_to_delete.append(a)
            click.echo(a, nl=False)
            click.echo(' [', nl=False)
            fsize = os.path.getsize(a)
            total_bytes += fsize
            click.secho('%s' % utils.sizeof_fmt(fsize), nl=False, fg='red')
            click.echo(']')
    click.echo()
    if click.confirm('Delete listed files [%s]?' % utils.sizeof_fmt(total_bytes)):
        for a in filenames_to_delete:
            os.remove(a)


@fs.command(help='Securely delete specified file')
@click.argument('input', type=click.Path(writable=True))
def sdel(input):
    def _random_sample(population, k=1):
        lst = list(population)
        random.shuffle(lst)
        return lst[:k]

    def _getsize(f):
        old_file_position = f.tell()
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(old_file_position, os.SEEK_SET)
        return size

    def _rename_random(path):
        dirname, base = os.path.dirname(path), os.path.basename(path)
        for c in _random_sample('0123456789abcdefABCDEF', k=3):
            new_base = c * len(base)
            if new_base == base:
                continue
            new_path = os.path.join(dirname, new_base)
            try:
                os.rename(path, new_path)
                path = new_path
            except:
                pass
        return path

    def _randombytes(size):
        return bytearray(os.urandom(size))

    def _remove_file(fd, progressbar=True):
        filesize = _getsize(fd)
        MB = 1024**2
        if progressbar:
            with click.progressbar(range(0, filesize, MB)) as bar:
                for i in range(0, filesize, MB):
                    remains = min(MB, filesize - i)
                    fd.write(_randombytes(remains))
                    bar.update(remains)
        else:
            for i in range(0, filesize, MB):
                remains = min(MB, filesize - i)
                fd.write(_randombytes(remains))
        os.fsync(fd)
        fd.close()
        renamed = _rename_random(fd.name)
        os.remove(renamed)

    if os.path.isdir(input):
        dirlst = sorted((
            (dpath.count(os.path.sep), dpath, dnames, fnames)
            for dpath, dnames, fnames in os.walk(input, topdown=False)
        ), reverse=True)
        to_remove = utils.flatten(
            ([(False, os.path.join(path, p)) for p in dirs] + [(True, os.path.join(path, p)) for p in files])
            for _, path, dirs, files in dirlst
        )
        with click.progressbar(list(to_remove)) as bar:
            for (is_file, p) in bar:
                if is_file:
                    _remove_file(open(p, 'r+b'), progressbar=False)
                else:
                    os.rmdir(_rename_random(p))
        os.rmdir(input)
    else:
        _remove_file(open(input, 'r+b'))


@fs.command(help='Flip random bits in file')
@click.argument('file', type=click.File(mode='rb', lazy=False))
@click.option('-n', type=int, default=1, show_default=True, help='How many file to create')
@click.option('-b', type=int, default=1, show_default=True, help='How many bits to swap')
def bitrot(file, n, b):
    original_data = bytearray(file.read())
    for _ in range(n):
        tries = 0
        while tries < 10:
            data = original_data.copy()
            bit_locations = random.sample(range(len(data)*8), b)

            for loc in bit_locations:
                byte_index = loc // 8
                bit_index = loc % 8
                data[byte_index] ^= (1 << bit_index)

            new_filename = f'{os.path.splitext(file.name)[0]}_' + '_'.join(str(x) for x in sorted(bit_locations)) + os.path.splitext(file.name)[1]
            try:
                with open(new_filename, 'xb') as f:
                    f.write(data)
            except FileExistsError:
                log.warn(f"file '{new_filename}' already exists")
                tries += 1
                continue
            log.info2("File saved as '", new_filename, "'")
            break


def duration_fmt(num):
    if math.isnan(num):
        return '--'
    for unit, m in [('s', 60), ('m', 60), ('h', 24), ('d', 7)]:
        if abs(num) < m:
            return "%3.1f%s" % (num, unit)
        num /= m
    return "%.1f%s" % (num, 'w')


def statformat(stattime, format):
    return time.strftime(format, time.localtime(stattime))


def mtime(fn):
    return os.stat(fn).st_mtime


def h(data): return hashlib.sha1(data).hexdigest()
def avg(lst): return sum(lst) / float(len(lst))


def exiftool_created(fn):
    try:
        r = subprocess.check_output(utils.where('exiftool') + [
            '-j', '-CreateDate', '-FileModifyDate', '--DateTimeOriginal', '--'
        ] + [fn], stderr=subprocess.STDOUT)
        j = json.loads(r.decode('utf-8'))
        d = (utils.sget_in(j, 0, 'CreateDate') or utils.sget_in(
            j, 0, 'FileModifyDate'))[:19]
        return time.mktime(datetime.datetime.strptime(d, '%Y:%m:%d %H:%M:%S').timetuple())
    except subprocess.CalledProcessError as e:
        raise Exception(str(e.output))


class UnixTable:
    CHAR_INNER_VERTICAL = '\033(0\x78\033(B'  # (│)
    CHAR_OUTER_BOTTOM_RIGHT = '\033(0\x6a\033(B'  # (┘)
    CHAR_OUTER_TOP_RIGHT = '\033(0\x6b\033(B'  # (┐)


class WindowsTable:
    """Draw a table using box-drawing characters on Windows platforms. This uses Code Page 437. Single-line borders.
    From: http://en.wikipedia.org/wiki/Code_page_437#Characters
    """
    CHAR_INNER_VERTICAL = b'\xb3'.decode('ibm437')
    CHAR_OUTER_BOTTOM_RIGHT = b'\xd9'.decode('ibm437')
    CHAR_OUTER_TOP_RIGHT = b'\xbf'.decode('ibm437')


class SingleTable(WindowsTable if sys.platform == 'win32' else UnixTable):
    pass


def window(lst):
    a = list(lst)
    return list(zip([None]+a, a, a[1:]+[None]))


@fs.command(help='Group files by creation time')
@click.option('--mtime', 'date_source', type=click.UNPROCESSED, flag_value=mtime, default=True, help='Use file modification date')
@click.option('--exiftool', 'date_source', type=click.UNPROCESSED, flag_value=exiftool_created, help='Use exiftool to obtain creation date')
@click.option('--cutoff', '-c', type=int, default=10, help='Cut-off in seconds', show_default=True)
@click.option('--target', '-t', type=click.Path(exists=False, file_okay=False, writable=True), default='output', help='Target directory')
@click.option('--min', '-m', 'min_series', type=int, default=2, help='Minimum number of files in series', show_default=True)
@click.option('--max', 'max_series', type=int, help='Maximum number of files in series', show_default=True)
@click.argument('paths', nargs=-1, type=click.Path(exists=True, dir_okay=False))
@click.pass_context
def fileseries(ctx, paths, date_source, cutoff, target, min_series, max_series):
    with click.progressbar(paths) as bar:
        paths = [(p, date_source(p)) for p in bar]
    if not paths:
        click.secho('no files to process', fg='red')
        ctx.exit(1)
    paths.sort(key=lambda x: x[1])
    max_length = max(len(x[0]) for x in paths)
    group_n = 0
    new_names = []
    groups = []
    Group = namedtuple('Group', 'path mtime diff_prev diff_next ideogram n')
    for pre, curr, post in window(paths):
        p, mtime = curr
        diff_prev = mtime - pre[1] if pre else float('nan')
        diff_next = post[1] - mtime if post else float('nan')
        ideogram = ''
        if diff_prev < cutoff and diff_next < cutoff:
            ideogram = SingleTable.CHAR_INNER_VERTICAL
        elif diff_prev < cutoff:
            ideogram = SingleTable.CHAR_OUTER_BOTTOM_RIGHT
        elif diff_next < cutoff:
            groups.append([])
            group_n = 0
            ideogram = SingleTable.CHAR_OUTER_TOP_RIGHT
        else:
            groups.append([])
        group_n += 1
        groups[-1].append(Group(p, mtime, diff_prev,
                          diff_next, ideogram, group_n))

    group_total = 0
    for group in groups:
        valid_group = len(group) >= min_series and (
            max_series is None or len(group) <= max_series)
        if valid_group:
            group_total += 1
        for p, mtime, diff_prev, diff_next, ideogram, group_n in group:
            if ideogram and valid_group:
                _, ext = os.path.splitext(p)
                new_name = '%d_%d%s' % (group_total, group_n, ext)
            else:
                new_name = ''

            click.secho("%s  " % p.ljust(max_length), nl=False)
            click.secho(statformat(mtime, r"%Y.%m.%d %H:%M:%S "),
                        nl=False, fg='yellow', bold=True)
            click.secho("%10s " % duration_fmt(diff_prev), fg=(
                'red' if diff_prev > cutoff else 'green'), bold=True, nl=False)
            click.echo(ideogram, nl=False)
            click.secho(" %s" % new_name, fg='blue', bold=True)
            d = mtime
            new_names.append(new_name)

    if click.confirm('Proceed?'):
        if any(new_names):
            os.mkdir(target)
        for path, dst in zip(paths, new_names):
            if not dst:
                continue
            d = os.path.join(target, dst)
            click.echo('%s -> %s' % (path[0], d))
            os.link(path[0], d)


@fs.command(help='Process file through a command stdin/stdout')
@click.argument('command', nargs=1, required=True)
@click.argument('files', type=click.Path(exists=True, dir_okay=False), nargs=-1)
@click.option('--output', '-o', type=click.Path(dir_okay=False), help='output file')
@click.option('--filename', '-f', 'pass_filename', is_flag=True, help='pass filename as argument instead of stdin')
def process(command, files, output, pass_filename):
    for file in files:
        click.secho("Start processing '%s'" % file, fg='yellow', err=True)
        if not output:
            with open(file, 'r+b') as f:
                content = f.read()
                processed = subprocess.check_output(command.split(
                    ' ') + ([file] if pass_filename else []), stderr=subprocess.STDOUT, input=(content if not pass_filename else None))
                f.seek(0)
                f.write(processed)
                f.truncate()
        else:
            with open(file, 'rb') as fr:
                content = fr.read()
                with open(output, 'wb') as fw:
                    processed = subprocess.check_output(command.split(
                        ' ') + ([file] if pass_filename else []), stderr=subprocess.STDOUT, input=(content if not pass_filename else None))
                    fw.write(processed)
        click.secho("File '%s' processed succesfully" % file, fg='green', err=True)


@fs.command(help='Move content of a directory up while combining the filename with dirname')
@click.argument('directories', type=click.Path(exists=True), nargs=-1)
@click.option('--sep', '-s', default='.', help='separator for joining directory names')
@click.option('--ignore', '-i', is_flag=True, help='ignore directory name')
@click.option('--namefromlargest', '-b', is_flag=True, help='Get name prefix from biggest file in parent directory')
@click.option('--yes', '-y', is_flag=True, help='Do not ask for confirmation')
def moveup(directories, sep, ignore, namefromlargest, yes):

    def splitpath(path):
        segments = os.path.normpath(path).split(os.path.sep)
        if segments:
            segments[0] += os.path.sep
        return segments

    def up(path, level=1):
        segments = splitpath(path)
        return os.path.join(*segments[:-level])

    def dircontent(path, _type=None):
        content = [os.path.join(path, f) for f in os.listdir(path)]
        if _type == 'f':
            content = [a for a in content if os.path.isfile(a)]
        return content

    def up_with_prefix(path, prefix):
        base = os.path.basename(path)
        return os.path.join(up(path, 2), prefix+base)

    for directory in directories:
        directory = os.path.abspath(directory)
        if not os.path.isdir(directory):
            click.secho("'%s' is not a directory" % directory, fg='red', err=True)
            continue
        parent = up(directory)
        content = [os.path.join(directory, f) for f in os.listdir(directory)]
        if not content:
            click.secho("'%s' is empty" % directory, fg='red', err=True)
            continue

        prefix = os.path.basename(directory)
        if namefromlargest:
            largest = sorted(dircontent(parent, 'f'),
                             key=os.path.getsize, reverse=True)[:1]
            if not largest:
                click.secho(f"'{parent}' contains no files: cannot find largest", fg='red', err=True)
                continue
            prefix, _ = os.path.splitext(os.path.basename(largest[0]))
        prefix += sep

        job = [(p, up_with_prefix(p, '' if ignore else prefix)) for p in content]
        for src, dst in job:
            click.secho(src, fg='yellow', nl=False)
            click.echo(' -> ')
            click.secho(dst, fg='green')
            click.echo()

        if yes or click.confirm('do you want to continue'):
            for src, dst in job:
                shutil.move(src, dst)
            if not dircontent(directory):
                os.rmdir(directory)
            click.secho('done.', bold=True)


@fs.command(help='Move single dirs one level up, combine names')
@click.option('--sep', default=' - ', help='separator for joining directory names')
def flatten(sep):
    def split(path):
        return os.path.normpath(path).split(os.path.sep)

    def random_name():
        return uuid.uuid4().hex

    def is_single_child(path):
        base, _ = os.path.split(path)
        if base in ('', '.'):
            return False
        return len(os.listdir(base)) == 1

    def replace(path, newname, level=0):
        segments = split(path)
        level = len(segments)-level
        segments[level-1] = newname
        return os.path.join(*segments)

    def renamedir(path, newname, level=0):
        segments = split(path)
        level = len(segments)-level
        oldpath = os.path.join(*segments[:level])
        newpath = replace(oldpath, newname)
        os.rename(oldpath, newpath)
        return newpath

    def moveall(src, dest):
        files = os.listdir(src)
        for f in files:
            shutil.move(os.path.join(src, f), dest)

    def moveup(src, separator):
        segments = split(src)
        name = separator.join([segments[-2], segments[-1]])
        rnd = renamedir(src, random_name())
        renamedir(src, name, level=1)
        rnd = replace(rnd, name, level=1)
        moveall(rnd, os.path.dirname(rnd))
        os.rmdir(rnd)

    def walkdirs(path='.'):
        out = []
        for root, dirs, files in os.walk(path, topdown=False):
            for name in dirs:
                dirpath = os.path.join(root, name)
                out.append(dirpath)
        return out

    def dir_to_flatten():
        try:
            return next(d for d in walkdirs() if is_single_child(d))
        except:
            return None

    while dir_to_flatten():
        d = dir_to_flatten()
        if click.confirm(d):
            moveup(d, sep)


_LANGUAGES = {
    'pl': (u'ąćńłżźę', ['iso-8859-2', 'windows-1250']),
    'es': (u'áéíóúüñ¿¡', ['iso-8859-1', 'windows-1252']),
    'gr': (u'αβγδεζηθικλμνξοπρςστυφχψω', ['iso-8859-7', 'windows-1257']),
    'de': (u'äöüß', ['iso-8859-15', 'windows-1252', 'cp273']),
    'ru': (u'абвгдеёжзийклмнопрстуфхцчшщъыьэюя', ['iso-8859-5', 'windows-1251', 'koi8-r']),
    'ua': (u'абвгдеёжзийклмнопрстуфхцчшщъыьэюя', ['iso-8859-5', 'windows-1251', 'koi8-u']),
}


def fix_encoding(text, language, encoding='utf-8', ignore_errors=False):
    def strip_accents(s):
        s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
        s = s.replace('ł', 'l').replace('Ł', 'L')
        s = s.replace('„', '"').replace('”', '"').replace('…', '...')
        return s
    lang_data = _LANGUAGES.get(language)
    if not lang_data:
        return text

    def grade(s): return sum([s.count(c) for c in lang_data[0]])
    try:
        decoded = []
        for e in lang_data[1] + ['utf-8', 'utf-16', 'utf-32']:
            try:
                decoded.append((e, text.decode(e, 'ignore')))
            except:
                pass
        enc, text = sorted(decoded, key=lambda e: grade(e[1]), reverse=True)[0]
    except:
        pass
    text = text[3:] if text[0:3] == codecs.BOM_UTF8 else text
    errors = 'ignore' if ignore_errors else 'strict'
    if encoding == 'ascii':
        return 'ascii', strip_accents(text).encode(encoding, errors)
    return enc, text.encode(encoding, errors)


@fs.command(help='Fix text encoding')
@click.option('-ext', '--extension', default='srt,txt,ass', show_default=True)
@click.option('-e', '--encoding', default='utf-8', show_default=True)
@click.option('-r', '--recurse', is_flag=True)
@click.option('-l', '--language', default='pl', show_default=True)
@click.option('-b', '--backup', is_flag=True)
@click.option('-i', '--ignore', is_flag=True)
def encoding(extension, encoding, recurse, language, backup, ignore):
    exts = set(extension.split(','))
    to_fix = []
    language = language.lower()
    if language not in _LANGUAGES.keys():
        utils.log.fatal('unknown language')
    for fn in pglob('*', recurse=recurse):
        _, ext = os.path.splitext(fn)
        if ext[1:] not in exts:
            continue
        with open(fn, 'rb') as f:
            text = f.read()
        fixed = fix_encoding(text, language, encoding, ignore)
        if fixed[1] != text:
            to_fix.append([fn, fixed])
    if not to_fix:
        log.fatal('nothing to process')
    for fn, (encoding, content) in to_fix:
        click.secho(fn, fg='green', nl=False)
        click.secho(' [%s]' % encoding, fg='blue')
    if click.confirm('do you want to continue?'):
        for fn, (encoding, content) in to_fix:
            if backup:
                base, ext = os.path.splitext(fn)
                backup_fn = os.path.join(base + '_bak' + ext)
                shutil.copyfile(fn, backup_fn)
            with open(fn, 'wb') as f:
                f.write(content)
            with open(fn, 'wb') as f:
                f.write(content)
        log.info('success')


def levenshtein_distance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1
    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(
                    1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


@fs.command(help='Rename files to closest match with different extension')
@click.option('--change', type=str, default='srt', show_default=True)
@click.option('--match', type=str, default='mkv,avi,mp4', show_default=True)
def pairmatch(change, match):
    def get_files_with_extensions(exts):
        def hasext(fn, ext):
            _, fileext = os.path.splitext(fn)
            return fileext.lstrip('.').lower() in ext
        extensions = set(e.lower() for e in exts)
        return sorted([f for f in os.listdir('.') if os.path.isfile(f) and hasext(f, extensions)])

    def tokenize_unique(arr):
        def tokenize(s):
            s = s.replace("'", '')
            return [x.strip().lstrip('0') for x in re.split(r'(\d+|\W+)', s.lower()) if x and not re.findall('^([^a-z0-9]+)$', x)]
        tokenized = [tokenize(e) for e in arr]
        if not tokenized:
            return []
        common = set(functools.reduce(
            lambda x, y: x.intersection(y), (set(e) for e in tokenized)))
        for c in common:
            for e in tokenized:
                e.remove(c)
        return tokenized

    def common_elements(l1, l2):
        return len([x for x in l1 if x in l2])

    def highrank(arr, key=None):
        if not arr:
            return []
        if not key:
            def key(x): return x
        s = sorted(arr, key=key, reverse=True)
        highkey = key(s[0])
        return [x for x in arr if key(x) == highkey]

    def base(fn): return os.path.splitext(fn)[0]

    to_match = [x for x in get_files_with_extensions(match.split(','))]
    to_match = list(zip(to_match, tokenize_unique(base(f) for f in to_match)))

    files_to_change = [x for x in get_files_with_extensions(change.split(','))]
    tokens = tokenize_unique(base(e) for e in files_to_change)
    used = set()
    to_rename = []
    for f, t in zip(files_to_change, tokens):
        ranked = [(x[0], common_elements(t, x[1]))
                  for x in to_match if x[0] not in used]
        high = highrank(ranked, key=lambda x: x[1])
        if len(high) == 1:
            new_fn = high[0][0]
            used.add(new_fn)
            _, ext = os.path.splitext(f)
            to_rename.append([f, base(new_fn) + ext])
        else:
            to_rename.append([f, None])

    errors = {f[1] for f in to_rename if not f[1] or os.path.exists(f[1])}
    to_rename = [(a, b, b in errors) for a, b in to_rename]
    click.echo('Files to rename:')
    for src, dst, err in to_rename:
        click.secho('  %s' % src, nl=False, fg='red' if err else 'blue')
        click.echo(' -> ', nl=False)
        click.secho(dst, fg='green')
    click.echo()
    to_rename = [(a, b) for a, b, c in to_rename if not c]
    if click.confirm('Rename listed files [%d]?' % len(to_rename)):
        for a, b in to_rename:
            os.rename(a, b)


def exiftool_metadata(filename, filter=True):
    def merge_keys(d, output, *keys):
        keys = [k.lower() for k in keys]
        out = next((str(d[k]) for k in keys if k in d and d[k]), '').strip()
        for k in keys:
            if k in d:
                del d[k]
        if out:
            d[output] = out
    try:
        r = subprocess.check_output(utils.where('exiftool') + ['-j', '-a', '--', filename], stderr=subprocess.STDOUT)
        stdout = r.decode('utf-8')
        tags = json.loads(stdout)[0]
        if filter:
            tags = {k.strip().lower(): v.strip() if isinstance(v, str) else
                    ', '.join(str(x) for x in v) if isinstance(v, list) else v
                    for k, v in tags.items()
                    if k.strip() in {
                        'FileType', 'Identifier', 'Title', 'BookName', 'Author', 'Publisher',
                        'Creator', 'PackageMetadataCreator', 'PackageMetadataDate', 'Date',
                        'Artist', 'TrackID', 'Album', 'ContentCreateDate', 'Year', 'PackageMetadataTitle'
            }}
            merge_keys(tags, 'title', 'BookName', 'Title', 'PackageMetadataTitle')
            merge_keys(tags, 'author', 'Author', 'Creator', 'PackageMetadataCreator')
            merge_keys(tags, 'date', 'Year', 'Date', 'ContentCreateDate', 'PackageMetadataDate')
            merge_keys(tags, 'track', 'TrackID')
        return tags
    except subprocess.CalledProcessError:
        return {}


def replace_keys_with_values(text, value_map):
    def replace(match):
        key = match.group(1)
        return str(value_map.get(key.lower(), match.group(0)))

    pattern = r'\{([^}]+)\}'
    result = re.sub(pattern, replace, text)
    return result


@fs.command(help='Exiftool utilities')
@click.argument('input_paths', type=click.Path(exists=True), nargs=-1)
@click.option('--filelist', '-f', help='file list', type=click.File('r'), default=sys.stdin)
@click.option('--all-tags', '-a', help='show all tags', is_flag=True)
@click.option('--rename', '-r', help='rename with pattern', type=str)
@click.option('--yes', '-y', help='confirm renaming', is_flag=True)
def tags(input_paths, filelist, all_tags, rename, yes):
    def echo(v, prefix='', postfix='', fg='bright_yellow', nl=False):
        if prefix:
            click.echo(prefix, err=True, nl=False)
        click.secho(v, nl=False, err=True, fg=fg)
        if postfix:
            click.echo(postfix, err=True, nl=False)
        if nl:
            click.echo(err=True)

    files = list(input_paths)
    if not files:
        files = [f for f in filelist.read().split('\n') if os.path.isfile(f)]

    if not rename:
        for path in files:
            click.secho(path, fg='bright_white', reverse=True)
            meta = exiftool_metadata(path, filter=not all_tags)
            max_key = max(len(k) for k in meta.keys()) if meta else 0
            for k, v in sorted(meta.items(), key=lambda x: x[0]):
                echo(k.rjust(max_key), prefix=' ', postfix=': ')
                echo(v, fg='bright_blue', nl=True)
        sys.exit(0)

    to_rename = files
    renamed = []
    for path in to_rename:
        meta = exiftool_metadata(path, filter=not all_tags)
        directory, filename = os.path.split(path)
        stem = utils.safe_filename(replace_keys_with_values(rename, meta))
        renamed.append(os.path.join(directory, stem + os.path.splitext(filename)[1]))

    changed = [(a, b) for a, b in zip(to_rename, renamed) if os.path.basename(a) != b]
    print_to_rename(changed)
    if not yes:
        click.confirm('Do you want to continue?', abort=True)

    for a, b in changed:
        directory_path, _ = os.path.split(a)
        b = os.path.join(directory_path, b)
        os.rename(a, b)
    click.secho('Objects has been renamed!', fg='green', bold=True)


if __name__ == '__main__':
    fs()
