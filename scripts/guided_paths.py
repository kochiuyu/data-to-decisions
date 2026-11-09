"""Connected, decision-led stories for the middle reading route.

Each story follows one business problem. Technical generation rules and the
complete set of original teaching stops remain in the lesson appendix.
"""

def chapter(title, *paragraphs, headers=None, rows=None, caption=None):
    return dict(title=title, paragraphs=paragraphs, headers=headers, rows=rows, caption=caption)

STORY_CONTEXT = {
    1: (
        'A useful first conversation with the travelers would pin down the arrival date, room type, maximum walk, and cancellation requirement. Otherwise the analyst may optimize the spreadsheet and still recommend something nobody can book. These requirements also explain why the lowest visible nightly price is only a lead to investigate, not the answer to the manager’s request.',
        'The count trail creates a practical review queue. The single duplicate can be resolved by checking the offer identifier and date; the incomplete scoped records need either a corrected quote or an explicit exclusion. The team should keep both the raw file and the cleaned shortlist so that a late correction can be traced through the recommendation without rebuilding the logic from memory.',
        'A compact recommendation could show the preferred offer and two backups under the same eligibility rule. Put the comparable total beside the cancellation deadline and walk time, and note when each quote was checked. That format lets the booking team act quickly while preserving a defensible answer if the first offer disappears or a traveler changes the arrival date.'),
    2: (
        'The cap has two possible jobs: control average spend or make individual bookings easy to approve. A pooled mean helps with forecasting the total travel budget, while the proportion under the cap helps predict how often employees will need an exception. Finance and operations should agree which job the rule is meant to do before treating one statistic as the policy answer.',
        'Notice that Willow Bay contributes more quotes than Juniper Vale. If the firm pooled everything, the most common destination would dominate the headline. That may be appropriate for forecasting spend under the current travel mix, but it is poor evidence that the same cap works for every destination. The town-level percentages reveal where staff will feel the friction.',
        'The exception process has a cost too. A rule that saves a little on paper but repeatedly sends routine trips for approval can waste staff time and delay bookings. The manager could track exception frequency and the final paid price over the next quarter, then revisit the cap using the destinations employees actually visit rather than a static file of available quotes.'),
    3: (
        'The team should prepare the matched sheet so each product appears once with both quotes and a common quantity. A missing online quote is not a zero price; a different package size is not the same product. Those mundane checks protect the meaning of the paired difference and make it possible to explain the analysis to buyers who never see the statistical test.',
        'The interval is a range for the average difference under this sampling model, while the tolerance is a management judgment about what difference matters. Bringing the two together is more useful than reporting a p-value alone. The positive mean tells the manager which way the average quote leans; the variation across products warns against applying that direction blindly to every purchase.',
        'A workable purchasing process might automatically compare both channels for high-value or time-sensitive items, while allowing staff to use the more convenient channel for small routine purchases. The manager can measure the actual delivered cost and the time spent ordering in a short pilot. That turns a quote comparison into a policy test with a clear operational payoff.'),
    4: (
        'The manager should ask what a bad prediction costs. A forecast that is ten minutes late on a batch with a tight customer deadline may matter more than several small early predictions. That answer determines whether the team should optimize average accuracy, late-job frequency, or a combination. It also tells staff what safety margin to add when the forecast becomes a promise.',
        'The candidate curves should be compared using the same held-out batches and the same error definition. Here the best score differs only slightly from the line, so the manager should not mistake the lowest decimal for a major business gain. Plotting the misses against batch size can show whether the small average advantage hides a useful improvement for the largest jobs.',
        'The rollout can begin in shadow mode: let planners make their usual estimates, record the model forecast alongside them, and compare both with completion time. After enough new batches, management can decide whether the model improves deadline promises or staffing decisions. This protects the operation from changing schedules on the strength of a tidy but narrow validation result.'),
    5: (
        'The capital request should begin with a concrete return calculation: how many extra calibrated units per hour are needed to recover purchase and installation cost? Rigs near retirement have little time to earn that back, while frequently used rigs may benefit from even a modest gain. That turns a vague average-effect question into a choice about which assets deserve the first investment.',
        'Age adjustment is not a mechanical cleaning step. Because older rigs received fixtures more often, the unadjusted gap compares two different portfolios. The fuller model also allows the fixture difference to change with age rather than forcing one number onto all rigs. Managers can read that pattern as a set of scenarios for the budget, with each scenario tied to a rig age they actually operate.',
        'The pilot should preserve a fair comparison. If the best technicians and least troublesome rigs receive the new fixtures first, the next before-and-after report will again mix equipment with selection. A planned assignment among suitable rigs, consistent output measures, and a fixed follow-up period would make the investment review much more informative.'),
    6: (
        'A practical intake checklist makes the data boundary visible. Job size, route, and the forecast weather assumption may be known when a quote is requested; final billed amount and post-service status are not. A feature that looks accurate in a historical export can fail completely if it arrives after the quote. The team should label each input with its real availability time.',
        'Root-mean-square error describes the typical scale of misses while putting extra weight on large ones. It does not tell the whole commercial story: a 40-credit underquote and a 40-credit overquote may have very different consequences. The final test therefore supports a candidate procedure, but the pricing team still needs a margin rule and a review path for unusual jobs.',
        'A shadow deployment can compare proposed quotes, actual costs, win rates, and overrides without forcing dispatchers to accept every forecast. The firm should set in advance what would count as an improvement: fewer damaging underquotes, acceptable customer retention, and manageable staff effort. That decision standard keeps the next evaluation tied to the business process rather than to a leaderboard metric.'),
    7: (
        'A rollout meeting should separate three groups that are easy to blur: teams offered the tool, teams that actually use it, and teams that would have performed well anyway. The last group cannot be identified from observed scores alone. Without that distinction, the firm might spend its budget on a tool that merely happened to reach its strongest teams first.',
        'Random assignment does not make every team identical; it makes the groups comparable in expectation before outcomes are seen. Managers should keep the assignment record even if some teams decline the offer, because changing groups after observing use would reintroduce selection. Adoption and ease of implementation are still useful secondary outcomes for planning a full rollout.',
        'The budget threshold should be written in the same units as the outcome: what gain per team would cover licenses, training and management attention? If a pilot misses that threshold, the firm can investigate whether the tool was poorly used or whether the benefit is simply too small. Either conclusion is more useful than treating the original user-versus-nonuser gap as a purchase order.'),
    8: (
        'The program office should map the sequence of events on one page: baseline need, offer, participation, intermediate behavior, and final outcome. That timeline helps a business audience see why adjusting for baseline need may help while adjusting for behavior caused by the program may answer a different question. It also exposes measurements that are missing for one group.',
        'Within each stratum, the analyst asks what happened to participants and comparable nonparticipants. The combined answer depends on which strata receive more weight. A network-wide expansion gives weight to all eligible units; a service improvement for current participants gives more weight to their mix. Making that choice visible prevents a technically correct estimate from answering the wrong budget question.',
        'The next action is to review the thin cells and the business reasons for program selection. If some eligible units have no credible comparison, the manager could pilot the program there rather than extrapolate an adjusted average. The analysis is most valuable when it clarifies where a decision is supported and where the organization should collect stronger evidence.'),
    9: (
        'The trial note should be written with operations staff, not just analysts. They know whether “coaching” meant the same activities at every facility, when staff first learned they were selected, and whether another initiative arrived at the same time. Those facts determine the intervention being evaluated and the start of follow-up long before a modeling choice matters.',
        'Standardization asks the model two questions for each facility: what outcome is predicted with coaching, and what is predicted without it? The difference is then averaged over the facilities in the proposed rollout. This makes the target tangible. It also makes missing comparison types visible: if no uncoached facility resembles a particular coached site, its second prediction rests mainly on extrapolation.',
        'The budget memo can show an estimated benefit per facility beside coaching cost and the number of sites with credible comparisons. A second phase could deliberately assign coaching among sites where the decision remains uncertain. That is a better use of scarce evaluation resources than polishing an adjusted estimate for facilities that never had a realistic alternative in the historical data.'),
    10: (
        'The operations timeline matters as much as the outcome table. Staff might have trained before the official start date, or comparison facilities might have copied the protocol informally. The director should ask when behavior actually changed, not only when the project plan says the rollout began. This prevents an apparently clean before-and-after window from hiding early exposure.',
        'The treated facilities improved by their own observed change, but the comparison facilities improved too. The second subtraction asks how much improvement remains after allowing for that wider movement. Presenting the four means lets managers challenge the calculation: they can see the starting gap, the two trends, and the exact contrast that supports the proposed effect.',
        'Before scaling, compare the estimated gain with the minimum improvement needed to cover training and disruption. Then inspect the most plausible alternative explanations: a staffing change at adopter sites, a shared supplier change, a copied practice among controls, or missing facilities after rollout. The decision can proceed in stages if those checks are reassuring, with new sites added under a recorded timetable.'),
}

def story(number, r):
    f = lambda x: f'{x:.2f}'
    q = r.get('quality', {})
    stories = {
        1: lambda: dict(
            chapters=[
                chapter('A booking request becomes a data question',
                    'A travel coordinator has to recommend a two-night stay for a visiting team. Finance wants a defensible total cost; the travelers also need a suitable room, an acceptable walk, and a refundable booking. The export looks like a price list, but each row is a quote for a property on a particular arrival date. Two rows with the same property name can be different offers.',
                    'The useful question is therefore not “Which number is smallest?” It is “Which eligible offer has the lowest comparable total, and what terms come with it?” That question determines the observation unit, the filters, and the cost calculation before anyone sorts the spreadsheet.'),
                chapter('Make the shortlist trustworthy',
                    f"The file begins with {q['raw']} rows. Checking the offer key removes one duplicate. The relevant market has {q['scoped']} rows, and {q['complete']} have the fields needed for a like-for-like comparison. The movement between these counts is part of the result: a manager should know which offers could not enter the shortlist.",
                    'For each remaining quote, the two-night total includes two room nights, the cleaning charge, and tax on both. A low nightly rate can lose its advantage once these terms are added. Joining a property table to a quote table also needs a key check: one-to-many matches can silently give a property several votes in a later average.',
                    headers=['Stage', 'Offers'], rows=[['Raw export', q['raw']], ['After duplicate check', q['deduplicated']], ['Relevant market', q['scoped']], ['Comparable offers', q['complete']]], caption='How the booking shortlist changes'),
                chapter('Send a recommendation someone can act on',
                    'The coordinator can now rank the comparable offers and present a short list with total cost, date, cancellation terms, and travel time. An excluded quote should stay in the audit trail, not disappear without explanation. If the cheapest eligible option is unavailable when booking begins, the same rule can be applied to the next option.',
                    'The practical handoff is a choice rule, not just a winning row: verify the live quote and terms, select the lowest total among offers that meet the team’s requirements, and record why any cheaper-looking row was rejected. That makes the recommendation repeatable when prices change.'),
            ],
            question='A manager asks why the report ranks only 37 offers when the export had 61 rows. What should the coordinator show?',
            answer='Show the row-count trail, the offer key, the eligibility rule, and the full two-night cost definition. Those explain which 37 offers were comparable and why.'),
        2: lambda: dict(
            chapters=[
                chapter('A single cap must serve different trips',
                    'A company proposes a 140 CU lodging cap for staff trips. A quick answer would compare the cap with the overall average price. That is attractive because it yields one number for finance, but a traveler needs an available offer under the cap in the town they actually visit. The relevant outcome is the share of usable quotes within budget, not only the mean.',
                    f"The generated file contains {r['n']} quotes. Its mean is {f(r['summary']['mean'])} CU and its median is {f(r['summary']['median'])} CU. Both are below 140, yet the upper tail still contains expensive offers. Before adopting the cap, the travel manager should ask how the distribution changes across destinations."),
                chapter('Look at the travelers’ destinations',
                    'The towns have different numbers of quotes and different price distributions. Count the quotes under 140 within each town, then divide by that town’s own total. Using the full dataset as every denominator would make the smaller towns look artificially weak. The table gives a more useful operational picture than one company-wide average.',
                    'Willow Bay has many under-cap options; Cedar Reach has far fewer. The travel manager should use those differences to plan where routine bookings can follow the cap and where staff will need an exception path.',
                    headers=['Town', 'Quotes', 'Share at or below 140 CU'], rows=[[g['town'],g['n'],f"{100*g['proportion']:.1f}%"] for g in r['groups']], caption='Budget coverage by destination'),
                chapter('Write a policy that handles exceptions',
                    'Finance can keep 140 CU as a starting point, but it should not promise that every legitimate trip fits it. A useful policy could allow a documented exception when a destination has too few compliant offers or when the only low-price listings fail the room, time, or cancellation requirements.',
                    'The report should show the cap, coverage by town, and the cost of an exception process. It should also name the mix of destinations used to produce the overall figure. If the company’s trips shift toward Cedar Reach, the current average will describe the wrong workload even if the arithmetic remains correct.'),
            ],
            question='Why can a company-wide average below 140 CU still produce frequent exception requests?',
            answer='Prices vary within and across towns. The cap must be judged against the share of eligible offers in each destination, not only the pooled mean.'),
        3: lambda: dict(
            chapters=[
                chapter('A channel rule sounds simpler than it is',
                    'A purchasing manager wonders whether staff should buy products online or offline. Comparing all online quotes with all shop quotes would mix different products. Instead, the team collects both quotes for the same 40 products at the same time and defines the difference as online minus offline. Product matching turns the question into a comparison the manager can understand.',
                    'The manager also sets a practical tolerance. A difference smaller than 1.50 CU per product would not by itself justify changing the purchasing process. This threshold comes from the decision, before looking at the estimated gap.'),
                chapter('Read the difference, not just the test',
                    f"The sample’s average paired difference is {f(r['paired']['mean'])} CU. Its 95% interval runs from {f(r['paired']['low'])} to {f(r['paired']['high'])} CU. The interval excludes zero, so this model detects a positive average gap; it also lies inside the manager’s 1.50 CU tolerance. Those statements answer different questions and can both be true.",
                    f"Individual products do not all follow the average. The generated differences range from {f(r['paired']['min'])} to {f(r['paired']['max'])} CU. A purchasing rule based only on the mean would miss products with a much larger channel advantage in either direction.",
                    headers=['Comparison', 'CU per product'], rows=[['Average online minus offline',f(r['paired']['mean'])],['95% interval, lower end',f(r['paired']['low'])],['95% interval, upper end',f(r['paired']['high'])],['Manager’s tolerance', '±1.50']], caption='Paired quote comparison'),
                chapter('Decide what changes in purchasing',
                    'A blanket “always buy offline” rule is too strong for this evidence. The manager can retain both channels, compare the full delivered cost for costly items, and check availability, returns, and staff time. If one channel offers operational benefits, an average quote difference within the tolerance may be an acceptable trade.',
                    'For a real rollout, the team would first verify product identity, package size, taxes, shipping, and quote timing. The immediate lesson is that a statistically detectable mean difference is a starting point for a cost decision, not the decision itself.'),
            ],
            question='Would an average gap of 0.79 CU justify forcing every product through one channel?',
            answer='No. The chosen tolerance, product-level variation, delivery costs, availability, and process costs all matter. Keep the rule conditional on the full cost of each purchase.'),
        4: lambda: dict(
            chapters=[
                chapter('The workshop needs a planning number',
                    'A workshop manager must promise completion times before the next batch arrives. Batch size is visible when a job is booked, so it is a useful forecasting input. A straight line offers a simple staffing rule: in this sample it adds about '+f(r['b'][1])+' minutes for each unit of batch size. That is easy to explain, but the manager cares about missed deadlines, not the elegance of the line.',
                    'The operations team plots completion time against size and checks the prediction errors. The pattern bends as batches grow, and the spread widens. A single slope summarizes the observed range but cannot describe every size equally well.'),
                chapter('Compare useful forecasts on new batches',
                    'The team compares candidate curves on batches held back during development. The hinge model has the lowest error, but its advantage over a straight line is small. The manager can now weigh that gain against the effort of maintaining a more complex scheduling rule.',
                    'The scores are measured in minutes of root-mean-square error, which gives large misses extra weight. If late jobs are especially costly, the manager should also inspect the worst misses and add a practical buffer rather than relying on the average error alone.',
                    headers=['Forecast rule', 'Held-out error, minutes'], rows=[[v['model'].title(),f(v['cv_rmse'])] for v in r['validation']], caption='Forecast accuracy on held-out development batches'),
                chapter('Turn the model into a scheduling rule',
                    'The manager can use a size-based forecast for batches within the observed size range, with a stated buffer for deadline promises. If a new batch is much larger than anything in the training set, it should trigger a manual review rather than a mechanically extrapolated promise.',
                    'A simple rule may be preferable when more flexible models improve error by only a few seconds and make the process harder to maintain. The decision memo should say what size range was tested, what error measure was used, and when staff should override the forecast.'),
            ],
            question='What would justify adopting a more complicated forecast than the straight line?',
            answer='A meaningful improvement on new batches or on costly late jobs, within the size range the workshop expects to handle.'),
        5: lambda: dict(
            chapters=[
                chapter('Should the firm buy powered fixtures?',
                    'A calibration manager sees higher output from rigs with powered fixtures and considers a wider purchase. The first comparison is tempting: fixture rigs produce about '+f(r['short'][1])+' more units per hour on average. But older rigs are more likely to have the fixture, and service age also relates to output. Buying equipment for every rig on the strength of the raw gap would confuse the equipment decision with the mix of rigs that already use it.',
                    'The manager therefore asks a narrower question: for rigs of similar age and operating conditions, how much output difference is associated with the fixture? This is the comparison needed for a targeted investment case.'),
                chapter('The answer changes with the comparison',
                    'A simple age-adjusted comparison is '+f(r['add'][1])+' units per hour, much smaller than the raw gap. A fuller model allows the fixture difference to change with service age; at six years its fitted difference is '+f(r['contrasts'][1][1])+' units per hour. These are three summaries of different questions, not three votes to average together.',
                    'The age pattern matters commercially. A fixture that is useful for an older rig may offer a different return on a newer one. The budget calculation should combine age-specific expected output with equipment price, downtime for installation, maintenance, and the remaining life of each rig.',
                    headers=['Comparison', 'Estimated units per hour'], rows=[['Raw fixture gap',f(r['short'][1])],['Simple age-adjusted gap',f(r['add'][1])],['Full-model gap at six years',f(r['contrasts'][1][1])]], caption='Why a fixture decision needs a specified comparison'),
                chapter('Recommend a staged investment',
                    'The manager should not turn one average coefficient into a universal purchase order. A sensible next step is a small, measured rollout among rig ages where the expected gain could repay the cost. Record output before and after installation, maintenance interruptions, and the assignment rule.',
                    'That pilot would answer a stronger operational question than the existing comparison alone. The current analysis is still valuable: it narrows the likely range of returns and shows which rig characteristics must be carried into the investment plan.'),
            ],
            question='Which rigs should be considered first for a pilot?',
            answer='Those for which the age-specific expected output gain could plausibly cover installation, maintenance, downtime, and remaining-life costs.'),
        6: lambda: dict(
            chapters=[
                chapter('A forecast becomes a quote',
                    'A dispatch firm must quote a job before it knows the final service cost. Underquoting an expensive job hurts margin; overquoting every job loses customers. The dispatcher can see job size and other intake information, but cannot use details recorded after the work is finished. The prediction rule has to work at the moment a quote is made.',
                    'The team sets aside a final group of jobs before choosing a model. It then tries several complete procedures on development data, including how missing inputs are filled, how variables are scaled, and how the predicted cost is brought back to credits. Keeping those choices inside each training fold makes the practice evaluation resemble a future quote.'),
                chapter('Judge the procedure on untouched jobs',
                    f"On the final {r['test_n']} generated jobs, a simple mean-cost baseline has root-mean-square error {f(r['final_scores'][0][1])} credits. The frozen selected procedure has error {f(r['final_scores'][1][1])} credits. The model earns attention because it improves a measure that penalizes large misses, not because its coefficient list looks impressive.",
                    'The dispatcher still needs to look at costly jobs separately. One average score can hide a pattern of underquoting the jobs that matter most to margin. A quote policy can pair the forecast with a review threshold for unusually large or poorly supported jobs.',
                    headers=['Frozen procedure', 'Final error, credits'], rows=[[v[0],f(v[1])] for v in r['final_scores']], caption='Prediction error on jobs not used for model choice'),
                chapter('Put boundaries around the quote rule',
                    'The firm can test the model in a limited quoting workflow, record actual margins, and check whether staff override it for sensible reasons. It should define a fallback for missing or unusual inputs and monitor the expensive tail, not simply announce a new accuracy percentage.',
                    'Next year’s jobs may have different routes, weather, prices, or customer mix. A calendar-based follow-up test will tell management more about deployment than another random split of the same generated world. The present result supports a controlled trial of the procedure, with clear monitoring and a human review path.'),
            ],
            question='What should happen when a new job is unlike the jobs used to develop the forecast?',
            answer='Flag it for review or a conservative fallback. A strong average test score does not validate unsupported jobs.'),
        7: lambda: dict(
            chapters=[
                chapter('A popular tool appears to work',
                    'A team-performance manager sees that teams using a new tool score much higher than teams that do not. The observed gap is '+f(r['observed_gap'])+' outcome units, large enough to make a rollout sound obvious. Yet managers chose which teams received the tool. High-performing teams may have been more likely to adopt it in the first place.',
                    'The business question is not whether users outperform nonusers. It is whether offering the tool changes outcomes enough to justify its cost. That question needs an action, a time window, a stable team unit, and a measure of performance that would matter to management.'),
                chapter('Separate selection from improvement',
                    'The observed gap contains two pieces: how recipients would have performed without the tool, and what the tool changed for them. The case lets the manager separate those pieces. The large user-versus-nonuser gap shrinks once selection is accounted for, changing the purchase discussion.',
                    'For an actual decision, the manager would assign the offer randomly among eligible teams, keep usual operations as the comparison, and measure the same outcome over the same period. The primary result would compare teams by offer, including those that barely use the tool; usage can be studied separately.'),
                chapter('Run a pilot tied to the budget',
                    'A pilot should name the minimum gain that repays license fees, training time, and workflow disruption. If the expected gain is smaller than that threshold, a statistically positive result may still be a poor purchase. If the gain clears it, management can expand gradually while checking whether the tool works for teams outside the pilot.',
                    'The pilot record needs the assignment list, dates, adoption rates, outcome definition, and reasons for missing teams. Without those practical details, a clean-looking difference could be hard to interpret or repeat.'),
            ],
            question='What does the 15-unit user-versus-nonuser gap leave unresolved?',
            answer='It does not show how much the tool changed recipients’ outcomes. Team selection contributed to the gap.'),
        8: lambda: dict(
            chapters=[
                chapter('A program is offered to different kinds of units',
                    'A manager is asked whether an existing program should be expanded. Program participants do better than nonparticipants by '+f(r['raw_gap'])+' units. But participation was not assigned at random: the groups have different starting characteristics. Comparing their final averages would mix program performance with the reasons they entered the program.',
                    'The manager first draws a simple causal story. Which characteristics existed before the offer and could affect both selection and outcome? Which measurements were produced after participation began? This ordering is more useful than feeding every available column into a regression.'),
                chapter('Make like-for-like comparisons',
                    'The team groups eligible units by pre-program characteristics where both participants and nonparticipants appear. It calculates a within-group difference, then combines those differences using weights for the population the expansion decision concerns. The resulting standardized average is '+f(r['standardized']['ATE'])+' units, much smaller than the raw gap.',
                    'Those weights are a business choice as well as a statistical one. A program meant for all eligible units needs a different mix from a program meant only for current participants. Thin comparison cells should be shown to the manager rather than hidden inside one reassuring adjusted number.',
                    headers=['Comparison', 'Outcome units'], rows=[['Raw participant gap',f(r['raw_gap'])],['Standardized all-unit estimate',f(r['standardized']['ATE'])]], caption='How the comparison changes after accounting for starting mix'),
                chapter('Use the graph to challenge the result',
                    'The causal diagram explains why a good predictor is not always a good control. If a variable is a consequence of participation, adjusting for it can remove part of the program’s effect. If it is a common consequence of two earlier causes, adjustment can create a false association. The point of the diagram is to make these choices discussable before the result is known.',
                    'For the expansion memo, report the adjusted comparison, the target population, and the strata with weak overlap. Then identify one plausible unmeasured reason for selection that would most change the recommendation. That is a more useful next investigation than adding controls simply to improve fit.'),
            ],
            question='Why not include every variable that predicts the outcome?',
            answer='Some variables occur after the program or are common consequences of other causes. Their timing and causal role determine whether adjustment helps.'),
        9: lambda: dict(
            chapters=[
                chapter('A coaching program looks promising',
                    'A service network gave process coaching to selected facilities. Coached sites average '+f(r['raw_gap'])+' outcome units above uncoached sites. The director wants to fund a wider rollout, but the facilities were chosen partly because of their starting conditions. The director needs the gain coaching would produce for a defined set of eligible facilities, not the difference between two existing lists.',
                    'Before fitting a model, the analyst writes down the trial they would have preferred: eligibility, coaching start date, comparison facilities, outcome window, and what counts as the coaching package. That design note prevents later choices from being made only because they yield an attractive result.'),
                chapter('Predict both options for the same facilities',
                    'The analyst uses pre-coaching characteristics to predict each facility’s outcome under coaching and under no coaching, then averages the predicted differences over the target population. In this generated case, that standardized estimate is '+f(r['regression']['ate'])+' units. It is more relevant to the rollout question than the raw '+f(r['raw_gap'])+'-unit gap.',
                    'The analyst marks facility types that appear in both groups and reports how many sites fall outside that shared range. That gives the director a clear rollout boundary and identifies where a planned pilot would add the most information.',
                    headers=['Comparison', 'Outcome units'], rows=[['Raw coached–uncoached gap',f(r['raw_gap'])],['Standardized all-facility estimate',f(r['regression']['ate'])]], caption='From a group gap to a defined rollout target'),
                chapter('Decide what evidence to buy next',
                    'The director can compare the estimated gain with the cost of coaches, staff time, and disruption, while reserving resources for a stronger follow-up. A limited rollout with a recorded assignment rule would be more informative than another round of retrospective adjustment.',
                    'The memo should distinguish two questions: whether coaching helped facilities like those already coached, and whether it would help every eligible facility. Different target mixes produce different answers when effects vary. The practical recommendation should name which population the budget actually covers.'),
            ],
            question='Why is the adjusted all-facility estimate a better starting point for network-wide expansion than the raw group gap?',
            answer='It compares predicted coached and uncoached outcomes for the same target mix, instead of comparing groups selected under different starting conditions.'),
        10: lambda: dict(
            chapters=[
                chapter('Performance rose after a rollout',
                    'A service network introduced a scheduling protocol at selected facilities. Their performance rose, and the operations director wants to know whether the protocol deserves expansion. A before–after improvement alone is not enough: staffing, demand, or the wider network may have improved at the same time.',
                    'The analyst gathers outcomes for the same adopting and comparison facilities before and after the common rollout date. The comparison facilities supply a picture of the change adopters might have experienced without the protocol. They do not need identical starting levels, but they need a plausible common untreated trend.'),
                chapter('Subtract the change that was already happening',
                    f"Adopters move from {f(r['means']['treated_pre'])} to {f(r['means']['treated_post'])} points. Comparison facilities move from {f(r['means']['control_pre'])} to {f(r['means']['control_post'])}. Subtracting the latter change from the former gives a difference-in-differences estimate of {f(r['did'])} points.",
                    'The four-cell table is the calculation the director should be able to reconstruct. Its value is that it removes a stable starting gap and the change shared by both groups. It would not remove a new event that affected only adopters, such as a simultaneous staffing initiative.',
                    headers=['Facilities', 'Before', 'After', 'Change'], rows=[['Adopters',f(r['means']['treated_pre']),f(r['means']['treated_post']),f(r['treated_change'])],['Comparison',f(r['means']['control_pre']),f(r['means']['control_post']),f(r['control_change'])]], caption='Performance before and after the scheduling rollout'),
                chapter('Check the rollout story before scaling',
                    'The director should verify when preparation actually began, whether comparison sites copied the new practice, and whether the same facilities remain in the report. A pre-period chart helps the team judge whether the comparison sites followed a similar path before rollout.',
                    'If the timing and comparison survive that review, the estimate can inform a staged expansion alongside implementation cost and a minimum useful gain. If a concurrent change or spillover is found, the next action is to redesign the comparison, not to interpret the same number more confidently.'),
            ],
            question='What business event would most threaten this before–after comparison?',
            answer='A change affecting adopters at the rollout date but not comparison facilities, such as a separate staffing or technology initiative.'),
    }
    result=stories[number]()
    for section, paragraph in zip(result['chapters'], STORY_CONTEXT[number], strict=True):
        section['paragraphs'] += (paragraph,)
    return result
