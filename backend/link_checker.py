"""Safe, read-only HTTP checks for discovered internal links."""
from urllib.parse import urlparse
import requests

def check_links(urls, origin, timeout=8):
    results=[]
    for url in urls:
        try:
            response=requests.get(url, timeout=timeout, allow_redirects=True,
                                  headers={"User-Agent":"SafeWebsiteQA/1.0"}, stream=True)
            status=response.status_code
            response.close()
            results.append({"url":url,"status":status,"ok":status < 400})
        except requests.RequestException as exc:
            results.append({"url":url,"status":None,"ok":False,"error":str(exc)[:180]})
    return results
