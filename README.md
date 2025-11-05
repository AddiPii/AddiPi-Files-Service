# AddiPi Files Service

Deploy IP: http://addipi-files.b3aaefdfe9dzdea0.swedencentral.azurecontainer.io:5000 
(Deploy IP może być nieaktywne z uwagi na oszczędność środków)
Lekki mikroserwis do przesyłania plików G-code do Azure Blob Storage
i powiadamiania systemu druku przez Azure Service Bus.

## Krótko

- Endpointy:
	- `POST /upload` — upload pliku (multipart/form-data). Pole pliku: `file`. Opcjonalne pole: `scheduledAt` (datetime-local).
	- `GET /health` — health check (zwraca JSON).
	- `GET /` — prosty status serwisu.
	- `GET /files/recent` - zwraca listę właściwości ostatnich 10 plików.
- Zapis plików: Azure Blob Storage, kontener `gcode`.
- Powiadomienia: Azure Service Bus — queue `print-queue` (wysyła JSON z eventem `file_uploaded`).

## Zawartość repo

- `app.py` — główny serwis Flask.
- `requirements.txt` — wymagane pakiety Python.
- `DOCKERFILE` — prosty obraz Docker do uruchomienia serwisu.
- `test.html` — prosty formularz HTML do ręcznego uploadu.

## Wymagania

- Python 3.11+ (kod testowany pod 3.13).
- Dostęp do konta Azure (Storage Account z Blob, Service Bus namespace z queue).
- Docker (Konteneryzacja i push konteneru do Azure)
- Zainstalowane zależności:

```powershell
python3 -m pip install -r .\requirements.txt
```

## Zmienne środowiskowe

Serwis odczytuje następujące zmienne środowiskowe:
- `STORAGE_CONN` — connection string do Azure Storage Account (Blob).
- `SERVICE_BUS_CONN` — connection string do Azure Service Bus (opcjonalne; jeśli brak, messaging jest wyłączony).

Przykład pliku `.env` (nie commituj prawdziwych kluczy):

```
STORAGE_CONN=DefaultEndpointsProtocol=https;AccountName=addipifiles;AccountKey=...;EndpointSuffix=core.windows.net
SERVICE_BUS_CONN=Endpoint=sb://addipisb.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=...
```

Upewnij się, że nie ma spacji wokół `=` i że nie opakowujesz wartości w `<...>`.

## Uruchomienie lokalnie

1. Ustaw zmienne środowiskowe (PowerShell), albo stwórz `.env` jeśli używasz `python-dotenv`:

```powershell
$env:STORAGE_CONN="DefaultEndpointsProtocol=https;AccountName=addipifiles;AccountKey=...;EndpointSuffix=core.windows.net"
$env:SERVICE_BUS_CONN="Endpoint=sb://addipisb.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=..."
```

2. Zainstaluj zależności i uruchom:

```powershell
python -m pip install -r requirements.txt
python app.py
```

Serwis będzie dostępny na http://localhost:5000

## Uruchomienie w Dockerze

Budowanie i uruchomienie obrazu:

```powershell
docker build -t addipi-files-service -f DOCKERFILE .
docker run -p 5000:5000 `
	-e STORAGE_CONN="DefaultEndpointsProtocol=...;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net" `
	-e SERVICE_BUS_CONN="Endpoint=sb://addipisb.servicebus.windows.net/;SharedAccessKeyName=...;SharedAccessKey=..." `
	addipi-files-service
```

## API — przykłady uploadu

Polecenie `curl` (PowerShell): użyj `curl.exe` by uniknąć aliasu PowerShell

```powershell
curl.exe -v -X POST http://localhost:5000/upload `
	-F "file=@C:\full\path\to\test.gcode" `
	-F "scheduledAt=2025-11-01T12:00:00"
```

Przykład prostego HTML (plik `test.html`) — otwórz w przeglądarce i wyślij plik.

Odpowiedź sukcesu:

```json
{"status":"success","fileId":"20251101_035701_test.gcode"}
```

## Co robi serwis po uploadzie

1. Tworzy blob o nazwie: `TIMESTAMP_originalFilename` (np. `20251101_035701_test.gcode`) w kontenerze `gcode`.
2. Publikuje wiadomość do Service Bus queue `print-queue` w formacie JSON:

```json
{
	"event": "file_uploaded",
	"fileId": "20251101_035701_test.gcode",
	"originalFileName": "test.gcode",
	"timestamp": "169xxx",
	"scheduledAt": "2025-11-01T12:00:00"
}
```

Jeśli Service Bus jest niedostępny, serwis loguje problem, ale upload do Bloba nadal zostanie wykonany.

## Troubleshooting — Service Bus

- DNS/połączenie: "getaddrinfo failed" lub "Name resolution failed" — sprawdź, czy namespace (np. `addipisb.servicebus.windows.net`) istnieje i jest poprawny.
- `amqp:client-error` — często oznacza, że kolejka `print-queue` nie istnieje lub brak uprawnień.

Szybkie sprawdzenia (PowerShell):

```powershell
nslookup addipisb.servicebus.windows.net
Test-NetConnection addipisb.servicebus.windows.net -Port 5671
Test-NetConnection addipisb.servicebus.windows.net -Port 443
```

Jeśli queue nie istnieje, utwórz ją w Azure Portal lub przez Azure CLI:

```powershell
az servicebus queue create --resource-group <rg> --namespace-name <namespace> --name print-queue
```

## Usuwanie/obsługa wiadomości z kolejki

- Portal Azure -> Service Bus -> Namespace -> Queues -> `print-queue` -> Data Explorer (Service Bus Explorer) — możesz "Peek", "Receive" i "Complete"/"Dead-letter".
- Możesz też użyć prostego skryptu Python (dodam go do repo na życzenie) do znalezienia i usunięcia wiadomości po `fileId`.

## Bezpieczeństwo

- Nie commituj `.env` ani connection stringów do repo.
- Dodaj `.env` do `.gitignore`.
- Jeśli klucze wyciekły, rotuj je w Azure Portal.

## Development notes

- Serwis loguje informację o uploadzie i ewentualnych błędach przy łączeniu do Service Bus.
- W kodzie istnieje fallback: jeśli Service Bus jest nieosiągalny, aplikacja nadal zapisze plik w Blob i zaloguje, że wysyłka wiadomości została pominięta.

## Contribution

- Zgłaszaj PRy do gałęzi `main`.
- Po mergu uruchom lokalne testy: uruchom serwis i prześlij testowy plik przy pomocy `test.html` lub `curl`.

## Przydatne polecenia

```powershell
curl.exe http://localhost:5000/health
docker build -t addipi-files-service -f DOCKERFILE .
```

---

Jeśli chcesz, mogę dodać do repo `README.md` (zostało zapisane), `.env.example`, `.gitignore` oraz opcjonalne skrypty pomocnicze (np. do usuwania wiadomości z kolejki). 


## Zmienne środowiskowe serwisu (szczegóły)

- `STORAGE_CONN` — connection string do Storage Account (wymagane).
- `SERVICE_BUS_CONN` — connection string do Service Bus (opcjonalne).
- `ALLOWED_EXTENSIONS` — lista dopuszczalnych rozszerzeń, domyślnie `.gcode`.
- `MAX_UPLOAD_SIZE` — maksymalny rozmiar uploadu w bajtach (domyślnie 10 MB).
- `STRICT_CONTENT_CHECK` — `0`/`1`, jeśli `1` włącza prostą heurystykę sprawdzania zawartości pliku.
- `ALLOWED_ORIGINS` — lista originów dozwolonych przez CORS (comma-separated). Używaj pełnych adresów z protokołem, np. `https://app.yourdomain.com`.

## CORS i deploy do ACI z dynamicznym FQDN

Jeśli deployujesz do Azure Container Instances (ACI), FQDN kontenera może się zmieniać. Najlepsze podejście:

1. W kodzie serwisu `app.py` czytaj `ALLOWED_ORIGINS` z env i ustaw CORS dynamicznie.
2. Przy deployu ustaw `ALLOWED_ORIGINS` na domenę frontendu (lub na FQDN ACI jeśli frontend też używa tej domeny).

Przykład `az container create` z przekazaniem `ALLOWED_ORIGINS`:

```powershell
az container create -g "<RG>" -n "<ACI_NAME>" \
	--image "<ACR_LOGIN_SERVER>/<IMAGE_NAME>:<TAG>" \
	--dns-name-label "<DNS_LABEL>" \
	--ports 5000 \
	--environment-variables ALLOWED_ORIGINS="https://app.yourdomain.com" \
	--registry-login-server "<ACR_LOGIN_SERVER>" \
	--registry-username "<ACR_USERNAME>" \
	--registry-password "<ACR_PASSWORD>"
```

Uwaga: do testów lokalnych możesz użyć `http://localhost:3000` jako origin, ale w produkcji podawaj dokładną domenę.

