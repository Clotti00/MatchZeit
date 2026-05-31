#####################
# Fragebogen#########
#####################

import pandas as pd
import streamlit as st
import smtplib

from io import BytesIO
from datetime import datetime
from email.message import EmailMessage

def sende_evaluierung_per_email(antworten):
    absender_email = "otto.winfred@gmail.com"
    empfaenger_email = "otto.winfred@gmail.com"
    app_passwort = st.secrets["gmail_app_passwort"]

    betreff = "Neue Evaluation MatchZeit"

    # Antworten in Excel-Datei im Arbeitsspeicher schreiben
    excel_datei = BytesIO()

    df = pd.DataFrame([antworten])

    with pd.ExcelWriter(excel_datei, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Evaluation")

    excel_datei.seek(0)

    nachricht = EmailMessage()
    nachricht["Subject"] = betreff
    nachricht["From"] = absender_email
    nachricht["To"] = empfaenger_email

    nachricht.set_content(
        """
        Neue Evaluation für MatchZeit.

        Die Ergebnisse befinden sich im Excel-Anhang.
        """
    )

    nachricht.add_attachment(
        excel_datei.read(),
        maintype="application",
        subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="evaluierung_matchzeit.xlsx"
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(absender_email, app_passwort)
        smtp.send_message(nachricht)

def zeige_evaluierungsfragebogen():
    st.markdown("---")
    st.header("Evaluierungs-Fragebogen")

    st.write(
        """
        Vielen Dank für die Nutzung des Tools.

        Die folgenden Fragen dienen ausschließlich der Evaluation der
        Benutzerfreundlichkeit und Verständlichkeit des Systems.

        Die Antworten werden anonym gespeichert.
        """
    )

    skala = {
        "1 - stimme überhaupt nicht zu": 1,
        "2 - stimme eher nicht zu": 2,
        "3 - teils / teils": 3,
        "4 - stimme eher zu": 4,
        "5 - stimme voll zu": 5
    }

    fragen = {
        "Bedienbarkeit": [
            "Die Bedienung des Tools war intuitiv.",
            "Die Benutzeroberfläche war übersichtlich gestaltet.",
            "Ich konnte das Tool ohne zusätzliche Hilfe verwenden."
        ],
        "Verständlichkeit der Inhalte": [
            "Die Fragen im Tool waren verständlich formuliert.",
            "Die Antwortmöglichkeiten waren eindeutig und verständlich.",
        ],
        "Verständlichkeit der Ergebnisse": [
            "Die Ergebnisse waren übersichtlich dargestellt.",
            "Ich konnte die Ergebnisse leicht nachvollziehen.",
            "Es war verständlich erklärt, wie die Ergebnisse zustande kommen.",
        ],
        "Gesamteindruck": [
            "Ich halte das Tool insgesamt für verständlich und übersichtlich.",
            "Ich würde das Tool weiteremfpehlen."
        ]
    }

    antworten = {
        "zeitstempel": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    #####################
    # Angaben zur Person
    #####################

    st.subheader("Angaben zur Person")

    antworten["alter"] = st.number_input(
        "Wie alt sind Sie?",
        min_value=0,
        max_value=120,
        step=1,
        key="eval_alter"
    )

    antworten["landwirtschaft_taetig"] = st.radio(
        "Sind Sie derzeit in der Landwirtschaft tätig?",
        ["Ja", "Nein"],
        index=None,
        key="eval_landwirtschaft_taetig"
    )

    antworten["entscheidungsbeteiligung"] = st.radio(
        "Sind Sie an Entscheidungen zu Personal-, Verwaltungs- oder Softwarefragen in Ihrem Betrieb beteiligt?",
        ["Ja", "Nein"],
        index=None,
        key="eval_entscheidungsbeteiligung"
    )

    frage_nummer = 1

    for themenbereich, fragen_liste in fragen.items():
        st.subheader(themenbereich)

        for frage in fragen_liste:
            antwort = st.radio(
                frage,
                list(skala.keys()),
                index=None,
                key=f"eval_{frage_nummer}"
            )

            antworten[f"frage_{frage_nummer}"] = skala[antwort] if antwort else None
            frage_nummer += 1

    st.subheader("Freitext")

    antworten["freitext_positiv"] = st.text_area(
        "Was hat Ihnen besonders gut gefallen an dem Tool?",
        key="eval_freitext_positiv"
    )

    antworten["freitext_verbesserung"] = st.text_area(
        "Was war unklar? / Welche Verbesserungen würden Sie sich wünschen?",
        key="eval_freitext_verbesserung"
    )

    antworten["freitext_sonstiges"] = st.text_area(
        "Weitere Bemerkungen",
        key="eval_freitext_sonstiges"
    )

    st.subheader("Angaben zur Datennutzung")

    antworten["nach_bestem_wissen"] = st.radio(
        "Haben Sie den Fragebogen nach bestem Wissen und Gewissen beantwortet?",
        ["Ja", "Nein"],
        index=None,
        key="eval_nach_bestem_wissen"
    )

    antworten["nutzung_wissenschaftlich"] = st.radio(
        "Dürfen Ihre anonymisierten Angaben für die wissenschaftliche Auswertung im Rahmen dieser Masterarbeit verwendet werden?",
        ["Ja", "Nein"],
        index=None,
        key="eval_nutzung_wissenschaftlich"
    )

    if st.button("Evaluierung senden"):
        try:
            sende_evaluierung_per_email(antworten)
            st.success("Vielen Dank für Ihr Feedback! Ihre Antworten wurden übermittelt.")
        except Exception as e:
            st.error("Die Evaluierung konnte leider nicht übermittelt werden.")
            st.error(str(e))