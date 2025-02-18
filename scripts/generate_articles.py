import os
import re
import sys
import openai
from datetime import datetime
from pathlib import Path
from frontmatter import load
from glob import glob

def generate_articles(files_pattern: str):
    # 初始化 OpenAI 客户端
    client = openai.OpenAI(
        base_url="https://api.302.ai/v1",
        api_key=os.environ["OPENAI_API_KEY"]
    )

    # 处理文件
    files = glob(files_pattern)
    if not files:
        print(f"警告：没有找到匹配的文件：{files_pattern}")
        return

    print(f"找到以下文件：")
    for f in files:
        print(f"  - {f}")

    # 处理所有匹配的文件
    for file_path in files:
        process_single_file(Path(file_path), client)

def process_single_file(topic_path: Path, client: openai.OpenAI):
    try:
        post = load(topic_path)
        prompt = f"""根据以下需求撰写专业 Markdown 格式文章：
        # {topic_path.stem}
        {post.content}

        要求：
        - 使用中文二级、三级标题
        - 包含技术细节和示例
        - 输出格式规范
        - 只输出 markdown 的内容，不要开头和结尾的 markdown 格式标签
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else topic_path.stem
        
        output_dir = Path("_posts")
        output_dir.mkdir(exist_ok=True)
        
        output_path = output_dir / f"{topic_path.stem}-generated.md"
        with open(output_path, "w") as f:
            frontmatter = f"""---
title: "{title}"
date: {datetime.now().strftime('%Y-%m-%d')}
description: Generated from {topic_path.name}
---

"""
            f.write(frontmatter)
            f.write(content)
            
        print(f"成功生成：{output_path}")

    except Exception as e:
        print(f"处理 {topic_path} 失败：{str(e)}")
        raise

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("请提供要处理的文件模式")
        sys.exit(1)
    generate_articles(sys.argv[1])