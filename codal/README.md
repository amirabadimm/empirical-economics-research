# Codal Company Research

This domain contains issuer-level research built from disclosures published through Iran's
Codal disclosure system. Each listed company has an independent project under
`codal/<company>/`, with its own source contracts, data lineage, processing code, tests, and
research documentation.

## Companies

- [National Iranian Copper Industries Company](national_copper/README.md) (`national_copper`;
  Tehran Stock Exchange ticker: `فملی`)

Cross-company Codal collection logic may be extracted into a shared package only after a stable
source contract is implemented. Until then, company filters and identifiers remain explicit in
the relevant company project.
