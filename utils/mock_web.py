from flask import Flask
import json

app = Flask(__name__)


@app.route('/judge/api/data')
def get_data():
    data = {
        'input': "1 2\n3 4\n",
        'output': "3\n7\n"
    }

    return json.dumps(data)


@app.route('/judge/api/report')
def report():
    return 'got'


if __name__ == '__main__':
    app.run()
