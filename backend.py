import os
import json
from flask import Flask, Response
from flask import g, abort, request, jsonify

DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)

# We define our own jsonify rather than using flask.jsonify because we wish
# to jsonify arbitrary objects (e.g. index returns a list) rather than kwargs.
def jsonify(obj, *args, **kwargs):
    res = json.dumps(obj, indent=None if request.is_xhr else 2)
    return Response(res, mimetype='application/json', *args, **kwargs)

@app.before_request
def before_request():
    try:
        g.data = json.load(open('data.json'))
    except IOError:
        g.data = {
            'canonicals':{},
            'canonicals_by_name':{},
            'names': [],
            'next_id': 1
        }

    print g.data['next_id']

@app.teardown_request
def teardown_request(response):
    with open('data.json', 'w') as f:
        json.dump(g.data, f)

@app.after_request
def after_request(response):
    ac = 'Access-Control-'

    response.headers[ac + 'Allow-Origin']      = request.headers.get('origin', '*')
    response.headers[ac + 'Expose-Headers']    = 'Content-Length, Content-Type, Location'

    if request.method == 'OPTIONS':
        response.headers[ac + 'Allow-Headers']  = 'Content-Length, Content-Type, X-Requested-With'
        response.headers[ac + 'Allow-Methods']  = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers[ac + 'Max-Age']        = '86400'

    return response

def get_id():
    ret = g.data['next_id']
    g.data['next_id'] += 1
    return ret

@app.route('/', methods=['GET'])
def index():
    return jsonify(g.data['canonicals'])

@app.route('/canonical', methods=['GET'])
def get_canonical():
    name = request.args['name']

    if name not in g.data['canonicals_by_name']:
        id_ = get_id()
        g.data['canonicals'][id_] = {'id': id_, 'names': [name], 'name': name}
        g.data['canonicals_by_name'][name] = g.data['canonicals'][id_]

    return jsonify(g.data['canonicals_by_name'][name])

@app.route('/canonical/<id>', methods=['GET'])
def read_canonical(id):
    try:
        c = g.data['canonicals'][int(id)]
    except KeyError:
        abort(404)
    else:
        return jsonify(c)

@app.route('/canonical/<id>', methods=['PUT'])
def update_canonical(id):
    try:
        c = g.data['canonicals'][int(id)]
    except KeyError:
        abort(404)

    for n in c['names']:
        del g.data['canonicals_by_name'][n]

    data = request.json
    del data['id']
    c.update(data)

    for n in c['names']:
        g.data['canonicals_by_name'][n] = c

    return jsonify(c)

@app.route('/names', methods=['GET'])
def get_names():
    return jsonify(g.data['names'])

@app.route('/names', methods=['PUT'])
def update_names():
    g.data['names'] = request.data.splitlines()
    return jsonify(g.data['names'])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(port=port)
