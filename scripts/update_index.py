from pathlib import Path
from frontmatter import load
from datetime import datetime
import re

def update_index_html():
    """更新首页的文章列表"""
    articles_dir = Path("articles")
    if not articles_dir.exists():
        print("articles 目录不存在")
        return

    # 获取所有文章
    articles = sorted(articles_dir.glob('*.md'), key=lambda x: x.stat().st_mtime, reverse=True)
    
    # 生成文章列表
    articles_html = []
    for article in articles:
        post = load(article)
        title = post.get('title', article.stem)
        date = datetime.fromtimestamp(article.stat().st_mtime).strftime('%Y-%m-%d')
        link = f'<li><span class="date">{date}</span> <a href="articles/{article.name}">{title}</a></li>'
        articles_html.append(link)

    articles_list = '\n'.join(articles_html)
    
    # 创建或更新 index.html
    index_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>深度新闻</title>
    <style>
        body {{
            max-width: 800px;
            margin: 0 auto;
            padding: 2em;
            font-family: -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
        }}
        .date {{ 
            color: #666; 
            margin-right: 1em;
            display: inline-block;
            width: 100px;
        }}
        ul {{ 
            list-style: none; 
            padding: 0; 
        }}
        li {{ 
            margin: 1em 0;
            padding: 0.5em;
            border-bottom: 1px solid #f5f5f5;
        }}
        a {{
            color: #0366d6;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <h1>文章列表</h1>
    <ul>
        {articles_list}
    </ul>
</body>
</html>'''

    index_path = Path('index.html')
    index_path.write_text(index_content)
    print("已更新 index.html")

if __name__ == "__main__":
    update_index_html()