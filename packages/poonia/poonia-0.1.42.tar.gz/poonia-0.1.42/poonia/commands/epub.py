#!/usr/bin/python3
import io
import zipfile
import itertools
import click
import subprocess
import re
import os
from collections import OrderedDict, defaultdict
import random
import string

from poonia.utils import log
from poonia import utils


@click.group(help="ePub utilities")
def epub():
    utils.require_exe('pandoc')

def to_jpeg(input_bytes, compression_quality=70):
    djpeg_process = subprocess.Popen([*utils.where('magick'), '-', 'ppm:-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    cjpeg_process = subprocess.Popen([*utils.where('cjpeg'), '-quality', str(compression_quality)], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    djpeg_stdout, _ = djpeg_process.communicate(input=input_bytes)
    compressed_output, _ = cjpeg_process.communicate(input=djpeg_stdout)
    return compressed_output


LUA = r'''
function remove_attr (x)
  if x.classes then
    x.classes = {}
  end
  if x.attr then
    x.attr = pandoc.Attr()
  end
  return x
end
return {
  { Image = (function()
        return {}
    end) },
  { Blocks = remove_attr },
}
'''

CSS = r'''
body { margin: 0; text-align: justify; font-size: medium; font-family: Athelas, Georgia, serif; }
code { font-family: monospace; font-size: small }
h1 { text-align: left; }
h2 { text-align: left; }
h3 { text-align: left; }
h4 { text-align: left; }
h5 { text-align: left; }
h6 { text-align: left; }
h1.title { }
h2.author { }
h3.date { }
ol.toc { padding: 0; margin-left: 1em; }
ol.toc li { list-style-type: none; margin: 0; padding: 0; }

h1, h2 { -epub-hyphens: none; -webkit-hyphens: none; -moz-hyphens: none; hyphens: none;}
p, blockquote { orphans: 2; widows: 2;}
p, figcaption { -epub-hyphens: auto; -webkit-hyphens: auto; -moz-hyphens: auto; hyphens: auto;}

h1, h2, h3, h4, h5, h6,table, img, figure, video,[data-page-break~=inside][data-page-break~=avoid] { page-break-inside: avoid; }
[data-page-break~=after] { page-break-after: always; }
h1, h2, h3, h4, h5, h6, [data-page-break~=after][data-page-break~=avoid] { page-break-after: avoid; }
[data-page-break~=before] { page-break-before: always; }
[data-page-break~=before][data-page-break~=avoid] { page-break-before: avoid; }
img[data-page-break~=before] { page-break-before: left; }

p { margin-bottom: 0; text-indent: 1.5em; margin-top: 0 }
'''

CSS_DASH_LIST_STYLE = '''
ul { list-style-type: none; }
ul > li:before { content: "–"; position: absolute; margin-left: -1.1em; }
'''

def pandoc_to_markdown(fn, header_shift=0):
    try:
        CMD = utils.where('pandoc') + ['-t', 'markdown', '--reference-location=block', '--wrap=none']
        if header_shift:
            CMD += ['--shift-heading-level-by=%d' % header_shift]
        CMD += ['--id-prefix=%s' %
                (''.join(random.choice(string.ascii_uppercase) for _ in range(20)))]
        r = subprocess.check_output(CMD + [fn], stderr=subprocess.STDOUT)
        return r.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return str(e.output)


def clear_markdown(src):
    html = subprocess.check_output(utils.where('pandoc') + ['--from=markdown', '--to=html'],
                                   stderr=subprocess.STDOUT, input=bytes(src, 'utf-8')).decode('utf-8')
    markdown = subprocess.check_output(utils.where('pandoc') + ['--from=html', '--to=markdown-raw_html-native_divs'],
                                       stderr=subprocess.STDOUT, input=bytes(html, 'utf-8')).decode('utf-8')
    return markdown

# --epub-cover-image=

def markdown_to_epub(target_fn, src, toc_depth=1, css=None, cover=None):
    try:
        src = bytes(src, 'utf-8')
        CMD = utils.where('pandoc') + ['-f', 'markdown', '-t', 'epub', '--strip-comments']
        CMD += ['--toc-depth=%d' % toc_depth]
        if cover:
            CMD += ['--epub-cover-image=%s' % cover]
        if css:
            for c in css:
                CMD += ['--css=%s' % c]
        with utils.temp_with_content(CSS) as css_path, utils.temp_with_content(LUA) as lua_path:
            CMD += ['--lua-filter=%s' % lua_path]
            CMD += ['--css=%s' % css_path]
            r = subprocess.check_output(
                CMD + ['-o', target_fn], stderr=subprocess.STDOUT, input=src)
        return r.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return str(e.output)

def until_unchanged(s, f):
    s1 = s
    while True:
        s2 = f(s1)
        if s2 == s1:
            break
        s1 = s2
    return s2

def re_first_match_or_empty(regexp, s):
    m = re.findall(regexp, s)
    return m[0] if m else ''

def markdown_header_level(s): return len(s)-len(s.lstrip('#'))

def find_chapters(src):
    p = re.compile("^#+.+$", re.MULTILINE)
    chapters = [(m.start(), m.group(), markdown_header_level(m.group()))
                for m in p.finditer(src)]
    return chapters

def capitalize_title(s): return ' '.join(
    [w.capitalize() if len(w) > 1 and w[0].isupper() else w for w in s.split(' ')])


@epub.command(help='Merge books to one epub')
@click.argument('files', type=click.Path(exists=True, dir_okay=False), nargs=-1)
@click.option('-t', '--book-title', type=str, prompt=True, required=True)
@click.option('-h', '--add-headers', is_flag=True, help='Include source file name as header')
@click.option('-o', '--output', required=True, type=str, prompt=True)
@click.option('-c', '--capitalize-headers', is_flag=True)
@click.option('-sep', '--title-separator', default=' - ', type=str)
@click.option('-seg', '--header-segments', default=100, type=int)
@click.option('-tsep', '--target-separator', type=str)
@click.option('-l', '--language', type=str, default='pl-PL')
@click.option('-css', '--css', type=click.Path(exists=True, dir_okay=False), multiple=True)
@click.option('-cov', '--cover', type=click.Path(exists=True, dir_okay=False))
def merge(files, book_title, add_headers, output, capitalize_headers, title_separator, header_segments, target_separator, language, css, cover):
    click.secho("<Processing %s>" % repr(files), fg="yellow", err=True)
    books = []
    with click.progressbar(files, label='Reading input files') as bar:
        for f in bar:
            title, _ = os.path.splitext(f)
            section = title_separator.join(
                s for s in title.split(title_separator)[:-header_segments])
            title = (target_separator or title_separator).join(
                s for s in title.split(title_separator)[-header_segments:])
            if capitalize_headers:
                title = capitalize_title(title)

            pandoc_src = pandoc_to_markdown(f)
            chapters = find_chapters(pandoc_src)
            min_header_level = min(c[2] for c in chapters) if chapters else 0
            if min_header_level:
                header_shift = (4 if section else 3) - min_header_level
                if header_shift:
                    pandoc_src = pandoc_to_markdown(f, header_shift)
                # min_header_level = min(c[2] for c in chapters) if chapters else 2
                # if min_header_level < (3 if section else 2):
                #     pandoc_src = pandoc_to_markdown(f, min_header_level + (1 if section else 0))

            books.append({
                'title': title,
                'src': pandoc_src,
                'section': section
            })

    out = u'''---
title: "%s"
language: "%s"
strip-empty-paragraphs: true
table-of-contents: false
---

''' % (book_title.replace('"', r'\"'), language.replace('"', r'\"'))

    has_sections = any(b['section'] for b in books)
    if not has_sections:
        for b in books:
            out += u'''## %s

%s

<div style="page-break-before:always;"></div>

''' % (b['title'], b['src'])
    else:
        sections = OrderedDict()
        for b in books:
            s = b['section']
            if s in sections:
                sections[s].append(b)
            else:
                sections[s] = [b]

        for s, section_books in sections.items():
            out += u'## %s\n\n' % s
            for b in section_books:
                out += u'''### %s

%s

<div style="page-break-before:always;"></div>

''' % (b['title'], b['src'])

    _, ext = os.path.splitext(output)
    if ext.lower() == '.epub':
        markdown_to_epub(
            output, out, toc_depth=2 if not has_sections else 3, css=css, cover=cover)
        click.secho("</saved '%s'>" % output, fg="yellow", err=True)
    elif ext.lower() == '.md':
        with open(output, 'w') as f:
            f.write(out)
        click.secho("</saved '%s'>" % output, fg="yellow", err=True)
    else:
        click.secho('cannot write to %s file' % output, err=True, fg='red')


def list_val_order(lst):
    i = 0
    mapping = {}
    for e in lst:
        if e in mapping:
            continue
        i += 1
        mapping[e] = i
    return mapping


class Pandoc(object):
    @staticmethod
    def _markdown_header_level(s):
        return len(s)-len(s.lstrip('#'))

    @staticmethod
    def _markdown_title(s):
        orig = '/'+s
        s = s.replace('\xa0', ' ')  # replace non-breaking space
        invisible_title = re_first_match_or_empty('{.*title="(.+?)".*}', s)
        s = re.sub(r'(^#+\s+|{.+?})', '', s)  # delete header and attributes
        s = re.sub(r'[\[\]]', '', s)
        s = re.sub(r'\s+', ' ', s)
        s = s.rstrip()
        s = until_unchanged(
            s, lambda s: s[1:-1] if s.startswith('[') and s.endswith(']') else s)
        s = until_unchanged(
            s, lambda s: s[1:-1] if s.startswith('*') and s.endswith('*') else s)
        return s or invisible_title or orig

    @classmethod
    def find_chapters(cls, src):
        p = re.compile("^#+.+$", re.MULTILINE)
        chapters = [(m.start(), cls._markdown_title(m.group()),
                    cls._markdown_header_level(m.group())) for m in p.finditer(src)]
        if len(chapters) < 2:  # try calibre formatting
            p = re.compile("^.+$", re.MULTILINE)
            chapters = [(m.start(), m.group()) for m in p.finditer(src)]

            def calibre_level(s):
                classes = re.findall('{(.+?)}', s)
                if '.bold' not in classes:
                    return 0
                nums = [re.sub(r'[^\d]', '', c) for c in classes]
                nums = [int(e) for e in nums if e]
                return max(nums)
            chapters = [(c[0], cls._markdown_title(c[1]), calibre_level(c[1]))
                        for c in chapters if calibre_level(c[1])]
        if len(chapters) < 2:  # try bold lines
            p = re.compile(r"^\*\*.+\*\*$", re.MULTILINE)
            chapters = [(m.start(), m.group(), 1) for m in p.finditer(src)]
            def font_size(s): return int(re_first_match_or_empty(
                r'font-size\s*:\s*(\d+)', s.lower()) or '1')
            chapter_font_size = [font_size(c[1]) for c in chapters]
            font_size_order = list_val_order(chapter_font_size)
            chapter_rank = [font_size_order[c] for c in chapter_font_size]
            chapters = [(c[0], cls._markdown_title(c[1]), r)
                        for c, r in zip(chapters, chapter_rank)]
        return chapters

    @staticmethod
    def pandoc_to_markdown(fn):
        PANDOC_CMD = utils.where('pandoc') + ['-t', 'markdown-auto_identifiers', '--wrap=none']
        try:
            r = subprocess.check_output(
                PANDOC_CMD + [fn], stderr=subprocess.STDOUT)
            return r.decode('utf-8')
        except subprocess.CalledProcessError as e:
            return str(e.output)


@epub.command(help='Extract chapters to new markdown file')
@click.argument('filename', type=click.Path(exists=True, dir_okay=False))
@click.option('-i', '--include-filename', is_flag=True, help='Include source file name')
def split(filename, include_filename):
    utils.require_exe('pandoc')
    pandoc_src = Pandoc.pandoc_to_markdown(filename)
    chapters = Pandoc.find_chapters(pandoc_src)
    for i, c in enumerate(chapters, 1):
        next_level = chapters[i][2] if len(chapters) > i else 0
        click.secho(u'% 3d: ' % i, nl=False)
        tree = ''.join(
            ['├─' if next_level > level else '└─' for level in range(1, c[2])])
        click.secho(tree, fg='red', bold=True, nl=False)
        click.secho(c[1], fg='green')

    while True:
        selected_index = click.prompt(
            'Select chapter to extract', type=click.IntRange(1, len(chapters)))-1
        selected_level = chapters[selected_index][2]
        selected_chapters = [chapters[selected_index]] + list(
            itertools.takewhile(lambda c: c[2] > selected_level, chapters[selected_index+1:]))
        start_pos = selected_chapters[0][0]
        end_pos = chapters[selected_index+len(selected_chapters)][0] if len(
            chapters) > selected_index+len(selected_chapters) else len(pandoc_src)

        target_filename = selected_chapters[0][1]
        if len(selected_chapters) <= 3:
            target_filename = ' - '.join(c[1] for c in selected_chapters if c[1] and not c[1].startswith('/'))
        if include_filename:
            base, _ = os.path.splitext(filename)
            target_filename = u'%s - %s' % (base, target_filename)

        target_filename = utils.safe_filename(target_filename + '.md')
        target_filename = click.prompt(
            'Target filename', type=str, default=target_filename)
        with open(target_filename, 'w') as f:
            f.write(pandoc_src[start_pos:end_pos])


@epub.command(help='Recompress embedded JPEG files to save space')
@click.argument('input_path', type=click.Path(exists=True, dir_okay=False))
@click.argument('output_path', type=click.Path(exists=False, dir_okay=False), required=False)
@click.option('-q', '--jpeg_quality', type=int, help='JPEG quality', default=50)
@click.option('-t', '--compression_threshold', type=utils.sizeof_parse, help='Compression threshold', default='100k', show_default=True)
@click.option('--apply', is_flag=True, help='Overwrite input file')
@click.option('-png', '--png-to-jpg', 'compress_png', is_flag=True, help='Convert PNG to JPG')
def compress(input_path, output_path, jpeg_quality, compression_threshold, apply, compress_png):
    utils.require_exe('cjpeg')
    utils.require_exe('magick')
    get_output_size = None
    get_output = None

    def open_output():
        nonlocal get_output_size, get_output
        if not output_path:
            f = io.BytesIO()
            def get_output_size(): return f.getbuffer().nbytes

            def get_output():
                nonlocal f
                f.seek(0)
                out = f.read()
                f = None
                return out
            return zipfile.ZipFile(f, 'w', zipfile.ZIP_DEFLATED)
        return zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED)

    input_stats = defaultdict(
        lambda: {'size': 0, 'post_size': 0, 'count': 0, 'post_count': 0})
    # Open the EPUB file in read mode
    with zipfile.ZipFile(input_path, 'r') as epub_file:
        # Extract the mimetype file
        mimetype_content = epub_file.read('mimetype')

        # Create a new EPUB file in write mode
        with open_output() as new_epub_zip:
            # Write the uncompressed mimetype file as the first file in the archive
            new_epub_zip.writestr(
                'mimetype', mimetype_content, compress_type=zipfile.ZIP_STORED)

            # Add the remaining files to the archive
            with click.progressbar(epub_file.infolist()) as items:
                for item in items:
                    if item.filename == 'mimetype':
                        continue

                    item_bytes = epub_file.read(item.filename)
                    _, item_ext = os.path.splitext(item.filename.lower())
                    input_stats[item_ext]['count'] += 1
                    input_stats[item_ext]['size'] += len(item_bytes)

                    if item_ext in {'.jpg', '.jpeg'} and len(item_bytes) > compression_threshold:
                        new_item_bytes = to_jpeg(
                            item_bytes, compression_quality=jpeg_quality)
                        if len(new_item_bytes) < (len(item_bytes)*.7):
                            item_bytes = new_item_bytes
                            input_stats[item_ext]['post_count'] += 1

                    if compress_png and item_ext in {'.png'} and len(item_bytes) > compression_threshold:
                        new_item_bytes = to_jpeg(
                            item_bytes, compression_quality=jpeg_quality)
                        if len(new_item_bytes) < (len(item_bytes)*.7):
                            item_bytes = new_item_bytes
                            input_stats[item_ext]['post_count'] += 1

                    input_stats[item_ext]['post_size'] += len(item_bytes)

                    new_epub_zip.writestr(item, item_bytes)

    def echo(v, prefix='', postfix='', fg='bright_yellow', nl=False):
        if prefix:
            click.echo(prefix, err=True, nl=False)
        click.secho(v, nl=False, err=True, fg=fg)
        if postfix:
            click.echo(postfix, err=True, nl=False)
        if nl:
            click.echo(err=True)
    click.echo('Input size breakdown:', err=True)
    for ext, vals in sorted(input_stats.items(), key=lambda x: x[1]['size'], reverse=True):
        count, size, post, post_count = vals['count'], vals['size'], vals['post_size'], vals['post_count']
        echo(ext, prefix='\t', postfix='\t')
        echo('% 5d' % count, postfix=' files\t')
        echo(utils.sizeof_fmt(size), prefix='total: ')
        if post != size:
            echo(post_count, prefix='\tcompressed ', postfix=' files')
            echo(utils.sizeof_fmt(post), prefix=' (', postfix=')', fg='bright_red')
        click.echo(err=True)
    click.echo(err=True)

    if get_output_size:
        input_size = os.stat(input_path).st_size
        output_size = get_output_size()
        click.echo('Output size: ', nl=False, err=True)
        echo(utils.sizeof_fmt(output_size), fg='bright_green', postfix=' ')
        echo('%.2f%%' % (output_size/input_size*100),
             prefix='(', postfix=' of ')
        echo(utils.sizeof_fmt(input_size), postfix=')', nl=True)

    if apply and get_output:
        input_size = os.stat(input_path).st_size
        if (input_size * .5) < get_output_size():
            log.fatal('Not enough reduction.')
        else:
            with open(input_path, 'wb') as f:
                f.write(get_output())
            log.info('EPUB recompressed successfully.')


if __name__ == '__main__':
    epub()
