# MonVerifyTools - UnitTests

Dieses Verzeichnis enthält Dateien, die zu Fehlern führen.

Alle Dateien verwenden die Header-Prüfdatei `Fehlertests.ref`.

- Vor dem Test sollte die Datei `fixPermissionsOfTest3.sh` ausgeführt werden, um den Zugriffsfehler zu erzwingen.
- Beim Durchlauf des Skripts sollten die Dateien `readme.md` und `fixPermissionsOfTest3.sh` ignoriert werden.
- Die Datei `Test_2016-03-04_00-00-00.csv` ist als einzige Datei korrekt und muss archiviert werden.
- Alle anderen Dateien müssen in das `review`-Verzeichnis verschobene werden.

## Dateien und erwartete Fehlerausgaben

- `Test_2016-03-04_00-00.csv`    - **BadFilename** ungültiges Dateinamensformat
- `Testx_2016-03-04_00-00.csv`   - **NotExpected** (Dateinamenspräfix ist nicht in der exp-Datei)
- `Test_2016-03-04_00-00-01.csv` - **InvalidHeader** (Erste Sensorbezeichnung ist verändert)
- `TestNoFilesize_2016-03-04_00-00-02.csv` - **SampleCountMismatch** (Datensektion fehlt komplett)
- `Test_2016-03-04_00-00-03.csv` - **AccessDenied** (vor dem Test manuell Zugriffsrechte entfernen!)
- `Test_2016-03-04_00-00-04.csv` - **FileSizeMismatch** (erlaubt sind nur Abweichungen von wenigen Datenzeilen, bei dieser Datei fehlt die Hälfte)
- `Test_2016-03-04_00-00-05.csv` - **ColumnCountMismatch** (im dritten Sample fehlt eine Spalte)
- `Test_2016-03-04_00-00-06.csv` - **SampleCountMismatch** (es fehlt das letzte Sample)
- `Test_2016-03-04_00-00-07.csv` - **InvalidSamplingInterval** (2. Sample ist verspätet, wodurch das erste Intervall zu lang und das zweite Interval zu kurz ist -> 2 Fehlermeldungen)
- `Test_2016-03-04_00-00-08.csv` - **InvalidTimeStamp** (Format des 1. Zeitstempels ist falsch (- statt :))
