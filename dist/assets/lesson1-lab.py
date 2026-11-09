"""Original synthetic lab: data preparation. No network or external files.
Seed 41021. Invented lodgings, towns, teams and managers. Currency is fictional CU.
Prices, fixture scores and service totals are authored simulation assumptions,
not fitted to external observations. Python 3 with numpy and pandas.
"""
import json
import numpy as np
import pandas as pd
rng=np.random.default_rng(41021)
# 1. Define a row: a two-night quote for one lodging on one arrival date.
# The latent base price is uniform 65..155 CU; quote noise has SD 9 CU.
records=[]
for i in range(30):
    base=rng.uniform(65,155)
    for date in ['2030-04-10','2030-04-17']:
        records.append(dict(lodging_id=f'L{i+1:03d}',arrival=date,
          town=['Willow Bay','Cedar Reach','Juniper Vale'][i%3],
          kind='Hotel' if i%5 else 'Guesthouse',
          room='Private' if i%7 else 'Shared',
          nightly_cu=round(max(1,base+rng.normal(0,9)),2),
          cleaning_cu=float([0,12,24][i%3]),tax_rate=.08,
          refundable=bool(i%2),rating=[2,3,4,5][i%4]))
raw=pd.DataFrame(records)
raw.loc[9,'nightly_cu']=np.nan
raw.loc[22,'nightly_cu']=np.nan
raw.loc[35,'nightly_cu']=-15.0
raw=pd.concat([raw,raw.iloc[[4]]],ignore_index=True) # known ingestion duplicate
# Keep defects visible: exact duplicates can be removed, but no price is imputed.
unique=raw.drop_duplicates().copy()
invalid=unique.nightly_cu.le(0)
unique.loc[invalid,'nightly_cu']=np.nan
scoped=unique.loc[unique.kind.eq('Hotel') & unique.room.eq('Private')].copy()
complete=scoped.dropna(subset=['nightly_cu']).copy()
complete['two_night_total_cu']=(2*complete.nightly_cu+complete.cleaning_cu)*1.08
assert not unique.duplicated(['lodging_id','arrival']).any()
# 2. Key-safe feature join: one dimension row per lodging, many quotes per lodging.
features=pd.DataFrame({'lodging_id':[f'L{i+1:03d}' for i in range(30)],
                       'walk_minutes':rng.integers(4,31,30)})
joined=complete.merge(features,on='lodging_id',validate='many_to_one',indicator=True)
assert joined._merge.eq('both').all() and len(joined)==len(complete)
bad_features=pd.concat([features,features.iloc[[1]]],ignore_index=True)
bad_join=complete.merge(bad_features,on='lodging_id',how='left')
# 3. Wide/long layouts: the missing Juniper-Q3 cell means unrecorded, not zero.
service=pd.DataFrame({'town':['Willow Bay','Cedar Reach','Juniper Vale'],
                     'Q1':rng.integers(70,130,3),'Q2':rng.integers(70,130,3),
                     'Q3':[int(rng.integers(70,130)),int(rng.integers(70,130)),np.nan]})
long=service.melt(id_vars='town',var_name='quarter',value_name='requests')
assert not long.duplicated(['town','quarter']).any()
wide=long.pivot(index='town',columns='quarter',values='requests')
# 4. Fixtures are events. Turn each into two team-level observations before grouping.
# Draw goals independently with Poisson mean 1.4. No real fixture is represented.
teams=['Aster','Bracken','Clover','Dahlia']
fixtures=[]
for week in range(12):
    pairs=[(0,1),(2,3)] if week%3==0 else ([(0,2),(1,3)] if week%3==1 else [(0,3),(1,2)])
    for a,b in pairs:
        ga,gb=map(int,rng.poisson(1.4,2))
        fixtures.append(dict(date=(pd.Timestamp('2030-01-05')+pd.Timedelta(days=7*week)).strftime('%Y-%m-%d'),home=teams[a],away=teams[b],hg=ga,ag=gb))
fixtures=pd.DataFrame(fixtures)
team_rows=[]
for j,r in fixtures.iterrows():
    for team,goals,against in [(r.home,r.hg,r.ag),(r.away,r.ag,r.hg)]:
        team_rows.append(dict(fixture_id=f'F{j+1:02d}',date=r.date,team=team,
                              points=3 if goals>against else 1 if goals==against else 0))
games=pd.DataFrame(team_rows)
# Half-open tenures [start,end): the new manager owns the boundary date.
tenures=[]
for i,team in enumerate(teams):
    tenures.extend([dict(team=team,manager=f'{team} North',start='2030-01-01',end='2030-02-16'),
                    dict(team=team,manager=f'{team} South',start='2030-02-16',end='2031-01-01')])
tenures=pd.DataFrame(tenures)
candidates=games.merge(tenures,on='team')
assigned=candidates.loc[(candidates.date>=candidates.start)&(candidates.date<candidates.end)].copy()
assert len(assigned)==len(games) and not assigned.duplicated(['fixture_id','team']).any()
summary=assigned.groupby(['team','manager']).agg(games=('points','size'),observed=('points','count'),total=('points','sum'),ppg=('points','mean')).reset_index()
# Weighted and unweighted summaries differ when groups have unequal exposure.
summary=summary.sort_values(['ppg','manager'],ascending=[False,True])
# A deliberately unbalanced toy comparison makes denominator logic transparent.
toy_n=np.array([2,8]);toy_total=np.array([6,8]);toy_means=toy_total/toy_n

def clean_records(df): return json.loads(df.to_json(orient='records'))
out={'seed':41021,'synthetic':True,
 'assumptions':['Fictional currency CU','Two nights, one room, tax applied to room plus cleaning','Poisson fixture goals with mean 1.4','No empirical calibration'],
 'quality':{'raw':len(raw),'deduplicated':len(unique),'duplicates_removed':len(raw)-len(unique),'initial_missing':int(raw.nightly_cu.isna().sum()),'invalid_nonpositive':int(invalid.sum()),'scoped':len(scoped),'complete':len(complete),'excluded_missing_in_scope':len(scoped)-len(complete),'unsafe_join_rows':len(bad_join),'safe_join_rows':len(joined)},
 'raw_excerpt':clean_records(raw.iloc[[1,4,9,22,35,60]]),
 'offers':clean_records(joined.drop(columns='_merge').sort_values('two_night_total_cu').head(6)),
 'town_summary':clean_records(complete.groupby('town').agg(n=('two_night_total_cu','size'),mean=('two_night_total_cu','mean'),median=('two_night_total_cu','median')).reset_index()),
 'service_wide':clean_records(service),'service_long':clean_records(long),
 'trace':int(service.loc[service.town.eq('Willow Bay'),'Q2'].iloc[0]),
 'fixtures':clean_records(fixtures.head(2)),'assigned_excerpt':clean_records(assigned[(assigned.team=='Aster') & assigned.date.isin(['2030-02-09','2030-02-16'])][['fixture_id','date','team','manager','points']]),
 'fixtures_n':len(fixtures),'team_rows_n':len(games),'candidate_rows_n':len(candidates),
 'manager_summary':clean_records(summary),'eligible':clean_records(summary.loc[summary.games.ge(6)]),
 'toy':{'n':toy_n.tolist(),'totals':toy_total.tolist(),'means':toy_means.tolist(),'weighted':float(toy_total.sum()/toy_n.sum()),'unweighted':float(toy_means.mean())}}
print(json.dumps(out,allow_nan=False))
