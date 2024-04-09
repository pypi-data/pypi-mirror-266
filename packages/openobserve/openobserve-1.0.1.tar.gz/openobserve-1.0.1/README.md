# OpenObserve
A library for sending logs to OpenObserve

## Logi
Logs for library errors and for `global_exception_logger` are located at:
```bash
cd /home/$USER/.openobserve/logs/log.log
```

## Configuration
```python
import openobserve
openobserve.username = ''
openobserve.password = ''
openobserve.host = 'http://127.0.0.1:5080',
openobserve.stream_global = 'default' #default stream
openobserve.organization_global = 'default' #default organization
openobserve.ssl_verify = False #SSL host verification
openobserve.additional_info = False #additional data
```

## Sending a log
Fields _stream and _organization override stream_global and organization_global
```python
def send(
    job: Any = '',
    level: str = 'INFO',
    _stream: str = None,
    _organization: str = None,
    **kwargs
)
```
### Example
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

## Additional data for openobserve.additionalinfo
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

## Global error collection
Code for globally collecting errors from the project
```python
import openobserve.global_exception_logger

print(1 / 0)
```
At this point, the log is sent to the server and saved on disk
### Configuration
```python
import openobserve.global_exception_logger

openobserve.global_exception_logger.organization_global = 'default'
openobserve.global_exception_logger.stream_global = 'default'
```