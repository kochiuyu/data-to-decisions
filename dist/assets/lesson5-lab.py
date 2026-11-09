"""Lesson 5: original fictional Cedar calibration rigs, seed 550829.
E~Uniform(0,12); D~Bernoulli(logit^-1(-1+.2E)); A~Uniform(0,1).
Bench C has probabilities (.4,.35,.25); Ec=E-6.
Y=70+2Ec-.08Ec^2+5D+1.1D*Ec+4A+.7Ec*A+offset(C)+(3+.4E)Z.
offset(amber,blue,copper)=(0,4,-3), independent Z~N(0,1); n=260.
Y: calibration units/hour; E: service years; D: powered fixture; A: tool setting.
The separate Gaussian interval experiment has Y=12+2X+4Z, X~Uniform(0,10).
No external inputs. The fixture assignment is associated with service age.
"""
import json
import numpy as np
from scipy.stats import t, f, chi2
from sklearn.model_selection import KFold
rng=np.random.default_rng(550829)
def fit(X,y):
    b=np.linalg.lstsq(X,y,rcond=None)[0];e=y-X@b;n,p=X.shape;inv=np.linalg.inv(X.T@X);sse=float(e@e);s2=sse/(n-p);h=np.sum((X@inv)*X,axis=1)
    hc3=inv@((X.T*(e/(1-h))**2)@X)@inv
    return dict(b=b,e=e,sse=sse,s2=s2,cov=s2*inv,hc3=hc3,h=h,n=n,p=p)
# Exact-normal finite-sample interval illustration, explicitly separate from heteroskedastic case.
x=rng.uniform(0,10,80);y=12+2*x+4*rng.normal(size=80);X=np.column_stack([np.ones(80),x]);a=fit(X,y);q=t.ppf(.975,78)
intervals=[]
for x0 in [0,5,10,12]:
    v=np.array([1.,x0]);pred=float(v@a['b']);se=float(np.sqrt(v@a['cov']@v));spe=float(np.sqrt(se*se+a['s2']))
    intervals.append(dict(x=x0,pred=pred,mean_lo=pred-q*se,mean_hi=pred+q*se,pred_lo=pred-q*spe,pred_hi=pred+q*spe,se_mean=se,se_pred=spe))
levels=[]
for level in [.9,.95,.99]:
    crit=t.ppf((1+level)/2,78);se=np.sqrt(a['cov'][1,1]);levels.append([level,float(a['b'][1]-crit*se),float(a['b'][1]+crit*se)])
coverage=[]
for repeat in range(400):
    yy=12+2*x+4*rng.normal(size=80);af=fit(X,yy);se=np.sqrt(af['cov'][1,1]);coverage.append([float(af['b'][1]),float(af['b'][1]-q*se),float(af['b'][1]+q*se)])
cover=float(np.mean([lo<=2<=hi for est,lo,hi in coverage]))
# Main case: all compared fits use the exact same 260 rows.
n=260;E=rng.uniform(0,12,n);Ec=E-6;D=rng.binomial(1,1/(1+np.exp(-(-1+.2*E))));A=rng.uniform(0,1,n);C=rng.choice(3,n,p=[.4,.35,.25]);Z=rng.normal(size=n)
mu=70+2*Ec-.08*Ec**2+5*D+1.1*D*Ec+4*A+.7*Ec*A+np.choose(C,[0,4,-3]);Y=mu+(3+.4*E)*Z
short=fit(np.column_stack([np.ones(n),D]),Y);add=fit(np.column_stack([np.ones(n),D,Ec]),Y);aux=fit(np.column_stack([np.ones(n),D]),Ec)
controls=np.column_stack([np.ones(n),Ec]);rD=D-controls@np.linalg.lstsq(controls,D,rcond=None)[0];rY=Y-controls@np.linalg.lstsq(controls,Y,rcond=None)[0];fwl=float(rD@rY/(rD@rD));ovb=float(add['b'][1]+add['b'][2]*aux['b'][1])
M=np.column_stack([np.ones(n),D,Ec,Ec**2,D*Ec,A,Ec*A,C==1,C==2]);names=['Intercept at E=6, A=0, amber','Powered fixture','Service years centered','Service years squared','Fixture × service years','Tool setting','Service years × tool setting','Blue bench','Copper bench'];full=fit(M,Y)
# Robust contrasts: asymptotic normal critical value; no claim of exact finite-sample coverage.
from scipy.stats import norm
contrasts=[]
for val in [3,6,9]:
    v=np.zeros(M.shape[1]);v[1]=1;v[4]=val-6;est=float(v@full['b']);se=float(np.sqrt(v@full['hc3']@v));contrasts.append([val,est,est-norm.ppf(.975)*se,est+norm.ppf(.975)*se])
# Drop curvature and fixture interaction together (2 restrictions).
restricted=np.delete(M,[3,4],axis=1);red=fit(restricted,Y);F=((red['sse']-full['sse'])/2)/(full['sse']/(n-M.shape[1]));Fp=float(f.sf(F,2,n-M.shape[1]));R=np.eye(M.shape[1])[[3,4]];W=float((R@full['b'])@np.linalg.solve(R@full['hc3']@R.T,R@full['b']));Wp=float(chi2.sf(W,2))
# Reference change: copper becomes baseline; fitted values are unchanged.
Mc=M.copy();Mc[:,7]=C==0;Mc[:,8]=C==1;fc=fit(Mc,Y);reference_error=float(np.max(np.abs(M@full['b']-Mc@fc['b'])))
# Residual audit uses predictions from models that did not see the held-out row.
oof=np.empty(n)
for tr,va in KFold(5,shuffle=True,random_state=550830).split(M):
    oof[va]=M[va]@np.linalg.lstsq(M[tr],Y[tr],rcond=None)[0]
er=Y-oof;largest=np.argsort(np.abs(er))[-5:][::-1]
residual_rows=[[int(i),float(Y[i]),float(oof[i]),float(er[i]),float(E[i])] for i in largest]
# Finite-sample identity must hold even though the additive model omits real terms.
assert np.isclose(short['b'][1],ovb,rtol=1e-10)
assert np.isclose(fwl,add['b'][1],rtol=1e-10)
assert reference_error<1e-8
counts=[[label,int((C==k).sum()),float(Y[C==k].mean())] for k,label in enumerate(['Amber','Blue','Copper'])]
fullcoef=[[names[i],float(full['b'][i]),float(np.sqrt(full['cov'][i,i])),float(np.sqrt(full['hc3'][i,i]))] for i in range(M.shape[1])]
print(json.dumps(dict(seed=550829,n=n,interval_b=a['b'].tolist(),interval_s=float(np.sqrt(a['s2'])),intervals=intervals,levels=levels,coverage=cover,repetitions=len(coverage),coverage_first=coverage[:16],short=short['b'].tolist(),add=add['b'].tolist(),aux=aux['b'].tolist(),fwl=fwl,ovb_reconstructed=ovb,shift=float(short['b'][1]-add['b'][1]),product=float(add['b'][2]*aux['b'][1]),rD2=float(rD@rD),D2=float(((D-D.mean())**2).sum()),fixture_prevalence=float(D.mean()),fullcoef=fullcoef,full_b=full['b'].tolist(),contrasts=contrasts,F=float(F),F_p=Fp,W=W,W_p=Wp,q=2,df=n-M.shape[1],restricted_sse=red['sse'],full_sse=full['sse'],counts=counts,reference_error=reference_error,copper_intercept=float(fc['b'][0]),amber_intercept=float(full['b'][0]),oof_rmse=float(np.sqrt(np.mean(er**2))),training_rmse=float(np.sqrt(np.mean(full['e']**2))),residual_rows=residual_rows,scatter=np.column_stack([Y[:36],oof[:36]]).tolist(),resid_plot=np.column_stack([oof[:36],er[:36]]).tolist(),continuous_slopes=[float(full['b'][5]+full['b'][6]*(v-6)) for v in [3,6,9]],quadratic_slopes=[float(full['b'][2]+2*full['b'][3]*(v-6)+full['b'][4]+full['b'][6]*.5) for v in [3,6,9]],group_means=[float(Y[D==v].mean()) for v in [0,1]],experience_means=[float(E[D==v].mean()) for v in [0,1]],residual_mean=float(er.mean()))))
