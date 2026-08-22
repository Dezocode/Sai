# Handoff 20260822-0211-pr73-rebase-lifecycle-cursor-cloud

OBSERVED_START_HEAD=`3c3c7767d397df8492eb15e023a7d4d237be2692`
ACTUAL_START_HEAD=`3c3c7767d397df8492eb15e023a7d4d237be2692` (no discrepancy vs observation)
PRIOR_START_HEAD=`7edbe3a2e95804231428f5e61bfb11c147a46073`
MERGE_HEAD=`5697d732f252c36dcc2dd88ee345a1d49fb31e03`
LIFECYCLE_HEAD=`18831aa1e11b281ca2e8c5bb537f6fc252488abe`
XCCONFIG_HEAD=`8aa271fb1b4cedb133b728fcaa47f89559aab655`
UNIT10_HEAD=`3c3c7767d397df8492eb15e023a7d4d237be2692`
BASE=`d40cf3346f263478895607c810ce0b30ede12a1e`
FINAL_HEAD=pending this push

Draft PR 73. Original /goal unchanged. Do not merge.

Reproduced @ 3c3c776: candidate `codePolicy` paths could widen the exempt tree, relocate the feature lock, and skip token bind when `SaiDesignLanguage.swift` is missing; `featureUIAllowed=false` only covered `SaiFeatures`; `SaiText` used unsized `Font.system(size:)`. Fixed: verifier-owned roots, fail-closed bind, global View lock except design authority + SaiMac/SaiIOS entries, `relativeTo: .title2`.

Historical Saul: 96967347020 @ 8aa271f ACTION_REQUIRED (UNIT-0010/0022, fixed on 3c3c776). 96968318437 @ 3c3c776 infra/neutral, not SUCCESS. Binding Saul for the new HEAD is pending.
