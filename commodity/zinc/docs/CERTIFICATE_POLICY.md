# Agent Instructions — Zinc Certificate

Raw data is immutable, full snapshot must be maintained, collector must be incremental,
remain idempotent and atomic. Both old and new codes are a continuous tool. volume days
Keep zero in raw and remove only in price analysis. Schema change or validation failure must
Stop pipeline execution.
The analytical underlying is limited to the 99.97/99.98 grade basket with cash or cash-matching contracts;
The extended raw should not be removed or rewritten to achieve this scope. Physical daily price
with weight `Quantity`, certificate price with `TodaySettlementPrice` and intrinsic price with
`LME cash / 1000 × USD/IRR` is created. In the main method only between real anchors
Interpolation and any extrapolation is prohibited.
