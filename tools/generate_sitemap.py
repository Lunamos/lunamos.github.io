#!/usr/bin/env python3
"""Deprecated shim.

Sitemap generation now lives in tools/build.py, which also pre-renders the
static blog pages and the RSS feed (all three must stay in sync). This wrapper
just forwards to it so old muscle memory / scripts keep working.

    python3 tools/build.py        # preferred
    python3 tools/generate_sitemap.py   # still works, runs the full build
"""
from build import main

if __name__ == "__main__":
    print("[generate_sitemap.py is deprecated — running tools/build.py instead]")
    main()
