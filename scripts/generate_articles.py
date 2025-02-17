import os
import openai
from pathlib import Path
from frontmatter import load
from glob import glob

def generate_articles(files_pattern: str):
    # 初始化自定义 OpenAI 客户端
    client = openai.OpenAI(
        base_url="https://api.302.ai",  # 自定义 API 地址
        api_key=os.environ["OPENAI_API_KEY"]         # 从环境变量获取密钥
    )

    # 使用 glob 展开文件模式
    files = glob(files_pattern)
    if not files:
        print(f"警告：没有找到匹配的文件：{files_pattern}")
        return

    # 处理所有匹配的文件
    for file_path in files:
        process_single_file(Path(file_path), client)

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
            model=os.environ.get("MODEL_NAME", "gpt-4"),  # 可配置模型名称
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
        print("请提供要处理的文件列表")
        sys.exit(1)
        
    generate_articles(' '.join(sys.argv[1:]))