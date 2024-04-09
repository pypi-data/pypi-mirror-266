#!/usr/bin/env python3
from functools import reduce
import json
import operator
import re
import subprocess
import sys
import click
from poonia.text import RegexSub
from poonia.utils import log, get_in, sliding_window


@click.group(help="Tools operating on stdio/stdout")
def io(): pass


def flatten(S):
    if not isinstance(S, list):
        return S
    if S == []:
        return S
    if isinstance(S[0], list):
        return flatten(S[0]) + flatten(S[1:])
    return S[:1] + flatten(S[1:])


@io.command(help='Filter JSON stream')
@click.option('--path', '-p', type=str, default='', help="filter path like 'authors 0 email'")
@click.option('--filter', '-f', type=str, default=None, help='text contained in filtered part')
@click.option('--output-filtered', '-o', is_flag=True, help='outputs only filtered part')
def jfilter(path, filter, output_filtered):
    path = [int(g) if g.isnumeric() else g for g in path.split()]
    for line in iter(sys.stdin.readline, ""):
        data = json.loads(line)
        extracted = flatten(get_in(data, *path))
        if filter and (not extracted or filter not in extracted):
            continue
        click.echo(json.dumps(extracted if output_filtered else data))


@io.command(help='Encode special characters to safe ASCII entities')
@click.option('--keep', type=str, default='10,13,32-91,93-126', help='characters to keep unchanged', show_default=True)
@click.option('--trigger', type=bytes, default=b'$', help='prefix for escaping', show_default=True)
@click.option('--escape', type=bytes, default=b'\\', help='escaping character in source (will be escaped in output)', show_default=True)
@click.option('--decode', '-d', is_flag=True)
def encode(keep, trigger, decode, escape):
    def expand_range(s):
        if '-' not in s:
            return [int(s)]
        [s_from, s_to] = map(int, s.split('-'))
        if s_to < s_from:
            s_from, s_to = s_to, s_from
        return list(range(s_from, s_to+1))

    def decode_stdin(trigger):
        read = sys.stdin.buffer.read
        write = sys.stdout.buffer.write
        while True:
            b = read(1)
            if not b:
                sys.exit(0)
            if b == trigger:
                rest = read(2)
                if len(rest) < 2:
                    log.fatal('error occured')
                write(bytes.fromhex(rest.decode('ascii')))
            else:
                write(b)

    def encode_stdin(expanded, trigger, escape):
        def encode(b): return trigger + b.hex().encode('ascii') if b else b''
        read = sys.stdin.buffer.read
        write = sys.stdout.buffer.write
        while True:
            b = read(1)
            if b in expanded:
                write(b)
            elif b == escape:
                write(encode(b))
                write(encode(read(1)))
            elif not b:
                sys.exit(0)
            else:
                write(encode(b))

    if decode:
        decode_stdin(trigger)
    else:
        expanded = reduce(operator.__add__, [
                          expand_range(r) for r in keep.split(',')])
        expanded = {x.to_bytes(1, 'big') for x in expanded} - {trigger}
        encode_stdin(expanded, trigger, escape)


def get_output(cmd, stdin_bytes=b''):
    try:
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as err:
        return -1, None, str(err)
    stdout, stderr = p.communicate(stdin_bytes)
    return (p.returncode, stdout, stderr)


def replace_cmd_references(cmd, data):
    def first_or_none(x): return x[0] if len(x) > 0 else None
    def col_from_pattern(s): return first_or_none(re.findall(r'^\{(.+)\}$', s))
    def ref_to_path(path): return [
        int(g) if g.isnumeric() else g for g in path.split()]
    out = []
    for c in cmd:
        ref = col_from_pattern(c)
        if not ref:
            out.append(c)
            continue
        path = ref_to_path(ref)
        data = get_in(data, *path)
        out.append(data or '')
    return out


@io.command(help='Execute commands on JSON stream')
@click.argument('command', type=str, nargs=-1)
@click.option('--output-field', '-o', required=True, help='output field')
@click.option('--stdin', help='standard input column')
@click.option('--verbose', '-v', is_flag=True, help='verbose')
def jexec(output_field, command, stdin, verbose):
    def escape_cmd(s): return s if ' ' not in s else "'%s'" % s

    for line in iter(sys.stdin.readline, ""):
        data = json.loads(line)
        cmd = replace_cmd_references(command, data)
        if verbose:
            log.info(' '.join(escape_cmd(c) for c in cmd))
        code, o_stdout, o_stderr = get_output(
            cmd, b'' if not stdin else bytes(data[stdin], encoding='utf-8'))
        if code == 0:
            data[output_field] = o_stdout.decode('utf-8').rstrip('\n')
            try:
                data[output_field] = json.loads(data[output_field])
            except:
                pass
        else:
            if verbose:
                log.warn("%s returned status code %s: %s" %
                         (' '.join(escape_cmd(c) for c in cmd), code, o_stderr))
        j = json.dumps(data)
        print(j)


@io.command(help='Greppable JSON')
@click.argument('input_file', type=click.File('r'), default=sys.stdin)
@click.option('--decode', '-d', '--ungron', is_flag=True, help='transform gron output back to JSON')
@click.option('--pretty', '-p', is_flag=True, help='pretty print JSON')
@click.option('--values', '-v', is_flag=True, help='print values only')
def gron(input_file, decode, pretty, values):
    def to_gron(node, name):
        def format_path(name):
            if not isinstance(name, str):
                return str(name)
            if ('[' in name or ' ' in name or '"' in name or name == ''):
                return '[%s]' % json.dumps(name, ensure_ascii=False)
            return '.' + name
        if node is None:
            yield name, 'null'
        elif isinstance(node, bool):
            yield name, str(node).lower()
        elif isinstance(node, str):
            yield name, json.dumps(node, ensure_ascii=False)
        elif isinstance(node, dict):
            yield name, '{}'
            for k, v in sorted(node.items()):
                yield from to_gron(v, name + format_path(k))
        elif isinstance(node, (list, tuple)):
            yield name, '[]'
            for i, e in enumerate(node):
                yield from to_gron(e, name + format_path([i]))
        else:
            yield name, repr(node)

    def split_gron(s):
        for i, c in enumerate(s):
            if not c == '=':
                continue
            left_half, right_half = s[:i], s[i+1:]
            if (left_half.replace('\\"', '').count('"') % 2 == 0) and (right_half.replace('\\"', '').count('"') % 2 == 0):
                return (left_half, right_half.rstrip(';'))
        return None

    def ungron(input):
        def json_must_load(val):
            try:
                return json.loads(val)
            except:
                log.fatal("cannot parse JSON value '%s'" % val)

        _RE = re.compile(
            r'^(\s*\[(?:"((?:(?:\\")|[^"])*?)"\.?|(\d+))\]\.?|([^ \.\[=]+)\.?)')

        def create_path(obj, path, val):
            if not path.strip():
                return json_must_load(val)
            key = _RE.findall(path)
            if key:
                num = key[0][2]
                st = key[0][1] or key[0][3]
                rest = path[len(key[0][0]):]
                if num:
                    num = int(num)
                    if not isinstance(obj, list):
                        obj = []
                    while len(obj) < num+1:
                        obj.append(None)
                    obj[num] = create_path(obj[num], rest, val)
                else:
                    if not isinstance(obj, dict):
                        obj = {}
                    obj[st] = create_path(obj.get(st), rest, val)
            return obj

        obj = None
        for line in input.split('\n'):
            parts = split_gron(line)
            if not parts:
                continue
            path, value = parts
            if path.startswith('json'):
                path = re.sub(r'^json\.?', '', path)
            obj = create_path(obj, path, value.strip())
        return obj

    def print_values(input):
        for line in input.split('\n'):
            parts = split_gron(line)
            if not parts:
                continue
            print(parts[1].strip())

    input = input_file.read()
    if decode:
        data = ungron(input)
        if pretty:
            json.dump(data, sys.stdout,
                      sort_keys=True, indent=2)
            print()
        else:
            json.dump(data, sys.stdout,
                      sort_keys=False, separators=(',', ':'))
            print()
    elif values:
        print_values(input)
    else:
        try:
            for k, v in to_gron(json.loads(input), 'json'):
                click.echo('%s = %s;' % (k, v))
        except json.decoder.JSONDecodeError as e:
            log.fatal(e)


@io.command(help='Make whitespace visible', name='ws')
@click.option('--input', '-i', help='input file', type=click.File('rb'), default=sys.stdin.buffer)
def whitespace(input):
    _dot = '·'.encode('utf-8')
    _tab = '￫'.encode('utf-8')
    _car = '§'.encode('utf-8')
    _end = '¶\n'.encode('utf-8')
    while True:
        buffer = input.read(2048)
        if not buffer:
            break
        sys.stdout.buffer.write(buffer.replace(
            b' ', _dot).replace(b'\t', _tab).replace(b'\r', _car).replace(b'\n', _end))


def read_slice_from_stream(stream, slice_str, max_bytes=None, chunk_size=1048576):
    start, stop = slice_str.split(':', 1)
    start = int(start) if start.isnumeric() else 0
    stop = int(stop) if stop.isnumeric() else -1

    if stop == -1:
        num_bytes = max_bytes or -1
    elif max_bytes is None:
        num_bytes = stop - start
    else:
        num_bytes = min(stop - start, max_bytes)

    if stream.seekable():
        stream.seek(start)
    else:
        for i in range(0, start, chunk_size):
            remains = min(chunk_size, start - i)
            stream.read(remains)

    if num_bytes < 0:
        while True:
            read = stream.read(chunk_size)
            if not read:
                break
            yield read
        return

    for i in range(0, num_bytes, chunk_size):
        remains = min(chunk_size, num_bytes - i)
        read = stream.read(remains)
        if not read:
            break
        yield read


@io.command(help='Get selected bytes only')
@click.argument('expr', type=str, nargs=1)
@click.option('--bytes', '-b', type=int, default=None, help='limit length to n bytes')
@click.option('--input', '-i', help='input file', type=click.File('rb'), default=sys.stdin.buffer)
def slice(expr, bytes, input):
    if ':' not in expr:
        log.fatal(f"error: wrong slice: '{expr}'")
    for chunk in read_slice_from_stream(input, expr, bytes):
        sys.stdout.buffer.write(chunk)


@io.command(help='Join lines split at wrong places')
@click.option('--input', '-i', help='input file', type=click.File('r'), default=sys.stdin)
def prose(input):
    def filter_dup_empty(stream):
        last = False
        for e in stream:
            if e.isspace():
                if not last:
                    yield e
                last = True
            else:
                yield e
                last = False

    def starts_with_lower(s):
        if not s:
            return False
        for c in s:
            if not c.isalnum():
                continue
            return c.islower()
        return False

    for window in sliding_window(filter_dup_empty(iter(input.readline, "")), n=5):
        line = window[0]
        next_lower = False
        for a in window[1:]:
            if a.isspace():
                continue
            next_lower = starts_with_lower(a)
            break
        if next_lower and line.isspace():
            continue
        line = line.rstrip('\n').rstrip('\r')
        print(line, end=(' ' if next_lower else '\n'))


@io.command(help='Replace string using regular expression')
@click.argument('pattern', type=str)
@click.argument('substitution', type=str)
@click.option('--ignorecase', '-i', is_flag=True, help="Case-insensitive matching, expressions like [A-Z] will also match lowercase letters")
@click.option('--multiline', '-m', is_flag=True, help="The '^' matches at the string and line beginnings, the '$' matches at the string and line ends.")
@click.option('--dotall', '-s', is_flag=True, help="Make the '.' match any character, including a newline")
@click.option('--eval', '-x', is_flag=True, help="Evaluate substitution as expression")
@click.option('--only-extract', '-o', is_flag=True, help="Print only substitution outputs, each on separate line")
@click.option('--input', help='Input file', type=click.File('r'), default=sys.stdin)
def sed(pattern, substitution, input, ignorecase, multiline, dotall, eval, only_extract):
    flags = re.NOFLAG
    flags |= re.IGNORECASE if ignorecase else re.NOFLAG
    flags |= re.MULTILINE if multiline else re.NOFLAG
    flags |= re.DOTALL if dotall else re.NOFLAG
    sub = RegexSub.compile(pattern, substitution, flags=flags, evaluate=eval, extract=only_extract)
    if not multiline:
        end = ''
        for line in iter(input.readline, ""):
            line, end = (line[:-1], line[-1]) if line.endswith('\n') else (line, '')
            line = sub(line)
            if line:
                sys.stdout.write(line+end)
    else:
        sys.stdout.write(sub(input.read()))
        if only_extract:
            sys.stdout.write('\n')


if __name__ == '__main__':
    io()
