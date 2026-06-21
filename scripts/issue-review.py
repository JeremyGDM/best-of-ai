#!/usr/bin/env python3
"""
Rule-based tool submission reviewer.
- Parses issue body for required fields
- Validates each field
- If valid: creates the .md file and opens a PR, closes issue
- If invalid: posts a comment listing problems and closes issue
"""

import os
import re
import json
import datetime
import urllib.request
import urllib.error
import yaml

# ── env ──────────────────────────────────────────────────────────────────────
GITHUB_TOKEN  = os.environ["GITHUB_TOKEN"]
REPO          = os.environ["REPO"]                  # owner/repo
ISSUE_NUMBER  = os.environ["ISSUE_NUMBER"]
ISSUE_TITLE   = os.environ.get("ISSUE_TITLE", "")
ISSUE_BODY    = os.environ.get("ISSUE_BODY", "")
ISSUE_AUTHOR  = os.environ.get("ISSUE_AUTHOR", "ghost")

VALID_PRICES   = {"free", "freemium", "paid"}
CATEGORIES_FILE = "data/categories.yaml"

# ── GitHub API helpers ────────────────────────────────────────────────────────

def gh(method, path, body=None):
    url = f"https://api.github.com/repos/{REPO}/{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"GitHub API error {e.code}: {e.read().decode()}")
        raise


def post_comment(body):
    gh("POST", f"issues/{ISSUE_NUMBER}/comments", {"body": body})


def close_issue():
    gh("PATCH", f"issues/{ISSUE_NUMBER}", {"state": "closed"})


def add_label(label):
    try:
        gh("POST", f"issues/{ISSUE_NUMBER}/labels", {"labels": [label]})
    except Exception:
        pass  # label may not exist yet, non-fatal


def get_main_sha():
    ref = gh("GET", "git/ref/heads/main")
    return ref["object"]["sha"]


def create_branch(branch_name, sha):
    gh("POST", "git/refs", {"ref": f"refs/heads/{branch_name}", "sha": sha})


def create_file_on_branch(branch, path, content, message):
    import base64
    gh("PUT", f"contents/{path}", {
        "message": message,
        "content": base64.b64encode(content.encode()).decode(),
        "branch": branch,
    })


def open_pr(title, body, head, base="main"):
    return gh("POST", "pulls", {
        "title": title,
        "body": body,
        "head": head,
        "base": base,
    })


# ── field parsing ─────────────────────────────────────────────────────────────

def extract_field(body, *labels):
    """
    Extract the value following any of the given bold labels in the issue body.
    Handles:
      **Name:** value on same line
      **Name:**
      value on next line
    """
    for label in labels:
        # Same-line: **Label:** value
        m = re.search(
            rf"\*\*{re.escape(label)}[:\s]*\*\*[:\s]*(.+)",
            body, re.IGNORECASE
        )
        if m:
            val = m.group(1).strip()
            if val:
                return val

        # Next-line: **Label:**\nvalue
        m = re.search(
            rf"\*\*{re.escape(label)}[:\s]*\*\*\s*\n+([^\n*#]+)",
            body, re.IGNORECASE
        )
        if m:
            val = m.group(1).strip()
            if val:
                return val

    return ""


def parse_issue(body):
    return {
        "name":        extract_field(body, "Name", "Tool Name"),
        "website":     extract_field(body, "Website URL", "Website", "URL"),
        "category":    extract_field(body, "Category"),
        "price":       extract_field(body, "Pricing", "Price"),
        "description": extract_field(body, "Short description", "Description"),
    }


# ── validation ────────────────────────────────────────────────────────────────

def load_valid_categories():
    try:
        with open(CATEGORIES_FILE) as f:
            cats = yaml.safe_load(f)
        return {c["slug"].lower() for c in cats if "slug" in c}
    except Exception as e:
        print(f"Warning: could not load categories: {e}")
        return set()


def slugify(name):
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def validate(fields, valid_categories):
    errors = []

    if not fields["name"]:
        errors.append("❌ **Name** is missing.")

    website = fields["website"]
    if not website:
        errors.append("❌ **Website URL** is missing.")
    elif not re.match(r"https?://", website):
        errors.append(f"❌ **Website URL** `{website}` must start with `https://`.")

    price_raw = fields["price"]
    price_clean = re.sub(r"\s*\(.*?\)", "", price_raw).strip().lower()
    if not price_raw:
        errors.append("❌ **Pricing** is missing. Use one of: `Free`, `Freemium`, `Paid`.")
    elif price_clean not in VALID_PRICES:
        errors.append(
            f"❌ **Pricing** `{price_raw}` is not valid. Use one of: `Free`, `Freemium`, `Paid`."
        )

    desc = fields["description"]
    if not desc:
        errors.append("❌ **Short description** is missing.")
    elif len(desc) < 20:
        errors.append("❌ **Short description** is too short (minimum 20 characters).")
    elif len(desc) > 300:
        errors.append("❌ **Short description** is too long (maximum 300 characters).")

    category_raw = fields["category"]
    if not category_raw:
        errors.append("❌ **Category** is missing.")
    else:
        # Try to match against known slugs (the submitter may write a human name)
        cat_slug = slugify(category_raw.split("(")[0].strip())
        if valid_categories and cat_slug not in valid_categories:
            cat_list = ", ".join(f"`{c}`" for c in sorted(valid_categories))
            errors.append(
                f"❌ **Category** `{category_raw}` doesn't match any known category slug.\n"
                f"   Available: {cat_list}"
            )

    return errors


# ── .md content builder ───────────────────────────────────────────────────────

def build_md(fields):
    name    = fields["name"]
    slug    = slugify(name)
    website = fields["website"].rstrip("/")
    price_raw = fields["price"]
    price   = re.sub(r"\s*\(.*?\)", "", price_raw).strip().capitalize()
    # Normalize to title-case recognised values
    price_map = {"Free": "Free", "Freemium": "Freemium", "Paid": "Paid"}
    price = price_map.get(price, price)

    category_raw = fields["category"].split("(")[0].strip()
    category_slug = slugify(category_raw)
    category_name = category_raw.title()

    desc = fields["description"].strip()
    if not desc.endswith("."):
        desc += "."

    today = datetime.date.today().isoformat()

    return slug, f"""---
title: '{name}'
name: '{name}'
slug: '{slug}'
description: '{desc}'
website: '{website}'
logo_url: ''
category: '{category_slug}'
category_name: '{category_name}'
price: '{price}'
featured: false
date: '{today}'
---
"""


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"Processing issue #{ISSUE_NUMBER}: {ISSUE_TITLE}")

    fields = parse_issue(ISSUE_BODY)
    print("Parsed fields:", fields)

    valid_categories = load_valid_categories()
    errors = validate(fields, valid_categories)

    if errors:
        # ── FAILED: comment + close ──────────────────────────────────────────
        error_list = "\n".join(errors)
        comment = f"""## ❌ Tool submission needs corrections

Hi @{ISSUE_AUTHOR}, thanks for submitting! Your submission has **{len(errors)} issue(s)** that need to be fixed before it can be added:

{error_list}

---

Please open a **new issue** with the corrected information using the [submit tool template]({f"https://github.com/{REPO}/issues/new?template=submit-tool.md"}).

> 🤖 *This review was performed automatically.*"""

        post_comment(comment)
        add_label("invalid")
        close_issue()
        print("Issue closed with validation errors.")

    else:
        # ── PASSED: create PR ────────────────────────────────────────────────
        slug, md_content = build_md(fields)
        tool_name = fields["name"]
        branch_name = f"add-tool-{slug}-issue-{ISSUE_NUMBER}"
        file_path   = f"content/tools/{slug}.md"

        # Create branch
        sha = get_main_sha()
        create_branch(branch_name, sha)
        print(f"Created branch: {branch_name}")

        # Commit the file
        create_file_on_branch(
            branch=branch_name,
            path=file_path,
            content=md_content,
            message=f"feat: add {tool_name} (closes #{ISSUE_NUMBER})",
        )
        print(f"Committed: {file_path}")

        # Open PR
        pr_body = f"""## Add tool: {tool_name}

Automatically generated from issue #{ISSUE_NUMBER} submitted by @{ISSUE_AUTHOR}.

### Tool details
| Field | Value |
|-------|-------|
| Name | {fields['name']} |
| Website | {fields['website']} |
| Category | {fields['category']} |
| Price | {fields['price']} |
| Description | {fields['description']} |

---
> 🤖 *This PR was created automatically after passing rule-based validation. Please review before merging.*

Closes #{ISSUE_NUMBER}"""

        pr = open_pr(
            title=f"Add tool: {tool_name}",
            body=pr_body,
            head=branch_name,
        )
        pr_url = pr.get("html_url", "")
        print(f"PR opened: {pr_url}")

        # Comment on issue
        comment = f"""## ✅ Submission validated — PR created!

Hi @{ISSUE_AUTHOR}, your submission passed all checks. A pull request has been opened automatically:

👉 **{pr_url}**

The maintainer will review and merge it shortly. This issue will be closed once the PR is merged.

> 🤖 *This review was performed automatically.*"""

        post_comment(comment)
        add_label("automated-pr")
        close_issue()
        print("Done.")


if __name__ == "__main__":
    main()