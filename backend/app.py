from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)
CORS(app)  # prevent CORS error

client = MongoClient('mongodb://localhost:27017')
db = client['flaskreactfullstack']  # db name

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/users', methods=['POST', 'GET'])
def data():
    if request.method == 'POST':
        body = request.json
        firstName = body['firstName']
        lastName = body['lastName']
        emailId = body['emailId']
        db['users'].insert_one({
            "firstName": firstName,
            "lastName": lastName,
            "emailId": emailId
        })
        return jsonify({
            'status': 'Data is posted to MongoDB',
            'firstName': firstName,
            'lastName': lastName,
            'emailId': emailId
        })

    if request.method == 'GET':
        allData = db['users'].find()
        dataJson = []
        for data in allData:
            id = str(data['_id'])  # Access the _id field
            firstName = data['firstName']
            lastName = data['lastName']
            emailId = data['emailId']

            dataDict = {
                'id': id,
                'firstName': firstName,
                'lastName': lastName,
                'emailId': emailId
            }
            dataJson.append(dataDict)
        return jsonify(dataJson)

@app.route('/users/<string:id>', methods=['GET', 'PUT', 'DELETE'])
def onedata(id):
    if request.method == 'GET':
        data = db['users'].find_one({"_id": ObjectId(id)})
        if data:
            id = data['_id']
            firstName = data['firstName']
            lastName = data['lastName']
            emailId = data['emailId']

            dataDict = {
                "id": str(id),
                "firstName": firstName,
                "lastName": lastName,
                "emailId": emailId
            }

            return jsonify(dataDict)
        else:
            return jsonify({"error": "User not found"}), 404

    elif request.method == 'PUT':
        # Logic for updating user data
        # Assuming you receive updated data in the request
        updated_data = request.json
        result = db['users'].update_one({"_id": ObjectId(id)}, {"$set": updated_data})
        if result.modified_count == 1:
            return jsonify({"status": "User data updated successfully"})
        else:
            return jsonify({"error": "User not found"}), 404

    elif request.method == 'DELETE':
        result = db['users'].delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 1:
            return jsonify({"status": "Data id: {} is deleted".format(id)})
        else:
            return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    app.debug = True
    app.run()
