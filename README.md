# csvstat

`csvstat` ist ein kleines Kommandozeilenwerkzeug in Python, das eine CSV-Datei
einliest und pro Spalte eine Statistik ausgibt. Für numerische Spalten werden
Anzahl (count), Minimum, Maximum, Mittelwert und die Anzahl der fehlenden Werte
berichtet; für Textspalten die Anzahl der eindeutigen, nicht fehlenden Werte. Die
Ausgabe ist standardmäßig eine lesbare Festbreiten-Tabelle und mit `--json` ein
maschinenlesbares JSON-Objekt. Trennzeichen und Spaltenauswahl sind über
Optionen steuerbar, Fehlerfälle werden mit klaren Meldungen auf stderr und
passenden Exit-Codes behandelt (kein Python-Traceback).

## Tech-Stack

- **Sprache:** Python 3.11+
- **CLI:** `argparse` (Standardbibliothek), Einstieg über `python -m csvstat` und das Konsolenskript `csvstat`
- **CSV-Parsing:** `csv`-Modul der Standardbibliothek
- **Ausgabe:** Festbreiten-Tabelle auf stdout, alternativ JSON über `json.dumps`
- **Tests:** pytest
- **Lint:** ruff

Der Produktcode nutzt ausschließlich die Standardbibliothek.

## Installation

```bash
python -m pip install -e .
```

Für Entwicklung inklusive Tests und Lint:

```bash
python -m pip install -e ".[dev]"
```

## Ausführen

```bash
csvstat <datei>
```

oder ohne Installation als Modul:

```bash
python -m csvstat <datei>
```

Beispiel:

```bash
csvstat daten.csv
```

Die Start- und Prüfkommandos sind in `RUN.json` deklariert; der Startbefehl ist
`python -m csvstat --help`.

## Optionen

| Option | Bedeutung |
| --- | --- |
| `<datei>` | Pflichtargument: die zu analysierende CSV-Datei |
| `--delimiter CHAR` | Trennzeichen der Eingabedatei (Standard: `,`) |
| `--columns a,b,c` | Nur diese Spalten ausgeben, in genau dieser Reihenfolge |
| `--json` | Bericht als JSON statt als Tabelle ausgeben |
| `--help` | Hilfe anzeigen und mit Exit-Code 0 beenden |

## Exit-Codes

| Code | Bedeutung |
| --- | --- |
| 0 | Erfolg |
| 1 | Datei- oder Lesefehler (z. B. Datei nicht gefunden, leere Datei) |
| 2 | Aufruffehler (z. B. unbekannte Spalte, unbekannte Option) |

Fehlermeldungen auf stderr haben immer die Form `csvstat: <Meldung>`.

## Tests ausführen

```bash
python -m pytest
```
