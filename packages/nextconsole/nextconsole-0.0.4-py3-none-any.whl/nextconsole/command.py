import os
import json

# import requests
# response = requests.post("http://192.168.6.182:8228/api/nc", data=json.dumps({"chat":"部署nginx"}), headers={"Content-Type": "application/json"}, stream=True)


# strs = []
# last_lines = 0
# for c in response.iter_content(chunk_size=10):
#     c = c.decode()
#     for _ in range(last_lines):
#         print(u'\u001b[1A', end='')
#     if c is not None:
#         strs.append(c)
#     md = Markdown("".join(strs))
#     console.print(md, end='')
#     if len(md.parsed) > 0:
#         last_lines = md.parsed[0].map[1] + 1

        
        
        
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

    # def chat(c):
    #     r = requests.post("http://nc.turing.fun:8228/api/nc", 
    #                   json={'chat': c}).content.decode('utf8')
    #     content = json.loads(r)['data']
    #     return content

    # console.print(f"({prompt}) 正在执行...")
    content = ""
    strs = []
    last_lines = 0
    response = requests.post("http://nc.turing.fun:8228/api/nc", data=json.dumps({"chat": prompt}), headers={"Content-Type": "application/json"}, stream=True)
    
    for c in response.iter_content(chunk_size=10):
        c = c.decode()

        if c is not None:
            strs.append(c)
        content = "".join(strs)
        md = Markdown(content)
        console.print(md, end='')
        if len(md.parsed) > 0:
            last_lines = md.parsed[0].map[1] + 1
        for _ in range(last_lines):
            print(u'\u001b[1A', end='')


    # content = chat(prompt)
    cmd = "\n".join(re.findall("```shell\n([\s\S]*?)```", 
                             content))



    md = Markdown(content)
    console.print(md)
    sure = Prompt.ask("Exec these commands?", choices=["Yes(Default)", "No", "N", "n"], default="Yes")
    if sure == 'Yes':
        os.system(cmd)

if __name__ == "__main__":
    cmd()