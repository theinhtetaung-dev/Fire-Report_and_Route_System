# PDF fonts

`NotoSansMyanmar-Regular.ttf` and `NotoSans-Regular.ttf` come from
https://github.com/notofonts/noto-fonts/tree/main/hinted/ttf and are licensed
under the bundled SIL Open Font License files.

`NotoEmergency-Regular.ttf` merges both sources and renames the resulting
family to **Emergency Demo**. It covers Myanmar shaping, Latin text, digits,
and punctuation in one font. Rebuild with `python Emergency/fonts/build_font.py`.

PDF paragraphs use HarfBuzz shaping and preserve logical Unicode through
`ActualText`. Validation includes raster inspection and PyMuPDF text extraction;
some PDF readers may handle selection differently.
