# Late-game document art — waves 8–9

These SVG props supplement canonical documents in the existing adventure. They do not replace authoritative text in `studio/content/TIHAYA_VODA/adventure.json`, and they add no actions, quests, flags, events, or endings.

## Wave 8 — existing props
- `D24_personal_page.svg`: unnumbered handwritten confession page, living module, chapter 11.
- `D25_outgoing_receipt.svg`: outgoing-mail receipt with intentionally conflicting dates, archive, optional chapter 11.
- `D26_irina_door_note.svg`: handwritten note taped to a cold metal door, gallery, chapter 12.

## Wave 9 — integrated props
- `D27_radio_transmission.svg`: archival radio transcript with waveform for the 2028 Mayak-9 emergency call, chapter 6.
- `D28_generator_bus_panel.svg`: load-distribution panel illustrating existing bus limits, diesel room, chapters 2/11.
- `D29_anna_draft.svg`: unsent draft beside a camera-frame prop, archive, chapters 8–9.

The build embeds the SVGs as data URIs in both the offline `game/index.html` payload and the public Pages preview, so they work offline and add no runtime network requests. The shared adventure UI renders the illustration when reading a document and from the saved journal. Canonical document text remains visible and authoritative.
