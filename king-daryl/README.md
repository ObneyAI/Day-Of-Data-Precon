# M3 — Vibe Coding 101: the "King Daryl" warm-up

**Goal:** teach total beginners the vibe-coding *loop* — describe intent → let the AI build → **run → break → fix** —
on something silly and low-stakes, so the skill is in their hands before M5 (the real MCP build). Mirrors the June lesson.

**Time:** ~15 min teach + ~30 min build. **Tool:** Claude Code. **No prior coding needed.**

## What Attendees build
A tiny **browser extension** that rewrites every occurrence of the word **"Daryl"** into **"King Daryl"** on any web
page. It's visible, instant, and harmless — the point is the *process*, not the product.

## Instructor flow
1. **Frame it (say this):** *"You will not write code. You'll describe what you want, read what the AI gives you, run it,
   and when it breaks — because it will — you'll tell the AI what happened and it'll fix it. That loop is the whole job."*
2. **Open Claude Code** in a fresh folder (`claude`). Have everyone type, in their own words:
   > *"Build a Chrome browser extension that replaces every 'Daryl' on the page with 'King Daryl'. Give me the files and tell me how to load it."*
3. **Load it** (Chrome → Extensions → Developer mode → Load unpacked → pick the folder). Visit any page with the word on it
   (or your slides). Watch it work.
4. **Break it on purpose** — this is the lesson. Suggest one:
   - *"Make it also turn 'SQL' into 'SQL 👑' "* → often works, sometimes breaks the matcher → fix by describing the error.
   - Ask for something slightly wrong, paste the console error back to Claude, watch it repair.
5. **Name the loop:** Express → Run → Observe (it broke) → Adapt. *(Daryl's AI Engineering Loop — the same muscle they'll
   use in M5.)*

## Talking points
- "Reading the output is the skill, not memorizing syntax."
- "Breaking things is data, not failure — every break tells the AI (and you) what to fix."
- "Small steps: one change, run, look. Not ten changes at once."

## Walk-around checklist
- Everyone got *something* loaded and saw at least one "Daryl → King Daryl" swap.
- Everyone experienced at least one break-and-fix cycle (that's the takeaway, more than a polished extension).
- No one is stuck silently — pair them up if Claude Code sign-in lagged.

## Reference (only if an Attendee is fully stuck)
A minimal working version is just two files — a `manifest.json` (Manifest V3, a content script on `<all_urls>`) and a
`content.js` that walks text nodes and replaces `/\bDaryl\b/g` with `King Daryl`. Let Claude generate it; don't hand it
out unless needed (the struggle-then-fix *is* the lesson).
