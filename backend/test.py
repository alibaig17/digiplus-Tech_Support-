from pymongo import MongoClient

uri = "mongodb+srv://admin:Osmanali17@cluster0.cdkkwmz.mongodb.net/?appName=Cluster0"

client = MongoClient(uri)

print(client.admin.command("ping"))
print("Connected!")