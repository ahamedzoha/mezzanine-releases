#!/usr/bin/env python3
"""Publishes a release staged by Mezzanine's private repo (Scripts/publish-release.sh).

staging/ holds Mezzanine-<version>.dmg, release.json (version, build, EdDSA signature, length,
notes as HTML) and notes.md. This creates the GitHub Release with the DMG, adds the version to
releases.json (the last ten), writes appcast.xml from it, and replaces the branch's history with
one commit without staging/, so the repository never accumulates disk images.
"""
import json, os, subprocess, sys
from pathlib import Path

REPO = os.environ.get("GITHUB_REPOSITORY", "ahamedzoha/mezzanine-releases")
OWNER_NAME, OWNER_EMAIL = "ahamedzoha", "13367662+ahamedzoha@users.noreply.github.com"
KEEP = 10

NOTES_STYLE = """<style>
:root { color-scheme: light dark; }
body { font: 13px/1.45 -apple-system, system-ui, sans-serif; margin: 10px 14px; }
ul { padding-left: 18px; margin: 4px 0; } li { margin: 4px 0; }
h3 { font-size: 13px; font-weight: 600; margin: 12px 0 4px; }
code { font: 12px ui-monospace, monospace; }
</style>"""


def run(*args, check=True):
    return subprocess.run(args, check=check, text=True, capture_output=True)


def appcast(releases):
    items = []
    for r in releases:
        notes = (NOTES_STYLE + r["notesHTML"]).replace("]]>", "]]&gt;")
        url = f"https://github.com/{REPO}/releases/download/v{r['version']}/{r['dmg']}"
        items.append(f"""    <item>
      <title>Mezzanine {r['version']}</title>
      <pubDate>{r['pubDate']}</pubDate>
      <sparkle:version>{r['build']}</sparkle:version>
      <sparkle:shortVersionString>{r['version']}</sparkle:shortVersionString>
      <sparkle:minimumSystemVersion>{r['minimumSystemVersion']}</sparkle:minimumSystemVersion>
      <description><![CDATA[{notes}]]></description>
      <enclosure url="{url}" length="{r['length']}" type="application/octet-stream" sparkle:edSignature="{r['edSignature']}"/>
    </item>""")
    return f"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:sparkle="http://www.andymatuschak.org/xml-namespaces/sparkle">
  <channel>
    <title>Mezzanine</title>
    <link>https://github.com/{REPO}</link>
    <description>Updates for Mezzanine.</description>
    <language>en</language>
{chr(10).join(items)}
  </channel>
</rss>
"""


def main():
    staged = Path("staging/release.json")
    if not staged.exists():
        print("Nothing staged.")
        return
    release = json.loads(staged.read_text())
    version, dmg = release["version"], Path("staging") / release["dmg"]
    if not dmg.exists() or dmg.stat().st_size != release["length"]:
        sys.exit(f"{dmg} is missing or not the size release.json records.")

    tag = f"v{version}"
    if run("gh", "release", "view", tag, "--repo", REPO, check=False).returncode != 0:
        notes = Path("staging/notes.md").read_text().strip()
        body = f"{notes}\n\nRequires macOS 26 on Apple silicon. Installed copies update themselves."
        run("gh", "release", "create", tag, str(dmg), "--repo", REPO, "--title", f"Mezzanine {version}",
            "--notes", body, "--latest")
        print(f"Created release {tag}.")
    else:
        print(f"Release {tag} exists; refreshing the feed only.")

    history = json.loads(Path("releases.json").read_text())
    history = [r for r in history if r["version"] != version]
    history.insert(0, release)
    history = history[:KEEP]
    Path("releases.json").write_text(json.dumps(history, indent=2) + "\n")
    Path("appcast.xml").write_text(appcast(history))

    # One commit, no staging/: the disk image now lives in the release, not in git.
    run("git", "rm", "-r", "-q", "--cached", "staging")
    for p in Path("staging").iterdir():
        p.unlink()
    Path("staging").rmdir()
    run("git", "checkout", "-q", "--orphan", "published")
    run("git", "add", "-A")
    run("git", "-c", f"user.name={OWNER_NAME}", "-c", f"user.email={OWNER_EMAIL}",
        "commit", "-q", "-m", f"Mezzanine {version}")
    run("git", "push", "-q", "--force", "origin", "published:main")
    print(f"Feed updated for {version}; history reset to one commit.")


if __name__ == "__main__":
    main()
