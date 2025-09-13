import sys
import os
import re
import json
import subprocess

# --- Settings ---
EXT = ".neel"
COMPILE_SUBFOLDER = "compiled"

# --- Convert N# expressions to Python ---
def nsharp_expr_to_python(expr):
    expr = expr.strip()
    if not expr:
        return "0"

    # N# additive forms
    if expr.startswith('+') or expr.lower().startswith('add '):
        tokens = expr.replace('add', '').replace('+', '').split()
        args = [t if t.isdigit() else f"variables.get('{t}',0)" for t in tokens]
        return ' + '.join(args) if args else "0"

    # N# subtractive forms
    if expr.startswith('-') or expr.lower().startswith(('minus ', 'sub ')):
        tokens = expr.replace('minus', '').replace('sub', '').replace('-', '').split()
        args = [t if t.isdigit() else f"variables.get('{t}',0)" for t in tokens]
        return ' - '.join(args) if args else "0"

    # Normal arithmetic or variable refs
    def repl(m):
        name = m.group(0)
        return name if name.isdigit() else f"variables.get('{name}',0)"
    return re.sub(r"[A-Za-z_]\w*", repl, expr)

# --- Compiler ---
def compile_nsharp(lines, compiled_folder, file_path, db):
    py_lines = [
        "import os, re",
        "variables = {}",
        "html_output = []",
        "db = " + json.dumps(db),
        # Helpers
        "def hex_to_rgb(h):",
        "    h = h.lstrip('#')",
        "    if len(h) == 3: h = ''.join([c*2 for c in h])",
        "    return int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)",
        "def print_html_gradient(val, start_hex, end_hex):",
        "    val = str(val)",
        "    start = hex_to_rgb(start_hex)",
        "    end = hex_to_rgb(end_hex)",
        "    n = max(1, len(val))",
        "    for i, ch in enumerate(val):",
        "        r = int(start[0] + (end[0]-start[0]) * (i/(n-1) if n>1 else 0))",
        "        g = int(start[1] + (end[1]-start[1]) * (i/(n-1) if n>1 else 0))",
        "        b = int(start[2] + (end[2]-start[2]) * (i/(n-1) if n>1 else 0))",
        "        html_output.append(f'<span style=\"color:rgb({r},{g},{b})\">{ch}</span><br>')",
    ]

    assignments, others = [], []
    for line in lines:
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if "=" in s and not s.lower().startswith(("print", "question")):
            assignments.append(s)
        else:
            others.append(s)

    # Assignments first
    for line in assignments:
        var, expr = line.split("=", 1)
        var_name = var.strip()
        py_expr = nsharp_expr_to_python(expr)
        py_lines.append(f"variables['{var_name}'] = {py_expr}")

    # Others (questions, prints)
    for raw_line in others:
        # Question
        m_q = re.match(r"question\s*\(\s*(\w+)\s*,\s*(\w+)\s*\)\s*=\s*(.+)", raw_line, re.IGNORECASE)
        if m_q:
            var1, var2, question_str = m_q.groups()
            indent = ""
            if " if " in question_str:
                question, condition = question_str.split(" if ", 1)
                question = question.strip()
                cond_py = re.sub(r"([A-Za-z_]\w*)\s*=\s*([^\s]+)",
                                 lambda mm: f"(variables.get('{mm.group(1)}')=={mm.group(2)})",
                                 condition.strip())
                py_lines.append(f"if {cond_py.strip()}:")
                indent = "    "
            else:
                question = question_str

            py_lines.append(f"{indent}q = {json.dumps(question.strip())}")
            py_lines.append(f"{indent}name = q.lower().replace('what is','').strip()")
            py_lines.append(f"{indent}# remove leading articles like 'a ', 'an ', 'the '")
            py_lines.append(f"{indent}for article in ['a ', 'an ', 'the ']:")
            py_lines.append(f"{indent}    if name.startswith(article):")
            py_lines.append(f"{indent}        name = name[len(article):]")
            py_lines.append(f"{indent}variables['subject'] = name")
            py_lines.append(f"{indent}entry = next((item for item in db if item.get('name','').lower() == name), None)")
            py_lines.append(f"{indent}if entry:")
            py_lines.append(f"{indent}    variables['{var1}'] = entry.get('description','')")
            py_lines.append(f"{indent}    variables['{var2}'] = entry.get('img','')")
            continue

        # Print
        m_p = re.match(r"print\s+([^\s]+)(?:\s+in\s+(gradient\s+(#\w+)\s+(#\w+)|#\w+|[a-zA-Z]+))?(?:\s+if\s+(.+))?$",
                       raw_line, re.IGNORECASE)
        if m_p:
            expr, gradient_part, start_color, end_color, condition = m_p.groups()
            indent = ""
            if condition:
                cond_py = re.sub(r"([A-Za-z_]\w*)\s*=\s*([^\s]+)",
                                 lambda mm: f"(variables.get('{mm.group(1)}')=={mm.group(2)})",
                                 condition.strip())
                py_lines.append(f"if {cond_py.strip()}:")
                indent = "    "

            # --- Special: answer ---
            if expr.lower() == "answer":
                py_lines.append(f"{indent}if 'answer' in variables:")
                py_lines.append(f"{indent}    subj = variables.get('subject','')")
                py_lines.append(f"{indent}    ans = variables['answer']")
                py_lines.append(f"{indent}    if ans.lower().startswith(('a ','an ','the ')):")
                py_lines.append(f"{indent}        combined = f\"{{subj}} is {{ans}}\"")
                py_lines.append(f"{indent}    else:")
                py_lines.append(f"{indent}        combined = f\"{{subj}} is a {{ans}}\"")
                color = None
                if gradient_part:
                    if gradient_part.lower().startswith("gradient"):
                        color = start_color
                    else:
                        color = gradient_part
                if not color:
                    color = "#ee3f31"
                py_lines.append(f"{indent}    html_output.append(f'<span style=\"color:{color}\">{{combined}}</span><br>')")
                continue

            # --- Special: img ---
            if expr.lower() == "img":
                py_lines.append(f"{indent}if 'img' in variables and variables['img']:")
                py_lines.append(f"{indent}    html_output.append(f\"<img src='images/{{os.path.basename(variables['img'])}}'></img>\")")
                continue

            # --- Normal expression ---
            py_expr = nsharp_expr_to_python(expr)
            py_lines.append(f"{indent}val = {py_expr}")
            if gradient_part:
                if gradient_part.lower().startswith("gradient"):
                    py_lines.append(f"{indent}print_html_gradient(val, '{start_color}', '{end_color}')")
                else:
                    py_lines.append(f"{indent}html_output.append(f'<span style=\"color:{gradient_part}\">{{val}}</span><br>')")
            else:
                py_lines.append(f"{indent}html_output.append(str(val) + '<br>')")

    # Write HTML
    compiled_html_path = os.path.join(compiled_folder,
                                      os.path.splitext(os.path.basename(file_path))[0] + "_compiled.html").replace("\\", "/")
    py_lines.append(f"""
html_result = "\\n".join(html_output)
with open(r'{compiled_html_path}', 'w', encoding='utf-8') as f:
    f.write(html_result)
print("HTML snapshot written to {compiled_html_path}")
""")
    return "\n".join(py_lines)

def load_db_for_file(file_path):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(file_path)), ".."))
    db_file = os.path.join(base_dir, "db.json")
    if os.path.isfile(db_file):
        with open(db_file, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

# --- Main ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <file.neel>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not file_path.endswith(EXT):
        file_path += EXT
    if not os.path.isfile(file_path):
        print(f"Error: {file_path} does not exist.")
        sys.exit(1)

    db = load_db_for_file(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    compiled_folder = os.path.join(os.path.dirname(file_path), COMPILE_SUBFOLDER)
    os.makedirs(compiled_folder, exist_ok=True)

    compiled_py_path = os.path.join(compiled_folder,
                                    os.path.splitext(os.path.basename(file_path))[0] + "_compiled.py").replace("\\", "/")

    compiled_code = compile_nsharp(lines, compiled_folder, file_path, db)
    with open(compiled_py_path, "w", encoding="utf-8") as f:
        f.write(compiled_code)

    print(f"Compiled python saved to {compiled_py_path}")
    subprocess.run(["python", compiled_py_path])
