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

    #Count Alphanumerical characters in retailer name
    for character in json['retailer']:
        if character.isalnum():
            total_points += 1


    # Check if total has cents
    if json['total'].split('.')[1] == '00':
        total_points += 50

    # Check if total is a multiple of .25
    if float(json['total']) % .25 == 0:
        total_points += 25

    # 5 pts every 2 items
    total_points += len(json['items']) // 2 * 5

    # If trimmed length of item desc is a multi of 3, multipy price by .2 and round up
    for item in json['items']:
        if len(item['shortDescription'].strip()) % 3 == 0:
            total_points += math.ceil(float(item['price'])*.2)

    # 6 points if the day in the purchase date is odd
    if int(json['purchaseDate'].split('-')[2]) % 2 == 1:
        total_points += 6

    # 10 points if time of purchase is between 2 and 4 PM
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

@app.route('/receipts/<string:currentId>/points', methods=['GET'])
def points(currentId):
    if currentId not in local_memory:
        return {'error': 'no such id'}, 404
    return {"points": local_memory[currentId]}, 200

if __name__ == '__main__':
    app.run(debug=True)