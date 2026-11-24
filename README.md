# AuditReel: an evidence-to-storyboard demo

AuditReel shows how to turn structured audit notes into a short, timestamped storyboard without making up findings. The demo uses only fictional records from a fictional website. Every factual beat includes its evidence IDs, and the validator completes before any storyboard is printed.

## Run it

```sh
python3 auditreel.py synthetic_audit.json
python3 -m unittest -v
```

The example returns a 21-second **text storyboard**, from a 3-second introduction to three 6-second findings. Each finding contains suggested narration, a visual instruction and its source IDs. No audio or video is produced. Python's standard library is sufficient.

## What blocks output

- Input must explicitly declare itself synthetic and use unique `SYN-` evidence IDs. The flag is a convention, not proof of where arbitrary input came from. Run only with invented records.
- Each requested topic needs evidence dated within the configured window as of the supplied date. Future-dated evidence is also rejected.
- Multiple records supporting the same topic must use the same observation text after trimming. This is a deliberately conservative exact-text rule, not semantic fact-checking.
- Missing, stale, conflicting or invalid data exits with code 2 and no partial storyboard.

This is a standalone portfolio simulation written for public review. The original project code and materials are not included. It does not collect data, access the network, contact anyone or publish anything.
