import os, re
variables = {}
html_output = []
db = [{"name": "apple", "description": "juicy fruit", "img": "E:/Neels Programs/first lang/images/apple.jpg"}, {"name": "paris", "description": "city in france", "img": "E:/Neels Programs/first lang/images/paris.jpg"}]
def hex_to_rgb(h):
    h = h.lstrip('#')
    if len(h) == 3: h = ''.join([c*2 for c in h])
    return int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
def print_html_gradient(val, start_hex, end_hex):
    val = str(val)
    start = hex_to_rgb(start_hex)
    end = hex_to_rgb(end_hex)
    n = max(1, len(val))
    for i, ch in enumerate(val):
        r = int(start[0] + (end[0]-start[0]) * (i/(n-1) if n>1 else 0))
        g = int(start[1] + (end[1]-start[1]) * (i/(n-1) if n>1 else 0))
        b = int(start[2] + (end[2]-start[2]) * (i/(n-1) if n>1 else 0))
        html_output.append(f'<span style="color:rgb({r},{g},{b})">{ch}</span><br>')
variables['a'] = 3 + 4 + 5
val = variables.get('a',0)
print_html_gradient(val, '#02f', '#ee3f31')
if (variables.get('a')==12):
    q = "what is an apple"
    name = q.lower().replace('what is','').strip()
    # remove leading articles like 'a ', 'an ', 'the '
    for article in ['a ', 'an ', 'the ']:
        if name.startswith(article):
            name = name[len(article):]
    variables['subject'] = name
    entry = next((item for item in db if item.get('name','').lower() == name), None)
    if entry:
        variables['answer'] = entry.get('description','')
        variables['img'] = entry.get('img','')
if 'answer' in variables:
    subj = variables.get('subject','')
    ans = variables['answer']
    if ans.lower().startswith(('a ','an ','the ')):
        combined = f"{subj} is {ans}"
    else:
        combined = f"{subj} is a {ans}"
    html_output.append(f'<span style="color:#ee3f31">{combined}</span><br>')
if (variables.get('a')==12):
    if 'img' in variables and variables['img']:
        html_output.append(f"<img src='images/{os.path.basename(variables['img'])}'></img>")

html_result = "\n".join(html_output)
with open(r'E:/Neels Programs/first lang/N# projects/compiled/test_compiled.html', 'w', encoding='utf-8') as f:
    f.write(html_result)
print("HTML snapshot written to E:/Neels Programs/first lang/N# projects/compiled/test_compiled.html")
