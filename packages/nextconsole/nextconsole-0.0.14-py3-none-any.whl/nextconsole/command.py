import os
import json
import re
from .envinfo import envinfo

def hidden(s):
    for seg in re.findall("(<!-- .*? -->)", s):
        s = s.replace(seg, "")
    return s
            
def cmd():
    import requests
    import json
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.prompt import Prompt
    import re
    import sys
    if len(sys.argv) < 2:
        print("NextConsole 未识别出需求呢!")
        exit()
    prompt = sys.argv[1]
    console = Console(soft_wrap=True)

    content = ""
    strs = []
    last_lines = 0
    response = requests.post("http://nc.turing.fun:8228/api/nc", data=json.dumps({"chat": prompt, 'envinfo': envinfo()}), headers={"Content-Type": "application/json"}, stream=True)
    console.print("命令如下\n")
    for i, c in enumerate(response.iter_content(chunk_size=10)):
        # if i <= 1:
        #     print(u'\u001b[1A', end='')
        c = c.decode()

        if c is not None:
            strs.append(c)
        content = "".join(strs)
        md = Markdown(content)
        console.print(md)
        if len(md.parsed) > 0:
            last_lines = md.parsed[0].map[1] + 1
        for _ in range(last_lines):
            print(u'\u001b[1A', end='')

    hcontent = hidden(content)
    # content = chat(prompt)
    cmd = "\n".join(re.findall("```shell\n([\s\S]*?)```", 
                             hcontent))


    console = Console()
    md = Markdown(hcontent)
    console.print(md)
    if 'mode=shell' in content:
        sure = Prompt.ask("Exec these commands?", choices=["Yes(Default)", "No", "N", "n"], default="Yes")
        if sure == 'Yes':
            os.system(cmd)

if __name__ == "__main__":
    cmd()
    
    