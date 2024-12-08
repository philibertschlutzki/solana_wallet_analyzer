Solana Wallet Analyzer
Dieses Projekt ist ein Solana Wallet Analyzer, der aktive Wallets identifiziert und analysiert.
Funktionen
Identifizierung aktiver Wallets basierend auf Signaturen
Analyse der identifizierten Wallets über einen 30-Tage-Zeitraum
Berechnung von Profit, Transaktionsanzahl und Bilanzänderungen
Identifikation von Top-Tradern (>10% Gewinn in 30 Tagen)
Umfangreiche Logging-Funktionalität
Hauptkomponenten
main.py: Hauptskript zur Ausführung der Analyse
wallet_identification.py: Identifiziert aktive Wallets
wallet_analysis.py: Analysiert die identifizierten Wallets
solana_api.py: Interagiert mit der Solana-API
utils.py: Enthält Hilfsfunktionen wie Profitberechnung
Verwendung
Stellen Sie sicher, dass alle Abhängigkeiten installiert sind.
Führen Sie main.py aus:
text
python main.py

Die Ergebnisse werden in der Konsole ausgegeben und in Log-Dateien gespeichert.
Log-Dateien
start_process_{timestamp}.log: Start des Analyseprozesses
identified_wallets_{timestamp}.log: Identifizierte aktive Wallets
analyzed_wallets_{timestamp}.log: Analyseergebnisse aller Wallets
top_traders_{timestamp}.log: Top-Trader mit über 10% Gewinn
end_process_{timestamp}.log: Abschluss des Analyseprozesses
Hinweis
Dieses Projekt befindet sich in der Entwicklung. Bitte beachten Sie die Solana API-Nutzungsbedingungen und -Beschränkungen bei der Verwendung.