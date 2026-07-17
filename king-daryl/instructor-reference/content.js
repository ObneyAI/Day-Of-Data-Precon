// King Daryl — instructor reference (the "fancier" version to reveal AFTER the exercise).
// Beginners typically get a one-shot text swap. This one is a notch nicer:
//   - crowns every standalone "Daryl" -> "👑 King Daryl"
//   - keeps working on pages that load content later (dynamic sites / single-page apps)
//   - never double-crowns an already-"King Daryl"
//   - leaves form fields, code, and editable areas alone
//   - logs a little royal tally to the console

const RE = /(?<!King )\bDaryl\b/g;              // whole word; skip an existing "King Daryl"
const REPLACEMENT = "👑 King Daryl";
const SKIP_TAGS = new Set(["SCRIPT", "STYLE", "TEXTAREA", "INPUT", "NOSCRIPT", "CODE", "PRE"]);
let crowned = 0;

function crownTextNode(node) {
  const text = node.nodeValue;
  if (!text || text.indexOf("Daryl") === -1) return;        // cheap pre-check (no stateful regex)
  const parent = node.parentNode;
  if (!parent || SKIP_TAGS.has(parent.nodeName) || parent.isContentEditable) return;
  const next = text.replace(RE, () => { crowned++; return REPLACEMENT; });
  if (next !== text) node.nodeValue = next;
}

function crownTree(root) {
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  nodes.forEach(crownTextNode);
}

// 1) crown everything already on the page
if (document.body) crownTree(document.body);

// 2) crown anything added later (this is the flair beginners usually skip)
new MutationObserver((mutations) => {
  for (const m of mutations) {
    m.addedNodes.forEach((n) => {
      if (n.nodeType === Node.TEXT_NODE) crownTextNode(n);
      else if (n.nodeType === Node.ELEMENT_NODE) crownTree(n);
    });
  }
}).observe(document.documentElement, { childList: true, subtree: true });

console.log(`%c👑 King Daryl reigns — crowned ${crowned} mention(s) on load.`,
            "color: goldenrod; font-weight: bold; font-size: 13px");
