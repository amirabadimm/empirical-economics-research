# Project independence

User requirement (2026-09-08): each research project should be independently presentable and
runnable for a professional portfolio.

## Asset allocation

Own README, scope, source contract, dependency manifest, and local data/output layout.
No sibling source imports exist. Source adapters are not implemented. Source paths in future
code must resolve from this project or explicit configuration, never a hard-coded workstation.
The project is still a folder in the parent Git repository, not a separate repository.

## Existing workspace audit

Commodity collectors import shared.ime_data. Copper/Zinc also use shared.market_data and
shared.market_analysis. Commodity notebook infrastructure uses shared.notebook_tools. These
projects currently depend on the workspace layout. E:/Housing is already a separate Git
repository; this audit did not modify it. Energy Exchange, Codal, and Options need a fuller
installation/path audit before claiming portable execution.

## Migration acceptance criteria

Each project needs its own install instructions and dependency manifest, explicit data inputs,
project-relative output paths, reproducible commands, meaningful tests, and a concise research
README with methodology, results, and limitations. A clean checkout must work without a sibling
research project. Common infrastructure can remain a separately installable, versioned package;
shared raw inputs retain one canonical owner and are provided through explicit configuration.
Avoid copying evolving helpers or moving immutable snapshots as a shortcut.

Repository topology is pending: separate Git repositories versus independently runnable folders
in one portfolio repository. No existing projects have been moved, repackaged, or split yet.
