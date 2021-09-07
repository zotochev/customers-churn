import numpy as np

from flask import Flask, request, jsonify, render_template

import pickle
import sys
from pathlib import Path
from datetime import datetime

from ProcessData import ProcessData


app = Flask(__name__)
model = None
a = None

file = Path('model.pkl')
if file.is_file() \
        and not file.is_dir():
    model = pickle.load(open('model.pkl', 'rb'))
    a = ProcessData(model)
    print("model loaded")
else:
    print("model load failed")


@app.route('/', methods=['POST', 'GET'])
def prolong():
    if request.method == 'POST':
        print('recieved POST request')
        if a is None:
            return jsonify({'status': 'Error: model load failed'})

        data = request.get_json(force=True)
        insert_json_rv = a.insert_json_data(data)
        if insert_json_rv is not None:
            result = a.predict()
            return jsonify(result)
        else:
            return jsonify({'status': 'Error: insert_json (to model) function returned None'})
    else:
        return jsonify({'status': 'Method not allowed'})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)

