from bottle import Bottle, get, post, run, request, HTTPResponse
from bottle import TEMPLATE_PATH, jinja2_template
import datetime
import json


class Message(object):
    """Bottleのjinja2テンプレートへ値を引き渡すためのクラス"""
    def __init__(self, title, handle, message):
        self.title = title
        self.handle = handle
        self.message = message
        self.created_at = datetime.datetime.now()

# テストコードで扱えるよう、変数appにインスタンスをセット
app = Bottle()

@app.get('/')
def get_top():
    return jinja2_template('bbs', message=None)

@app.post('/')
def post_top():
    print(request.forms.get('handle'))
    message = Message(
        # get()だと文字化けするため、getunicode()を使う
        title=request.forms.getunicode('title'),
        handle=request.forms.getunicode('handle'),
        message=request.forms.getunicode('message'),
    )
    return jinja2_template('bbs', message=message)

@app.post('/json')
def post_json():
    json_body = request.json
    print(json_body)

    body = json.dumps({
        'title': json_body.get('title'),
        'message': json_body.get('message'),
        'remarks': '備考'})
    r = HTTPResponse(status=200, body=body)
    r.set_header('Content-Type', 'application/json')
    return r


if __name__ == "__main__":
    run(app, host="localhost", port=8080, debug=True, reloader=True)