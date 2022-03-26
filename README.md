 # BlackJackBot VK
 Этот проект выполнен в качестве выпускного в backend-школе от [KTS](https://metaclass.kts.studio/beginner_backend)

## Идея
 - Целью данного проекта была реализация игрового бота в VK и API админа.

### Архитектура
Приложение можно разделить на три логических составляющих:

- `VK poller` - получает обновления/действия пользователя из VK и передает их `Bot manager` 
- `Bot manager` - логика обработки событий бота
- `Admin API` - позволяет собрать статистику/информацию по проведенным и текущим играм
![Архитектура](https://github.com/cherrykolya/BlackJackProjectKTS/main/images_for_readme/architecture.png)

### БД
Я выделил следующие сущности БД
![БД](https://github.com/cherrykolya/BlackJackProjectKTS/main/images_for_readme/BD.png)

### API
##### Админская часть
- `/admin.login` - авторизация админа по почте и паролю 
- `/admin.current` - получение текущего админа

##### Информация по пользователям/играм
- `/blackjack.add_cash` - добавить деньги пользователю по его vk_id
- `/blackjack.get_players` - получить игроков за столом, по id стола
- `/blackjack.get_user` - получить информацию о пользователе по vk_id
- `/blackjack.get_table` - получить информацию о столе по его id

Все методы и их описание доступны в swagger
![swagger](https://github.com/cherrykolya/BlackJackProjectKTS/main/images_for_readme/swagger.png)

### Пример игры
![work](https://github.com/cherrykolya/BlackJackProjectKTS/main/images_for_readme/work.gif)
## Стэк
| library | version |
| ------ | ------ |
| [Aiohttp](https://docs.aiohttp.org/en/stable/) | 3.7.4 |
| [Postgres](https://www.postgresql.org/) | - |
| [Docker](https://www.docker.com/) | 20.10.12 |
| [Gino](https://python-gino.org/) | 1.0.1 |