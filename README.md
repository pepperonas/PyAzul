# Azul - Digitales Brettspiel

Eine Python-Implementation des beliebten Brettspiels Azul mit grafischer Benutzeroberfläche.

## Entwickler
**Martin Pfeffer** - 2025

## Lizenz
MIT License

## Über das Spiel

Azul ist ein strategisches Brettspiel, bei dem Spieler bunte Fliesen sammeln und auf ihren Spielerablagen platzieren, um Punkte zu erzielen. Das Ziel ist es, durch geschicktes Sammeln und Platzieren von Fliesen die höchste Punktzahl zu erreichen.

## Installation und Start

### Voraussetzungen
- Python 3.7 oder höher
- tkinter (normalerweise mit Python vorinstalliert)

### Spiel starten
```bash
python game.py
```

## Spielanleitung

### Spielaufbau
- 2-4 Spieler
- Jeder Spieler hat eine individuelle Spielerablage mit:
  - 5 Musterreihen (1-5 Plätze)
  - 5×5 Wandmuster
  - Bodenreihe für überschüssige Fliesen
- Manufakturplättchen (5/7/9 je nach Spieleranzahl)
- Tischmitte für übrige Fliesen

### Spielablauf

#### 1. Musterphase
Spieler sind abwechselnd am Zug und wählen:

**Fliesen nehmen:**
- Klicke auf eine Manufaktur oder die Tischmitte
- Wähle eine Farbe aus den verfügbaren Optionen
- Nimm alle Fliesen dieser Farbe

**Fliesen platzieren:**
- Wähle eine Musterreihe (1-5) oder die Bodenreihe
- Fliesen können nur in Reihen gelegt werden, wenn:
  - Die Reihe leer ist oder bereits dieselbe Farbe enthält
  - Die Farbe noch nicht in der entsprechenden Wandreihe liegt
  - Noch Platz in der Reihe ist

**Besondere Regeln:**
- Übrige Fliesen von Manufakturen gehen in die Tischmitte
- Wer zuerst aus der Mitte nimmt, erhält den Startspielermarker
- Überschüssige Fliesen gehen in die Bodenreihe

#### 2. Fliesungsphase (automatisch)
- Komplette Musterreihen werden zur Wand bewegt
- Punkte werden für neue Wandfliesen berechnet
- Bodenreihe wird ausgewertet (Minuspunkte)

### Punktevergabe

#### Während des Spiels:
- **Einzelne Fliese:** 1 Punkt
- **Horizontale Verbindung:** Anzahl verbundener Fliesen
- **Vertikale Verbindung:** Anzahl verbundener Fliesen

#### Spielende-Bonus:
- **Vollständige horizontale Reihe:** 2 Punkte
- **Vollständige vertikale Reihe:** 7 Punkte  
- **Alle 5 Fliesen einer Farbe:** 10 Punkte

#### Minuspunkte (Bodenreihe):
- Position 1-2: -1 Punkt
- Position 3-5: -2 Punkte
- Position 6-7: -3 Punkte
- Startspielermarker: -1 Punkt

### Spielende
Das Spiel endet, wenn ein Spieler eine komplette horizontale Wandreihe gefüllt hat. Nach der Endwertung gewinnt der Spieler mit den meisten Punkten.

## Bedienung

### Hauptspiel
- **Manufaktur/Tischmitte anklicken:** Fliesen auswählen
- **Farbauswahl:** Button mit gewünschter Farbe klicken
- **Musterreihe wählen:** Gewünschte Reihe oder Bodenreihe auswählen

### Spieleroberfläche
- **Musterreihen:** Links auf der Spielerablage (1-5 Plätze)
- **Wand:** Rechts mit farbigem 5×5 Muster
- **Bodenreihe:** Unten mit Minuspunkt-Anzeige
- **Punkte:** Aktuelle Punktzahl oben rechts

### Spielphasen
- **Musterphase:** Spieler setzen Fliesen
- **Fliesungsphase:** Automatische Auswertung
- **Vorbereitung:** Nächste Runde wird vorbereitet
- **Spielende:** Endwertung und Gewinner-Anzeige

## Funktionen
- Vollständige Spiellogik nach Originalregeln
- Grafische Benutzeroberfläche mit tkinter
- 2-4 Spieler Unterstützung
- Automatische Punkteberechnung
- Endspiel-Auswertung mit Bonuspunkten
- Neues Spiel starten

## Technische Details
- **Sprache:** Python 3
- **GUI-Framework:** tkinter
- **Architektur:** Model-View-Controller Pattern
- **Spiellogik:** Separate Klassen für Game, Player, Factory etc.

---
*Basierend auf dem Brettspiel "Azul" von Michael Kiesling*