"""Reviewed takeaway titles and a reading-mode outline derived from the actual deck."""
from html import escape
from pathlib import Path
import json

OVERRIDES=json.loads((Path(__file__).resolve().parents[1]/'content/skim-titles.json').read_text(encoding='utf-8'))

def revise_titles(number, titles, appendix=False):
    revised={key:list(values) for key,values in titles.items()}
    for item in OVERRIDES:
        if (item['lesson'],item['appendix']) != (number,appendix): continue
        key,index=item['section'],item['index']
        assert revised[key][index] == item['old'], (number,appendix,key,index,revised[key][index])
        revised[key][index]=item['title']
    return revised

def revise_lesson(number, content):
    content['headlines']=revise_titles(number,content['headlines'])
    # Keep authored reading headings aligned with the corresponding slide takeaway.
    for item in OVERRIDES:
        if item['lesson'] != number or item['appendix']: continue
        old,new=escape(item['old'],quote=True),escape(item['title'],quote=True)
        for section in content['sections']:
            section['body']=section['body'].replace('data-presentation-title="'+old+'"','data-presentation-title="'+new+'"').replace('<h3>'+old+'</h3>','<h3>'+new+'</h3>')
    return content

def add_skim_outline(body, number, appendix=False):
    from slide_titles import groups
    names=[title for _,node,_ in groups(body) for title in json.loads(node.attrs['data-slide-titles'])]
    filename=f'lesson-{number}'+('-appendix' if appendix else '')+'.html'
    links=''.join(f'<li><a href="{filename}?present=1&amp;slide={i}">{escape(title)}</a></li>' for i,title in enumerate(names,1))
    outline='<div class="wrap"><details class="skim-outline"><summary>Read the lesson in its slide titles</summary><p>Follow the argument in order. Open any title to study its evidence, calculation and explanation.</p><ol>'+links+'</ol></details></div>'
    anchor='<div class="content wrap">' if appendix else '<div class="lesson-layout wrap">'
    assert anchor in body
    return body.replace(anchor,outline+anchor,1)
