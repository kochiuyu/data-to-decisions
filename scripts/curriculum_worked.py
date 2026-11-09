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
assert np.isclose(correlation, lesson_result(2)['depth']['correlation'])''',
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
assert np.isclose(differences.mean(), lesson_result(3)['depth']['paired']['mean'])''',
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
assert np.isclose(smearing, lesson_result(4)['depth']['forms'][1]['smearing'])''',
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
