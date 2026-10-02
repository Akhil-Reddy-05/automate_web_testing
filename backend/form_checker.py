"""Basic, non-submitting form checks."""
def inspect_forms(forms):
    issues=[]
    for form in forms:
        problems=[]
        if not form.get("action"): problems.append("Form has no explicit action (submission target is implicit).")
        for field in form.get("fields",[]):
            if field.get("type") in ("text","email","password","search","url") and not field.get("label") and not field.get("ariaLabel"):
                problems.append(f"Input '{field.get('name') or field.get('type')}' has no accessible label.")
        if problems: issues.append({"url":form["page"],"description":"; ".join(problems),"category":"Form","severity":"Medium","evidence":f"Form on {form['page']}","fix":"Add a clear accessible label for each input and set an explicit form action."})
    return issues
