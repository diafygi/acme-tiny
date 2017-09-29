import os, re, hmac
from wsgiref.simple_server import make_server

KEY_AUTHORIZATION = {"uri": "/not_set", "data": ""}
TRAVIS_SESSION = os.getenv("TRAVIS_SESSION", "not_yet_set")

def app(req, resp):
    if req['REQUEST_METHOD'] == "POST":
        if hmac.compare_digest(req['QUERY_STRING'], TRAVIS_SESSION):
            body_len = min(int(req['CONTENT_LENGTH']), 90)
            body = req['wsgi.input'].read(body_len).decode("utf8")
            body = re.sub(r"[^A-Za-z0-9_\-\.]", "_", body)
            KEY_AUTHORIZATION['uri'] = "/{0}".format(body.split(".", 1)[0])
            KEY_AUTHORIZATION['data'] = body
            resp('201 Created', [])
            return ["".encode("utf8")]
        else:
            resp("403 Forbidden", [])
            return ["403 Forbidden".encode("utf8")]
    else:
        if hmac.compare_digest(req['PATH_INFO'], KEY_AUTHORIZATION['uri']):
            resp('200 OK', [])
            return [KEY_AUTHORIZATION['data'].encode("utf8")]
        else:
            resp("404 Not Found", [])
            return ["404 Not Found".encode("utf8")]

make_server("localhost", 8888, app).serve_forever()
