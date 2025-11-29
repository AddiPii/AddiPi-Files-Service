# AddiPi Files Service

Deploy IP: http://addipi-files.b3aaefdfe9dzdea0.swedencentral.azurecontainer.io:5000 
(Deploy IP może być nieaktywne z uwagi na oszczędność środków)
Lekki mikroserwis do przesyłania plików G-code do Azure Blob Storage
i powiadamiania systemu druku przez Azure Service Bus.

# AddiPi Files Service — English

Lightweight Flask microservice for uploading G-code files to Azure Blob Storage and sending notifications via Azure Service Bus.

IMPORTANT: Recent refactor — endpoints were moved to a Flask `Blueprint` and controller functions were added. See "Repository changes" below.

Quick summary
- Endpoints:
	- `POST /upload` — upload file (multipart/form-data). File field: `file`. Optional form field: `scheduledAt`.
	- `GET /health` — health check (returns JSON).
	- `GET /` — basic service status.
	- `GET /files/recent` — recent files (up to 10 most recent).
- Storage: Azure Blob Storage, container `gcode`.
- Notifications: Azure Service Bus queue `print-queue` (message JSON with `event: file_uploaded`). Service Bus is optional — uploads still succeed if messaging fails.

Repository changes (recent)
- `controllers/files_controller.py` — new controller functions `upload_file_handler` and `recent_files_handler` that contain upload/list logic.
- `routes/files_bp.py` — new Flask `Blueprint('files')` which registers routes and delegates to the controller functions.
- `app.py` — now registers the blueprint and exposes dependencies via `app.config` (e.g. `BLOB_CLIENT`, `SB_CLIENT`, `MAX_UPLOAD_SIZE`, `ALLOWED_EXTENSIONS`, `STRICT_CONTENT_CHECK`).
- `.gitignore` — added `controllers/__pycache__/` (and consider ignoring all `__pycache__/`).

Important notes about defaults
- `MAX_UPLOAD_SIZE` default: 50 * 1024 * 1024 (50 MB).
- `ALLOWED_EXTENSIONS` default: `.gcode` (can be set via env `ALLOWED_EXTENSIONS` comma-separated).

Environment variables
- `STORAGE_CONN` — required: Azure Storage connection string for Blob access.
- `SERVICE_BUS_CONN` — optional: Azure Service Bus connection string. If missing, messaging is disabled (uploads still work).
- `ALLOWED_EXTENSIONS` — optional comma-separated list (default `.gcode`).
- `MAX_UPLOAD_SIZE` — optional (bytes, default 50MB).
- `STRICT_CONTENT_CHECK` — `0` or `1` (default `0`). If `1`, a simple content heuristic is applied to uploaded files.

Local run (example, PowerShell)
1. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

2. Set env vars and run (example):

```powershell
#$env:STORAGE_CONN = "DefaultEndpointsProtocol=...;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net"
#$env:SERVICE_BUS_CONN = ""  # optional
python app.py
```

If you don't want to connect to Azure for local testing, either set a placeholder `STORAGE_CONN` (e.g. a local emulator) or modify `app.py` to allow running without a blob client during development. I can add a safe development mode on request.

Running tests
- There is a simple test `tests/test_health.py` that imports `app` and checks `/health`. Be aware `app.py` attempts to create `BlobServiceClient` at import time; to run tests without Azure, set `STORAGE_CONN` to a valid value or update the app to avoid raising on missing env. Example command:

```powershell
# set env then run pytest
#$env:STORAGE_CONN = "UseDevelopmentStorage=true"
# AddiPi Files Service — English

Lightweight Flask microservice for uploading G-code files to Azure Blob Storage and sending notifications via Azure Service Bus.

Important: Recent refactor moved route logic into a Flask Blueprint and controller functions — see "Repository changes".

## Quick summary

- Endpoints:
	- `POST /upload` — upload file (multipart/form-data). File field: `file`. Optional form field: `scheduledAt`.
	- `GET /health` — health check (returns JSON).
	- `GET /` — basic service status.
	- `GET /files/recent` — recent files (up to 10 most recent).
- Storage: Azure Blob Storage, container `gcode`.
- Notifications: Azure Service Bus queue `print-queue` (message JSON with `event: file_uploaded`). Service Bus is optional — uploads still succeed if messaging fails.

## Repository changes

- `controllers/files_controller.py` — new controller functions `upload_file_handler` and `recent_files_handler`.
- `routes/files_bp.py` — new Flask `Blueprint('files')` that registers routes and delegates to controllers.
- `app.py` — now registers the blueprint and exposes dependencies via `app.config` (e.g. `BLOB_CLIENT`, `SB_CLIENT`, `MAX_UPLOAD_SIZE`, `ALLOWED_EXTENSIONS`, `STRICT_CONTENT_CHECK`).
- `.gitignore` — added `controllers/__pycache__/` (consider ignoring all `__pycache__/`).

## Defaults and configuration

- `MAX_UPLOAD_SIZE` default: 50 * 1024 * 1024 (50 MB).
- `ALLOWED_EXTENSIONS` default: `.gcode` (env `ALLOWED_EXTENSIONS` comma-separated).
- `STRICT_CONTENT_CHECK` default: `0` (set to `1` to enable a simple content heuristic).

Environment variables

- `STORAGE_CONN` — required: Azure Storage connection string (Blob).
- `SERVICE_BUS_CONN` — optional: Azure Service Bus connection string. If missing, messaging is disabled.
- `ALLOWED_EXTENSIONS` — optional comma-separated list (default `.gcode`).
- `MAX_UPLOAD_SIZE` — optional (bytes, default 50MB).
- `STRICT_CONTENT_CHECK` — `0` or `1` (default `0`).

## Local run (PowerShell)

1. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

2. Set env vars and run (example):

```powershell
# set STORAGE_CONN to your Azure Storage connection string
$env:STORAGE_CONN = "DefaultEndpointsProtocol=...;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net"
# optional: SERVICE_BUS_CONN
$env:SERVICE_BUS_CONN = ""
python app.py
```

If you want to run without Azure for quick local testing, either set a placeholder `STORAGE_CONN` (local emulator) or I can add a development mode that avoids raising on missing storage.

## Tests

- `tests/test_health.py` imports `app` and checks `/health`.
- Note: `app.py` currently instantiates `BlobServiceClient` at import time and will raise if `STORAGE_CONN` is not set. To run tests without Azure, set `STORAGE_CONN` or modify `app.py` to allow importing without a blob client. Example:

```powershell
# set env then run pytest
$env:STORAGE_CONN = "UseDevelopmentStorage=true"
pytest -q
```

## API examples

- Upload (PowerShell/curl.exe):

```powershell
curl.exe -v -X POST http://localhost:5000/upload `
	-F "file=@C:\path\to\test.gcode" `
	-F "scheduledAt=2025-11-01T12:00:00"
```

- Health:

```powershell
curl.exe http://localhost:5000/health
```

## Notes about CORS

- CORS is configured in `app.py` (includes `http://localhost:3000` and a deployment FQDN). Edit `app.py` to change allowed origins or ask me to add env-driven CORS.

---

# AddiPi Files Service — Polski

Lekki mikroserwis Flask do przesyłania plików G-code do Azure Blob Storage i powiadamiania przez Azure Service Bus.

Ważne: Niedawno zrefaktoryzowano kod — logika tras przeniesiona do `Blueprint` i funkcji w folderze `controllers`.

## Szybkie podsumowanie

- Endpointy:
	- `POST /upload` — przesyłanie pliku (multipart/form-data). Pole pliku: `file`. Opcjonalne pole formularza: `scheduledAt`.
	- `GET /health` — health check (zwraca JSON).
	- `GET /` — status serwisu.
	- `GET /files/recent` — lista ostatnich plików (do 10).
- Przechowywanie: Azure Blob Storage, kontener `gcode`.
- Powiadomienia: Service Bus queue `print-queue` (wiadomość JSON z `event: file_uploaded`). Messaging jest opcjonalny — uploady działają bez kolejki.

## Zmiany w repozytorium

- `controllers/files_controller.py` — funkcje kontrolera `upload_file_handler` i `recent_files_handler`.
- `routes/files_bp.py` — `Blueprint('files')` rejestrujący trasy i delegujący do kontrolerów.
- `app.py` — rejestruje blueprint i umieszcza zależności w `app.config` (np. `BLOB_CLIENT`, `SB_CLIENT`, `MAX_UPLOAD_SIZE`, `ALLOWED_EXTENSIONS`, `STRICT_CONTENT_CHECK`).
- `.gitignore` — dodano `controllers/__pycache__/`.

## Domyślne ustawienia

- `MAX_UPLOAD_SIZE`: 50 MB (50 * 1024 * 1024).
- `ALLOWED_EXTENSIONS`: domyślnie `.gcode`.
- `STRICT_CONTENT_CHECK`: domyślnie `0` (ustaw `1`, by włączyć prostą walidację zawartości pliku).

## Zmienne środowiskowe

- `STORAGE_CONN` — wymagane: connection string do Azure Storage (Blob).
- `SERVICE_BUS_CONN` — opcjonalne: connection string do Azure Service Bus. Jeśli brak, messaging jest wyłączony.
- `ALLOWED_EXTENSIONS`, `MAX_UPLOAD_SIZE`, `STRICT_CONTENT_CHECK` — jak wyżej.

## Uruchomienie lokalne (PowerShell)

1. Zainstaluj zależności:

```powershell
python -m pip install -r requirements.txt
```

2. Ustaw zmienne środowiskowe i uruchom:

```powershell
$env:STORAGE_CONN = "DefaultEndpointsProtocol=...;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net"
$env:SERVICE_BUS_CONN = ""
python app.py
```

Jeśli chcesz testować lokalnie bez Azure, ustaw tymczasowy `STORAGE_CONN` lub poproszę o dodanie trybu developerskiego, który nie wymaga storage przy imporcie.

## Testy

- `tests/test_health.py` sprawdza endpoint `/health`.
- Uwaga: `app.py` tworzy `BlobServiceClient` podczas importu; aby uruchomić testy bez Azure ustaw `STORAGE_CONN` lub zmodyfikuj `app.py`.

## Przykłady API

- Upload (PowerShell/curl.exe):

```powershell
curl.exe -v -X POST http://localhost:5000/upload `
	-F "file=@C:\path\to\test.gcode"
```

## CORS

- CORS jest ustawione w `app.py` (m.in. `http://localhost:3000` i FQDN deployu). Edytuj `app.py` aby zmienić dozwolone originy lub poproś mnie o dodanie konfiguracji przez zmienne środowiskowe.

---
