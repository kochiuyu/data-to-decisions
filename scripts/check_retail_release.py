"""Check shared data, meaningful numerical identities, pages, and independent labs."""
from pathlib import Path
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor
import ast,json,re,sys,subprocess,urllib.parse,math,os,hashlib
import numpy as np
import pandas as pd
from retail_case import world,all_results,SPEC,nearest_score_match
from curriculum_map import validate_coverage,SLIDE_COUNTS
from slide_titles import groups
from slide_headlines import APPENDIX
from lecture_structure import reorganize
from curriculum_content import enrich
from retail_content import lesson
ROOT=Path(__file__).resolve().parents[1];SITE=ROOT/'dist'

class Page(HTMLParser):
    def __init__(self,text):
        super().__init__(convert_charrefs=True);self.ids=[];self.links=[];self.h1=0;self.svgs=0;self.named_svgs=0;self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):self.ids.append(a['id'])
        for key in ('href','src'):
            if a.get(key):self.links.append(a[key])
        if tag=='h1':self.h1+=1
        if tag=='svg':
            self.svgs+=1
            if a.get('aria-label') or a.get('aria-labelledby'):self.named_svgs+=1

def equivalent(a,b):
    if isinstance(a,bool) or isinstance(b,bool):return a==b
    if isinstance(a,(int,float)) and isinstance(b,(int,float)):
        return math.isfinite(a) and math.isfinite(b) and math.isclose(a,b,rel_tol=1e-8,abs_tol=1e-8)
    if isinstance(a,dict):return isinstance(b,dict) and a.keys()==b.keys() and all(equivalent(a[k],b[k]) for k in a)
    if isinstance(a,list):return isinstance(b,list) and len(a)==len(b) and all(equivalent(x,y) for x,y in zip(a,b))
    return a==b

def check_science():
    controls=pd.DataFrame({'store_id':['S002','S001','S003'],'logit':[1.,-1.,4.]},index=[20,10,30])
    for perturbation in [-1e-14,0,1e-14]:
        assert nearest_score_match(controls,perturbation)==10
        assert nearest_score_match(controls.iloc[::-1],perturbation)==10
    assert nearest_score_match(controls,.01)==20
    w=world();p=w['panel'];s=w['stores'];r=all_results()
    assert len(s)==150 and s.store_id.is_unique
    assert len(p)==150*32 and not p.duplicated(['store_id','week']).any()
    assert s.groupby('cohort').size().to_dict()=={'Pilot':50,'Rollout':50,'Voluntary':50}
    assert s.query("cohort=='Pilot'").offer.sum()==25 and s.query("cohort=='Rollout'").offer.sum()==25
    assert not p.query('week<=16').active.any()
    assert not p.query("cohort=='Rollout' and week<25").active.any()
    assert (p.exposure==140).all() and p.stockout_days.between(0,140).all()
    assert np.allclose(p.stockout_rate,100*p.stockout_days/p.exposure)
    assert np.allclose(p.operating_cost,6*p.stockout_days+20*p.active)
    assert (p.y1<=p.y0).all() and (p.p0-p.effect_pp/100>0).all()
    assert not {'p0','effect_pp','y0','y1','store_effect'} & set(w['public'].columns)
    assert math.isclose(r[1]['rate'],r[2]['mean'])
    assert (r[1]['raw'],r[1]['duplicates'],r[1]['flagged'],r[1]['clean'])==(1212,12,12,1200)
    assert r[3]['n']==30 and w['audit'].store_id.is_unique
    assert r[6]['windows']==dict(training=[3,10],validation=[11,13],test=[14,16])
    assert not {'stockout_rate','demand_index','offer','active','operating_cost'} & set(r[6]['features'])
    assert r[6]['test_n']==450
    assert np.isclose(r[7]['savings']['value'],8.4*r[7]['effect']['value']-20)
    assert np.isclose(sum(x['weight'] for x in r[8]['strata']),1)
    assert np.isclose(sum(x['contribution'] for x in r[8]['strata']),r[8]['standardized'])
    assert all(x['offered']>0 and x['control']>0 for x in r[8]['strata'])
    assert np.isclose(r[9]['predicted_usual']-r[9]['predicted_alert'],r[9]['estimate'])
    assert all(np.isclose(x['usual_prediction']-x['alert_prediction'],x['reduction']) for x in r[9]['sample'])
    assert np.isclose(r[10]['comparison_change']-r[10]['adopter_change'],r[10]['effect']['value'])
    assert np.isclose(r[10]['counterfactual']-r[10]['adopter_post'],r[10]['effect']['value'])
    assert np.isclose(r[10]['savings']['value'],8.4*r[10]['effect']['value']-20)
    public=pd.read_csv(SITE/'assets/store-weeks.csv')
    assert hashlib.sha256((SITE/'assets/store-weeks.csv').read_bytes()).hexdigest()==w['fingerprint']
    assert public.shape==w['public'].shape and public.store_id.tolist()==w['public'].store_id.tolist()
    assert np.allclose(public.stockout_rate,w['public'].stockout_rate,atol=1e-7)
    baseline=pd.read_csv(SITE/'assets/baseline.csv')
    assert baseline.week.max()==16 and not {'offer','active'} & set(baseline.columns)
    for histogram in r[2]['depth']['histograms']:
        assert sum(b['count'] for b in histogram['bins'])==150
    for g in r[2]['depth']['composition']:assert np.isclose(sum(g['percent']),100)
    assert 0<=r[3]['depth']['proportion']['low']<=r[3]['depth']['proportion']['high']<=1
    d=r[4]['depth'];assert np.isclose(d['sst'],d['sse']+d['ssr'])
    d=r[5]['depth']['ovb'];assert np.isclose(d['short'],d['long']+d['product'])
    for row in r[5]['depth']['intervals']:
        assert row['prediction_low']<row['mean_low']<row['mean_high']<row['prediction_high']
    d=r[6]['depth'];assert d['alpha']==min(d['tuning'],key=lambda v:v['rmse'])['alpha']
    assert all(v['train_end']<v['validation_start']<=v['validation_end']<=13 for v in d['folds'])
    d=r[7]['depth'];assert np.isclose(d['ate'],d['treated_share']*d['att']+(1-d['treated_share'])*d['atu'])
    assert np.isclose(r[7]['effect']['value'],d['att']+d['selection_component'])
    for name in ['ate','att','atu']:
        assert np.isclose(sum(g[name+'_weight'] for g in r[8]['depth']['weights']),1)
    for row in r[9]['depth']['matching']:assert 0<row['matched_adopters']<=row['total_adopters']
    assert np.isclose(r[10]['depth']['regression_reduction'],r[10]['effect']['value'])
    return r

def validate(execute=False):
    validate_coverage()
    results=check_science()
    texts={path:path.read_text(encoding='utf-8') for path in SITE.glob('*.html')}
    pages={path:Page(txt) for path,txt in texts.items()};assert len(pages)==35
    for path,page in pages.items():
        assert page.h1==1,(path,'H1');assert len(page.ids)==len(set(page.ids)),(path,'Duplicate IDs')
        assert page.svgs==page.named_svgs,(path,'Unlabeled figure')
        for url in page.links:
            u=urllib.parse.urlsplit(url)
            if u.scheme or u.netloc:continue
            dest=(path.parent/urllib.parse.unquote(u.path)).resolve() if u.path else path.resolve()
            assert dest.is_relative_to(SITE.resolve()) and dest.is_file(),(path,'Missing file',url)
            if u.fragment and dest.suffix=='.html':assert urllib.parse.unquote(u.fragment) in Page(dest.read_text(encoding='utf-8')).ids,(path,'Missing anchor',url)
        assert not re.search(r'lodging|powered fixtures|calibration rigs|dispatch.cost|online quote',texts[path],re.I),(path,'Unrelated legacy case')
    lengths={}
    for n in range(1,11):
        text=texts[SITE/f'lesson-{n}.html'];page=pages[SITE/f'lesson-{n}.html']
        authored_main=reorganize(n,enrich(n,lesson(n,results[n]),results[n]))['headlines']
        observed_phases=[]
        for suffix,authored in [('',authored_main),('-appendix',APPENDIX[n])]:
            for key,node,frames in groups(texts[SITE/f'lesson-{n}{suffix}.html']):
                titles=json.loads(node.attrs['data-slide-titles'])
                assert titles==authored[key],(n,suffix,key,'Title source drift')
                assert len(titles)==len(frames),(n,suffix,key,'Title/frame mismatch')
                assert all(content.strip() for _,content in frames),(n,suffix,key,'Empty visual frame')
                if not suffix:observed_phases.extend([node.attrs['data-teaching-phase']]*len(frames))
        phase_order={'Business motivation':0,'General theory':1,'Worked application':2,'Decision and synthesis':3,'Synthesis':4}
        assert [phase_order[x] for x in observed_phases]==sorted(phase_order[x] for x in observed_phases),(n,'Theory/application interleaving')
        assert observed_phases.count('Business motivation')==2 and observed_phases.count('General theory')>=7
        assert text==texts[SITE/f'lesson-{n}-guide.html'],(n,'Guide bookmark must retain the full lesson')
        assert all(k in page.ids for k in ['decision-brief','read-data','calculate','interpret','act','memo','big-picture'])
        assert '<table>' in text and f'lesson-{n}-appendix.html#calculation' in text
        assert 'data-present-start' in text and 'data-present-source' in text and 'teaching-block' in text
        main=text.split('<main',1)[1].split('</main>')[0];lengths[n]=len(re.sub('<[^>]+>',' ',main).split())
        assert lengths[n]>=650,(n,'Insufficient core explanation',lengths[n])
        assert all(k in pages[SITE/f'lesson-{n}-appendix.html'].ids for k in ['data','calculation','uncertainty','extension','generation','known-answer'])
        assert 'original-coverage' in pages[SITE/f'lesson-{n}-appendix.html'].ids
        data=json.loads((SITE/f'assets/lesson{n}-results.json').read_text(encoding='utf-8'))
        assert equivalent(data,results[n]),(n,'Saved analysis differs')
        src=(SITE/f'assets/lesson{n}-lab.py').read_text(encoding='utf-8');ast.parse(src)
        nb=json.loads((SITE/f'assets/lesson{n}-lab.ipynb').read_text(encoding='utf-8'));code=[c for c in nb['cells'] if c['cell_type']=='code']
        assert ''.join(''.join(c['source']) for c in code)==src,(n,'Notebook source drift')
        output=''.join(''.join(o.get('text',[])) for c in code for o in c.get('outputs',[]) if o['output_type']=='stream')
        assert equivalent(json.loads(output),data),(n,'Notebook output drift')
        assert all(c['execution_count'] is not None for c in code)
        ids=[c['id'] for c in nb['cells']];assert len(ids)==len(set(ids))
    if execute:
        def run(n):
            env=dict(os.environ,PYTHONUTF8='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
            proc=subprocess.run([sys.executable,str(SITE/f'assets/lesson{n}-lab.py')],cwd=ROOT,env=env,check=True,capture_output=True,text=True,encoding='utf-8')
            assert equivalent(json.loads(proc.stdout),results[n]),(n,'Independent rerun differs')
            return n
        with ThreadPoolExecutor(max_workers=3) as pool:completed=list(pool.map(run,range(1,11)))
        assert len(completed)==10
    for path in SITE.rglob('*'):
        if path.is_file() and path.suffix in {'.html','.py','.json','.ipynb','.js','.css','.csv'}:
            txt=path.read_text(encoding='utf-8')
            assert not re.search(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}',txt)
            if path.suffix in {'.py','.ipynb'}:assert not re.search(r'read_(?:csv|excel)\s*\(\s*[\'\"]https?://|requests\.get|urlopen\(',txt)
    print(json.dumps(dict(pages=len(pages),case=SPEC['case'],shared_data_verified=True,original_slides_mapped=sum(SLIDE_COUNTS.values()),lesson_words=lengths,labs_rerun=10 if execute else 0),indent=2))

if __name__=='__main__':validate('--execute' in sys.argv)
