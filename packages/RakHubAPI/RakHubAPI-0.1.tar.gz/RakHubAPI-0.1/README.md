# RakHubAPI

Библиотека для работы с API RakHub, позволяющая удобно запускать RakBot сессии на игроков San Andreas Multiplayer (SAMP).

## Установка

Установите библиотеку с помощью pip:
```bash
pip install RakHubAPI
```
## Использование

Сначала импортируйте и инициализируйте RakHubAPI с вашим API ключом:
```python
from RakHubAPI import RakHubAPI
api = RakHubAPI('your-api-key')
```
Затем вы можете запустить сессию, передав параметры в метод `start_session`:
```python
rakstart = api.start_session(token=1, nickname='test', timeout=12, session_name='test-session', ip='127.0.0.1')
```
В этом примере `nickname` - это никнейм игрока, `timeout` - это время в часах, через которое сессия будет остановлена, `session_name` - это имя сессии, и `ip` - это IP-адрес сервера без порта 7777.

## Лицензия

Этот проект лицензирован под лицензией MIT - подробности см. в файле LICENSE.
