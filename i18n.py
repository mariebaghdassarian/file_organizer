"""
i18n.py — Internationalisation.

Contains all user-visible strings in French and English.
Use t("key") anywhere in the codebase to get the current translation.
Call set_lang("fr") / set_lang("en") to switch language at runtime.
"""

_current_lang: str = "fr"

TRANSLATIONS: dict[str, dict[str, str]] = {
    "fr": {
        # Window & tabs
        "window_title":       "Organisateur de Fichiers",
        "tab_media":          "📷  Médias",
        "tab_docs":           "📄  Documents",
        # Folder selector
        "no_folder":          "📁  Aucun dossier sélectionné",
        "choose_folder":      "CHOISIR UN DOSSIER",
        # Media tab
        "sort_format_label":  "Format de tri",
        "fmt_ym":             "Année / Mois",
        "fmt_y":              "Année",
        "sort_btn_ym":        "TRIER PAR DATE  (YYYY / YYYY-MM)",
        "sort_btn_y":         "TRIER PAR DATE  (YYYY)",
        # Docs tab
        "sort_docs_btn":      "TRIER PAR TYPE DE FICHIER",
        "legend_title":       "Dossiers créés automatiquement :",
        "legend_types":       "PDF · Word · Excel · PowerPoint · Texte · Archives · Code · Autres",
        "others":             "Autres",
        # Misc
        "quit":               "Quitter",
        "manual_folder":      "_A_TRIER_MANUELLEMENT",
        # Progress windows
        "scanning":           "Analyse des fichiers…",
        "moving_media":       "Déplacement des fichiers…",
        "moving_docs":        "Déplacement des documents…",
        "collecting":         "Collecte en cours…",
        "lbl_elapsed":        "⏱  Écoulé : {t}",
        "lbl_remaining":      "⏳  Restant : {t}",
        # Warnings & results
        "warn_no_folder":     "Veuillez d'abord choisir un dossier.",
        "no_media_found":     "Aucun fichier média trouvé dans ce dossier.",
        "no_docs_found":      "Aucun document trouvé dans ce dossier.",
        "all_sorted_title":   "Tout est trié !",
        "all_sorted_media":   "{n} fichier(s) analysé(s) — tout est déjà correctement classé. 🎉",
        "all_sorted_docs":    "Aucun document à déplacer. {n} déjà bien classé(s).",
        "preview_media":      "Aperçu — {n} déplacement(s)",
        "preview_docs":       "Tri par type — {n} fichier(s)",
        "n_to_move":          "{n} fichier(s) à déplacer",
        "confirm":            "✅  Confirmer et trier",
        "cancel_btn":         "❌  Annuler",
        "result_title":       "Résultat",
        "result_ok":          "✅ Tri terminé !\n{n} fichier(s) déplacé(s).",
        "result_errors":      "\n⚠️ {e} erreur(s) — ces fichiers n'ont pas pu être déplacés.",
        "sum_already_ok":     "✅ {n} fichier(s) déjà bien classé(s) — ignorés",
        "sum_duplicates":     "🔁 {n} doublon(s) identique(s) — ignorés",
        "sum_ok_docs":        "✅ {n} fichier(s) déjà dans le bon dossier — ignorés",
    },
    "en": {
        # Window & tabs
        "window_title":       "File Organizer",
        "tab_media":          "📷  Media",
        "tab_docs":           "📄  Documents",
        # Folder selector
        "no_folder":          "📁  No folder selected",
        "choose_folder":      "CHOOSE A FOLDER",
        # Media tab
        "sort_format_label":  "Sort format",
        "fmt_ym":             "Year / Month",
        "fmt_y":              "Year",
        "sort_btn_ym":        "SORT BY DATE  (YYYY / YYYY-MM)",
        "sort_btn_y":         "SORT BY DATE  (YYYY)",
        # Docs tab
        "sort_docs_btn":      "SORT BY FILE TYPE",
        "legend_title":       "Folders created automatically:",
        "legend_types":       "PDF · Word · Excel · PowerPoint · Text · Archives · Code · Others",
        "others":             "Others",
        # Misc
        "quit":               "Quit",
        "manual_folder":      "_TO_SORT_MANUALLY",
        # Progress windows
        "scanning":           "Scanning files…",
        "moving_media":       "Moving files…",
        "moving_docs":        "Moving documents…",
        "collecting":         "Collecting files…",
        "lbl_elapsed":        "⏱  Elapsed: {t}",
        "lbl_remaining":      "⏳  Remaining: {t}",
        # Warnings & results
        "warn_no_folder":     "Please choose a folder first.",
        "no_media_found":     "No media files found in this folder.",
        "no_docs_found":      "No documents found in this folder.",
        "all_sorted_title":   "All sorted!",
        "all_sorted_media":   "{n} file(s) analyzed — everything is already correctly sorted. 🎉",
        "all_sorted_docs":    "Nothing to move. {n} file(s) already in the right folder.",
        "preview_media":      "Preview — {n} move(s)",
        "preview_docs":       "Sort by type — {n} file(s)",
        "n_to_move":          "{n} file(s) to move",
        "confirm":            "✅  Confirm and sort",
        "cancel_btn":         "❌  Cancel",
        "result_title":       "Result",
        "result_ok":          "✅ Done!\n{n} file(s) moved.",
        "result_errors":      "\n⚠️ {e} error(s) — these files could not be moved.",
        "sum_already_ok":     "✅ {n} file(s) already correctly sorted — skipped",
        "sum_duplicates":     "🔁 {n} identical duplicate(s) — skipped",
        "sum_ok_docs":        "✅ {n} file(s) already in the right folder — skipped",
    },
}


def t(key: str, **kwargs) -> str:
    """Return the translation for *key* in the current language.

    Keyword arguments are forwarded to str.format(), e.g.::

        t("result_ok", n=42)  →  "✅ Tri terminé !\\n42 fichier(s) déplacé(s)."
    """
    s = TRANSLATIONS[_current_lang].get(key, key)
    return s.format(**kwargs) if kwargs else s


def get_lang() -> str:
    """Return the current language code ("fr" or "en")."""
    return _current_lang


def set_lang(lang: str) -> None:
    """Switch the current language.  *lang* is case-insensitive ("FR", "en", …)."""
    global _current_lang
    _current_lang = lang.lower()
