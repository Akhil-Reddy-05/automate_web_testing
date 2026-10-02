"""Browser-based image checks, including lazy loaded images."""
async def inspect_images(page):
    return await page.locator("img").evaluate_all("els => els.map(i => ({src:i.currentSrc||i.src, alt:i.getAttribute('alt'), loaded:i.complete && i.naturalWidth>0}))")
