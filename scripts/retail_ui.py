"""Accessible static components for the continuing retail case."""
from html import escape

EXTRA_CSS = '''.brief{max-width:860px;background:var(--surface);border:1px solid var(--line);border-top:4px solid var(--green);border-radius:8px;padding:25px 30px;margin-top:30px}.brief h2{font-size:1.45rem}.brief p:last-child{margin-bottom:0}.stage-note{font-size:.88rem;font-weight:650;color:var(--muted);border-left:3px solid var(--green);padding-left:14px}.calculation{padding:18px 22px;background:var(--soft);border-radius:8px;font-weight:650;overflow-wrap:anywhere}.memo{border-left:4px solid var(--green);padding:8px 22px;background:var(--soft)}.memo p{margin:8px 0}.lesson-step figure{margin-bottom:22px}.lesson-step .table-scroll{margin-bottom:26px}.hero .brief h2{max-width:none}@media(max-width:720px){.brief{padding:20px}.calculation{padding:15px}.memo{padding:8px 16px}.hero h1{max-width:none}}'''

def esc(v): return escape(str(v))
def p(*items): return ''.join('<p>'+esc(x)+'</p>' for x in items)
def formula(text): return '<p class="calculation">'+esc(text)+'</p>'
def table(headers,rows,caption):
    return '<div class="table-scroll" tabindex="0" role="region" aria-label="'+esc(caption)+'"><table><caption>'+esc(caption)+'</caption><thead><tr>'+''.join('<th scope="col">'+esc(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join(('<th scope="row">'+esc(v)+'</th>') if j==0 else '<td>'+esc(v)+'</td>' for j,v in enumerate(row))+'</tr>' for row in rows)+'</tbody></table></div>'
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
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="One retail decision, ten connected lessons in data analysis."><title>{esc(title)} · Data to decisions</title>{link}<link rel="stylesheet" href="assets/style.css"><link rel="stylesheet" href="assets/retail.css"><script src="assets/app.js" defer></script></head><body><a class="skip" href="#main">Skip to main content</a><header><div class="header-inner"><a class="brand" href="index.html"><span aria-hidden="true">d.</span><strong>Data to decisions<small>One case. Ten decisions.</small></strong></a><nav aria-label="Main"><a href="index.html">Course map</a><a href="study-guide.html">The case</a><a href="resources.html">Data & labs</a></nav></div></header>{body}<footer><p>Data to decisions · Applied business statistics</p><p><a href="index.html#teaching-data">About the case data</a> · <a href="synthesis.html">The final recommendation</a></p></footer></body></html>'

def section(key,title,body): return dict(id=key,title=title,body=body)
def step_link(n,key,label='Follow this calculation further'):
    return f'<p class="text-link"><a href="lesson-{n}-appendix.html#{key}">{esc(label)} →</a></p>'
