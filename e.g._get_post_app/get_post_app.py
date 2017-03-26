import datetime
import cgi
import io
from jinja2 import Environment, FileSystemLoader

# WSGIアプリとして、以下より移植
# https://github.com/thinkAmi-sandbox/wsgi_application-sample

class Message(object):
    def __init__(self, title, handle, message):
        self.title = title
        self.handle = handle
        self.message = message
        self.created_at = datetime.datetime.now()


class MyWSGIApplication(object):
    def __init__(self):
        self.messages = []

    # https://knzm.readthedocs.io/en/latest/pep-3333-ja.html#the-application-framework-side
    def __call__(self, environ, start_response):
        if environ['REQUEST_METHOD'].upper() == "POST":
            # POSTヘッダとボディが一緒に格納されている
            # cgi.FieldStorageで使うために、
            # 　・リクエストをデコード
            # 　・ヘッダとボディを分離
            # 　・ボディをエンコード
            # 　・ボディをio.BytesIOに渡す
            # を行う
            decoded = environ['wsgi.input'].read().decode('utf-8')
            header_body_list = decoded.split('\r\n')
            body = header_body_list[-1]
            encoded_body = body.encode('utf-8')

            # http://docs.python.jp/3/library/io.html#io.BytesIO
            with io.BytesIO(encoded_body) as bytes_body:
                fs = cgi.FieldStorage(
                    fp=bytes_body,
                    environ=environ,
                    keep_blank_values=True,
                )
            # 念のためFieldStorageの内容を確認
            print('-'*20 + '\nFieldStorage:{}\n'.format(fs) + '-'*20)

            self.messages.append(Message(
                title=fs['title'].value,
                handle=fs['handle'].value,
                message=fs['message'].value,
            ))

            # リダイレクトはLocationヘッダをつけてあげれば、ブラウザがうまいことやってくれる
            location = "{scheme}://{name}:{port}/".format(
                scheme = environ['wsgi.url_scheme'],
                name = environ['SERVER_NAME'],
                port = environ['SERVER_PORT'],
            )
            start_response(
                '301 Moved Permanently',
                [('Location', location), ('Content-Type', 'text/plain')])
            # 適当な値を返しておく
            return [b'1']

        else:
            jinja2_env = Environment(loader=FileSystemLoader('./templates', encoding='utf8'))
            template = jinja2_env.get_template('bbs.html')
            html = template.render({'messages': self.messages})
            start_response('200 OK', [('Content-Type', 'text/html')])
            return [html.encode('utf-8')]


app = MyWSGIApplication()