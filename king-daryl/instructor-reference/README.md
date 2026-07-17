# King Daryl — instructor reference build 👑

This is Daryl's polished version — the "here's the one I made" reveal after the M3 exercise. Now that you've
built your own, here's how this fancier one works and how to run it.

## What it does (a notch fancier than the beginners' version)
Crowns every standalone **Daryl → 👑 King Daryl** on any page, and unlike a basic one-shot swap it also:
- keeps working when a page **loads content later** (dynamic sites / single-page apps),
- **never double-crowns** an existing "King Daryl",
- leaves **form fields, code blocks, and editable areas** alone,
- logs a **royal tally** to the console.

## Load it (Chrome or Edge)
1. Go to **`chrome://extensions`** (or `edge://extensions`).
2. Turn on **Developer mode** (top-right toggle).
3. Click **Load unpacked** → select this folder:
   `~/Desktop/Code/Day-Of-Data-Precon/king-daryl/instructor-reference`
4. The extension **King Daryl (instructor reference)** appears and is on.

> **Tip for the day:** keep it **toggled OFF** during earlier modules (so your screen isn't full of crowns), then
> flip it **ON** right before the reveal — or load it in a separate Chrome window. You toggle it on/off from
> `chrome://extensions` (the switch on its card).

## Test it (30 seconds)
1. Open the included test page — drag **`test.html`** into a browser tab (or `File → Open`).
2. You should see **"Welcome, 👑 King Daryl"** and the crowns throughout — but:
   - **"Darylize"** stays unchanged (not a whole word),
   - **"King Daryl"** stays single-crowned,
   - the **input field** keeps a plain "Daryl" if you type it.
3. Click **"Add a line that says 'Daryl'"** → the new line appears **already crowned** (that's the live-update flair).
4. Open the console (**⌥⌘J**) to see: `👑 King Daryl reigns — crowned N mention(s) on load.`

## Show students YOUR version (the reveal, ~1 min after the exercise)
1. Students finish their own extension. Ask a few "what did yours do?"
2. 🎙️ *"Here's one I made earlier — same idea, a little fancier."*
3. Toggle this extension **ON** (or Load unpacked), then **refresh** the test page — or refresh your slides / any page
   with "Daryl" on it. Crowns everywhere.
4. Click the **Add** button on the test page to show it crowns **new** content live: 🎙️ *"and it keeps up as the page
   changes — that's the kind of polish you get by describing one more thing to the AI."*
5. Point them back to the loop: *"I didn't write this by hand either — I described each of those touches and read
   what came back."*

*(To change the flair, edit `content.js` — e.g. the `REPLACEMENT` string — then hit the **reload** ↻ icon on the
extension card in `chrome://extensions`.)*
