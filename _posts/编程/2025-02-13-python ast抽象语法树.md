---
layout: post
title: Python 文件的抽象语法树 AST
date: 2025-02-13 21:55 +0800
categories: [编程, Python]
tags: [Python]
---

如果你想对一个 Python 文件进行扫描，提取其中的类和方法接口，可以使用 Python 的 ast（抽象语法树）模块。ast 可以让你解析 Python 代码并提取其中的类、函数和方法定义等信息。

使用 ast 模块获取类和方法接口
ast 模块可以将 Python 代码解析为一个抽象语法树，遍历这个树结构就可以提取到类和方法的定义。具体步骤如下：

1. 读取 Python 文件内容。
2. 将文件内容解析为抽象语法树。
3. 遍历语法树，提取出类和方法（函数）信息。


创建一个python文件命名为：ast.py
```python3
import ast
import argparse


def scan_python_file(file_path: str):
    with open(file_path, "r", encoding="utf-8") as file:
        tree = ast.parse(file.read())  # 解析文件内容，生成 AST
    
    # 存储类和方法信息
    classes = []
    methods = []
    
    # 遍历 AST
    for node in ast.walk(tree):
        # 如果是类定义
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
            
            # 查找类中的方法
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    methods.append((node.name, item.name))
    
    return classes, methods

if __name__ == "__main__":
    # 使用示例
    parser = argparse.ArgumentParser(description="这是一个命令行工具")
    parser.add_argument("-f", "--file_path", type=str, help="待解析文件路径")
    args = parser.parse_args()

    file_path = args.file_path
    classes, methods = scan_python_file(file_path)

    print("Classes:", classes)
    print("Methods:")
    for cls, method in methods:
        print(f"Class: {cls}, Method: {method}")
```

使用如下命令对相应的python文件进行ast语法解析：
```bash
python3 ast.py -f ./test.py
```
