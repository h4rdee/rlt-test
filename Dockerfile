FROM mongo:7.0

# Install Python
RUN apt-get update -y
RUN apt-get install -y python3-pip python3.9 build-essential

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Set the environment variable for tg_bot_token
# ARG tg_bot_token
# ENV TG_BOT_TOKEN=$tg_bot_token

# Run MongoDB and import the database, then run app.py
RUN mkdir -p /data/db
COPY ./db/sample_collection.bson /data/db/sample_collection.bson
CMD mongod --fork --logpath /var/log/mongodb.log && \
    mongorestore --host=localhost --port=27017 /data/db/sample_collection.bson && \
    python3 app.py