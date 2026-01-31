## Log of pain

I'm not a Python coder.

Following the helpful Usage in [README.md].

```zsh
# What did I do first was it ... python3 venv?

% source .venv/bin/activate
% export FLASK_APP=virtual_metro
% flask run

...
ImportError: cannot import name 'Markup' from 'jinja2' 
```

Google suggests I update Flask.

`pip install --upgrade Flask` updated Flask in ./.venv/lib/python3.10/site-packages (3.1.2).
It has not however updated `requirements.txt` which still seeks 1.0.2.

 - [ ] does one do a `pip freeze > requirements.txt`?

Next try.

```zsh
% export FLASK_APP=virtual_metro
% flask run

Usage: flask run [OPTIONS]
Try 'flask run --help' for help.

Error: While importing 'virtual_metro', an ImportError was raised:

Traceback (most recent call last):
  File "/Users/iain/src/ishepherd/VirtualMetro/.venv/lib/python3.10/site-packages/flask/cli.py", line 245, in locate_app
    __import__(module_name)
  File "/Users/iain/src/ishepherd/VirtualMetro/virtual_metro/__init__.py", line 6, in <module>
    from . import config
ImportError: cannot import name 'config' from partially initialized module 'virtual_metro' (most likely due to a circular import) (/Users/iain/src/ishepherd/VirtualMetro/virtual_metro/__init__.py)
```

Hmmm

 - [ ] look for a minimal example Flask project, see if that works, and adopt its structure.

https://flask.palletsprojects.com/en/stable/quickstart/#a-minimal-application.

has a different variant of starting the app.

```zsh
% flask --app virtual_metro run

Usage: flask run [OPTIONS]
Try 'flask run --help' for help.
```

I seem to always get printed usage instructions even if I've used it exactly as the instructions say.
Anyway let's focus on the ImportError.

```
ImportError: cannot import name 'config' from partially initialized module 'virtual_metro' (most likely due to a circular import) ...
```

`most likely due to a circular import` lol or maybe the file you're importing is not there eh?
I just forgot to create the `config.py` which was in fact called out in the README.
Trying with fake key (from `config.example.py` just for giggles.

```zsh
% cp virtual_metro/config.example.py virtual_metro/config.py
% flask run
% flask run

 * Serving Flask app 'virtual_metro'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit


# I open the web link ...


127.0.0.1 - - [31/Jan/2026 19:51:51] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [31/Jan/2026 19:51:51] "GET /static/template1.svg HTTP/1.1" 200 -
127.0.0.1 - - [31/Jan/2026 19:51:51] "GET /favicon.ico HTTP/1.1" 404 -
[2026-01-31 19:51:51,252] ERROR in app: Exception on /latest [GET]
Traceback (most recent call last):
  File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/urllib/request.py", line 1348, in do_open
    h.request(req.get_method(), req.selector, req.data, headers,
  File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/http/client.py", line 1283, in request
    self._send_request(method, url, body, headers, encode_chunked)
  File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/http/client.py", line 1329, in _send_request
    self.endheaders(body, encode_chunked=encode_chunked)
  File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/http/client.py", line 1278, in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
  File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/http/client.py", line 1038, in _send_output
    self.send(msg)
  File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/http/client.py", line 976, in send
    self.connect()
  File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/http/client.py", line 1455, in connect
    self.sock = self._context.wrap_socket(self.sock,
  File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/ssl.py", line 513, in wrap_socket
    return self.sslsocket_class._create(
  File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/ssl.py", line 1071, in _create
    self.do_handshake()
  File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/ssl.py", line 1342, in do_handshake
    self._sslobj.do_handshake()
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1007)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Users/iain/src/ishepherd/VirtualMetro/.venv/lib/python3.10/site-packages/flask/app.py", line 1511, in wsgi_app
    response = self.full_dispatch_request()
  File "/Users/iain/src/ishepherd/VirtualMetro/.venv/lib/python3.10/site-packages/flask/app.py", line 919, in full_dispatch_request
    rv = self.handle_user_exception(e)
  File "/Users/iain/src/ishepherd/VirtualMetro/.venv/lib/python3.10/site-packages/flask/app.py", line 917, in full_dispatch_request
    rv = self.dispatch_request()
  File "/Users/iain/src/ishepherd/VirtualMetro/.venv/lib/python3.10/site-packages/flask/app.py", line 902, in dispatch_request
    return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)  # type: ignore[no-any-return]
  File "/Users/iain/src/ishepherd/VirtualMetro/virtual_metro/__init__.py", line 189, in latest
    departures = do_request('/v3/departures/route_type/{}/stop/{}'.format(ROUTE_TYPE, flask.request.args['stop_id']), args, cachetime=60)
  File "/Users/iain/src/ishepherd/VirtualMetro/virtual_metro/__init__.py", line 44, in do_request
    raise ex
  File "/Users/iain/src/ishepherd/VirtualMetro/virtual_metro/__init__.py", line 37, in do_request
    resp = urlopen(req)
  File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/urllib/request.py", line 216, in urlopen
    return opener.open(url, data, timeout)
  File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/urllib/request.py", line 519, in open
    response = self._open(req, data)
  File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/urllib/request.py", line 536, in _open
    result = self._call_chain(self.handle_open, protocol, protocol +
  File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/urllib/request.py", line 496, in _call_chain
    result = func(*args)
  File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/urllib/request.py", line 1391, in https_open
    return self.do_open(http.client.HTTPSConnection, req,
  File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/urllib/request.py", line 1351, in do_open
    raise URLError(err)
urllib.error.URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1007)>
127.0.0.1 - - [31/Jan/2026 19:51:51] "GET /latest?stop_id=1099&plat_id=1 HTTP/1.1" 500 -

```

My working assumption is:
It's making an invalid call to https://timetableapi.ptv.vic.gov.au.
For one thing, obviously the API credits I am using (from config.example.py) are not real. Let's try real ones.

No, exactly the same.

 - [ ] Figure out with curl etc a working way to make this call and then replicate it in the Python code.