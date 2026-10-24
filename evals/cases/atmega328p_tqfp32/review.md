# Review — ATmega328P-AU, Microchip TQFP-32, datasheet 7810D-AVR (automotive)

Round-1 GOLD-verdict import, no review at the time. This file was created 2026-10-14 to record
the MPN-001 adjudication for this case.

## MPN (checked 2026-10-14, no change — escape clause)

`ATmega328P-AU` is kept. This revision of the datasheet is the **automotive** document
(Atmel-7810-Automotive), and its ordering information (p.285) lists only the automotive
orderables for the part: `ATmega328P-15AZ` (package MA) and `ATmega328P-15MZ` (package PN), both
2.7-5.5 V / 16 MHz. The AU (TQFP-32) orderable this gold records is not printed anywhere in this
revision — a token-boundary search confirms `ATmega328P-AU` appears on no page.

Per `reference.md`'s mpn paragraph the fallback is "use the number it does print and say so in the
hand-over"; here the sheet prints no orderable for the TQFP-32 case at all, so the gold keeps the
standard Microchip orderable for the package and records the discrepancy here: a consumer needing
a string this exact PDF prints for the TQFP-32 variant will not find one. If a future round
adopts the non-automotive ATmega328P datasheet revision (which lists `ATmega328P-AU` in its
ordering table), this note is the place to swap the citation.
