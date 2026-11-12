"""Verify the new teaching arithmetic, independent CSV reconstructions and practice artifacts."""
from pathlib import Path
import ast,contextlib,io,json,os,subprocess,sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
from course_practice import evidence,WORK

ROOT=Path(__file__).resolve().parents[1]; ASSETS=ROOT/'dist/assets'

def check(execute=False):
    from check_retail_release import equivalent
    # Independent algebra and hand-checkable examples, not just saved-output equality.
    assert np.isclose(evidence(1)['all_high'],100*72/190)
    assert np.isclose(evidence(2)['weighted'],.6*.1+.4*.3)
    assert evidence(3)['audit_n']==62 and evidence(3)['per_arm']==63
    assert np.allclose(evidence(4)['loss'],[34,14,24])
    assert np.allclose(evidence(7)['bounds'],[-14.6,5.4])
    assert evidence(8)['identified_from_W_alone']==[True,False]
    assert evidence(10)['unpaired_change']==3 and evidence(10)['paired_change']==-2
    # Recover the partial-regression result from published CSVs, using no shared case functions.
    s=pd.read_csv(ASSETS/'stores.csv');x=s.lead_days.to_numpy();y=s.baseline_rate.to_numpy()
    Z=np.column_stack([np.ones(len(s)),s.urban,s.baseline_demand-100,s.promotion_share,x*s.urban])
    residual_x=x-Z@np.linalg.lstsq(Z,x,rcond=None)[0]
    residual_y=y-Z@np.linalg.lstsq(Z,y,rcond=None)[0]
    assert np.isclose(residual_x@residual_y/(residual_x@residual_x),evidence(5)['partial'],atol=1e-7)
    # Independently rebuild the new score design from rounded public covariates.
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression
    v=s.query("cohort=='Voluntary'").sort_values('store_id').reset_index(drop=True)
    outcomes=pd.read_csv(ASSETS/'store-weeks.csv')
    assigned=outcomes.query("cohort=='Voluntary' and week==17").set_index('store_id').offer
    v['offer']=v.store_id.map(assigned); cols=['lead_days','urban','baseline_rate']
    prob=make_pipeline(StandardScaler(),LogisticRegression(C=1.,max_iter=1000)).fit(v[cols],v.offer).predict_proba(v[cols])[:,1]
    v['logit']=np.log(prob/(1-prob));caliper=.2*v.logit.std(ddof=1); pairs=[]
    for i,a in v[v.offer==1].iterrows():
        candidates=v[(v.offer==0)&(v.urban==a.urban)].copy()
        candidates['distance']=abs(candidates.logit-a.logit)
        nearest=candidates.distance.min()
        # Same documented near-tie tolerance; no reliance on row position.
        j=candidates[candidates.distance<=nearest+1e-8].sort_values('store_id').index[0]
        if candidates.loc[j,'distance']<=caliper:pairs.append((i,int(j)))
    kept=[i for i,j in pairs];used=[j for i,j in pairs]
    assert len(kept)==18 and len(set(used))==10
    means=outcomes.query("cohort=='Voluntary' and 17<=week<=24").groupby('store_id').stockout_rate.mean()
    gain=np.mean([means[v.loc[j,'store_id']]-means[v.loc[i,'store_id']] for i,j in pairs])
    assert np.isclose(gain,evidence(9)['matched'],atol=1e-7)
    notebooks={}
    for n in range(1,11):
        student=json.loads((ASSETS/f'lesson{n}-practice.ipynb').read_text(encoding='utf-8'))
        solution=json.loads((ASSETS/f'lesson{n}-practice-solutions.ipynb').read_text(encoding='utf-8'))
        reference=json.loads((ASSETS/f'lesson{n}-lab.ipynb').read_text(encoding='utf-8'))
        notebooks[n]=dict(student=len(student['cells']),solution=len(solution['cells']),reference=len(reference['cells']))
        assert len(student['cells'])>=13 and len(reference['cells'])>4
        for nb in [student,solution,reference]:
            assert len({c['id'] for c in nb['cells']})==len(nb['cells'])
            for cell in nb['cells']:
                if cell['cell_type']=='code':ast.parse(''.join(cell['source']))
        script=(ASSETS/f'lesson{n}-practice-solutions.py').read_text(encoding='utf-8')
        # Ignore an intentionally blank separator between the support and output stages.
        nb_code=''.join(''.join(c['source']) for c in solution['cells'] if c['cell_type']=='code')
        assert ast.dump(ast.parse(script))==ast.dump(ast.parse(nb_code))
        saved=json.loads((ASSETS/f'lesson{n}-practice-results.json').read_text(encoding='utf-8'))
        assert equivalent(saved,evidence(n))
    if execute:
        def run(n):
            env=dict(os.environ,PYTHONUTF8='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
            proc=subprocess.run([sys.executable,str(ASSETS/f'lesson{n}-practice-solutions.py')],env=env,check=True,capture_output=True,text=True,encoding='utf-8')
            assert equivalent(json.loads(proc.stdout),evidence(n)),n
            # Actually run notebook cells separately to catch boundary/dependency errors.
            for suffix in ['practice','practice-solutions']:
                scope={};captured=io.StringIO()
                nb=json.loads((ASSETS/f'lesson{n}-{suffix}.ipynb').read_text(encoding='utf-8'))
                for cell in nb['cells']:
                    if cell['cell_type']=='code':
                        with contextlib.redirect_stdout(captured):exec(compile(''.join(cell['source']),cell['id'],'exec'),scope)
                if suffix=='practice-solutions':assert equivalent(json.loads(captured.getvalue()),evidence(n))
            return n
        with ThreadPoolExecutor(max_workers=2) as pool:assert len(list(pool.map(run,range(1,11))))==10
    print(json.dumps(dict(bridges='passed',csv_reconstruction='passed',practice_scripts_rerun=10 if execute else 0,
                         practice_notebooks_executed=20 if execute else 0,notebook_cells=notebooks),indent=2))

if __name__=='__main__':check('--execute' in sys.argv)
