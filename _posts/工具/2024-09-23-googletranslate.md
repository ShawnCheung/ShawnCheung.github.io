---
layout: post
title: 使用googletranslate api翻译文本
date: 2024-09-23 14:53 +0800
categories: [工具, 谷歌翻译]
tags: [工具]
---
1. 安装googletrans库
```bash
pip install googletrans==3.1.0a0
```

2. 使用googletranslate api翻译文本
```python
from googletrans import Translator

translator = Translator()
translation = translator.translate(text, dest='zh-CN')
en_text = translation.text
```
