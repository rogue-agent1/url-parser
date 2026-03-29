#!/usr/bin/env python3
"""URL parser and builder with query string handling."""
import sys, re
from urllib.parse import quote, unquote

def parse_url(url):
    m = re.match(r'^(?:(?P<scheme>[a-zA-Z][a-zA-Z0-9+.-]*):)?//(?:(?P<user>[^@]+)@)?(?P<host>[^/:?#]+)(?::(?P<port>\d+))?(?P<path>/[^?#]*)?(?:\?(?P<query>[^#]*))?(?:#(?P<fragment>.*))?$', url)
    if not m: return {"raw": url}
    d = {k: v for k, v in m.groupdict().items() if v}
    if "port" in d: d["port"] = int(d["port"])
    if "query" in d: d["params"] = parse_qs(d["query"])
    return d

def parse_qs(qs):
    params = {}
    for pair in qs.split("&"):
        if "=" in pair:
            k, v = pair.split("=", 1); params.setdefault(unquote(k), []).append(unquote(v))
        elif pair: params.setdefault(unquote(pair), []).append("")
    return params

def build_url(scheme="https", host="", port=None, path="/", params=None, fragment=None):
    url = f"{scheme}://{host}"
    if port: url += f":{port}"
    url += path
    if params:
        qs = "&".join(f"{quote(k)}={quote(v)}" for k, vs in params.items() for v in (vs if isinstance(vs, list) else [vs]))
        url += f"?{qs}"
    if fragment: url += f"#{fragment}"
    return url

def is_absolute(url): return bool(re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', url))
def join_url(base, path):
    if is_absolute(path): return path
    parsed = parse_url(base)
    base_path = parsed.get("path", "/").rsplit("/", 1)[0]
    new_path = f"{base_path}/{path}" if not path.startswith("/") else path
    return build_url(parsed.get("scheme", "https"), parsed.get("host", ""), parsed.get("port"), new_path)

def main():
    if len(sys.argv) < 2: print("Usage: url_parser.py <demo|test>"); return
    if sys.argv[1] == "test":
        p = parse_url("https://user:pass@example.com:8080/path?q=hello&x=1#frag")
        assert p["scheme"] == "https"; assert p["host"] == "example.com"
        assert p["port"] == 8080; assert p["path"] == "/path"
        assert p["params"]["q"] == ["hello"]; assert p["fragment"] == "frag"
        u = build_url("https", "example.com", 443, "/api", {"key": "val"})
        assert "example.com:443" in u; assert "key=val" in u
        assert is_absolute("https://x.com"); assert not is_absolute("/path")
        j = join_url("https://example.com/a/b", "c")
        assert j == "https://example.com/a/c"
        j2 = join_url("https://example.com/a/b", "/d")
        assert "/d" in j2
        p2 = parse_url("http://localhost")
        assert p2["host"] == "localhost"
        print("All tests passed!")
    else:
        url = sys.argv[2] if len(sys.argv) > 2 else "https://example.com:8080/path?q=test"
        print(parse_url(url))

if __name__ == "__main__": main()
