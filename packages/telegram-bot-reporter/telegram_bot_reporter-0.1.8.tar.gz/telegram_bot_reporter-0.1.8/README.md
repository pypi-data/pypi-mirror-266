### Stack:

- [x] <a href="https://www.python.org/"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-plain.svg" alt="python" width="15" height="15"/>
  Python 3.10+ <br/></a>
- [x] <a href="https://github.com/jawah/niquests"><img src="https://user-images.githubusercontent.com/9326700/282852138-160f32e9-e6cf-495f-b39d-99891602acf9.png" alt="niquests" width="15" height="15"/>
  Niquests 3.5.5+ <br/>

### Installation

    pip install telegram-bot-reporter

### Usage Sync

    from telegram_bot_reporter import Bot

    bot = Bot(bot_token=TELEBOT_TOKEN, chat_id=CHAT_ID)

    # Send message
    bot.send_message('Hello, world')

    # Send file
    temp_file = Path('test.txt')
    with open(temp_file, mode='w', encoding='utf-8') as f:
        f.write('Test message')
    bot.send_document(temp_file)

    # Send long message (more than 4000 symbols)
    bot.send_message('Very long message over 4000 symbols', split_message=True)

### Usage Async

    from telegram_bot_reporter import AsyncBot

    bot = AsyncBot(bot_token=TELEBOT_TOKEN, chat_id=CHAT_ID)

    await bot.send_message('Hello, world')

    # Send file
    temp_file = Path('test.txt')
    with open(temp_file, mode='w', encoding='utf-8') as f:
        f.write('Test message')
    await bot.send_document(temp_file)

    # Send long message (more than 4000 symbols)
    await bot.send_message('Very long message over 4000 symbols', split_message=True)
