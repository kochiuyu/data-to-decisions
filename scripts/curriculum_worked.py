"""Visible worked continuations, shared by technical pages and executable labs."""
WORKED={
2:'''# Inspect distribution and association using the same store profiles.
stores = world()['stores']
rates = stores.baseline_rate.to_numpy()
counts, edges = np.histogram(rates, bins=np.arange(0, 36, 4))
assert counts.sum() == 150
sample_sd = rates.std(ddof=1)
correlation = np.corrcoef(stores.baseline_demand, rates)[0,1]
assert np.isclose(sample_sd, lesson_result(2)['depth']['sd'])
assert np.isclose(correlation, lesson_result(2)['depth']['correlation'])
x = stores.baseline_demand.to_numpy()
products = (x-x.mean()) * (rates-rates.mean())
covariance = products.sum() / (len(x)-1)
assert np.isclose(covariance, np.cov(x,rates,ddof=1)[0,1])
assert np.isclose(correlation, covariance/(x.std(ddof=1)*sample_sd))
# Recalculate distributions and association within each group.
group_checks = {}
for name, g in stores.groupby('risk_group'):
    q = g.baseline_rate.quantile([.25,.5,.75])
    corr = g.baseline_demand.corr(g.baseline_rate)
    group_checks[name] = dict(n=len(g),quartiles=q.to_list(),r=corr)
    bands = pd.cut(g.baseline_rate, [-np.inf,10,15,np.inf])
    shares = bands.value_counts(sort=False) / len(g)
    assert np.isclose(shares.sum(), 1)
assert sum(g['n'] for g in group_checks.values()) == 150
# Verify normalization and the relation between raw and binned views.
for width in [2,4]:
    edges = np.arange(4,24+width,width)
    counts, _ = np.histogram(rates, edges)
    density = counts / (len(rates)*width)
    assert counts.sum() == len(rates)
    assert np.isclose((density*np.diff(edges)).sum(), 1)
binned = stores.assign(bin=pd.qcut(stores.baseline_demand,5))
bin_means = binned.groupby('bin',observed=True).baseline_rate.mean()
assert np.isclose(bin_means.mean(), rates.mean())''',
3:'''# Bootstrap sampled stores, then test the specified target.
audit = world()['audit'].stockout_rate.to_numpy()
rng = np.random.default_rng(SEED + 303)
boot = audit[rng.integers(0, len(audit), (2000, len(audit)))].mean(axis=1)
percentile_interval = np.quantile(boot, [.025, .975])
standard_error = audit.std(ddof=1) / np.sqrt(len(audit))
test_statistic = (audit.mean() - 10) / standard_error
one_sided_p = t.sf(test_statistic, len(audit)-1)
assert np.isclose(percentile_interval[0], lesson_result(3)['depth']['bootstrap_low'])
assert np.isclose(one_sided_p, lesson_result(3)['depth']['p_one_sided'])

# Paired observations retain their store identity.
audit_rows = world()['audit'][['store_id','stockout_rate']]
system_rows = world()['panel'].query('week==16')[['store_id','stockout_rate']]
paired = audit_rows.merge(system_rows, on='store_id', suffixes=('_audit','_system'), validate='one_to_one')
differences = paired.stockout_rate_audit - paired.stockout_rate_system
assert np.isclose(differences.mean(), lesson_result(3)['depth']['paired']['mean'])
# Complete the paired t-test from the differences.
paired_se = differences.std(ddof=1) / np.sqrt(len(differences))
paired_t = differences.mean() / paired_se
paired_p = 2*t.sf(abs(paired_t), len(differences)-1)
assert np.isclose(paired_p,lesson_result(3)['depth']['paired']['p'])
# Independent groups require separate variance contributions.
context = world()['stores'][['store_id','urban']]
compare = audit_rows.merge(context,on='store_id',validate='one_to_one')
u = compare.loc[compare.urban==1,'stockout_rate']
r = compare.loc[compare.urban==0,'stockout_rate']
v1, v0 = u.var(ddof=1)/len(u), r.var(ddof=1)/len(r)
welch_se = np.sqrt(v1+v0)
welch_df = (v1+v0)**2 / (v1**2/(len(u)-1)+v0**2/(len(r)-1))
welch_t = (u.mean()-r.mean()) / welch_se
welch_p = 2*t.sf(abs(welch_t),welch_df)
expected = lesson_result(3)['depth']['independent']
assert np.allclose([welch_se,welch_df,welch_p],
                   [expected['se'],expected['df'],expected['p']])
# Wilson arithmetic uses the proportion of stores above target.
n = len(audit)
phat = np.mean(audit>10)
z = norm.ppf(.975)
centre = (phat+z*z/(2*n)) / (1+z*z/n)
half = z*np.sqrt(phat*(1-phat)/n+z*z/(4*n*n)) / (1+z*z/n)
expected_prop = lesson_result(3)['depth']['proportion']
assert np.allclose([centre-half,centre+half],
                   [expected_prop['low'],expected_prop['high']])
# Histogram bins retain every paired difference, including the right tail.
assert np.histogram(differences,bins=np.arange(-5,12,2))[0].sum()==30''',
4:'''# Verify the OLS variation decomposition and a log specification.
stores = world()['stores']
x = stores.lead_days.to_numpy()
y = stores.baseline_rate.to_numpy()
X = np.column_stack([np.ones(len(x)), x])
beta, covariance, residual = fit_ols(X, y)
sst = np.sum((y-y.mean())**2)
sse = np.sum(residual**2)
ssr = np.sum((X@beta-y.mean())**2)
assert np.isclose(sst, sse+ssr)
assert np.isclose(1-sse/sst, lesson_result(4)['depth']['r_squared'])
log_beta, _, log_residual = fit_ols(X, np.log(y))
smearing = np.exp(log_residual).mean()
rate_predictions = np.exp(X@log_beta) * smearing
assert np.isclose(smearing, lesson_result(4)['depth']['forms'][1]['smearing'])
# OLS identities use an intercept and the same estimation sample.
fitted = X @ beta
assert np.isclose(residual.sum(), 0, atol=1e-9)
assert np.isclose(fitted.mean(), y.mean())
assert np.isclose(np.dot(fitted-y.mean(), residual), 0, atol=1e-9)
assert np.isclose(1-sse/sst, np.corrcoef(x,y)[0,1]**2)
slope_manual = np.cov(x,y,ddof=1)[0,1] / np.var(x,ddof=1)
assert np.isclose(beta[1], slope_manual)
# Four equations; log outcomes return to the same rate scale.
form_fits = []
for xx, yy, logged in [(x,y,False),(x,np.log(y),True),
                       (np.log(x),y,False),(np.log(x),np.log(y),True)]:
    design = np.column_stack([np.ones(len(x)), xx])
    coef = np.linalg.lstsq(design,yy,rcond=None)[0]
    err = yy-design@coef
    smear = np.exp(err).mean() if logged else 1.
    pred = np.exp(design@coef)*smear if logged else design@coef
    form_fits.append((coef,smear,np.sqrt(np.mean((y-pred)**2))))
assert np.allclose([v[2] for v in form_fits],
                  [v['rmse_original'] for v in lesson_result(4)['depth']['forms']])
# The nonlinear comparison uses continuous demand in these same stores.
dx = stores.baseline_demand.to_numpy()
z = (dx-100)/10  # one unit is ten demand-index points
grid = np.linspace(dx.min(), dx.max(), 121)
zg = (grid-100)/10
curve_fits = {}
for degree in [1,2,3]:
    design = np.column_stack([z**k for k in range(degree+1)])
    coef = np.linalg.lstsq(design,y,rcond=None)[0]
    pred = design@coef
    line = np.column_stack([zg**k for k in range(degree+1)])@coef
    curve_fits[degree] = (coef,pred,line,np.sqrt(np.mean((y-pred)**2)))
# A continuous hinge changes the slope after demand index 110 (z=1).
design = np.column_stack([np.ones(len(z)),z,np.maximum(z-1,0)])
spline_coef = np.linalg.lstsq(design,y,rcond=None)[0]
spline_pred = design@spline_coef
spline_line = np.column_stack([np.ones(len(zg)),zg,np.maximum(zg-1,0)])@spline_coef
assert np.isclose(spline_coef[0]+spline_coef[1],
                  spline_coef[0]-spline_coef[2]+sum(spline_coef[1:]))
# Local linear fits: closest fraction, tricube weights, no robust iterations.
def local_fit(at, fraction):
    values = []
    for point in at:
        distance = abs(dx-point)
        width = np.sort(distance)[int(np.ceil(fraction*len(dx)))-1]
        weight = np.maximum(1-(distance/width)**3,0)**3
        local_x = np.column_stack([np.ones(len(dx)),dx-point])
        coef = np.linalg.lstsq(local_x*np.sqrt(weight[:,None]),
                               y*np.sqrt(weight),rcond=None)[0]
        values.append(coef[0])
    return np.array(values)
smooth35, smooth65 = local_fit(grid,.35), local_fit(grid,.65)
assert np.isfinite([smooth35,smooth65]).all()
# A leave-one-store-out calculation measures influence on the delivery slope.
leave_slopes = []
for i in range(len(x)):
    keep = np.arange(len(x)) != i
    leave_slopes.append(np.linalg.lstsq(X[keep],y[keep],rcond=None)[0][1])
influential = int(np.argmax(abs(np.array(leave_slopes)-beta[1])))
# A cubic on four distinct delivery values reproduces their group means.
cubic = np.linalg.lstsq(np.column_stack([x**k for k in range(4)]),y,rcond=None)[0]
assert np.allclose(np.column_stack([np.arange(2,6)**k for k in range(4)])@cubic,
                   stores.groupby('lead_days').baseline_rate.mean())''',
5:'''# Verify the omitted-variable identity on a fixed sample.
stores = world()['stores']
x = stores.lead_days.to_numpy()
y = stores.baseline_rate.to_numpy()
short_X = np.column_stack([np.ones(len(x)), x])
long_X = np.column_stack([np.ones(len(x)), x, stores.urban])
short, _, _ = fit_ols(short_X, y)
long, _, _ = fit_ols(long_X, y)
sorting, _, _ = fit_ols(short_X, stores.urban)
assert np.isclose(short[1], long[1]+long[2]*sorting[1])''',
6:'''# Tune LASSO in expanding time windows; preprocessing stays inside each fit.
data = world()['panel'].query('3<=week<=16')
development = data.query('week<=13')
final_test = data.query('week>=14')
features = lesson_result(6)['features']
scores = []
for alpha in [.001, .01, .1, 1.]:
    errors = []
    for train_end, start, stop in [(7,8,9),(9,10,11),(11,12,13)]:
        training = development[development.week<=train_end]
        validation = development[development.week.between(start,stop)]
        candidate = make_pipeline(PolynomialFeatures(2,include_bias=False),
            StandardScaler(), Lasso(alpha=alpha,max_iter=10000))
        candidate.fit(training[features], training.stockout_rate)
        errors.extend(validation.stockout_rate-candidate.predict(validation[features]))
    scores.append((np.sqrt(np.mean(np.square(errors))),alpha))
chosen_alpha = min(scores)[1]
assert chosen_alpha == lesson_result(6)['depth']['alpha']
final_model = make_pipeline(PolynomialFeatures(2,include_bias=False),
    StandardScaler(), Lasso(alpha=chosen_alpha,max_iter=10000))
final_model.fit(development[features],development.stockout_rate)
final_errors = final_test.stockout_rate-final_model.predict(final_test[features])
assert np.isclose(np.sqrt(np.mean(final_errors**2)),lesson_result(6)['depth']['test_rmse'])''',
7:'''# Teaching reveal: recover the potential-outcome targets.
potential = world()['panel'].query("cohort=='Pilot' and 17<=week<=24")
potential = potential.groupby(['store_id','offer'])[['y0','y1']].mean().reset_index()
potential['reduction'] = 100*(potential.y0-potential.y1)/140
share = potential.offer.mean()
att = potential.loc[potential.offer==1,'reduction'].mean()
atu = potential.loc[potential.offer==0,'reduction'].mean()
ate = potential.reduction.mean()
assert np.isclose(ate,share*att+(1-share)*atu)
assert np.isclose(ate,lesson_result(7)['depth']['ate'])''',
8:'''# Keep within-stratum differences fixed and change target weights.
strata = lesson_result(8)['strata']
adopters = sum(g['offered'] for g in strata)
nonadopters = sum(g['control'] for g in strata)
ate = sum(g['reduction']*g['n']/50 for g in strata)
att = sum(g['reduction']*g['offered']/adopters for g in strata)
atu = sum(g['reduction']*g['control']/nonadopters for g in strata)
assert np.isclose(ate,lesson_result(8)['depth']['ate'])
assert np.isclose(att,lesson_result(8)['depth']['att'])
assert np.isclose(atu,lesson_result(8)['depth']['atu'])''',
9:'''# Estimate adoption propensities using only starting conditions.
w = world()
voluntary = w['panel'].query("cohort=='Voluntary' and 17<=week<=24")
v = voluntary.groupby(['store_id','offer']).stockout_rate.mean().reset_index()
v = v.merge(w['stores'][['store_id','lead_days','urban','baseline_rate']],
    on='store_id',validate='one_to_one')
covariates = ['lead_days','urban','baseline_rate']
model = make_pipeline(StandardScaler(),LogisticRegression(C=1.,max_iter=1000))
model.fit(v[covariates],v.offer)
propensity = model.predict_proba(v[covariates])[:,1]
v['logit'] = np.log(propensity/(1-propensity))
caliper = .2*v.logit.std(ddof=1)
controls = v[v.offer==0]
matched_effects = []
for adopter in v[v.offer==1].itertuples():
    # Numerically tied distances use the lowest store ID.
    closest = nearest_score_match(controls,adopter.logit)
    comparison = controls.loc[closest]
    if abs(comparison.logit-adopter.logit)<=caliper:
        matched_effects.append(comparison.stockout_rate-adopter.stockout_rate)
assert np.isclose(np.mean(matched_effects),lesson_result(9)['depth']['matching'][2]['estimate'])''',
10:'''# Verify that the interaction regression reproduces the four-mean contrast.
panel = world()['panel'].query("cohort=='Rollout' and 17<=week<=32")
periods = panel.assign(after=(panel.week>=25).astype(int))
periods = periods.groupby(['store_id','offer','after']).stockout_rate.mean().reset_index()
X = np.column_stack([np.ones(len(periods)),periods.offer,
    periods.after,periods.offer*periods.after])
beta, _, _ = fit_ols(X,periods.stockout_rate)
reduction = -beta[3]
assert np.isclose(reduction,lesson_result(10)['effect']['value'])'''
}

from lesson5_depth import CALCULATIONS
WORKED[5] = CALCULATIONS
