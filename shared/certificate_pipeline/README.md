# Certificate research engine

One execution interface for copper, zinc, pellet, rebar, bitumen, and pistachio.
Local pipeline.json files select source collectors and ordered product builders.
Economic filters and formulas remain in the product projects.

From the workspace root:

    python -m shared.certificate_pipeline.refresh all --plan
    python -m shared.certificate_pipeline.refresh all
    python -m shared.certificate_pipeline.refresh copper --collect

Default execution rebuilds from existing inputs. --collect runs the registered source
collectors first, with shared FX collected once per all-project run. --plan performs
no collection or writes. Pistachio's company workbook must still be supplied manually.
The closed global-copper research collectors are excluded.

Each product retains refresh_powerbi.cmd and refresh_powerbi.py as compatibility
entry points. Results retain their existing filenames and 14-column delivery schema.
Bitumen now stores its comparison in processed/bubble before publishing the delivery
copy and adds empirical-distribution outputs.

Stages fail fast. Each existing builder retains its atomic-file behavior; the run is
not a transaction across all datasets. Earlier processed outputs may have been rebuilt
when a later stage fails, but that product's delivery export is not published.
Network collection is optional and must never be implied by a successful offline rebuild.

For an academic portfolio, report source provenance, the economic question, methodology,
reproduction command and actual findings for each product. Distinguish deployed software
from approval of economic comparability. Empirical CDFs describe historical samples and
do not establish predictive performance or arbitrage profitability.

This integration centralizes execution and delivery. Existing product locations and
notebook layouts are retained for compatibility; further layout migration is separate.
