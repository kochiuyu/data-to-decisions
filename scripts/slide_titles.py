"""Authored takeaway titles, attached to the lesson's own presentation sections.

The build checks the title count against the actual visual blocks, including
table and code continuations. A changed lesson must update its title sequence.
"""
from html.parser import HTMLParser
from html import escape
import json
from slide_headlines import MAIN, APPENDIX


class Node:
    def __init__(self, tag='', attrs=(), start=0, end=0):
        self.tag, self.attrs, self.start, self.end = tag, dict(attrs), start, end
        self.children = []

    def has(self, name):
        return name in self.attrs.get('class', '').split()

    def text(self):
        return ''.join(c if isinstance(c, str) else c.text() for c in self.children)

    def elements(self):
        return [c for c in self.children if isinstance(c, Node)]

    def find(self, predicate):
        return next((c for c in self.walk() if predicate(c)), None)

    def walk(self):
        for c in self.elements():
            yield c
            yield from c.walk()


class Tree(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.html = html
        self.offsets = [0]
        for line in html.splitlines(keepends=True):
            self.offsets.append(self.offsets[-1] + len(line))
        self.root = Node()
        self.stack = [self.root]
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        line, col = self.getpos()
        start = self.offsets[line-1] + col
        node = Node(tag, attrs, start, start+len(self.get_starttag_text()))
        self.stack[-1].children.append(node)
        if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def visual_frames(container, heading):
    """Mirror the public presentation's documented splitting rules."""
    children = container.elements()
    template = next((c for c in children if 'data-slide-outline' in c.attrs), None)
    detail = next((c for c in children if c.tag == 'details'), None) if container.has('check') else None
    frames = []
    if template:
        frames.append((heading, template.text()))
    i = 0
    while i < len(children):
        node = children[i]
        i += 1
        if node is detail or node.tag in {'h2','h3','template','nav'} or any(node.has(c) for c in ['memo','downloads','text-link']):
            continue
        if node.tag == 'p' and not node.has('calculation'):
            continue
        if node.has('teaching-block'):
            frames += visual_frames(node.find(lambda c:c.has('teaching-visual')), node.attrs['data-presentation-title'])
            continue
        if node.has('check'):
            frames += visual_frames(node, node.find(lambda c:c.tag=='h3').text())
            continue
        if node.tag in {'ul','ol'} and i < len(children) and children[i].tag == 'details':
            frames.append((heading, node.text()))
            i += 1
            continue
        if node.has('table-scroll'):
            tbody = node.find(lambda c:c.tag=='tbody')
            rows = tbody.elements() if tbody else []
            for j in range(0, max(1,len(rows)), 6):
                frames.append((heading, ' | '.join(r.text() for r in rows[j:j+6])))
        elif node.tag == 'pre':
            lines = node.text().rstrip().split('\n')
            for j in range(0,len(lines),10):
                frames.append((heading, '\n'.join(lines[j:j+10])))
        else:
            frames.append((heading, node.text()))
    return frames


def groups(html):
    tree = Tree(html)
    hero = tree.root.find(lambda c:c.has('hero'))
    yield 'main', hero, [(hero.find(lambda c:c.tag=='h1').text(), hero.text())]
    brief = tree.root.find(lambda c:c.has('brief'))
    if brief:
        yield 'decision-brief', brief, visual_frames(brief, 'The decision brief')
    for node in tree.root.walk():
        if 'data-present-source' in node.attrs:
            yield node.attrs['id'], node, visual_frames(node,node.find(lambda c:c.tag=='h2').text())


def apply_titles(html, number, appendix=False):
    titles = APPENDIX[number] if appendix else MAIN[number]
    sections = list(groups(html))
    assert set(titles) == {key for key,_,_ in sections}, (number,appendix,set(titles),[k for k,_,_ in sections])
    edits = []
    seen = set()
    for key, node, frames in sections:
        names = titles[key]
        assert len(names) == len(frames), (number,appendix,key,len(names),len(frames))
        for name in names:
            assert 3 <= len(name.split()) <= 16, (number,key,name)
            assert name not in seen, (number,key,name)
            seen.add(name)
        attr = ' data-slide-titles="'+escape(json.dumps(names,ensure_ascii=False),quote=True)+'"'
        edits.append((node.end-1,attr))
    for at,text in sorted(edits,reverse=True):
        html = html[:at]+text+html[at:]
    return html


if __name__ == '__main__':
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    for n in range(1,11):
        for suffix in ['', '-appendix']:
            print(f'\nLESSON {n}{suffix}')
            for key,_,frames in groups((root/'dist'/f'lesson-{n}{suffix}.html').read_text(encoding='utf-8')):
                print(key)
                for title,text in frames:
                    print('  '+title+' :: '+' '.join(text.split())[:230])
