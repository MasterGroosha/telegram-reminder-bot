Описание на русском языке ниже.

# Trivia
[Reminder bot](http://telegram.me/eng_alarms_bot) allows you to set date, time and text to be sent at that time. 

## Under the hood
[Reminder bot](http://telegram.me/eng_alarms_bot) uses Linux ["__at__"](http://linux.die.net/man/1/at) command to schedule one-time operations (f.ex. send message to user). This is the main feature of Reminder bot: even if bot itself stops because of exception, all scheduled messages are controlled by Linux and 99,9% will be sent in time.  

## Features
* All scheduled messages are controlled by Linux itself.
* Different timezones support (_offset currently depends on your server's GMT offset_)
* Multiple languages support (_just set necessary lang file in config.py_)
* Anti-flood (_by default, new users can have not more than 5 reminders at once; expired reminders are erased from database once in a day; you can also add user's ID to "VIP"-list to allow him to have more than 5 reminders_)
* Adjustable logging
* A simple [State machine](https://en.wikipedia.org/wiki/Finite-state_machine) easiers step-by-step reminder adding

## External Requirements
- Python 3  
- [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI/) by @eternoir - the most awesome Telegram Python API I've seen
- Set "export LC_ALL=en_US.UTF-8" via Shell (or start bot from __start_clean.sh__ or __start_normal.sh__ )

## TODO:
- View/Remove currenly set reminders
- Add attachments to reminders
- Configure server offset related to GMT +O
- any new features I'll think about

Special thanks to [pevdh](https://github.com/pevdh) for help and [eternoir](https://github.com/eternnoir) for his awesome API

# Описание на русском языке
[Reminder bot](telegram.me/alarms_bot) - бот для Telegram, помогающий отправлять сообщения-напоминалки в указанное время

## Что внутри?
Основная функциональность бота кроется в Linux-команде ["__at__"](http://www.opennet.ru/man.shtml?topic=at). Данная команда идеальна для выполнения одноразовых действий. Собственно, в ней заключается и главная фича бота - даже если он зависнет или "упадёт" с какой-либо ошибкой, все уже запланированные сообщения будут доставлены, т.к. обрабатываются и хранятся самим Linux'ом. База данных в боте используется только для отслеживания количества напоминалок у каждого юзера

## Особенности
- Все запланированные сообщения будут отправлены, т.к. не зависят от состояния бота
- Поддержка различных часовых поясов (пояс "ноль" на данный момент зависит от самого сервера)
- Поддержка различных языков (загляните в config.py и выберите языковой файл)
- Анти-спам: по умолчанию, каждый юзер может иметь не более пяти одновременно активных уведомлений. Можно добавить юзера в "VIP"-лист, тогда он сможет ставить любое число напоминалок. Истёкшие уведомления могут быть удалены скриптом old_remover.py (например, можно добавить его в cron)
- Настраиваемое логирование
- Для бота был написан простейший [конечный автомат](https://ru.wikipedia.org/wiki/%D0%9A%D0%BE%D0%BD%D0%B5%D1%87%D0%BD%D1%8B%D0%B9_%D0%B0%D0%B2%D1%82%D0%BE%D0%BC%D0%B0%D1%82) для возможности пошаговой настройки напоминаний.

## Зависимости
- Python 3
- [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI/) by @eternoir - это лучший API для Telegram, который я когда-либо видел
- (_особенно актуально для работы с кириллицей_) необходимо прописать __export LC_ALL=en_US.UTF-8__ в консоли или запускать бота через скрипты __start_clean.sh__ или __start_normal.sh__ (есть в репозитории)

## TODO
- Просмотр/удаление установленных уведомлений
- Добавление аттачей (картинки, аудио, видео) к заметкам
- Обеспечение нормальных часовых поясов (не относительно сервера, а относительно GMT +O)
- Что-то ещё, что придет в мою голову :)
