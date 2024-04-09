from collections import namedtuple
from html.parser import HTMLParser
import re

_BOLD_TAGS = {'b', 'strong'}
_ITALIC_TAGS = {'i', 'em'}
_IGNORE_TAGS = {'script', 'style'}


class _HTMLTextParser(HTMLParser):
    def __init__(self):
        super(_HTMLTextParser, self).__init__(convert_charrefs=True)
        self.bold = []
        self.italic = []
        self.tag_bold = 0
        self.tag_italic = 0
        self.tag_ignore = 0
        self.parsed_text = []

    def handle_starttag(self, tag, attr_list):
        if tag in _BOLD_TAGS:
            self.tag_bold += 1
        elif tag in _ITALIC_TAGS:
            self.tag_italic += 1
        elif tag in _IGNORE_TAGS:
            self.tag_ignore += 1
        elif tag == 'br':
            self.handle_data('\n', replace_whitespace=False)

    def handle_endtag(self, tag):
        if tag in _BOLD_TAGS:
            self.tag_bold -= 1
        elif tag in _ITALIC_TAGS:
            self.tag_italic -= 1
        elif tag in _IGNORE_TAGS:
            self.tag_ignore -= 1

    def handle_data(self, data, replace_whitespace=True):
        if self.tag_ignore > 0:
            return
        if replace_whitespace:
            data = re.sub(r'\s+', ' ', data)
        self.bold += [self.tag_bold > 0]*len(data)
        self.italic += [self.tag_italic > 0]*len(data)
        self.parsed_text.append(data)


class RichText(str):
    def __new__(cls, html):
        parser = _HTMLTextParser()
        parser.feed(html)
        s = super().__new__(cls, ''.join(parser.parsed_text))
        s.bold = parser.bold
        s.italic = parser.italic
        return s

class RegexSub:
    @staticmethod
    def _where(func, iterable):
        for item in iterable:
            if func(item):
                yield item
            else:
                return

    @classmethod
    def _parse(cls, s, unescape=True):
        group = re.findall(r'^\$(\d+):', s)
        if group:
            group = int(group[0])
            s = s[s.index(':')+1:]
        else:
            group = 0
        i, out, buf = 0, [], []
        while i < len(s):
            if s[i] == '$':
                if s[i+1:i+2].isnumeric():
                    n = ''.join(cls._where(lambda c: c.isnumeric(), s[i+1:]))
                    if buf:
                        out.append(''.join(buf))
                        buf.clear()
                    out.append(int(n))
                    i += len(n)+1
                    continue
                elif s[i+1:i+2] == '$':
                    i += 1
            buf.append(s[i])
            i += 1
        if buf:
            out.append(''.join(buf))
        if unescape:
            out = [e.encode().decode('unicode-escape', 'ignore') if isinstance(e, str) else e for e in out]
        return group, list(out)

    @staticmethod
    def _extract(pattern, repl, string, count=0, flags=0):
        out = []
        for i, capture in enumerate(re.finditer(pattern, string, flags), 1):
            if count > 0 and i > count:
                break
            out.append(repl(capture))
        if out:
            return '\n'.join(out)
        return ''

    @classmethod
    def compile(cls, regex, replacement, count=0, evaluate=False, flags=re.MULTILINE, extract=False):
        replace_group, parsed = cls._parse(replacement, unescape=not evaluate)
        max_group = max(replace_group, max([n for n in parsed if isinstance(n, int)], default=0))
        group_tuple = namedtuple('Group', ['text', 'start', 'end'])

        def replace(text):
            def capture(m):
                groups = []
                for i in range(0,len(m.groups())+1):
                    groups.append(group_tuple(m.group(i), *m.span(i)))
                if max_group > len(groups):
                    raise IndexError(f'group ${max_group} does not exist')
                repl_str = ''
                if not evaluate:
                    repl_str = ''.join(
                        (groups[p][0] if isinstance(p, int) else p)
                        for p in parsed
                    )
                else:
                    group_params = {f'GROUP{i}': g.text for i, g in enumerate(groups)}
                    eval_text = ''.join((f'GROUP{e}' if isinstance(e, int) else e) for e in parsed)
                    repl_str = str(eval(eval_text, group_params))

                if replace_group == 0:
                    return repl_str
                out = []
                out.append(text[groups[0].start:groups[1].start])
                for i, g in enumerate(groups[1:], 1):
                    out.append(repl_str if i == replace_group else g.text)
                    if i+1 < len(groups):
                        out.append(text[groups[i].end:groups[i+1].start])
                    else:
                        out.append(text[groups[i].end:groups[0].end])
                return ''.join(out)
            if extract:
                return cls._extract(regex, capture, text, count=count, flags=flags)
            return re.sub(regex, capture, text, count=count, flags=flags)
        return replace

    @classmethod
    def sub(cls, regex, replacement, text, count=0, evaluate=False, flags=re.MULTILINE):
        return cls.compile(regex, replacement, count=count, evaluate=evaluate, flags=flags)(text)
