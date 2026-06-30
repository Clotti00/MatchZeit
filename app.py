##############################################
# Interaktion mit dem Nutzer##################
# Streamlit-UI, Fragebogen, Ergebnisanzeige###
##############################################
# Stand 02.06.2026

import streamlit as st
from data_loader import lade_excel_datei
from matching import berechne_matching
import streamlit.components.v1 as components # Um Druckfunktion im Browser zu öffnen
from utils import (
    zeige_fragebogen,
    mappe_antworten_auf_werte,
    waehle_ko_kriterien,
    zeige_matching_ergebnisse,
    waehle_doppelte_gewichtung,
    erzeuge_ergebnis_html,
)

# Seitenabstände verkleinern
st.markdown("""
<style>
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}

h1, h2, h3 {
    margin-top: 0rem;
}
</style>
""", unsafe_allow_html=True)

st.header("MatchZeit")

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

# Druckbutton entfernen, wenn man nicht auf der Ergebnisseite ist
if st.session_state.seite != "ergebnis":
    components.html(
        """
        <script>
        const doc = window.parent.document;
        const alterButton = doc.getElementById("print-button-fixed");
        if (alterButton) {
            alterButton.remove();
        }
        </script>
        """,
        height=0
    )


# Willkommensseite
if st.session_state.seite == "start":

    st.write(
        """
        Dieses Programm hilft Ihnen dabei, anhand Ihrer individuellen Anforderungen
        passende Software zur Erfassung von Arbeitszeit zu finden.
        

        **So funktioniert’s:**

        - Geben Sie die benötigten Informationen im Fragebogen ein.
        - Wählen Sie bei Bedarf bis zu drei KO-Kriterien aus oder gewichten Sie Ihre Antworten.
        - Das Programm berechnet passende Übereinstimmungen.
        - Sie erhalten Ihre Ergebnisse übersichtlich angezeigt.
        - Bearbeitungszeit: 10-15 Minuten

        Klicken Sie auf **„Matching starten“**, um zu beginnen.
        """
    )

    st.info(
        "Für eine optimale Nutzung wird die Verwendung eines PCs "
        "oder Laptops mit einem aktuellen Webbrowser empfohlen. "
        "Die Anwendung ist grundsätzlich auch auf mobilen Geräten nutzbar, "
        "der Bedienkomfort kann dort jedoch eingeschränkt sein. "
    )

    if st.button("Matching starten"):
        st.session_state.seite = "fragebogen"
        st.rerun()


# Fragebogen und Matching
else:
    try:
        daten = lade_excel_datei(pfad)

        programme_info, bewertungen, kriterien, fragen, antwortmapping = daten

        if st.session_state.seite == "fragebogen":
            nutzerantworten = zeige_fragebogen(fragen)

        elif st.session_state.seite == "ko":
            st.markdown(
                "### KO-Kriterien",
                help="KO-Kriterien sind Anforderungen, die eine Software zwingend erfüllen muss. Programme, die mindestens eines dieser Kriterien nicht erfüllen, werden aus den Matching-Ergebnissen ausgeschlossen."
            )
            nutzerantworten = st.session_state.nutzerantworten

            nutzerwerte = mappe_antworten_auf_werte(
                nutzerantworten,
                antwortmapping
            )

            st.session_state.ko_kriterien = waehle_ko_kriterien(
                nutzerwerte,
                kriterien
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                        "Zurück zum Fragebogen",
                        use_container_width=True
                ):
                    st.session_state.fragebogen_abgeschlossen = False

                    if "nutzerantworten" in st.session_state:
                        st.session_state.frage_index = max(
                            len(st.session_state.nutzerantworten) - 1,
                            0
                        )

                    st.session_state.seite = "fragebogen"
                    st.rerun()

            with col2:
                if st.button(
                        "Weiter zur Gewichtung",
                        disabled=not st.session_state.get("ko_auswahl_gueltig", True),
                        use_container_width=True
                ):
                    st.session_state.seite = "gewichtung"
                    st.rerun()


        elif st.session_state.seite == "gewichtung":
            st.markdown(
                "### Gewichtung",
                help="Hier können Sie einzelne Antworten als besonders wichtig markieren. Diese Antworten werden bei der Berechnung des Matchings doppelt gewichtet. Das bedeutet: Wenn ein Programm diese Anforderungen erfüllt, wirkt sich das stärker positiv auf das Ergebnis aus. Durch Ihre Entscheidung werden keine Programme komplett aus der Ergebnisberechnung ausgeschlossen. Diejenigen Kriterien, die bereits als KO-Kriterium ausgewählt worden sind, befinden sich nicht mehr in dieser Aufzählung."
            )

            nutzerantworten = st.session_state.nutzerantworten

            st.session_state.doppelt_gewichtete_fragen = waehle_doppelte_gewichtung(
                nutzerantworten,
                fragen,
                st.session_state.ko_kriterien
            )

            nutzerwerte = mappe_antworten_auf_werte(
                nutzerantworten,
                antwortmapping
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                        "Zurück zu den KO-Kriterien",
                        use_container_width=True
                ):
                    st.session_state.seite = "ko"
                    st.rerun()

            with col2:
                if st.button(
                        "Matching berechnen",
                        use_container_width=True
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
                if st.button("Zurück zur Gewichtung"):
                    st.session_state.seite = "gewichtung"
                    st.rerun()

            druck_html = erzeuge_ergebnis_html(
                st.session_state.matching_ergebnisse,
                programme_info,
                bewertungen,
                kriterien
            )

            components.html(
                f"""
                <script>
                const doc = window.parent.document;

                // alten Button entfernen, falls er durch Streamlit-Rerun schon existiert
                const alterButton = doc.getElementById("print-button-fixed");
                if (alterButton) {{
                    alterButton.remove();
                }}

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

                button.onclick = function() {{
                    const printWindow = window.open("", "_blank");
                    printWindow.document.open();
                    printWindow.document.write({druck_html!r});
                    printWindow.document.close();
                    printWindow.focus();
                    printWindow.print();
                }};

                doc.body.appendChild(button);
                </script>
                """,
                height=0
            )

            nutzerwerte = mappe_antworten_auf_werte(
                st.session_state.nutzerantworten,
                antwortmapping
            )

            zeige_matching_ergebnisse(
                st.session_state.matching_ergebnisse,
                programme_info,
                bewertungen,
                kriterien,
                nutzerwerte
            )

        # Über MatchZeit
        elif st.session_state.seite == "ueber":

            st.subheader("Über MatchZeit")

            st.markdown("""
            ### Ziel und Zweck von MatchZeit

            MatchZeit ist ein webbasiertes Entscheidungshilfesystem zur Auswahl von Softwarelösungen für die Erfassung von Arbeitszeiten in landwirtschaftlichen Betrieben. Ziel ist es, Betriebe dabei zu unterstützen, aus einer Vielzahl verfügbarer Programme diejenigen zu identifizieren, die den individuellen Anforderungen möglichst gut entsprechen.

            ---

            ### Hintergrund der Entwicklung

            Die Anwendung wurde im Rahmen einer Masterarbeit im Studiengang Landwirtschaft (M.Sc.) an der Hochschule Anhalt entwickelt. Ausgangspunkt war die Fragestellung, wie landwirtschaftliche Betriebe bei der Auswahl geeigneter Arbeitszeiterfassungssoftware systematisch und nachvollziehbar unterstützt werden können.

            ---

            ### Funktionsweise

            Im Fragebogen werden zunächst die Anforderungen und Präferenzen des Nutzers erfasst. Optional können bis zu drei KO-Kriterien festgelegt werden, die eine Software zwingend erfüllen muss. Zusätzlich besteht die Möglichkeit, einzelne Anforderungen höher zu gewichten.

            Anschließend werden die Eingaben mit den in MatchZeit hinterlegten Eigenschaften der verfügbaren Softwarelösungen verglichen. Aus diesem Vergleich wird für jedes Programm ein Matching-Wert berechnet, der die Übereinstimmung zwischen den Nutzeranforderungen und den Programmeigenschaften widerspiegelt.

            ---

            ### Interpretation der Ergebnisse

            Die angezeigten Ergebnisse stellen eine Entscheidungshilfe dar. Ein hoher Matching-Wert bedeutet, dass eine Software die angegebenen Anforderungen besonders gut erfüllt. Die endgültige Auswahl einer Software sollte jedoch zusätzlich unter Berücksichtigung individueller betrieblicher Anforderungen sowie einer eigenen Prüfung der Programme erfolgen.

            Die Bewertung der Softwarelösungen basiert auf dem im Rahmen der Masterarbeit erarbeiteten Kriterienkatalog und dem zum Zeitpunkt der Erstellung verfügbaren Informationsstand. Änderungen an Softwarefunktionen oder Preisen nach diesem Zeitpunkt können dazu führen, dass einzelne Angaben nicht mehr aktuell sind.

            ---

            ### Hinweise zur Nutzung

            Die Nutzung von MatchZeit ist kostenfrei. Die im Matching eingegebenen Antworten werden nicht dauerhaft gespeichert. Die Teilnahme am freiwilligen Evaluierungsfragebogen dient ausschließlich der wissenschaftlichen Auswertung und Weiterentwicklung des Systems im Rahmen der Masterarbeit.
            """)

            if st.button("Zurück"):
                st.session_state.seite = st.session_state.vorherige_seite
                st.rerun()

        # Impressum
        elif st.session_state.seite == "impressum":

            st.subheader("Impressum")

            st.markdown("""
            Claudia Bäuerlein

            Lindenhof 7  
            38828 Wegeleben

            E-Mail-Adresse: matchzeit@gmail.com

            Hochschule Anhalt  
            Landwirtschaft (M.Sc.)
            """)

            if st.button("Zurück"):
                st.session_state.seite = st.session_state.vorherige_seite
                st.rerun()

        # Datenschutzhinweise
        elif st.session_state.seite == "datenschutz":

            st.subheader("Datenschutzhinweise")

            st.markdown("""

            ### 1. Zweck der Datenverarbeitung

            MatchZeit wurde im Rahmen einer Masterarbeit an der Hochschule Anhalt entwickelt. Die im Evaluierungsfragebogen erhobenen Daten dienen ausschließlich der wissenschaftlichen Evaluation und Verbesserung des Systems sowie der Auswertung im Rahmen der Masterarbeit.

            ---

            ### 2. Welche Daten werden erhoben?

            - Alter
            - Tätigkeit in der Landwirtschaft
            - Beteiligung an betrieblichen Entscheidungen
            - Antworten auf die Bewertungsfragen
            - Freitextantworten
            - Zeitpunkt der Übermittlung

            Die Nutzung des eigentlichen Matching-Tools erfolgt ohne Speicherung der eingegebenen Antworten.

            ---

            ### 3. Freiwilligkeit

            Die Teilnahme am Evaluierungsfragebogen ist freiwillig. Die Nutzung von MatchZeit ist auch ohne Teilnahme an der Evaluation möglich.

            ---

            ### 4. Rechtsgrundlage der Datenverarbeitung

            Die Verarbeitung der im Evaluierungsfragebogen erhobenen personenbezogenen Daten erfolgt ausschließlich auf Grundlage Ihrer freiwilligen Einwilligung gemäß Art. 6 Abs. 1 lit. a Datenschutz-Grundverordnung (DSGVO).

            Mit dem Absenden des Evaluierungsfragebogens und der zuvor erteilten Einwilligung erklären Sie sich damit einverstanden, dass Ihre Angaben zum Zweck der wissenschaftlichen Evaluation und Auswertung im Rahmen der Masterarbeit verarbeitet werden.

            Die Einwilligung ist freiwillig und kann jederzeit mit Wirkung für die Zukunft widerrufen werden. Die Rechtmäßigkeit der bis zum Widerruf erfolgten Datenverarbeitung bleibt hiervon unberührt.

            ---

            ### 5. Empfänger der Daten

            Die Daten werden per E-Mail an die verantwortliche Person übermittelt und ausschließlich für die wissenschaftliche Auswertung der Masterarbeit verwendet.

            ---

            ### 6. Speicherdauer

            Die erhobenen Daten werden ausschließlich für die Durchführung und Dokumentation der Masterarbeit gespeichert und nach Abschluss der wissenschaftlichen Arbeiten gelöscht.

            ---

            ### 7. Weitergabe

            Eine Weitergabe personenbezogener Daten an Dritte erfolgt nicht.

            ---

            ### 8. Betroffenenrechte

            Sie haben im Rahmen der geltenden datenschutzrechtlichen Bestimmungen das Recht auf Auskunft über die zu Ihrer Person gespeicherten Daten. Darüber hinaus haben Sie das Recht auf Berichtigung unrichtiger Daten, auf Löschung Ihrer Daten sowie auf Einschränkung der Verarbeitung, soweit die gesetzlichen Voraussetzungen hierfür vorliegen.

            Eine erteilte Einwilligung zur Verarbeitung Ihrer personenbezogenen Daten können Sie jederzeit mit Wirkung für die Zukunft widerrufen. Der Widerruf berührt nicht die Rechtmäßigkeit der aufgrund der Einwilligung bis zum Widerruf erfolgten Verarbeitung.

            Bei Fragen zur Verarbeitung Ihrer personenbezogenen Daten oder zur Ausübung Ihrer Rechte können Sie sich an die im Impressum genannte verantwortliche Person wenden.

            ---

            ### 9. Verantwortliche Person

            Claudia Bäuerlein

            Lindenhof 7  
            38828 Wegeleben

            matchzeit@gmail.com
            """)

            if st.button("Zurück"):
                st.session_state.seite = st.session_state.vorherige_seite
                st.rerun()

    except Exception as e:
        st.error(str(e))

st.write("")
st.write("")

# Über MatchZeit, Impressum, Datenschutzhinweise
col1, col2, col3, col4, col5 = st.columns(
    [0.53, 0.1, 0.39, 0.1, 2]
)



with col1:
    if st.button("Über MatchZeit", type="tertiary"):
        if st.session_state.seite not in ["ueber", "impressum", "datenschutz"]:
            st.session_state.vorherige_seite = st.session_state.seite
        st.session_state.seite = "ueber"
        st.rerun()

with col2:
    st.markdown(
        "<div style='text-align:center;color:#999;padding-top:8px;'>|</div>",
        unsafe_allow_html=True
    )

with col3:
    if st.button("Impressum", type="tertiary"):
        if st.session_state.seite not in ["ueber", "impressum", "datenschutz"]:
            st.session_state.vorherige_seite = st.session_state.seite
        st.session_state.seite = "impressum"
        st.rerun()

with col4:
    st.markdown(
        "<div style='text-align:center;color:#999;padding-top:8px;'>|</div>",
        unsafe_allow_html=True
    )

with col5:
    if st.button("Datenschutzhinweise", type="tertiary"):
        if st.session_state.seite not in ["ueber", "impressum", "datenschutz"]:
            st.session_state.vorherige_seite = st.session_state.seite
        st.session_state.seite = "datenschutz"
        st.rerun()