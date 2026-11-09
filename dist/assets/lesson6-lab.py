"""Lesson 6: original fictional Mica dispatch costs, seed 660913.
DGP n=604: distance U(1,25), size U(1,12), priority Bernoulli(.25), weather N(0,1),
hub categorical probabilities (.4,.35,.25), 20 independent normal distractors.
log(cost)=3.2+.035*distance+.055*size+.12*priority+.15*weather
          +.012*distance*priority+hub_offset+.08*sin(distance/3)+.28Z.
hub_offset=(0,.12,-.08); Z independent N(0,1). Cost is fictional credits.
Size/weather missing completely at random with probability .08; distractors .05.
Predeclare 75% development, 25% final evaluation; five shuffled development folds.
All imputation, scaling, coefficient fitting and smearing are fitted within each fold.
Separate original simulations demonstrate loss, optimism and information criteria.
No external inputs, inherited fitted outputs or historical source records.
"""
import json
import numpy as np
from scipy.stats import t
from sklearn.model_selection import train_test_split,KFold
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Lasso,LinearRegression
rng=np.random.default_rng(660913)
# Loss changes the population functional being estimated.
outcomes=rng.lognormal(3,.65,3000);mean=float(outcomes.mean());median=float(np.median(outcomes));p80=float(np.quantile(outcomes,.8))
loss=[]
for label,v in [('Mean',mean),('Median',median),('80th percentile',p80)]:
    loss.append([label,v,float(np.mean((outcomes-v)**2)),float(np.mean(np.abs(outcomes-v))),float(np.mean(4*np.maximum(outcomes-v,0)+np.maximum(v-outcomes,0)))])
# Bias/variance demonstration, independent of main case. True curve: 8+3x+4x^2.
grid=np.linspace(-1,1,41);truth=8+3*grid+4*grid**2;sim=[]
for degree in [1,3,9]:
    preds=[];trainloss=[]
    for j in range(160):
        xx=rng.uniform(-1,1,45);yy=8+3*xx+4*xx**2+rng.normal(0,2,45);X=np.vander(xx,degree+1,increasing=True);b=np.linalg.lstsq(X,yy,rcond=None)[0];preds.append(np.vander(grid,degree+1,increasing=True)@b);trainloss.append(float(np.mean((yy-X@b)**2)))
    P=np.array(preds);bias2=float(np.mean((P.mean(axis=0)-truth)**2));variance=float(np.mean(P.var(axis=0,ddof=0)));sim.append([degree,float(np.mean(trainloss)),bias2,variance,4.,bias2+variance+4])
# Same-data Gaussian likelihood comparison, including unknown variance in k.
qx=rng.uniform(-1,1,140);qy=45+10*qx+12*qx**2+rng.normal(0,5,140);criteria=[]
for degree in [1,2,3,6]:
    Q=np.vander(qx,degree+1,increasing=True);b=np.linalg.lstsq(Q,qy,rcond=None)[0];e=qy-Q@b;sse=float(e@e);k=degree+2;n=len(qx);minus2=n*(np.log(2*np.pi)+1+np.log(sse/n));criteria.append([degree,k,sse,float(minus2+2*k),float(minus2+np.log(n)*k)])
Q=np.vander(qx,3,increasing=True);b=np.linalg.lstsq(Q,qy,rcond=None)[0];e=qy-Q@b;s2=float(e@e/(140-3));v=np.array([1,.5,.25]);pred=float(v@b);sem=float(np.sqrt(s2*v@np.linalg.inv(Q.T@Q)@v));sep=float(np.sqrt(sem**2+s2));crit=t.ppf(.975,137);example_interval=[pred,pred-crit*sem,pred+crit*sem,pred-crit*sep,pred+crit*sep]

def generate(n,shift=False):
    distance=rng.uniform(20,40,n) if shift else rng.uniform(1,25,n)
    size=rng.uniform(1,12,n);priority=rng.binomial(1,.25,n);weather=rng.normal(size=n);hub=rng.choice(3,n,p=[.4,.35,.25]);noise=rng.normal(size=(n,20))
    logmu=3.2+.035*distance+.055*size+.12*priority+.15*weather+.012*distance*priority+np.choose(hub,[0,.12,-.08])+.08*np.sin(distance/3)+(.12 if shift else 0)
    y=np.exp(logmu+.28*rng.normal(size=n))
    # Build interactions after recording raw missing values, so missingness propagates.
    size[rng.random(n)<.08]=np.nan;weather[rng.random(n)<.08]=np.nan;noise[rng.random((n,20))<.05]=np.nan
    X=np.column_stack([distance,size,priority,weather,hub==1,hub==2,distance**2,size**2,distance*size,distance*priority,noise])
    return X,y
scale_x=np.arange(2.,12.,2.);scale_mean=float(scale_x.mean());scale_sd=float(scale_x.std(ddof=0));scale_z=(scale_x-scale_mean)/scale_sd
scaling_example=dict(x=scale_x.tolist(),z=scale_z.tolist(),mean=scale_mean,sd=scale_sd,raw_slope=2.5,scaled_slope=float(2.5*scale_sd),soft_z=.8,alpha=.15,soft_solution=float(max(.8-.15,0)))
names=['Distance','Size','Priority','Weather','Hub blue','Hub copper','Distance squared','Size squared','Distance × size','Distance × priority']+[f'Noise {i+1}' for i in range(20)]
X,y=generate(604);dev,test=train_test_split(np.arange(len(y)),test_size=.25,random_state=660914);folds=list(KFold(5,shuffle=True,random_state=660915).split(dev));alphas=np.logspace(-3,0,9)
def pipeline(alpha):
    estimator=LinearRegression() if alpha is None else Lasso(alpha=float(alpha),max_iter=100000,tol=1e-9)
    return make_pipeline(SimpleImputer(strategy='median'),StandardScaler(),estimator)
def fit_predict(tr,va,alpha,cols=None):
    cols=np.arange(X.shape[1]) if cols is None else cols
    model=pipeline(alpha);model.fit(X[tr][:,cols],np.log(y[tr]));smear=float(np.exp(np.log(y[tr])-model.predict(X[tr][:,cols])).mean());pred=smear*np.exp(model.predict(X[va][:,cols]));return model,smear,pred
search=[];oofs={};fold_results={}
for alpha in alphas:
    oof=np.empty(len(dev));fr=[]
    for train,valid in folds:
        model,smear,pred=fit_predict(dev[train],dev[valid],alpha);oof[valid]=pred;se=(y[dev[valid]]-pred)**2;fr.append([len(valid),float(se.sum()),float(np.sqrt(se.mean()))])
    mse=float(np.mean((y[dev]-oof)**2));search.append([float(alpha),float(np.sqrt(mse))]);oofs[float(alpha)]=oof;fold_results[float(alpha)]=fr
best=min(search,key=lambda r:r[1])[0]
# Compare declared feature sets on same rows/folds; only alpha search selects final LASSO.
feature_comparisons=[]
for label,cols in [('Core: distance, size, priority',np.arange(3)),('Context: core + weather + hub',np.arange(6)),('Expanded: context + shapes + noise',np.arange(30))]:
    oof=np.empty(len(dev))
    for tr,va in folds:
        model,smear,pred=fit_predict(dev[tr],dev[va],None,cols);oof[va]=pred
    model,smear,training=fit_predict(dev,dev,None,cols)
    feature_comparisons.append([label,len(cols)+1,float(np.sqrt(np.mean((y[dev]-training)**2))),float(np.sqrt(np.mean((y[dev]-oof)**2)))])
# Final procedure frozen: minimum CV original-scale RMSE alpha; median imputation;
# standardized expanded design; log target; global training smearing; no post-test tuning.
final,smear,testpred=fit_predict(dev,test,best);trainpred=smear*np.exp(final.predict(X[dev]));base=float(y[dev].mean());res=y[test]-testpred
scores=[]
for label,prediction in [('Development mean baseline',np.full(len(test),base)),('Frozen LASSO + smearing',testpred)]:
    err=y[test]-prediction;scores.append([label,float(np.sqrt(np.mean(err**2))),float(np.mean(np.abs(err))),float(np.mean(err))])
medpred=np.exp(final.predict(X[test]));median_rmse=float(np.sqrt(np.mean((y[test]-medpred)**2)));log_rmse=float(np.sqrt(np.mean((np.log(y[test])-final.predict(X[test]))**2)))
# Coefficient path uses development data only. It is descriptive, not another selection rule.
path=[]
for alpha in alphas:
    model,sm,pr=fit_predict(dev,dev,float(alpha));est=model[-1];path.append([float(alpha)]+est.coef_[:10].tolist()+[int(np.count_nonzero(np.abs(est.coef_)>1e-10)),float(est.dual_gap_),int(est.n_iter_)])
est=final[-1];coef=[[name,float(v),float(final[1].scale_[i])] for i,(name,v) in enumerate(zip(names,est.coef_)) if abs(v)>1e-10]
# Explain a leakage boundary with observed fitted medians, not a falsely optimistic score.
tr0,va0=folds[0];fold_median=float(np.nanmedian(X[dev[tr0],1]));dev_median=float(np.nanmedian(X[dev,1]));global_median=float(np.nanmedian(X[:,1]))
# Subgroup threshold fixed using development outcome distribution, then audited on test.
threshold=float(np.quantile(y[dev],.9));tail=y[test]>=threshold;subgroups=[]
for label,mask in [('Below development p90',~tail),('At/above development p90',tail)]:
    rr=res[mask];subgroups.append([label,int(mask.sum()),float(np.sqrt(np.mean(rr**2))),float(np.mean(rr))])
# A new fictional future population changes support AND conditional mean, on purpose.
futureX,futurey=generate(200,shift=True);futurepred=smear*np.exp(final.predict(futureX));future_err=futurey-futurepred
future=dict(n=len(futurey),rmse=float(np.sqrt(np.mean(future_err**2))),bias=float(future_err.mean()),outside=float(np.mean(futureX[:,0]>np.max(X[dev,0]))),distance_min=float(futureX[:,0].min()),distance_max=float(futureX[:,0].max()))
fr=fold_results[best];pooled=float(np.sqrt(sum(row[1] for row in fr)/sum(row[0] for row in fr)));meanroot=float(np.mean([row[2] for row in fr]));assert np.isclose(pooled,min(row[1] for row in search));assert len(set(dev)&set(test))==0
print(json.dumps(dict(seed=660913,n=len(y),development_n=len(dev),test_n=len(test),loss=loss,bias_variance=sim,criteria=criteria,example_interval=example_interval,search=search,selected_alpha=best,folds=fr,pooled_rmse=pooled,mean_fold_rmse=meanroot,feature_comparisons=feature_comparisons,final_scores=scores,smear=smear,theoretical_smear=float(np.exp(.28**2/2)),median_rmse=median_rmse,log_rmse=log_rmse,training_rmse=float(np.sqrt(np.mean((y[dev]-trainpred)**2))),coefficients=coef,nonzeros=len(coef),path=path,dual_gap=float(est.dual_gap_),iterations=int(est.n_iter_),fold_size_median=fold_median,dev_size_median=dev_median,all_size_median=global_median,tail_threshold=threshold,subgroups=subgroups,future=future,scaling_example=scaling_example,scatter=np.column_stack([y[test],testpred]).tolist(),tail_rows=[[int(test[i]),float(y[test][i]),float(testpred[i]),float(res[i])] for i in np.argsort(y[test])[-5:][::-1]],residual_scatter=np.column_stack([testpred[:40],res[:40]]).tolist(),selected_first=[float(y[test][0]),float(medpred[0]),float(testpred[0])],baseline=base,missing_counts=np.isnan(X[dev]).sum(axis=0).tolist(),train_distance_max=float(np.max(X[dev,0])))))
