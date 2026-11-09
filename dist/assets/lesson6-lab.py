"""One reproducible retail world for all ten lessons. No external data required.

Units: 150 stores, 32 weeks, 140 scheduled product-days per store-week.
The three 50-store cohorts are disjoint. Pilot and voluntary adoption begin
in week 17; a separate later rollout begins in week 25. Baseline ends in 16.
All rates are percentages; a difference in rates is in percentage points.
"""
from functools import lru_cache
import hashlib
import json
import numpy as np
import pandas as pd
from scipy.stats import t
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor

SEED = 20261109
SPEC = dict(case='Retail stockouts and replenishment alerts', seed=SEED,
    stores=150, weeks=32, exposure=140, currency='CU',
    outcome='stockout product-days / 140 × 100',
    cost_per_stockout_day=6, weekly_alert_fee=12, weekly_extra_holding_cost=8,
    cost_definition='6 × stockout product-days + 20 when alerts are offered',
    cost_status='Management accounting scenario; no claim about recovered sales',
    decision='Reduce stockouts profitably; decide where to expand alerts',
    releases=[dict(name='Baseline',weeks='1–16',cohort='All 150 stores'),
      dict(name='Randomized pilot',weeks='17–24',cohort='S001–S050; 25 random offers'),
      dict(name='Voluntary adoption',weeks='17–24',cohort='S051–S100; selected by observed starting conditions'),
      dict(name='Later rollout',weeks='25–32',cohort='S101–S150; 25 selected adopters')])

def records(frame):
    return json.loads(frame.to_json(orient='records',double_precision=12))

def interval(values):
    a=np.asarray(values,float); n=len(a); mean=float(a.mean())
    sd=float(a.std(ddof=1)); se=sd/np.sqrt(n); critical=float(t.ppf(.975,n-1))
    return dict(n=n,mean=mean,sd=sd,se=se,critical=critical,low=mean-critical*se,high=mean+critical*se)

def difference(a,b):
    """Mean(a)-mean(b), independent store-level Welch interval."""
    a=np.asarray(a,float); b=np.asarray(b,float)
    va=a.var(ddof=1)/len(a); vb=b.var(ddof=1)/len(b); se=float(np.sqrt(va+vb))
    df=float((va+vb)**2/(va**2/(len(a)-1)+vb**2/(len(b)-1)))
    value=float(a.mean()-b.mean()); z=float(t.ppf(.975,df))
    return dict(value=value,se=se,df=df,low=value-z*se,high=value+z*se,n_a=len(a),n_b=len(b))

def fit_ols(X,y):
    X=np.asarray(X,float); y=np.asarray(y,float); b=np.linalg.lstsq(X,y,rcond=None)[0]
    residual=y-X@b; bread=np.linalg.pinv(X.T@X)
    covariance=(len(y)/(len(y)-X.shape[1]))*bread@(X.T@(residual[:,None]**2*X))@bread
    return b,covariance,residual

@lru_cache(maxsize=1)
def world():
    rng=np.random.default_rng(SEED)
    stores=pd.DataFrame(dict(store_id=[f'S{i:03d}' for i in range(1,151)],
        cohort=np.repeat(['Pilot','Voluntary','Rollout'],50),
        lead_days=rng.integers(2,6,150),urban=rng.binomial(1,.5,150)))
    stores['base_demand']=rng.normal(100,12,150)
    stores['store_effect']=rng.normal(0,.006,150)
    rows=[]
    for s in stores.itertuples(index=False):
        for week in range(1,33):
            promo=int(rng.random()<.22)
            forecast=s.base_demand+5*np.sin(week/3)+.15*week+8*promo
            demand=forecast+rng.normal(0,7)
            p0=.055+.014*s.lead_days+.0005*(demand-100)+.018*s.urban+.003*(s.lead_days-3)*s.urban+.02*promo+s.store_effect+.006*np.sin(week/4)
            tau=.006+.008*s.lead_days+.004*s.urban
            assert 0<p0-tau<p0<1
            draws=rng.random(140)
            y0=int((draws<p0).sum()); y1=int((draws<p0-tau).sum())
            rows.append(dict(store_id=s.store_id,cohort=s.cohort,week=week,lead_days=int(s.lead_days),urban=int(s.urban),
                demand_forecast=float(forecast),demand_index=float(demand),promotion_plan=promo,
                exposure=140,y0=y0,y1=y1,p0=float(p0),effect_pp=float(100*tau)))
    panel=pd.DataFrame(rows)
    baseline=panel.query('week<=8').groupby('store_id',sort=False).agg(
        baseline_rate=('y0',lambda x:100*x.mean()/140),baseline_demand=('demand_index','mean'),
        promotion_share=('promotion_plan','mean')).reset_index()
    stores=stores.merge(baseline,on='store_id',validate='one_to_one')
    stores['offer']=0
    pilot=stores.index[stores.cohort=='Pilot'].to_numpy()
    stores.loc[rng.choice(pilot,25,replace=False),'offer']=1
    voluntary=stores.cohort=='Voluntary'
    score=-.15+.65*(stores.lead_days-3.5)+.35*stores.urban+.15*(stores.baseline_rate-stores.baseline_rate.mean())
    propensity=1/(1+np.exp(-score))
    stores.loc[voluntary,'offer']=(rng.random(int(voluntary.sum()))<propensity[voluntary]).astype(int)
    rollout=stores[stores.cohort=='Rollout'].sort_values('baseline_rate').tail(25).index
    stores.loc[rollout,'offer']=1
    stores['risk_group']=np.where(stores.lead_days>=4,'Long lead (4–5 days)','Short lead (2–3 days)')
    panel=panel.merge(stores[['store_id','offer','baseline_rate','risk_group']],on='store_id',validate='many_to_one')
    panel['active']=((panel.offer==1)&(((panel.cohort!='Rollout')&(panel.week>=17))|((panel.cohort=='Rollout')&(panel.week>=25)))).astype(int)
    panel['stockout_days']=np.where(panel.active==1,panel.y1,panel.y0)
    panel['stockout_rate']=100*panel.stockout_days/panel.exposure
    panel['operating_cost']=6*panel.stockout_days+20*panel.active
    panel['lag_rate']=panel.groupby('store_id').stockout_rate.shift(1)
    # Defects in the initial export are reconciled against a transaction ledger.
    clean=panel.query('week<=8')[['store_id','week','exposure','stockout_days']].reset_index(drop=True)
    raw=clean.copy(); bad=rng.choice(len(raw),12,replace=False)
    repairs=clean.iloc[bad].copy(); repairs['reason']=['Missing count']*8+['Negative count']*4
    raw.loc[bad[:8],'stockout_days']=np.nan; raw.loc[bad[8:],'stockout_days']=-1
    raw=pd.concat([raw,raw.iloc[rng.choice(len(raw),12,replace=False)]],ignore_index=True)
    audit_source=panel.query('week==16').copy()
    chosen=rng.choice(len(audit_source),30,replace=False)
    audit=audit_source.iloc[chosen][['store_id','exposure','p0']].copy()
    audit['stockout_days']=rng.binomial(140,audit.p0.to_numpy())
    audit['stockout_rate']=100*audit.stockout_days/140
    public_cols=['store_id','cohort','week','lead_days','urban','demand_forecast','demand_index','promotion_plan','exposure','stockout_days','stockout_rate','operating_cost','lag_rate','offer','active']
    public=panel[public_cols]
    fingerprint=hashlib.sha256(public.to_csv(index=False,float_format='%.8f',lineterminator='\n').encode()).hexdigest()
    return dict(stores=stores,panel=panel,public=public,raw=raw,repairs=repairs,clean=clean,audit=audit,
        audit_truth=float(100*audit_source.p0.mean()),fingerprint=fingerprint)

def voluntary_design(frame,D):
    lead=frame.lead_days.to_numpy()-3.5; urban=frame.urban.to_numpy(); d=np.asarray(D)
    return np.column_stack([np.ones(len(frame)),d,lead,urban,frame.baseline_rate.to_numpy(),d*lead,d*urban])

@lru_cache(maxsize=1)
def all_results():
    w=world(); p=w['panel']; stores=w['stores']; out={}
    raw=w['raw']; dedup=raw.drop_duplicates(['store_id','week']); flagged=dedup.stockout_days.isna()|(dedup.stockout_days<0)
    fixed=dedup.merge(w['repairs'][['store_id','week','stockout_days']],on=['store_id','week'],how='left',suffixes=('','_ledger'),validate='one_to_one')
    fixed.loc[fixed.stockout_days.isna()|(fixed.stockout_days<0),'stockout_days']=fixed.stockout_days_ledger
    fixed=fixed.sort_values(['store_id','week'])
    assert np.array_equal(fixed.stockout_days.to_numpy(),w['clean'].sort_values(['store_id','week']).stockout_days.to_numpy())
    example=fixed.iloc[0]
    out[1]=dict(raw=len(raw),deduplicated=len(dedup),duplicates=len(raw)-len(dedup),flagged=int(flagged.sum()),clean=len(fixed),
        sample=records(fixed[['store_id','week','exposure','stockout_days']].head(5)),repairs=records(w['repairs'].head(5)),
        total_stockouts=int(fixed.stockout_days.sum()),total_exposure=int(fixed.exposure.sum()),rate=float(100*fixed.stockout_days.sum()/fixed.exposure.sum()),
        worked=dict(store=example.store_id,week=int(example.week),count=int(example.stockout_days),exposure=int(example.exposure),rate=float(100*example.stockout_days/example.exposure)))
    b=stores.copy(); groups=[]
    for label,g in b.groupby('risk_group',sort=True):
        groups.append(dict(group=label,n=len(g),mean=float(g.baseline_rate.mean()),median=float(g.baseline_rate.median()),above=int((g.baseline_rate>10).sum()),share=float((g.baseline_rate>10).mean())))
    out[2]=dict(n=len(b),mean=float(b.baseline_rate.mean()),median=float(b.baseline_rate.median()),q1=float(b.baseline_rate.quantile(.25)),q3=float(b.baseline_rate.quantile(.75)),groups=groups,
        top=records(b.nlargest(5,'baseline_rate')[['store_id','lead_days','urban','baseline_rate']]),weekly=records(p.query('week<=8').groupby('week').stockout_rate.mean().reset_index()))
    out[3]=dict(**interval(w['audit'].stockout_rate),target=10,exposure=140,
        sample=records(w['audit'][['store_id','stockout_days','exposure','stockout_rate']].head(6)),truth=w['audit_truth'])
    X=np.column_stack([np.ones(len(b)),b.lead_days]); coef,cov,res=fit_ols(X,b.baseline_rate)
    out[4]=dict(n=len(b),intercept=float(coef[0]),slope=float(coef[1]),rmse=float(np.sqrt(np.mean(res**2))),
        sample=records(b[['store_id','lead_days','baseline_rate']].head(5).assign(prediction=(X@coef)[:5],residual=res[:5])),
        group_means=records(b.groupby('lead_days').baseline_rate.mean().reset_index()),predictions=[dict(lead=x,rate=float(coef[0]+coef[1]*x)) for x in range(2,6)])
    X5=np.column_stack([np.ones(len(b)),b.lead_days,b.urban,b.baseline_demand-100,b.promotion_share,b.lead_days*b.urban])
    coef5,cov5,res5=fit_ols(X5,b.baseline_rate)
    profiles=[]
    for urban in (0,1):
        for lead in (2,4,5):
            row=np.array([1,lead,urban,0,.25,lead*urban]); profiles.append(dict(urban=urban,lead=lead,demand=100,promotion_share=.25,predicted=float(row@coef5)))
    out[5]=dict(n=len(b),coefficients=dict(zip(['Intercept','Lead days','Urban','Demand above 100','Promotion share','Lead × urban'],map(float,coef5))),
        profiles=profiles,short_slope=float(coef[1]),rural_slope=float(coef5[1]),urban_slope=float(coef5[1]+coef5[5]),rmse=float(np.sqrt(np.mean(res5**2))))
    features=['lag_rate','lead_days','urban','demand_forecast','promotion_plan']
    forecast=p.query('3<=week<=16').copy(); train=forecast.query('week<=10'); val=forecast.query('11<=week<=13'); test=forecast.query('week>=14')
    candidates={'Linear regression':LinearRegression(),'Small tree':DecisionTreeRegressor(max_depth=3,min_samples_leaf=30,random_state=SEED)}
    scores=[]
    for name,model in candidates.items():
        model.fit(train[features],train.stockout_rate); pred=model.predict(val[features]); scores.append(dict(model=name,rmse=float(np.sqrt(np.mean((val.stockout_rate-pred)**2)))))
    choice=min(scores,key=lambda z:z['rmse'])['model']; model=candidates[choice]; dev=forecast.query('week<=13'); model.fit(dev[features],dev.stockout_rate)
    predicted=model.predict(test[features]); baseline=float(dev.stockout_rate.mean()); errors=test.stockout_rate.to_numpy()-predicted
    ex=test[['store_id','week','stockout_rate']].copy();ex['prediction']=predicted;ex['error']=errors;ex['squared_error']=errors**2
    watch=ex.query('week==16').nlargest(5,'prediction')
    out[6]=dict(features=features,train_n=len(train),validation_n=len(val),test_n=len(test),scores=scores,selected=choice,
        baseline=baseline,baseline_rmse=float(np.sqrt(np.mean((test.stockout_rate-baseline)**2))),rmse=float(np.sqrt(np.mean(errors**2))),mae=float(np.mean(np.abs(errors))),
        sample=records(ex.head(5)),watchlist=records(watch),windows=dict(training=[3,10],validation=[11,13],test=[14,16]))
    post=p.query('17<=week<=24').groupby(['store_id','cohort','offer']).agg(rate=('stockout_rate','mean'),cost=('operating_cost','mean'),
        truth_effect=('effect_pp','mean'),realized_effect=('y0',lambda x:0)).reset_index()
    post=post.drop(columns='realized_effect').merge(stores[['store_id','lead_days','urban','baseline_rate','risk_group']],on='store_id',validate='one_to_one')
    pilot=post.query("cohort=='Pilot'"); treated=pilot[pilot.offer==1];control=pilot[pilot.offer==0]
    trial=difference(control.rate,treated.rate); savings=difference(control.cost,treated.cost)
    out[7]=dict(n=len(pilot),offered=len(treated),control=len(control),offered_mean=float(treated.rate.mean()),control_mean=float(control.rate.mean()),effect=trial,savings=savings,
        cost_threshold=100*20/(6*140),truth=float(pilot.truth_effect.mean()),
        sample=records(pilot[['store_id','offer','baseline_rate','rate','cost']].head(6)),
        groups=[dict(group='Usual operations',n=len(control),rate=float(control.rate.mean()),cost=float(control.cost.mean())),dict(group='Alert offer',n=len(treated),rate=float(treated.rate.mean()),cost=float(treated.cost.mean()))])
    v=post.query("cohort=='Voluntary'").reset_index(drop=True); strata=[]
    for name,g in v.groupby('risk_group',sort=True):
        ct=g[g.offer==0];tr=g[g.offer==1];assert len(ct)>0 and len(tr)>0
        gap=float(ct.rate.mean()-tr.rate.mean());strata.append(dict(group=name,n=len(g),offered=len(tr),control=len(ct),usual=float(ct.rate.mean()),alerts=float(tr.rate.mean()),reduction=gap,weight=len(g)/len(v),contribution=gap*len(g)/len(v)))
    raw_gap=float(v[v.offer==0].rate.mean()-v[v.offer==1].rate.mean())
    out[8]=dict(n=len(v),raw_reduction=raw_gap,strata=strata,standardized=float(sum(s['contribution'] for s in strata)),
        balance=[dict(variable=k,adopters=float(v[v.offer==1][k].mean()),comparison=float(v[v.offer==0][k].mean())) for k in ['lead_days','urban','baseline_rate']])
    D=v.offer.to_numpy();Xv=voluntary_design(v,D);beta,covv,rv=fit_ols(Xv,v.rate)
    X0=voluntary_design(v,np.zeros(len(v)));X1=voluntary_design(v,np.ones(len(v)));pred0=X0@beta;pred1=X1@beta;effects=pred0-pred1
    contrast=(X0-X1).mean(axis=0);se=float(np.sqrt(contrast@covv@contrast));estimate=float(effects.mean())
    ctr=v[v.offer==0]; tr=v[v.offer==1];scale=v[['lead_days','urban','baseline_rate']].std(ddof=0).to_numpy()
    distances=((tr[['lead_days','urban','baseline_rate']].to_numpy()[:,None,:]-ctr[['lead_days','urban','baseline_rate']].to_numpy()[None,:,:])/scale)**2
    nearest=np.argmin(distances.sum(axis=2),axis=1)
    matches=[dict(adopter=a.store_id,comparison=ctr.iloc[j].store_id,adopter_rate=float(a.rate),comparison_rate=float(ctr.iloc[j].rate),reduction=float(ctr.iloc[j].rate-a.rate)) for a,j in zip(tr.itertuples(),nearest)]
    vs=v[['store_id','lead_days','urban','baseline_rate','offer']].copy();vs['usual_prediction']=pred0;vs['alert_prediction']=pred1;vs['reduction']=effects
    out[9]=dict(n=len(v),raw_reduction=raw_gap,estimate=estimate,se=se,low=estimate-1.96*se,high=estimate+1.96*se,
        att=float(effects[D==1].mean()),matching_att=float(np.mean([m['reduction'] for m in matches])),matches=matches[:5],sample=records(vs.head(5)),
        predicted_usual=float(pred0.mean()),predicted_alert=float(pred1.mean()),truth=float(v.truth_effect.mean()),truth_att=float(v[v.offer==1].truth_effect.mean()),
        coefficients=list(map(float,beta)),coefficient_names=['Intercept','Offer','Lead minus 3.5','Urban','Baseline rate','Offer × centered lead','Offer × urban'])
    roll=p.query("cohort=='Rollout'").copy(); pre=roll.query('17<=week<=24').groupby(['store_id','offer']).agg(pre=('stockout_rate','mean'),pre_cost=('operating_cost','mean')).reset_index()
    after=roll.query('25<=week<=32').groupby('store_id').agg(post=('stockout_rate','mean'),post_cost=('operating_cost','mean'),truth_effect=('effect_pp','mean')).reset_index()
    rd=pre.merge(after,on='store_id',validate='one_to_one');rd['change']=rd.post-rd.pre;rd['cost_change']=rd.post_cost-rd.pre_cost
    a=rd[rd.offer==1];c=rd[rd.offer==0];did=difference(c.change,a.change);costdid=difference(c.cost_change,a.cost_change)
    out[10]=dict(n=len(rd),adopters=len(a),comparison=len(c),effect=did,savings=costdid,
        adopter_pre=float(a.pre.mean()),adopter_post=float(a.post.mean()),comparison_pre=float(c.pre.mean()),comparison_post=float(c.post.mean()),
        adopter_change=float(a.change.mean()),comparison_change=float(c.change.mean()),counterfactual=float(a.pre.mean()+c.change.mean()),truth=float(a.truth_effect.mean()),
        sample=records(rd.head(5)),weekly=[dict(week=int(week),usual=float(g[g.offer==0].stockout_rate.mean()),adopters=float(g[g.offer==1].stockout_rate.mean())) for week,g in roll.groupby('week')])
    for number,result in out.items():
        result.update(lesson=number,seed=SEED,case=SPEC['case'],data_fingerprint=w['fingerprint'])
    return out

def lesson_result(number):
    return all_results()[int(number)]

data = world()['panel'].query('3 <= week <= 16')
features = ['lag_rate','lead_days','urban','demand_forecast','promotion_plan']
train = data.query('week <= 10')
valid = data.query('11 <= week <= 13')
test = data.query('week >= 14')
models = {'Linear regression': LinearRegression(),
          'Small tree': DecisionTreeRegressor(max_depth=3,min_samples_leaf=30,random_state=SEED)}
scores = {}
for name, model in models.items():
    model.fit(train[features], train.stockout_rate)
    scores[name] = np.sqrt(np.mean((valid.stockout_rate-model.predict(valid[features]))**2))
chosen = min(scores, key=scores.get)
development = data.query('week <= 13')
model = models[chosen].fit(development[features], development.stockout_rate)
worked_rmse = np.sqrt(np.mean((test.stockout_rate-model.predict(test[features]))**2))
assert np.isclose(worked_rmse, lesson_result(6)['rmse'])
print(json.dumps(lesson_result(6), indent=2, allow_nan=False))
