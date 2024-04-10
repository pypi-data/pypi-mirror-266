import toml

def new(path,project_name):
    pyproject_toml_content = {
        "[build-system]": {
            "requires": ["setuptools"],
            "build-backend": "setuptools.build_meta"
        },
        "[project]": {
            "name": project_name,
            "version": "0.0.1",
            "requires-python": ">=3.12",
            "authors": [{"name": "NotForund", "email": "example@email.com"}],
            "description": "A template python project",
            "readme": "README.md",
            "license": {"file": "LICENSE"},
        }
    }
    # 创建并写入pyproject.toml文件
    with open(f"{path}/{project_name}/pyproject.toml", "w") as f:
        toml.dump(pyproject_toml_content, f)
    print(f"成功!")

def init(path):
    # 询问用户输入项目名称
    project_name = input("请输入项目名称：")
    # 询问用户输入项目版本
    version = input("请输入项目版本（例如：0.0.1）：")
    # 询问用户输入Python最低版本要求
    requires_python = input("请输入项目所需的最低Python版本（例如：>=3.12）：")
    # 询问用户输入作者信息
    authors = []
    while True:
        author_name = input("请输入作者姓名（若无更多作者，请直接回车）：")
        if not author_name:
            break
        email = input(f"请输入{author_name}的电子邮件地址：")
        authors.append({"name": author_name, "email": email})
    # 询问用户输入项目描述
    description = input("请输入项目描述：")
    # 询问用户是否包含自定义README文件
    has_readme = input("项目中是否包含README.md文件？（yes/no）：").lower() == "yes"
    readme = "README.md" if has_readme else None
    # 询问用户是否包含自定义LICENSE文件
    has_license = input("项目中是否包含LICENSE文件？（yes/no）：").lower() == "yes"
    license_file = "LICENSE" if has_license else None
    # 询问用户输入关键词
    keywords = input("请输入项目的关键词（以逗号分隔）：").split(",")
    # 询问用户输入脚本信息
    scripts = {}
    while True:
        script_name = input("请输入脚本名称（若无更多脚本，请直接回车）：")
        if not script_name:
            break
        entry_point = input(f"请输入{script_name}对应的入口点（格式：模块名:函数名）：")
        scripts[script_name] = entry_point
    # 构建pyproject.toml内容
    pyproject_toml_content = {
        "[build-system]": {
            "requires": ["setuptools"],
            "build-backend": "setuptools.build_meta"
        },
        "[project]": {
            "name": project_name,
            "version": version,
            "requires-python": requires_python,
            "authors": authors,
            "description": description,
            "readme": readme,
            "license": {"file": license_file} if license_file else None,
            "keywords": keywords,

            "scripts": scripts
        }
    }
    # 创建并写入pyproject.toml文件
    with open(f"{path}/{project_name}/pyproject.toml", "w") as f:
        toml.dump(pyproject_toml_content, f)
    print(f"成功！")