"""Render a demo's public report from local content and reviewed images."""
from pathlib import Path
import argparse,html,json
ROOT=Path(__file__).resolve().parents[1]
def render(demo):
    folder=ROOT/'demos'/demo/'reports';data=json.loads((folder/'report.json').read_text())
    content=[]
    for i,section in enumerate(data['sections'],1):
        content.append(f'<section><h2><span class="num">{i:02}</span><br>{html.escape(section["title"])}</h2>')
        for text in section.get('paragraphs',[]):content.append('<p>'+html.escape(text)+'</p>')
        for image in section.get('images',[]):content.append('<figure><img src="'+html.escape(image['src'],quote=True)+'" alt="'+html.escape(image['caption'],quote=True)+'"><figcaption>'+html.escape(image['caption'])+'</figcaption></figure>')
        content.append('</section>')
    template=(ROOT/'templates/report.html').read_text()
    for key,value in {'title':html.escape(data['title']),'dek':html.escape(data['dek']),'body':''.join(content),'footer':'<a href="../README.md">Demo setup and source</a> · <a href="../LEARNINGS.md">Recorded lessons</a>', 'css':(ROOT/'templates/report.css').read_text()}.items():template=template.replace('{{'+key+'}}',value)
    (folder/'index.html').write_text(template,encoding='utf8')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('demo',choices=['fury','i6-astra']);render(p.parse_args().demo)
