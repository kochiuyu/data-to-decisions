"""Shared static rendering helpers. No external observations are bundled."""
from pathlib import Path
import html, json, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
def esc(value): return html.escape(str(value))
def table(headers,rows,caption):
    return '<div class="table-scroll" tabindex="0" role="region" aria-label="'+esc(caption)+'"><table><caption>'+esc(caption)+'</caption><thead><tr>'+''.join('<th scope="col">'+esc(v)+'</th>' for v in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join(('<th scope="row">'+esc(v)+'</th>') if i==0 else '<td>'+esc(v)+'</td>' for i,v in enumerate(row))+'</tr>' for row in rows)+'</tbody></table></div>'
def bars(labels,values,title,ylabel='Value'):
    """Zero-baseline bar chart. Accessible table preserves all plotted values."""
    vals=[float(v) for v in values]; lo=min(0.,min(vals)); hi=max(0.,max(vals)); span=hi-lo or 1
    w=720; h=360; left=70; top=30; ph=240; pw=620; zero=top+hi/span*ph
    svg=f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}"><title>{esc(title)}</title><desc>{esc(ylabel)}. Values are provided in the following table.</desc>'
    for i in range(5):
        val=lo+span*i/4; y=top+(hi-val)/span*ph
        svg+=f'<line x1="{left}" y1="{y:.2f}" x2="690" y2="{y:.2f}" stroke="#d4ddd4"/><text x="60" y="{y+5:.2f}" text-anchor="end" font-size="14">{val:.3g}</text>'
    for i,(label,v) in enumerate(zip(labels,vals)):
        x=left+(i+.15)*pw/len(vals); bw=.7*pw/len(vals); vy=top+(hi-v)/span*ph
        svg+=f'<rect x="{x:.2f}" y="{min(zero,vy):.2f}" width="{bw:.2f}" height="{max(1,abs(zero-vy)):.2f}" fill="#276451"/><text x="{x+bw/2:.2f}" y="300" font-size="13" text-anchor="middle">{esc(label)}</text>'
    svg+=f'<text x="{left}" y="343" font-size="14">{esc(ylabel)} · Synthetic teaching data</text></svg>'
    return '<figure>'+svg+'<figcaption>'+esc(title)+' All plotted observations are synthetic.</figcaption></figure>'+table(['Group',ylabel],list(zip(labels,[f'{v:.6g}' for v in vals])),title+' — chart data')
def line_chart(x,series,title,xlabel='X',ylabel='Y'):
    """series is a mapping label -> same-length numeric y sequence."""
    xx=list(map(float,x)); ys=[float(v) for a in series.values() for v in a]; xmin,xmax=min(xx),max(xx); ymin,ymax=min(ys),max(ys); dx=xmax-xmin or 1; dy=ymax-ymin or 1
    pad=dy*.08;ymin-=pad;ymax+=pad;dy=ymax-ymin
    colors=['#276451','#ab4e24','#3259a2','#8055a0']; paths=''
    for i,(label,values) in enumerate(series.items()):
        pts=' '.join(f'{70+(a-xmin)/dx*600:.2f},{30+(ymax-float(b))/dy*230:.2f}' for a,b in zip(xx,values))
        paths+=f'<polyline fill="none" stroke="{colors[i%4]}" stroke-width="3" points="{pts}"'+(' stroke-dasharray="7 4"' if i%2 else '')+'/>'
    axes=''
    for i in range(5):
        xp=70+i*150;yp=30+i*57.5
        axes+=f'<text x="{xp}" y="285" text-anchor="middle" font-size="13">{xmin+dx*i/4:.3g}</text><text x="60" y="{yp+5}" text-anchor="end" font-size="13">{ymax-dy*i/4:.3g}</text><line x1="70" y1="{yp}" x2="670" y2="{yp}" stroke="#d4ddd4"/>'
    legend=' '.join(f'<span style="color:{colors[i%4]}">{esc(label)} ({"dashed" if i%2 else "solid"})</span>' for i,label in enumerate(series))
    return f'<figure><svg viewBox="0 0 720 330" role="img" aria-label="{esc(title)}"><title>{esc(title)}</title><desc>{esc(xlabel)} versus {esc(ylabel)}. Values follow in the chart table.</desc>{axes}{paths}<text x="370" y="320" text-anchor="middle">{esc(xlabel)}</text></svg><figcaption>{esc(title)}. {legend}. Vertical axis: {esc(ylabel)}.</figcaption></figure>'+table([xlabel]+list(series),[[f'{a:.6g}']+[f'{float(b[i]):.6g}' for b in series.values()] for i,a in enumerate(xx)],title+' — chart data')
def shell(title,body,current=''):
    nav='<a href="index.html">Learning map</a><a href="study-guide.html">Study guide</a><a href="resources.html">Data & labs</a>'
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="A reproducible applied statistics course using original synthetic teaching datasets."><title>{esc(title)} · Data to decisions</title><link rel="stylesheet" href="assets/style.css"><script src="assets/app.js" defer></script></head><body><a class="skip" href="#main">Skip to main content</a><header><div class="header-inner"><a class="brand" href="index.html"><span aria-hidden="true">d.</span><strong>Data to decisions<small>Applied business statistics</small></strong></a><nav aria-label="Main">{nav}</nav></div></header>{body}<footer><p>Data to decisions · Public synthetic edition</p><p>All case observations are generated for teaching. They are not evidence about real people, firms or markets. <a href="resources.html">Provenance and reproduction</a></p></footer></body></html>'
def render_lesson(number,title,intro,sections,*,outcomes=None):
    """sections: list of dicts id,title,body (HTML), optional check/answer."""
    toc=''.join(f'<li><a href="#{esc(s["id"])}">{i+1:02d}. {esc(s["title"])}</a></li>' for i,s in enumerate(sections))
    blocks=[]
    for i,s in enumerate(sections):
        check=''
        if s.get('check'):check='<aside class="check"><h3>Pause and explain</h3><p>'+s['check']+'</p><details><summary>Compare your reasoning</summary><div>'+s.get('answer','')+'</div></details></aside>'
        blocks.append(f'<section class="lesson-step" id="{esc(s["id"])}"><p class="eyebrow">Stop {i+1:02d} / {len(sections)}</p><h2>{esc(s["title"])}</h2>{s["body"]}{check}</section>')
    links=f'<a class="button" href="assets/lesson{number}-lab.ipynb" download>Download notebook</a> <a class="text-link" href="assets/lesson{number}-lab.py" download>Python script</a> <a class="text-link" href="assets/lesson{number}-results.json">Calculated results</a>'
    previous=f'<a href="lesson-{number-1}.html">← Lesson {number-1}</a>' if number>1 else '<a href="index.html">← Learning map</a>'
    nxt=f'<a href="lesson-{number+1}.html">Lesson {number+1} →</a>' if number<10 else '<a href="synthesis.html">Course synthesis →</a>'
    body=f'<main id="main"><div class="hero wrap"><p class="eyebrow">Lesson {number} · Public synthetic edition</p><h1>{esc(title)}</h1><p class="lead">{intro}</p><div class="notice"><strong>Synthetic, reproducible examples.</strong> All case data in this lesson are newly generated from documented assumptions and fixed seeds. No historical source records or their fitted results are reused.</div><div class="downloads">{links}</div></div><div class="lesson-layout wrap"><aside class="roadmap"><details open><summary>Lesson roadmap</summary><ol>{toc}</ol></details></aside><article>'+''.join(blocks)+f'<nav class="lesson-end" aria-label="Lessons">{previous}{nxt}</nav></article></div></main>'
    (DIST/f'lesson-{number}.html').write_text(shell(f'Lesson {number}: {title}',body),encoding='utf-8')
def write_lab(number,script,description):
    """Run the exact standalone source, record its fresh results and notebook stdout.
    Script must print only a JSON object and must never retrieve external inputs.
    """
    target=DIST/'assets'/f'lesson{number}-lab.py';target.write_text(script,encoding='utf-8')
    result=subprocess.run([sys.executable,str(target)],check=True,capture_output=True,text=True,cwd=ROOT)
    data=json.loads(result.stdout)
    (DIST/'assets'/f'lesson{number}-results.json').write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
    nb={'cells':[{'cell_type':'markdown','id':f'lesson-{number}-intro','metadata':{},'source':[f'# Lesson {number}: reproducible synthetic lab\n',description+'\n','All observations are generated for teaching; they do not describe actual people, firms or markets. Run every cell from a fresh kernel. Dependencies: numpy, pandas, scipy, scikit-learn.\n']},{'cell_type':'code','id':f'lesson-{number}-analysis','execution_count':1,'metadata':{},'source':script.splitlines(keepends=True),'outputs':[{'output_type':'stream','name':'stdout','text':result.stdout.splitlines(keepends=True)}]}],'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':sys.version.split()[0]}},'nbformat':4,'nbformat_minor':5}
    (DIST/'assets'/f'lesson{number}-lab.ipynb').write_text(json.dumps(nb,indent=2)+'\n')
    return data
