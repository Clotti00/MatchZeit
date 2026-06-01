############################
##### Hilfsfunktionen ######
############################
import streamlit as st
import pandas as pd
from evaluation import zeige_evaluierungsfragebogen

#####################
# zeigt Matching Ergebnisse
def zeige_matching_ergebnisse(matching_ergebnisse, programme_info, bewertungen, kriterien):

    if matching_ergebnisse.empty:
        st.warning(
            "Es wurde kein passendes Programm gefunden. "
            "Bitte prüfen Sie Ihre KO-Kriterien."
        )
        return

    # Programminformationen ergänzen
    matching_ergebnisse = matching_ergebnisse.merge(
        programme_info,
        on="programm_id",
        how="left"
    )

    # Top 3 Programme nach Matching-Prozent
    top_ergebnisse = matching_ergebnisse.sort_values(
        by="matching_prozent",
        ascending=False
    ).head(3)

    # Top 3 Programme nach Matching-Prozent
    top_ergebnisse = matching_ergebnisse.sort_values(
        by="matching_prozent",
        ascending=False
    ).head(3)

    st.subheader("Top 3 Matching-Ergebnisse")  # kurze Ausgabe: Platz 1: Name des Programms (matching_prozent)

    for platz, (_, programm) in enumerate(top_ergebnisse.iterrows(), start=1):
        st.write(
            f"Platz {platz}: "
            f"**{programm['programm_name']}** "
            f"({programm['matching_prozent']} %)"
        )

    for platz, (_, programm) in enumerate(top_ergebnisse.iterrows(), start=1):

        st.markdown("---")

        st.header(f"{platz}. {programm['programm_name']}")

        if pd.notna(programm["kurzbeschreibung"]): # falls Information fehlt, wird nichts angezeigt
            st.subheader(programm["kurzbeschreibung"])

        if pd.notna(programm["anbieter"]): # falls Information fehlt, wird nichts angezeigt
            st.write(f"**Anbieter:** {programm['anbieter']}")
        if pd.notna(programm["zielgruppe"]):
            st.write(f"**Zielgruppe:** {programm['zielgruppe']}")
        if pd.notna(programm["erfassungsmedium"]):
            st.write(f"**Erfassungsmedien:** {programm['erfassungsmedium']}")
        if pd.notna(programm["besonderheiten"]):
            st.write(f"**Besonderheiten:** {programm['besonderheiten']}")

        st.write(
            f"**Matching:** {programm['matching_prozent']} %"
        )

        st.write(
            f"**Bewertete Kriterien:** "
            f"{programm['bewertete_kriterien']} von "
            f"{programm['moegliche_kriterien']} möglichen Kriterien"
        )

        if pd.notna(programm["website"]):
            st.link_button("Unternehmenswebsite öffnen", programm["website"])

    zeige_programmvergleich(
        top_ergebnisse,
        bewertungen,
        kriterien
    )

    st.markdown("---")

    if st.button("Evaluierungs-Fragebogen"):
        st.session_state.evaluierung_starten = True

    if st.session_state.evaluierung_starten:
        zeige_evaluierungsfragebogen()
#####################

#####################
# Vergleichstabelle Programme Ergebnisse
def zeige_programmvergleich(top_ergebnisse, bewertungen, kriterien):
    st.subheader("Programmvergleich")

    aktive_kriterien = kriterien[
        kriterien["aktiv_im_matching"] == 1
    ]

    vergleichsdaten = []

    for _, kriterium in aktive_kriterien.iterrows():
        kriterium_id = kriterium["kriterium_id"]
        kriterium_name = kriterium["kriterium_name"]

        zeile = {
            "Kriterium": kriterium_name
        }

        for platz, (_, programm) in enumerate(top_ergebnisse.iterrows(), start=1):

            programm_id = programm["programm_id"]
            programm_name = programm["programm_name"]

            programm_bewertung = bewertungen[
                bewertungen["programm_id"] == programm_id
            ]

            if programm_bewertung.empty:
                wert_text = "-"
            else:
                wert = programm_bewertung.iloc[0][kriterium_id]

                if pd.isna(wert):
                    wert_text = "-"
                elif int(wert) == 1:
                    wert_text = "✔"
                elif int(wert) == 0:
                    wert_text = "✘"
                else:
                    wert_text = str(wert)

            zeile[programm_name] = wert_text # Name der Tabellenspalte: Programm 1, Programm 2, ...

        vergleichsdaten.append(zeile)

    vergleich_df = pd.DataFrame(vergleichsdaten)

    # Zellen einfärben
    def zellenfarbe(wert):
        if wert == "✔":
            return "background-color: #c8e6c9;"
        elif wert == "✘":
            return "background-color: #ffcdd2;"
        # elif wert == "-":
        #     return "background-color: #f5f5f5;"
        return ""

    vergleich_df_styled = vergleich_df.style.map(
        zellenfarbe,
        subset=vergleich_df.columns[1:]
    )

    leg1, leg2, leg3 = st.columns(3) # Legende eingefärbte Zellen

    with leg1:
        st.markdown("🟩 **✔ Kriterium erfüllt**")

    with leg2:
        st.markdown("🟥 **✘ Kriterium nicht erfüllt**")

    with leg3:
        st.markdown("⬜ **- Keine Angabe vorhanden**")

    st.dataframe(
        vergleich_df_styled,
        use_container_width=True,
        hide_index=True
    )
#####################

#####################
# Ergebnisse speichern
def erzeuge_ergebnis_html(matching_ergebnisse, programme_info, bewertungen, kriterien):
    matching_ergebnisse = matching_ergebnisse.merge(
        programme_info,
        on="programm_id",
        how="left"
    )

    top_ergebnisse = matching_ergebnisse.sort_values(
        by="matching_prozent",
        ascending=False
    ).head(3)

    html = """
    <html>
    <head>
        <meta charset="utf-8">
        <title>Matching-Ergebnisse</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 40px;
                color: #222;
            }
            h1, h2, h3 {
                color: #111;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin-top: 20px;
                font-size: 12px;
            }
            th, td {
                border: 1px solid #ccc;
                padding: 6px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
            .programm {
                margin-top: 30px;
                padding-top: 15px;
                border-top: 1px solid #ccc;
            }
        </style>
    </head>
    <body>
    """

    html += "<h1>Matching-Ergebnisse</h1>"
    html += "<h2>Top 3 Matching-Ergebnisse</h2>"

    for platz, (_, programm) in enumerate(top_ergebnisse.iterrows(), start=1):
        html += (
            f"<p>Platz {platz}: "
            f"<strong>{programm['programm_name']}</strong> "
            f"({programm['matching_prozent']} %)</p>"
        )

    html += "<h2>Übersicht der Top 3 Programme</h2>"

    for platz, (_, programm) in enumerate(top_ergebnisse.iterrows(), start=1):
        html += f"<div class='programm'>"
        html += f"<h3>{platz}. {programm['programm_name']}</h3>"

        if pd.notna(programm["kurzbeschreibung"]):
            html += f"<p><strong>{programm['kurzbeschreibung']}</strong></p>"

        if pd.notna(programm["anbieter"]):
            html += f"<p><strong>Anbieter:</strong> {programm['anbieter']}</p>"

        if pd.notna(programm["zielgruppe"]):
            html += f"<p><strong>Zielgruppe:</strong> {programm['zielgruppe']}</p>"

        if pd.notna(programm["erfassungsmedium"]):
            html += f"<p><strong>Erfassungsmedien:</strong> {programm['erfassungsmedium']}</p>"

        if pd.notna(programm["besonderheiten"]):
            html += f"<p><strong>Besonderheiten:</strong> {programm['besonderheiten']}</p>"

        html += f"<p><strong>Matching:</strong> {programm['matching_prozent']} %</p>"
        html += (
            f"<p><strong>Bewertete Kriterien:</strong> "
            f"{programm['bewertete_kriterien']} von "
            f"{programm['moegliche_kriterien']} möglichen Kriterien</p>"
        )

        if pd.notna(programm["website"]):
            html += f"<p><strong>Website:</strong> {programm['website']}</p>"

        html += "</div>"

    html += "<h2>Programmvergleich</h2>"

    aktive_kriterien = kriterien[
        kriterien["aktiv_im_matching"] == 1
    ]

    vergleichsdaten = []

    for _, kriterium in aktive_kriterien.iterrows():
        kriterium_id = kriterium["kriterium_id"]
        kriterium_name = kriterium["kriterium_name"]

        zeile = {
            "Kriterium": kriterium_name
        }

        for _, programm in top_ergebnisse.iterrows():
            programm_id = programm["programm_id"]
            programm_name = programm["programm_name"]

            programm_bewertung = bewertungen[
                bewertungen["programm_id"] == programm_id
            ]

            if programm_bewertung.empty:
                wert_text = "-"
            else:
                wert = programm_bewertung.iloc[0][kriterium_id]

                if pd.isna(wert):
                    wert_text = "-"
                elif int(wert) == 1:
                    wert_text = "✔"
                elif int(wert) == 0:
                    wert_text = "✘"
                else:
                    wert_text = str(wert)

            zeile[programm_name] = wert_text

        vergleichsdaten.append(zeile)

    vergleich_df = pd.DataFrame(vergleichsdaten)

    html += vergleich_df.to_html(
        index=False,
        escape=False
    )

    html += """
    </body>
    </html>
    """

    return html
#####################

#####################
# Gewichtung
def waehle_doppelte_gewichtung(nutzerantworten, fragen, ausgeschlossene_kriterien=None):

    if ausgeschlossene_kriterien is None: # KO-Fragen sind ausgeschlossen für Auswahl Gewichtung
        ausgeschlossene_kriterien = []

    st.write(
        """
        Sie können einzelne Antworten als besonders wichtig markieren.
        Ausgewählte Antworten werden im Matching doppelt gewichtet.
        Das bedeutet: Wenn ein Programm diese Anforderungen erfüllt,
        wirkt sich das stärker positiv auf das Ergebnis aus.
        """
    )

    beantwortete_fragen = fragen[
        fragen["kriterium_id"].isin(nutzerantworten.keys()) &
        ~fragen["kriterium_id"].isin(ausgeschlossene_kriterien)
        ]

    optionen = {}

    for _, frage in beantwortete_fragen.iterrows():
        kriterium_id = frage["kriterium_id"]
        frage_text = frage["frage_text"]

        antwort = nutzerantworten[kriterium_id]

        if isinstance(antwort, list):
            antwort_text = ", ".join(antwort)
        else:
            antwort_text = str(antwort)

        anzeigename = f"{frage_text} → Ihre Antwort: {antwort_text}"
        optionen[anzeigename] = kriterium_id

    st.write("Welche Ihrer Antworten sind Ihnen besonders wichtig?")

    ausgewaehlte_kriterien = []

    with st.container(height=400):
        for anzeigename, kriterium_id in optionen.items():

            ist_ausgewaehlt = kriterium_id in st.session_state.doppelt_gewichtete_fragen

            checkbox = st.checkbox(
                anzeigename,
                value=ist_ausgewaehlt,
                key=f"gewichtung_{kriterium_id}"
            )

            if checkbox:
                ausgewaehlte_kriterien.append(kriterium_id)

    return ausgewaehlte_kriterien
#####################

#####################
# KO-Kriterium
def waehle_ko_kriterien(nutzerwerte, kriterien):

    moegliche_kriterien = kriterien[
        kriterien["kriterium_id"].isin(nutzerwerte.keys())
    ]

    ko_faehige_kriterien_ids = [ # nur Kriterien mit eindeutiger Nutzerpräferenz (nicht neutral), sind auswählbar
        kriterium_id
        for kriterium_id, nutzerwert in nutzerwerte.items()
        if nutzerwert in [0, 1]
    ]

    moegliche_kriterien = kriterien[
        kriterien["kriterium_id"].isin(ko_faehige_kriterien_ids)
    ]

    optionen = {
        row["kriterium_name"]: row["kriterium_id"]
        for _, row in moegliche_kriterien.iterrows()
    }

    st.write(
        "Wählen Sie bis zu 3 Kriterien aus, die zwingend erfüllt sein müssen:"
    )

    # Checkboxen beim ersten Laden mit der bisherigen Auswahl vorbelegen
    for anzeigename, kriterium_id in optionen.items():
        key = f"ko_{kriterium_id}"

        if key not in st.session_state:
            st.session_state[key] = kriterium_id in st.session_state.ko_kriterien

    # Aktuelle Auswahl direkt aus den Checkboxen lesen
    aktuelle_auswahl = [
        kriterium_id
        for kriterium_id in optionen.values()
        if st.session_state.get(f"ko_{kriterium_id}", False)
    ]

    max_erreicht = len(aktuelle_auswahl) >= 3

    auswahl = []

    for anzeigename, kriterium_id in optionen.items():
        key = f"ko_{kriterium_id}"

        checkbox = st.checkbox(
            anzeigename,
            key=key,
            disabled=(
                    max_erreicht
                    and not st.session_state.get(key, False)
            )
        )

        if checkbox:
            auswahl.append(kriterium_id)

    st.write("")  # Leerzeile zwischen Auswahl und Buttons

    st.session_state.ko_auswahl_gueltig = True

    return auswahl

#####################
# ordnet Textantworten des Nutzers den numerischen Wert zu
def mappe_antworten_auf_werte(nutzerantworten, antwortmapping):
    nutzerwerte = {}

    for kriterium_id, antwort in nutzerantworten.items():

        antworten = antwort if isinstance(antwort, list) else [antwort]

        for einzelne_antwort in antworten:
            mapping_zeilen = antwortmapping[
                (antwortmapping["kriterium_id"] == kriterium_id) &
                (antwortmapping["antwort_text"] == einzelne_antwort)
            ]

            for _, zeile in mapping_zeilen.iterrows():
                ziel_kriterium_id = zeile["ziel_kriterium_id"]
                antwort_wert = zeile["antwort_wert"]

                if antwort_wert == -1:
                    continue

                nutzerwerte[ziel_kriterium_id] = float(antwort_wert)

    return nutzerwerte


#####################
# Prüft, ob eine Frage angezeigt werden soll, basierend auf Abhängigkeiten
# z.B. nur anzeigen, wenn eine vorherige frage eine bestimmte Antwort hat
def soll_frage_angezeigt_werden(frage, nutzerantworten):
    abhaengig_von = frage["abhaengig_von_kriterium_id"]
    erwartete_antwort = frage["abhaengig_von_antwort"]

    # Keine Abhängigkeit vorhanden
    if str(abhaengig_von) == "nan":
        return True

    # Werte aus Excel bereinigen
    abhaengig_von = str(abhaengig_von).strip()
    erwartete_antwort = str(erwartete_antwort).strip()

    # # Debug Test
    # st.write("Debug")
    # st.write("Kriterium:", frage["kriterium_id"])
    # st.write("Abhängigkeit:", abhaengig_von)
    # st.write("Erwartet:", erwartete_antwort)
    # st.write("Vorhandene Antworten:", nutzerantworten)

    # Falls die abhängige vorherige Antwort noch nicht gegeben wurde
    if abhaengig_von not in nutzerantworten:
        return False

    # Tatsächliche Nutzerantwort bereinigen
    tatsaechliche_antwort = nutzerantworten[abhaengig_von]

    # Falls vorherige Antwort eine Liste ist, z. B. bei multiple_select
    if isinstance(tatsaechliche_antwort, list):
        tatsaechliche_antwort = [str(a).strip() for a in tatsaechliche_antwort]
        return erwartete_antwort in tatsaechliche_antwort

    # Normale single_choice-Antwort
    tatsaechliche_antwort = str(tatsaechliche_antwort).strip()

    if tatsaechliche_antwort != erwartete_antwort:
        return False

    return True
#####################

#####################
# holt Antwortoptionen für eine Frage und entfernt leere Werte
def hole_optionen(frage):
    optionen = [
        frage["option_1"],
        frage["option_2"],
        frage["option_3"],
        frage["option_4"]
    ]

    return [option for option in optionen if str(option) != "nan"]
#####################

#####################
# erstellt Fragebogen in Streamlit, zeigt Fragen an
# speichert Antworten des Nutzers in einem Dictionary "nutzerantworten"
def zeige_fragebogen(fragen):
    st.subheader("Fragebogen")

    if "frage_index" not in st.session_state:
        st.session_state.frage_index = 0

    if "nutzerantworten" not in st.session_state:
        st.session_state.nutzerantworten = {}

    if "fragebogen_abgeschlossen" not in st.session_state:
        st.session_state.fragebogen_abgeschlossen = False

    nutzerantworten = st.session_state.nutzerantworten

    sichtbare_fragen = []

    for _, frage in fragen.iterrows():
        if soll_frage_angezeigt_werden(frage, nutzerantworten):
            sichtbare_fragen.append(frage)

    if st.session_state.frage_index >= len(sichtbare_fragen):
        st.session_state.fragebogen_abgeschlossen = True
        st.session_state.seite = "ko"
        st.rerun()

    aktuelle_frage = sichtbare_fragen[st.session_state.frage_index]

    kriterium_id = aktuelle_frage["kriterium_id"]
    frage_text = aktuelle_frage["frage_text"]
    antwort_datentyp = aktuelle_frage["antwort_datentyp"]
    optionen = hole_optionen(aktuelle_frage)

    st.write(
        f"**Frage {st.session_state.frage_index + 1} "
        f"von {len(sichtbare_fragen)}**"
    )

    st.markdown(f"### {frage_text}")

    if antwort_datentyp == "multiple_select":
        ausgewaehlte_optionen = []

        gespeicherte_antworten = (
            nutzerantworten.get(kriterium_id, [])
            if isinstance(nutzerantworten.get(kriterium_id), list)
            else []
        )

        for option in optionen:
            if st.checkbox(
                    option,
                    value=option in gespeicherte_antworten,
                    key=f"{kriterium_id}_{option}"
            ):
                ausgewaehlte_optionen.append(option)

        antwort = ausgewaehlte_optionen
        nutzerantworten[kriterium_id] = antwort

        st.write("") # Leerzeile zwischen Dropdown und Buttons

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(
                    "Zurück",
                    disabled=st.session_state.frage_index == 0,
                    use_container_width=True
            ):
                st.session_state.frage_index -= 1
                st.rerun()

        with col2:
            if st.button(
                    "Weiter",
                    disabled=len(antwort) == 0,
                    use_container_width=True
            ):
                st.session_state.frage_index += 1 # "Weiter" anklickbar, wenn mindestens eine Checkbox ausgewählt wurde
                st.rerun()

        with col3:
            if st.button(
                    "Frage überspringen",
                    use_container_width=True
            ):
                nutzerantworten[kriterium_id] = "Frage überspringen"
                st.session_state.frage_index += 1
                st.rerun()

        if antwort:
            nutzerantworten[kriterium_id] = antwort

        st.write("")

    else:
        gespeicherte_antwort = nutzerantworten.get(kriterium_id)

        if gespeicherte_antwort:
            st.info(f"Aktuelle Antwort: {gespeicherte_antwort}")

        for option in optionen:
            if st.button(option, key=f"{kriterium_id}_{option}"):
                nutzerantworten[kriterium_id] = option
                st.session_state.frage_index += 1
                st.rerun()

        st.write("")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(
                    "Zurück",
                    use_container_width=True,
                    disabled=st.session_state.frage_index == 0
            ):
                st.session_state.frage_index -= 1
                st.rerun()

        with col2:
            if kriterium_id in nutzerantworten:
                if st.button("Weiter",
                    use_container_width=True):
                    st.session_state.frage_index += 1
                    st.rerun()

        with col3:
            if st.button("Frage überspringen",
                use_container_width=True):
                nutzerantworten[kriterium_id] = "Frage überspringen"
                st.session_state.frage_index += 1
                st.rerun()

    return nutzerantworten
#####################