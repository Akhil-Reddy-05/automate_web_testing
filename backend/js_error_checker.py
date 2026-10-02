"""Collect page JavaScript console errors and uncaught exceptions."""
def attach_error_capture(page, errors):
    page.on("pageerror", lambda exc: errors.append(str(exc)[:300]))
    page.on("console", lambda msg: errors.append(msg.text[:300]) if msg.type == "error" else None)
