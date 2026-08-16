# MechInterp Notes

Static Chinese paper explainers for `zehaojin.com/mechinterp/`.

## Build

```bash
python3 mechinterp/build.py
```

The builder has no third-party dependencies. It generates the library index and one semantic, SEO-ready HTML page per paper. Shared presentation and interaction live in `static/style.css` and `static/site.js`.

Each paper follows the same review contract: research question, method, findings, evidence audit, connection to Zehao's research, and interview follow-ups. Keep author claims and editorial audit separate when adding new entries.
