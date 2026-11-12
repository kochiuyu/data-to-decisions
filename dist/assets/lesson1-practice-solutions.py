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
from scipy.stats import t, norm, skew, kurtosis, binomtest, gaussian_kde
from sklearn.linear_model import LinearRegression, Lasso, LogisticRegression
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import make_pipeline
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

def nearest_score_match(controls,target):
    """Nearest logit; distances within 1e-8 tie by ID, stable to CSV rounding."""
    distance=(controls.logit-target).abs()
    tied=controls.loc[np.isclose(distance,distance.min(),rtol=0,atol=1e-8)]
    return tied.sort_values('store_id').index[0]

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
def preparation_examples():
    """Small worked extracts and explicitly illustrative operational ledgers."""
    w=world(); clean=w['clean'].copy(); stores=w['stores']
    long=clean.query("store_id in ['S001','S002'] and week<=2").copy()
    wide=long.set_index(['store_id','week'])[['stockout_days','exposure']].unstack('week')
    wide.columns=[f'{variable}_{week}' for variable,week in wide.columns]
    joined=clean.merge(stores[['store_id','lead_days','urban']],on='store_id',how='left',validate='many_to_one',indicator=True)
    assert len(joined)==len(clean) and joined['_merge'].eq('both').all()
    # Supplemental staffing and transfer ledgers illustrate relationships only;
    # they never alter stockout outcomes or any intervention study.
    assignments=pd.DataFrame([
        ['S001','M01',1,4],['S001','M02',5,8],['S002','M03',1,8]],
        columns=['store_id','manager_id','start_week','end_week'])
    weekly=clean.query("store_id in ['S001','S002']")
    candidates=weekly.merge(assignments,on='store_id',validate='many_to_many')
    responsible=candidates[candidates.week.between(candidates.start_week,candidates.end_week)].copy()
    assert len(responsible)==len(weekly) and not responsible.duplicated(['store_id','week']).any()
    transfers=pd.DataFrame([
        ['T001',2,'S001','S002',6],['T002',3,'S002','S003',4]],
        columns=['transfer_id','week','from_store','to_store','units'])
    outgoing=transfers[['transfer_id','week','from_store','units']].rename(columns={'from_store':'store_id'}).assign(direction='Out',signed_units=lambda x:-x.units)
    incoming=transfers[['transfer_id','week','to_store','units']].rename(columns={'to_store':'store_id'}).assign(direction='In',signed_units=lambda x:x.units)
    perspectives=pd.concat([outgoing,incoming],ignore_index=True).sort_values(['transfer_id','direction'])
    assert len(perspectives)==4 and perspectives.signed_units.sum()==0
    # An incomplete submission extract demonstrates an explicit eligibility rule.
    reports=clean.query("store_id in ['S001','S002','S003','S004','S005','S006']").copy()
    reports=reports[~((reports.store_id.eq('S001')&(reports.week>1))|(reports.store_id.eq('S002')&(reports.week>2)))]
    summary=reports.groupby('store_id').agg(weeks=('week','size'),stockouts=('stockout_days','sum'),exposure=('exposure','sum'))
    summary['rate']=100*summary.stockouts/summary.exposure
    summary=summary.sort_values('rate').reset_index()
    return dict(long=records(long),wide=records(wide.reset_index()),wide_columns=list(wide.columns),
        joined=records(joined.drop(columns='_merge').head(5)),joined_rows=len(joined),
        store_counts=records(stores.groupby('cohort').size().rename('stores').reset_index()),
        assignments=records(assignments),assignment_candidates=len(candidates),assignment_rows=len(responsible),
        assigned_sample=records(responsible.query("store_id=='S001' and 3<=week<=6")[['store_id','week','manager_id','stockout_days']]),
        transfers=records(transfers),perspectives=records(perspectives[['transfer_id','week','store_id','direction','signed_units']]),
        reports=records(reports),summary=records(summary),eligible=records(summary.query('weeks>=6')))


FORECAST_FEATURES = ['lag_rate','lead_days','urban','demand_forecast','promotion_plan']
FORECAST_FOLDS = [(7,8,9),(9,10,11),(11,12,13)]

def forecast_basis(values):
    """Five main terms, three continuous squares, ten pairwise products."""
    polynomial = PolynomialFeatures(2, include_bias=False)
    matrix = polynomial.fit_transform(np.asarray(values))
    keep = (polynomial.powers_[:,2] < 2) & (polynomial.powers_[:,4] < 2)
    return matrix[:,keep]

def forecast_feature_names():
    polynomial = PolynomialFeatures(2, include_bias=False).fit(np.zeros((1,5)))
    keep = (polynomial.powers_[:,2] < 2) & (polynomial.powers_[:,4] < 2)
    return polynomial.get_feature_names_out(FORECAST_FEATURES)[keep]

def fit_forecast(training, kind, alpha=.01):
    """Learn the entire procedure on this training window only."""
    assert kind in ['Mean','Linear regression','Quadratic','Log-linear','LASSO']
    from sklearn.preprocessing import FunctionTransformer
    from sklearn.dummy import DummyRegressor
    target = training.stockout_rate.to_numpy()
    if kind == 'Mean':
        model = DummyRegressor(strategy='mean')
    elif kind in ['Quadratic','LASSO']:
        estimator = Lasso(alpha=alpha,max_iter=50000,tol=1e-8) if kind=='LASSO' else LinearRegression()
        model = make_pipeline(FunctionTransformer(forecast_basis),StandardScaler(),estimator)
    else:
        model = make_pipeline(StandardScaler(),LinearRegression())
    outcome = np.log1p(target) if kind == 'Log-linear' else target
    model.fit(training[FORECAST_FEATURES],outcome)
    smear = float(np.mean(np.exp(outcome-model.predict(training[FORECAST_FEATURES])))) if kind=='Log-linear' else 1.
    return model,kind,smear

def predict_forecast(fitted, rows):
    model,kind,smear = fitted
    predicted = model.predict(rows[FORECAST_FEATURES])
    return np.exp(predicted)*smear-1 if kind=='Log-linear' else predicted

@lru_cache(maxsize=1)
def prediction_analysis():
    data = world()['panel'].query('3<=week<=16').copy()
    development = data.query('week<=13'); final = data.query('week>=14')
    def validate(kind,alpha=.01):
        errors=[]; train_errors=[]; fold_scores=[]
        for end,start,stop in FORECAST_FOLDS:
            training=development[development.week<=end]
            validation=development[development.week.between(start,stop)]
            fitted=fit_forecast(training,kind,alpha)
            error=validation.stockout_rate.to_numpy()-predict_forecast(fitted,validation)
            train_error=training.stockout_rate.to_numpy()-predict_forecast(fitted,training)
            errors.extend(error);train_errors.extend(train_error)
            fold_scores.append(float(np.sqrt(np.mean(error**2))))
        return dict(rmse=float(np.sqrt(np.mean(np.square(errors)))),fold_rmse=fold_scores,
                    training_rmse=float(np.sqrt(np.mean(np.square(train_errors)))))
    tuning=[dict(alpha=a,**validate('LASSO',a)) for a in [.001,.01,.1,1.]]
    best=min(tuning,key=lambda x:x['rmse'])['alpha']
    scores=[dict(model=kind,**validate(kind)) for kind in ['Mean','Linear regression','Quadratic','Log-linear']]
    scores.append(dict(model='LASSO',**validate('LASSO',best)))
    selected=min(scores,key=lambda x:x['rmse'])['model']
    fitted=fit_forecast(development,selected,best)
    prediction=predict_forecast(fitted,final);errors=final.stockout_rate.to_numpy()-prediction
    baseline=float(development.stockout_rate.mean())
    ex=final[['store_id','week','stockout_rate']+FORECAST_FEATURES].copy()
    ex['prediction']=prediction;ex['error']=errors;ex['squared_error']=errors**2
    core=dict(features=FORECAST_FEATURES,train_n=len(development.query('week<=7')),validation_n=len(development.query('week>=8')),test_n=len(final),
      scores=scores,selected=selected,baseline=baseline,
      baseline_rmse=float(np.sqrt(np.mean((final.stockout_rate-baseline)**2))),
      rmse=float(np.sqrt(np.mean(errors**2))),mae=float(np.mean(abs(errors))),
      sample=records(ex.head(5)),watchlist=records(ex.query('week==16').nlargest(5,'prediction')),
      windows=dict(training=[3,7],validation=[8,13],test=[14,16]))
    tuned=fit_forecast(development,'LASSO',best);lp=predict_forecast(tuned,final)
    names=forecast_feature_names();coef=tuned[0][-1].coef_
    terms=sorted([dict(feature=str(name),coefficient=float(v)) for name,v in zip(names,coef) if abs(v)>1e-8],key=lambda x:abs(x['coefficient']),reverse=True)
    criteria=[]
    for degree,kind in [(1,'Linear regression'),(2,'Quadratic')]:
        fit=fit_forecast(development,kind);residual=development.stockout_rate-predict_forecast(fit,development)
        design=development[FORECAST_FEATURES].to_numpy() if degree==1 else forecast_basis(development[FORECAST_FEATURES])
        rank=int(np.linalg.matrix_rank(np.column_stack([np.ones(len(design)),design])))
        assert rank==design.shape[1]+1
        rss=float(np.sum(residual**2));nn=len(development);k=rank+1
        negative2log=nn*(np.log(2*np.pi)+1+np.log(rss/nn))
        criteria.append(dict(degree=degree,parameters=k,mean_parameters=rank,training_rmse=float(np.sqrt(rss/nn)),
                             rss=rss,negative2log=negative2log,aic=negative2log+2*k,bic=negative2log+k*np.log(nn)))
    depth=dict(folds=[dict(train_end=a,validation_start=b,validation_end=c) for a,b,c in FORECAST_FOLDS],
      tuning=tuning,alpha=best,retained=len(terms),candidate_features=len(names),largest=terms[:6],terms=terms,
      test_rmse=float(np.sqrt(np.mean((final.stockout_rate-lp)**2))),test_mae=float(np.mean(abs(final.stockout_rate-lp))),
      criteria=criteria,
      log_example=dict(naive=10.,smearing=float(np.mean(np.exp([-.2,.2]))),mean=float(10*np.mean(np.exp([-.2,.2])))))
    return core,depth

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
        worked=dict(store=example.store_id,week=int(example.week),count=int(example.stockout_days),exposure=int(example.exposure),rate=float(100*example.stockout_days/example.exposure)),preparation=preparation_examples())
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
    out[6]=dict(prediction_analysis()[0])
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
    expanded=expanded_results(w,out)
    for number,result in out.items():
        result['depth']=expanded.get(number,{})
        result.update(lesson=number,seed=SEED,case=SPEC['case'],data_fingerprint=w['fingerprint'])
    return out

def lesson_result(number):
    return all_results()[int(number)]

def expanded_results(w,core):
    """Worked teaching material restored from the original ten-slide curriculum.

    All case estimates use the same records. Auxiliary resampling, design
    demonstrations and model tuning have separate, fixed random streams.
    """
    s=w['stores']; p=w['panel']; out={}; y=s.baseline_rate.to_numpy(); n=len(s)
    # Lesson 2: distribution, visualization, association and composition.
    hist=[]
    for width in (2,4):
        edges=np.arange(0,32+width,width); counts,_=np.histogram(y,bins=edges)
        hist.append(dict(width=width,bins=[dict(low=float(a),high=float(b),count=int(c)) for a,b,c in zip(edges[:-1],edges[1:],counts)]))
    q1,q3=np.quantile(y,[.25,.75]); iqr=q3-q1
    composition=[]
    for name,g in s.groupby('risk_group'):
        counts=[int((g.baseline_rate<=10).sum()),int(g.baseline_rate.between(10,15,inclusive='right').sum()),int((g.baseline_rate>15).sum())]
        composition.append(dict(group=name,n=len(g),counts=counts,percent=[100*c/len(g) for c in counts]))
    bs=s.assign(bin=pd.qcut(s.baseline_demand,5,duplicates='drop')).groupby('bin',observed=True).agg(demand=('baseline_demand','mean'),rate=('baseline_rate','mean'),n=('store_id','size'))
    density_x=np.linspace(0,30,61);density_y=gaussian_kde(y)(density_x)
    out[2]=dict(density=[dict(rate=float(x),density=float(v)) for x,v in zip(density_x,density_y)],sd=float(np.std(y,ddof=1)),variance=float(np.var(y,ddof=1)),minimum=float(min(y)),maximum=float(max(y)),iqr=float(iqr),
        skewness=float(skew(y,bias=False)),excess_kurtosis=float(kurtosis(y,bias=False)),histograms=hist,composition=composition,
        low_fence=float(q1-1.5*iqr),high_fence=float(q3+1.5*iqr),outliers=int(((y<q1-1.5*iqr)|(y>q3+1.5*iqr)).sum()),
        covariance=float(np.cov(s.baseline_demand,y,ddof=1)[0,1]),correlation=float(np.corrcoef(s.baseline_demand,y)[0,1]),bins=records(bs.reset_index(drop=True)))
    # Lesson 3: sampling variation, proportions, resampling, and three t tests.
    audit=w['audit']; a=audit.stockout_rate.to_numpy(); an=len(a); rng=np.random.default_rng(SEED+303)
    boot=a[rng.integers(0,an,size=(2000,an))].mean(axis=1)
    sub=np.array([rng.choice(a,15,replace=False).mean() for _ in range(2000)])
    se=np.std(a,ddof=1)/np.sqrt(an); statistic=(a.mean()-10)/se
    successes=int((a>10).sum()); prop=binomtest(successes,an).proportion_ci(method='wilson')
    paired=audit[['store_id','stockout_rate']].merge(p.query('week==16')[['store_id','stockout_rate','urban']],on='store_id',suffixes=('_audit','_system'),validate='one_to_one')
    d=paired.stockout_rate_audit-paired.stockout_rate_system; pair=interval(d)
    pair.update(statistic=float(pair['mean']/pair['se']),p=float(2*t.sf(abs(pair['mean']/pair['se']),an-1)))
    independent=difference(paired[paired.urban==1].stockout_rate_audit,paired[paired.urban==0].stockout_rate_audit)
    independent['p']=float(2*t.sf(abs(independent['value']/independent['se']),independent['df']))
    out[3]=dict(bootstrap_se=float(boot.std(ddof=1)),bootstrap_low=float(np.quantile(boot,.025)),bootstrap_high=float(np.quantile(boot,.975)),subsample_size=15,subsample_sd=float(sub.std(ddof=1)),
        t_statistic=float(statistic),p_one_sided=float(t.sf(statistic,an-1)),p_two_sided=float(2*t.sf(abs(statistic),an-1)),
        proportion=dict(successes=successes,n=an,value=successes/an,low=float(prop.low),high=float(prop.high)),paired=pair,independent=independent,
        paired_rows=records(paired.head(5)),bootstrap_repetitions=2000)
    # Lesson 4: the OLS decomposition, transformations and flexible forms.
    x=s.lead_days.to_numpy(); X=np.column_stack([np.ones(n),x]); b,vc,res=fit_ols(X,y); fitted=X@b
    sst=float(((y-y.mean())**2).sum()); sse=float((res**2).sum()); ssr=float(((fitted-y.mean())**2).sum())
    forms=[]
    for name,xx,yy,log_y in [('Level–level',x,y,False),('Log–level',x,np.log(y),True),('Level–log',np.log(x),y,False),('Log–log',np.log(x),np.log(y),True)]:
        design=np.column_stack([np.ones(n),xx]); beta,_,err=fit_ols(design,yy); smearing=float(np.mean(np.exp(err))) if log_y else 1.
        pred=np.exp(design@beta)*smearing if log_y else design@beta
        forms.append(dict(model=name,intercept=float(beta[0]),slope=float(beta[1]),smearing=smearing,rmse_original=float(np.sqrt(np.mean((y-pred)**2)))))
    nonlinear=[]
    for degree in [1,2,3]:
        design=np.column_stack([x**k for k in range(degree+1)]); beta,_,err=fit_ols(design,y)
        nonlinear.append(dict(model=['','Linear','Quadratic','Cubic'][degree],parameters=degree+1,rmse=float(np.sqrt(np.mean(err**2))),coefficients=list(map(float,beta))))
    design=np.column_stack([np.ones(n),x,np.maximum(x-3.5,0)]); beta,_,err=fit_ols(design,y)
    nonlinear.append(dict(model='Spline, knot 3.5',parameters=3,rmse=float(np.sqrt(np.mean(err**2))),coefficients=list(map(float,beta))))
    # A local linear smoother on a continuous store characteristic.
    dx=s.baseline_demand.to_numpy(); grid=np.linspace(dx.min(),dx.max(),7); local=[]
    for point in grid:
        dist=abs(dx-point); bandwidth=np.partition(dist,int(.6*n))[int(.6*n)]; weights=np.maximum(1-(dist/bandwidth)**3,0)**3
        design=np.column_stack([np.ones(n),dx-point]); fit=np.linalg.lstsq(design*np.sqrt(weights[:,None]),y*np.sqrt(weights),rcond=None)[0]
        local.append(dict(demand=float(point),rate=float(fit[0])))
    out[4]=dict(sst=sst,sse=sse,ssr=ssr,r_squared=1-sse/sst,mse=sse/n,rmse=np.sqrt(sse/n),slope_covariance=float(np.cov(x,y,ddof=1)[0,1]/np.var(x,ddof=1)),forms=forms,nonlinear=nonlinear,local=local)
    # Lesson 5: regression uncertainty, omitted-variable identity, residual use.
    X5=np.column_stack([np.ones(n),x,s.urban,s.baseline_demand-100,s.promotion_share,x*s.urban]); b5,v5,e5=fit_ols(X5,y)
    coefficients=[]
    for name,value,standard in zip(core[5]['coefficients'],b5,np.sqrt(np.diag(v5))):
        coefficients.append(dict(term=name,value=float(value),se=float(standard),low=float(value-1.96*standard),high=float(value+1.96*standard),p=float(2*norm.sf(abs(value/standard)))))
    Xfull=np.column_stack([np.ones(n),x,s.urban]); bf,_,_=fit_ols(Xfull,y); aux,_,_=fit_ols(X,s.urban)
    sigma2=sse/(n-2); bread=np.linalg.inv(X.T@X); intervals=[]
    for val in [2,3.5,5]:
        row=np.array([1,val]); mu=float(row@b); mean_se=float(np.sqrt(sigma2*(row@bread@row))); pred_se=float(np.sqrt(sigma2+mean_se**2)); crit=t.ppf(.975,n-2)
        intervals.append(dict(lead=val,mean=mu,mean_low=mu-crit*mean_se,mean_high=mu+crit*mean_se,prediction_low=mu-crit*pred_se,prediction_high=mu+crit*pred_se))
    residuals=s[['store_id','baseline_rate']].assign(predicted=X5@b5,residual=e5).nlargest(5,'residual')
    out[5]=dict(coefficients=coefficients,intervals=intervals,ovb=dict(short=float(b[1]),long=float(bf[1]),omitted_effect=float(bf[2]),sorting=float(aux[1]),product=float(bf[2]*aux[1])),
        residuals=records(residuals),r_squared=float(1-np.sum(e5**2)/sst),adjusted_r_squared=float(1-(np.sum(e5**2)/(n-X5.shape[1]))/(sst/(n-1))))
    # Lesson 6 uses one chronological comparison for all candidate procedures.
    out[6]=dict(prediction_analysis()[1])
    # Lesson 7: reveal both potential paths only in a known-answer exercise.
    pilot=p.query("cohort=='Pilot' and 17<=week<=24").groupby(['store_id','offer']).agg(y0=('y0','mean'),y1=('y1','mean')).reset_index()
    pilot['y0']=100*pilot.y0/140;pilot['y1']=100*pilot.y1/140;pilot['reduction']=pilot.y0-pilot.y1
    tr=pilot.offer==1; ate=float(pilot.reduction.mean());att=float(pilot.loc[tr,'reduction'].mean());atu=float(pilot.loc[~tr,'reduction'].mean())
    bias=float(pilot.loc[~tr,'y0'].mean()-pilot.loc[tr,'y0'].mean())
    ps=s.query("cohort=='Pilot'"); balance=[]
    for var in ['lead_days','urban','baseline_rate']:
        balance.append(dict(variable=var,offered=float(ps[ps.offer==1][var].mean()),usual=float(ps[ps.offer==0][var].mean())))
    out[7]=dict(potential_rows=records(pilot.head(6)),ate=ate,att=att,atu=atu,treated_share=float(tr.mean()),selection_component=bias,balance=balance)
    # Lesson 8: use population-specific stratum weights on the same comparisons.
    strata=core[8]['strata']; nt=sum(g['offered'] for g in strata); nc=sum(g['control'] for g in strata)
    weights=[dict(group=g['group'],reduction=g['reduction'],ate_weight=g['n']/50,att_weight=g['offered']/nt,atu_weight=g['control']/nc) for g in strata]
    rng=np.random.default_rng(SEED+808); simulations=[]; count=3000
    # Separate mechanism experiments for the DAG appendix, not extra field records.
    offer=rng.binomial(1,.5,count); mediator=1.5*offer+rng.normal(size=count); outcome=20-2*mediator+rng.normal(size=count)
    naive,_,_=fit_ols(np.column_stack([np.ones(count),offer]),outcome)
    adjusted,_,_=fit_ols(np.column_stack([np.ones(count),offer,mediator]),outcome)
    simulations.append(dict(mechanism='Chain',control='Post-offer review effort',total_reduction=3.,naive=float(-naive[1]),adjusted=float(-adjusted[1])))
    common=rng.normal(size=count);offer=(.8*common+rng.normal(size=count)>0).astype(int);outcome=12+2*common-3*offer+rng.normal(size=count)
    naive,_,_=fit_ols(np.column_stack([np.ones(count),offer]),outcome)
    adjusted,_,_=fit_ols(np.column_stack([np.ones(count),offer,common]),outcome)
    simulations.append(dict(mechanism='Fork',control='Pre-offer operating pressure',total_reduction=3.,naive=float(-naive[1]),adjusted=float(-adjusted[1])))
    offer=rng.binomial(1,.5,count);outcome=12-3*offer+rng.normal(size=count);collider=.8*offer+.8*outcome+rng.normal(size=count)
    naive,_,_=fit_ols(np.column_stack([np.ones(count),offer]),outcome)
    adjusted,_,_=fit_ols(np.column_stack([np.ones(count),offer,collider]),outcome)
    simulations.append(dict(mechanism='Collider',control='Post-offer escalation score',total_reduction=3.,naive=float(-naive[1]),adjusted=float(-adjusted[1])))
    out[8]=dict(weights=weights,ate=sum(g['reduction']*g['ate_weight'] for g in weights),att=sum(g['reduction']*g['att_weight'] for g in weights),atu=sum(g['reduction']*g['atu_weight'] for g in weights),simulations=simulations)
    # Lesson 9: exact/coarsened/propensity matching, explicit overlap and targets.
    v=p.query("cohort=='Voluntary' and 17<=week<=24").groupby(['store_id','offer']).stockout_rate.mean().reset_index().merge(s[['store_id','lead_days','urban','baseline_rate']],on='store_id',validate='one_to_one')
    matching=[]
    for method,cols in [('Exact on lead and location',['lead_days','urban']),('Coarsened baseline + lead + location',['lead_days','urban','baseline_band'])]:
        frame=v.assign(baseline_band=np.floor(v.baseline_rate/5)); effects=[]; kept=[]
        for _,group in frame.groupby(cols):
            treated=group[group.offer==1]; control=group[group.offer==0]
            if len(control) and len(treated):effects.extend((control.stockout_rate.mean()-treated.stockout_rate).tolist());kept.extend(treated.store_id.tolist())
        matching.append(dict(method=method,matched_adopters=len(effects),total_adopters=int(v.offer.sum()),estimate=float(np.mean(effects))))
    covars=['lead_days','urban','baseline_rate']; scoremodel=make_pipeline(StandardScaler(),LogisticRegression(C=1.,max_iter=1000));scoremodel.fit(v[covars],v.offer)
    score=scoremodel.predict_proba(v[covars])[:,1];logit=np.log(score/(1-score));v=v.assign(score=score,logit=logit)
    tr=v[v.offer==1];ct=v[v.offer==0];caliper=.2*np.std(logit,ddof=1);matches=[]
    for a in tr.itertuples():
        index=nearest_score_match(ct,a.logit); c=ct.loc[index]
        if abs(c.logit-a.logit)<=caliper:matches.append((a.Index,index))
    effects=[v.loc[c,'stockout_rate']-v.loc[a,'stockout_rate'] for a,c in matches]
    matching.append(dict(method='Propensity, logit caliper',matched_adopters=len(matches),total_adopters=len(tr),estimate=float(np.mean(effects))))
    balance=[]
    for col in covars:
        denom=np.sqrt((tr[col].var(ddof=1)+ct[col].var(ddof=1))/2)
        balance.append(dict(variable=col,before=float((tr[col].mean()-ct[col].mean())/denom),after=float((v.loc[[a for a,c in matches],col].mean()-v.loc[[c for a,c in matches],col].mean())/denom)))
    models=[]
    for name,design in [('Unadjusted',np.column_stack([np.ones(len(v)),v.offer])),('Starting conditions',np.column_stack([np.ones(len(v)),v.offer,v[covars]]))]:
        beta,cov,err=fit_ols(design,v.stockout_rate);standard=float(np.sqrt(cov[1,1]));models.append(dict(model=name,reduction=float(-beta[1]),low=float(-beta[1]-1.96*standard),high=float(-beta[1]+1.96*standard)))
    models.append(dict(model='Heterogeneous, standardized',reduction=core[9]['estimate'],low=core[9]['low'],high=core[9]['high']))
    out[9]=dict(matching=matching,balance=balance,models=models,caliper=float(caliper),unique_comparisons=len(set(c for a,c in matches)),
        score_ranges=[dict(group='Adopters',low=float(tr.score.min()),high=float(tr.score.max())),dict(group='Nonadopters',low=float(ct.score.min()),high=float(ct.score.max()))])
    # Lesson 10: regression equivalence, placebo windows, targets and controls.
    roll=p.query("cohort=='Rollout' and 17<=week<=32"); periods=roll.assign(after=(roll.week>=25).astype(int)).groupby(['store_id','offer','after']).stockout_rate.mean().reset_index()
    design=np.column_stack([np.ones(len(periods)),periods.offer,periods.after,periods.offer*periods.after]);beta,_,_=fit_ols(design,periods.stockout_rate)
    wide=periods.pivot(index=['store_id','offer'],columns='after',values='stockout_rate').reset_index().merge(s[['store_id','lead_days','urban','baseline_rate']],on='store_id',validate='one_to_one');wide['change']=wide[1]-wide[0]
    X=np.column_stack([np.ones(len(wide)),wide.offer,wide.lead_days,wide.urban,wide.baseline_rate]);bc,vc,ec=fit_ols(X,wide.change);standard=float(np.sqrt(vc[1,1]))
    earlier=roll.query('week<=24').assign(later=lambda x:(x.week>=21).astype(int)).groupby(['store_id','offer','later']).stockout_rate.mean().unstack('later').reset_index();earlier['change']=earlier[1]-earlier[0]
    placebo=difference(earlier[earlier.offer==0].change,earlier[earlier.offer==1].change)
    subgroups=[]
    for urban,group in wide.groupby('urban'):
        result=difference(group[group.offer==0].change,group[group.offer==1].change)
        subgroups.append(dict(urban=int(urban),adopters=int(group.offer.sum()),comparison=int((group.offer==0).sum()),**result))
    weight=np.where(wide.lead_days>=4,2.,1.);treated=wide.offer==1
    weighted=float(np.average(wide.loc[~treated,'change'],weights=weight[~treated])-np.average(wide.loc[treated,'change'],weights=weight[treated]))
    out[10]=dict(regression=list(map(float,beta)),regression_reduction=float(-beta[3]),balanced_stores=len(wide),period_rows=len(periods),placebo=placebo,
        controlled=dict(value=float(-bc[1]),low=float(-bc[1]-1.96*standard),high=float(-bc[1]+1.96*standard)),subgroups=subgroups,priority_weighted=weighted)
    return out

# A separate fictional export: B has an unresolved count; C has conflicting duplicates.
extract = pd.DataFrame({'store':['A','B','C','C'], 'count':[10,np.nan,8,12], 'exposure':[100,50,40,40]})
assert extract.duplicated('store').sum()==1
# The two C records describe the same 40 opportunities: never add both denominators.
complete_low = 100*(10+8)/(100+40)
complete_high = 100*(10+12)/(100+40)
all_low = 100*(10+0+8)/190
all_high = 100*(10+50+12)/190
equal_store_low = (10+100*8/40)/2
assert all_low < complete_low < complete_high < all_high
answer = dict(complete_low=complete_low,complete_high=complete_high,
              all_low=all_low,all_high=all_high,equal_store_low=equal_store_low)

print(json.dumps(answer, indent=2, allow_nan=False))
