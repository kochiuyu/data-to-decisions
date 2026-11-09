"""Worked technical bridges embedded in the middle reading route."""


def method(number, r):
    f = lambda value: f'{value:.2f}'
    q = r.get('quality', {})
    methods = {
        1: lambda: dict(
            anchor='comparison',
            setup='The unit is an offer for a property and arrival date. Check that its key is unique, restrict the file to the requested market, and require every charge needed for a total. Keep the counts at each step; they are the audit trail for the shortlist.',
            worked=f"{q['raw']} raw rows − {q['duplicates_removed']} duplicate = {q['deduplicated']} distinct offers; {q['scoped']} are in scope and {q['complete']} have complete prices. For each of those offers, comparable total = two room nights + cleaning + tax on both charges.",
            use='The ranking is calculated only after the eligible set and cost formula are fixed. A late quote correction can then change a price without silently changing what counts as an offer.'),
        2: lambda: dict(
            anchor='budget-decision',
            setup='The budget question is a proportion within each destination. Count quotes priced at or below 140 CU, then divide by all quotes in that same town. The town count, rather than the whole file, is the denominator travelers experience.',
            worked=f"Willow Bay: {r['groups'][0]['under']} ÷ {r['groups'][0]['n']} = {100*r['groups'][0]['proportion']:.1f}%. Cedar Reach: {r['groups'][1]['under']} ÷ {r['groups'][1]['n']} = {100*r['groups'][1]['proportion']:.1f}%.",
            use='The calculation turns a pooled price summary into a policy forecast: where will a 140 CU cap be routine, and where will it send bookings into the exception process?'),
        3: lambda: dict(
            anchor='paired-test',
            setup='For each product, subtract its shop quote from its online quote. Average those 40 paired differences. To quantify precision, divide the standard deviation of the differences by the square root of 40, then use a t multiplier for the interval.',
            worked=f"Standard error = {f(r['paired']['sd'])} ÷ √{r['paired']['n']} = {f(r['paired']['se'])} CU. The 95% interval is {f(r['paired']['mean'])} ± {f(r['paired']['critical'])} × {f(r['paired']['se'])}, or {f(r['paired']['low'])} to {f(r['paired']['high'])} CU.",
            use='The interval addresses the average paired gap. The manager then compares that range with the 1.50 CU change threshold and checks full delivered cost for individual purchases.'),
        4: lambda: dict(
            anchor='juniper-candidate-scores',
            setup='First fit the simple line from batch size to minutes. Then compare the line and more flexible candidates using batches withheld from each training fold. Every candidate is scored in minutes using the same root-mean-square error calculation.',
            worked=f"The fitted line is about {f(r['b'][0])} + {f(r['b'][1])} × batch size minutes. Held-out error is {f(r['validation'][0]['cv_rmse'])} minutes for the line and {f(next(v['cv_rmse'] for v in r['validation'] if v['model']=='hinge'))} for the hinge rule.",
            use='The hinge rule has the lower score, but the difference is small. Planners can compare that gain with the effort of maintaining the rule and the cost of late completion.'),
        5: lambda: dict(
            anchor='cedar-continuous-interaction',
            setup='The first comparison averages all fixture rigs against all other rigs. The adjusted analysis compares rigs at similar service ages; the fuller model also lets the fixture difference vary with age. The question for finance is the gain at ages in the purchase plan.',
            worked=f"Raw gap: {f(r['short'][1])} units per hour. Simple age-adjusted gap: {f(r['add'][1])}. In the fuller model, the fitted fixture difference is {f(r['contrasts'][0][1])} at age three, {f(r['contrasts'][1][1])} at age six, and {f(r['contrasts'][2][1])} at age nine.",
            use='These are different comparisons, not competing votes. An age-specific output gain can be placed beside installation cost, downtime, maintenance, and remaining useful life.'),
        6: lambda: dict(
            anchor='mica-final-lock',
            setup='Set aside the final jobs before choosing any model. On the development jobs, fit the entire procedure inside each training fold: missing-value handling, scaling, model choice, and return to the credit scale. After selecting the procedure, score it once on the held-out jobs.',
            worked=f"On {r['test_n']} final jobs, root-mean-square error = √(average squared forecast miss). The mean-cost baseline scores {f(r['final_scores'][0][1])} credits; the selected procedure scores {f(r['final_scores'][1][1])} credits.",
            use='This tests the complete quoting procedure, including preparation steps, on jobs it did not help select. The pricing team can then inspect underquotes and margins during a limited trial.'),
        7: lambda: dict(
            anchor='decomposition',
            setup='Define the treatment as an offer to an eligible team. The current user-versus-nonuser comparison combines the effect on recipients with their starting advantage. That is why a pilot should compare teams by assigned offer rather than by who chose to use the tool.',
            worked=f"Observed user gap = {f(r['observed_gap'])} outcome units. Conceptually, that gap = the tool’s gain for recipients + the difference those teams would have shown without it. A randomized offer aims to make the second component average out across groups.",
            use='Keep the assignment list, outcome window, and adoption record. The offer comparison answers the purchase question; adoption explains whether the proposed rollout can be delivered.'),
        8: lambda: dict(
            anchor='strata-calculation',
            setup='Divide the eligible population into pre-program groups where both participants and nonparticipants appear. Compute a participant-minus-nonparticipant gap inside each group. For a decision about all eligible units, weight each gap by that group’s share of the eligible population.',
            worked=f"Group gaps are {f(r['strata'][0]['gap'])}, {f(r['strata'][1]['gap'])}, and {f(r['strata'][2]['gap'])} units. Their population weights are {r['weights']['ATE'][0]:.1%}, {r['weights']['ATE'][1]:.1%}, and {r['weights']['ATE'][2]:.1%}; the weighted result is {f(r['standardized']['ATE'])} units.",
            use='The arithmetic makes the target visible. A program for current participants would reuse the group gaps but give them a different set of weights.'),
        9: lambda: dict(
            anchor='standardization',
            setup='Use only pre-coaching characteristics to model outcomes. For every facility in the proposed rollout, predict an outcome with coaching and another under usual operations. Subtract the two predictions for that same facility, then average those differences over the target facilities.',
            worked=f"The observed coached-minus-uncoached group gap is {f(r['raw_gap'])} units. Averaging the model’s paired predictions across all eligible facilities gives {f(r['regression']['ate'])} units; averaging over the already coached mix gives {f(r['regression']['att'])}.",
            use='The first adjusted number speaks to a network-wide budget. The second speaks to sites like current recipients. Naming the population keeps the model output tied to the director’s spending choice.'),
        10: lambda: dict(
            anchor='second-difference',
            setup='Keep the same adopters and comparison facilities in the before and after periods. Calculate each group’s change, then subtract the comparison change from the adopter change. That removes the common movement from the rollout contrast.',
            worked=f"Adopters change by {f(r['means']['treated_post'])} − {f(r['means']['treated_pre'])} = {f(r['treated_change'])} points. Comparison sites change by {f(r['means']['control_post'])} − {f(r['means']['control_pre'])} = {f(r['control_change'])}. The extra change is {f(r['treated_change'])} − {f(r['control_change'])} = {f(r['did'])} points.",
            use='The director can reconstruct the result from four averages, then review the rollout timeline and implementation cost before extending the protocol.'),
    }
    return methods[number]()
