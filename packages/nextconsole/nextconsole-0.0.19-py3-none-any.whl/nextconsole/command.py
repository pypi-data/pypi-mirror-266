import os
import json
import re
import subprocess
import sys
import pdb
import math
from .envinfo import envinfo
from wcwidth import wcwidth

def hidden(s):
    for seg in re.findall("(<!-- .*? -->)", s):
        s = s.replace(seg, "")
    return s
           

def inc_height(cstr):
    inc = 0
    width = os.get_terminal_size().columns
    for l in cstr.split("\n"):
        inc += max(sum([wcwidth(w) for w in l]) // (width) - 1, 0)
    return inc
    

def console_md(console, md):
    from io import StringIO
    import sys
    _stdout = sys.stdout
    sys.stdout = sto = StringIO()
    console.print(md)
    sys.stdout = _stdout
    v = sto.getvalue()
    print(v)
    return v

    
def cmd():
    import requests
    import json
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.prompt import Prompt
    import re
    import sys
    mode = 'shell'
    lasterr = ""
    if os.path.exists("/tmp/.ntcache"):
        lasterr = open("/tmp/.ntcache", "r").read()
    if len(sys.argv) < 2 and lasterr == "":
        print("NextConsole 未识别出需求呢!")
        exit()
    if len(sys.argv) < 2:
        prompt = lasterr
        mode = 'error'
    else:
        prompt = sys.argv[1]
    console = Console(soft_wrap=False)

    content = ""
    strs = []
    last_lines = 0
    response = requests.post("http://nc.turing.fun:8228/api/nc", data=json.dumps({"mode": mode,"chat": prompt, 'envinfo': envinfo()}), headers={"Content-Type": "application/json"}, stream=True)
    console.print(" \n")
    for i, c in enumerate(response.iter_content(chunk_size=10)):
        # if i <= 1000:
        #     print(u'\u001b[1A', end='')
        c = c.decode()

        if c is not None:
            strs.append(c)
        content = "".join(strs)
        md = Markdown(content)
        
        # if mode == 'error':
        #     console.log(content)
        # else:
        # console.print(md)
        raw = console_md(console, md)
        last_lines = raw.count("\n") + 1
        # if len(md.parsed) > 0:
        #     last_lines = sum([p.map[1] for p in md.parsed if p is not None and p.map is not None])
            
        # if not i % 100:
        #     pdb.set_trace()
        
        for _ in range(last_lines + inc_height(content)): #+ math.ceil(content.count('```') / 2) * 2 - 1):
            print(u'\u001b[1A', end='')
        
        
     # print(content)

    hcontent = hidden(content)
    # content = chat(prompt)
    cmd = "\n".join(re.findall("[```|```shell]\n([\s\S]*?)```", 
                             hcontent))

    console = Console()
    md = Markdown(hcontent)
    console.print(md)
    if 'mode=shell' in content:
        sure = Prompt.ask("Exec these commands?", choices=["Yes(Default)", "No", "N", "n"], default="Yes")
        if sure == 'Yes':
            proc = subprocess.Popen(cmd, shell=True, 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE, 
                                    text=True)
            lines = []
            for line in proc.stdout:
                print(line)  # 打印每一行输出
                lines.append(line)

            # 检查是否有错误输出
            if proc.stderr:
                for line in proc.stderr:
                    print(f"{line}")
                    lines.append(line)
                   
            open("/tmp/.ntcache", "w").write("\n".join(lines))

if __name__ == "__main__":
    cmd()
    
    

    