# Solana Wallet Analyzer

Dieses Projekt ist ein Tool zur Analyse von Solana-Wallets. Es identifiziert aktive Wallets und analysiert deren Aktivitäten über einen bestimmten Zeitraum.

## 🚀 Funktionen

- Identifizierung aktiver Wallets basierend auf Transaktionssignaturen
- Analyse der Wallet-Aktivitäten über einen konfigurierbaren Zeitraum (standardmäßig 30 Tage)
- Berechnung von Profit, Transaktionsanzahl und Bilanzänderungen
- Identifikation von Top-Tradern (>10% Gewinn im Analysezeitraum)
- Umfangreiche Logging-Funktionalität

## 📁 Hauptkomponenten

| Datei | Beschreibung |
|-------|--------------|
| `main.py` | Hauptskript zur Ausführung der Analyse |
| `wallet_identification.py` | Modul zur Identifizierung aktiver Wallets |
| `wallet_analysis.py` | Modul zur Analyse der identifizierten Wallets |
| `solana_api.py` | Modul für die Interaktion mit der Solana-API |
| `utils.py` | Hilfsmodul mit Funktionen wie Profitberechnung |

## 🔧 Verwendung

1. Stellen Sie sicher, dass alle Abhängigkeiten installiert sind.
2. Führen Sie `main.py` aus:
   ```python
   python main.py
   ```
3. Die Ergebnisse werden in der Konsole ausgegeben und in Log-Dateien gespeichert.

## 📊 Log-Dateien

Der Analyzer erstellt folgende Log-Dateien:

- `start_process_{timestamp}.log`: Protokolliert den Start des Analyseprozesses
- `identified_wallets_{timestamp}.log`: Enthält die identifizierten aktiven Wallets
- `analyzed_wallets_{timestamp}.log`: Enthält die detaillierten Analyseergebnisse aller Wallets
- `top_traders_{timestamp}.log`: Listet die Top-Trader mit über 10% Gewinn auf
- `end_process_{timestamp}.log`: Protokolliert den Abschluss des Analyseprozesses

## ⚠️ Hinweis

> Dieses Projekt befindet sich in der Entwicklung. Bitte beachten Sie die Nutzungsbedingungen und Beschränkungen der Solana-API bei der Verwendung dieses Tools.

## 🤝 Beitrag

Beiträge zum Projekt sind willkommen. Bitte erstellen Sie einen Pull Request oder eröffnen Sie ein Issue für Vorschläge und Fehlermeldungen.

**Beispiel-Ausgabe:**

```
Analysis Results:
Address: Wallet123XYZ
Transactions in the last 30 days: 42
Last activity: 2023-12-08 15:30:45
Profit: 12.5%
--------------------------------------------------
```
