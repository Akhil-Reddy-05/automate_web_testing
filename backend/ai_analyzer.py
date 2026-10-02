"""Local evidence-based summaries. No external AI service or invented findings."""
def analyze(site, stats, issues, limitations):
    if not issues:
        lead="No issues were detected by the checks that completed."
    else:
        top=sorted(issues,key=lambda x:{"Critical":0,"High":1,"Medium":2,"Low":3}.get(x["severity"],4))[:3]
        lead=" ".join(f"{i['severity']} {i['category'].lower()} issue: {i['description']}" for i in top)
    pages=sorted({i["url"] for i in issues if i.get("url")})
    impact="These findings may affect reliability, navigation, accessibility, or search previews; impact depends on how visitors use the affected pages."
    actions="Review the evidence below, address the highest severity findings first, then rerun the scan."
    if limitations: actions += " Some checks were not completed: " + "; ".join(limitations[:3]) + "."
    return {"summary":lead,"impact":impact,"pages":pages,"suggestions":actions,"quality":f"Scanned {stats['pagesTested']} page(s); {len(issues)} evidence-backed issue(s) were recorded."}
