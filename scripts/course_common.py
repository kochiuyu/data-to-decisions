"""Shared static rendering helpers. No external observations are bundled."""
from pathlib import Path
import html, json, subprocess, sys
from business_cases import case
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
    """Publish a short business lesson and preserve the full lesson in an appendix."""
    result=json.loads((DIST/'assets'/f'lesson{number}-results.json').read_text(encoding='utf-8'))
    brief=case(number,result)
    toc=''.join(f'<li><a href="#{esc(s["id"])}">{i+1:02d}. {esc(s["title"])}</a></li>' for i,s in enumerate(sections))
    blocks=[]
    for i,s in enumerate(sections):
        check=''
        if s.get('check'):check='<aside class="check"><h3>Pause and explain</h3><p>'+s['check']+'</p><details><summary>Compare your reasoning</summary><div>'+s.get('answer','')+'</div></details></aside>'
        blocks.append(f'<section class="lesson-step" id="{esc(s["id"])}"><p class="eyebrow">Stop {i+1:02d} / {len(sections)}</p><h2>{esc(s["title"])}</h2>{s["body"]}{check}</section>')
    links=f'<a class="button" href="assets/lesson{number}-lab.ipynb" download>Download notebook</a> <a class="text-link" href="assets/lesson{number}-lab.py" download>Python script</a> <a class="text-link" href="assets/lesson{number}-results.json">Calculated results</a>'
    previous=f'<a href="lesson-{number-1}.html">← Lesson {number-1}</a>' if number>1 else '<a href="index.html">← Learning map</a>'
    nxt=f'<a href="lesson-{number+1}.html">Lesson {number+1} →</a>' if number<10 else '<a href="synthesis.html">Course synthesis →</a>'
    appendix=f'lesson-{number}-appendix.html'
    short=(f'<main id="main"><div class="hero wrap"><p class="eyebrow">Lesson {number} · Business route</p><h1>{esc(title)}</h1>'
           f'<p class="lead">{esc(brief["question"])}</p><div class="notice"><strong>Fictional case.</strong> The observations are generated for teaching, not evidence about a real business. The full data-generating process is in the <a href="{appendix}#generation">technical appendix</a>.</div></div>'
           f'<div class="content wrap"><section id="evidence"><h2>What the data show</h2><p>{esc(brief["evidence"])}</p></section>'
           f'<section id="decision"><h2>What would you decide?</h2><p>{esc(brief["decision"])}</p><aside class="check"><h3>Pause and explain</h3><p>{esc(brief["prompt"])}</p><details><summary>Compare your reasoning</summary><div><p>{esc(brief["answer"])}</p></div></details></aside></section>'
           f'<section id="reveal"><h2>What the generator knows</h2><details><summary>Reveal the known truth after making your judgment</summary><div><p>{esc(brief["truth"])}</p></div></details><p>The truth belongs to this invented model. A real organization would still need to test the assumptions and collect its own evidence.</p></section>'
           f'<section id="deeper"><h2>Go further if useful</h2><p>The <a href="{appendix}">technical appendix</a> has the generation rules, worked derivations, charts and all {len(sections)} original teaching stops. The notebook and script reproduce the case.</p></section>'
           f'<nav class="lesson-end" aria-label="Lessons">{previous}{nxt}</nav></div></main>')
    (DIST/f'lesson-{number}.html').write_text(shell(f'Lesson {number}: {title}',short),encoding='utf-8',newline='\n')
    detailed=(f'<main id="main"><div class="hero wrap"><p class="eyebrow">Lesson {number} · Optional technical appendix</p><h1>{esc(title)}: methods and data</h1>'
              f'<p class="lead">Keep the business question in view while inspecting how this fictional case was made and analyzed.</p><div class="downloads"><a class="button" href="lesson-{number}.html">Return to short lesson</a>{links}</div></div>'
              f'<div class="lesson-layout wrap"><aside class="roadmap"><details open><summary>Appendix roadmap</summary><ol><li><a href="#generation">Data generation</a></li>{toc}</ol></details></aside><article>'
              f'<section class="appendix-intro" id="generation"><p class="eyebrow">Reproducibility</p><h2>How the fictional data were generated</h2><p>{esc(brief["generator"])}</p><p><strong>Fixed seed:</strong> {esc(result["seed"])}. <a href="assets/lesson{number}-lab.py" download>Read the complete generator and analysis code</a>; <a href="assets/lesson{number}-results.json">inspect the saved results</a>.</p><p><strong>Known truth:</strong> {esc(brief["truth"])}</p><p>These are model assumptions and generated outcomes, not claims about a real population.</p></section>'
              +''.join(blocks)+f'<nav class="lesson-end" aria-label="Lessons"><a href="lesson-{number}.html">← Short lesson</a>{nxt}</nav></article></div></main>')
    (DIST/appendix).write_text(shell(f'Lesson {number} appendix: {title}',detailed),encoding='utf-8',newline='\n')
def write_lab(number,script,description):
    """Run the exact standalone source, record its fresh results and notebook stdout.
    Script must print only a JSON object and must never retrieve external inputs.
    """
    target=DIST/'assets'/f'lesson{number}-lab.py';target.write_text(script,encoding='utf-8',newline='\n')
    result=subprocess.run([sys.executable,str(target)],check=True,capture_output=True,text=True,cwd=ROOT)
    data=json.loads(result.stdout)
    (DIST/'assets'/f'lesson{number}-results.json').write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',newline='\n')
    nb={'cells':[{'cell_type':'markdown','id':f'lesson-{number}-intro','metadata':{},'source':[f'# Lesson {number}: reproducible synthetic lab\n',description+'\n','All observations are generated for teaching; they do not describe actual people, firms or markets. Run every cell from a fresh kernel. Dependencies: numpy, pandas, scipy, scikit-learn.\n']},{'cell_type':'code','id':f'lesson-{number}-analysis','execution_count':1,'metadata':{},'source':script.splitlines(keepends=True),'outputs':[{'output_type':'stream','name':'stdout','text':result.stdout.splitlines(keepends=True)}]}],'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':sys.version.split()[0]}},'nbformat':4,'nbformat_minor':5}
    (DIST/'assets'/f'lesson{number}-lab.ipynb').write_text(json.dumps(nb,indent=2)+'\n',newline='\n')
    return data
