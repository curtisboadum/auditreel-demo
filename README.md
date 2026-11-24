# AuditReel

**Turn audit evidence into a short storyboard a reviewer can verify.**

Audit notes often lose their source references when they become a script. AuditReel keeps the evidence ID alongside each finding and stops the entire script if a requested topic lacks fresh, consistent evidence. This standalone Python demo uses an invented website audit and runs offline.

## See the result

The included sample produces a **21-second text storyboard**:

| Time | Narration or direction | Evidence |
| --- | --- | --- |
| 00:00–00:03 | Introduce the fictional audit on a title card. | None; introduction only |
| 00:03–00:09 | The fictional booking page does not show session length. | `SYN-01` |
| 00:09–00:15 | The fictional contact page lists an email form but no phone option. | `SYN-02` |
| 00:15–00:21 | The fictional mobile menu puts Help under a second menu. | `SYN-03` |

The CLI returns JSON with start and end times, narration, a visual instruction, and evidence IDs for each beat. Timings are fixed planning slots, not measured spoken durations.

## Run it

From the repository root, with Python 3 (verified on 3.9.6):

```sh
python3 auditreel.py synthetic_audit.json
python3 -m unittest -v
```

No packages, API keys or network access are required. The example pins its review date in the input so it remains reproducible.

## What gets blocked

- **Missing evidence:** Every requested topic needs at least one record.
- **Stale or future-dated evidence:** Every record must fall within the configured freshness window relative to the review date.
- **Conflicting evidence:** Records for one topic must have identical observation text after trimming. Matching records keep all their evidence IDs.
- **Invalid input:** The schema requires a synthetic-data declaration and unique evidence IDs that start with `SYN-`.

If a check fails, the CLI exits with code **2**, prints a diagnostic to stderr, and emits no partial storyboard. The test suite checks the successful path and the failure cases, including the absence of partial CLI output.

## Scope

This is a public portfolio simulation, not the full AuditReel project. It does not collect evidence, decide whether an observation is true, reconcile equivalent wording, or render audio or video. The synthetic declaration is an input convention, not proof of provenance. Use only invented records.

## Licence

[MIT](LICENSE)
