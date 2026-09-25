---
name: raise-pr
description: Stage all local changes, create a git commit whose message starts with the JIRA ID, push a feature branch, and raise a GitHub pull request into the main branch using only plain git (no gh CLI) by generating a prefilled GitHub "compare" link whose description starts with the user story number. Use this skill whenever the user wants to "raise a PR", "open a pull request", "check in my code", "commit and push", "ship this", "send this for review", or otherwise get their current work into main via a PR — even if they only mention one step like committing or pushing, since the end goal is usually a PR.
---

# Raise a PR to main

This skill takes the user's working-tree changes all the way to a GitHub pull request targeting `main`, using only plain `git` commands. The `gh` CLI is not installed, so don't use or suggest it. Plain git can't create a PR by itself, so the last step builds a GitHub "compare" URL with the title and description prefilled. The user opens that link and clicks **Create pull request**.

1. Pre-flight checks
2. Get the JIRA ID and user story number
3. Make sure we're on a feature branch (never commit directly to `main`)
4. Stage everything (`git add -A`)
5. Commit with a message that starts with the JIRA ID
6. Push the branch
7. Build a prefilled PR link against `main`, with the user story number in the description
8. Report the link

Run the steps in order. If any step fails, stop, show the user the error, and explain what to fix rather than trying workarounds that could lose work (no `--force`, no `reset --hard`, no stash-and-drop).

## 1. Pre-flight checks

Run these and stop with a clear message if any fails:

```bash
git rev-parse --is-inside-work-tree   # must be a git repo
git remote get-url origin             # needs an origin remote on github.com
git status --porcelain                # must show changes (otherwise nothing to commit)
```

If `git status --porcelain` is empty, check whether the current branch has unpushed commits (`git log origin/main..HEAD --oneline`). If it does, get the IDs (step 2), then skip to step 6 and just push + open the PR. If it doesn't, tell the user there's nothing to raise.

Also fetch so comparisons against main are accurate:

```bash
git fetch origin main
```

## 2. Get the JIRA ID and user story number

The team's convention needs two references:

- **JIRA ID**: goes at the start of every commit message. Example: `BCNH-3456` (project key, hyphen, number).
- **User story number**: goes at the start of the PR description. Example: `BNHG9876`.

These are two separate references with different formats. Don't assume one from the other, and don't reformat either one (don't add or remove a hyphen, don't change case). Use them exactly as the user or the source gives them.

Find them in this order:

1. **The user's message.** For example: "raise a PR for BCNH-3456, story BNHG9876".
2. **The branch name.** For example, `BCNH-3456-add-to-cart` or `feature/BCNH-3456-...` gives the JIRA ID. Check with `git branch --show-current`.
3. **Earlier commits on this branch.** Check `git log origin/main..HEAD --oneline`. If they already start with a JIRA ID, reuse it.

**Never invent or guess an ID.** A wrong ID links the work to the wrong ticket, which is worse than a missing one. If either ID is still unknown after these checks, ask the user for the missing one(s) in a single short question before committing. If you found an ID in the branch name or earlier commits, mention which one you're using so the user can correct it.

## 3. Ensure a feature branch

A PR can't go from `main` into `main`, and committing directly to `main` bypasses review. Check the current branch:

```bash
git branch --show-current
```

- **On `main` (or detached HEAD):** create a new branch before staging. Name it with the JIRA ID followed by a short kebab-case summary, e.g. `BCNH-3456-add-product-to-cart`. This keeps the ID visible in the branch and lets later runs find it (step 2). Look at the diff first (`git diff`, `git status`) so the name reflects the work. Then `git switch -c <branch-name>`. Uncommitted changes carry over to the new branch automatically.
- **On any other branch:** stay on it.

## 4. Stage all changes

```bash
git add -A
```

Then review what's staged before committing — `git add -A` picks up everything, so this is the safety net:

```bash
git diff --cached --stat
```

Look for things that almost certainly shouldn't be committed: `.env` / secrets files, private keys, credentials, `node_modules/`, build output (`dist/`, `build/`, `target/`), large binaries, OS junk (`.DS_Store`). If you see any, unstage them (`git restore --staged <path>`), tell the user what you excluded and why, and suggest adding them to `.gitignore`. Don't silently commit secrets — once pushed they're hard to take back.

## 5. Commit with the JIRA ID first

Read the staged diff (`git diff --cached`) to understand what actually changed, then write the message in exactly this format:

```
<JIRA-ID> : <short description of the change>
```

Note the spaces on both sides of the colon: `BCNH-3456 : adding product to the cart`. Match this exactly, because teams often have tooling or hooks that parse it.

**Rules for the description:** keep it short (the whole line under about 72 characters), lowercase, with no trailing period. Write it in the team's style, which describes the work in progress, e.g. "adding product to the cart". Say what changed for the user or the system, not which files were touched.

If the changes are big enough to need more explanation, add a blank line and then a short body that explains what changed and why.

If the user gave a message, keep their wording and add the JIRA ID prefix if it's missing. If it already starts with an ID in a slightly different layout (e.g. `BCNH-3456: ...` or `BCNH-3456 - ...`), change it to the `ID : description` layout and tell them you did.

**Examples:**
- Diff adds an "Add to cart" button handler, JIRA `BCNH-3456` → `BCNH-3456 : adding product to the cart`
- Diff fixes a crash when the user profile is empty, JIRA `BCNH-3501` → `BCNH-3501 : fixing crash on empty user profile`
- Diff only updates the README, JIRA `BCNH-3510` → `BCNH-3510 : updating local setup steps in readme`

Commit using a heredoc so the message survives quoting:

```bash
git commit -F - <<'EOF'
BCNH-3456 : adding product to the cart
EOF
```

If a pre-commit hook fails, show the hook output to the user. If it auto-fixed files (formatters often do), re-stage with `git add -A` and commit again once. Don't bypass hooks with `--no-verify` unless the user explicitly asks.

## 6. Push the branch

```bash
git push -u origin HEAD
```

If the push is rejected because the remote branch has diverged, stop and tell the user — don't force-push.

## 7. Build the prefilled PR link

Without `gh`, the PR is raised through GitHub's compare page. A URL of this form opens the "Open a pull request" form with the base set to `main` and the title and body already filled in:

```
https://github.com/<owner>/<repo>/compare/main...<branch>?expand=1&title=<urlencoded>&body=<urlencoded>
```

**Get owner/repo from the remote.** `git remote get-url origin` returns one of these forms:
- `git@github.com:owner/repo.git`
- `https://github.com/owner/repo.git` (the `.git` suffix may be missing)
- `ssh://git@github.com/owner/repo.git`

Strip the prefix and any trailing `.git` to get `owner/repo`. If the host isn't `github.com` (e.g. GitHub Enterprise at `github.mycompany.com`), use that host in the URL instead. If it isn't GitHub at all, tell the user this skill targets GitHub and just report the pushed branch.

**Write the title and body.** Use the commit message line as the title (e.g. `BCNH-3456 : adding product to the cart`). The **description must start with the user story number**, followed by a colon and a one-line summary. Write the body like this:

```
BNHG9876: adding product to the cart

## Summary
<1–3 sentences on what this PR does and why>

## Changes
- <key change>
- <key change>

## Testing
<how it was tested, or "Not yet tested" if unknown — don't invent test results>
```

The first line, `BNHG9876: ...` in the example, is required. Keep it as the first line even when you fill in a PR template. Use the story number exactly as found in step 2.

When the branch has several commits, base the title and body on all of them (`git log origin/main..HEAD --oneline`), not just the latest. If the repo has a PR template (`.github/pull_request_template.md`), put the user story line first and then fill in the template below it.

**Build the URL.** Title and body must be URL-encoded. Branch names containing `/` (like `feature/BCNH-3456-x`) work as-is in the compare path. This one-liner builds the URL; `python3` is usually available, so use it:

```bash
REMOTE=$(git remote get-url origin)
BRANCH=$(git branch --show-current)
python3 - "$REMOTE" "$BRANCH" <<'PY'
import sys, re, urllib.parse
remote, branch = sys.argv[1], sys.argv[2]
m = re.search(r'(?://(?:[^@/]+@)?|^[^@/]+@)([^/:]+)[:/](.+?)(?:\.git)?/?$', remote)
host, repo = m.group(1), m.group(2)
title = """BCNH-3456 : adding product to the cart"""
body = """BNHG9876: adding product to the cart

## Summary
Adds an Add to cart action on the product page.
"""
q = urllib.parse.urlencode({"expand": "1", "title": title, "body": body})
print(f"https://{host}/{repo}/compare/main...{branch}?{q}")
PY
```

Replace the `title` and `body` values with the real ones. If `python3` isn't available, build the URL with `expand=1` and the title only, then show the body (starting with the user story line) for the user to paste into the form. Keep the body short, since very long URLs can get cut off. If the body would be more than about 1,500 characters, leave it out of the URL and show it for the user to paste.

**If a PR already exists** for this branch, the push has already updated it. Plain git can't check for an existing PR, but the compare page shows a "View pull request" link in that case. Mention this so the user isn't surprised.

**Tip:** on the first push of a new branch, GitHub usually prints a "Create a pull request for '<branch>'" link in the `git push` output. That link works too, but it isn't prefilled. The generated link is better.

## 8. Report back

Tell the user, briefly:
- Branch name (and whether you created it)
- The JIRA ID and user story number used, and where each came from (user, branch name, or earlier commits)
- The commit message
- Anything you unstaged/excluded in step 4
- The prefilled PR link, clearly labelled, with a note that one click on **Create pull request** finishes it