# Simulating Liquidity Contagion in the UK Banking Sector: A Maximum Entropy Approach
### Jamie Wilson, June 9 2026

The aggressive monetary tightening seen in the UK in 2022 following the COVID-19 pandemic disrupted standard bank liquidity management, exposing severe vulnerabilities when faced with large scale consumer withdrawals and other capital flight. In this project, I develop a macroprudential stress-testing simulation to evaluate these risks based on varying responses, and the ripple effect on other major institutions. Across six of the largest UK financial institutions - *Barclays, HSBC, NatWest, Lloyd's, Standard Chartered, and Santander* - I construct an unbiased topology of the interbank liability network using a *Maximum Entropy* framework, structurally optimised via an *Iterative Proportional Fitting (IPF)* algorithm.

I subject this network to systemic funding shocks by altering the runoff rate parameter and tracking defaults using a cascade deque algorithm. The empirical findings suggest that vulnerability peaked in 2022, where individual bank liquidity buffers are at their tightest, and declined over the following three years. One can interpret a structural shift to an industry-wide state of precautionary liquidity ‘hoarding’, perhaps in response to high-profile bank failures observed over this period. While the network exhibits resilience under moderate runoff rates, higher rates trigger a total systemic cascade, failing most of, if not all, the six institutions. These results demonstrate that conventional liquidity metrics fail to capture network vulnerabilities, highlighting the need for frameworks involving interbank relationships in modern macroprudential oversight.



# Outline

Famous financial network models such as Eisenberg \& Noe (2001) focus on solvency, meaning a bank defaults because its total liabilities exceed total assets; when bad loans or investments wipe out its capital equity, for example. (Eisenberg \& Noe 2001) In the real world, however, banks rarely collapse for this reason. They may have plenty of long-term assets, such as mortgages or government bonds, but if they cannot satisfy a sudden run on deposits through conversion of these assets or by other means, it faces a default by a liquidity mismatch. While solvency metrics dictate whether a bank should survive in the long term, liquidity metrics dictate whether a bank can survive for the next x days. By modelling the liquidity shortfall and looking at the cause of the collapse, not the result, one can see the near-misses that aren't visible in solvency models. Consequently, systemic networks are far more sensitive to localised liquidity shocks.

Modern liquidity ratio regulations in the UK were introduced in stages following the 2007–2008 global financial crisis, and following the collapse of Northern Rock. The *Financial Services Authority (FSA)* introduced strict domestic liquidity rules in December 2009, and the *Liquidity Coverage Ratio (LCR)* minimum requirement increased in phases until it complied with the *Basel III Liquidity Coverage Ratio (LCR)*, which requires banks to hold enough high-quality liquid assets to survive a 30-day run on the bank or acute liquidity stress scenario.

The LCR evaluates each bank as an isolated node. This exposes a massive structural blind spot: even if every single UK bank satisfies its LCR requirement on its own, a massive macroprudential shock (like the 2022 tightening cycle) can burn through individual buffers. Once the first bank is breached, the ill effects spread through hidden interbank connections, rendering standalone metrics useless. This paper seeks to explore how stress-resistant these banks are while modelling each as a node of an interconnected web, in which one failure may propagate through a network by affecting others’ assets rather than collapse as a standalone unit. This approach aligns perfectly with Basel III liquidity metrics, specifically the LCR and *Net Stable Funding Ratio (NSFR)*.



# Method

The method shall proceed as such:

 - Having scraped data on each of the six banks of interest - *Barclays,
   HSBC, NatWest, Lloyd's, Standard Chartered, and Santander* - I will
   construct metrics to represent *Liquid Assets* (consisting of physical
   cash, reserves held at the central bank, and sovereign debt
   securities that can be liquidated instantly with minimal price
   impact), *Volatile Funding* (to represent short-term liabilities that
   can be withdrawn with little to no notice) and *Tangible Equity*
   (loss-absorbing solvency capital, calculated by stripping intangible
   assets and goodwill from common equity shareholders' funds).
   
 - From these metrics, I shall calculate the *Liquidity Buffer*, the
   leftover cash a bank has after it completely sets aside enough money
   to pay off all of its *Volatile Funding*.
   
 - A bank shall be considered breached if its *Stressed Liquid Assets*,
   that is, its *Liquid Assets* subtracted by its *Volatile Funding*
   multiplied by a runoff rate $α$, is less than zero. This means this
   bank has completely run out of cash and immediately accessible funds
   to pay back the waves of panicking depositors hitting its system. For
   these breached banks, we shall consider their short-term interbank
   obligations wiped out. Following this asset contraction, each
   counterparty’s *Liquidity Buffer* is re-evaluated - if the
   counterparty’s buffer falls below zero, we register a second
   liquidity breach and so on. This sequence continues iteratively until
   no bank is, or remains to be, breached, mapping out the precise
   systemic footprint of the domino effect across the estimated
   interbank topology.

### Model and Modelling Choices

To ensure structural consistency across the network, all bank balance sheet metrics must be denominated in a single, standardized currency. While *Barclays, NatWest, and Lloyd's* publish their financial disclosures in *British Pounds (GBP), HSBC* and *Standard Chartered* report in *United States Dollars (USD)*, and *Santander* reports in *Euros (EUR)*. Therefore, all foreign currency denominations are converted to *Sterling (GBP)* utilizing the official year-end closing spot exchange rates reported by the Bank of England for December 31st of each respective fiscal year.

Given balance sheets of each of the years 2022-25 for each bank $i$ $∈$ $N$, with each year end on December 31st, I shall define the three metrics as such:

 - $\text{Liquid Assets}  ({LA}_{it}) = \text{Cash and due from banks} + \text{Security agree to be resold}$ 
 - $\text{Volatile Funding} ({VF}_{it}) = \text{Trading liabilities} + \text{Derivative product liabilities}$    
 - $\text{Tangible Equity} = \text{Net tangible assets}$ or $\text{Total equity gross minority interest - Goodwill and other intangible assets}$

From these core abstractions, we define the baseline *Liquidity Buffer (LB)* of each bank $i$ at time $t$ as the residual cash reservoir remaining after setting aside sufficient liquid reserves to fully extinguish its short-term volatile obligations:

$$\text{LB}_{it} = \text{LA}_{it} - \text{VF}_{it}$$

The network is subjected to a systemic, macroeconomic liquidity stress event defined by a static runoff rate parameter, $α$, in $[0.1, 1.0]$. The parameter $α$ represents the proportion of Volatile Funding withdrawn from the institution during an active panic cycle. For each bank $i$ at time $t$, the immediate post-shock state is determined by its *Stressed Liquid Assets*, which represents the cash reservoir remaining after servicing the localised bank run:

$$\text{Stressed Liquid Assets}_{it} = \text{LA}_{it} - \alpha \cdot \text{VF}_{it}$$

An institution is deemed to have a liquidity breach at time t if this stressed cash position falls below zero:

$$\text{Stressed Liquid Assets}_{it} < 0$$

Once an institution $i$ initially crosses this threshold, it undergoes an operational default and enters a state of systemic breach. In this network, because the liabilities of this breached bank represent assets to the lending banks, the sudden default of a borrower node results in the instantaneous freezing of those assets.

Let $X$ denote the $n$ x $n$ interbank liability matrix estimated via the *Maximum Entropy* and *Iterative Proportional Fitting (IPF)* framework, where entry ${x}_{ji}$ represents the nominal value of capital owed by bank $i$ to bank $j$. When bank $i$ breaches, it is placed into a queue $Q$, and for each element within the queue, we update the financial standing of all remaining unbreached counterparties $j ∈$ $N - Q$ by applying a direct asset write-down. The dynamic transmission of the shock is formulated as follows:

The current liquid asset total of each counterparty bank $j$ is updated by subtracting its asset exposure to the failed institution $i$:

$$\text{Stressed Liquid Assets}_{jt} = \text{Stressed Liquid Assets}_{jt} - x_{ji}$$

We must then update the *Liquidity Buffer*, where we consider the remaining *Volatile Funding* after the proportion *α* of it is lost in the initial bank run:

$$\text{LB}^{\text{new}}_{jt} = \text{Stressed Liquid Assets}_{jt} - (1 - \alpha) \cdot \text{VF}_{jt}$$

If this *Liquidity Buffer* falls below zero, a second breach is registered, bank $j$ added to the queue, and the loop repeats. The cascade terminates when the queue is empty, meaning that the remaining network nodes, if any, possess sufficient liquidity reservoirs to absorb the aggregate systemic shock.



### The Maximum Entropy Framework

A primary challenge is that the exact exposures that bank $i$ has to bank $j$ are strictly confidential. We only have access to public balance sheets, containing figures that are aggregate marginals. To resolve this under conditions of complete information asymmetry, we employ the *Maximum Entropy Framework* (Upper 2011). In information theory, maximising this entropy gives us an unbiased baseline by assuming that banks spread their interbank lending as evenly and randomly across the system as possible, introducing no arbitrary behavioural assumptions or hidden concentrations.

Mathematically, let $X$ be our hidden $n \times n$ matrix where each entry $x_{ji}$ represents how much bank $i$ owes to bank $j$. Our estimated values must perfectly add up to the publicly available balance sheet totals:

$$\text{Total Interbank Assets}_j = A_j = \sum_{i=1}^{n} \text{Exposure Matrix}[i, j]$$

$$\text{Total Interbank Liabilities}_i = L_i = \sum_{j=1}^{n} \text{Exposure Matrix}[i, j]$$

To make our map as unbiased as possible, we transform these values into probabilities (${p}_{ji}$) and minimize the *Kullback-Leibler divergence* (a metric that measures how much one probability distribution drifts from another). We contrast our map against a completely neutral, independent background prior, where we assume a bank's lending is determined purely by its size:

$$q_{ji} = \frac{A_j}{\sum A} \cdot \frac{L_i}{\sum L}$$ 

Our goal is to find the matrix $P$ that is as close to this neutral background as possible, formalised as: 
$$\text{P} = \min \sum_{j=1}^{n} \sum_{i=1}^{n} p_{ji} \ln \left( \frac{p_{ji}}{q_{ji}} \right)$$

By solving this optimisation problem using calculus (Lagrangian multipliers), we get a straightforward formula to build our baseline matrix: that the initial guess for any connection is simply a product of the two banks' total interbank sizes divided by the size of the whole network: $$x_{ji} = \frac{A_j \cdot L_i}{\sum_{k=1}^{n} A_k}$$

By deploying this framework, we can reliably proxy the unobserved bilateral topology of the interbank market using publicly available, aggregate balance sheet data. (Aldasoro and Alves 2018)

### The Iterative Proportional Fitting (IPF) Optimisation

While the analytic solution provides an unbiased baseline estimation,  the diagonal entries ${x}_{ii}$ are greater than zero.

For example, consider the diagonal entries for the unadjusted *Maximum Entropy* matrix for the year *2022*:

![alt text](https://github.com/j-c-wilson/liquidity-contagion/blob/main/Matrix%20Adjustments.png "Non-Zero Diagonal Entries")

This mathematically implies that an institution lends capital to itself, which violates structural accounting principles. To force a realistic network topology, we must enforce a zero-diagonal constraint: 
$${x}_{ji} = {0} \text{ if } j = i.$$

The IPF algorithm proceeds as follows:

 - Initialize the exposure matrix using the closed-form *Maximum Entropy*
   solution, and set each diagonal entry to be zero.
 - Fix the columns and scale each row $j$ so that the sum of its entries
   matches the true balance sheet asset total ${A}_{j}$.
 - Fix the rows and scale each column $i$ so that the sum of its entries
   matches the true balance sheet liability total ${L}_{i}$.
 - Calculate the row and column errors as the difference between the
   estimated matrix and the balance sheet numbers it is required to
   match. Once the larger of these two errors is below a chosen
   threshold, we stop iterating; otherwise, we scale rows and columns
   again as above.

When this loop stops, the resulting matrix gives us our definitive map of the UK interbank network which honors the real-world balance sheet numbers for all six clearing banks to a precision chosen by our threshold, which I will set as ${10}^{-4}$, which, with data in the thousands of pounds, represents a precision of ten pence.

### Other Modelling Choices

We select these five balance sheet entries because they isolate the purest, highly liquid and volatile bank-to-bank connections. They discard the accounting "noise" of retail accounts and illiquid loans. On the asset side, adding $\text{Cash and due from banks}$ to $\text{Securities agreed to be resold}$ measures a bank's immediate emergency fund. It captures both standard cash accounts and secured short-term lending, giving us a realistic view of the cash a bank can use right away to survive a panic. On the liability side, tracking $\text{Trading liabilities}$ and $\text{Derivative product liabilities}$ isolates the bank's most dangerous short-term debts. These represent volatile, bank-to-bank obligations where counterparties can demand their cash or collateral back instantly overnight. Relating these to $\text{Net tangible assets}$ keeps a realistic safety net in place, ensuring our simulation tracks genuine domino effects through the banking system rather than making banks look artificially weak.

*Nationwide Building Society*, as a firm with major clearing, was excluded from this model because Nationwide reports its fiscal year-end in March while the other banks report in December. Including them would inject structural lag, as a major liquidity crunch or interest rate spike in Q4 2022 would show up instantly on Barclays' balance sheet but would be missing or warped on Nationwide's lagged statement. Excluding them preserves the synchronous timeline of the systemic shock.



# Findings

![alt text](https://github.com/j-c-wilson/liquidity-contagion/blob/main/Analysis.png "Findings")

Please note: for all monetary values stated, in matrices and elsewhere, data is recorded in thousands of Great British Pounds (GBP).

Looking across the annual graphs and matrices, one can observe a narrative about the changing state of liquidity in the UK banking system following the 2022 inflationary spike and central bank rate-hike cycles.

During *COVID-19*, central banks flooded the system with cheap liquidity. Banks took these massive customer deposits and parked them in "safe" long-term government bonds (UK Gilts). Balance sheets often report these bonds at *Amortized Cost* (Hold-to-Maturity) rather than *Fair Value* (Available-for-Sale). This means the raw balance sheet data understates the actual drop in liquidity because those unrealised losses are hidden until a bank is forced to sell them. When inflation surged in 2022, the *Bank of England* raised interest rates at the fastest pace in decades. Mathematically, when interest rates rocket upward, the market value of long-term bonds drops catastrophically.

The *Liquid Assets* on the balance sheets of these six banks would have been plagued by massive, hidden and unrealised losses. If customers suddenly pulled their *Volatile Funding*, the banks would be forced to sell these bonds at a massive loss, instantly vapourising their *Liquidity Buffers*, explaining why the model finds 2022 to be the peak window of systemic vulnerability.

In the 2022 baseline matrix, individual bank liquidity buffers are at their tightest. Three of the six banks - *NatWest, HSBC* and *Santander* - are running a negative baseline liquidity buffer, meaning they are highly efficient in a low-rate environment but highly exposed to sudden capital shocks. This is exactly why the 2022 network shows immediate, acute vulnerability when runoff stress sweeps across the system, and it is therefore little surprise that *NatWest* is the bank that is first to experience an initial breach when $α$ increases from 0.4 to 0.5 in 2022.

By 2025, bank behaviour undergoes a structural shift. Only *Santander* has a negative initial buffer, and the other five banks have significantly larger positive buffers. This reflects industry-wide precautionary liquidity hoarding, which is perhaps in response to the high-profile bank failures of 2023 (like *Silicon Valley Bank* and *Credit Suisse*). This shows these banks aggressively retained cash, widened their asset buffers, and pulled back from aggressive funding markets. It is worth noting that, even at the highest runoff rates, the 2025 graph shows just one initial breach and no subsequent failures, whereas in each of the three other years investigated, we observe at least five of the six banks being breached at high runoff rates. This is a testament to the large buffers and the structural shift over this period.

Across all years, *Barclays* and *HSBC* consistently emerge as the systemic anchors of the network. For example, in 2022, using the model, *Barclays* holds a massive $£220.4B$ exposure to *HSBC*, while *HSBC* holds $£179.3B$ against *Barclays*. Note that these numbers are significantly larger than any others observed in the liability matrix, and this pattern is preserved for the other three years. This establishes a highly concentrated core made up of these two banks in the UK system. If either of these banks moves into breach territory, the massive bilateral exposure ensures the immediate destruction of the other's buffer. Based on the simulations, there is not a single case across any of the evaluated years where either *HSBC* or *Barclays* fails while the other survives. This simulation dynamic provides powerful evidence of the notion that these two institutions act as the dual core stalwarts of the system and share an exceptionally heavy interbank connection.

The core mathematical finding, however, is that systemic risk is highly non-linear and exhibits catastrophic tipping points.

Under lower runoff constraints, the network is perfectly stable. Individual balance sheets take damage, but their isolated liquidity buffers completely absorb the cash strain. This is where conventional regulatory metrics (like the LCR) create a false sense of security. Because no individual bank hits a negative stressed asset position, a regulator looking at individual entities would declare the UK banking sector perfectly safe.

As one example, once the runoff rate hits 50% in 2022, the collapse of *NatWest* combined with already heavily depleted buffers (as a result of the initial 50% runoff) means counterparties do not have the margin to absorb a second shock. The cascade rapidly hits the *Barclays-HSBC* core, and *Santander* observes a negative buffer also, creating a massive liquidation wave that instantly wipes out the remaining survival buffers of *Lloyd's* and *Standard Chartered*. The cascade size jumps non-linearly from 0 failed banks to all 6 failed banks in a single step.

In 2024, the baseline balance sheets show that three banks - *HSBC, NatWest,* and *Santander* - started the year with a negative initial liquidity buffer, yet there were zero initial failures at lower runoff rates. When the runoff rate is very low, the simulated market run is only pulling out a tiny fraction of the *Volatile Funding*, meaning, even though a bank like *HSBC* has more total short-term liabilities than liquid assets over this year, a sudden 30-day run of only 10% of those funds doesn't overpower the assets. This proves that the system shifted from an unconditional vulnerability in 2022, where a small run caused immediate defaults, to a conditional vulnerability in 2023–2024, where the sheer volume of *Liquid Assets* held was large enough to easily absorb low-magnitude shocks, even if the absolute annual accounting buffers looked underwater.

Considering the 2025 Liability Matrix, *Santander* has exposures to *Barclays* of $£54.5B$ and to *HSBC* of $£22.0B$ as two examples. If Santander were to experience a liquidity breach (as they do with higher runoff rates), the shock is entirely nullified in terms of the most severe consequences; as $Barclays$ holds $£379.8B$ in *Liquid Assets* and *HSBC* holds $£244.1B$, the incoming hits from a *Santander* failure are completely swallowed up by the surviving banks' multi-billion-pound defenses, showing the queue empties after its first breach. The other banks have significantly larger asset totals than their exposures to *Santander*, showing why *Santander* is the lone failure at higher runoff rates in 2025.

It is worth noting that a 50% runoff rate within a single cycle used to be considered an impossible academic abstraction until March 2023, when *Silicon Valley Bank* lost 25% of its deposits in a single afternoon via smartphone apps and digital panic, proving that modern runs make the 50% tipping-point scenario observed in 2022 a genuine risk for these banks.



# Improvements, methodological limitations and technical assumptions
My script will absolutely identify the correct final list of failed banks for a given runoff rate. This is because liquidity contagion is a monotonic process: if $\text{Bank A}$’s failure forces a surviving bank’s buffer below zero, adding a subsequent shock from $\text{Bank B}$’s failure can only push it deeper into a deficit. However, it possesses a structural limitation regarding the exact financial numbers reported at the end of a cascade. The algorithm uses a queue system where a bank is marked as 'breached' the moment its *Liquidity Buffer* drops below zero, causing the code to stop tracking any further incoming hits to that specific bank. Because liquidity damage only flows one way, this shortcut does not change the final list of failed banks. However, it does mean the final negative buffers are artificially small. In a real crisis, a bank that is already failing would continue to take massive damage as its peers collapse, a compounding effect that my current tracking metrics omit. This means my model is a liquidity framework and not an algorithm used to depict full clearing.

The model could be extended to bank exclusion capabilities. By running counterfactual simulations that completely remove a major hub, such as *Barclays* or *HSBC*, from the asset-liability matrix, the resulting shifts in cascades could be measured. Observing which institutional exclusion produces the steepest decline in total system vulnerability would provide a clear, network-theoretic identification of the primary driver of systemic risk and the most systemically important bank.

Using *Iterative Proportional Fitting (IPF)* to clear the matrix requires the data to be perfectly clean and synchronised. I cleaned the data and selected columns of interest beforehand; note that this must be done in a designated section of the code if dealing with a raw dataset. A notable data-cleaning choice was the deliberate exclusion of *Nationwide Building Society*; this was an active modelling requirement to keep the row and column margins mathematically consistent, preventing the algorithm from getting trapped in an infinite non-convergence loop due to structural scale asymmetries.

For *Standard Chartered PLC*, the *Yahoo Finance* data does not report a separate *'Trading liabilities'* line item in any of the four years of interest. A review of the bank’s annual report (Standard Chartered 2026a) and Pillar 3 disclosures (Standard Chartered 2026b) confirms that its market risk represents only 12% of risk-weighted assets and that it maintains no active proprietary trading teams, which explains the absence of standard trading liability entries. Consequently, we conservatively defined the bank's *Volatile Funding* using its reported *'Derivative Product Liabilities'* alone, creating a deliberate lower-bound estimate of its systemic exposure footprint. Under international financial reporting standards (IFRS 9), any negligible non-derivative trading balances are consolidated into broader fair-value accounting categories due to lack of material systemic scale, validating the empirical accuracy of using this value alone in each year as *Standard Chartered’s* volatile interbank risk.

Regarding the IPF framework, if the model features a bank $i$ where its volatile funding is greater than or equal to the sum of all other banks' *Liquid Assets* combined, the algorithm will hit a deadlock. This happens because of the explicit setting of the diagonal to zero to stop a bank from lending to itself. If bank $i$ owes more than the rest of the environment can possibly lend it, the algorithm will infinitely loop, endlessly scaling rows up and columns down, never satisfying the tolerance threshold. In reality, economic, regulatory, and market forces act as automatic circuit breakers that stop a balance sheet from ever reaching this extreme distortion.

Given that we use the *Maximum Entropy* framework, a prominent structural limitation of this methodology is the inherent information asymmetry regarding the true bilateral relationships between individual financial institutions. By deploying the *Maximum Entropy* algorithm, this model is forced to assume that interbank obligations are distributed as smoothly and evenly across the network as mathematically possible given the marginal balance sheet constraints to give a reliable and unbiased baseline for systemic stress testing. It cannot, however, capture real-world relationships that naturally deviate from this topography. $MaxEnt$ also artificially overestimates the connectivity of the network (everyone lends to everyone), which can underestimate systemic risk by spreading shocks too smoothly, or conversely, create unrealistic domino paths. Real-world networks exhibit much higher sparsity than a $MaxEnt$ estimation allows.

The reduction of complex, multi-layered financial operations into my chosen three metrics - *Liquid Assets, Volatile Funding,* and *Tangible Equity* - intentionally simplifies how we look at a bank's true risk profile. In a real-world liquidity crisis, a bank's survival depends on many moving parts, such as how fast everyday retail customers pull their savings, unexpected off-balance-sheet demands, which assets the bank can use as collateral, and how quickly management can launch emergency recovery plans. By treating the *Liquidity Buffer* as a simple, static math problem, our model leaves out these fluid elements, so my model should be viewed as a clear structural assessment of a bank's basic cash defenses, rather than a literal depiction of an adverse event.



# Conclusion
This study finds that enforcing compliance to microprudential liquidity frameworks alone, specifically the *LCR*, is not enough to ensure macroprudential stability. The non-linear transitions observed in the 2022 and 2023 networks demonstrate that an interbank system can transition instantaneously from apparent equilibrium to catastrophic domino collapse. This occurs because these frameworks fail to account for the dense network of liabilities mapped as suitably as possible without prior knowledge by our *Maximum Entropy* topography.

While hoarding massive liquid asset buffers is a highly sensible defensive strategy that protects the network against systemic collapse, it introduces a severe structural trade-off. The profound fortress-like resilience observed in the 2025 baseline balance sheets came as banks aggressively pulled back from wholesale lending markets to hold cash. In a broader macroeconomic context, this defensive cash hoarding carries a heavy systemic opportunity cost: it traps capital that would otherwise aid productive economic credit expansion, potentially stalling GDP growth.

For bank supervisors such as the *Bank of England*, these results vindicate the need to move from traditional, independent balance-sheet monitoring toward network-aware macroprudential regulation. This could include introducing strict regulatory concentration caps on the maximum allowable bilateral exposure lines between banks, as it is almost inevitable that each of the ‘major’ pair of *Barclays* and *HSBC* would fail if the other were to do so. Regulation would ensure that a failure of a peripheral node or core giant cannot travel across the network's structural fault lines to trigger a total systemic shutdown.



# Citations
### Data Sources
Yahoo Finance (2026a) Barclays PLC (BARC.L) Balance Sheet. Available at: https://uk.finance.yahoo.com/quote/BARC.L/balance-sheet/ (Accessed: 6 June 2026).

Yahoo Finance (2026b) HSBC Holdings plc (HSBA.L) Balance Sheet. Available at: https://uk.finance.yahoo.com/quote/HSBA.L/balance-sheet/ (Accessed: 6 June 2026).

Yahoo Finance (2026c) NatWest Group plc (NWG.L) Balance Sheet. Available at: https://uk.finance.yahoo.com/quote/NWG.L/balance-sheet/ (Accessed: 6 June 2026).

Yahoo Finance (2026d) Lloyds Banking Group plc (LLOY.L) Balance Sheet. Available at: https://uk.finance.yahoo.com/quote/LLOY.L/balance-sheet/ (Accessed: 6 June 2026).

Yahoo Finance (2026e) Standard Chartered PLC (STAN.L) Balance Sheet. Available at: https://uk.finance.yahoo.com/quote/STAN.L/balance-sheet/ (Accessed: 6 June 2026).

Yahoo Finance (2026f) Banco Santander, S.A. (BNC.L) Balance Sheet. Available at: https://uk.finance.yahoo.com/quote/BNC.L/balance-sheet/ (Accessed: 6 June 2026).

### Academic Sources
Allard, D., D'Or, D. and Froidevaux, R. (2011) 'An efficient maximum entropy approach for categorical variable prediction', European Journal of Soil Science, 62(3), pp. 381-393. Available at: https://doi.org/10.1111/j.1365-2389.2011.01362.x.

Aldasoro, I. and Alves, I. (2018) 'Multiplex interbank networks and systemic importance: An application to European data', Journal of Financial Stability, 35, pp. 17-37. Available at: https://doi.org/10.1016/j.jfs.2016.12.008.

Eisenberg, L.K. and Noe, T.H. (2001) 'Systemic risk in financial systems', Management Science, 47(2), pp. 236-249. Available at: https://doi.org/10.1287/mnsc.47.2.236.9835.

Standard Chartered (2026a) Annual Report 2025. London: Standard Chartered PLC. Available at: https://uk.finance.yahoo.com/quote/STAN.L/balance-sheet/ (Accessed: 9 June 2026).

Standard Chartered (2026b) Pillar 3 Disclosures 2025. London: Standard Chartered PLC. Available at: https://uk.finance.yahoo.com/quote/STAN.L/balance-sheet/ (Accessed: 9 June 2026).

Upper, C. (2011) 'Simulation methods to assess the likelihood and extent of systemic interbank contagion: A survey', Journal of Financial Stability, 7(1), pp. 15-25. Available at: https://doi.org/10.1016/j.jfs.2010.08.001.
