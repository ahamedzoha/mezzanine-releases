# Mezzanine releases

Mezzanine is a personal, native macOS client for Plex. Its source is private; this repository
only hosts the installer disk images and the update feed the app checks.

## Install

1. Download the latest `Mezzanine-x.y.z.dmg` from
   [Releases](https://github.com/ahamedzoha/mezzanine-releases/releases/latest).
2. Open it and drag **Mezzanine** into **Applications**.
3. The app is signed but not notarized, so the first time you open it macOS refuses: open
   **System Settings ▸ Privacy & Security**, scroll to Security and click **Open Anyway** next to
   the note about Mezzanine. You only do this once.

Requires macOS 26 on Apple silicon.

## Updates

Mezzanine checks [`appcast.xml`](appcast.xml) every few hours, downloads new versions in the
background and installs them when you quit (Settings ▸ Updates has the switches). Every update is
signed with Mezzanine's EdDSA key, so the app installs only builds made for it.

This repository's history is rewritten on every release: it only ever holds the feed, the record
of recent releases, and the tools that publish them.
