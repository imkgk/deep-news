import os
import openai
from pathlib import Path
from frontmatter import load
from glob import glob
from datetime import datetime
import re

def update_index_html(articles_dir: Path):
    """更新首页的文章列表"""
    # 获取所有生成的文章
    articles = sorted(articles_dir.glob('*.md'), key=lambda x: x.stat().st_mtime, reverse=True)

    # 生成文章列表 HTML
    articles_html = []
    for article in articles:
        # 读取文章frontmatter获取标题
        post = load(article)
        title = post.get('title', article.stem)
        date = datetime.fromtimestamp(article.stat().st_mtime).strftime('%Y-%m-%d')

        # 生成文章链接
        link = f'<li><span class="date">{date}</span> <a href="articles/{article.name}">{title}</a></li>'
        articles_html.append(link)

    articles_list = '\n'.join(articles_html)

    # 更新 index.html
    index_path = Path('index.html')
    if not index_path.exists():
        # 如果不存在则创建基础模板
        index_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>深度新闻</title>
    <style>
        .date {{ color: #666; margin-right: 1em; }}
        ul {{ list-style: none; padding: 0; }}
        li {{ margin: 1em 0; }}
    </style>
</head>
<body>
    <h1>文章列表</h1>
    <ul>
        {articles_list}
    </ul>
</body>
</html>'''
        index_path.write_text(index_content)
    else:
        # 如果存在则更新文章列表部分
        content = index_path.read_text()
        # 在 <ul> 和 </ul> 之间更新内容
        content = re.sub(
            r'(<ul>).*?(</ul>)',
            f'\\1\n        {articles_list}\n    \\2',
            content,
            flags=re.DOTALL
        )
        index_path.write_text(content)

def generate_articles(files_pattern: str):
    # 初始化自定义 OpenAI 客户端
    client = openai.OpenAI(
        base_url="https://api.302.ai/v1",
        api_key=os.environ["OPENAI_API_KEY"]
    )

    # 直接使用 glob 处理模式
    files = glob(files_pattern)

    if not files:
        print(f"警告：没有找到匹配的文件：{files_pattern}")
        # 列出 topics 目录内容以便调试
        topics_dir = Path("topics")
        if topics_dir.exists():
            print("topics 目录中的文件：")
            for f in topics_dir.glob("*.md"):
                print(f"  - {f.name}")
        return

    print(f"找到以下文件：")
    for f in files:
        print(f"  - {f}")

    # 处理所有匹配的文件
    for file_path in files:
        process_single_file(Path(file_path), client)

    # 更新首页
    update_index_html(Path("articles"))

def process_single_file(topic_path: Path, client: openai.OpenAI):
    try:
        # 读取主题文件
        post = load(topic_path)
        
        # 构建自定义提示词
        prompt = f"""根据以下需求撰写专业 Markdown 格式文章：
        
        {post.content}
        
        要求：
        - 使用中文二级、三级标题
        - 包含技术细节和示例
        - 输出格式规范
        """

        # 调用自定义 API 端点
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )

        # 保存生成结果
        output_dir = Path("articles")
        output_dir.mkdir(exist_ok=True)
        
        output_path = output_dir / f"{topic_path.stem}-generated.md"
        with open(output_path, "w") as f:
            f.write(response.choices[0].message.content)
            
        print(f"成功生成：{output_path}")

    except Exception as e:
        print(f"处理 {topic_path} 失败：{str(e)}")
        raise  # 抛出异常使 Action 失败

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("请提供要处理的文件模式")
        sys.exit(1)
        
    # 直接使用命令行参数中的文件模式
    generate_articles(sys.argv[1])