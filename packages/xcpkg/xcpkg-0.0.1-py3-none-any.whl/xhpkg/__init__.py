import sys,os
from . import init_project
def main():
    # 防盗版
    if sys.argv[1] != "xcpkg":
        print("您正在使用非正式版或盗版的xcpkg，请使用正式版xcpkg！")
        key= input()
        if key != "xcabcd":
            exit()
        else:
            pass
    # 判断功能
    if sys.argv[2] == "help":
        help = """
        xcpkg init 初始化项目\n
        xcpkg new [项目名] 新建项目
        """
        print(help)
    elif sys.argv[2] == "init":
        init_project.init(os.getcwd())
    elif sys.argv[2] == "new":
        init_project.new(os.getcwd(),sys.argv[3])
    else:
        print("调用方式错误！")