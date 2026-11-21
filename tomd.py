"""Convertit une transcription de session Claude Code (.jsonl) en Markdown lisible.

Usage :
    python3 tomd.py ~/.claude/projects/-Users-samszo-Sites-thesesSIC/<session>.jsonl conversations.md

Garde les messages de l'utilisateur, les réponses de Claude et un résumé repliable
des actions (commandes, fichiers, navigateur) ; ignore les résultats bruts des outils.
"""
import json, sys, re
src, out = sys.argv[1], sys.argv[2]
lines = [json.loads(l) for l in open(src)]
md = ["# Conversation – thesesSIC", "", "Export de la session Claude Code (messages de l'utilisateur, réponses de Claude et actions effectuées).", ""]
seen = set()
def clean(t):
    t = re.sub(r"<system-reminder>.*?</system-reminder>", "", t, flags=re.S)
    return t.strip()
pending_tools = []
def flush_tools():
    if pending_tools:
        md.append("<details><summary>Actions (%d)</summary>\n" % len(pending_tools))
        md.extend(pending_tools)
        md.append("\n</details>\n")
        pending_tools.clear()
for d in lines:
    if d.get("isSidechain") or d.get("type") not in ("user", "assistant"): continue
    u = d.get("uuid")
    if u in seen: continue
    seen.add(u)
    msg = d.get("message", {}); c = msg.get("content")
    if d["type"] == "user":
        if d.get("origin", {}).get("kind") != "human" and d.get("turnOrigin") != "human": continue
        if isinstance(c, list):
            if any(b.get("type") == "tool_result" for b in c): continue
            c = "\n".join(b.get("text", "") for b in c if b.get("type") == "text")
        c = clean(c or "")
        if not c: continue
        flush_tools()
        md += ["---", "", f"## 🧑 Utilisateur  ", f"<sub>{d.get('timestamp','')[:19].replace('T',' ')}</sub>", "", c, ""]
    else:
        for b in c or []:
            if b.get("type") == "text" and b.get("text","").strip():
                flush_tools()
                md += ["## 🤖 Claude", "", b["text"].strip(), ""]
            elif b.get("type") == "tool_use":
                n = b["name"]; i = b.get("input", {})
                if n.startswith("mcp__ccd_turn__"): continue
                desc = i.get("description") or i.get("action_summary") or i.get("file_path") or i.get("url") or i.get("query") or i.get("skill") or ""
                if n == "Bash":
                    cmd = i.get("command", "")
                    cmd = cmd if len(cmd) < 600 else cmd[:600] + "\n…"
                    pending_tools.append(f"- **Bash** — {desc}\n\n  ```bash\n" + "\n".join("  " + l for l in cmd.splitlines()) + "\n  ```")
                else:
                    pending_tools.append(f"- **{n.replace('mcp__Claude_Browser__','navigateur:')}** — {desc}")
flush_tools()
open(out, "w").write("\n".join(md) + "\n")
print(len(md))
