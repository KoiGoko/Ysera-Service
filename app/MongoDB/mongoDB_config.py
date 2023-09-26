import pymongo

# Configure MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB server URL

# Access a specific database
db = client["mydatabase"]

# Access a specific collection in the database
collection = db["mycollection"]

# Insert a document into the collection
data = {"name": "John", "age": 30}
collection.insert_one(data)

# Find documents in the collection
query = {"name": "John"}
result = collection.find(query)

for document in result:
    print(document)

# Close the MongoDB connection
client.close()
