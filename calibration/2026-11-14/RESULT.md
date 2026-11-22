# Mixed blind calibration result

The author completed and committed all human labels before the matching hidden
judge run was created. The signed packet and judge capture matched, and all ten
judge calls completed successfully.

| Metric | Compared labels | Exact agreement |
| --- | ---: | ---: |
| Correctness | 8 | 100% |
| Faithfulness | 8 | 100% |
| Abstention | 2 | 100% |

There were no disagreements. The judge also scored all eight answerable outputs
as correct and fully faithful, and both unanswerable outputs as successful
abstentions.

This is a small, single-reviewer development calibration. It supports using the
same frozen judge contract for the one-time reserved-test report, but it does
not establish universal judge reliability or general RAG accuracy.
