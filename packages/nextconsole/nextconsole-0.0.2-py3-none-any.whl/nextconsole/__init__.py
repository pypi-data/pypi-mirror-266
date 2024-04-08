__version__ = __VERISON__ = "0.0.2"
import os
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
    console = Console()

    def chat(c):
        r = requests.post("http://nc.turing.fun:8228/api/nc", 
                      json={'chat': c}).content.decode('utf8')
        content = json.loads(r)['data']
        return content

    console.print(f"({prompt}) 正在执行...")

    content = chat(prompt)
    cmd = "\n".join(re.findall("```shell\n([\s\S]*?)```", 
                             content))



    md = Markdown(content)
    console.print(md)
    sure = Prompt.ask("Exec these commands?", choices=["Yes(Default)", "No", "N", "n"], default="Yes")
    if sure == 'Yes':
        os.system(cmd)

