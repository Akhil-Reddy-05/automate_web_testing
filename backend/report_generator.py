"""Build the terminal-style human-readable report."""
def generate_report(site, stats, summary, issues):
    lines=["================================","WEBSITE TEST REPORT","===================","",f"Website:\n{site}","",f"Pages Tested: {stats['pagesTested']}",f"Links Tested: {stats['linksTested']}",f"Forms Tested: {stats['formsTested']}",f"Images Tested: {stats['imagesTested']}","", "---", "", "## BUG SUMMARY", ""]
    for sev in ("Critical","High","Medium","Low"): lines.append(f"{sev:<8}: {sum(i['severity']==sev for i in issues)}")
    lines += ["", "---", "", "## DETECTED ISSUES", ""]
    if not issues: lines.append("No issues detected.")
    for n,item in enumerate(issues,1): lines += [f"{n}. {item['description']}",f"   Page: {item['url']}",f"   Category: {item['category']}",f"   Severity: {item['severity']}",f"   Evidence: {item['evidence']}",f"   Recommended Fix: {item['fix']}",""]
    lines += ["---", "", "## AI ANALYSIS", "", summary["summary"], summary["impact"], summary["suggestions"], "", "================================"]
    return "\n".join(lines)
