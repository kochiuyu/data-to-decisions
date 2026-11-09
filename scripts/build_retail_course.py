"""Build the continuing retail case and its executable, self-contained labs."""
from pathlib import Path
import argparse,contextlib,io,json,sys
import retail_case
from retail_case import SPEC,world,all_results
from retail_content import MAP,lesson
from retail_ui import esc,p,table,formula,shell,EXTRA_CSS,presentation_launch,presentation_dialog
from curriculum_content import enrich
from presentation_content import outline,annotate_sections,lesson_points,EXTRA_POINTS,GENERATION_REVEAL

ROOT=Path(__file__).resolve().parents[1];DIST=ROOT/'dist';ASSETS=DIST/'assets'
def write(name,text):
    target=DIST/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,encoding='utf-8',newline='\n')
def downloads(n):
    return f'<div class="downloads"><a class="button" href="assets/lesson{n}-lab.ipynb" download>Work through the notebook</a><a href="assets/lesson{n}-lab.py" download>Standalone Python lab</a><a href="assets/lesson{n}-results.json">Calculated results</a></div>'
def navigation(n):
    before=f'<a href="lesson-{n-1}.html">← Lesson {n-1}</a>' if n>1 else '<a href="index.html">← Course questions</a>'
    after=f'<a href="lesson-{n+1}.html">Lesson {n+1} →</a>' if n<10 else '<a href="synthesis.html">Complete the recommendation →</a>'
    return '<nav class="lesson-end" aria-label="Lessons">'+before+after+'</nav>'
def publish_lesson(n,result):
    c=enrich(n,lesson(n,result),result); sections=c['sections']
    main_points,appendix_points=lesson_points(n,result)
    roadmap=''.join(f'<li><a href="#{s["id"]}">{esc(s["title"])}</a></li>' for s in sections)
    body=f'<main id="main"><div class="hero wrap"><p class="eyebrow">Lesson {n} · {esc(MAP[n-1][2])}</p><h1>{esc(c["title"])}</h1><p class="lead">{esc(c["inherited"])}</p><p class="stage-note">{esc(c["stage"])}</p><p><strong>Method in this decision:</strong> {esc(c["method"])}</p><div class="brief" id="decision-brief"><h2>The decision brief</h2>{p(c["brief"])}</div></div>'
    body=body.replace('<div class="brief"',presentation_launch()+'<div class="brief"',1)
    body+=f'<div class="lesson-layout wrap"><aside class="roadmap"><details open><summary>Follow the analysis</summary><ol>{roadmap}<li><a href="#memo">Update the decision memo</a></li><li><a href="#big-picture">The bigger picture</a></li></ol></details></aside><article>'
    for s in sections:
        body+=f'<section class="lesson-step" data-present-source id="{s["id"]}"><h2>{esc(s["title"])}</h2>{s["body"]}</section>'
    body+=f'<section class="lesson-step" id="memo"><h2>Update the decision memo</h2><div class="memo">{p(c["memo"])}</div><aside class="check"><h3>Make the call</h3>{p(c["question"])}<details><summary>Compare your reasoning</summary><div>{p(c["answer"])}</div></details></aside></section>'
    body+=f'<section class="lesson-step" id="big-picture"><h2>The bigger picture</h2>{p(c["bigger"])}<details><summary>After your decision: open the known answer</summary><div>{p(c["truth"])}</div></details><p><a href="lesson-{n}-appendix.html">Continue the same analysis in the technical appendix →</a></p>{downloads(n)}</section>{navigation(n)}</article></div></main>'
    body=body.replace('class="lesson-step" id="memo"','class="lesson-step" data-present-source id="memo"').replace('class="lesson-step" id="big-picture"','class="lesson-step" data-present-source id="big-picture"')
    body=annotate_sections(body,main_points)
    body=body.replace('<p class="lead">',outline([c['stage'],'Method: '+c['method']])+'<p class="lead">',1)
    body=body.replace('<h2>The decision brief</h2>','<h2>The decision brief</h2>'+outline(main_points['brief']))
    body=body.replace('<h3>Make the call</h3>','<h3>Make the call</h3>'+outline(main_points['question']))
    body=body.replace('<summary>Compare your reasoning</summary>','<summary>Compare your reasoning</summary>'+outline(main_points['answer'],'answer'))
    body=body.replace('<summary>After your decision: open the known answer</summary>','<summary>After your decision: open the known answer</summary>'+outline(main_points['truth'],'answer'))
    page=shell(c['title'],body+presentation_dialog(),f'lesson-{n}.html');write(f'lesson-{n}.html',page);write(f'lesson-{n}-guide.html',page)
    technical=c['technical']
    app=f'<main id="main"><div class="hero wrap"><p class="eyebrow">Lesson {n} · Technical continuation</p><h1>{esc(c["title"])}</h1><p class="lead">The same stores, calculation, and decision—with the specification and reproducible steps visible.</p><p class="stage-note">{esc(c["stage"])}</p><p><a href="lesson-{n}.html#calculate">← Return to the worked analysis</a></p></div><div class="content wrap">'
    app+=f'<section id="data"><h2>Use the same analysis rows</h2>{p(technical[0])}<p>Case seed: {SPEC["seed"]}. All ten labs use the same store IDs and underlying records. <a href="resources.html#dictionary">Read the shared data dictionary</a>.</p></section>'
    app+=f'<section id="calculation"><h2>Reproduce the calculation</h2>{p(technical[1])}<pre><code>{esc(c["code"])}</code></pre><p>The code runs after the shared setup in the notebook. The downloadable script includes that setup and runs on its own.</p></section>'
    app+=f'<section id="uncertainty"><h2>Read the model and uncertainty</h2>{p(technical[2])}</section><section id="extension"><h2>Change one analytical choice</h2>{p(technical[3])}</section>'
    app+=f'<section id="generation"><h2>How this case is generated</h2>{p("The shared world contains 150 stores followed for 32 weeks. Delivery time, location, demand, promotions, store differences, and a common time pattern generate the probability of a stockout. Each store-week contains 140 product-days. The generator draws their availability and records both policy paths using the same underlying draws.","The expected alert reduction varies with delivery time and location. Offers are randomized only within the 50-store pilot cohort. Voluntary adoption uses measured starting conditions in a separate cohort. The final cohort starts a selected rollout in week 25. These are distinct studies inside the same business history.")}<details><summary>Inspect the numerical mechanism</summary><div>{formula("p0 = 0.055 + 0.014 × lead + 0.0005 × (demand − 100) + 0.018 × urban + 0.003 × (lead − 3) × urban + 0.020 × promotion + store effect + 0.006 × sin(week / 4)")}{formula("Expected reduction = 0.006 + 0.008 × lead + 0.004 × urban; p1 = p0 − reduction")}{p("The probabilities are converted to counts by comparing 140 uniform draws with p0 or p1. Cost is 6 CU per stockout product-day plus 20 CU per week when alerts are offered. These costs are the stated management accounting scenario. The complete assignment rules, random streams, and calculations are in the shared source.")}</div></details><p><a href="assets/retail_case.py" download>Read the shared generator and analysis source</a></p></section>'
    app+=f'<section id="known-answer"><h2>Compare with the known answer</h2>{p(c["truth"])}</section>{downloads(n)}{navigation(n)}</div></main>'
    app=app.replace('</div><div class="content wrap">',presentation_launch()+'</div><div class="content wrap">',1)
    app=app.replace('<section id=','<section data-present-source id=')
    app=app.replace('<section data-present-source id="generation">',c.get('appendix_extra','')+'<section data-present-source id="generation">')
    app=app.replace('<section id=','<section data-present-source id=')
    app=app.replace('</div></main>',c.get('coverage','')+'</div></main>')
    app=annotate_sections(app,{**appendix_points,**EXTRA_POINTS})
    app=app.replace('<p class="lead">',outline([c['stage'],'Reproduce the model, calculation, and decision'])+'<p class="lead">',1)
    app=app.replace('<summary>Inspect the numerical mechanism</summary>','<summary>Inspect the numerical mechanism</summary>'+outline(GENERATION_REVEAL,'answer'))
    write(f'lesson-{n}-appendix.html',shell(c['title']+' — technical continuation',app+presentation_dialog()))
    source=(ROOT/'scripts/retail_case.py').read_text(encoding='utf-8')
    tail=c['code']+f'\nprint(json.dumps(lesson_result({n}), indent=2, allow_nan=False))\n'
    namespace=dict(retail_case.__dict__);captured=io.StringIO()
    with contextlib.redirect_stdout(captured): exec(compile(tail,f'lesson{n}-worked-step','exec'),namespace)
    output=captured.getvalue();assert json.loads(output)==result
    write(f'assets/lesson{n}-lab.py',source+'\n'+tail)
    write(f'assets/lesson{n}-results.json',output)
    notebook=dict(cells=[dict(cell_type='markdown',id=f'intro-{n}',metadata={},source=[f'# Lesson {n}: {c["title"]}\n',c['brief']+'\n','Run the shared setup, then trace the worked calculation. The same seed and stores are used in every lesson.\n']),
        dict(cell_type='code',id=f'setup-{n}',metadata={'jupyter':{'source_hidden':True}},execution_count=1,source=(source+'\n').splitlines(keepends=True),outputs=[]),
        dict(cell_type='markdown',id=f'worked-note-{n}',metadata={},source=['## Work through this lesson\n',technical[0]+'\n']),
        dict(cell_type='code',id=f'worked-{n}',metadata={},execution_count=2,source=tail.splitlines(keepends=True),outputs=[dict(output_type='stream',name='stdout',text=output.splitlines(keepends=True))])],metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':sys.version.split()[0]}},nbformat=4,nbformat_minor=5)
    write(f'assets/lesson{n}-lab.ipynb',json.dumps(notebook,indent=2,ensure_ascii=False)+'\n')
    return c

def publish_data():
    w=world();stores=w['stores'][['store_id','cohort','lead_days','urban','baseline_rate','baseline_demand','promotion_share','risk_group']]
    data={'stores.csv':stores,'store-weeks.csv':w['public'],'raw-baseline.csv':w['raw'],'baseline-repairs.csv':w['repairs'],
        'baseline.csv':w['public'].query('week<=16').drop(columns=['offer','active']),
        'shelf-audit.csv':w['audit'][['store_id','exposure','stockout_days','stockout_rate']]}
    for name,frame in data.items(): write('assets/'+name,frame.to_csv(index=False,float_format='%.8f',lineterminator='\n'))
    write('assets/retail_case.py',(ROOT/'scripts/retail_case.py').read_text(encoding='utf-8'))
    write('assets/requirements.txt',(ROOT/'requirements.txt').read_text(encoding='utf-8'))
    write('assets/case-spec.json',json.dumps(dict(**SPEC,data_fingerprint=w['fingerprint']),indent=2,ensure_ascii=False)+'\n')
    write('assets/course-results.json',json.dumps(all_results(),indent=2,ensure_ascii=False,allow_nan=False)+'\n')

def build(selected=None):
    result=all_results();publish_data();write('assets/retail.css',EXTRA_CSS)
    for name in ['presentation.js','presentation.css']:
        write('assets/'+name,(ROOT/'static'/name).read_text(encoding='utf-8'))
    for n in selected or range(1,11):
        publish_lesson(n,result[n]);print(f'Built retail lesson {n}',flush=True)
    if selected is None:
        from retail_pages import publish_pages
        publish_pages(write,result)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--pilot',action='store_true');args=parser.parse_args()
    build([1,6,9] if args.pilot else None)
