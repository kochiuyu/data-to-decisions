"""Accessible static components for the continuing retail case."""
from html import escape
from hashlib import sha256
from pathlib import Path
import re

STATIC=Path(__file__).resolve().parents[1]/'static'
PRESENT_JS_VERSION=sha256((STATIC/'presentation.js').read_bytes()).hexdigest()[:12]
PRESENT_CSS_VERSION=sha256((STATIC/'presentation.css').read_bytes()).hexdigest()[:12]

EXTRA_CSS = '''.brief{max-width:860px;background:var(--surface);border:1px solid var(--line);border-top:4px solid var(--green);border-radius:8px;padding:25px 30px;margin-top:30px}.brief h2{font-size:1.45rem}.brief p:last-child{margin-bottom:0}.stage-note{font-size:.88rem;font-weight:650;color:var(--muted);border-left:3px solid var(--green);padding-left:14px}.calculation{padding:18px 22px;background:var(--soft);border-radius:8px;font-weight:650;overflow-wrap:anywhere}.memo{border-left:4px solid var(--green);padding:8px 22px;background:var(--soft)}.memo p{margin:8px 0}.lesson-step figure{margin-bottom:22px}.lesson-step .table-scroll{margin-bottom:26px}.hero .brief h2{max-width:none}@media(max-width:720px){.brief{padding:20px}.calculation{padding:15px}.memo{padding:8px 16px}.hero h1{max-width:none}}'''

# Long inline design vectors must wrap in the reading view on narrow screens.
EXTRA_CSS += '.teaching-explanation{overflow-wrap:anywhere}'

def esc(v): return escape(str(v))
def p(*items): return ''.join('<p>'+esc(x)+'</p>' for x in items)
def formula(text): return '<p class="calculation">'+esc(text)+'</p>'
def table(headers,rows,caption):
    numeric=lambda value:bool(re.fullmatch(r'[-+−]?\d[\d,.]*(?:%)?',str(value)))
    numeric_columns=[all(numeric(row[j]) for row in rows) for j in range(len(headers))]
    return '<div class="table-scroll" tabindex="0" role="region" aria-label="'+esc(caption)+'"><table><caption>'+esc(caption)+'</caption><thead><tr>'+''.join('<th scope="col"'+(' class="number"' if numeric_columns[j] else '')+'>'+esc(x)+'</th>' for j,x in enumerate(headers))+'</tr></thead><tbody>'+''.join('<tr>'+''.join(('<th scope="row">'+esc(v)+'</th>') if j==0 else '<td'+(' class="number"' if numeric(v) else '')+'>'+esc(v)+'</td>' for j,v in enumerate(row))+'</tr>' for row in rows)+'</tbody></table></div>'

def distribution_figure(points,q1,median,q3,minimum,maximum):
    sx=lambda x:70+590*x/30;scale=max(row['density'] for row in points)
    upper=[(sx(row['rate']),100-55*row['density']/scale) for row in points]
    lower=[(sx(row['rate']),100+55*row['density']/scale) for row in reversed(points)]
    shape=' '.join(f'{x:.1f},{y:.1f}' for x,y in upper+lower)
    ticks=''.join(f'<text x="{sx(x)}" y="265" text-anchor="middle" font-size="14">{x}</text>' for x in range(0,31,5))
    return f'<figure><svg viewBox="0 0 720 310" role="img" aria-label="Density shape and quartiles of store stockout rates"><title>Density shape and quartiles of store stockout rates</title><desc>Upper violin shows a smoothed density. Lower box runs from the first to third quartile with a median mark. Exact summaries are in the accompanying tables.</desc><polygon points="{shape}" fill="#88b49a" stroke="#276451"/><text x="70" y="25">Smoothed distribution</text><line x1="{sx(minimum)}" x2="{sx(maximum)}" y1="210" y2="210" stroke="#276451"/><rect x="{sx(q1)}" y="190" width="{sx(q3)-sx(q1)}" height="40" fill="#eaf0e2" stroke="#276451"/><line x1="{sx(median)}" x2="{sx(median)}" y1="190" y2="230" stroke="#9b421e" stroke-width="4"/>{ticks}<text x="365" y="300" text-anchor="middle">Baseline stockout rate (%)</text></svg><figcaption>Density and quartiles of the same 150 store averages. The lower line spans the observed range.</figcaption></figure>'
def chart(x,series,title,xlabel='Week',ylabel='Stockout rate (%)'):
    xs=list(map(float,x)); ys=[float(v) for a in series.values() for v in a]
    xmin,xmax=min(xs),max(xs); ymin=0.; ymax=max(ys)*1.12 or 1; dx=xmax-xmin or 1
    colors=['#276451','#9b421e','#3259a2']; lines=[]
    for j,(name,values) in enumerate(series.items()):
        points=' '.join(f'{70+600*(a-xmin)/dx:.1f},{250-210*float(b)/ymax:.1f}' for a,b in zip(xs,values))
        lines.append(f'<polyline points="{points}" fill="none" stroke="{colors[j%3]}" stroke-width="3"'+(' stroke-dasharray="7 4"' if j%2 else '')+'/>')
    axes=''.join(f'<line x1="70" x2="670" y1="{250-52.5*j}" y2="{250-52.5*j}" stroke="#d3dcd0"/><text x="60" y="{255-52.5*j}" text-anchor="end" font-size="13">{ymax*j/4:.1f}</text>' for j in range(5))
    ticks=''.join(f'<text x="{70+600*(v-xmin)/dx}" y="276" text-anchor="middle" font-size="13">{v:g}</text>' for v in xs[::max(1,len(xs)//6)])
    legend='; '.join(name+(' (dashed)' if j%2 else ' (solid)') for j,name in enumerate(series))
    svg=f'<figure><svg viewBox="0 0 720 325" role="img" aria-label="{esc(title)}"><title>{esc(title)}</title><desc>{esc(ylabel)}; exact values follow in the table.</desc>{axes}{"".join(lines)}{ticks}<text x="360" y="310" text-anchor="middle">{esc(xlabel)}</text></svg><figcaption>{esc(title)}. {esc(legend)}. Vertical axis: {esc(ylabel)}.</figcaption></figure>'
    return svg+table([xlabel]+list(series),[[v]+[f'{float(a[i]):.2f}' for a in series.values()] for i,v in enumerate(xs)],title+' — values')

def shell(title,body,canonical=''):
    link=f'<link rel="canonical" href="https://kochiuyu.github.io/data-to-decisions/{canonical}">' if canonical else ''
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Ten lectures in business statistics: motivation, theory, and worked applications."><title>{esc(title)} · Data to decisions</title>{link}<link rel="stylesheet" href="assets/style.css"><link rel="stylesheet" href="assets/retail.css"><link rel="stylesheet" href="assets/presentation.css?v={PRESENT_CSS_VERSION}"><script src="assets/app.js" defer></script><script src="assets/presentation.js?v={PRESENT_JS_VERSION}" defer></script></head><body><a class="skip" href="#main">Skip to main content</a><header><div class="header-inner"><a class="brand" href="index.html"><span aria-hidden="true">d.</span><strong>Data to decisions<small>Concepts. Methods. Decisions.</small></strong></a><nav aria-label="Main"><a href="index.html">Course map</a><a href="study-guide.html">The case</a><a href="resources.html">Data & labs</a></nav></div></header>{body}<footer><p>Data to decisions · Applied business statistics</p><p><a href="index.html#teaching-data">About the case data</a> · <a href="synthesis.html">The final recommendation</a></p></footer></body></html>'

def presentation_launch():
    return '<div class="present-launch"><button type="button" data-present-start hidden>Present lesson</button><span>Read here or present the same material, one step at a time.</span></div>'

def presentation_dialog():
    return '''<dialog id="lesson-presentation" aria-label="Lesson presentation"><div class="slide-toolbar"><label for="slide-chooser">Go to slide</label><select class="slide-chooser" id="slide-chooser" aria-label="Go to slide"></select><span class="slide-counter" aria-live="polite"></span><button type="button" data-slide-fullscreen>Full screen</button><button type="button" data-slide-close aria-label="Exit presentation">Exit</button></div><div class="slide-layout"><div class="slide-card" tabindex="-1"><p class="slide-phase"></p><h2 class="slide-title"></h2><div class="slide-body"></div><span class="slide-scroll-hint" hidden>Scroll within this slide to see the remaining content.</span></div><aside class="slide-notes" aria-label="Teaching explanation" hidden></aside></div><div class="slide-controls"><div><button type="button" data-slide-prev>← Previous</button><button type="button" data-slide-next>Next →</button><span class="slide-help">Arrow keys · Home / End · Esc to exit</span></div><div><button type="button" data-slide-notes aria-pressed="false">Notes</button><button type="button" data-slide-read>Read this section</button><button type="button" data-slide-print>Print slides</button></div><span class="slide-status" role="status"></span></div></dialog>'''

def section(key,title,body): return dict(id=key,title=title,body=body)
def step_link(n,key,label='Follow this calculation further'):
    return f'<p class="text-link"><a href="lesson-{n}-appendix.html#{key}">{esc(label)} →</a></p>'

def bar_figure(rows,title):
    rows=[row for row in rows if row['count']];maximum=max(row['count'] for row in rows);width=600/len(rows)
    bars=''.join(f'<rect x="{70+i*width+3:.1f}" y="{240-190*row["count"]/maximum:.1f}" width="{width-6:.1f}" height="{190*row["count"]/maximum:.1f}" fill="#276451"/><text x="{70+(i+.5)*width:.1f}" y="{230-190*row["count"]/maximum:.1f}" text-anchor="middle">{row["count"]}</text><text x="{70+(i+.5)*width:.1f}" y="265" text-anchor="middle" font-size="14">{row["low"]:g}–{row["high"]:g}</text>' for i,row in enumerate(rows))
    return f'<figure><svg viewBox="0 0 720 320" role="img" aria-label="{esc(title)}"><title>{esc(title)}</title><desc>Bar heights count stores; exact counts appear in the following table.</desc><line x1="70" x2="675" y1="240" y2="240" stroke="#183f36"/>{bars}<text x="370" y="305" text-anchor="middle">Baseline stockout rate (%)</text><text x="70" y="25">Number of stores</text></svg><figcaption>{esc(title)}. Each store contributes one baseline average.</figcaption></figure>'

def scatter_figure(xs,ys,title,xlabel,ylabel,line=None,unit='store'):
    xs=list(map(float,xs));ys=list(map(float,ys));xmin=min(xs);xmax=max(xs);ymin=min(ys);ymax=max(ys)
    if line:ymin=min(ymin,min(y for x,y in line));ymax=max(ymax,max(y for x,y in line))
    dx=xmax-xmin or 1;dy=ymax-ymin or 1;ymin-=.08*dy;ymax+=.08*dy;dy=ymax-ymin
    sx=lambda v:75+585*(v-xmin)/dx;sy=lambda v:245-200*(v-ymin)/dy
    axes=''.join(f'<text x="{sx(xmin+dx*i/4):.1f}" y="270" text-anchor="middle" font-size="13">{xmin+dx*i/4:.1f}</text><text x="65" y="{sy(ymin+dy*i/4)+4:.1f}" text-anchor="end" font-size="13">{ymin+dy*i/4:.1f}</text><line x1="75" x2="665" y1="{sy(ymin+dy*i/4):.1f}" y2="{sy(ymin+dy*i/4):.1f}" stroke="#d6dfd1"/>' for i in range(5))
    dots=''.join(f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="3.2" fill="#276451" opacity=".48"/>' for x,y in zip(xs,ys))
    fitted='' if not line else '<polyline points="'+' '.join(f'{sx(x):.1f},{sy(y):.1f}' for x,y in line)+'" fill="none" stroke="#a44824" stroke-width="3"/>'
    return f'<figure><svg viewBox="0 0 720 325" role="img" aria-label="{esc(title)}"><title>{esc(title)}</title><desc>{len(xs)} plotted observations. Horizontal: {esc(xlabel)}. Vertical: {esc(ylabel)}. Data are in the shared results and store records.</desc>{axes}{dots}{fitted}<text x="360" y="310" text-anchor="middle">{esc(xlabel)}</text><text x="75" y="22">{esc(ylabel)}</text></svg><figcaption>{esc(title)}. Each dot represents one {esc(unit)}; overlapping dots remain separate observations.</figcaption></figure>'
