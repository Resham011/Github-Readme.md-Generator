# import os
# import re
# import requests
# import gradio as gr

# # ─────────────────────────────────────────
# #  Config
# # ─────────────────────────────────────────
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# GITHUB_TOKEN       = os.getenv("GITHUB_TOKEN", "")
# OPENROUTER_MODEL   = "nvidia/nemotron-nano-12b-v2-vl:free"

# SYSTEM_PROMPT = """You are an elite open-source developer and technical writer.
# Generate a stunning, COMPLETE GitHub README.md strictly in Markdown format.

# Rules:
# - Use real markdown: headers, code blocks, badges, tables, emojis
# - Be SPECIFIC — use the actual project name, language, file names, and real details from context
# - Include EVERY section listed by the user — do NOT skip any
# - Folder structure must be a real ASCII tree using the actual files/dirs provided
# - Contributing section must be detailed with step-by-step git workflow
# - Badge line must use shields.io markdown syntax (realistic placeholders)
# - Output ONLY the markdown. No explanations, no preamble, no trailing comments."""

# ALL_SECTIONS = [
#     "Project Title & Tagline",
#     "Badges (stars, forks, license, language)",
#     "Table of Contents",
#     "About / Overview",
#     "Features",
#     "Tech Stack",
#     "Folder / Project Structure",
#     "Prerequisites",
#     "Installation & Setup",
#     "Usage / Examples",
#     "Environment Variables",
#     "Roadmap",
#     "Contributing Guidelines (with git workflow)",
#     "License",
#     "Acknowledgements",
# ]

# LOADER_HTML = """
# <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
#             gap:16px;padding:32px 0 24px;font-family:'Fira Code',monospace;">
#   <div style="width:54px;height:54px;border-radius:50%;
#               border:3px solid #1f2840;
#               border-top-color:#3cffd0;
#               border-right-color:#f0c060;
#               animation:rfSpin .85s linear infinite;"></div>
#   <div style="color:#3cffd0;font-size:.76rem;letter-spacing:2.5px;
#               text-transform:uppercase;animation:rfPulse 1.4s ease-in-out infinite;">
#     Forging your README&hellip;
#   </div>
#   <div style="display:flex;gap:8px;">
#     <span style="width:8px;height:8px;border-radius:50%;background:#f0c060;
#                  animation:rfBounce 1.1s ease-in-out infinite;animation-delay:0s;"></span>
#     <span style="width:8px;height:8px;border-radius:50%;background:#3cffd0;
#                  animation:rfBounce 1.1s ease-in-out infinite;animation-delay:.18s;"></span>
#     <span style="width:8px;height:8px;border-radius:50%;background:#ff5e7a;
#                  animation:rfBounce 1.1s ease-in-out infinite;animation-delay:.36s;"></span>
#   </div>
# </div>
# <style>
#   @keyframes rfSpin   { to { transform: rotate(360deg); } }
#   @keyframes rfPulse  { 0%,100%{opacity:.35} 50%{opacity:1} }
#   @keyframes rfBounce { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-8px)} }
# </style>
# """


# # ─────────────────────────────────────────
# #  GitHub helpers
# # ─────────────────────────────────────────
# def gh_headers():
#     h = {"Accept": "application/vnd.github+json"}
#     if GITHUB_TOKEN:
#         h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
#     return h

# def parse_repo_url(url: str):
#     url = url.strip().rstrip("/")
#     m = re.search(r"github\.com[:/]([^/]+)/([^/\s]+?)(?:\.git)?$", url)
#     if m:
#         return m.group(1), m.group(2)
#     return None, None

# def fetch_repo_meta(owner, repo):
#     r = requests.get(f"https://api.github.com/repos/{owner}/{repo}",
#                      headers=gh_headers(), timeout=10)
#     r.raise_for_status()
#     return r.json()

# def fetch_tree(owner, repo, branch="HEAD"):
#     r = requests.get(
#         f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1",
#         headers=gh_headers(), timeout=10,
#     )
#     if r.status_code != 200:
#         return []
#     return [item["path"] for item in r.json().get("tree", []) if item["type"] == "blob"]

# def fetch_file(owner, repo, path):
#     import base64
#     r = requests.get(
#         f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
#         headers=gh_headers(), timeout=10,
#     )
#     if r.status_code != 200:
#         return ""
#     try:
#         return base64.b64decode(r.json().get("content", "")).decode("utf-8", errors="ignore")[:2000]
#     except Exception:
#         return ""

# def fetch_languages(owner, repo):
#     r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/languages",
#                      headers=gh_headers(), timeout=10)
#     return list(r.json().keys()) if r.status_code == 200 else []

# def build_folder_tree(paths, max_depth=3):
#     tree = {}
#     for path in paths:
#         parts = path.split("/")
#         if len(parts) > max_depth:
#             parts = parts[:max_depth]
#         node = tree
#         for p in parts:
#             node = node.setdefault(p, {})
#     lines = []
#     def render(node, prefix=""):
#         items = list(node.items())
#         for i, (name, children) in enumerate(items):
#             is_last = i == len(items) - 1
#             lines.append(prefix + ("└── " if is_last else "├── ") + name)
#             if children:
#                 render(children, prefix + ("    " if is_last else "│   "))
#     render(tree)
#     return "\n".join(lines)


# # ─────────────────────────────────────────
# #  OpenRouter
# # ─────────────────────────────────────────
# def call_openrouter(prompt: str) -> str:
#     if not OPENROUTER_API_KEY:
#         return "ERROR: OPENROUTER_API_KEY secret not set in HF Space settings."
#     r = requests.post(
#         "https://openrouter.ai/api/v1/chat/completions",
#         headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}",
#                  "Content-Type": "application/json"},
#         json={
#             "model": OPENROUTER_MODEL,
#             "max_tokens": 4096,
#             "messages": [
#                 {"role": "system", "content": SYSTEM_PROMPT},
#                 {"role": "user",   "content": prompt},
#             ],
#         },
#         timeout=90,
#     )
#     r.raise_for_status()
#     obj = r.json()
#     if "choices" in obj and obj["choices"]:
#         return obj["choices"][0]["message"]["content"].strip()
#     return "[No response from model]"


# # ─────────────────────────────────────────
# #  Main generator — plain function (no yield)
# #  Returns: (loader_update, status_str, readme_str)
# # ─────────────────────────────────────────
# def generate_readme(repo_url, license_choice, extra_context, sections):
#     hide = gr.update(visible=False)

#     if not repo_url.strip():
#         return hide, "Please paste a GitHub repository URL.", ""

#     owner, repo = parse_repo_url(repo_url)
#     if not owner:
#         return hide, "Could not parse GitHub URL. Use: https://github.com/owner/repo", ""

#     log = []
#     log.append(f"Fetching {owner}/{repo} from GitHub...")

#     try:
#         meta      = fetch_repo_meta(owner, repo)
#         languages = fetch_languages(owner, repo)
#         all_files = fetch_tree(owner, repo, meta.get("default_branch", "HEAD"))
#     except Exception as e:
#         return hide, "\n".join(log) + f"\nGitHub API error: {e}", ""

#     log.append(f"Got {len(all_files)} files. Languages: {', '.join(languages) or 'unknown'}")

#     key_files = ["requirements.txt", "pyproject.toml", "package.json",
#                  "Cargo.toml", "setup.py", "Dockerfile", ".env.example", "Makefile"]
#     snippets = ""
#     for kf in key_files:
#         if kf in all_files:
#             content = fetch_file(owner, repo, kf)
#             if content:
#                 snippets += f"\n\n### {kf}\n```\n{content[:600]}\n```"

#     folder_tree = build_folder_tree(all_files, max_depth=3)
#     sections_str = "\n".join(f"- {s}" for s in (sections or ALL_SECTIONS))

#     prompt = f"""Generate a complete GitHub README.md for this repository.

# ## Repository Info
# - **Name:** {meta.get('name', repo)}
# - **Owner:** {owner}
# - **Description:** {meta.get('description') or extra_context or 'No description provided'}
# - **Primary Language:** {meta.get('language') or 'Unknown'}
# - **All Languages:** {', '.join(languages) or 'Unknown'}
# - **Stars:** {meta.get('stargazers_count', 0)} | **Forks:** {meta.get('forks_count', 0)}
# - **Default Branch:** {meta.get('default_branch', 'main')}
# - **License:** {license_choice}
# - **Topics:** {', '.join(meta.get('topics', [])) or 'none'}
# - **Homepage:** {meta.get('homepage') or 'none'}

# ## Folder Structure (actual repo files)
# ```
# {repo}/
# {folder_tree[:2000]}
# ```

# ## Key File Contents{snippets}

# ## Extra Context from User
# {extra_context or 'None provided'}

# ## Required Sections — include ALL of these
# {sections_str}

# Use **{license_choice}** license in the License section.

# Now generate the full README.md:"""

#     log.append("Calling AI model... (this may take 15-30s)")

#     try:
#         readme = call_openrouter(prompt)
#     except Exception as e:
#         return hide, "\n".join(log) + f"\nAI error: {e}", ""

#     log.append("Done! Your README is ready below.")
#     return hide, "\n".join(log), readme


# # ─────────────────────────────────────────
# #  CSS
# # ─────────────────────────────────────────
# CSS = """
# @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@300;400;500;600&family=Fira+Code:wght@300;400;500&display=swap');
# :root {
#     --ink:   #0b0e14;
#     --paper: #111520;
#     --card:  #161b27;
#     --rim:   #1f2840;
#     --gold:  #f0c060;
#     --teal:  #3cffd0;
#     --rose:  #ff5e7a;
#     --dim:   #4a5570;
#     --body:  #c8cfe0;
# }
# *, *::before, *::after { box-sizing: border-box; }
# body, .gradio-container {
#     background: var(--ink) !important;
#     color: var(--body) !important;
#     font-family: 'Outfit', sans-serif !important;
# }
# .gradio-container { max-width: 1180px !important; margin: 0 auto !important; }
# .hdr {
#     display:flex; align-items:center; gap:24px;
#     padding:38px 0 28px;
#     border-bottom:1px solid var(--rim);
#     margin-bottom:32px;
# }
# .hdr-icon { font-size:3.2rem; line-height:1; filter:drop-shadow(0 0 18px rgba(240,192,96,.45)); }
# .hdr-text h1 {
#     font-family:'Bebas Neue',sans-serif;
#     font-size:3rem; letter-spacing:3px;
#     color:var(--gold); margin:0 0 4px;
#     text-shadow:0 0 30px rgba(240,192,96,.3);
# }
# .hdr-text p { color:var(--dim); font-size:.82rem; margin:0; letter-spacing:.5px; }
# .lbl {
#     font-family:'Fira Code',monospace;
#     font-size:.68rem; letter-spacing:2.5px;
#     text-transform:uppercase; color:var(--teal);
#     margin-bottom:10px;
# }
# textarea, input[type="text"] {
#     background:var(--card) !important;
#     border:1px solid var(--rim) !important;
#     border-radius:6px !important;
#     color:var(--body) !important;
#     font-family:'Fira Code',monospace !important;
#     font-size:.83rem !important;
#     transition:border-color .18s, box-shadow .18s !important;
# }
# textarea:focus, input[type="text"]:focus {
#     border-color:var(--teal) !important;
#     box-shadow:0 0 0 2px rgba(60,255,208,.08) !important;
# }
# .status-box textarea {
#     background:var(--paper) !important;
#     border-color:var(--rim) !important;
#     font-family:'Fira Code',monospace !important;
#     font-size:.78rem !important;
#     color:var(--teal) !important;
# }
# .out-box textarea {
#     background:var(--paper) !important;
#     border:1px solid var(--rim) !important;
#     font-family:'Fira Code',monospace !important;
#     font-size:.8rem !important;
#     color:#e0e8ff !important;
#     line-height:1.55 !important;
# }
# .divider {
#     height:1px;
#     background:linear-gradient(90deg,transparent,var(--rim),transparent);
#     margin:6px 0 20px;
# }
# .tip {
#     background:var(--card);
#     border:1px solid var(--rim);
#     border-left:3px solid var(--gold);
#     border-radius:6px;
#     padding:11px 15px;
#     font-size:.78rem;
#     color:var(--dim);
#     line-height:1.65;
#     margin-bottom:16px;
#     font-family:'Fira Code',monospace;
# }
# .ftr {
#     text-align:center; margin-top:36px;
#     color:#1e2535; font-size:.68rem;
#     font-family:'Fira Code',monospace;
#     letter-spacing:.5px;
# }
# """

# # ─────────────────────────────────────────
# #  UI
# # ─────────────────────────────────────────
# with gr.Blocks(title="README Forge", css=CSS,
#                theme=gr.themes.Base(primary_hue="emerald", neutral_hue="slate")) as demo:

#     gr.HTML("""
#     <div class="hdr">
#       <div class="hdr-icon">📜</div>
#       <div class="hdr-text">
#         <h1>README FORGE</h1>
#         <p>Paste a GitHub repo URL &rarr; get a production-ready README in seconds</p>
#       </div>
#     </div>
#     """)

#     with gr.Row(equal_height=False):

#         # LEFT panel
#         with gr.Column(scale=1, min_width=320):
#             gr.HTML('<div class="lbl">Configuration</div><div class="divider"></div>')
#             gr.HTML('<div class="tip">Paste any public GitHub URL. Real file trees, languages and metadata are fetched automatically.</div>')

#             repo_url = gr.Textbox(
#                 label="GitHub Repository URL",
#                 placeholder="https://github.com/owner/repository",
#                 lines=1,
#             )
#             license_choice = gr.Dropdown(
#                 label="License",
#                 choices=["MIT", "Apache 2.0", "GPL-3.0", "BSD-2-Clause", "AGPL-3.0", "Unlicense"],
#                 value="MIT",
#             )
#             extra_context = gr.Textbox(
#                 label="Extra Context (optional)",
#                 placeholder="What does it do? Any special details the AI should know?",
#                 lines=3,
#             )
#             gr.HTML('<div class="lbl" style="margin-top:18px;">Sections to Include</div>')
#             sections = gr.CheckboxGroup(
#                 choices=ALL_SECTIONS,
#                 value=ALL_SECTIONS,
#                 label="",
#                 interactive=True,
#             )
#             with gr.Row():
#                 gen_btn   = gr.Button("Generate README", variant="primary", size="lg")
#                 clear_btn = gr.Button("Clear", variant="secondary")

#         # RIGHT panel
#         with gr.Column(scale=2):

#             loader = gr.HTML(value="", visible=False)

#             gr.HTML('<div class="lbl">Status</div><div class="divider"></div>')
#             status_box = gr.Textbox(
#                 label="", interactive=False, lines=4,
#                 placeholder="Waiting for input...",
#                 elem_classes=["status-box"],
#             )
#             gr.HTML('<div class="lbl" style="margin-top:20px;">Generated README.md</div><div class="divider"></div>')
#             output_box = gr.Textbox(
#                 label="", interactive=False, lines=30,
#                 placeholder="Your README will appear here — ready to copy and paste into GitHub.",
#                 show_copy_button=True,
#                 elem_classes=["out-box"],
#             )

#     gr.HTML('<div class="ftr">README Forge &nbsp;&middot;&nbsp; Powered by OpenRouter &middot; nvidia/nemotron-nano-12b &middot; GitHub API</div>')

#     # Show loader → run generation (which returns loader=hidden) → done
#     gen_btn.click(
#         fn=lambda: gr.update(value=LOADER_HTML, visible=True),
#         inputs=None,
#         outputs=loader,
#     ).then(
#         fn=generate_readme,
#         inputs=[repo_url, license_choice, extra_context, sections],
#         outputs=[loader, status_box, output_box],
#     )

#     clear_btn.click(
#         fn=lambda: ("", "MIT", "", ALL_SECTIONS, "", ""),
#         outputs=[repo_url, license_choice, extra_context, sections, status_box, output_box],
#     )

# if __name__ == "__main__":
#     demo.launch(server_name="0.0.0.0", server_port=7860, debug=True)

import os
import re
import requests
import gradio as gr

# ─────────────────────────────────────────
#  Config
# ─────────────────────────────────────────
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GITHUB_TOKEN       = os.getenv("GITHUB_TOKEN", "")
OPENROUTER_MODEL   = "nvidia/nemotron-nano-12b-v2-vl:free"

SYSTEM_PROMPT = """You are an elite open-source developer and technical writer.
Generate a stunning, COMPLETE GitHub README.md strictly in Markdown format.

Rules:
- Use real markdown: headers, code blocks, badges, tables, emojis
- Be SPECIFIC — use the actual project name, language, file names, and real details from context
- Include EVERY section listed by the user — do NOT skip any
- Folder structure must be a real ASCII tree using the actual files/dirs provided
- Contributing section must be detailed with step-by-step git workflow
- Badge line must use shields.io markdown syntax (realistic placeholders)
- Output ONLY the markdown. No explanations, no preamble, no trailing comments."""

ALL_SECTIONS = [
    "Project Title & Tagline",
    "Badges (stars, forks, license, language)",
    "Table of Contents",
    "About / Overview",
    "Features",
    "Tech Stack",
    "Folder / Project Structure",
    "Prerequisites",
    "Installation & Setup",
    "Usage / Examples",
    "Environment Variables",
    "Roadmap",
    "Contributing Guidelines (with git workflow)",
    "License",
    "Acknowledgements",
]

LOADER_HTML = """
<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
            gap:16px;padding:32px 0 24px;font-family:'Fira Code',monospace;">
  <div style="width:54px;height:54px;border-radius:50%;
              border:3px solid #1f2840;
              border-top-color:#3cffd0;
              border-right-color:#f0c060;
              animation:rfSpin .85s linear infinite;"></div>
  <div style="color:#3cffd0;font-size:.76rem;letter-spacing:2.5px;
              text-transform:uppercase;animation:rfPulse 1.4s ease-in-out infinite;">
    Forging your README&hellip;
  </div>
  <div style="display:flex;gap:8px;">
    <span style="width:8px;height:8px;border-radius:50%;background:#f0c060;
                 animation:rfBounce 1.1s ease-in-out infinite;animation-delay:0s;"></span>
    <span style="width:8px;height:8px;border-radius:50%;background:#3cffd0;
                 animation:rfBounce 1.1s ease-in-out infinite;animation-delay:.18s;"></span>
    <span style="width:8px;height:8px;border-radius:50%;background:#ff5e7a;
                 animation:rfBounce 1.1s ease-in-out infinite;animation-delay:.36s;"></span>
  </div>
</div>
<style>
  @keyframes rfSpin   { to { transform: rotate(360deg); } }
  @keyframes rfPulse  { 0%,100%{opacity:.35} 50%{opacity:1} }
  @keyframes rfBounce { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-8px)} }
</style>
"""

# ─────────────────────────────────────────
#  GitHub helpers
# ─────────────────────────────────────────
def gh_headers():
    h = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return h

def parse_repo_url(url: str):
    url = url.strip().rstrip("/")
    m = re.search(r"github\.com[:/]([^/]+)/([^/\s]+?)(?:\.git)?$", url)
    if m:
        return m.group(1), m.group(2)
    return None, None

def fetch_repo_meta(owner, repo):
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}",
                     headers=gh_headers(), timeout=10)
    r.raise_for_status()
    return r.json()

def fetch_tree(owner, repo, branch="HEAD"):
    r = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1",
        headers=gh_headers(), timeout=10,
    )
    if r.status_code != 200:
        return []
    return [item["path"] for item in r.json().get("tree", []) if item["type"] == "blob"]

def fetch_file(owner, repo, path):
    import base64
    r = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
        headers=gh_headers(), timeout=10,
    )
    if r.status_code != 200:
        return ""
    try:
        return base64.b64decode(r.json().get("content", "")).decode("utf-8", errors="ignore")[:2000]
    except Exception:
        return ""

def fetch_languages(owner, repo):
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/languages",
                     headers=gh_headers(), timeout=10)
    return list(r.json().keys()) if r.status_code == 200 else []

def build_folder_tree(paths, max_depth=3):
    tree = {}
    for path in paths:
        parts = path.split("/")
        if len(parts) > max_depth:
            parts = parts[:max_depth]
        node = tree
        for p in parts:
            node = node.setdefault(p, {})
    lines = []
    def render(node, prefix=""):
        items = list(node.items())
        for i, (name, children) in enumerate(items):
            is_last = i == len(items) - 1
            lines.append(prefix + ("└── " if is_last else "├── ") + name)
            if children:
                render(children, prefix + ("    " if is_last else "│   "))
    render(tree)
    return "\n".join(lines)

# ─────────────────────────────────────────
#  OpenRouter
# ─────────────────────────────────────────
def call_openrouter(prompt: str) -> str:
    if not OPENROUTER_API_KEY:
        return "ERROR: OPENROUTER_API_KEY secret not set."
    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}",
                 "Content-Type": "application/json"},
        json={
            "model": OPENROUTER_MODEL,
            "max_tokens": 4096,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
        },
        timeout=90,
    )
    r.raise_for_status()
    obj = r.json()
    if "choices" in obj and obj["choices"]:
        return obj["choices"][0]["message"]["content"].strip()
    return "[No response from model]"

# ─────────────────────────────────────────
#  Generator — yields status updates live
# ─────────────────────────────────────────
def generate_readme(repo_url, license_choice, extra_context, sections):
    # Each yield: (loader_html, status_text, readme_text)

    if not repo_url.strip():
        yield gr.update(visible=False), "Please paste a GitHub repository URL.", ""
        return

    owner, repo = parse_repo_url(repo_url)
    if not owner:
        yield gr.update(visible=False), "Could not parse GitHub URL. Use: https://github.com/owner/repo", ""
        return

    log = []

    log.append("🔍 Fetching repo metadata from GitHub...")
    yield gr.update(value=LOADER_HTML, visible=True), "\n".join(log), ""

    try:
        meta      = fetch_repo_meta(owner, repo)
        languages = fetch_languages(owner, repo)
        all_files = fetch_tree(owner, repo, meta.get("default_branch", "HEAD"))
    except Exception as e:
        yield gr.update(visible=False), f"GitHub API error: {e}", ""
        return

    log.append(f"✅ Got {len(all_files)} files · Languages: {', '.join(languages) or 'unknown'}")
    yield gr.update(value=LOADER_HTML, visible=True), "\n".join(log), ""

    key_files = ["requirements.txt", "pyproject.toml", "package.json",
                 "Cargo.toml", "setup.py", "Dockerfile", ".env.example", "Makefile"]
    snippets = ""
    for kf in key_files:
        if kf in all_files:
            content = fetch_file(owner, repo, kf)
            if content:
                snippets += f"\n\n### {kf}\n```\n{content[:600]}\n```"

    folder_tree = build_folder_tree(all_files, max_depth=3)
    sections_str = "\n".join(f"- {s}" for s in (sections or ALL_SECTIONS))

    prompt = f"""Generate a complete GitHub README.md for this repository.

## Repository Info
- **Name:** {meta.get('name', repo)}
- **Owner:** {owner}
- **Description:** {meta.get('description') or extra_context or 'No description provided'}
- **Primary Language:** {meta.get('language') or 'Unknown'}
- **All Languages:** {', '.join(languages) or 'Unknown'}
- **Stars:** {meta.get('stargazers_count', 0)} | **Forks:** {meta.get('forks_count', 0)}
- **Default Branch:** {meta.get('default_branch', 'main')}
- **License:** {license_choice}
- **Topics:** {', '.join(meta.get('topics', [])) or 'none'}
- **Homepage:** {meta.get('homepage') or 'none'}

## Folder Structure (actual repo files)
```
{repo}/
{folder_tree[:2000]}
```

## Key File Contents{snippets}

## Extra Context from User
{extra_context or 'None provided'}

## Required Sections — include ALL of these
{sections_str}

Use **{license_choice}** license in the License section.

Now generate the full README.md:"""

    log.append("🤖 AI is writing your README... (15–30s)")
    yield gr.update(value=LOADER_HTML, visible=True), "\n".join(log), ""

    try:
        readme = call_openrouter(prompt)
    except Exception as e:
        yield gr.update(visible=False), "\n".join(log) + f"\nAI error: {e}", ""
        return

    log.append("✅ Done! Your README is ready below.")
    yield gr.update(visible=False), "\n".join(log), readme


# ─────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@300;400;500;600&family=Fira+Code:wght@300;400;500&display=swap');
:root {
    --ink:   #0b0e14;
    --paper: #111520;
    --card:  #161b27;
    --rim:   #1f2840;
    --gold:  #f0c060;
    --teal:  #3cffd0;
    --rose:  #ff5e7a;
    --dim:   #4a5570;
    --body:  #c8cfe0;
}
*, *::before, *::after { box-sizing: border-box; }
body, .gradio-container {
    background: var(--ink) !important;
    color: var(--body) !important;
    font-family: 'Outfit', sans-serif !important;
}
.gradio-container { max-width: 1180px !important; margin: 0 auto !important; }
.hdr {
    display:flex; align-items:center; gap:24px;
    padding:38px 0 28px;
    border-bottom:1px solid var(--rim);
    margin-bottom:32px;
}
.hdr-icon { font-size:3.2rem; line-height:1; filter:drop-shadow(0 0 18px rgba(240,192,96,.45)); }
.hdr-text h1 {
    font-family:'Bebas Neue',sans-serif;
    font-size:3rem; letter-spacing:3px;
    color:var(--gold); margin:0 0 4px;
    text-shadow:0 0 30px rgba(240,192,96,.3);
}
.hdr-text p { color:var(--dim); font-size:.82rem; margin:0; letter-spacing:.5px; }
.lbl {
    font-family:'Fira Code',monospace;
    font-size:.68rem; letter-spacing:2.5px;
    text-transform:uppercase; color:var(--teal);
    margin-bottom:10px;
}
textarea, input[type="text"] {
    background:var(--card) !important;
    border:1px solid var(--rim) !important;
    border-radius:6px !important;
    color:var(--body) !important;
    font-family:'Fira Code',monospace !important;
    font-size:.83rem !important;
    transition:border-color .18s, box-shadow .18s !important;
}
textarea:focus, input[type="text"]:focus {
    border-color:var(--teal) !important;
    box-shadow:0 0 0 2px rgba(60,255,208,.08) !important;
}
.status-box textarea {
    background:var(--paper) !important;
    border-color:var(--rim) !important;
    font-family:'Fira Code',monospace !important;
    font-size:.78rem !important;
    color:var(--teal) !important;
}
.out-box textarea {
    background:var(--paper) !important;
    border:1px solid var(--rim) !important;
    font-family:'Fira Code',monospace !important;
    font-size:.8rem !important;
    color:#e0e8ff !important;
    line-height:1.55 !important;
}
.divider { height:1px; background:linear-gradient(90deg,transparent,var(--rim),transparent); margin:6px 0 20px; }
.tip {
    background:var(--card); border:1px solid var(--rim);
    border-left:3px solid var(--gold); border-radius:6px;
    padding:11px 15px; font-size:.78rem; color:var(--dim);
    line-height:1.65; margin-bottom:16px; font-family:'Fira Code',monospace;
}
.ftr { text-align:center; margin-top:36px; color:#1e2535; font-size:.68rem; font-family:'Fira Code',monospace; letter-spacing:.5px; }
"""

# ─────────────────────────────────────────
#  UI
# ─────────────────────────────────────────
with gr.Blocks(title="README Forge", css=CSS,
               theme=gr.themes.Base(primary_hue="emerald", neutral_hue="slate")) as demo:

    gr.HTML("""
    <div class="hdr">
      <div class="hdr-icon">📜</div>
      <div class="hdr-text">
        <h1>README FORGE</h1>
        <p>Paste a GitHub repo URL &rarr; get a production-ready README in seconds</p>
      </div>
    </div>
    """)

    with gr.Row(equal_height=False):

        with gr.Column(scale=1, min_width=320):
            gr.HTML('<div class="lbl">Configuration</div><div class="divider"></div>')
            gr.HTML('<div class="tip">Paste any public GitHub URL. Real file trees, languages and metadata are fetched automatically.</div>')

            repo_url = gr.Textbox(
                label="GitHub Repository URL",
                placeholder="https://github.com/owner/repository",
                lines=1,
            )
            license_choice = gr.Dropdown(
                label="License",
                choices=["MIT", "Apache 2.0", "GPL-3.0", "BSD-2-Clause", "AGPL-3.0", "Unlicense"],
                value="MIT",
            )
            extra_context = gr.Textbox(
                label="Extra Context (optional)",
                placeholder="What does it do? Any special details the AI should know?",
                lines=3,
            )
            gr.HTML('<div class="lbl" style="margin-top:18px;">Sections to Include</div>')
            sections = gr.CheckboxGroup(
                choices=ALL_SECTIONS,
                value=ALL_SECTIONS,
                label="",
                interactive=True,
            )
            with gr.Row():
                gen_btn   = gr.Button("⚡  Generate README", variant="primary", size="lg")
                clear_btn = gr.Button("↺  Clear", variant="secondary")

        with gr.Column(scale=2):

            loader = gr.HTML(value="", visible=False)

            gr.HTML('<div class="lbl">Status</div><div class="divider"></div>')
            status_box = gr.Textbox(
                label="", interactive=False, lines=4,
                placeholder="Waiting for input...",
                elem_classes=["status-box"],
            )
            gr.HTML('<div class="lbl" style="margin-top:20px;">Generated README.md</div><div class="divider"></div>')
            output_box = gr.Textbox(
                label="", interactive=False, lines=30,
                placeholder="Your README will appear here — ready to copy and paste into GitHub.",
                show_copy_button=True,
                elem_classes=["out-box"],
            )

    gr.HTML('<div class="ftr">README Forge &nbsp;&middot;&nbsp; OpenRouter &middot; nvidia/nemotron-nano-12b &middot; GitHub API</div>')

    gen_btn.click(
        fn=generate_readme,
        inputs=[repo_url, license_choice, extra_context, sections],
        outputs=[loader, status_box, output_box],
    )

    clear_btn.click(
        fn=lambda: ("", "MIT", "", ALL_SECTIONS, "", ""),
        outputs=[repo_url, license_choice, extra_context, sections, status_box, output_box],
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, debug=True)