# MischiefKid 🎮 Game Console

![image](https://github.com/sxannyy/MischiefKid_game_console/blob/main/logo.png)

Данная консоль поддерживает авторизацию через **Telegram-бота**, а также хранит **персональные сохранения** для каждого пользователя в облаке.

## 🛒 Покупка консоли

Каждая консоль поставляется с прошивкой, поддерживающей несколько пользователей. Для привязки пользователя используется Telegram-бот и одноразовый 6-значный токен входа.

## 📝 Регистрация в системе

Для подключения своей учетной записи выполните следующие шаги:

1. Откройте Telegram и найдите нашего бота: `@MischiefKidConsoleBot`.
2. Отправьте команду /register для регистрации.
3. Укажите данные: **логин, имя и фамилию**.
4. Бот занесет ваши данные и чат ID в БД.
5. Вы получите **одноразовый 6-значный токен входа**.

**Обратите внимание: токен одноразовый, то есть после его ввода, во второй раз воспользоваться им не получится!**

## 👤 Добавление другого пользователя на консоль

1. Включите консоль.
2. В главном меню выберите пункт "Войти".
3. Зарегистрируйтесь в Telegram-боте с аккаунта другого человека.
4. Получите **6-значный токен**.
5. Введите полученные данные и свой логин. 

После подтверждения создается новый профиль, связанный с вашим аккаунтом в Telegram.

### В профиле доступны:
- Общая библиотека игр;
- Индивидуальные сохранения.

Вы можете переключаться между пользователями через главное меню и вкладку **"Профили"**.

## 🕹 Использование консоли

После входа в профиль:
- Загружается **общая библиотека игр**.
- Прогресс сохраняется **отдельно от других пользователей**.
- Можно запускать игры и загружать сохранения.

## 🤖 Управление аккаунтом через Telegram

Основные команды бота:
- **/start** - начало работы бота, здесь вы можете ознакомиться с командами;
- **/register** - регистрация пользователя;
- **/token** - получение 6-значного токена.

Вы можете входить в свой профиль в любое время и продолжать игру с того места, где остановились.

## 🔍 Дополнительно

**Поддержка**:
Если возникли вопросы — обратитесь напрямую к нам!

**Диаграмма последовательностей проекта**:
![image](https://github.com/sxannyy/MischiefKid_game_console/blob/main/diagram.png)

**Схема использования игровой консоли**:
![image](https://github.com/sxannyy/MischiefKid_game_console/blob/main/scheme.png)

## ⚙️ Настройка и установка проекта
При необходимости сделать ```chmod +x ./scripts/<script_name>.sh``` для всех скриптов!

### Для установки всех библиотек python и linux, запускаем в папке проекта:
```
./scripts/configure.sh
```

### Для поднятия сервисов баз для локальной разработки нужно запустить команду:
```
sudo make up
```

### Для запуска FastAPI и Telegram-бота:
```
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
