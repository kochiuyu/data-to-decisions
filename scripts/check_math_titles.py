"""Verify published outlines match real slides and equations retain authored content."""
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import re
from slide_titles import Tree, groups
from math_render import EXPRESSIONS, typeset

ROOT=Path(__file__).resolve().parents[1]

def check():
    for source,lines in EXPRESSIONS.items():
        rendered=[]
        for tex in lines:
            root=ET.fromstring(typeset(tex))
            assert root.tag=='{http://www.w3.org/1998/Math/MathML}math'
            text=' '.join(root.itertext())
            assert '\\' not in text, (source,'Unrendered TeX',text)
            rendered.append(text)
        numbers=lambda s:set(re.findall(r'(?<![A-Za-z])\d+(?:\.\d+)?',s))
        assert numbers(source)<=numbers(' '.join(rendered)), (source,'Missing numerical value')
    slides=equations=0
    for n in range(1,11):
        for suffix in ['', '-appendix']:
            path=ROOT/'dist'/f'lesson-{n}{suffix}.html'
            html=path.read_text(encoding='utf-8')
            tree=Tree(html)
            names=[name for _,node,_ in groups(html) for name in json.loads(node.attrs['data-slide-titles'])]
            outline=tree.root.find(lambda c:c.has('skim-outline'))
            links=[node for node in outline.walk() if node.tag=='a']
            assert [a.text() for a in links]==names, (path,'Outline and deck differ')
            assert all(a.attrs['href']==path.name+f'?present=1&slide={i}' for i,a in enumerate(links,1))
            assert not any('?' in name or name.startswith(('Reproduce ','Trace ','Reconstruct the calculation','Transfer the method')) for name in names), (path,'Generic or question-only slide title')
            for node in tree.root.walk():
                if node.has('calculation'):
                    assert node.has('typeset-math') and node.find(lambda c:c.tag=='math' or c.has('math-prose')),path
                    assert node.attrs['data-equation-source'] in EXPRESSIONS,path
                    equations+=1
            slides+=len(names)
    print(json.dumps(dict(takeaway_titles=slides,equation_blocks=equations,unique_authored_equations=len(EXPRESSIONS),outline_links='passed',math_structure_and_numbers='passed')))

if __name__=='__main__': check()
