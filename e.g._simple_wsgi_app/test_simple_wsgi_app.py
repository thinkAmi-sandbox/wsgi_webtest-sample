from webtest import TestApp
import simple_wsgi_app

class Test_simple_wsgi_app(object):
    def test_get(self):
        sut = TestApp(simple_wsgi_app.application)
        actual = sut.get('/')

        assert actual.status_code == 200
        assert actual.content_type == 'text/plain'
        assert actual.body == b'Hello, world.'

        # テスト時に
        # cannot collect test class 'TestApp' because it has a __init__ constructor
        # と出るが、TestAppはテスト対象外なので、気にしない
        # http://stackoverflow.com/questions/21430900/py-test-skips-test-class-if-constructor-is-defined


