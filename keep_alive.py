from flask import Flask
from threading import Thread

#create server
app = Flask('')

#Route
@app.route('/')
def main():
    return "ManageInvites Online."

#run https requests
def run():
    app.run(host="0.0.0.0", port=8080)

#Ping server
def keep_alive():
    server = Thread(target=run)
    server.start()