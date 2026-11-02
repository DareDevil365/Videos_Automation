from html.parser import HTMLParser
import ipaddress
import json
import socket
from urllib.error import HTTPError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .core import Held


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl): return None


def public_url(url):
    parsed=urlparse(url)
    if parsed.scheme not in ("http","https") or not parsed.hostname or parsed.username or parsed.password:
        raise Held("unsafe_source","Use a public HTTP(S) source URL without embedded credentials.")
    if parsed.port not in (None,80,443): raise Held("unsafe_source","Source URLs must use normal web ports.")
    try: addresses=socket.getaddrinfo(parsed.hostname,parsed.port or (443 if parsed.scheme=="https" else 80),type=socket.SOCK_STREAM)
    except OSError: raise Held("source_unavailable","Source hostname could not be resolved.",retry_after=600)
    if not addresses or any(not ipaddress.ip_address(row[4][0]).is_global for row in addresses):
        raise Held("unsafe_source","Local/private-network URLs are not permitted as research sources.")
    return url


def fetch(url, maximum=2_000_000, headers=None):
    opener=build_opener(NoRedirect())
    for _ in range(4):
        public_url(url)
        try:
            request=Request(url,headers={"User-Agent":"LocalVideoResearch/0.2 (+source verification)",**(headers or {})})
            with opener.open(request,timeout=20) as response:
                size=response.headers.get("Content-Length")
                if size and int(size)>maximum: raise Held("source_too_large","Source exceeded its download limit.")
                body=response.read(maximum+1)
                if len(body)>maximum: raise Held("source_too_large","Source exceeded its download limit.")
                return body,response.headers.get("Content-Type",""),url
        except HTTPError as exc:
            if exc.code in (301,302,303,307,308) and exc.headers.get("Location"):
                url=urljoin(url,exc.headers["Location"]);headers=None;continue
            if exc.code==429: raise Held("source_rate_limited","Source rate limit reached; retry later.",retry_after=3600)
            raise Held("source_unavailable",f"Source returned HTTP {exc.code}.",retry_after=600 if exc.code>=500 else None)
        except (TimeoutError,OSError): raise Held("source_unavailable","Source request failed; no content was invented.",retry_after=600)
    raise Held("source_redirects","Source redirected too many times.")


class Readable(HTMLParser):
    def __init__(self): super().__init__();self.skip=0;self.parts=[];self.title=[];self.in_title=False
    def handle_starttag(self,tag,attrs):
        if tag in ("script","style","nav","noscript"): self.skip+=1
        if tag=="title": self.in_title=True
    def handle_endtag(self,tag):
        if tag in ("script","style","nav","noscript"): self.skip=max(0,self.skip-1)
        if tag=="title": self.in_title=False
    def handle_data(self,data):
        if self.in_title:self.title.append(data)
        if not self.skip and data.strip():self.parts.append(data.strip())


def page(url):
    body,mime,final=fetch(url)
    if not any(kind in mime for kind in ("text/","json","xml")):
        raise Held("unsupported_source","Research sources must return readable text, HTML, JSON or feeds.")
    text=body.decode("utf-8",errors="replace")
    parser=Readable();parser.feed(text)
    return {"url":final,"title":" ".join(parser.title)[:250] or urlparse(final).hostname,
            "excerpt":"\n".join(parser.parts)[:18000] if "html" in mime else text[:18000]}
