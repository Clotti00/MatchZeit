########################################
# Zugriff auf Datenbasis################
# liest und validiert Excel-Daten#######
########################################

import pandas as pd
import streamlit as st

##### benötigte Tabellenblätter und Spalten in den Tabellenblättern validieren #####
# Funktion "pruefe_sheets" prüft, ob benötigten Tabellenblätter in EXCEL vorhanden sind
def pruefe_sheets(excel: pd.ExcelFile, benoetigte_sheets: list[str]):
    vorhandene_sheets = excel.sheet_names # liest alle Namen von den Tabellenblättern
    fehlende_sheets = [] # Leere Liste: Ort, um fehlende Tabellenblätter später zu speichern

    for sheet in benoetigte_sheets:
        if sheet not in vorhandene_sheets:
            fehlende_sheets.append(sheet)

    if fehlende_sheets:# Falls Tabellenblätter fehlen
        raise Exception(
            "Folgende Tabellenblätter fehlen: "
            + ", ".join(fehlende_sheets)
        )

# Funktion "pruefe_spalten" prüft, ob in Tabellenblättern die benötigten Spalten vorhanden sind
def pruefe_spalten(df: pd.DataFrame, erwartete_spalten: list[str], sheet_name: str):
    vorhandene_spalten = list(df.columns)
    fehlende_spalten = [] # leere Liste

    for spalte in erwartete_spalten:
        if spalte not in vorhandene_spalten:
            fehlende_spalten.append(spalte)

    if fehlende_spalten: # falls Spalten fehlen
        raise Exception(
            f"Fehlende Spalten im Tabellenblatt '{sheet_name}': "
            + ", ".join(fehlende_spalten)
        )

# Funktion "lade_excel_datei" zentrale Funktion, um benötigte Tabellenblätter und Spalten zu laden und zu überprüfen
@st.cache_data # EXCEL Datei wird nur einmal geladen und während der Nutzung zwischengespeichert
def lade_excel_datei(pfad: str):
    try: # alles wird versucht, falls Fehler dann wird except ausgeführt
        excel = pd.ExcelFile(pfad) # Datei wird geladen

        benoetigte_sheets = [ # die erwarteten Tabellenblätter
            "programme_info",
            "bewertungen",
            "kriterien",
            "fragen",
            "antwortmapping"
        ]

        pruefe_sheets(excel, benoetigte_sheets) # prüft, ob alle Tabellenblätter da sind

        programme_info = pd.read_excel(excel, sheet_name="programme_info") # Daten laden
        bewertungen = pd.read_excel(excel, sheet_name="bewertungen")
        kriterien = pd.read_excel(excel, sheet_name="kriterien")
        fragen = pd.read_excel(excel, sheet_name="fragen")
        antwortmapping = pd.read_excel(excel, sheet_name="antwortmapping")

        pruefe_spalten(     # jeweilige Spalten in dem jeweiligen Tabellenblatt prüfen
            programme_info,
            ["programm_id", "programm_name", "anbieter", "website", "kurzbeschreibung", "zielgruppe", "erfassungsmedium", "besonderheiten", "preis"],
            "programme_info"
        )

        pruefe_spalten(
            bewertungen,
            ["programm_id" ,"K01", "K02","K02.1", "K02.1.1", "K03", "K04", "K04.1", "K04.2", "K05", "K05.1", "K06.1", "K06.2", "K06.3", "K07", "K08", "K08.1", "K08.2", "K09", "K10", "K10.1", "K10.2", "K10.3", "K10.4", "K10.5", "K10.6", "K10.7", "K11", "K12", "K13", "K14", "K15", "K16", "K17", "K18", "K19", "K20", "K21", "K22"],
            "bewertungen"
        )

        pruefe_spalten(
            kriterien,
            ["kriterium_id", "aktiv_im_matching", "kriterium_name", "kriterium_beschreibung_1", "mapping_typen", "gewichtung_standard"],
            "kriterien"
        )

        pruefe_spalten(
            fragen,
            ["kriterium_id", "abhaengig_von_kriterium_id", "abhaengig_von_antwort", "frage_text", "antwort_datentyp", "option_1", "option_2", "option_3", "option_4"],
            "fragen"
        )

        pruefe_spalten(
            antwortmapping,
            ["kriterium_id", "antwort_text", "antwort_wert", "ziel_kriterium_id", "kriterium_beschreibung_2", "kriterium_wert"],
            "antwortmapping"
        )

        return programme_info, bewertungen, kriterien, fragen, antwortmapping # Daten an app.py zurückgeben

    except Exception as e: # Exception: Fehler bzw. unerwartetes Ergebnis während Programmausführung, Speicherung in Variable e
        raise Exception(f"Fehler beim Laden der Excel-Datei: {e}") # raise: beendet Programm an dieser Stelle und gibt Fehler aus


##########