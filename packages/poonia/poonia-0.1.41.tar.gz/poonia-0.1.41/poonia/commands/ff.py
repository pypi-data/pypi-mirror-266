#!/usr/bin/env python3
import base64
import collections
import datetime
import functools
import io
import itertools
import json
import math
import operator
import os
import pathlib
import re
import subprocess
import sys
import time
import urllib
import xml
from functools import reduce

import click
from poonia import utils
from poonia.utils import get_in, sget_in, log, temp_with_content

from poonia.commands.fs import exiftool_metadata


@click.group(help="FFMPEG helpers")
def ff():
    utils.require_exe('ffmpeg')
    utils.require_exe('ffprobe')

def re_find_all_groups(regexp, s):
    return [m.groupdict() for m in re.finditer(regexp, s)]


def parse_stream_filters(filter, default_action='-'):
    filters = re_find_all_groups(
        r'(?P<type>[vas])(?P<action>\+|\-)(?P<text>[^+\s]+)', filter)
    filters = utils.group_by(operator.itemgetter('type'), filters)

    actions_per_type = {t: set(f['action'] for f in fs)
                        for t, fs in filters.items()}
    if any(1 for _, a in actions_per_type.items() if len(a) > 1):
        log.fatal('You can use only one filter action type (+ or -) per stream type!')
    actions_per_type = {t: list(f)[0] for t, f in actions_per_type.items()}

    def _filter(stream_type, *identifiers):
        stream_type_id = stream_type[:1]
        action = actions_per_type.get(stream_type_id, default_action)
        if action == '-':
            for f in filters.get(stream_type_id, []):
                if f['text'] in identifiers:
                    return False
            return True
        else:
            for f in filters.get(stream_type_id, []):
                if f['text'] in identifiers:
                    return True
            return False
    return _filter


def parse_default_filters(filter):
    filters = re_find_all_groups(r'(?P<type>[vas])\!(?P<text>\w+)', filter)
    filters = utils.group_by(operator.itemgetter('type'), filters)
    type_index = {}

    def _filter(stream_type, language, index):
        stream_type_id = stream_type[:1]
        if stream_type_id in type_index:
            return type_index[stream_type_id] == index
        for f in filters.get(stream_type_id, []):
            if f['text'] == language:
                type_index[stream_type_id] = index
                return True
        return False
    return _filter


class FFPROBE(object):
    @classmethod
    @functools.lru_cache(1)
    def probe_file(cls, filename):
        try:
            r = subprocess.check_output(utils.where('ffprobe') + [
                '-hide_banner', '-loglevel', 'fatal',
                '-show_error', '-show_format', '-show_streams', '-show_programs', '-show_chapters', '-show_private_data',
                '-print_format', 'json', '--', filename
            ], stderr=subprocess.STDOUT)
            return json.loads(r.decode('utf-8'))
        except subprocess.CalledProcessError as e:
            return {'error': str(e.output)}

    @classmethod
    def duration_s(cls, filename, exact=True):
        if not exact:
            try:
                meta = cls.probe_file(filename)
                return float(get_in(meta, 'format', 'duration'))
            except:
                return None
        else:
            r = subprocess.check_output(utils.where('ffprobe') + [
                '-i', filename, '-show_packets', '-v', 'quiet'    
            ], stderr=subprocess.STDOUT)
            dts_time = '0'
            for e in r.decode('utf-8').split('\n'):
                e = e.strip()
                if e.startswith('dts_time='):
                    dts_time = e[9:]
            return float(dts_time)

    @classmethod
    def contains_video_audio(cls, filename):
        probe = cls.probe_file(filename)
        streams = get_in(probe, 'streams') or []
        return any(s for s in streams if s.get('codec_type') == 'video'),\
            any(s for s in streams if s.get('codec_type') == 'audio')

    MEDIA_EXTENSIONS = set(itertools.chain(utils.MIME.AUDIO.keys(), utils.MIME.VIDEO.keys()))

    @classmethod
    def is_media_file(cls, filename):
        _, ext = os.path.splitext(filename)
        return ext.lower() in cls.MEDIA_EXTENSIONS

    @classmethod
    def get_tags(cls, filename):
        probe = cls.probe_file(filename)
        tags = probe.get('format', {}).get('tags', {})
        return {k.lower(): v for k, v in tags.items()}

    @classmethod
    def get_framerate(cls, filename):
        def parse_frame_rate(framerate):
            matches = re.findall(r'^(\d+)/(\d+)$', framerate)
            if not matches:
                return None
            a, b = matches[0]
            if int(b) == 0:
                return 0
            return int(a) / float(b)

        probe = cls.probe_file(filename)
        fps = [get_in(stream, 'r_frame_rate')
               for stream in get_in(probe, 'streams')]
        fps = [parse_frame_rate(f) for f in fps]
        fps = [f for f in fps if f]
        return fps[0] if fps else None


def escape_cmd(s):
    return "'%s'" % s if ' ' in s else s


extract_formats = {
    'hdmv_pgs_subtitle': 'sup',
    'subrip': 'srt',
    'aac': 'aac',
    'opus': 'opus'
}


def escape_video_filter_param(s):
    return s.replace('[', r'\[').replace(']', r'\]')


def find_external_subtitles(filename):
    from pprint import pprint
    pprint(filename)


@ff.command(help='FFMPEG stream operations')
@click.argument('input', nargs=-1, type=click.Path(exists=True))
@click.option('-f', '--filters', default='', help='Filter streams by language (eg. "s+eng a-ger")')
@click.option('--print', 'print_', is_flag=True, help='Print ffmpeg commands')
@click.option('--apply', is_flag=True, help='Run conversion')
@click.option('--hardsub', is_flag=True, help='Run conversion')
@click.option('--force-stereo', is_flag=True, help="Convert 5.1 audio streams to stereo")
@click.option('-c:a', 'acodec', type=click.Choice(['mp3', 'aac', 'opus']), help="Audio codec")
@click.option('-b:a', 'abitrate', type=str, help="Audio bitrate", default='96k')
@click.option('-c:v', 'vcodec', type=click.Choice(['hevc', 'avc']), help="Video codec")
@click.option('--width', type=int, help="Resize video to specified width")
@click.option('-b:v', 'vbitrate', type=str, help="Video bitrate", default='')
@click.option('--crf', default=28, help='Sets quality when converting video')
@click.option('-hw', '--hardware', is_flag=True, help='Use hardware video encoding')
@click.option('-extsub', '--external-subtitles', is_flag=True, help='Find subtitles in external file')
def sel(input, filters, print_, apply, hardsub, force_stereo, acodec, abitrate, vcodec, vbitrate, width, crf, hardware, external_subtitles):
    media_ext = set([*utils.MIME.AUDIO, *utils.MIME.VIDEO])
    files = sorted(utils.fs_expand(input or ['.'], allowed_ext=media_ext), key=utils.natural_sort_key)
    output = []

    for f in files:
        if external_subtitles:
            find_external_subtitles(f)

        stream_filter = parse_stream_filters(filters)
        default_filter = parse_default_filters(filters)
        hw_cli = []
        if hardware:
            if sys.platform.startswith('linux'):
                hw_cli = ['-hwaccel', 'auto']
            elif sys.platform.startswith('windows') or sys.latform == 'cygwin':
                hw_cli = ['-hwaccel', 'dxva2']
        cmd = utils.where('ffmpeg') + hw_cli
        cmd += ['-i', f, '-c', 'copy']

        probe = FFPROBE.probe_file(f)
        if not print_:
            click.secho(f, bold=True, nl=False)
            click.secho(' (%s)' % utils.sizeof_fmt(
                get_in(probe, 'format', 'size') or 0), fg='yellow')
        if not get_in(probe, 'streams'):
            continue

        streams = []
        default_streams = collections.defaultdict(dict)
        input_stream_counter = collections.defaultdict(lambda: -1)
        for s in get_in(probe, 'streams'):
            # video, audio, subtitle, attachment
            s_type = get_in(s, 'codec_type')
            s_lang = sget_in(s, 'tags', 'language')
            s_index = get_in(s, 'index')
            input_stream_counter[s_type] += 1
            s_index_type = input_stream_counter[s_type]
            s_default = bool(get_in(s, 'disposition', 'default'))

            keep = stream_filter(
                s_type, *filter(bool, [s_lang, get_in(s, 'channel_layout')]))
            mark_default = default_filter(
                s_type, s_lang, s_index) if keep else False
            streams.append([s, keep, mark_default, s_index_type])
            if mark_default:
                default_streams[s_type][True] = s_index
            if s_default and not mark_default:
                default_streams[s_type][False] = s_index
        to_undefault = [s[False] for _, s in default_streams.items() if s.get(
            True) and s.get(False)]

        output_stream_counter = collections.defaultdict(lambda: -1)
        vfilter = []
        if width:
            vfilter += ['scale=%i:trunc(ow/a/2)*2' % width]
        for s, keep, mark_default, s_index_type in streams:
            s_type = get_in(s, 'codec_type')
            s_info = ''
            if s_type == 'video':
                s_info = '%sx%s' % (get_in(s, 'width'), get_in(s, 'height'))
            elif s_type == 'audio':
                s_info = '%s' % (get_in(s, 'channel_layout'),)
            if get_in(s, 'disposition', 'default'):
                s_info = (s_info + ' default').strip()
            s_index = get_in(s, 'index')
            s_codec = get_in(s, 'codec_name')
            s_lang = sget_in(s, 'tags', 'language')
            unmark_default = s_index in to_undefault

            t = ('  ' if keep else ' -') + \
                '%i %s %s %s %s' % (s_index, s_type, s_codec, s_info, s_lang)
            if not print_:
                click.secho(t, fg=('white' if keep else 'red'), nl=False)
                if mark_default:
                    click.secho(' + DEFAULT', fg='green')
                elif unmark_default:
                    click.secho(' - DEFAULT', fg='red')
                else:
                    click.echo()
            if keep:
                if not (hardsub and mark_default and s_type == 'subtitle'):
                    cmd += ['-map', '0:%i' % s_index]
                output_stream_counter[s_type] += 1
                if force_stereo and s_type == 'audio' and get_in(s, 'channel_layout') not in ('stereo', 'mono'):
                    cmd += [
                        '-filter:a:%i' % output_stream_counter[s_type],
                        'pan=stereo|FL < 1.0*FL + 0.707*FC + 0.707*BL|FR < 1.0*FR + 0.707*FC + 0.707*BR'
                    ] if get_in(s, 'channel_layout') == '5.1' else [
                        '-ac:a:%i' % output_stream_counter[s_type],
                        '2'
                    ]
                    cmd += [
                        '-c:a:%i' % output_stream_counter[s_type], acodec or 'aac',
                        '-b:a:%i' % output_stream_counter[s_type], abitrate
                    ]
                elif acodec:
                    cmd += [
                        '-c:a:%i' % output_stream_counter[s_type], acodec or 'aac',
                        '-b:a:%i' % output_stream_counter[s_type], abitrate
                    ]
                if s_type == 'video' and vcodec:
                    cmd += [
                        '-c:v', 'hevc_videotoolbox' if vcodec == 'hevc' else 'h264_videotoolbox' if (
                            hardware and sys.platform == 'darwin') else 'libx265' if vcodec == 'hevc' else 'libx264',
                        '-preset', 'fast'
                    ]
                    cmd += ['-b:v', '%s' %
                            vbitrate] if vbitrate else ['-crf', '%d' % crf]
                if unmark_default:
                    cmd += [
                        '-disposition:%s:%i' % (s_type[0],
                                                output_stream_counter[s_type]), '0'
                    ]
                elif hardsub and mark_default and s_type == 'subtitle':
                    vfilter += [
                        'subtitles=%s:si=%i' % (
                            escape_video_filter_param(f), s_index_type)
                    ]
                elif mark_default:
                    cmd += [
                        '-disposition:%s:%i' % (s_type[0],
                                                output_stream_counter[s_type]), 'default'
                    ]
        base, ext = os.path.splitext(f)
        if vfilter:
            cmd += ['-vf', ', '.join(vfilter)]
        cmd += ['out__%s%s' % (base, ext)]

        output_command = ' '.join((escape_cmd(c) for c in cmd))
        output += [output_command]
        if print_:
            click.echo(output_command)

    if apply:
        click.confirm('Do you want to continue?', abort=True)
        for cmd in output:
            os.system(cmd)


@ff.command(help='Edit metadata')
@click.argument('input', type=click.Path(exists=True, dir_okay=False, readable=True))
@click.argument('output', type=click.Path(exists=False, dir_okay=False, writable=True), required=False)
def meta(input, output=None):
    meta = subprocess.check_output(utils.where('ffmpeg') + ['-i', input, '-f', 'ffmetadata', '-'], stderr=None)
    edited_meta = click.edit(meta.decode('utf-8'))
    if edited_meta is not None:
        FFMPEGMeta.replace(input_filename=input, metadata=edited_meta, output_filename=output)

class FFMPEGMeta(object):
    @classmethod
    def read(cls, filename):
        meta = subprocess.check_output(utils.where('ffmpeg') + ['-i', filename, '-f', 'ffmetadata', '-'], stderr=subprocess.PIPE)
        return cls.parse(meta.decode('utf-8'))

    @classmethod
    def replace(cls, input_filename, metadata, output_filename=None):
        replace_input = not output_filename or output_filename == input_filename
        if replace_input:
            output_filename = utils.random_filename(os.path.splitext(input_filename)[1])

        has_video, has_audio = FFPROBE.contains_video_audio(input_filename)
        if not (has_video or has_audio):
            raise Exception('input file contains no streams')
        mapping = [] + (['-map', '1:v'] if has_video else []) + (['-map', '1:a'] if has_audio else [])
        try:
            with temp_with_content(metadata, dir='.', suffix='.txt') as f:
                subprocess.check_output(utils.where('ffmpeg') + ['-hide_banner', '-i', f, '-i', input_filename, '-map_metadata', '0'] + mapping + ['-codec', 'copy', output_filename], stderr=None)
            if replace_input:
                os.remove(input_filename)
                os.rename(output_filename, input_filename)
        except subprocess.CalledProcessError as e:
            if replace_input and os.path.exists(output_filename):
                os.remove(output_filename)
            raise e

    @staticmethod
    def parse(s):
        if not s.startswith(';FFMETADATA1\n'):
            return None
        out = [collections.OrderedDict()]
        append_next_line = False
        for x in s.split('\n')[1:]:
            if append_next_line:
                if not x.endswith('\\'):
                    append_next_line = False
                else:
                    x = x[:-1]
                next(reversed(out[-1].values())).append(x.replace('\\=', '='))
            else:
                if x == '[CHAPTER]':
                    out.append(collections.OrderedDict())
                elif '=' in x:
                    if x.endswith('\\'):
                        append_next_line = True
                        x = x[:-1]
                    key, val = x.split('=', 1)
                    out[-1][key] = [val.replace('\\=', '=')]
        for ch in out:
            for k, v in ch.items():
                ch[k] = '\n'.join(v)
        return out

    @staticmethod
    def milliseconds_to_timestamp(milliseconds):
        seconds, milliseconds = divmod(milliseconds, 1000)
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02d}:{seconds:02d}:{milliseconds/(1000/75):02.0f}"

    @staticmethod
    def timestamp_to_milliseconds(timestamp):
        minutes, seconds, frames = map(int, timestamp.split(':'))
        milliseconds = (minutes * 60 + seconds) * 1000 + (frames * 1000 / 75)
        return int(milliseconds)

    @staticmethod
    def to_str(meta, chapters_only=False):
        def escape_val(k, v):
            vlines = list(e.replace('=', '\\=') for e in str(v).split('\n'))
            vlines = list(f'{e}\\' for e in vlines[:-1]) + vlines[-1:]
            vlines = [f'{k}={e}' for e in vlines[:1]] + vlines[1:]
            return vlines
        lines = []
        if not chapters_only:
            lines = [';FFMETADATA1']
        if meta:
            if not chapters_only:
                for k, v in meta[0].items():
                    if v:
                        lines += escape_val(k, v)
            for chapter in meta[1:]:
                lines.append('[CHAPTER]')
                for k, v in utils.order(chapter.items(), ['TIMEBASE', 'START', 'END'], key=lambda e: e[0]):
                    if v is not None and v != '':
                        lines += escape_val(k, v)
        return '\n'.join(lines)

    @classmethod
    def to_cue(cls, meta, filename='unnamed.wav'):
        common = meta[0]
        out = []
        if 'artist' in common:
            artist = common.get("artist").replace('"', "''")
            out += [f'PERFORMER "{artist}"']
        if 'album' in common or 'title' in common:
            title = common.get('album') or common.get('title').replace('"', "''")
            out += [f'TITLE "{title}"']
        out += [f'FILE "{filename}" WAVE']
        for n, ch in enumerate(meta[1:], 1):
            out += [f'  TRACK {n:02d} AUDIO']
            if 'title' in ch:
                title = ch["title"].replace('"', "''")
                out += [f'    TITLE "{title}"']
            if ch.get('TIMEBASE') == '1/1000':
                out += [f'    INDEX 01 {cls.milliseconds_to_timestamp(int(ch.get("START")))}']
        return '\n'.join(out)

    @classmethod
    def parse_cue(cls, s):
        def eq(lst, cmp, min_length=0):
            return len(lst) >= max(min_length, len(cmp)) and all(
                b is None or (a.lower() == b if isinstance(b, str) else a.lower() in b) for a, b in zip(lst, cmp)
            )
        tracks = [{}]
        current_file = None
        for line in s.split('\n'):
            segments = [[g] if i % 2 else re.split(r'\s+', g.strip()) for i,g in enumerate(re.split('"(.+?)"', line)) if g]
            segments = [e for s in segments for e in s]
            if eq(segments, ['rem', {'genre', 'date', 'discid', 'comment'}], 3):
                tracks[-1][segments[1].lower()] = segments[2]
            elif eq(segments, [{'performer', 'title'}], 2):
                tracks[-1][segments[0].lower()] = segments[1]
            elif eq(segments, ['file', None, 'wave'], 3):
                current_file = segments[1]
            elif eq(segments, ['track'], 2):
                tracks.append({'file': current_file})
            elif eq(segments, ['index', '01'], 3):
                tracks[-1]['start'] = cls.timestamp_to_milliseconds(segments[2])
        return tracks

    @staticmethod
    def cue_to_meta(cue):
        def get_len(filename):
            if not os.path.exists(filename):
                base, _ = os.path.splitext(filename)
                found = find_first_file(os.path.dirname(filename) or '.', [base+ext for ext in utils.MIME.AUDIO.keys()]) or log.fatal(f"'{filename}' not found")
                filename = found
            return float(FFPROBE.duration_s(filename)) * 1000

        def rename_key(d, src, dst):
            if src in d:
                d[dst] = d[src]
                del d[src]

        def keep_keys(d, *keys):
            for k in list(d.keys()):
                if k not in keys:
                    del d[k]
        files = {c['file'] for c in cue[1:] if 'file' in c}
        files = {f: get_len(f) for f in files}
        current_file = None
        current_file_pos = 0
        pos = 0
        for i, c in enumerate(cue[1:], 1):
            if 'file' in c and c['file'] != current_file:
                pos += files.get(current_file, 0)
                current_file = c['file']
            current_file_pos = c.get('start', 0)
            c['pos'] = pos + current_file_pos
            if i > 1:
                cue[i-1]['endpos'] = c['pos']
        cue[-1]['endpos'] = pos+files.get(current_file, 0)
        rename_key(cue[0], 'performer', 'artist')
        rename_key(cue[0], 'title', 'album')
        keep_keys(cue[0], 'artist', 'date', 'album')
        for chapter in cue[1:]:
            rename_key(chapter, 'pos', 'START')
            rename_key(chapter, 'endpos', 'END')
            keep_keys(chapter, 'START', 'END', 'title')
            chapter['TIMEBASE'] = '1/1000'
            chapter['START'] = int(chapter.get('START', 0))
            chapter['END'] = int(chapter.get('END', 0))
        return cue

    def humanize_chapters(meta, lengths=False):
        out = []
        for c in meta[1:]:
            if 'START' not in c:
                continue
            timebase = int(c.get('TIMEBASE', '1/1000').lstrip('1').lstrip('/'))
            s = int(c.get('START')) / timebase
            if lengths:
                s = (int(c.get('END')) / timebase) - s
            m, s = divmod(s, 60)
            h, m = divmod(m, 60)
            frac = ('%.3f' % (s % 1)).strip('0').rstrip('.')
            hours = f'{int(h):>2d}:' if h else ''
            out.append((
                f'{hours:>3s}{int(m):02d}:{int(s):02d}{frac:<4}',
                c.get('title', '')
            ))
        return out

    def find_chapters(src, length=None):
        def strip(s, *to_strip):
            while True:
                c = s = s.strip()
                for e in to_strip:
                    s = s[len(e):] if s.startswith(e) else s
                    s = s[:-len(e)] if s.endswith(e) else s
                if s == c:
                    return s

        def to_ms(s):
            return sum(float(v)*mul for v, mul in zip(str(s).split(':')[::-1], [1, 60, 3600])) * 1000

        ts_re = r'((?:\d{1,}):(?:(?:\d{1,2})(?:\.\d+)?:?)*)'
        out = []
        for s in src.split('\n'):
            cand = []
            for f in re.finditer(ts_re, s):
                group, span = f.group(), f.span()
                dist = (span[0], len(s) - span[1])
                trimmed = strip(s[:span[0]] + s[span[1]:], '()', '[]', '-')
                cand.append((*dist, group, trimmed))
            if cand:
                out.append(cand)
        first = [sorted(x, key=lambda e: e[0])[0] for x in out]
        last = [sorted(x, key=lambda e: e[1])[0] for x in out]
        best = sorted([
            [(e[0], *e[2:]) for e in first],
            [(e[1], *e[2:]) for e in last],
        ], key=lambda cand: len({e[0] for e in cand}))[0]
        best = [[e[0], to_ms(e[1]), e[2]] for e in best]
        if length is not None:
            length_from_chapters = sum(e[1] for e in best)
            gap = (length - length_from_chapters) / (len(best)-1) if length > length_from_chapters else 0
            total = 0
            for c in best:
                ts = total
                total = total + c[1] + gap
                c[1] = ts
        return [{'TIMEBASE': '1/1000', 'START': int(e[1]), 'title': e[2]} for e in best]


@ff.command(help='Edit chapters')
@click.argument('input', type=click.Path(exists=True, dir_okay=False, readable=True), required=False)
@click.option('--output', '-o', type=click.Path(exists=False, dir_okay=False, file_okay=False))
@click.option('--chapters', '-c', type=click.Path(exists=True, dir_okay=False, readable=True))
@click.option('--cue', is_flag=True)
@click.option('--lengths', is_flag=True)
def chapters(input, output, chapters, cue, lengths):
    def print_chapters(parsed):
        for i, (start, title) in enumerate(FFMPEGMeta.humanize_chapters(parsed), 1):
            click.echo(f'{i:>3}. ', nl=False)
            click.secho(f'{start} ', nl=False, fg='bright_yellow')
            click.echo(title)
    chapters_to_parse = None
    if chapters:
        with open(chapters, 'r', encoding='utf-8') as f:
            chapters_to_parse = f.read()
    else:
        chapters_to_parse = ''
        if input:
            for start, title in FFMPEGMeta.humanize_chapters(FFMPEGMeta.read(input), lengths):
                chapters_to_parse += f'{start} {title}\n'
        if not cue:
            chapters_to_parse = click.edit(chapters_to_parse)
    if not chapters_to_parse:
        log.fatal('no chapters provided')
    parsed = FFMPEGMeta.parse_cue(chapters_to_parse)
    if len(parsed) < 2:
        gap_length = None
        if lengths:
            gap_length = FFPROBE.duration_s(input)*1000 if input else 0
        parsed = FFMPEGMeta.find_chapters(chapters_to_parse, length=gap_length)
    else:
        parsed = FFMPEGMeta.cue_to_meta(parsed)[1:]

    if len(parsed) < 2:
        log.fatal('no chapters provided')
    if cue:
        click.echo(FFMPEGMeta.to_cue(parsed, filename=os.path.basename(input)))
    elif input:
        original = FFMPEGMeta.read(input)
        ends = [e['START'] for e in parsed[1:]] + [int(FFPROBE.duration_s(input)*1000)]
        for e, end in zip(parsed, ends):
            e['END'] = end
        print_chapters(parsed)
        click.confirm('continue?', abort=True)
        meta_file = FFMPEGMeta.to_str(original[:1] + parsed)
        try:
            FFMPEGMeta.replace(input, meta_file, output_filename=output)
        except subprocess.CalledProcessError as e:
            log.fatal(e)
    else:
        print_chapters(parsed)


@ff.command(help='Change tag in multiple files')
@click.argument('tag', nargs=1, required=True)
@click.argument('input', type=click.Path(exists=True, dir_okay=False, readable=True), nargs=-1)
@click.option('--from-tag', help='if value is empty take from another tag')
@click.option('--from-filename', is_flag=True, help='if value is empty take filename')
@click.option('--replace-if-empty', help='if value is empty take this value')
@click.option('--force-replace', help='take this value')
@click.option('--yes', '-y', help='do not ask for confirmation')
def tag(tag, input, from_tag, from_filename, replace_if_empty, force_replace, yes):
    def analyse(filename):
        has_video, has_audio = FFPROBE.contains_video_audio(filename)
        if not (has_video or has_audio):
            log.fatal(f"file '{filename}' has no streams")
        meta = subprocess.check_output(utils.where('ffmpeg') + ['-i', filename, '-f', 'ffmetadata', '-'], stderr=subprocess.PIPE)
        decoded = FFMPEGMeta.parse(meta.decode('utf-8'))
        return has_video, has_audio, decoded

    input_data = {}
    for filename, (has_video, has_audio, decoded) in utils.parallel(input, analyse, progressbar='reading files', show_pos=True, max_workers=(1 if not yes else None)):
        original_tag = decoded[0].get(tag, '')
        v = original_tag
        if not v and from_tag:
            v = decoded[0].get(from_tag, '')
        if not v and from_filename:
            name, _ = os.path.splitext(os.path.basename(filename))
            v = name
        if not v and replace_if_empty:
            v = replace_if_empty
        if force_replace:
            v = force_replace
        input_data[filename] = (decoded, original_tag, v, has_video, has_audio)

    lines = []
    for filename, (_, _, val, _, _) in input_data.items():
        lines.append(f"={filename}")
        lines.append(val)
    lines = '\n'.join(lines)
    changed = click.edit(lines)
    if not changed:
        sys.exit(0)

    fn = ''
    changes = {}
    for line in changed.rstrip().split('\n'):
        if line.startswith('='):
            fn = line[1:]
        else:
            changes[fn] = f"{changes.get(fn)}\n{line}" if fn in changes else line
    changes = {k:(input_data[k][1], v) for k,v in changes.items() if k in input_data and input_data[k][1] != v}

    for fn, (old_tag, new_tag) in changes.items():
        click.echo(f'{fn}: ', err=True, nl=False)
        click.secho(f'{old_tag}', err=True, nl=False, fg='bright_red')
        click.echo(' -> ', err=True, nl=False)
        click.secho(f'{new_tag}', err=True, fg='bright_green')

    if not yes:
        click.confirm('\ndo you want to continue', abort=True)
    for filename, (old_tag, new_tag) in changes.items():
        meta, _, _, has_video, has_audio = input_data[filename]
        _, input_ext = os.path.splitext(filename)
        mapping = [] + (['-map', '1:v'] if has_video else []) + \
            (['-map', '1:a'] if has_audio else [])
        meta[0][tag] = new_tag
        edited_meta = FFMPEGMeta.to_str(meta)
        click.secho(filename, fg='green', bold=True)
        output = utils.random_filename(input_ext)
        with temp_with_content(edited_meta) as meta_file:
            subprocess.check_output(utils.where('ffmpeg') + ['-i', meta_file, '-i', filename, '-map_metadata', '0'] + mapping + ['-codec', 'copy', output], stderr=subprocess.PIPE)
        os.remove(filename)
        os.rename(output, filename)


def find_first_file(rootdir, names):
    to_find = set(e.lower() for e in names)
    candidates = []
    for subdir, _, files in os.walk(rootdir):
        candidates += list((f.lower(), os.path.join(subdir, f)) for f in files if f.lower() in to_find)
    candidates.sort(key=lambda e: e[1].count(os.path.sep))
    for n in names:
        found = next((path for (f, path) in candidates if f == n.lower()), None)
        if found:
            return found


@ff.command(help='Merge audio files')
@click.argument('input', type=click.Path(readable=True), nargs=-1, required=True)
@click.option('--output', '-o', type=click.Path(exists=False, dir_okay=False, writable=True))
@click.option('--vbr', type=click.IntRange(1, 100), help='vbr quality', default=50, show_default=True)
@click.option('--bitrate', '-b', show_default=True)
@click.option('--channels', '-c', type=click.Choice('1', '2'))
def merge(input, output, bitrate, vbr, channels):
    files = list(utils.fs_expand(input, allowed_ext=utils.MIME.AUDIO))
    files = sorted(files, key=utils.natural_sort_key)
    log.info(f'Processing {len(files)} files')
    if not files:
        log.fatal(f"cannot read input '{input}'")
    for f in files:
        click.secho(f'  {f}', fg='yellow', err=True)
    common_dir = utils.common_dir(files)
    basedir = os.path.basename(common_dir)
    if not output:
        output = f'{basedir}.m4a'
    os.path.exists(output) and log.fatal('output file exists')
    output_ext = os.path.splitext(output)[1].lower()

    def ca_args(compress=False):
        if not compress:
            return ['-c:a', 'copy']
        ca = [] if not channels else ['-ac', channels]
        if output_ext in {'.m4a', '.mp4'}:
            ca += ['-b:a', bitrate] if bitrate else ['-q:a', f'{utils.remap_point2point(vbr, (1, .5), (50, 1), (100, 5)):.2f}']
            if sys.platform == 'darwin':
                ca += ['-c:a', 'aac_at', '-b:a', bitrate] if bitrate else ['-c:a', 'aac_at', '-aac_at_mode', 'vbr', '-q:a', f'{utils.remap_point2point(vbr, (1, 1), (100, 10)):.2f}']
        elif output_ext in {'.opus', '.webm'}:
            ca += ['-c:a', 'libopus', '-b:a', bitrate] if bitrate else log.fatal('provide bitrate for opus encoder')
        else:
            log.fatal('cannot determine codec')
        return ca

    output_dir, output_file = os.path.dirname(output), os.path.basename(output)
    nochap_output = os.path.join(output_dir, f'nochap_{output_file}')
    cover = find_first_file(common_dir, [n+'.'+e for n in ['cover', 'front', 'folder'] for e in ['jpg', 'jpeg', 'png']])
    concat_file = ''
    chapter_file = ''
    escape = lambda s: s.replace("'", "'\\''")
    start = 0.0
    artist, date, album = None, None, None
    to_delete = []

    input_extensions = {os.path.splitext(f)[1].lower() for f in files}
    compress_during_concat = bool(channels) or (len(input_extensions) == 1 and output_ext not in input_extensions)

    def get_meta(filename):
        meta = FFPROBE.probe_file(filename)
        duration = FFPROBE.duration_s(filename)
        chapters = meta.get('chapters', [])
        tags = exiftool_metadata(filename)
        tags = {
            'artist': tags.get('artist'),
            'title': tags.get('title'),
            'date': tags.get('date'),
            'album': tags.get('album')
        }
        return duration, chapters, tags

    for fn, (duration, chapters, tags) in utils.parallel(files, get_meta):
        if artist is None:
            artist = tags.get('artist')
        if date is None:
            date = tags.get('date')
        if album is None:
            album = tags.get('album')
        _, ext = os.path.splitext(fn)
        base, _ = os.path.splitext(os.path.basename(fn))
        if not compress_during_concat and (
            (output_ext in {'.m4a', '.mp4'} and ext.lower() not in {'.m4a', '.mp4'})
            or (output_ext in {'.opus', '.webm'} and ext.lower() not in {'.opus', '.webm'})
        ):
            click.secho(f"Compressing '{fn}' to AAC", bg='green', fg='bright_white', err=True)
            temp_m4a = os.path.join(common_dir, utils.random_filename(ext=output_ext, prefix='tmp_'))
            subprocess.check_output(utils.where('ffmpeg') + [
                '-hide_banner', '-i', fn, '-vn', *ca_args(), temp_m4a
            ])
            to_delete.append(temp_m4a)
            fn = temp_m4a
        concat_file += f"file '{escape(fn)}'\n"
        end = start + duration
        title = tags.get('title') or base
        chapter_file += f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={start*1000:.0f}\nEND={end*1000:.0f}\ntitle={title}\n"
        start = end

    album = album or basedir
    meta_file = f''';FFMETADATA
artist={artist or "Unknown"}
album={album or ""}
date={date or ""}
{chapter_file}'''

    with temp_with_content(concat_file, dir='.', suffix='.txt') as f:
        click.secho("Concatenating files", bg='green', fg='bright_white', err=True)
        subprocess.check_output(utils.where('ffmpeg') + [
            '-hide_banner', '-f', 'concat', '-safe', '0', '-i', f, '-map', '0:a', '-c', 'copy', *ca_args(compress=compress_during_concat), nochap_output
        ])

    input_args, map_args, disp_args = [], [], []
    if cover:
        click.echo(err=True)
        click.secho(f"found cover art: '{cover}'", err=True, bg='green', fg='bright_white')
        click.echo(err=True)
        input_args = ['-i', cover]
        map_args = ['-map', '2']
        disp_args = ['-disposition:v', 'attached_pic']
    with temp_with_content(meta_file, dir='.', suffix='.txt') as f:
        click.secho("Adding metadata", bg='green', fg='bright_white', err=True)
        subprocess.check_output(utils.where('ffmpeg') + [
            '-hide_banner', '-vn', '-i', nochap_output, '-i', f, *input_args, '-map', '0', *map_args, '-map_metadata', '1', '-c', 'copy', *disp_args, output
        ])
    os.remove(nochap_output)
    for f in to_delete:
        os.remove(f)

@ff.command(help='Rename folder by common tags', name='folder')
@click.argument('directories', type=click.Path(exists=True), nargs=-1)
@click.option('-t', '--template', default=r'%artist% [%year%] - %album%', help='name template', show_default=True)
@click.option('--tags', is_flag=True, help='Show available tags')
@click.option('--apply', is_flag=True, help='Apply changes')
def foldertag(directories, template, tags, apply):
    def common_keys(d1, d2):
        return dict(set(d1.items()).intersection(set(d2.items())))

    def format_str(tpl, kv):
        def sub(m):
            k = m.group(1).lower()
            if k not in kv:
                raise Exception(f"'{k}' not found in source tags. Could not interpolate the template '{tpl}'")
            return kv[k]
        return re.sub('%(.+?)%', sub, tpl)

    def print_tags(d):
        for k, v in d.items():
            click.secho(k, nl=False, fg='yellow')
            click.echo(": '%s'" % v)

    def add_custom_tags(d):
        if d.get('date', None):
            m = re.findall(r'(\d{4})', d.get('date'))
            if m:
                d['year'] = m[0]
        if d.get('album_artist', None) and not d.get('artist', None):
            d['artist'] = d['album_artist']

    def show_rename_msg(src, dst, apply=False):
        click.secho("'%s'" % src, bold=True, fg='green', nl=False)
        click.secho(" has been renamed to " if apply else ' will be renamed to ', nl=False)
        click.secho("'%s'" % dst, fg='green', bold=True)

    for directory in directories:
        directory = os.path.normpath(directory)
        if not os.path.isdir(directory):
            click.secho(f"'{directory}' is not a directory", fg='red')
            continue
        files = [os.path.join(dp, f)
                 for dp, dn, fn in os.walk(directory) for f in fn]
        files = [f for f in files if os.path.isfile(
            f) and FFPROBE.is_media_file(f)]
        file_tags = []
        for f in files:
            try:
                file_tags.append(FFPROBE.get_tags(f))
            except Exception as e:
                click.secho("'%s': " % f, fg='yellow', nl=False)
                click.secho(str(e), fg='red')
                continue
        if not file_tags:
            click.secho(f"'{directory}' contains no music files", fg='red')
            continue
        common_tags = reduce(common_keys, file_tags)
        add_custom_tags(common_tags)
        if tags:
            print_tags(common_tags)
            click.echo()

        basename = os.path.basename(directory)
        try:
            target_name = utils.safe_filename(format_str(template, common_tags))
        except Exception as e:
            click.secho("'%s': " % directory, fg='yellow', nl=False)
            click.secho(str(e), fg='red')
            continue
        if basename == target_name:
            log.info2('', f"'{basename}", ' adheres to provided template')
            continue
        show_rename_msg(basename, target_name, apply)
        if apply:
            os.rename(directory, target_name)


@ff.command(help='Extract embedded subtitles', name='subx')
@click.argument('fn', type=click.Path(dir_okay=False, resolve_path=True))
@click.option('--lang', 'language', default=None)
@click.option('--encoding', 'encoding', default='windows-1250')
@click.option('-f', '--first', is_flag=True, default=False)
def subextract(fn, language, encoding, first):
    def get_languages(fn):
        cmd = utils.where('ffmpeg') + ['-i', fn]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        output, error = p.communicate()
        return re.findall(r'Stream #(\d+:\d+)\(?(\w*?)\)?: Subtitle: (\w+)', str(error), flags=re.S)

    langs = get_languages(fn)
    if not (language or first):
        if langs:
            return click.echo('\n'.join('#%s: language "%s" format "%s"' % a for a in langs))
        else:
            return click.secho('no subtitles found', fg='red', bold=True)
    lang = [a for a in langs if a[1] == language or first]
    if not lang:
        return click.secho('no subtitles in selected language', fg='red', bold=True)
    lang = lang[0]
    sfn = os.path.splitext(fn)[0] + '.' + \
        ('srt' if lang[2] == 'subrip' else lang[2])
    click.echo('saving %s subtitles to "%s"' % (lang[1], sfn))
    subprocess.Popen(utils.where('ffmpeg') + [
        '-i', fn, '-map', lang[0],
        '-c', 'copy', sfn
    ]).communicate()


class Subtitle(object):
    @staticmethod
    def parse_mpl(content):
        time_re = r'\[(\d+)\]'
        out = []
        for start, end, text in re.findall(r'^%s%s(.+)$' % (time_re, time_re), content, re.MULTILINE):
            start = int(start)/10.
            end = int(end)/10.
            out.append((start, end, text.replace('|', '\n')),)
        return out

    @staticmethod
    def parse_subrip(content, fps=23.976):
        time_re = r'\{(\d+)\}'
        out = []
        for start, end, text in re.findall(r'^%s%s(.+)$' % (time_re, time_re), content, re.MULTILINE):
            start = int(start)/fps
            end = int(end)/fps
            out.append((start, end, text.replace('|', '\n')),)
        return out

    @staticmethod
    def parse_srt(content):
        def from_srt_time(s):
            parts = [float(x.replace(',', '.')) for x in s.split(':')][::-1]
            s = parts[0] + parts[1] * 60 + parts[2] * 3600
            return s

        time_re = r'(\d+:\d+:\d+,\d+)'
        out = []
        for line in re.split('\n\n', content):
            if not line:
                continue
            m = re.findall(r'%s --> %s\n(.+)' %
                           (time_re, time_re), line, re.DOTALL)
            if not m:
                continue
            start, end, text = m[0]
            start = from_srt_time(start)
            end = from_srt_time(end)
            text = text.strip()
            out.append((start, end, text),)
        return out

    @staticmethod
    def parse(content):
        return Subtitle.parse_srt(content) or \
            Subtitle.parse_subrip(content) or \
            Subtitle.parse_mpl(content)

    @staticmethod
    def emit_srt(lines):
        def to_srt_time(seconds):
            hours, remainder = divmod(seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            s = ('%06.3f' % seconds).replace('.', ',')
            return '%02.0f:%02.0f:%s' % (hours, minutes, s)

        for i, [start, end, text] in enumerate(lines, 1):
            click.echo(
                '%d\n%s --> %s\n%s\n' % (i, to_srt_time(start), to_srt_time(end), text))

    @staticmethod
    def strip_markup(lines):
        out = []
        for start, end, text in lines:
            text = re.sub(r'\</?[\w]+?\>', '', text)
            text = '\n'.join(x.strip() for x in text.split('\n'))
            out.append((start, end, text))
        return out


@ff.command(help='Convert subtitle formats to srt', name='sub')
@click.argument('fn', type=click.Path(dir_okay=False, resolve_path=True))
@click.option('--encoding', 'encoding', default='utf-8')
@click.option('--strip', is_flag=True)
def subconvert(fn, encoding, strip):
    _, ext = os.path.splitext(fn)
    if ext in {'.txt', '.srt'}:
        content = ''
        with open(fn, encoding=encoding) as f:
            content = f.read()
        parsed = Subtitle.parse(content)
        if strip:
            parsed = Subtitle.strip_markup(parsed)
        Subtitle.emit_srt(parsed)
    else:
        x = FFPROBE.get_framerate(fn)
        click.secho(x, nl=True, fg='yellow', bold=True)


@ff.command(help='Audiobook tool')
@click.argument('input', type=click.Path(exists=True, dir_okay=False, readable=True), nargs=-1)
@click.option('--cover', type=click.Path(exists=True, dir_okay=False, readable=True))
@click.option('--metadata', type=click.Choice(['full', 'no-chapters', 'none']), default='full')
@click.option('--bitrate', '-b', default='24k')
def book(input, cover, metadata, bitrate):
    def read_audio(fn):
        r = subprocess.check_output(
            utils.where('ffmpeg') + ['-i', fn, '-f', 'u16le', '-ar', '48000', '-ac', '1', '-'], stderr=None)
        return bytes(r)

    probes = [FFPROBE.ffprobe(f) for f in input]
    if not probes:
        log.fatal('No files to process!')

    title = sget_in(probes[0], 'format', 'tags', 'title')
    artist = sget_in(probes[0], 'format', 'tags', 'artist')
    album_artist = sget_in(probes[0], 'format', 'tags', 'album_artist')
    album = sget_in(probes[0], 'format', 'tags', 'album')

    durations = [float(get_in(p, 'format', 'duration')) for p in probes]
    chapter_marks = [sum(durations[:i]) for i in range(len(durations))]
    chapters = []
    for i, p in enumerate(probes):
        duration = float(get_in(p, 'format', 'duration'))

        click.secho('%s ' % sget_in(p, 'format', 'filename'),
                    bold=True, nl=False)
        click.secho('%s ' % utils.timestamp_fmt(duration), fg='yellow', nl=False)
        click.secho('%s ' % utils.sizeof_fmt(
            get_in(p, 'format', 'size')), fg='cyan', nl=False)

        if metadata == 'full':
            chapter = ('Chapter %d' % (i+1), utils.timestamp_fmt(chapter_marks[i]))
            chapters += [chapter]
            click.echo('[%s | %s]' % chapter, nl=False)
        click.echo()

    click.confirm('Do you want to continue?', abort=True)

    pcm_filename = '__output.pcm'
    metadata_filename = '__metadata_ogg.txt'
    ogg_filename = '__ogg.opus'
    output_filename = '_book.mka'

    if metadata != 'none':
        with open(metadata_filename, 'wb') as f:
            f.write(''';FFMETADATA1
title=%s
artist=%s
album_artist=%s
album=%s
''' % (title, artist, album_artist, album))
            if metadata == 'full':
                for i, ch in enumerate(chapters, 1):
                    f.write('CHAPTER%02d=%s\n' % (i, ch[1]))
                    f.write('CHAPTER%02dNAME=%s\n' % (i, ch[0]))

    with open(pcm_filename, 'wb') as f:
        for i, p in enumerate(probes):
            x = read_audio(sget_in(p, 'format', 'filename'))
            f.write(x)

    subprocess.check_output(utils.where('ffmpeg') + [
        '-f', 'u16le', '-ar', '48000', '-ac', '1',
        '-i', pcm_filename
    ] + (['-i', metadata_filename, '-map_metadata', '1'] if metadata != 'none' else []) + [
        '-b:a', bitrate, '-c:a', 'libopus', ogg_filename
    ], stderr=None)

    subprocess.check_output(utils.where('ffmpeg') + [
        '-i', ogg_filename
    ] + ([
        '-attach', cover, '-metadata:s', 'mimetype=image/jpeg', '-metadata:s', 'filename=book-cover.jpg'
    ] if cover else []) + ['-c:a', 'copy', output_filename], stderr=None)


def extract_cover(fn, probe, max_size=(400, 400)):
    streams = get_in(probe, 'streams')
    covers = [s for s in streams if get_in(s, 'codec_name') == 'mjpeg']
    if not covers:
        return None
    cover = covers[0]
    r = subprocess.check_output(utils.where('ffmpeg') + [
        '-hide_banner',
        '-loglevel', 'panic',
        '-i', fn,
        '-map', '0:%s' % sget_in(cover, 'index'),
        '-vframes', '1',
        '-vf', f'scale=w={max_size[0]}:h={max_size[1]}:force_original_aspect_ratio=decrease',
        '-c:v', 'mjpeg',
        '-huffman', 'optimal',
        '-q:v', '10',
        '-f', 'image2pipe',
        '-'
    ], stderr=None)
    return 'data:image/jpeg;base64,' + base64.b64encode(bytes(r)).decode('ascii')


def gen_rss(title, description, self_url, episodes):
    items = []
    for e in episodes:
        link = urllib.parse.urljoin(self_url, urllib.request.pathname2url(e['filename']))
        item = ''
        item += '<item>\n'
        item += '  <guid>%s</guid>\n' % link
        item += '  <link>%s</link>\n' % link
        item += '  <title>%s</title>\n' % xml.sax.saxutils.escape(e['title'])
        item += '  <description>%s</description>\n' % xml.sax.saxutils.escape(
            e['description'])
        item += '  <pubDate>%s</pubDate>\n' % e['rssdate']
        item += '  <enclosure url="%s" type="audio/mp4a-latm" length="%s"/>\n' % (
            link, e['size'])
        # item += '  <itunes:image href="%s" />\n' % e['cover']
        item += '  <itunes:duration>%d</itunes:duration>\n' % e['duration']
        item += '</item>'
        items.append(item)

    items = '\n'.join(items)
    return '''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <atom:link href="%s" rel="self" type="application/rss+xml" />
    <title>%s</title>
    <description>%s</description>
    <link>http://example.com/</link>
    %s
   </channel>
</rss>
''' % (self_url or '', title, description, items)


@ff.command(help='Generate podcast RSS', name='podcast')
@click.argument('input', type=click.Path(exists=True), default='.')
@click.option('--title', '-t', type=str, default='My Podcast', help='podcast title')
@click.option('--description', '-d', type=str, default='...', help='podcast description')
@click.option('--url', type=str, help='RSS file URL')
def podcastrss(input, title, description, url):
    def is_audio_file(fn):
        _, ext = os.path.splitext(fn)
        return ext.lower() in utils.MIME.AUDIO

    def first_sentence(s):
        return re.findall(r'^(.*?)(?:\.|$|\n)', s or '')[0]

    files = [f for f in os.listdir(input) if os.path.isfile(
        f) and not f.startswith('.')] if os.path.isdir(input) else [input]
    files = [f for f in files if is_audio_file(f)]
    episodes = []

    for f in files:
        probe = FFPROBE.ffprobe(f)
        tags = get_in(probe, 'format', 'tags')

        stat = pathlib.Path(f).stat()

        def dtformat(dt, format): return time.strftime(
            format, time.localtime(time.mktime(dt.timetuple())))

        def statformat(stattime, format): return time.strftime(
            format, time.localtime(stattime))

        tag_date = sget_in(tags, 'date')
        file_date = statformat(stat.st_mtime, '%Y%m%d')
        date = tag_date or file_date

        rssdate = dtformat(datetime.datetime.strptime(
            date, '%Y%m%d'), "%a, %d %b %Y %H:%M:%S %z")
        if tag_date == file_date:
            rssdate = statformat(stat.st_mtime, "%a, %d %b %Y %H:%M:%S %z")

        episodes.append({
            'filename': f,
            'title': sget_in(tags, 'title'),
            'description': first_sentence(sget_in(tags, 'description') or sget_in(tags, 'comment')),
            'date': tag_date or file_date,
            'rssdate': rssdate,
            'duration': int(float(get_in(probe, 'format', 'duration') or 0)),
            'size': stat.st_size
        })
    episodes.sort(key=lambda e: e['date'], reverse=True)
    for e in episodes:
        click.secho(e['filename'], fg='green', bold=True, file=sys.stderr)
        click.secho('title=%(title)s\ndescription=%(description)s\ndate=%(date)s' %
                    e, fg='yellow', file=sys.stderr)
    click.echo(gen_rss(title, description, url, episodes))


@ff.command(help='Get duration of media files', name='len')
@click.argument('input', type=click.Path(exists=True), nargs=-1)
@click.option('--csv', 'output_csv', is_flag=True)
@click.option('--recursive', '-r', is_flag=True)
def duration(input, output_csv, recursive):
    def escape_csv(s):
        if '"' in s or "," in s:
            return '"%s"' % s.replace('"', '""')
        return s
    media_ext = set([*utils.MIME.AUDIO, *utils.MIME.VIDEO])
    files = sorted(utils.fs_expand(input or ['.'], allowed_ext=media_ext, recursive=recursive), key=utils.natural_sort_key)
    output = []
    total_duration = 0.0
    total_size = 0
    for f, duration in utils.parallel(
        files,
        lambda f: FFPROBE.duration_s(f, exact=False),
        progressbar='Analysing files' if len(files) > 20 else None
    ):
        size = os.path.getsize(f)
        duration = duration or 0
        output.append([
            click.format_filename(f),
            utils.timestamp_fmt(duration),
            utils.sizeof_fmt(size),
            size/duration/1000*8 if duration > 0 else 0
        ])

        total_duration += duration
        total_size += size

    lines = ["filename,duration,size,bitrate"]
    for line in output:
        lines += ['%s,%s,%s,%.1f kbps' % (escape_csv(line[0]), line[1], line[2], line[3])]
    lines += ['-- total --,%s,%s,%.1f kbps' % (
        utils.timestamp_fmt(total_duration),
        utils.sizeof_fmt(total_size),
        total_size/total_duration/1000*8 if total_duration > 0 else 0
    )]
    csv_src = '\n'.join(lines)
    click.echo(csv_src) if output_csv else utils.print_csv(csv_src)


class Photo(object):
    @staticmethod
    def identify_size(filename):
        cmd = utils.where('magick') + ['identify', '-format', '%wx%h', filename]
        ret = subprocess.check_output(cmd)
        w, h = ret.decode('utf-8').split('x')
        return int(w), int(h)

    @staticmethod
    def largest_fitting(lst, target, margin=0):
        current_size, n = margin, 0
        for e in lst:
            if current_size + e + margin > target:
                break
            current_size += e + margin
            n += 1
        return n

    @classmethod
    def best_fit(cls, image_size, target_size, margin=0):
        max_cols = int(target_size[0] // min(image_size))
        best_n, best_arr = -1, None
        for rotated in [0, max_cols, *range(1, max_cols)] if image_size[0] != image_size[1] else [0]:
            nonrotated = max_cols - rotated
            sizes = list(image_size if not x else image_size[::-1] for x in [0] * nonrotated + [1] * rotated)
            cols = n = current_width = 0
            for s in sizes:
                if (current_width + s[0] + margin * (cols + 2)) > target_size[0]:
                    break
                current_width += s[0]
                cols += 1
                n += cls.largest_fitting(itertools.repeat(s[1]), target_size[1], margin=margin)
            if n > best_n:
                best_n, best_arr = n, sizes[:cols]
        return best_arr, best_n

    @classmethod
    def open(cls, filename):
        cmd = utils.where('magick') + [filename, 'ppm:-']
        image_data = subprocess.check_output(cmd)
        from PIL import Image
        image = Image.open(io.BytesIO(image_data))
        return image

    @classmethod
    @functools.lru_cache(2)
    def open_resized(cls, filename, rect):
        orig_x, orig_y = cls.identify_size(filename)
        rotate_cmd = []
        if (orig_x > orig_y and rect[0] < rect[1]) or (orig_x < orig_y and rect[0] > rect[1]):
            rotate_cmd = ['-rotate', '90']
        rect_formatted = f'{rect[0]}x{rect[1]}'
        cmd = utils.where('magick') + [filename, '-colorspace', 'LAB', *rotate_cmd, '-resize', f'{rect_formatted}^', '-gravity', 'center', '-crop', f'{rect_formatted}+0+0', '+repage', '-colorspace', 'sRGB', 'png:-']
        image_data = subprocess.check_output(cmd)
        from PIL import Image
        image = Image.open(io.BytesIO(image_data))
        return image


def ratio(ratio):
    w, h = ratio.split('x')
    return float(w), float(h)

def reorder(lst):
    count = collections.OrderedDict()
    for e in lst:
        count[e] = count.get(e, 0) + 1
    for k, v in count.items():
        for _ in range(v):
            yield k

@ff.command(help='Arrange photos', name='print')
@click.argument('files', type=click.Path(exists=True, file_okay=True, dir_okay=False), nargs=-1, required=True)
@click.option('--size', default='35x45', type=ratio, help='photo size', show_default=True)
@click.option('--target', default='152x102', type=ratio, help='target print size', show_default=True)
@click.option('--dpi', type=int, default=600, show_default=True)
@click.option('--margin', type=int, default=1, show_default=True)
@click.option('--output', '-o', type=click.Path(writable=True), required=True)
def print_photo(files, size, target, dpi, margin, output):
    utils.require_exe('magick')
    if os.path.exists(output):
        log.fatal(f"file '{output}' already exists")

    from PIL import Image
    pixels_per_mm = dpi / 25.4
    target_px = round(target[0] * pixels_per_mm), round(target[1] * pixels_per_mm)
    photo_px = math.ceil(size[0] * pixels_per_mm), math.ceil(size[1] * pixels_per_mm)
    margin_px = math.ceil(margin * pixels_per_mm)

    best_arrangement, n = Photo.best_fit(image_size=photo_px, target_size=target_px, margin=margin_px)
    flip = False
    flipped = Photo.best_fit(image_size=photo_px, target_size=target_px[::-1], margin=margin_px)
    if flipped[1] > n:
        target_px = target_px[::-1]
        best_arrangement, n = flipped[0], flipped[1]
        flip = True

    photos = reorder(itertools.islice(itertools.cycle(files), n))
    im = Image.new("RGB", target_px, (255, 255, 255))
    margin_x = (target_px[0] - sum(e[0] for e in best_arrangement)) // (len(best_arrangement)+1)
    x = margin_x
    with click.progressbar(length=n, label='Resizing', file=sys.stderr) as bar:
        for col in best_arrangement:
            rows = (target_px[1] - margin_px) // (col[1] + margin_px)
            margin_y = (target_px[1] - rows * col[1]) // (rows + 1)
            y = margin_y
            for row in range(rows):
                f = next(photos)
                bar.update(1)
                image = Photo.open_resized(f, col)
                im.paste(image, (x, y))
                y += image.height + margin_y
            x += col[0] + margin_x

    if flip:
        im = im.transpose(Image.ROTATE_90)

    click.echo('Saving ', nl=False, err=True)
    click.secho(output, fg='bright_green', err=True, bold=True)
    im.save(output, quality=95, subsampling=0, dpi=(dpi,dpi))


def split_ppms(input_stream):
    accumulator = bytearray()
    while True:
        magic = input_stream.read(3)
        if not magic == b'P6\x0A':
            break
        accumulator.extend(magic)
        dimensions = utils.read_until(input_stream)
        if not dimensions:
            break
        accumulator.extend(dimensions)
        width, height = map(int, dimensions.strip().split())
        value_range = utils.read_until(input_stream)
        if not value_range:
            break
        accumulator.extend(value_range)
        data_size = width * height * 3
        data = input_stream.read(data_size)
        if not data:
            break
        accumulator.extend(data)
        yield bytes(accumulator)
        accumulator.clear()

@ff.command(help='Process video frames')
@click.argument('input', type=click.Path(readable=True, dir_okay=False), nargs=1)
@click.argument('output', type=click.Path(writable=True, dir_okay=False), nargs=1)
@click.option('--fps', type=int)
@click.option('--threads', '-j', type=int)
@click.option('--quality', '-q', type=click.IntRange(0, 100), default=80)
@click.argument('command', type=click.Path(writable=True, dir_okay=False), nargs=-1, required=True)
def proc(input, output, fps, threads, quality, command):
    def extract_frames(filename, fps=None):
        p = subprocess.Popen([
            *utils.where('ffmpeg'), '-i', filename, *(['-r', f'{fps}'] if fps else []),
            '-c:v', 'ppm', '-f', 'image2pipe', '-'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        yield from split_ppms(p.stdout)

    def get_output(stdin_bytes=b''):
        try:
            p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as err:
            return -1, None, str(err).encode('utf-8')
        stdout, stderr = p.communicate(stdin_bytes)
        return (p.returncode, stdout, stderr)

    ext = os.path.splitext(input)[1].lower()
    if ext in utils.MIME.IMAGE:
        from PIL import Image
        im = Image.open(input)
        has_alpha = im.mode == "RGBA"
        if has_alpha:
            alpha = im.getchannel('A')
        im_rgb = im.convert("RGB") if im.mode != "RGB" else im
        rgb = bytes(f'P6\n{im.width} {im.height}\n255\n', encoding='ascii') + im_rgb.tobytes()
        returncode, rgb, err = get_output(rgb)
        if returncode != 0:
            log.fatal(err)
        im = Image.open(io.BytesIO(rgb))
        rgb = None
        if has_alpha:
            im = Image.merge("RGBA", (im.getchannel('R'), im.getchannel('G'), im.getchannel('B'), alpha))
        im.save(output, quality=quality)
    elif ext in utils.MIME.VIDEO:
        s = lambda cmd: cmd.split(' ')
        framerate = fps or FFPROBE.get_framerate(input)
        _, has_audio = FFPROBE.contains_video_audio(input)
        length = FFPROBE.duration_s(input, exact=False)
        encode_cmd = [
            *utils.where('ffmpeg'),
            *s(f'-f image2pipe -framerate {framerate} -i -'),
            *(['-i', input, '-map', '1:a'] if has_audio else []),
            *s(f'-map 0:v -c:a copy -c:v libx264rgb -pix_fmt rgb24 -preset ultrafast -crf {utils.remap_point2point(quality, (0, 51), (100, 0)):.0f} -y'),
            output
        ]
        p = subprocess.Popen(encode_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for out in utils.parallel(
            extract_frames(input, fps=fps), get_output, keep_input=False, max_workers=threads,
            progressbar='', item_count=int(length*framerate), show_pos=True
        ):
            if out[0] != 0:
                log.fatal(out[2])
            p.stdin.write(out[1])
        p.stdin.close()
        p.wait()
    else:
        log.fatal('input format unsupported')

def clamp_int(v, min_val=0, max_val=100):
    return max(min(int(v), max_val), min_val)

@ff.command(help='Reduce image fidelity')
@click.argument('input', nargs=1)
@click.argument('output', nargs=1)
@click.option('-n', type=int, default=10, help='number of iterations', show_default=True)
@click.option('-q', type=click.IntRange(0, 100), default=10, show_default=True)
@click.option('-m', 'mode', type=click.Choice(['const', 'down', 'alt']), default='down', help='processing mode', show_default=True)
def lofi(input, output, n, q, mode):
    if input == '-':
        image_data = sys.stdin.buffer.read()
    else:
        with open(input, 'rb') as f:
            image_data = f.read()
    f, output = (os.path.splitext(output)[1].lower().lstrip('.'), output) if ':' not in output else output.split(':', 1)
    with click.progressbar(range(n), label="compressing", file=sys.stderr) as bar:
        for i in bar:
            input_args = input if i == 0 else f'{f}:-'
            if mode == 'down':
                quality = clamp_int(q+(n-1)-i, 1, 100)
            elif mode == 'alt':
                quality = clamp_int(q + (i % 3))
            elif mode == 'const':
                quality = q
            cmd = utils.where('magick') + [input_args, '-quality', str(quality), f'{f}:-']
            image_data = subprocess.check_output(cmd, input=image_data)
    if output == '-':
        sys.stdout.buffer.write(image_data)
    else:
        with open(output, 'wb') as f:
            f.write(image_data)


class ReaderWithProgressbar(object):
    def __init__(self, reader, progress):
        self.pos, self.r, self.bar = 0, reader, progress

    def read(self, n):
        b = self.r.read(n)
        self.pos += len(b)
        if self.pos > 320000:
            self.bar.update(self.pos)
            self.pos = 0
        return b

@ff.command(help='Generate subtitles')
@click.argument('input', type=click.Path(readable=True), nargs=1)
@click.option('--output', '-o', type=click.File('wb'), default=sys.stdout.buffer)
@click.option('--language', '-l', default='en-us', show_default=True)
@click.option('--per-line', type=int, default=7, help='words per line', show_default=True)
@click.option('--time', '-t', type=int, help='first n seconds')
def subgen(input, output, language, per_line, time):
    try:
        import vosk
    except:
        log.fatal('vosk not found')
    vosk.SetLogLevel(-1)
    rec = vosk.KaldiRecognizer(vosk.Model(lang=language), 16000)
    rec.SetWords(True)
    args = ['-t', str(time)] if time else []
    with subprocess.Popen(
        utils.where('ffmpeg') + ['-loglevel', 'quiet', *args, '-i', input, '-ar', '16000', '-ac', '1', '-f', 's16le', '-'],
        stdout=subprocess.PIPE
    ).stdout as stream:
        with click.progressbar(length=int((time or FFPROBE.duration_s(input, exact=False))*32000), file=sys.stderr) as bar:
            p = ReaderWithProgressbar(stream, bar)
            output.write(rec.SrtResult(p, per_line).encode('utf-8', 'ignore'))


if __name__ == '__main__':
    ff()
