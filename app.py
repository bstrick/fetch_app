import math
from flask import Flask, request
import uuid

app = Flask(__name__)

#local hash_map used to save results
local_memory = {}

@app.route('/receipts/process', methods=['POST'])
def receipts():
    json = request.get_json()
    total_points = 0

    #Checking for JSON abnormalities.
    if ("retailer" not in json or
        "total" not in json or
        "items" not in json or
        "purchaseTime" not in json or
        "purchaseDate" not in json):
        return {"error": "Missing required parameters"}, 400

    #Count Alphanumerical characters in retailer name
    for character in json['retailer']:
        if character.isalnum():
            total_points += 1

    # total checks
    if '.' not in json['total']:
        return {"error": "Total variable formatted incorrectly"}, 400

    dollar,cents = json['total'].split('.')

    if cents == '00' and dollar != '00':
        total_points += 50

    if float(json['total']) % .25 == 0 and json['total'] != '00.00':
        total_points += 25

    # 5 pts every 2 items
    total_points += len(json['items']) // 2 * 5

    # If trimmed length of item description is a multiple of 3, multipy price by .2 and round up
    for item in json['items']:
        if ('shortDescription' not in item or
                'price' not in item):
            return {"error": "items block missing values. Please include a shortDescription and price with every item"}, 400

        if len(item['shortDescription'].strip()) % 3 == 0:
            total_points += math.ceil(float(item['price']) * .2)

    if '-' not in json['purchaseDate'] or int(json['purchaseDate'].split('-')[1]) > 12 or int(
            json['purchaseDate'].split('-')[2]) > 31:
        return {"error": "Please format a valid Purchase Date in the format YYYY-MM-DD"}, 400

    # 6 points if purchase date is odd
    if int(json['purchaseDate'].split('-')[2]) % 2 == 1:
        total_points += 6

    # 10 points if time of purchase is between 2 and 4 PM
    if ':' not in json['purchaseTime']:
        return {"error": "Please format purchase time in the format HH:MM"}, 400

    PurchaseTime = json['purchaseTime'].split(':')
    hour, minute = map(int, PurchaseTime)
    totalTime = hour * 60 + minute

    #840 = 14 * 60 (14:00) 960 = 16*60 (16:00)
    if 840 <= totalTime < 960:
        total_points += 10

    #generate uuid for this result so it can be pulled later
    result_uuid = uuid.uuid4()
    while result_uuid in local_memory:
        result_uuid = uuid.uuid4()

    local_memory[str(result_uuid)] = total_points

    return {'id':str(result_uuid)}, 200


@app.route('/receipts/<string:id>/points', methods=['GET'])
def points(id):
    if id not in local_memory:
        return {'error': 'No receipt found for that ID.'}, 404
    return {"points": local_memory[id]}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)