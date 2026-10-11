# Prediction and measurement provenance

The two attached source files are copied byte-for-byte into `data/` with descriptive names. Python never overwrites these inputs.

| Dataset | Origin |
|---|---|
| `data/measured_temperature.csv` | Uploaded `EGN321_Module6_Assignment6_2_1800_Measured.csv` |
| `data/predicted_temperature.csv` | Uploaded `EGN321_Module6_Assignment6_2_1800_Predictions.csv` |

Both files contain 1,800 matching sample and UTC timestamp pairs, and both label the measured/predicted variable as temperature in Celsius. These facts support **data-level alignment**, not independent verification of the actual environment or simulation model.

## Unverified original model

The prediction file does **not** include the earlier engineering function, its repository/commit, or the assumptions used to calculate `predicted_temperature_c`. Accordingly this submission uses the permitted **prediction output** integration path and does not describe it as an independently reproduced earlier-tool calculation. If the instructor requires direct proof of reuse from Modules 1–4, attach the relevant original source code and explain how it generated this prediction CSV.

The provided `ivansuarez-AU/EGN321_Module6_Assignment6_2` GitHub link is an instructor reference project, not the student's owned repository; uploading into it is not authorized by the current GitHub permissions.

- SHA-256 (`measured_temperature.csv`): `e5bbd55d2ebd93c07108827949e026f2aaedba166baa31d441fa5030e5744eb7`

- SHA-256 (`predicted_temperature.csv`): `fce36ce6444b7f3f742c5f28ffad4f207032f5b47b7fbdb21e4849a2b719a3fc`

## Student GitHub submission

The student-owned project repository is https://github.com/Barquito0/EGN-321-Module-6_2. The instructor example under `ivansuarez-AU` is not modified.
