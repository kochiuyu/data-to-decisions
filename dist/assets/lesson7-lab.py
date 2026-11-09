"""Lesson 7. All data are invented, fixed-seed teaching observations.
DGPs are chosen for pedagogy, not estimated from any external dataset.
One ad observation is one independently assigned, fully followed user.
"""
import json,itertools,math
import numpy as np
from scipy.stats import norm
rng=np.random.default_rng(7107)
n=12
skill=rng.integers(0,4,n); load=rng.integers(0,3,n)
y0=40+4*skill-2*load+rng.normal(0,2,n)
tau=2+1.5*skill-2*load
y1=y0+tau
d=(skill>=2).astype(int); y=np.where(d,y1,y0)
ate=tau.mean();att=tau[d==1].mean();atu=tau[d==0].mean()
gap=y[d==1].mean()-y[d==0].mean()
base=y0[d==1].mean()-y0[d==0].mean()
mini_y0=rng.integers(20,36,4).astype(float);mini_tau=rng.integers(-2,8,4).astype(float)
rollouts=[]
for chosen in itertools.combinations(range(4),2):
    z=np.array([i in chosen for i in range(4)])
    observed=mini_y0+z*mini_tau
    rollouts.append({'treated':','.join(str(i+1) for i in chosen),'estimate':float(observed[z].mean()-observed[~z].mean()),'baseline_gap':float(mini_y0[z].mean()-mini_y0[~z].mean()),'att':float(mini_tau[z].mean())})
ads=[]
for z in (0,1):
    N=12000; click=rng.binomial(1,.065+.009*z,N); buy=click*rng.binomial(1,.10-.005*z,N)
    ads.append({'arm':z,'users':N,'clicks':int(click.sum()),'actions':int(buy.sum()),'click_rate':float(click.mean()),'action_rate':float(buy.mean()),'postclick_rate':float(buy.sum()/click.sum())})
def diff(key):
    a,b=ads;p0=a[key];p1=b[key];se=math.sqrt(p0*(1-p0)/a['users']+p1*(1-p1)/b['users']);delta=p1-p0
    return {'difference':delta,'se':se,'low':delta-1.96*se,'high':delta+1.96*se,'relative':delta/p0,'p_value':float(2*norm.sf(abs(delta/se)))}
click_diff=diff('click_rate');action_diff=diff('action_rate')
z=rng.binomial(1,.5,3000);uptake_u=rng.uniform(size=len(z));take0=(uptake_u<.15).astype(int);take1=(uptake_u<.70).astype(int);take=np.where(z,take1,take0); outcome=20+4*take+rng.normal(0,4,len(z))
assert np.all(take1>=take0)
itt=outcome[z==1].mean()-outcome[z==0].mean();first=take[z==1].mean()-take[z==0].mean()
pbar=(.065+.073)/2;needed=math.ceil(2*(norm.ppf(.975)+norm.ppf(.8))**2*pbar*(1-pbar)/.008**2)
net={'value_per_action':30,'incremental_cost_per_user':.02,'per_user':30*action_diff['difference']-.02,'low':30*action_diff['low']-.02,'high':30*action_diff['high']-.02,'break_even_rate':.02/30}
out={'seed':7107,'teams':[{'team':i+1,'skill':int(skill[i]),'load':int(load[i]),'d':int(d[i]),'y0':float(y0[i]),'y1':float(y1[i]),'tau':float(tau[i]),'observed':float(y[i])} for i in range(n)],'ate':float(ate),'att':float(att),'atu':float(atu),'treated_share':float(d.mean()),'observed_gap':float(gap),'baseline_gap':float(base),'mini_y0':mini_y0.tolist(),'mini_tau':mini_tau.tolist(),'rollouts':rollouts,'randomization_mean':float(np.mean([r['estimate'] for r in rollouts])),'mini_ate':float(mini_tau.mean()),'ads':ads,'click_diff':click_diff,'action_diff':action_diff,'itt':float(itt),'first_stage':float(first),'wald':float(itt/first),'sample_size_per_arm':needed,'net':net}
assert np.isclose(gap,att+base)
assert np.isclose(ate,d.mean()*att+(1-d.mean())*atu)
assert np.isclose(out['randomization_mean'],out['mini_ate'])
print(json.dumps(out,indent=2,allow_nan=False))
