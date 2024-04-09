
import platform
import subprocess
def is_brew_install():
    try:
        result = subprocess.run(["brew", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # 如果命令执行成功（返回码为0），则表示brew已安装
        if result.returncode == 0:
            return True
        else:
            return False
    except OSError as e:
        # 如果无法执行brew命令，可能是因为未安装或路径问题
        return False

def is_docker_install():
    try:
        result = subprocess.run(['docker', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if 'docker' in result.stdout.lower():
            return True
        else:
            return False 
    except Exception as e:
        return False
        
        
def get_system_name():
    # 获取操作系统名称
    os_name = platform.system()
    
    # 根据操作系统名称返回特定的值
    if os_name == 'Darwin':
        return 'macos'
    elif os_name == 'Linux':
        # 获取Linux发行版名称
        linux_dist = subprocess.check_output(['lsb_release', '-i']).decode().strip()
        if 'Ubuntu' in linux_dist or 'Debian' in linux_dist:
            return 'debian'
        elif 'CentOS' in linux_dist:
            return 'centos'
        else:
            return 'linux'  # 对于其他Linux发行版，统一返回'linux'
    elif os_name == 'Windows':
        return 'windows'
    else:
        return 'unknown'

    
import platform
def get_python_version():
    return platform.python_version()


def envinfo():
    return {
      'python_version':  get_python_version(),
       'system_name': get_system_name(),
        'is_docker_install': is_docker_install(),
        'is_brew_install': is_brew_install()
    }

# 打印简化的操作系统名称
if __name__ == "__main__":
    print({
      'python_version':  get_python_version(),
       'system_name': get_system_name(),
        'is_docker_install': is_docker_install(),
        'is_brew_install': is_brew_install()
    })