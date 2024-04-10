from flask import Flask
import json

app = Flask(__name__)
items = {}
with open('jama_items.json') as f:
  items = json.loads(f.read())

@app.route('/rest/v1/items/<id>', methods=['GET'])
def index(id):
  return json.dumps(items[str(id)])

@app.route('/rest/v1/items', methods=['GET'])
def get_items():
  ret_items = list(items.values())
  ret_val = {
    'meta': {
      'pageInfo': {
        'startIndex': 0,
        'totalResults': len(ret_items)
      }
    },
    'data': ret_items
  }
  return json.dumps(ret_val)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)