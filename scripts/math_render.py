"""Typeset authored equations as native MathML at build time, including offline use."""
from functools import lru_cache
from html import escape, unescape
from pathlib import Path
import json
import re
from latex2mathml.converter import convert

EXPRESSIONS = json.loads((Path(__file__).resolve().parents[1] / 'content/math-expressions.json').read_text(encoding='utf-8'))
BLOCK = re.compile(r'<p class="calculation">(.*?)</p>', re.S)

def source_text(inner):
    return unescape(re.sub(r'<br\s*/?>', '\n', inner)).strip()

@lru_cache(maxsize=None)
def typeset(tex):
    # TeX is authored in the repository; no remote renderer or runtime script is needed.
    return convert(tex, display='block')

def render_line(tex):
    prose=re.fullmatch(r'\\text\{([^{}]*)\}',tex)
    if prose:
        return '<span class="math-prose">'+escape(prose[1])+'</span>'
    return '<span class="math-line">'+typeset(tex)+'</span>'

def render_math(body):
    def replace(match):
        source = source_text(match[1])
        if source not in EXPRESSIONS:
            raise ValueError('Equation needs an explicit TeX transcription: ' + repr(source))
        lines = ''.join(render_line(tex) for tex in EXPRESSIONS[source])
        return '<p class="calculation typeset-math" data-equation-source="' + escape(source, quote=True) + '">' + lines + '</p>'
    return BLOCK.sub(replace, body)
