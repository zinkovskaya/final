# Дружелюбный Ассистент Бот "Voice Guide"

Этот Telegram бот представляет собой внимательного и дружелюбного ассистента, готового помочь вам в различных ситуациях. Он может быть экспертом в домашних заданиях по истории, эмпатичным собеседником для обсуждения ваших личных переживаний или просто компаньоном для общения.

## Функциональности

1. Принятие текстовых и голосовых сообщений от пользователя.
2. Обработка текстовых сообщений: отправка текста в качестве промта в YandexGPT для генерации ответа.
3. Обработка голосовых сообщений: расшифровка текста с помощью SpeechKit, отправка текста в YandexGPT для генерации ответа, преобразование ответа в голос с помощью SpeechKit.
4. Отправка ответа пользователю в том же формате, в котором был получен запрос: текст в ответ на текст, голос в ответ на голос.

## Использование

1. Отправьте боту текстовое или голосовое сообщение.
2. Бот обработает ваш запрос и сгенерирует ответ.
3. Получите ответ от бота в том же формате, что и ваш запрос.

## Команды бота

- /start - начало работы бота
- /help - для помощи с ботом
- /about - описание бота
- /tts - озвучить текст
- /sst - распознать голосовой файл
- /debug - посмотреть ошибки