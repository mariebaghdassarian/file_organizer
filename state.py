"""
state.py — Mutable application state shared across modules.

These are simple module-level variables.  Any module that needs to read
or write the current folder selection or sort format imports this module
and accesses (or mutates) the variables directly::

    import state
    state.media_source = chosen_path
    if state.sort_format == "year": ...
"""

# Currently selected source folder for the Media tab (empty = not yet chosen)
media_source: str = ""

# Currently selected source folder for the Documents tab
doc_source: str = ""

# Sort format for the Media tab: "year_month" → YYYY/YYYY-MM  |  "year" → YYYY
sort_format: str = "year_month"
