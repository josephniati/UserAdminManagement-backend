from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from hashlib import sha256
import os
from dotenv import load_dotenv
load_dotenv()
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from send_email import send_email

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'abc'
JWTManager(app)

CORS(app)  # prevent CORS error

client = MongoClient('mongodb://localhost:27017')
db = client['flaskreactfullstack']  # db name

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    body = request.json
    firstName = body['firstName']
    lastName = body['lastName']
    emailId = body['emailId']
    password = body['password']
    password = sha256(password.encode()).hexdigest()
    if os.getenv('SECRET_KEY') == body['SECRET_KEY']:
        db['admins'].insert_one({
            "firstName": firstName,
            "lastName": lastName,
            "emailId": emailId,
            "password": password
        })
        return jsonify({
            'status': 'Data is posted to MongoDB',
            'firstName': firstName,
            'lastName': lastName,
            'emailId': emailId
        }), 201
    return jsonify(error="Invalid Secret Key"), 401
@app.route('/profile')
@jwt_required()
def get_Profile():
    emailId= get_jwt_identity() 
    admin = db['admins'].find_one({
        "emailId": emailId,
    })
    id = str(admin['_id'])  # Access the _id field
    firstName = admin['firstName']
    lastName = admin['lastName']
    emailId = admin['emailId']
    dataDict = {
                'id': id,
                'firstName': firstName,
                'lastName': lastName,
                'emailId': emailId
            }
    return jsonify(dataDict)
@app.route('/login', methods=['POST'])
def login():
    body = request.json
    emailId = body['emailId']
    password = body['password']
    password = sha256(password.encode()).hexdigest()
    admin = db['admins'].find_one({
        "emailId": emailId,
        "password": password
    })
    if admin:
        token = create_access_token(identity=emailId)
        return jsonify(token=token), 201
    return jsonify({
        'error': 'Invalid Credentials',
        'emailId': emailId
    }), 401

@app.route('/users', methods=['POST', 'GET'])
@jwt_required()
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
@jwt_required()
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
@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    body = request.json
    email = body['email']
    token = create_access_token(identity=email)
    url = "http://localhost:3000/password-recovery/" + token
    send_email(url,"password reset link", email)
    return jsonify(message = "email has been sent") 
@app.route('/change-password', methods=['POST'])
def change_password():
    body = request.json
    emailId = body['emailId']
    newPassword = body['newPassword']
    secretKey = body['secretKey']
    if not emailId or not newPassword or not secretKey:
        return jsonify({'error': 'Please provide email, new password, and secret key'}), 400
    user = db['admins'].find_one({'emailId': emailId})
    if user and os.getenv('SECRET_KEY') == secretKey:
        hashed_password = sha256(newPassword.encode()).hexdigest()
        db['admins'].update_one(
            {'_id': user['_id']},
            {'$set': {'password': hashed_password}}
        )
        return jsonify({'status': 'Password has been reset successfully'}), 200
    return jsonify({'error': 'Invalid email or secret key'}), 401

@app.route('/recover-password', methods=['POST'])
@jwt_required()
def recover_password():
    body = request.json
    emailId = get_jwt_identity()
    newPassword = body['newPassword']
    if not emailId or not newPassword:
        return jsonify({'error': 'Please provide email, new password, and secret key'}), 400
    user = db['admins'].find_one({'emailId': emailId})
    if user:
        hashed_password = sha256(newPassword.encode()).hexdigest()
        db['admins'].update_one(
            {'_id': user['_id']},
            {'$set': {'password': hashed_password}}
        )
        return jsonify({'status': 'Password has been reset successfully'}), 200
    return jsonify({'error': 'Invalid email or secret key'}), 401

# Payroll routes
@app.route('/payroll', methods=['POST', 'GET'])
@jwt_required()
def manage_payroll():
    if request.method == 'POST':
        body = request.json
        email_id = body['email_id']
        date = body['date']
        salary = body['salary']
        tax_deduction = body['tax_deduction']
        hours_worked = body['hours_worked']
        employee = db['users'].find_one({"emailId": email_id})
        if not employee:
           
            return jsonify(error = "employee does not exist"), 404
        db['payroll'].insert_one({
            "email_id": email_id,
            "date": date,
            "salary": salary,
            "tax_deduction": tax_deduction,
            "hours_worked": hours_worked
        })
        return jsonify({
            'status': 'Payroll data is posted to MongoDB',
            'email_id': email_id,
            "date": date,
            "salary": salary,
            "tax_deduction": tax_deduction,
            "hours_worked": hours_worked
        }), 201
    if request.method == 'GET':
        allData = db['payroll'].find()
        dataJson = []
        for data in allData:
            print (data)
            id = str(data['_id'])
            email_id = str(data['email_id'])
            date = data['date']
            salary = data['salary']
            hours_worked = data['hours_worked']
            tax_deduction = data["tax_deduction"]
            dataDict = {
                'id': id,
                'email_id': email_id,

                'date': date,
                'salary': salary,
                "tax_deduction": tax_deduction,
            "hours_worked": hours_worked
            }
        
            dataJson.append(dataDict)
        return jsonify(dataJson)

@app.route('/payroll/<string:id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def manage_single_payroll(id):
    if request.method == 'GET':
        data = db['payroll'].find_one({"_id": ObjectId(id)})
        if data:
            id = data['_id']
            email_id = str(data['email_id'])
            date = data['date']
            salary = data['salary']
            hours_worked = data['hours_worked']
            tax_deduction = data["tax_deduction"]           
            dataDict = {
                "id": str(id),
                "email_id": email_id,
                "date": date,
                "hours": hours_worked,
                "tax": tax_deduction,
                "salary": salary
            }
            return jsonify(dataDict)
        else:
            return jsonify({"error": "Payroll data not found"}), 404
    elif request.method == 'PUT':
        updated_data = request.json
        result = db['payroll'].update_one({"_id": ObjectId(id)}, {"$set": updated_data})
        if result.modified_count == 1:
            return jsonify({"status": "Payroll data updated successfully"})
        else:
            return jsonify({"error": "Payroll data not found"}), 404
    elif request.method == 'DELETE':
        result = db['payroll'].delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 1:
            return jsonify({"status": "Payroll data id: {} is deleted".format(id)})
        else:
            return jsonify({"error": "Payroll data not found"}), 404

if __name__ == '__main__':
    app.debug = True
    app.run()
