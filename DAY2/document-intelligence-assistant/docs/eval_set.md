# Draft Eval Set (20 questions)

Source: `evals/dataset.jsonl`. Run with `python -m evals.run_evals` after `python -m scripts.ingest_pdfs`.

Metrics: citation hit (right document + page), answer correct (key fact present), tool use as expected, refusal on not-in-manual questions, latency.

| # | Manual | Question | Type | Expected page(s) | Answer must contain | Tool? |
|---|---|---|---|---|---|---|
| 1 | Falcon X200 | What engine oil grade does the Falcon X200 need? | fact | 2 | 5W-30 | no |
| 2 | Falcon X200 | How often should the brake fluid be replaced on the Falcon X200? | fact | 5, 7 | 2 years | no |
| 3 | Falcon X200 | What is the minimum brake pad thickness on the Falcon X200? | fact | 5 | 3 mm | no |
| 4 | Falcon X200 | What is the Falcon X200 wheel nut torque in lbf-ft? | tool | 3 | 79. | yes |
| 5 | Falcon X200 | What are the steps to change the engine oil on the Falcon X200? | steps | 4 | drain plug, 4.2 | no |
| 6 | Aurora E5 | How long does a DC fast charge from 0 to 80 percent take on the Aurora E5? | fact | 5 | 35 minutes | no |
| 7 | Aurora E5 | What is the wheel nut torque for the Aurora E5? | fact | 3 | 120 | no |
| 8 | Aurora E5 | What is the front tyre pressure of the Aurora E5 in bar? | tool | 2 | 2.4 | yes |
| 9 | Aurora E5 | How long must I wait after switching off before working on the Aurora E5 high-voltage system? | fact | 4 | 10 minutes | no |
| 10 | Aurora E5 | Where is the service plug located on the Aurora E5? | fact | 4 | rear seat | no |
| 11 | Aurora E5 | How often should the cabin air filter be replaced on the Aurora E5? | fact | 6 | 15,000 | no |
| 12 | Nomad T300 | What engine oil grade does the Nomad T300 need? | fact | 2 | 5W-40 | no |
| 13 | Nomad T300 | How much engine oil does the Nomad T300 take? | fact | 2 | 7.5 | no |
| 14 | Nomad T300 | What is the Nomad T300 wheel nut torque in lbf-ft? | tool | 3 | 103 | yes |
| 15 | Nomad T300 | What is the Nomad T300 fuel tank capacity in gallons? | tool | 2 | 21.1 | yes |
| 16 | Nomad T300 | How often should the fuel filter be replaced on the Nomad T300? | fact | 4, 6 | 30,000 | no |
| 17 | Nomad T300 | What is the maximum speed for driving in 4L on the Nomad T300? | fact | 5 | 40 km/h | no |
| 18 | - | What is the price of the Falcon X200? | not_in_manual | - | must say not found | no |
| 19 | - | What is the warranty period of the Aurora E5? | not_in_manual | - | must say not found | no |
| 20 | - | How do I replace the clutch on the Nomad T300? | not_in_manual | - | must say not found | no |

Note: Q2 and Q16 appear on two pages each, so either page counts as a hit. Questions 18-20 are not covered by any manual; the correct behaviour is `found: false`.
