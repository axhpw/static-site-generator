import os
import sys
import markdown
import frontmatter
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from collections import defaultdict

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

def getUrl(md_path):
    rel = os.path.relpath(md_path, CONTENT_DIR)
    slug, _ = os.path.splitext(rel)
    if os.path.basename(slug) == 'index':
        parent = os.path.dirname(slug)
        return f"/{parent}/" if parent else "/"
    return f"/{slug}/"

def buildAndCollect():
    dir_posts = defaultdict(list)
    has_index_md = set()

    for root, _, files in os.walk(CONTENT_DIR):
        for fname in files:
            if not fname.endswith('.md'):
                continue
            md_path = os.path.join(root, fname)
            rel_dir = os.path.relpath(root, CONTENT_DIR)

            post = frontmatter.load(md_path)
            
            # Assign Metadata
            title = post.get('title', 'Untitled')
            date_obj = None
            if 'date'  in post.metadata:
                date_obj = datetime.strptime(post['date'], '%Y-%m-%d')

            if fname == 'index.md':
                has_index_md.add(rel_dir)

            # Render HTML
            html = mdToHtml(post.content)
            layout = post.get('layout','default')
            template = env.get_template(f"{layout}.html")
            rendered = template.render(
                title=title,
                content=html,
                metadata=post.metadata,
                date_obj=date_obj,
                stylesheet='/style.css'
            )

            # Write out
            out_path = getOutputPath(md_path)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            # Incremental Build
            if not force and os.path.exists(out_path):
                if os.path.getmtime(out_path) >= os.path.getmtime(md_path):
                    print(f"Skipping {out_path}")
                else:
                    open(out_path,'w',encoding='utf-8').write(rendered)
                    print(f"Rebuilt {out_path}")
            else:
                open(out_path,'w',encoding='utf-8').write(rendered)
                print(f"Generated {out_path}")

            # Collect Metadata
            if fname != 'index.md':
                dir_posts[rel_dir].append({
                    'title': title,
                    'date': date_obj,
                    'url': getUrl(md_path)
                })
    return dir_posts, has_index_md

def generateIndexes(dir_posts, has_index_md):
    for rel_dir, posts in dir_posts.items():
        if rel_dir in has_index_md:
            continue

        # sort newest first
        posts.sort(key=lambda p: p['date'] or datetime.min, reverse =True)

        out_dir = os.path.join(OUTPUT_DIR, rel_dir)
        os.makedirs(out_dir, exist_ok=True)
        index_path = os.path.join(out_dir, 'index.html')

        template = env.get_template('posts.html')
        rendered = template.render(
            title = f"Index of /{rel_dir}" if rel_dir else "Home",
            posts = posts,
            stylesheet = '/style.css'
        )
        open(index_path, 'w', encoding='utf-8').write(rendered)
        print(f"Generated index: {index_path}")

if __name__ == '__main__':
    dir_posts, has_index_md = buildAndCollect()
    generateIndexes(dir_posts, has_index_md)