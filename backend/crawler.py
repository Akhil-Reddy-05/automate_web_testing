"""Bounded same-origin, read-only website quality crawl using Playwright."""
import asyncio
import requests
from urllib.parse import urljoin, urlparse, urldefrag
from playwright.async_api import async_playwright
from .image_checker import inspect_images
from .js_error_checker import attach_error_capture

MAX_PAGES=20
def origin_of(url):
    p=urlparse(url); return f"{p.scheme}://{p.netloc}"
def normalize(url):
    p=urlparse(urldefrag(url)[0]); return p._replace(query="",fragment="").geturl().rstrip("/") or url

async def scan_site(start_url, progress):
    origin=origin_of(start_url); queue=[normalize(start_url)]; seen=set(); pages=[]; links=set(); forms=[]; images=[]; issues=[]; js_errors=[]; limitations=[]
    # Record TLS validation failures, then allow Chromium to inspect the site.
    # This is diagnostic only; the certificate issue remains a reported finding.
    try:
        probe=requests.get(start_url, timeout=8, stream=True, headers={"User-Agent":"SafeWebsiteQA/1.0"})
        probe.close()
    except requests.exceptions.SSLError as exc:
        issues.append(issue(start_url,"HTTPS certificate validation failed","Security","High",str(exc)[:280],"Renew or correctly configure the TLS certificate and certificate chain."))
    except requests.RequestException:
        pass
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True)
        # Continue read-only QA even when TLS is broken; the failed validation is
        # separately recorded above so it is not hidden from the report.
        context=await browser.new_context(ignore_https_errors=True)
        while queue and len(seen)<MAX_PAGES:
            url=queue.pop(0)
            if url in seen: continue
            seen.add(url); progress("Crawling pages...", min(70,10+int(60*len(seen)/MAX_PAGES)))
            page=await context.new_page(); attach_error_capture(page,js_errors)
            try:
                response=await page.goto(url,wait_until="domcontentloaded",timeout=20000)
                if response and response.status>=400:
                    issues.append(issue(url,"Page returned HTTP error","HTTP", "High" if response.status>=500 else "Medium",f"HTTP {response.status}","Check the route and server response."))
                pages.append(url)
                title=await page.title()
                if not title.strip(): issues.append(issue(url,"Page is missing a title","Metadata","Medium","document.title is empty","Add a concise, descriptive <title>."))
                meta=await page.locator('meta[name="description"]').count()
                if not meta: issues.append(issue(url,"Page is missing a meta description","Metadata","Low","No meta[name=description] element","Add a page-specific meta description."))
                for a in await page.locator("a[href]").evaluate_all("els=>els.map(a=>a.href)"):
                    if urlparse(a).scheme in ("http","https"):
                        links.add(a)
                        if origin_of(a)==origin and len(seen)+len(queue)<MAX_PAGES and normalize(a) not in seen and normalize(a) not in queue: queue.append(normalize(a))
                for img in await inspect_images(page):
                    images.append(img)
                    if not img.get("alt") and img.get("alt") is None: issues.append(issue(url,"Image is missing alt text","Accessibility","Low",img.get("src","(source unavailable)"),"Add alt text, or alt=\"\" for decorative images."))
                    if not img.get("loaded"): issues.append(issue(url,"Image failed to load","Images","Low",img.get("src","(source unavailable)"),"Verify the image URL and that the asset is served."))
                fs=await page.locator("form").evaluate_all("forms=>forms.map(f=>({page:location.href,action:f.getAttribute('action'),fields:[...f.querySelectorAll('input,textarea,select')].map(x=>({type:x.type||x.tagName.toLowerCase(),name:x.name,label:!!(x.labels&&x.labels.length),ariaLabel:x.getAttribute('aria-label')}))}))")
                forms.extend(fs)
                await page.close()
            except Exception as exc:
                limitations.append(f"Could not inspect {url}: {str(exc)[:120]}")
                if url==start_url: raise
                await page.close()
        await browser.close()
    for error in js_errors:
        issues.append(issue(start_url,"JavaScript console or runtime error","JavaScript","High",error,"Inspect the browser console and fix the reported script error."))
    return {"pages":pages,"links":sorted(links),"forms":forms,"images":images,"issues":issues,"jsErrors":js_errors,"limitations":limitations,"capped":bool(queue)}

def issue(url,description,category,severity,evidence,fix):
    return {"url":url,"description":description,"category":category,"severity":severity,"evidence":str(evidence)[:300],"fix":fix}
def scan(start_url,progress): return asyncio.run(scan_site(start_url,progress))
