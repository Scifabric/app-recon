import os
import json
import shelve
from flask import Flask, Response
from flask import g, abort, request, jsonify

DEBUG = True
DATAFILE = os.path.join(os.path.dirname(__file__), 'backend_data')

app = Flask(__name__)
app.config.from_object(__name__)

# We define our own jsonify rather than using flask.jsonify because we wish
# to jsonify arbitrary objects (e.g. index returns a list) rather than kwargs.
def jsonify(obj, *args, **kwargs):
    res = json.dumps(obj, indent=None if request.is_xhr else 2)
    return Response(res, mimetype='application/json', *args, **kwargs)

@app.before_request
def before_request():
    g.data = shelve.open(DATAFILE, protocol=2)
    g.canonicals =         g.data.get('canonicals', {})
    g.canonicals_by_name = g.data.get('canonicals_by_name', {})
    g.names =              g.data.get('names', [])
    g.next_id =            g.data.get('next_id', 1)

@app.teardown_request
def teardown_request(response):
    for k in ['canonicals', 'canonicals_by_name', 'names', 'next_id']:
        g.data[k] = getattr(g, k)
    g.data.close()

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
    ret = g.next_id
    g.next_id += 1
    return ret

@app.route('/', methods=['GET'])
def index():
    return jsonify(g.canonicals)

@app.route('/canonical', methods=['GET'])
def get_canonical():
    name = request.args['name']

    if name not in g.canonicals_by_name:
        id_ = get_id()
        g.canonicals[id_] = {'id': id_, 'names': [name], 'name': name}
        g.canonicals_by_name[name] = id_
    else:
        id_ = g.canonicals_by_name[name]

    return jsonify(g.canonicals[id_])

@app.route('/canonical/<id>', methods=['GET'])
def read_canonical(id):
    try:
        c = g.canonicals[int(id)]
    except KeyError:
        abort(404)
    else:
        return jsonify(c)

@app.route('/canonical/<id>', methods=['PUT'])
def update_canonical(id):
    try:
        c = g.canonicals[int(id)]
    except KeyError:
        abort(404)

    for n in c['names']:
        del g.canonicals_by_name[n]

    data = request.json
    del data['id']
    c.update(data)

    for n in c['names']:
        g.canonicals_by_name[n] = c['id']

    return jsonify(c)

@app.route('/names', methods=['GET'])
def get_names():
    return jsonify(g.names)

@app.route('/names', methods=['PUT'])
def update_names():
    g.names = request.data.splitlines()
    return jsonify(g.names)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(port=port)
