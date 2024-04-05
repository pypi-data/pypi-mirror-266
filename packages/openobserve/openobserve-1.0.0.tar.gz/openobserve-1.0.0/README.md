# OpenObserve
Biblioteka do wysyłania logów do OpenObserve

## Logi
Logi błędów biblioteki oraz dla `global_exception_logger` to:
```bash
cd /home/$USER/.openobserve/logs/log.log
```

## Konfiguracja
```python
import openobserve
openobserve.username = ''
openobserve.password = ''
openobserve.host = 'http://127.0.0.1:5080',
openobserve.stream_global = 'default' #domyślny stream
openobserve.organization_global = 'default' #domyślna organizacja
openobserve.ssl_verify = False #weryfikacja ssl hosta
openobserve.additional_info = False #dodatkowe dane
```

## Wysyłanie loga
pola `_stream` oraz `_organization` nadpisują `stream_global` oraz `organization_global`
```python
def send(
    job: Any = '',
    level: str = 'INFO',
    _stream: str = None,
    _organization: str = None,
    **kwargs
)
```
### Przykład
```python
import openobserve
openobserve.send(job='test', _return_data=True,message='test message')
```
Log:
```json
{
    '_timestamp': '2024-03-25T20:10:47.106', 
    'level': 'INFO',
    'job': 'test', 
    'message': 'test message'
}
```

## Dodatkowe dane dla openovserver.additionalinfo
```json
{
    'hostname': socket.gethostname(),
    'user_name': socket.gethostname(),
    'system': platform.system(),
    'system_architecture': platform.machine(),
    'system_version': platform.version(),
    'system_release': platform.release(),
    'python_version': platform.python_version()
}
```

## Globalne zbieranie błędow
Kod do globalnego zbierania błędów z projektu
```python
import openobserve.global_exception_logger

print(1 / 0)
```
W tym momencie log wysyła się na serwer oraz zapisuje na dysku
### Konfiguracja
```python
import openobserve.global_exception_logger

openobserve.global_exception_logger.organization_global = 'default'
openobserve.global_exception_logger.stream_global = 'default'
```