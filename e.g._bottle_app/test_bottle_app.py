from webtest import TestApp
import pytest
import bottle_app


class Test_bottle_app(object):
    @pytest.mark.xfail
    def test_form_submit(self):
        """GETして、formに入力し、submitボタンを押すテスト"""
        sut = TestApp(bottle_app.app)
        response = sut.get('/')
        form = response.form
        form['title'] = u'ハム'.encode('utf-8').decode('utf-8')
        form['handle'] = b'\xe3\x81\x82' #あ
        form['message'] = 'メッセージ'
        actual = form.submit()

        # https://github.com/Pylons/webtest/issues/150
        print(actual)
        """結果：文字化けしている
        <p>
            <span class="title">「ãã 」</span>&nbsp;&nbsp;
            <span class="handle">ã さん</span>&nbsp;&nbsp
            <span class="created_at">2017-03-26 10:58:14.466710</span>
        </p>
        <p class="message">ã¡ãã»ã¼ã¸</p>
        """

        assert actual.status_code == 200
        assert actual.content_type == 'text/html'

        assert 'ハム' in actual.text
        assert 'スパム さん' in actual.text
        assert 'メッセージ' in actual.text


    @pytest.mark.xfail
    def test_post(self):
        """直接POSTするテスト"""
        sut = TestApp(bottle_app.app)
        actual = sut.post(
            '/',
            {'title': 'ハム', 'handle': 'スパム', 'message': 'メッセージ'},
            content_type='application/x-www-form-urlencoded; charset=UTF-8 ')

        # https://github.com/Pylons/webtest/issues/150
        print(actual.text)
        """結果：文字化けしている
        <p>
            <span class="title">「ãã 」</span>&nbsp;&nbsp;
            <span class="handle">ã さん</span>&nbsp;&nbsp
            <span class="created_at">2017-03-26 10:58:14.466710</span>
        </p>
        <p class="message">ã¡ãã»ã¼ã¸</p>
        """

        assert actual.status_code == 200
        assert actual.content_type == 'text/html'

        assert 'ハム' in actual.text
        assert 'スパム さん' in actual.text
        assert 'メッセージ' in actual.text


    def test_post_json(self):
        """JSONをポストするテスト

        formのsubmitとは異なり、日本語が入っていても大丈夫
        """
        # 直ったっぽい
        # https://github.com/Pylons/webtest/issues/177
        sut = TestApp(bottle_app.app)
        actual = sut.post_json('/json', dict(title='タイトル', message='メッセージ'))

        assert actual.status_code == 200
        assert actual.content_type == 'application/json'

        assert actual.json.get('title') == 'タイトル'
        assert actual.json.get('message') == 'メッセージ'
        assert actual.json.get('remarks') == '備考'