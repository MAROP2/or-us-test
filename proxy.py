import http.server, http.client, ssl, sys
TARGET = ("openrouter.ai", 443)
class H(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    def _relay(self):
        body = None
        cl = self.headers.get("Content-Length")
        if cl: body = self.rfile.read(int(cl))
        c = http.client.HTTPSConnection(*TARGET, context=ssl.create_default_context())
        hdrs = {k: v for k, v in self.headers.items() if k.lower() not in ("host", "transfer-encoding")}
        try:
            c.request(self.command, self.path, body=body, headers=hdrs)
            r = c.getresponse()
            self.send_response(r.status)
            for k, v in r.getheaders():
                if k.lower() in ("transfer-encoding", "connection", "keep-alive", "content-length"): continue
                self.send_header(k, v)
            self.send_header("Connection", "close")
            self.end_headers()
            self.close_connection = True
            while True:
                chunk = r.read(8192)
                if not chunk: break
                self.wfile.write(chunk)
                self.wfile.flush()
        except Exception as e:
            sys.stderr.write("relay error: %s\n" % e)
        finally:
            try:
                c.close()
            except Exception:
                pass
H.do_GET = H._relay
H.do_POST = H._relay
H.do_PUT = H._relay
H.do_DELETE = H._relay
H.do_PATCH = H._relay
H.do_HEAD = H._relay
http.server.ThreadingHTTPServer(("127.0.0.1", 8080), H).serve_forever()