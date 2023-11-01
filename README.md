# RLT Test Task
Salaries aggregation Telegram bot, implemented using `mongodb` and `aiogram`

# Running:
You can run this bot either locally or by using Docker container

## Running via Docker container
1. **Build** Docker image <br>
   `docker build -t rlt-test .`

2. **Run** it! <br>
   `docker run -d --name=rlt-test-container -p 5000:5000 -e TG_BOT_TOKEN="YOUR_TG_BOT_TOKEN_HERE" rlt-test`

## Running locally
1. **Clone** this repository
2. **Install** necessary requirements <br>
  `pip install -r requirements.txt`

3. **Export** dumped database <br>
  `mongorestore --host=localhost --port=27017 ./db/sample_collection.bson`

4. **Configure** bot by basically changing Telegram bot token in `config.json` file
   ```
   {
     ...
     "tg_bot_token": "YOUR_TG_BOT_TOKEN_HERE"
   }
   ```

6. **Run** it! <br>
  `python3 app.py`

