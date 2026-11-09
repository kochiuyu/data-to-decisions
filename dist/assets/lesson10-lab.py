"""Lesson 10. Synthetic facility rollout panel, fixed seed 10110.
80 facilities, 8 periods, fixed baseline treatment groups, rollout at period 4.
Unit heterogeneity, common shocks and AR(1) noise generate repeated observations.
No external sources or empirical calibration. All units remain observed.
"""
import json
import numpy as np
from scipy.stats import t as student_t
rng=np.random.default_rng(10110);G=80;T=8
# Purposive adoption depends on baseline type, but the untreated DGP has common trends.
x=rng.normal(size=G);treated=(x+ .6*rng.normal(size=G)>0).astype(int)
size=rng.integers(50,201,G);alpha=55+5*x+rng.normal(0,3,G);tau=2+1.2*x
noise=np.zeros((G,T));noise[:,0]=rng.normal(0,2,G)
for t in range(1,T):noise[:,t]=.65*noise[:,t-1]+rng.normal(0,1.5,G)
common=np.array([0,.5,.9,1.4,2.0,2.4,2.8,3.5])
y0=alpha[:,None]+common+noise
y=y0+treated[:,None]*(np.arange(T)>=4)*tau[:,None]
pre=y[:,:4].mean(1);post=y[:,4:].mean(1);delta=post-pre
means={'treated_pre':float(pre[treated==1].mean()),'treated_post':float(post[treated==1].mean()),'control_pre':float(pre[treated==0].mean()),'control_post':float(post[treated==0].mean())}
did=means['treated_post']-means['treated_pre']-means['control_post']+means['control_pre']
N=G*T;g=np.repeat(np.arange(G),T);d=np.repeat(treated,T);postrow=np.tile(np.arange(T)>=4,G).astype(int)
X=np.column_stack([np.ones(N),d,postrow,d*postrow]);outcome=y.ravel();beta=np.linalg.lstsq(X,outcome,rcond=None)[0];res=outcome-X@beta;bread=np.linalg.inv(X.T@X)
naive_cov=(res@res/(N-X.shape[1]))*bread
meat=np.zeros((4,4))
for k in range(G):
    score=X[g==k].T@res[g==k];meat+=np.outer(score,score)
cluster_cov=G/(G-1)*(N-1)/(N-X.shape[1])*bread@meat@bread
cluster_se=float(np.sqrt(cluster_cov[3,3]));crit=float(student_t.ppf(.975,G-1))
naive_se=float(np.sqrt(naive_cov[3,3]))
prechange=y[:,3]-y[:,0];early=float(prechange[treated==1].mean()-prechange[treated==0].mean());earlyse=float(np.sqrt(prechange[treated==1].var(ddof=1)/(treated==1).sum()+prechange[treated==0].var(ddof=1)/(treated==0).sum()))
vt=prechange[treated==1].var(ddof=1)/(treated==1).sum();vc=prechange[treated==0].var(ddof=1)/(treated==0).sum();earlydf=float((vt+vc)**2/(vt**2/((treated==1).sum()-1)+vc**2/((treated==0).sum()-1)));earlycrit=float(student_t.ppf(.975,earlydf))
weighted=float(np.average(delta[treated==1],weights=size[treated==1])-np.average(delta[treated==0],weights=size[treated==0]))
weighted_truth=float(np.average(tau[treated==1],weights=size[treated==1]))
# Counterfactual violations: add a treated-only untreated drift after baseline,
# or give comparison facilities part of the same post-rollout effect.
def estimator(a):
    change=a[:,4:].mean(1)-a[:,:4].mean(1)
    return float(change[treated==1].mean()-change[treated==0].mean())
drift=.35*treated[:,None]*np.arange(T)
spill=.8*(1-treated[:,None])*(np.arange(T)>=4)
anticipation=1.2*treated[:,None]*(np.arange(T)==3)
# Changing sample composition: remove low-baseline treated facilities post-period.
retained=(treated==0)|(alpha>=np.median(alpha[treated==1]))
composition=float(post[(treated==1)&retained].mean()-pre[treated==1].mean()-(post[treated==0].mean()-pre[treated==0].mean()))
# Log specification is a genuinely different transformed outcome model.
logdid=estimator(np.log(y));logchange=np.log(y[:,4:].mean(1))-np.log(y[:,:4].mean(1));logratio=float(logchange[treated==1].mean()-logchange[treated==0].mean())
series={'Treated observed':y[treated==1].mean(0).tolist(),'Comparison observed':y[treated==0].mean(0).tolist(),'Treated untreated truth':y0[treated==1].mean(0).tolist()}
# Baseline-weighted aggregate rates illustrate compatible numerators/denominators.
rate_before=float((pre*size).sum()/size.sum());unweighted_before=float(pre.mean())
out={'seed':10110,'units':G,'periods':T,'treated_units':int(treated.sum()),'control_units':int((1-treated).sum()),'rows':N,'means':means,'treated_change':means['treated_post']-means['treated_pre'],'control_change':means['control_post']-means['control_pre'],'counterfactual':means['treated_pre']+means['control_post']-means['control_pre'],'did':did,'truth_att':float(tau[treated==1].mean()),'regression_beta':beta.tolist(),'naive_se':naive_se,'cluster_se':cluster_se,'interval':[did-crit*cluster_se,did+crit*cluster_se],'pretrend':{'difference':early,'se':earlyse,'low':early-earlycrit*earlyse,'high':early+earlycrit*earlyse,'df':earlydf,'p_value':float(2*student_t.sf(abs(early/earlyse),earlydf))},'weighted_did':weighted,'weighted_truth_att':weighted_truth,'series':series,'violations':{'differential_drift':estimator(y+drift),'drift_bias':.35*(np.arange(4,8).mean()-np.arange(4).mean()),'comparison_spillover':estimator(y+spill),'anticipation':estimator(y+anticipation),'composition':composition,'post_treated_retained':int(((treated==1)&retained).sum())},'sensitivity':{'drifts':[-.5,-.25,0,.25,.5],'effects':[did-v for v in [-.5,-.25,0,.25,.5]]},'log_did':logdid,'log_percent':float(100*np.expm1(logdid)),'log_of_period_means_did':logratio,'baseline_weighted_rate':rate_before,'baseline_unweighted_rate':unweighted_before,'subgroups':[{'type':name,'n':int(((treated==1)&mask).sum()),'true_att':float(tau[(treated==1)&mask].mean())} for name,mask in [('X below 1',x<1),('X at least 1',x>=1)]]}
assert np.isclose(did,beta[3])
assert np.isclose(estimator(y),did)
assert np.all(y>0)
print(json.dumps(out,indent=2,allow_nan=False))
