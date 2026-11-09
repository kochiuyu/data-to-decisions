"""Short, decision-led route through the ten synthetic lessons.

The detailed derivations and complete generators live on each lesson's appendix page.
Numbers below come from the matching saved lab result, not hand-entered output.
"""

def case(number, r):
    f = lambda value: f'{value:.2f}'
    cases = {
        1: lambda r: dict(
            question='Which lodging offer can we recommend with confidence?',
            evidence=f"The fictional file starts with {r['quality']['raw']} offer rows. After checking the key, defining the relevant market and removing incomplete scoped records, {r['quality']['complete']} comparable offers remain.",
            decision='Compare the full two-night cost for offers that meet the same requirements. Record every exclusion before ranking. A cheaper row is not automatically a better or even a valid offer.',
            prompt='If a join creates more rows than either source table, should the manager trust the resulting ranking?',
            answer='No. Check the join keys and row counts first. Duplicate matches can change prices, weights and rankings.',
            truth='The generator deliberately includes one duplicate and three incomplete records in the selected market. Those are known teaching facts, not discoveries about real hotels.',
            generator='A fixed-seed script creates fictional lodging attributes, prices, dates and data-quality defects. It defines the two-night total as two room nights plus cleaning, with tax on both. A separate fixture case illustrates joins and denominators.'),
        2: lambda r: dict(
            question='What budget covers a useful share of lodging offers?',
            evidence=f"Among {r['n']} fictional prices, the sample mean is {f(r['summary']['mean'])} CU and the median is {f(r['summary']['median'])} CU. The difference points to a right tail: a single typical-price number hides some costly offers.",
            decision='Show a distribution and the share below the proposed budget for each town. State the denominator. Do not turn a descriptive association into a claim that changing town causes a price change.',
            prompt='Would the overall mean alone be enough to set a travel budget?',
            answer='No. The tail, the proportion under the budget and the mix of towns matter to the decision.',
            truth='The script specifies how these fictional prices and group labels are drawn. The displayed mean and median are realized sample summaries, not population constants or real-market estimates.',
            generator='A fixed-seed generator draws fictional lodging prices and group attributes, then creates separate probability and firm-association examples. The appendix identifies which mechanism belongs to each case.'),
        3: lambda r: dict(
            question='Is the average online quote meaningfully different from the matched offline quote?',
            evidence=f"For {r['paired']['n']} fictional matched products, online minus offline averages {f(r['paired']['mean'])} CU. The model-based 95% interval is {f(r['paired']['low'])} to {f(r['paired']['high'])} CU.",
            decision='Match the same product at the same time, then judge the interval against a decision-relevant cost difference. A detectable average does not mean every product is cheaper in one channel.',
            prompt='Does an interval above zero prove that all online quotes are higher?',
            answer='No. It concerns the population average under the model; individual paired differences vary in both directions.',
            truth='The paired-difference generator sets the population mean to 0.45 CU. The observed average differs because this is one random sample. The other cases in this lesson have separate generators and targets.',
            generator='The retail case draws independent normally distributed product differences with mean 0.45 CU and SD 1.55 CU, then adds varying base prices to both channels. Separate generators create the index, waiting-time and quality-check examples.'),
        4: lambda r: dict(
            question='How should a workshop forecast completion time for a new batch?',
            evidence=f"A straight-line fit estimates {f(r['b'][1])} additional minutes per unit of batch size in this sample. Its strong in-sample fit does not establish that the same slope applies at every batch size.",
            decision='Inspect the curve and residuals, then compare candidate forecasts on held-out data. Choose the level of complexity that improves the decision, not merely the training score.',
            prompt='Does a high in-sample fit make the line a reliable forecast for very large batches?',
            answer='No. The generating mean bends, and prediction beyond the observed size range needs a separate argument.',
            truth='The generator uses a curved mean completion-time function with noise that grows with batch size. The single fitted slope is an approximation, not a true constant effect.',
            generator='Batch size is drawn between 1 and 16. Mean minutes equal 20 + 5 × size + 0.18 × size² + 5 × sin(size/3); random noise grows with size. Other transformation examples are separate simulations.'),
        5: lambda r: dict(
            question='Do powered fixtures improve calibration output across service ages?',
            evidence=f"The unadjusted fixture comparison is {f(r['short'][1])} units per hour. After a simple service-age adjustment it is {f(r['add'][1])}. The change shows why the comparison group matters.",
            decision='Compare rigs of similar age and bench setting, and allow the fixture difference to vary with age. Report an effect for a specified rig rather than one universal number.',
            prompt='Can the difference between the two fitted coefficients automatically be called bias?',
            answer='No. The models ask different conditional questions; a causal bias claim also needs an assignment and measurement argument.',
            truth='In the generator, the fixture difference is 5 units per hour at six years of service and changes by 1.1 units for each additional year. One fitted coefficient need not equal that whole effect function.',
            generator='The script draws service age, fixture assignment, tool setting and bench type. Fixture use is more likely for older rigs. Generated output includes curvature, interactions, bench offsets and age-dependent noise. A separate simple normal model teaches intervals.'),
        6: lambda r: dict(
            question='Which dispatch-cost forecast is useful for future jobs?',
            evidence=f"On the untouched fictional test set, the simple baseline has root-mean-square error {f(r['final_scores'][0][1])} credits; the frozen selected procedure has {f(r['final_scores'][1][1])} credits.",
            decision='Choose the loss that matches costly mistakes, learn every preparation step within development data, and open the final test only after freezing the procedure. Monitor performance when conditions change.',
            prompt='Does a better score on one test set guarantee the model will win next year?',
            answer='No. It estimates performance in this generated setting. A future change in jobs, costs or measurement can reverse the ranking.',
            truth='The script controls the cost mechanism and can create a new population for a transport stress test. The final test score is still a finite-sample result, not a universal risk guarantee.',
            generator='A fixed-seed dispatch-cost model creates job features, missing values and noise. Candidate prediction pipelines are tuned on development folds; a separate held-out set evaluates the frozen procedure.'),
        7: lambda r: dict(
            question='Would offering a new team tool improve performance?',
            evidence=f"Teams that received the tool exceed others by {f(r['observed_gap'])} outcome units in the observed data. That raw gap mixes selection and treatment.",
            decision='Define who should receive the offer and what outcome matters. Random assignment, when feasible, makes the offered and usual-operation groups comparable on average.',
            prompt='Can the observed treated–untreated gap be reported as the tool effect?',
            answer='No. Teams were selected partly for characteristics related to their outcomes. The gap includes a baseline difference.',
            truth=f"The generator stores both potential outcomes. Its average effect among recipients is {f(r['att'])}; its average effect across all teams is {f(r['ate'])}. Those are different targets.",
            generator='The script creates both with-tool and without-tool outcomes for each fictional team, then reveals only the outcome under the assigned status to the analyst. Separate mini-rollout and advertising experiments illustrate random assignment.'),
        8: lambda r: dict(
            question='Can an observational comparison recover a program effect?',
            evidence=f"The raw group gap is {f(r['raw_gap'])} units. A comparison standardized across the generated strata estimates an average effect of {f(r['standardized']['ATE'])} units.",
            decision='Map the causal story before choosing controls. Compare people or units with enough overlap, and use weights that match the population of interest.',
            prompt='Should every variable that predicts the outcome be used as a control?',
            answer='No. A variable affected by treatment or a common consequence of treatment and outcome causes can distort the causal comparison.',
            truth=f"The generator's true average effect is {f(r['truth']['ATE'])}. The adjusted estimate is close in this authored world; that agreement does not validate the same adjustment in real data.",
            generator='The main case draws fictional strata with treatment selection and heterogeneous effects. Separate structural simulations create a confounder, a collider and a mediator so their different roles are visible.'),
        9: lambda r: dict(
            question='How much did a selected program help its eligible population?',
            evidence=f"The observed treated–control gap is {f(r['raw_gap'])} units. Regression standardization estimates an average effect of {f(r['regression']['ate'])} units after using measured pre-program characteristics.",
            decision='State the target population, check that comparable treated and untreated units exist, and test whether unmeasured selection could change the recommendation.',
            prompt='If adjusted groups look balanced, is the causal estimate proven?',
            answer='No. Balance covers measured variables. Hidden causes and weak overlap can still change the answer.',
            truth=f"The generated average effect is {f(r['truth']['ate'])}. The script can reveal it because it created both potential outcomes; an actual program evaluation cannot observe that truth directly.",
            generator='A fixed-seed model creates program selection, baseline outcomes and effects that vary by unit. The lab compares regression, matching and weighting, and separately changes hidden causes and the target population.'),
        10: lambda r: dict(
            question='Did a facility rollout improve performance beyond the trend already underway?',
            evidence=f"The treated group's before–after change minus the comparison group's change is {f(r['did'])} index points. The calculation removes a stable level gap, but depends on a credible untreated trend.",
            decision='Check rollout timing, comparison facilities, spillovers and changing participation before presenting the contrast as a policy effect.',
            prompt='Do similar pre-rollout trends prove that the groups would have moved together afterward?',
            answer='No. They can challenge a bad comparison, but the treated group’s post-rollout untreated path remains unobserved.',
            truth=f"The generator's average effect among adopters is {f(r['truth_att'])} points. The difference from the estimated contrast reflects this finite realization of untreated noise.",
            generator='Eighty fictional facilities are followed for eight periods. Adoption begins at period 4 for selected facilities. The generator creates common time effects, persistent facility differences, serial noise and effects that vary with baseline type.'),
    }
    return cases[number](r)
