from webtest import TestApp
import pytest
import get_post_app


class Test_simple_wsgi_app(object):
    def test_get(self):
        """GETのテスト"""
        sut = TestApp(get_post_app.app)
        actual = sut.get('/')

        assert actual.status_code == 200
        assert actual.content_type == 'text/html'
        # bodyは、レスポンスボディをバイト文字列で取得
        assert 'テスト掲示板'.encode('utf-8') in actual.body
        # textは、レスポンスボディをユニコード文字列で取得
        assert 'テスト掲示板' in actual.text


    @pytest.mark.xfail
    def test_print_respose_object(self):
        """レスポンスオブジェクトを表示してみる"""
        sut = TestApp(get_post_app.app)
        actual = sut.get('/')
        print(actual)
        assert False
        """
        Response: 200 OK
        Content-Type: text/html
        <html>
            <head>
                <meta charset="UTF-8">
                <title>���������������������</title>
            </head>
            <body>
                <h1>������������������</h1>
                <form action="/" method="POST">
                    ��������������� <input type="text" name="title" size="60"><br>
                    ������������������ <input type="text" name="handle"><br>
                    <textarea name="message" rows="4" cols="60"></textarea>
                    <input type="submit">
                </form>
                <hr>
            </body>
        </html>
        """


    def test_post(self):
        """直接POSTのテスト"""
        sut = TestApp(get_post_app.app)
        actual = sut.post(
            '/',
            {'title': 'ハム', 'handle': 'スパム', 'message': 'メッセージ'})

        assert actual.status_code == 301
        assert actual.content_type == 'text/plain'
        assert actual.location == 'http://localhost:80/'
        assert actual.body == b'1'
        # redirectの検証には、follow()を使う
        # http://docs.pylonsproject.org/projects/webtest/en/latest/api.html#webtest.response.TestResponse.follow
        redirect_response = actual.follow()
        assert 'ハム' in redirect_response.text
        assert 'スパム さん' in redirect_response.text
        assert 'メッセージ' in redirect_response.text


    def test_form_post(self):
        """GETして、formに入力し、submitボタンを押すテスト"""
        sut = TestApp(get_post_app.app)
        form = sut.get('/').form
        form['title'] = 'ハム'
        form['handle'] = 'スパム'
        form['message'] = 'メッセージ'
        actual = form.submit()

        assert actual.status_code == 301
        assert actual.content_type == 'text/plain'
        assert actual.location == 'http://localhost:80/'
        assert actual.body == b'1'

        redirect_response = actual.follow()
        assert 'ハム' in redirect_response.text
        assert 'スパム さん' in redirect_response.text
        assert 'メッセージ' in redirect_response.text


    @pytest.mark.xfail
    def test_post_with_beautifulsoup(self):
        """BeautifulSoupを使って検証する"""
        sut = TestApp(get_post_app.app)
        response = sut.post(
            '/',
            {'title': 'ハム', 'handle': 'スパム', 'message': 'メッセージ'})
        redirect_respose = response.follow()
        actual = redirect_respose.html

        title = actual.find('span', class_='title')
        # BeautifulSoupのget_text()で出力してみると、文字化けしていた
        print(title.get_text())  #=> ������������

        assert '「ハム」' == actual.find('span', class_='title').get_text()
