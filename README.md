# AI Website Testing & Bug Detection

A beginner-friendly local dashboard for safe, read-only website quality checks. It crawls up to 20 same-origin pages, checks up to 100 internal links, inspects forms without submitting them, checks images and metadata, and captures browser JavaScript errors. Findings include evidence and suggested fixes. The summary is generated locally from collected findings; no external AI account or API key is needed.

Only scan websites you own or have permission to test. This tool does not submit forms, log in, brute force, exploit, stress test, or run intrusive vulnerability scans. Public address validation helps prevent accidental scans of private network hosts.

## Project structure

```text
ai_web_testing/
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── backend/
│   ├── __init__.py
│   ├── app.py
│   ├── crawler.py
│   ├── link_checker.py
│   ├── form_checker.py
│   ├── image_checker.py
│   ├── js_error_checker.py
│   ├── ai_analyzer.py
│   └── report_generator.py
├── reports/                 # Optional location for saved reports
├── requirements.txt
└── README.md
```

## Install and run

Python 3.10+ is recommended. In the VS Code terminal, from this project directory:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py -m playwright install chromium
py -m backend.app
```

Open http://127.0.0.1:5000. The server binds to localhost. Keep the terminal open while using the app. On Windows PowerShell, if script activation is disabled, run `.venv\Scripts\python.exe -m pip install -r requirements.txt` and `.venv\Scripts\python.exe -m backend.app` instead.

## How the modules work

- `app.py` serves the UI and manages background scan jobs and progress polling. It rejects non-HTTP URLs, embedded credentials, and hosts resolving to non-public IPs.
- `crawler.py` opens pages with headless Chromium, stays on the submitted origin, and limits the crawl to 20 pages. It records titles, descriptions, links, forms, images, and console/runtime errors.
- `link_checker.py` makes read-only HTTP GET requests for up to 100 discovered same-origin links and records HTTP failures.
- `form_checker.py` checks for implicit form targets and unlabeled inputs. It never submits forms.
- `image_checker.py` reads image load state and alt text from the rendered page.
- `js_error_checker.py` captures console errors and uncaught browser exceptions.
- `ai_analyzer.py` produces a local evidence-based explanation from detected findings. It does not invent issues or call a hosted LLM.
- `report_generator.py` formats findings in the terminal-style report.
- `frontend/` provides the responsive dashboard, progress view, severity filters, light/dark theme, report download, JSON and CSV export.

Checks that could not run appear in Scan notes. Form behavior, authenticated pages, and security vulnerabilities are not tested. HTTP checks are basic; sites that block automated browsers or require client-side interactions may yield incomplete results.

## Example report format

Numbers below illustrate formatting only; actual numbers and findings come from each scan.

```text
================================
WEBSITE TEST REPORT
===================

Website:
example.com

Pages Tested: 1
Links Tested: 2
Forms Tested: 0
Images Tested: 0

---

## BUG SUMMARY

Critical : 0
High     : 0
Medium   : 0
Low      : 0

---

## DETECTED ISSUES

No issues detected.

---

## AI ANALYSIS

No issues were detected by the checks that completed.
...
================================
```
