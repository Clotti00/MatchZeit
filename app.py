##############################################
# Interaktion mit dem Nutzer##################
# Streamlit-UI, Fragebogen, Ergebnisanzeige###
##############################################

import streamlit as st
from data_loader import lade_excel_datei
from matching import berechne_matching
import streamlit.components.v1 as components # Um Druckfunktion im Browser zu öffnen
from utils import (
#    zeige_erfolgsmeldung_einmal,
    zeige_fragebogen,
    mappe_antworten_auf_werte,
    waehle_ko_kriterien,
    zeige_matching_ergebnisse,
    waehle_doppelte_gewichtung,
)
st.title("MatchZeit")

pfad = "data/Programmliste_Kriterien_Python.xlsx"

# Session-State für Startseite initialisieren
if "seite" not in st.session_state:
    st.session_state.seite = "start"

if "matching_ergebnisse" not in st.session_state:
    st.session_state.matching_ergebnisse = None

if "evaluierung_starten" not in st.session_state:
    st.session_state.evaluierung_starten = False

if "doppelt_gewichtete_fragen" not in st.session_state:
    st.session_state.doppelt_gewichtete_fragen = []

if "ko_kriterien" not in st.session_state:
    st.session_state.ko_kriterien = []


# Willkommensseite
if st.session_state.seite == "start":
    # st.header("Willkommen!")

    st.write(
        """
        Dieses Programm hilft Ihnen dabei, anhand Ihrer individuellen Anforderungen
        passende Software zur Erfassung von Arbeitszeit zu finden.

        **So funktioniert’s:**

        - Geben Sie die benötigten Informationen im Fragebogen ein.
        - Wählen Sie bei Bedarf bis zu drei KO-Kriterien aus oder gewichten Sie Ihre Antworten.
        - Das Programm berechnet passende Übereinstimmungen.
        - Sie erhalten Ihre Ergebnisse übersichtlich angezeigt.

        Klicken Sie auf **„Matching starten“**, um zu beginnen.
        """
    )

    if st.button("Matching starten"):
        st.session_state.seite = "fragebogen"
        st.rerun()


# Fragebogen und Matching
else:
    try:
        daten = lade_excel_datei(pfad)

        programme_info, bewertungen, kriterien, fragen, antwortmapping = daten

        # zeige_erfolgsmeldung_einmal(
        #     "Daten wurden erfolgreich geladen.",
        #     "daten_geladen"
        # )

        if st.session_state.seite == "fragebogen":
            nutzerantworten = zeige_fragebogen(fragen)


        elif st.session_state.seite == "gewichtung":
            st.header("Gewichtung")

            nutzerantworten = st.session_state.nutzerantworten

            st.session_state.doppelt_gewichtete_fragen = waehle_doppelte_gewichtung(
                nutzerantworten,
                fragen
            )

            col1, spacer, col2 = st.columns([1, 6, 1])

            with col1:
                if st.button("Zurück"): # man kommt zurück zum Fragebogen und kann letzte Frage wieder beantworten
                    st.session_state.fragebogen_abgeschlossen = False

                    if "nutzerantworten" in st.session_state:
                        st.session_state.frage_index = max(
                            len(st.session_state.nutzerantworten) - 1,
                            0
                        )

                    st.session_state.seite = "fragebogen"
                    st.rerun()

            with col2:
                if st.button("Weiter"):
                    st.session_state.seite = "ko"
                    st.rerun()

        elif st.session_state.seite == "ko":
            st.header("KO-Kriterien")

            nutzerantworten = st.session_state.nutzerantworten

            nutzerwerte = mappe_antworten_auf_werte(
                nutzerantworten,
                antwortmapping
            )

            st.session_state.ko_kriterien = waehle_ko_kriterien(
                nutzerwerte,
                kriterien
            )

            col1, spacer, col2 = st.columns([1, 2, 1])

            with col1:
                if st.button("Zurück"):
                    st.session_state.seite = "gewichtung"
                    st.rerun()

            with col2: # Button nur aktiv, wenn maximal 3 KO-Kriterien ausgewählt worden sind
                if st.button(
                        "Matching berechnen",
                        disabled=not st.session_state.get("ko_auswahl_gueltig", True)
                ):
                    st.session_state.matching_ergebnisse = berechne_matching(
                        nutzerwerte,
                        bewertungen,
                        kriterien,
                        st.session_state.ko_kriterien,
                        st.session_state.doppelt_gewichtete_fragen
                    )

                    st.session_state.seite = "ergebnis"
                    st.rerun()


        elif st.session_state.seite == "ergebnis":
            col1, spacer, col2 = st.columns([1, 1, 1])
            with col1:
                if st.button("Zurück zu den KO-Kriterien"):
                    st.session_state.seite = "ko"
                    st.rerun()

            components.html(
                """
                <script>
                const doc = window.parent.document;

                // alten Button entfernen, falls er durch Streamlit-Rerun schon existiert
                const alterButton = doc.getElementById("print-button-fixed");
                if (alterButton) {
                    alterButton.remove();
                }

                const button = doc.createElement("button");
                button.id = "print-button-fixed";
                button.innerText = "Ergebnisse speichern";

                button.style.position = "fixed";
                button.style.top = "20px";
                button.style.right = "30px";
                button.style.zIndex = "999999";
                button.style.backgroundColor = "#f63366";
                button.style.color = "white";
                button.style.border = "none";
                button.style.borderRadius = "8px";
                button.style.padding = "0.6rem 1rem";
                button.style.fontSize = "1rem";
                button.style.fontWeight = "600";
                button.style.cursor = "pointer";
                button.style.boxShadow = "0 2px 6px rgba(0,0,0,0.2)";

                button.onclick = function() {
                    window.parent.print();
                };

                doc.body.appendChild(button);
                </script>
                """,
                height=0
            )

            zeige_matching_ergebnisse(
                st.session_state.matching_ergebnisse,
                programme_info,
                bewertungen,
                kriterien
            )

    except Exception as e:
        st.error(str(e))