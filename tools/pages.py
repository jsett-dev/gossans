#!/usr/bin/env python3
"""Content for the generated pages. Edit here, then run tools/build.py.

Each finding on the home page gets a page of its own. That is deliberate. The
home page has to sell, so it states each defect in three lines. A search engine
and a sceptical engineer both want the mechanism, the test and the fix, and
that does not fit on a sales page.
"""

CTA_LINE = (
    '<p style="margin-top:26px;"><a href="/contact/">An Asset Health Check</a> '
    "finds this one on a producing asset in two weeks, fixed fee.</p>"
)


def article(section_pairs):
    """Turn (rail label, rail sub, html) triples into the page body blocks."""
    out = []
    for label, sub, html in section_pairs:
        out.append(
            '  <div class="block">\n'
            '    <div class="rail"><b>%s</b><span>%s</span></div>\n'
            '    <div class="col prose">\n%s\n    </div>\n'
            "  </div>\n" % (label, sub, html)
        )
    return "\n".join(out)


FINDINGS = [
    {
        "slug": "decline-fitted-to-field-rate",
        "nav": "Decline fitted to field rate",
        "title": "Decline fitted to field rate instead of per-well rate",
        "description": (
            "Fitting an Arps decline to total field rate collapses the regression onto "
            "a straight exponential and misreads recovery by a factor. How the error "
            "happens, how to test for it, and how to fix the fit."
        ),
        "standfirst": (
            "Adding wells makes total rate rise. No decline curve can fit that, so the "
            "regression gives up and reports a straight exponential with a recovery "
            "estimate to match."
        ),
        "cost": "R&#178; falls from 0.98 to 0.15.<br>Recovery misread by a factor.",
        "sections": [
            ("Mechanism", "Why it happens", """
      <p>
        An Arps decline curve describes one well depleting one drainage volume.
        It assumes rate only ever falls. Field rate is not that. It is the sum of
        wells at different ages, and it steps upward every time a new well is
        turned to sales.
      </p>
      <p>
        Point a least-squares fit at that series and it has no good options. It
        cannot bend a decline curve upward, so it flattens the curve until the
        residuals on either side of the step roughly cancel. The hyperbolic
        exponent is driven to zero, which is a straight exponential, and the
        initial decline comes back far shallower than any individual well
        actually exhibits. The fitted curve is not a bad description of the
        reservoir. It is not a description of the reservoir at all.
      </p>
      <p>
        The reason it survives review is that the output still looks like a
        decline curve. It has an initial rate, a decline rate and a recovery
        number, all in the units everyone expects. Nothing about the printed
        answer says the regression failed.
      </p>"""),
            ("Detection", "Test your own model", """
      <p>
        Three checks, in order of how quickly they settle the question.
      </p>
      <p>
        <b>Look for the step.</b> Plot rate against time for the whole history
        and mark every date a well was turned to sales. If the rate rises after
        any of those dates, a single curve cannot fit the series and whatever was
        fitted to it is meaningless.
      </p>
      <p>
        <b>Ask for the quality measure.</b> A decline fit reported without its
        coefficient of determination is a decline fit somebody chose not to look
        at. Field-rate fits on a growing pad routinely land below 0.3. A clean
        per-well fit on the same data lands above 0.95.
      </p>
      <p>
        <b>Check the exponent.</b> If the hyperbolic exponent came back at
        exactly zero, or pinned to whichever bound the solver was given, the
        solver hit a wall rather than found an answer. Real tight oil wells sit
        near one, and often above it early in life.
      </p>"""),
            ("The fix", "What to do instead", """
      <p>
        <b>Normalise to rate per producing well.</b> Divide by the count of wells
        actually online in each month, not the count drilled. Adding wells then
        stops looking like a reservoir doing something impossible.
      </p>
      <p>
        <b>Segment at each step change.</b> Wells brought online two years apart
        are different vintages with different completions. Fit them separately
        and let the model add them, rather than asking one curve to describe
        both.
      </p>
      <p>
        <b>Drop the flowback month.</b> The first partial month is choked,
        cleaning up, and not on the depletion trend that governs the rest of the
        life.
      </p>
      <p>
        <b>Fit on the logarithm of rate.</b> Production spans two orders of
        magnitude across a well's life. A fit on raw rate is dominated by the
        first six months and effectively ignores the tail, which is exactly where
        the reserve lives.
      </p>
      <p>
        <b>Validate against something independent.</b> Build a type curve from
        offset wells in the same interval and compare recoveries. Agreement
        inside a few percent means the fit is describing rock rather than
        arithmetic.
      </p>""" + CTA_LINE),
        ],
    },
    {
        "slug": "decline-quoted-on-the-wrong-basis",
        "nav": "Decline quoted on the wrong basis",
        "title": "Decline quoted on the wrong basis",
        "description": (
            "Secant, tangent and nominal decline are three different numbers wearing "
            "the same label. Type curves are published one way and modelled another, "
            "and estimated ultimate recovery moves 15 to 25 percent."
        ),
        "standfirst": (
            "A seventy percent decline is three different numbers depending on how it "
            "was defined. Type curves are quoted one way and modelled another more "
            "often than not."
        ),
        "cost": "15&ndash;25% on estimated<br>ultimate recovery.",
        "sections": [
            ("Mechanism", "Three definitions, one label", """
      <p>
        Decline can be stated three ways, and they only agree when the curve is
        exponential, which a shale well never is.
      </p>
      <p>
        <b>Nominal decline</b> is the instantaneous rate of change, the parameter
        the hyperbolic equation actually consumes. <b>Tangent effective decline</b>
        is the annual drop implied by that instantaneous rate if it never
        changed. <b>Secant effective decline</b> is the plain observed drop from
        the rate today to the rate twelve months from now.
      </p>
      <p>
        Public type curves and investor decks almost always quote secant
        effective, because it is the one a non-specialist can check against a
        production plot. Reservoir software almost always consumes nominal. The
        conversion between them depends on the hyperbolic exponent, so it is not
        a constant you can memorise and it is not close to unity for a well with
        an exponent near one.
      </p>
      <p>
        Type a secant number into a field expecting nominal and the well declines
        too slowly for its whole life. Every year of the forecast inherits the
        error, and it compounds into the tail where most of the remaining reserve
        sits.
      </p>"""),
            ("Detection", "Test your own model", """
      <p>
        <b>Ask what basis the number is on.</b> If nobody can answer in one
        sentence, the conversion was not done. This single question resolves the
        issue more often than any amount of re-derivation.
      </p>
      <p>
        <b>Recompute the first year.</b> Take the fitted curve, integrate the
        first twelve months, and compare it against the first-year volume the
        type curve claims. If those two disagree, the parameter was entered on
        the wrong basis. This is a five-minute check and it is decisive.
      </p>
      <p>
        <b>Look for a conversion anywhere in the workbook.</b> In most
        spreadsheets there is no conversion step at all. The number was copied
        from a slide into a cell.
      </p>"""),
            ("The fix", "What to do instead", """
      <p>
        <b>Label the basis on every decline parameter, everywhere.</b> Not in a
        comment. In the field name. A parameter called <code>Di</code> tells you
        nothing; one called <code>Di_secant_effective</code> cannot be misused
        silently.
      </p>
      <p>
        <b>Convert once, at the boundary.</b> Take the published basis in at the
        edge of the model, convert immediately, and work in nominal everywhere
        inside. Conversions scattered through a workbook get applied twice as
        often as they get skipped.
      </p>
      <p>
        <b>Test the first-year volume automatically.</b> Any model worth keeping
        should assert that its own first-year output matches the type curve it
        was built from. That test catches this class of error permanently, and it
        catches it the day somebody changes the parameter rather than a year
        later.
      </p>""" + CTA_LINE),
        ],
    },
    {
        "slug": "capital-and-flush-production-in-the-same-period",
        "nav": "Capital and flush production in one period",
        "title": "Capital and flush production charged to the same period",
        "description": (
            "Annual models charge drilling capital and first-year flush production to "
            "the same period. Net present value comes out overstated and the peak "
            "funding requirement disappears entirely."
        ),
        "standfirst": (
            "A well spudded during a year does not produce for that whole year. "
            "Charging both to period one moves cash into exactly the period a discount "
            "rate rewards most."
        ),
        "cost": "14% overstatement of value.<br>Peak funding need hidden.",
        "sections": [
            ("Mechanism", "Two errors from one shortcut", """
      <p>
        An annual model has one bucket per year. Capital spent in that year goes
        in, revenue earned in that year comes out, and the difference is
        discounted from the midpoint. That is fine when the two are genuinely
        contemporaneous. For a drilling programme they are not.
      </p>
      <p>
        Between spud and first sales sit the drilling days, the completion, the
        frac crew queue and flowback. Several months, sometimes most of a year.
        The capital is certain and early. The production is later and declining
        from the moment it starts.
      </p>
      <p>
        Collapsing that into one bucket does two separate kinds of damage. It
        moves revenue earlier than it happens, into the period a discount rate
        weights most heavily, which inflates present value. And it nets the
        outflow against an inflow that had not arrived yet, which erases the peak
        funding requirement. Those two errors are read by different people.
        Finance sees the first. Treasury needed the second.
      </p>
      <p>
        The second one is the more dangerous of the two, because it is not a
        valuation opinion. It is a number somebody has to actually fund, and the
        model said it was small.
      </p>"""),
            ("Detection", "Test your own model", """
      <p>
        <b>Find the spud-to-sales lag.</b> Search the model for a parameter that
        represents it. In most annual models there is not one, which settles the
        question immediately.
      </p>
      <p>
        <b>Compare peak exposure against treasury.</b> Ask the model what the
        largest cumulative cash outflow is before the programme turns cash
        positive, then ask treasury what they actually had to draw. A model
        reporting a small fraction of the real draw has netted inflow against
        outflow inside a period.
      </p>
      <p>
        <b>Re-run it monthly.</b> If moving the same assumptions from annual to
        monthly periods changes net present value by more than a couple of
        percent, the annual grid was doing the work rather than the economics.
      </p>"""),
            ("The fix", "What to do instead", """
      <p>
        <b>Carry spud date and first sales date as separate inputs.</b> They are
        separate facts. Every well already has both recorded somewhere in
        operations.
      </p>
      <p>
        <b>Model monthly through the capital programme.</b> You can drop to
        annual periods once the wells are on decline and the error stops
        mattering, but not during the years when capital and flush production
        overlap.
      </p>
      <p>
        <b>Report peak exposure as its own headline number.</b> Not buried in a
        cash-flow tab. Net present value and peak funding requirement answer
        different questions for different people, and only one of them can
        actually stop a programme.
      </p>""" + CTA_LINE),
        ],
    },
    {
        "slug": "constant-strip-ratio-constant-grade",
        "nav": "Constant strip ratio, constant grade",
        "title": "Constant strip ratio and constant grade across a mine life",
        "description": (
            "A pit deepens and its best ore goes first. Modelling one strip ratio and "
            "one grade across the whole life is not conservative, it describes a "
            "different mine."
        ),
        "standfirst": (
            "A pit deepens and its best ore goes first. A mine modelled at one strip "
            "ratio and one grade across its life is not being conservative. It is "
            "describing a mine that does not exist."
        ),
        "cost": "Unit costs understated<br>across the back half.",
        "sections": [
            ("Mechanism", "Averages that describe nothing", """
      <p>
        Life-of-mine average strip ratio is a real number that appears in real
        technical reports, and it is a perfectly good summary statistic. It is a
        terrible model input.
      </p>
      <p>
        An open pit gets deeper. Waste per tonne of ore climbs as it does,
        usually steeply in the later benches. Meanwhile the mine plan sends the
        highest-grade, lowest-cost material first, because every mine plan ever
        written does that. So unit cost rises through the life and unit revenue
        falls, and both effects land in the same years.
      </p>
      <p>
        Apply a single average to both and the model understates cost and
        overstates revenue in exactly the back half of the life, while
        overstating cost and understating revenue at the front. Those errors do
        not cancel, because discounting weights the front end more heavily. The
        model reports a mine that is more profitable, later, than the one the
        engineers designed.
      </p>
      <p>
        It also quietly breaks the cutoff decision. Whether marginal material is
        worth hauling depends on the strip ratio and grade at the time it would
        be mined, not on a life average that no single period ever experiences.
      </p>"""),
            ("Detection", "Test your own model", """
      <p>
        <b>Look for a schedule.</b> Does the model carry strip ratio and grade
        per period, or one value each? If it is one value, the mine plan's own
        sequencing has been discarded and the answer cannot be right.
      </p>
      <p>
        <b>Check the last five years.</b> Take the modelled unit cost in the
        final years of the life and compare it to what the pit design implies at
        those benches. A flat unit cost across a deepening pit is not a modelling
        simplification, it is a wrong answer.
      </p>
      <p>
        <b>Ask where the stockpile went.</b> Most schedules stockpile marginal
        material and reclaim it late. If the model has no stockpile, tonnes and
        grades are arriving in the wrong years.
      </p>"""),
            ("The fix", "What to do instead", """
      <p>
        <b>Take the profile from the mine schedule.</b> The engineers already
        produced strip ratio and grade per period. The number you want exists
        and someone has already defended it.
      </p>
      <p>
        <b>Carry stockpiles explicitly.</b> Model what is mined, what is
        processed, and what is sitting on a pad in between. The gap between those
        three is where a lot of working capital and a lot of grade actually
        lives.
      </p>
      <p>
        <b>Recompute the cutoff each period.</b> With a real strip and grade
        profile, cutoff grade becomes an output of the economics rather than an
        input somebody chose once.
      </p>""" + CTA_LINE),
        ],
    },
    {
        "slug": "reclamation-capitalised-rather-than-expensed",
        "nav": "Reclamation capitalised, not expensed",
        "title": "Reclamation capitalised rather than expensed",
        "description": (
            "Closure cost pooled into capital and depreciated on units of production "
            "leaves the deduction stranded, because by the time closure is paid there "
            "is no production left to depreciate against."
        ),
        "standfirst": (
            "By the time closure is paid there is no production left to depreciate it "
            "against. Pooled into capital under units of production, the deduction is "
            "stranded entirely."
        ),
        "cost": "Real cash, and it lands<br>in the terminal years.",
        "sections": [
            ("Mechanism", "A deduction with nothing to deduct against", """
      <p>
        Units-of-production depreciation spreads a cost over the tonnes or
        barrels that the cost helped produce. It is the right method for a
        processing plant. It is incoherent for closure.
      </p>
      <p>
        Reclamation is paid after the last tonne is mined. There are no
        subsequent units for the deduction to attach to, so a units-of-production
        pool containing closure cost simply never depreciates. The tax shield
        that the model booked silently fails to arrive, and the error is invisible
        because the depreciation schedule still balances.
      </p>
      <p>
        There is a second problem sitting underneath. Many models stop at the
        last year of production. Closure spending happens after that, so it falls
        off the end of the horizon entirely and the model values a mine that
        never gets cleaned up. The liability is real, it is often bonded, and
        somebody is going to pay it.
      </p>"""),
            ("Detection", "Test your own model", """
      <p>
        <b>Check where the model horizon ends.</b> If the last period is the last
        producing period, closure is not in the answer at all.
      </p>
      <p>
        <b>Find the closure line.</b> Trace whether it is capital or operating
        cost, and if it is capital, find which pool it went into and what
        depreciates that pool.
      </p>
      <p>
        <b>Compare against the bond.</b> Regulators require a bonded closure
        estimate. If the model's number is materially below the bond, the model
        is optimistic about something the regulator has already priced.
      </p>"""),
            ("The fix", "What to do instead", """
      <p>
        <b>Treat closure as cash in the period it is spent.</b> That is what it
        is. Its tax treatment is a separate question from its cash timing, and
        conflating them is what caused the problem.
      </p>
      <p>
        <b>Run the horizon past last production.</b> Far enough to cover
        reclamation, monitoring and bond release, which can be many years for
        water treatment obligations.
      </p>
      <p>
        <b>Model the accrued liability separately from the cash.</b> The balance
        sheet obligation and the cheque are different objects on different
        timelines, and lenders will ask about both.
      </p>""" + CTA_LINE),
        ],
    },
    {
        "slug": "nameplate-mistaken-for-a-bottleneck",
        "nav": "Nameplate mistaken for a bottleneck",
        "title": "Nameplate capacity mistaken for the actual bottleneck",
        "description": (
            "A plant can be exactly the right size while something upstream is binding. "
            "Shadow price every constraint before sizing an expansion, or the capital "
            "buys nothing."
        ),
        "standfirst": (
            "A plant can be exactly the right size while something else is holding the "
            "asset back. Expansion capital gets proposed against the constraint that is "
            "easiest to measure, not the one that binds."
        ),
        "cost": "Capital spent where the<br>shadow price is zero.",
        "sections": [
            ("Mechanism", "Visible is not the same as binding", """
      <p>
        Nameplate capacity is a number on a sign. It is written down, everybody
        knows it, and it is the first thing anyone reaches for when asked why
        production is not higher.
      </p>
      <p>
        The constraint that is actually binding is frequently something with no
        sign on it. Water disposal capacity. Compression on a gathering line.
        Truck availability. A permit condition on hours. Power supply. Any of
        these can be the reason the asset produces what it produces, and none of
        them are on the plant nameplate.
      </p>
      <p>
        The economics of this are unforgiving. A constraint that is not binding
        has a shadow price of zero, meaning an extra unit of it is worth exactly
        nothing. Expansion capital aimed at a non-binding constraint does not
        earn a poor return. It earns no return, because the asset was never
        limited by the thing that got bigger.
      </p>
      <p>
        Worse, relieving one constraint usually just exposes the next. Sizing
        without knowing the order of the queue produces an expansion that hits a
        new wall a few months after commissioning.
      </p>"""),
            ("Detection", "Test your own model", """
      <p>
        <b>Perturb each constraint one at a time.</b> Relax it by a small
        increment in the full model, re-run, and read the change in value. That
        change is the shadow price. Constraints that return zero are not binding
        and no amount of capital aimed at them will help.
      </p>
      <p>
        <b>Check utilisation against the sign.</b> A plant running well below
        nameplate while production is capped means the cap is somewhere else
        entirely.
      </p>
      <p>
        <b>Ask the operators before the engineers.</b> The people who run the
        asset day to day usually know exactly what stops them. It is rarely the
        thing in the capital proposal.
      </p>"""),
            ("The fix", "What to do instead", """
      <p>
        <b>Shadow price every constraint, not just the candidate.</b> Relax and
        tighten each one against the full model. The output separates what binds
        from what is merely large.
      </p>
      <p>
        <b>Couple capital to the dial being turned.</b> Sizing a debottleneck
        without its capital cost attached produces a recommendation that ignores
        whether the increment is worth buying.
      </p>
      <p>
        <b>Find the next constraint before committing.</b> Relieve the binding
        one in the model, re-run, and see what binds after that. If it binds
        immediately, the expansion is smaller than it looks.
      </p>""" + CTA_LINE),
        ],
    },
    {
        "slug": "opportunities-ranked-on-gross-uplift",
        "nav": "Opportunities ranked on gross uplift",
        "title": "Opportunities ranked on gross uplift",
        "description": (
            "Every asset team's best idea wins its own study, because none of them "
            "carry a cost or a probability. Ranked on risked value across a portfolio, "
            "the ordering usually inverts."
        ),
        "standfirst": (
            "Every asset team's best idea wins its own study, because none of them "
            "carry a cost or a probability. Ranked properly, the ordering usually "
            "inverts."
        ),
        "cost": "The free commercial fix<br>loses to the big project.",
        "sections": [
            ("Mechanism", "A headline is not a ranking", """
      <p>
        Opportunities arrive as gross uplift. Recover an extra two hundred
        thousand barrels. Add eight percent to throughput. Each number is
        defensible on its own terms and each was produced by a team that believes
        in it.
      </p>
      <p>
        Two things are missing from all of them, and they are the two things that
        determine whether the idea is worth doing. What it costs, and how likely
        it is to work. Without those, ranking is by headline size, which
        systematically favours large capital projects over cheap commercial
        fixes.
      </p>
      <p>
        The inversion is routine once you correct it. A marketing or contract
        renegotiation costing nothing, with even moderate odds, frequently
        outranks a nine-figure refrac programme with a coin-flip chance of
        working. It never wins the argument in a meeting, because it does not
        sound like an achievement.
      </p>
      <p>
        There is a subtler failure underneath. Ideas evaluated one at a time
        against a base case cannot see each other. Two improvements that both
        relieve the same constraint are not additive, and a model that tests them
        separately will happily approve both and book the benefit twice.
      </p>"""),
            ("Detection", "Test your own model", """
      <p>
        <b>Count the odds.</b> Look at the opportunity list. How many entries
        carry a probability? If the answer is none, the list is sorted by
        enthusiasm.
      </p>
      <p>
        <b>Count the costs.</b> Same question. An uplift without its capital
        attached is not a proposal, it is an observation.
      </p>
      <p>
        <b>Check whether they were tested together.</b> Re-run the model with
        every approved opportunity active at once and compare the total against
        the sum of the individual cases. A gap means they were competing for the
        same constraint.
      </p>"""),
            ("The fix", "What to do instead", """
      <p>
        <b>Price and risk every line.</b> Risked value is the probability of
        success times the change in value, less the capital required. It is not a
        sophisticated formula. It is just the one nobody applies consistently.
      </p>
      <p>
        <b>Workshop the odds with the people who would execute.</b> Not with
        finance. The crew that has attempted this three times before has the only
        useful prior, and they will tell you if you ask them in a room rather
        than in a form.
      </p>
      <p>
        <b>Re-run the whole model for each one.</b> Testing an opportunity by
        adjusting a line in a summary tab misses every interaction. Running the
        full model catches the case where the benefit is already capped by
        something else.
      </p>
      <p>
        We have seen a gas lift conversion return exactly nothing on this test,
        not because gas lift does not work, but because the recovery cap on those
        wells already bound. Flattening the tail moved no barrels. That is
        invisible without a model that carries the constraint.
      </p>""" + CTA_LINE),
        ],
    },
    {
        "slug": "variance-reported-as-a-single-number",
        "nav": "Variance reported as one number",
        "title": "Variance reported as a single number",
        "description": (
            "We were eleven million light points nobody at anything. Split into volume, "
            "price, cost usage and cost rate, the same variance names the department "
            "that can act on it."
        ),
        "standfirst": (
            "We were eleven million light points nobody at anything. Split four ways, "
            "the same eleven million names the department that can act on it."
        ),
        "cost": "A month of argument,<br>every month.",
        "sections": [
            ("Mechanism", "One number, no owner", """
      <p>
        A single variance figure is arithmetically true and operationally
        useless. It confirms that the month was worse than planned and says
        nothing about why, which means the meeting that follows is an argument
        rather than a decision.
      </p>
      <p>
        The number always has at least four causes inside it, and they belong to
        different people. Volume, which is operations. Realised price, which is
        marketing and basis. Cost rate, which is procurement and contracts. Cost
        usage, which is operations again but a different question from volume.
      </p>
      <p>
        Left aggregated, each department can construct a story in which the
        variance was somebody else's. All of those stories are consistent with
        the single number, which is precisely why the same argument recurs every
        month and never resolves.
      </p>
      <p>
        The undecomposed number also destroys the feedback loop the forecast
        needs. If you cannot attribute a miss, you cannot tell whether the model
        needs refitting or the asset had a bad month, so nothing gets corrected
        and next month's forecast carries the same error.
      </p>"""),
            ("Detection", "Test your own reporting", """
      <p>
        <b>Open last month's pack.</b> Is the variance split by cause, or is it
        one line with commentary underneath? Commentary is not decomposition.
      </p>
      <p>
        <b>Check whether the splits reconcile.</b> A decomposition that does not
        add back to the total exactly has a residual bucket, and the residual is
        where the uncomfortable part usually got put.
      </p>
      <p>
        <b>Ask whether last month changed anything.</b> If the same variance
        appears three months running and no parameter was refitted, the reporting
        is describing the problem rather than feeding back into the forecast.
      </p>"""),
            ("The fix", "What to do instead", """
      <p>
        <b>Decompose four ways, every period.</b> Volume, price, cost rate, cost
        usage. Each one names an owner. The conversation changes from whose fault
        it was to which of these four we are fixing.
      </p>
      <p>
        <b>Reconcile to the total exactly.</b> No residual bucket. If the pieces
        do not sum, the decomposition is wrong and should be fixed rather than
        plugged.
      </p>
      <p>
        <b>Feed it back into the model.</b> A variance that persists across
        periods is a parameter that has drifted, not bad luck. That is the signal
        to refit, and it is the whole point of measuring in the first place.
      </p>""" + CTA_LINE),
        ],
    },
]


def finding_body(item, index, total):
    prev_item = FINDINGS[index - 1] if index > 0 else None
    next_item = FINDINGS[index + 1] if index < total - 1 else None

    pager = ""
    if prev_item or next_item:
        left = right = ""
        if prev_item:
            left = ('<a href="/findings/%s/"><span class="dir">Previous</span>%s</a>'
                    % (prev_item["slug"], prev_item["nav"]))
        else:
            left = "<span></span>"
        if next_item:
            right = ('<a href="/findings/%s/" style="text-align:right;">'
                     '<span class="dir">Next</span>%s</a>'
                     % (next_item["slug"], next_item["nav"]))
        else:
            right = "<span></span>"
        pager = ('  <div class="block">\n'
                 '    <div class="rail"><b>More</b><span>Redline list</span></div>\n'
                 '    <div class="col">\n'
                 '      <div class="pager">%s%s</div>\n'
                 '    </div>\n'
                 '  </div>\n' % (left, right))

    head = (
        '\n  <section class="thesis article">\n'
        '    <div class="crumb"><a href="/findings/">Findings</a> &middot; '
        "%02d of %02d</div>\n"
        "    <h1>%s</h1>\n"
        '    <p class="standfirst">%s</p>\n'
        '    <div class="costline">%s</div>\n'
        "  </section>\n\n" % (index + 1, total, item["title"],
                              item["standfirst"], item["cost"])
    )
    return head + article(item["sections"]) + "\n" + pager


def findings_index_body():
    rows = []
    for i, item in enumerate(FINDINGS):
        rows.append(
            '        <a class="row" href="/findings/%s/">\n'
            '          <span class="num">%02d</span>\n'
            "          <span><h3>%s</h3><p>%s</p></span>\n"
            '          <span class="tag">%s</span>\n'
            "        </a>" % (item["slug"], i + 1, item["title"],
                              item["standfirst"],
                              item["cost"].split("<br>")[0].rstrip("."))
        )
    return (
        '\n  <section class="thesis article">\n'
        '    <div class="crumb">Findings &middot; Recurring defects</div>\n'
        "    <h1>Eight ways a production model quietly lies</h1>\n"
        '    <p class="standfirst">\n'
        "      These are the errors we find most often, in models built by competent\n"
        "      people. Each one is invisible in the output, and each one moves the\n"
        "      answer in the same direction, which is toward approval.\n"
        "    </p>\n"
        "  </section>\n\n"
        '  <div class="block">\n'
        '    <div class="rail"><b>Redline list</b><span>Eight defects</span></div>\n'
        '    <div class="col">\n'
        '      <div class="indexlist">\n%s\n      </div>\n'
        "    </div>\n"
        "  </div>\n" % "\n".join(rows)
    )


# TODO, needs Jonathan: the page states only what he has confirmed. Still to
# come, and each one is worth real money on a page a lender reads: employers or
# clients he is willing to name, the basins and assets actually modelled, any
# professional registration, a city, and a photograph.
ABOUT_BODY = """
  <section class="thesis article">
    <div class="crumb">About &middot; Who does the work</div>
    <h1>Who you are actually hiring.</h1>
    <p class="standfirst">
      A model is only worth what its author can defend in a room. This page
      exists so you know whose judgement is behind the number before you send us
      anything.
    </p>
  </section>

  <div class="block">
    <div class="rail"><b>Principal</b><span>Who does the work</span></div>
    <div class="col prose">
      <p>
        Gossans is a single-principal practice led by a petroleum engineer.
      </p>
      <p>
        Hyperbolic decline behaviour, the gap between a fit to per-well rate and
        a fit to field rate, and the reason a type curve entered on the wrong
        basis stays wrong for the life of a forecast are not incidental
        interests here. They are the subject, and the published work is there to
        be checked rather than taken on trust.
      </p>
      <p>
        The person who takes the scoping call is the person who builds the model
        and presents the finding. Nothing is handed to an analyst you have not
        met. That is a deliberate limit on how much work we take, and it is the
        reason a two-week engagement is two weeks rather than a quarter.
      </p>
    </div>
  </div>

  <div class="block">
    <div class="rail"><b>Range</b><span>Why this many commodities</span></div>
    <div class="col prose">
      <p>
        The commodity list on this site looks broad for a single practice. It is
        close to the list one state produces, and it is the state this practice
        was trained in.
      </p>
      <p>
        Wyoming is the largest coal producer in the United States and its largest
        uranium producer. It mines the world's largest trona deposit, separates
        helium out of its own declining gas streams, holds one of the few
        advanced rare earth projects in the country, and produces oil and gas
        across the Powder River and Green River basins. Those assets share
        regulators, a labour market and frequently an owner, which makes the
        comparison between them a practical question rather than an academic one.
      </p>
      <p>
        The arithmetic of extraction economics is the same in every one of those
        cases. What differs is the physics feeding it, and the engine carries
        that difference explicitly rather than averaging it away.
      </p>
    </div>
  </div>

  <div class="block">
    <div class="rail"><b>Location</b><span>Where we work from</span></div>
    <div class="col prose">
      <p>
        Gossans works from <b>Gillette, Wyoming</b>, in the Powder River Basin.
        Not from Houston, and not from Denver.
      </p>
      <p>
        Gillette sits inside both halves of what this practice covers. The
        largest coal mines in the United States are a short drive out of town,
        and the oil and coalbed gas of the basin are underneath it. The
        comparison this site keeps insisting on, between a mine and a well valued
        on one basis, is a local question here rather than a theoretical one.
      </p>
      <p>
        That proximity matters more than a mailing address usually does, because
        of how these engagements run. The costing workshop is the step that
        decides whether an opportunity list is worth anything, since the price
        and the odds on every line have to come from the crew who would execute
        it rather than from an assumption somebody typed into a spreadsheet.
        Being a drive away rather than a flight and a hotel turns that from a
        production into a half day.
      </p>
      <p>
        It also means the regulators, operators and service companies whose
        public filings feed two thirds of our data request are on our doorstep,
        in our time zone, filing with agencies we read every week.
      </p>
    </div>
  </div>

  <div class="block">
    <div class="rail"><b>Independence</b><span>Why it matters</span></div>
    <div class="col prose">
      <p>
        We sell no software, resell no data, and take no commission on any
        transaction we are asked to value. There is no product whose adoption our
        recommendation could favour, which is the usual reason a technical
        opinion quietly bends.
      </p>
      <p>
        When our model disagrees with yours, that disagreement is the deliverable.
        We would rather tell you the project is worth less than you thought and
        not be hired again than tell you what the scoping call suggested you
        wanted to hear.
      </p>
    </div>
  </div>

  <div class="block">
    <div class="rail"><b>Confidentiality</b><span>Your data</span></div>
    <div class="col prose">
      <p>
        Data arrives under a non-disclosure agreement signed before the request
        goes out. It is held in a single-client workspace, is never pooled with
        another client's, and is returned or destroyed at your instruction when
        the engagement closes.
      </p>
      <p>
        We publish method, never clients. Every figure on this site is either
        public record or model output built to demonstrate the method, and no
        engagement is referenced without written permission.
      </p>
    </div>
  </div>
"""

# TODO, needs Jonathan: a direct booking link beside the email address, plus
# a phone number and a city. Buyers of technical work check that a firm is
# somewhere real, and a booking link removes a round trip.
CONTACT_BODY = """
  <section class="thesis article">
    <div class="crumb">Contact &middot; Scoping call</div>
    <h1>Forty-five minutes, and we will tell you if we are the wrong people.</h1>
    <p class="standfirst">
      The first two steps of any engagement cost nothing. If the answer is that
      your model is fine, or that the decision in front of you does not need a
      model, you will hear that instead of a proposal.
    </p>
  </section>

  <div class="block">
    <div class="rail"><b>Start</b><span>Get in touch</span></div>
    <div class="col prose">
      <p>
        Email is the fastest route. Tell us what the asset is, what decision is
        pending, and roughly when it has to be made. You do not need to prepare
        anything or send data to have the first conversation.
      </p>
      <p style="margin-top:24px;">
        <a class="btn" href="mailto:hello@gossans.com?subject=Scoping%20call">hello@gossans.com</a>
      </p>
    </div>
  </div>

  <div class="block">
    <div class="rail"><b>Where</b><span>Based in the basin</span></div>
    <div class="col prose">
      <p>
        Gillette, Wyoming, in the Powder River Basin. Work is remote by default
        and most engagements never need a visit, but the costing workshop is
        better in a room, and for an asset in this basin that is a drive rather
        than a trip.
      </p>
    </div>
  </div>

  <div class="block">
    <div class="rail"><b>Process</b><span>What happens next</span></div>
    <div class="col prose">
      <p>
        <b>Scoping call, forty-five minutes, no charge.</b> What the asset is,
        what decision is pending, and whether we are the right people for it. We
        will say so if we are not.
      </p>
      <p>
        <b>A written scope, no charge.</b> Fixed fee, fixed deliverable, a date,
        and the exact data request. You can take that document to somebody else
        and get it quoted, and we would rather you did than that you felt
        committed by a conversation.
      </p>
      <p>
        <b>Non-disclosure agreement, then data.</b> Signed before the request
        goes out, not after. For a producing asset in the United States, about
        two thirds of what we need is public and we pull that ourselves first.
      </p>
      <p>
        <b>Build, fit and reconcile.</b> We rebuild the asset from its own
        history and fit it to outturn, rather than adjusting the model you
        already have.
      </p>
      <p>
        <b>Workshop with the people who run the asset.</b> Costs and odds on
        every opportunity come from the crew who would execute them, not from a
        spreadsheet assumption.
      </p>
      <p>
        <b>Report, model files and handover.</b> You keep the model. Every
        assumption is one line in a text file, so next year's change is a
        difference rather than an excavation.
      </p>
    </div>
  </div>

  <div class="block">
    <div class="rail"><b>Data</b><span>What we ask for</span></div>
    <div class="col prose">
      <p>
        Nothing, until there is a signed scope and a non-disclosure agreement.
        When we do ask, the request is one page: monthly volumes with producing
        days and well count, monthly operating cost, capital authorisations and
        actuals, realised price, and one page of lease and fiscal terms. Two
        spreadsheet exports covers most of it.
      </p>
      <p>
        The rest we collect ourselves from state regulators, mine safety filings,
        technical reports on comparable projects, and published price series.
      </p>
    </div>
  </div>
"""


ORG_SCHEMA = """{
  "@context": "https://schema.org",
  "@type": "ProfessionalService",
  "name": "Gossans",
  "url": "https://www.gossans.com/",
  "description": "Fixed-fee production outlook simulation and opportunity screening. Assets simulated on one basis, fitted to outturn, with every option ranked on risked value.",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Gillette",
    "addressRegion": "WY",
    "addressCountry": "US"
  },
  "areaServed": {
    "@type": "Place",
    "name": "United States"
  },
  "knowsAbout": [
    "Reservoir engineering",
    "Decline curve analysis",
    "Mine planning",
    "Project economics",
    "Reserves evaluation"
  ]
}"""


def build_pages():
    import study_prb

    total = len(FINDINGS)
    pages = []

    import fitter_page
    import model_page

    pages.append({
        "url": "/fit/",
        "title": "%s | Gossans" % fitter_page.TITLE,
        "description": fitter_page.DESCRIPTION,
        "kicker": "Runs in your browser",
        "priority": "1.0",
        "body": fitter_page.BODY,
        "head_extra": fitter_page.HEAD_EXTRA,
    })

    pages.append({
        "url": "/basin-model/",
        "title": "%s | Gossans" % model_page.TITLE,
        "description": model_page.DESCRIPTION,
        "kicker": "Interactive model",
        "priority": "1.0",
        "body": model_page.BODY,
        "head_extra": model_page.HEAD_EXTRA,
    })

    pages.append({
        "url": "/powder-river-basin/",
        "title": "%s | Gossans" % study_prb.TITLE,
        "description": study_prb.DESCRIPTION,
        "kicker": "Study &middot; Converse County, Wyoming",
        "priority": "1.0",
        "body": study_prb.BODY,
    })

    pages.append({
        "url": "/findings/",
        "title": "Eight ways a production model quietly lies | Gossans",
        "description": (
            "Eight recurring defects in production and mine economic models, each one "
            "invisible in the output and each one moving the answer toward approval."
        ),
        "kicker": "Recurring defects in production models",
        "priority": "0.9",
        "body": findings_index_body(),
    })

    for i, item in enumerate(FINDINGS):
        pages.append({
            "url": "/findings/%s/" % item["slug"],
            "title": "%s | Gossans" % item["title"],
            "description": item["description"],
            "kicker": "Redline list &middot; %02d of %02d" % (i + 1, total),
            "priority": "0.8",
            "body": finding_body(item, i, total),
            "schema": _article_schema(item),
        })

    pages.append({
        "url": "/about/",
        "title": "About Gossans",
        "description": (
            "How the practice works, why independence matters when a model disagrees "
            "with yours, and how client data is handled."
        ),
        "kicker": "Gillette, Wyoming",
        "priority": "0.9",
        "body": ABOUT_BODY,
        "schema": ORG_SCHEMA,
    })

    pages.append({
        "url": "/contact/",
        "title": "Contact Gossans",
        "description": (
            "A forty-five minute scoping call at no charge, followed by a written "
            "fixed-fee scope. Production outlook simulation and screening from Gillette, "
            "Wyoming. Nothing is "
            "requested until both are agreed."
        ),
        "kicker": "Gillette, Wyoming",
        "priority": "0.9",
        "body": CONTACT_BODY,
    })

    return pages


def _article_schema(item):
    return (
        "{\n"
        '  "@context": "https://schema.org",\n'
        '  "@type": "Article",\n'
        '  "headline": "%s",\n'
        '  "description": "%s",\n'
        '  "url": "https://www.gossans.com/findings/%s/",\n'
        '  "isPartOf": {\n'
        '    "@type": "CollectionPage",\n'
        '    "name": "Redline list",\n'
        '    "url": "https://www.gossans.com/findings/"\n'
        "  },\n"
        '  "publisher": {\n'
        '    "@type": "Organization",\n'
        '    "name": "Gossans",\n'
        '    "url": "https://www.gossans.com/"\n'
        "  }\n"
        "}" % (item["title"], item["description"].replace('"', "'"), item["slug"])
    )
