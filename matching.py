############################################
# fachliche Entscheidungslogik##############
# berechnet Scores, Distanzen, Ranking######
############################################
import pandas as pd

def berechne_matching(
        nutzerwerte,
        bewertungen,
        kriterien,
        ko_kriterien=None,
        doppelt_gewichtete_fragen=None
): # Funktion erstellen, (Parameter): erhält diese Informationen

    if ko_kriterien is None:
        ko_kriterien = []

    if doppelt_gewichtete_fragen is None:
        doppelt_gewichtete_fragen = []

    aktive_kriterien = kriterien[kriterien["aktiv_im_matching"] == 1] # nur die Kriterien, die ins Matching auch einfließen sollten (wo aktiv_im_matching == 1

    ergebnisse = [] # leere Liste erstellen (für jedes Programm wird ein Ergebnis gespeichert)

    for _, programm in bewertungen.iterrows(): # iterrows(): Python  geht Zeile für Zeile durch die Tabelle "bewertungen"
        programm_id = programm["programm_id"] # aus aktueller Zeile die ID holen

        if pd.isna(programm_id) or str(programm_id).strip() == "": # prüft, ob programm:id wirklich leer ist, entfernt Leerzeichen
            continue # wenn, leer, dann überspringen

        ko_nicht_erfuellt = False # Variable festlegen, False = alles ok, True = KO-Kriterium verletzt

        for kriterium_id in ko_kriterien: # Schleife über alle KO-Kriterien, für jedes Programm wird geprüft, ob es die KO-Kriterien erfüllt
            if kriterium_id not in bewertungen.columns: # falls Kriterium in Programmdaten gar nicht existiert
                ko_nicht_erfuellt = True
                break # Schleife wird abgebrochen -> Programm fällt sofort raus

            programmwert = programm[kriterium_id]
            nutzerwert = nutzerwerte[kriterium_id]

            # KO-Prüfung
            if pd.isna(programmwert) or int(programmwert) != int(nutzerwert): # Ausschluss, wenn Wert fehlt / Werte nicht übereinstimmen
                ko_nicht_erfuellt = True
                break # sobald eines nicht erfüllt, keine weiteren prüfen

        if ko_nicht_erfuellt:
            continue # Entscheidung: wenn mindestens ein KO-Kriterium nicht erfüllt, dann Programm komplett ignorieren

        punkte = 0 # für jedes Programm startet Berechnung neu bei 0, tatsächlich erreichten Matching-Punkte
        max_punkte = 0 # maximal möglichen Punkte bei für beantwortete Kriterien

        anzahl_bewertet = 0 # Anzahl der Kriterien, die bewertet wurden
        anzahl_moeglich = 0 # Anzahl der Kriterien, die bewertet werden hätten können

        for kriterium_id, nutzerwert in nutzerwerte.items(): # geht Kriterien durch, die aus Nutzerantworten entstanden sind

            kriterium_zeile = aktive_kriterien[ # nach passender Zeile zum Kriterium innerhalb der aktiven Kriterien suchen
                aktive_kriterien["kriterium_id"] == kriterium_id
            ]

            if kriterium_zeile.empty: # falls Kriterium nicht aktiv oder nicht vorhanden -> überspringen
                continue

            gewichtung = float(kriterium_zeile.iloc[0]["gewichtung_standard"]) # aus passender Kriterienzeile wird Gewichtung geholt, float: Zahl mit Nachkommastelle

            if kriterium_id in doppelt_gewichtete_fragen:
                gewichtung = gewichtung * 2

            anzahl_moeglich += 1  # zählt jedes relevante Kriterium

            programmwert = programm[kriterium_id] # Wert des aktuellen Programms für das Kriterium aus "bewertungen" holen

            if pd.isna(programmwert): # falls kein Wert vorhanden -> überspringen
                continue

            anzahl_bewertet += 1  # nur wenn Wert vorhanden

            max_punkte += gewichtung # maximal erreichbare Punkte steigen um Gewichtung des Kriteriums

            programmwert = float(programmwert) # Werte werden in eine Kommazahl umgewandelt
            nutzerwert = float(nutzerwert) # Werte werden in eine Kommazahl umgewandelt

            # eigentliche Logik:
            # abs: absoluter Betrag
            # programmwert-nutzerwert: berechnet Abstand zwischen beiden Werten
            # 1 - abs(): Abstand in Ähnlichkeit umgewandelt
            aehnlichkeit = 1 - abs(programmwert - nutzerwert)

            punkte += gewichtung * aehnlichkeit

        matching_prozent = 0
        if max_punkte > 0: # Matching-Prozentwert standardmäßig = 0 %
            matching_prozent = round((punkte / max_punkte) * 100, 2) # Berechnung vom prozentualem Match

        datenabdeckung = 0 # Datenabdeckung standardmäßig = 0 %
        if anzahl_moeglich > 0:
            datenabdeckung = round((anzahl_bewertet / anzahl_moeglich) * 100, 2) # Berechnung wie vollständig Datenbasis ist, z.B. anzahl_bewertet = 8, anzahl_moeglich = 10 → 80 % Datenabdeckung.

        ergebnisse.append({
            "programm_id": programm_id,
            "matching_punkte": punkte,
            "max_punkte": max_punkte,
            "matching_prozent": matching_prozent,
            "datenabdeckung_prozent": datenabdeckung,
            "bewertete_kriterien": anzahl_bewertet,
            "moegliche_kriterien": anzahl_moeglich
        })

    # Falls keine Ergebnisse vorhanden sind
    if not ergebnisse:
        return pd.DataFrame(columns=[
            "programm_id",
            "matching_punkte",
            "max_punkte",
            "matching_prozent",
            "datenabdeckung_prozent",
            "bewertete_kriterien",
            "moegliche_kriterien"
        ])

    return pd.DataFrame(ergebnisse).sort_values(
        by="matching_prozent",
        ascending=False
    )