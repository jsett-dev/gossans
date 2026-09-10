#!/usr/bin/env python3
"""The Powder River Basin study page.

Every figure here came out of the public record. Nothing in it is client work
and nothing is confidential. That is the point: a reader can check it against
the same filings.
"""

TITLE = "What 1,459 Powder River Basin wells say about completion intensity"

DESCRIPTION = (
    "A study of every producing horizontal oil well in Converse County, Wyoming, "
    "built entirely from public records. Recovery by formation, the collapse in "
    "barrels per pound of proppant, and the point where more sand stops paying."
)

BODY = """
  <section class="thesis article">
    <div class="crumb">Study &middot; Powder River Basin &middot; Converse County</div>
    <h1>Everyone knows fracs got bigger. Almost nobody has priced the last increment.</h1>
    <p class="standfirst">
      We rebuilt every producing horizontal oil well in Converse County, Wyoming
      from the state's own records, fitted each one, and asked a single
      question: at what point does another pound of sand stop paying for
      itself. The answer is not where the industry's behaviour suggests it
      believes it is.
    </p>
    <div class="costline">
      1,459 wells &middot; 148,524 production months &middot; every figure from public filings.
    </div>
  </section>

  <div class="block">
    <div class="rail"><b>Scope</b><span>What was studied</span></div>
    <div class="col prose">
      <p>
        Converse County holds 1,459 producing horizontal and directional oil
        wells, out of 2,863 across the Powder River Basin and 4,023 statewide.
        We pulled the monthly production history of every one of them, together
        with 531,535 formation tops, 149,933 perforation records and 75,335
        completion treatments covering the whole state.
      </p>
      <p>
        All of it is public. It comes from the Wyoming Oil and Gas Conservation
        Commission, and every number below can be checked against the same
        filings by anybody who wants to. No client data was used and none of
        this is anyone's confidential information.
      </p>
      <p>
        Of those wells, 1,371 had at least eighteen producing months. We fitted
        1,368 of them and <b>refused 174</b> outright, either because the
        hyperbolic exponent pinned against its bound or because the fit quality
        was too poor to mean anything. Refusing a fit is not a failure. Reporting
        one that should have been refused is.
      </p>
    </div>
  </div>

  <div class="block">
    <div class="rail"><b>Method</b><span>How each well was fitted</span></div>
    <div class="col prose">
      <p>
        <b>Rate per producing day, not per calendar month.</b> A well that was
        down for eleven days did not decline. It was off. Dividing by the month
        confuses the two, and downtime then gets forecast forward as reservoir
        behaviour.
      </p>
      <p>
        <b>The flowback month dropped.</b> The first partial month is choked and
        cleaning up. It is not on the depletion trend that governs everything
        after it.
      </p>
      <p>
        <b>Fitted on the logarithm of rate.</b> Production spans two orders of
        magnitude across a well's life. A fit on raw rate is dominated by the
        first six months and effectively ignores the tail, which is exactly
        where the reserve lives.
      </p>
      <p>
        <b>A terminal decline switch.</b> The curve runs hyperbolic until its
        own decline flattens to six percent a year, then exponential to the
        economic limit. Without that switch, a well fitted at an exponent of 1.4
        books sixty percent more oil than it will ever deliver, and at 1.8 it
        books almost nine times too much. That correction alone is larger than
        most of the arguments people have about type curves.
      </p>
      <p>
        Across the wells that passed, the median hyperbolic exponent is 1.05,
        the median secant decline 76.2 percent, and the median fit quality 0.886
        on log rate.
      </p>
    </div>
  </div>

  <div class="block">
    <div class="rail"><b>Result</b><span>Recovery by formation</span></div>
    <div class="col">
      <h2>The raw ranking and the honest ranking are different.</h2>
      <p class="prose" style="color:var(--ink-2); margin-bottom:22px;">
        Median estimated recovery per well, and the same figure divided by
        lateral length. Where a directional survey is on file the lateral is
        measured from it; otherwise the perforated interval stands in, and on
        the wells that have both the two agree at the median to within two
        percent. Wells with under a thousand feet are excluded from the second
        column, because a vertical completion returns a ratio in the millions
        and that is arithmetic rather than geology.
      </p>
      <div class="tbl">
        <table>
          <tr><th>Formation</th><th>Wells</th><th>Median recovery, bbl</th><th>Per 1,000 ft</th></tr>
          <tr><td>Niobrara</td><td>442</td><td>414,783</td><td>45,448</td></tr>
          <tr><td>Turner</td><td>255</td><td>325,713</td><td><b>50,604</b></td></tr>
          <tr><td>Parkman</td><td>125</td><td>307,848</td><td>43,451</td></tr>
          <tr><td>Sussex</td><td>101</td><td>223,342</td><td>40,899</td></tr>
          <tr><td>Frontier</td><td>97</td><td>273,860</td><td>33,294</td></tr>
          <tr><td>Teapot</td><td>77</td><td>277,070</td><td>32,922</td></tr>
        </table>
      </div>
      <div class="prose">
        <p>
          On raw recovery the Niobrara wins and it is not close. Normalised for
          how much rock each well was actually completed across, the Turner is
          ahead of it. The Niobrara's advantage is substantially that its wells
          are longer, which is a decision somebody made rather than a property
          of the rock.
        </p>
      </div>
    </div>
  </div>

  <div class="block">
    <div class="rail"><b>Result</b><span>Completion intensity</span></div>
    <div class="col">
      <h2>Proppant per well rose twenty-nine fold in thirteen years.</h2>
      <div class="tbl">
        <table>
          <tr><th>Year</th><th>Median proppant per well, lb</th><th>Median stages</th></tr>
          <tr><td>2012</td><td>848,205</td><td>11</td></tr>
          <tr><td>2016</td><td>1,393,619</td><td>14</td></tr>
          <tr><td>2019</td><td>4,921,560</td><td>19</td></tr>
          <tr><td>2022</td><td>12,044,437</td><td>38</td></tr>
          <tr><td>2025</td><td>24,531,509</td><td>41</td></tr>
        </table>
      </div>
      <div class="prose">
        <p>
          This is the single most important number in the study, and not because
          of what it says about fracs. It is important because it means
          <b>any comparison of wells across vintages is measuring the calendar</b>
          unless it explicitly controls for design. A performance map built
          without that control is a map of when people drilled, wearing a
          geologist's coat.
        </p>
      </div>
    </div>
  </div>

  <div class="block">
    <div class="rail"><b>Result</b><span>What the sand buys</span></div>
    <div class="col">
      <h2>Within the same year, doubling the sand buys about a fifth more oil.</h2>
      <p class="prose" style="color:var(--ink-2); margin-bottom:22px;">
        Wells split at the median proppant per foot, compared only against
        others completed in the same year. That restriction costs sample size
        and is the whole reason the answer is trustworthy.
      </p>
      <div class="tbl">
        <table>
          <tr><th>Completion year</th><th>Wells</th><th>Extra lb per ft</th><th>Extra bbl per ft</th><th>Pounds per extra barrel</th></tr>
          <tr><td>2012</td><td>36</td><td>408</td><td>3.2</td><td>129</td></tr>
          <tr><td>2013</td><td>58</td><td>298</td><td>&minus;0.5</td><td><b>no gain</b></td></tr>
          <tr><td>2014</td><td>40</td><td>509</td><td>&minus;14.9</td><td><b>no gain</b></td></tr>
          <tr><td>2020</td><td>31</td><td>1,065</td><td>&minus;0.7</td><td><b>no gain</b></td></tr>
          <tr><td>2021</td><td>41</td><td>742</td><td>3.0</td><td>245</td></tr>
          <tr><td>2022</td><td>96</td><td>1,625</td><td>11.6</td><td>140</td></tr>
          <tr><td>2023</td><td>99</td><td>1,198</td><td>8.6</td><td>140</td></tr>
          <tr><td>2024</td><td>115</td><td>1,736</td><td>17.9</td><td>97</td></tr>
        </table>
      </div>
      <div class="prose">
        <p>
          Weighted across cohorts, an extra barrel costs about 163 pounds of
          extra proppant. In the recent cohorts recovery scales with roughly
          the quarter power of intensity, so the response is real, consistent,
          and nowhere close to proportional.
        </p>
        <p>
          Three cohorts bought nothing at all. In 2013, 2014 and 2020 the
          heavier half recovered less per foot than the lighter half, despite
          pumping more sand, and in 2014 it was not close.
        </p>
      </div>
    </div>
  </div>

  <div class="block">
    <div class="rail"><b>Decision</b><span>Where it stops paying</span></div>
    <div class="col">
      <h2>The last increment earns eight cents on the dollar.</h2>
      <p class="prose" style="color:var(--ink-2); margin-bottom:22px;">
        A ten thousand foot Niobrara lateral, priced through a monthly cash flow
        with capital spent before first sales rather than alongside it. Oil at
        $70 less a $6 differential, sand at nine cents a pound delivered and
        pumped, three barrels of water per barrel of oil, discounted at ten
        percent. Change any of those and the answer moves.
      </p>
      <div class="tbl">
        <table>
          <tr><th>Step in intensity</th><th>Extra capital</th><th>Gain in present value</th><th>Return per dollar of sand</th></tr>
          <tr><td>1.00x to 1.25x</td><td>$281,250</td><td>+$224,687</td><td><b>0.80</b></td></tr>
          <tr><td>1.25x to 1.50x</td><td>$281,250</td><td>+$154,378</td><td>0.55</td></tr>
          <tr><td>1.50x to 2.00x</td><td>$562,500</td><td>+$168,357</td><td>0.30</td></tr>
          <tr><td>2.00x to 2.50x</td><td>$562,500</td><td>+$43,634</td><td><b>0.08</b></td></tr>
        </table>
      </div>
      <div class="prose">
        <p>
          Every step still adds barrels, and every step still adds value, which
          is precisely why the decision keeps getting made. But the last one
          returns eight cents of present value per dollar of sand, which is
          inside the noise of execution risk, price and water handling. It is a
          coin flip dressed as a capital programme.
        </p>
        <p>
          The base design does not clear a ten percent hurdle at these terms at
          all. It returns nine percent. The heavier completions are not an
          optimisation on a good well. They are what makes the well work.
        </p>
      </div>
    </div>
  </div>

  <div class="block">
    <div class="rail"><b>Limits</b><span>What this does not show</span></div>
    <div class="col prose">
      <p>
        <b>Recent wells are forecasts, not observations.</b> The 2022 to 2024
        cohorts have short histories, so their recoveries lean on extrapolation,
        and the terminal decline switch moves such numbers materially.
      </p>
      <p>
        <b>Perforated interval stands in for lateral length.</b> Neither the
        state nor the operator publishes the latter directly. Directional
        surveys would replace the proxy and are the obvious next improvement.
      </p>
      <p>
        <b>There is no pressure data in the public record.</b> So there is no
        rate transient analysis and no material balance, which means no
        independent check on contacted volume. Decline analysis alone cannot
        tell you whether a well is draining what you think it is.
      </p>
      <p>
        <b>Costs are parameters, not filings.</b> Well cost is not public.
        Everything in the decision table moves with the sand price, the
        differential, water handling and the discount rate, all of which are
        inputs a reader can and should change.
      </p>
      <p>
        <b>This compares medians within cohorts.</b> It is not a regression, and
        it does not control for formation within a completion year.
      </p>
    </div>
  </div>

  <div class="block">
    <div class="rail"><b>Sources</b><span>Check it yourself</span></div>
    <div class="col prose">
      <p>
        Monthly production, formation tops, perforations and completion
        treatments all come from the Wyoming Oil and Gas Conservation
        Commission. Well locations and status come from its public map service.
        Nothing here required a subscription, a licence or a login.
      </p>
      <p>
        That is deliberate, and it is worth saying plainly. The commercial data
        vendors prohibit building tools or models on their data. Any study that
        can actually be reproduced by its reader has to be built on the public
        record instead.
      </p>
      <p style="margin-top:26px;">
        <a href="/contact/">Ask us to run this on your asset</a>, in your basin,
        against your own production history.
      </p>
    </div>
  </div>
"""
