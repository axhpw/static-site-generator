import os
import sys
import markdown
import frontmatter
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

CONTENT_DIR = 'content'
OUTPUT_DIR = 'output'
TEMPLATE_DIR = 'templates'

force = '--force' in sys.argv

print(f"force rebuild: {force}")

# initialize jinja2
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
template = env.get_template('base.html')

def mdToHtml(md_content):
    """Convert markdown text to html"""
    html = markdown.markdown(md_content, extensions=['extra', 'codehilite', 'pymdownx.tasklist' ])
    return html

def getOutputPath(md_path):
    rel = os.path.relpath(md_path, CONTENT_DIR)
    slug, _ = os.path.splitext(rel)

    if os.path.basename(slug) == 'index':
        parent = os.path.dirname(slug)
        if parent == '':
            return os.path.join(OUTPUT_DIR, 'index.html')
        return os.path.join(OUTPUT_DIR, parent, 'index.html')
    
    return os.path.join(OUTPUT_DIR, slug, 'index.html')

def buildSite():
    posts = []

    for root, dirs, files in os.walk(CONTENT_DIR):
        for file in files:
            if file.endswith('.md'):
                md_path = os.path.join(root, file)
                # rel_path = os.path.relpath(md_path, CONTENT_DIR)
                # output_path = os.path.join(OUTPUT_DIR, rel_path)
                # output_path = output_path.replace('.md', '.html')
                output_path = getOutputPath(md_path)

                # Make sure output subdirectories exist
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                if not force:
                # Incremental build check
                    md_mtime = os.path.exists(md_path)
                    if os.path.exists(output_path):
                        html_mtime = os.path.getmtime(output_path)
                        if html_mtime >= md_mtime:
                            print(f"Skipping unchanged: {output_path}")
                            continue    # Skip unchanged file

                print(f"Generating {output_path}")

                # read and convert
                with open(md_path, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)

                html_content = markdown.markdown(post.content, extensions=['extra', 'codehilite', 'pymdownx.tasklist'])

                # format post date
                date_str = post.get('date', '')
                date_obj = None

                if date_str:
                    try:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    except ValueError:
                        print(f"Invalid date format: {date_str}")

                # Pick a template
                layout = post.get('layout', 'default')
                template = env.get_template(f"{layout}.html")

                rendered_html = template.render(
                    title=post.get('title', 'Untitled'),
                    content=html_content,
                    metadata=post.metadata,
                    date_obj=date_obj
                )

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(rendered_html)
                print(f"Generated {output_path}")

if __name__ == '__main__':
    buildSite()            