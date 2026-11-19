# Verification scope

The evaluation input is a sum per execution, configuration and seed. It supports Table 6 and the five primary test contrasts in Table 7. Fold numerators and denominators are pooled before calculating a seed's forward-chaining MRR. Each fitted seed receives equal weight. Empty targets contribute zero RR; positive-case Recall@3 is the mean of per-case fractions of distinct targets in the top three. The common ranking puts observed types last and uses the frozen candidate order to break ties.

For Table 7 the five seed differences share a paired execution draw. Each draw uses its own eligible-case denominator. Pointwise percentile intervals use 2000 PCG64 draws with seed 20260808 and linear interpolation. The original decision requires complete coverage, mean difference at least 0.01, lower bound strictly above zero and at least four positive seeds.

Table 4 counts executions with zero eligible cases in the generation population. Figure 6 uses fold sums under both ranking rules. Figure 8 compares labels with the source rows of S23, S26 and S54. Figure 10 supplies stored case targets, top-five lists and selected ranks, for the three illustrated cases and seed 20260716. Other tables and diagrams are indexed by caption and can be consulted in the paper or supplement.

The conditional-frequency and fixed-call-budget analyses are descriptive additions following the original test evaluation. The author reproduction record covers final training to Test for the relation indicator at seed 20260716. The observed-status configuration record documents training and feature disagreement. These records do not supply a performance contrast between the two indicator models.

The package contains derived numerical summaries. Obtain source reports separately from the original providers. Feature matrices, fitted weights and original execution identifiers are outside the release. Reconstructing individual predictions or refitting the models requires inputs beyond the public summaries.


For Table 4, eligible and target-positive counts in forward chaining, validation and the primary test set are summed once per execution using one configuration and seed after denominator agreement checks. Training, auxiliary test and generated totals are cross-checked against the preserved population counts in data/populations.csv. Test auxiliary execution-level membership is outside the released data.

For Table 6, Table S66 documents the original configurations. The additional conditional-frequency row comes from the subsequent conditional-frequency analysis and the released execution sums. Overall test MRR uses 29,222 eligible cases, including 1156 empty targets. Positive-case test MRR and Recall@3 use 28,066 cases.

Figure 6 recalculates 16 points from 240 fold- and seed-level sums. Figure 8 cross-checks the exact four overall test ratio groups and 16 split-by-ratio-by-condition groups. Figure 10 checks the 12 case-model combinations using the stored lists and target sets. Additional stored rank fields establish ranks 8 and 12. The alphabetic case labels identify illustrations; the model_B and model_C entries identify training configurations.

For Section S4, the nine stored MRR values and applicable execution counts are cross-checked for the eligible population, for each of three budgets and three configurations. The common-execution population is reported separately in the same result file.
