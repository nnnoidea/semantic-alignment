"""Structural and approximate geometry checks for any generated layered report.

No browser, source-truth judgment, screenshots, hashes or persistent check cache.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote
import re,xml.etree.ElementTree as ET

class Index(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=[];self.links=[];self.report_links=[];self.keys=[];self.views=[];self.panels={};self.mini_states={};self.violations=set();self.references={};self.panel_links={};self.article=None;self.in_dt=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if a.get('href','').startswith('#'):self.links.append(unquote(a['href'][1:]))
        href=a.get('href','')
        if href.split('#',1)[0] in ('index.html','summary.html'):self.report_links.append(href.partition('#')[::2])
        if 'data-key' in a:self.keys.append(a['data-key'])
        if tag=='section' and a.get('class')=='flow-level':self.views.append(a)
        if tag=='article' and a.get('class')=='inspect-content':self.article=a['id'];self.panels[self.article]=[]
        if self.article and 'constraint-alert' in a.get('class','').split():self.violations.add(self.article)
        if self.article and tag=='a' and a.get('href','').startswith('#'):
            target=unquote(a['href'][1:]);self.panel_links.setdefault(self.article,set()).add(target)
            if a.get('class')=='detail-reference':self.references.setdefault(self.article,set()).add(target)
        if self.article and 'data-mini-select' in a:
            states=self.mini_states.setdefault(self.article,set())
            if a.get('data-meaning') in ('unspecified','unreviewed'):states.add(a['data-meaning'])
            if a.get('data-pending')=='true':states.add('pending')
        if tag=='dt' and self.article:self.in_dt=True;self.panels[self.article].append('')
    def handle_endtag(self,tag):
        if tag=='article':self.article=None
        if tag=='dt':self.in_dt=False
    def handle_data(self,data):
        if self.article and self.in_dt:self.panels[self.article][-1]+=data

def overlap(a,b):
    x,y,w,h=a;xx,yy,ww,hh=b
    return min(x+w,xx+ww)>max(x,xx)+2 and min(y+h,yy+hh)>max(y,yy)+2

def crosses(p,q,box):
    x,y,w,h=box;left,right=x+2,x+w-2;top,bottom=y+2,y+h-2
    if p[0]==q[0]:return left<p[0]<right and min(p[1],q[1])<bottom and max(p[1],q[1])>top
    if p[1]==q[1]:return top<p[1]<bottom and min(p[0],q[0])<right and max(p[0],q[0])>left
    return False  # Approximate checker: authored diagonal curves still need inspection.

def text_boxes(root):
    for text in root.iter('{http://www.w3.org/2000/svg}text'):
        size=float(text.get('font-size',20));anchor=text.get('text-anchor','start');x=float(text.get('x',0));y=float(text.get('y',0))
        lines=list(text) or [text]
        for line in lines:
            x=float(line.get('x',x));y+=float(line.get('dy',0))
            label=''.join(line.itertext());width=sum(size*(1 if ord(c)>255 else .57) for c in label)
            left=x-width/2 if anchor=='middle' else x-width if anchor=='end' else x
            yield (left,y-size,width,size*1.2),label

def check_report(path):
    html=Path(path).read_text();index=Index();index.feed(html);errors=[]
    def need(ok,message):
        if not ok:errors.append(message)
    need(len(index.ids)==len(set(index.ids)),'Duplicate HTML/SVG IDs')
    need(len(index.keys)==len(set(index.keys)),'Duplicate selectable keys')
    targets=set(index.ids)|set(index.keys)
    for link in set(index.links):need(link in targets,'Broken local reference: '+link)
    expected={ 'inspect-'+key for key in index.keys }
    need(expected==set(index.panels),'Node/relation inspectors are missing or orphaned')
    for key,fields in index.panels.items():
        need(fields==['用户要求','实际做法','影响与取舍'],'Invalid detail fields: '+key)
    for source,targets in index.references.items():
        for target in targets:
            if 'inspect-'+target in index.panels:
                need(source[len('inspect-'):] in index.panel_links.get('inspect-'+target,set()),'Missing return reference: '+target+' -> '+source[len('inspect-'):])
    views={v['data-view']:v for v in index.views}
    roots=[v for v in index.views if not v.get('data-owner')]
    need(len(roots)==1,'Expected one root view')
    need(sum('hidden' not in v for v in index.views)==1,'Initially show only the root')
    key_view={}
    trees=[]
    for fragment in re.findall(r'<svg\b.*?</svg>',html,re.S):
        tree=ET.fromstring(fragment);trees.append(tree)
        for n in tree.iter():
            if n.get('data-key'):key_view[n.get('data-key')]=n.get('data-key').split('--',1)[0]
    expanded={};visible_states={}
    for tree in trees:
        width,height=map(float,tree.get('viewBox').split()[2:]);ids={n.get('id') for n in tree.iter() if n.get('id')}
        nodes={n.get('data-key'):tuple(map(float,n.get('data-box').split(','))) for n in tree.iter() if n.get('class')=='node architecture-node'}
        contexts={f'context-{i}':tuple(map(float,n.get('data-box').split(','))) for i,n in enumerate(tree.iter()) if n.get('class')=='upper-context' and n.get('data-box')}
        boxes={**nodes,**contexts}
        boundary=next((n for n in tree.iter() if n.get('class')=='expansion-boundary'),None)
        if boundary is not None:
            fx,fy,fw,fh=map(float,boundary.get('data-box').split(','))
            for key,(x,y,w,h) in nodes.items():need(x>=fx and y>=fy and x+w<=fx+fw and y+h<=fy+fh,'Internal node outside parent boundary: '+key)
        for key,box in boxes.items():
            x,y,w,h=box;need(x>=0 and y>=0 and x+w<=width and y+h<=height,'Node outside canvas: '+key)
        items=list(boxes.items())
        for i,(a,box) in enumerate(items):
            for b,other in items[i+1:]:need(not overlap(box,other),'Overlapping nodes: '+a+' / '+b)
        for n in tree.iter():
            if n.get('data-key'):
                visible_states[n.get('data-key')]={m.get('data-meaning') for m in n.iter() if m.get('data-meaning')}
            if n.get('data-child'):
                child=n.get('data-child');need(child not in expanded,'Child has multiple expansion owners: '+child);expanded[child]=n.get('data-key')
            for value in n.attrib.values():
                for ref in re.findall(r'url\(#([^)]*)\)',value):need(ref in ids,'Broken SVG marker: '+ref)
            if n.get('class')=='edge-line':
                edge_path=n.get('d','')
                # Renderer emits absolute M/L polylines. Do not mistake control
                # coordinates from arbitrary curves for their actual bounds.
                if re.search(r'[A-KN-Za-kn-z]',re.sub(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?','',edge_path)):continue
                coords=[float(v) for v in re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?',edge_path)];points=list(zip(coords[::2],coords[1::2]))
                for x,y in points:need(0<=x<=width and 0<=y<=height,'Connector outside canvas: '+str((x,y)))
                for p,q in zip(points,points[1:]):
                    for key,box in boxes.items():need(not crosses(p,q,box),'Connector crosses node: '+key)
            if n.get('class')=='node relation-node':
                for box,label in text_boxes(n):
                    for key,node in boxes.items():need(not overlap(box,node),'Relation label overlaps node/context: '+label+' / '+key)
        for (x,y,w,h),label in text_boxes(tree):need(x>=-6 and y>=-6 and x+w<=width+6 and y+h<=height+6,'Text outside canvas: '+label)
    for key,v in views.items():
        depth=int(v['data-depth']);owner=v.get('data-owner');need(1<=depth<=3,'Invalid depth: '+key)
        if owner:
            parent=key_view.get(owner);need(expanded.get(key)==owner,'Expansion owner mismatch: '+key)
            need(parent in views and int(views[parent]['data-depth'])+1==depth,'Invalid ancestor depth: '+key)
        else:need(depth==1 and 'hidden' not in v,'Root visibility/depth mismatch')
    need(set(expanded)=={k for k,v in views.items() if v.get('data-owner')},'Missing child view')
    for key,states in visible_states.items():
        need(index.mini_states.get('inspect-'+key,set())<=states,'Detail states missing from outer markers: '+key)
        if 'inspect-'+key in index.violations:need('violation' in states,'Restriction violation missing from graph: '+key)
    for child,owner in expanded.items():
        child_states=set().union(*(states for key,states in visible_states.items() if key_view.get(key)==child))
        need(child_states<=visible_states.get(owner,set()),'Descendant states missing from parent markers: '+owner)
    if any(file=='summary.html' for file,_ in index.report_links):
        summary_path=Path(path).with_name('summary.html')
        need(summary_path.is_file(),'Missing summary.html')
        if summary_path.is_file():
            summary=Index();summary.feed(summary_path.read_text())
            need(len(summary.ids)==len(set(summary.ids)),'Duplicate summary IDs')
            for link in summary.links:need(link in summary.ids,'Broken summary section: '+link)
            report_targets={'index.html':set(index.ids)|set(index.keys),'summary.html':set(summary.ids)}
            for file,link in index.report_links+summary.report_links:
                need(not link or unquote(link) in report_targets[file],'Broken report page reference: '+file+'#'+link)
            need(any(file=='index.html' for file,_ in summary.report_links),'Summary lacks a detailed-report link')
    if errors:raise ValueError('Report check failed:\n'+'\n'.join(dict.fromkeys(errors)))
    return {'views':len(views),'details':len(index.panels),'structure':'passed','geometry':'basic bounds/overlap/orthogonal-path checks passed; visual inspection still required'}

if __name__=='__main__':
    import sys
    print(check_report(sys.argv[1]))
