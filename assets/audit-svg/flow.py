"""Small layout presets + offline report assembly. Inputs are report-local Python.

python flow.py report.py output-directory
python flow.py --check output-directory/index.html
report.py defines REPORT; loading it executes trusted local Python, not Markdown.
"""
from pathlib import Path
import argparse,runpy
from architecture import Scene,module_html
from semantic_template import detail_html,detail_cells,specification_state,pending_state,pending_label,violation_state,cell_html,check_perspective,summary_findings,PROJECT
from components import esc,wrap
from layers import Expansion,validate,write_layers
from check_report import check_report,crosses

def grid(layout):
    """Slots describe visual placement only. Edges are always supplied separately."""
    kind=layout['kind'];rows=[];placed={}
    def put(key,col,row):
        if key is None:return
        if key in placed:raise ValueError('Node appears twice in layout: '+key)
        placed[key]=(col,row)
    if kind=='sequence':rows=[(0,layout['order'])]
    elif kind=='branch':
        branches=layout['branches']
        if len(branches)<2 or not any(branches):raise ValueError('Branch layout needs at least two paths and one internal node; an empty path is a bypass')
        put(layout['decision'],0,(len(branches)-1)/2)
        for i,branch in enumerate(branches):
            for j,key in enumerate(branch):put(key,j+1,i)
        put(layout['merge'],max(map(len,branches))+1,(len(branches)-1)/2)
    elif kind=='wait':
        rows=[(0,layout['main']),(1,[None]*layout.get('worker_start',1)+layout['worker'])]
    elif kind=='interaction':rows=list(enumerate(layout['lanes']))
    else:raise ValueError('Unknown layout: '+kind)
    for row,keys in rows:
        for col,key in enumerate(keys):put(key,col,row)
    return placed

def text_width(text,size):return sum(size*(1 if ord(c)>255 else .57) for c in text)

def arrangement(spec,child=False):
    nodes=spec['nodes'];slots=grid(spec['layout'])
    if not nodes or set(slots)!=set(nodes):raise ValueError('Layout must place every node exactly once: '+spec['title'])
    width=max(220,min(320,max(text_width(n['label'],20)/.7+20 if n.get('shape')=='decision' else text_width(n['label'],20)+40 for n in nodes.values())))
    height=max(80,max(len(wrap(n['label'],width*.7 if n.get('shape')=='decision' else width-36,20))*27+44 for n in nodes.values()))
    if any(n.get('shape')=='decision' for n in nodes.values()):height=max(120,height)
    gap=max(240,max((text_width(e.get('label',''),15)+32 for e in spec.get('edges',[])),default=0))
    incoming=max((text_width('入 · '+h['label'],13)+30 for h in spec.get('handoffs',[]) if h['direction']=='in'),default=90)
    x0=240+max(260,incoming) if child else 80;y0=175 if child else 125
    boxes={k:(x0+c*(width+gap),y0+r*(height+120),width,height) for k,(c,r) in slots.items()}
    for key,box in spec.get('positions',{}).items():
        if key not in boxes or len(box)!=4:raise ValueError('Invalid position override: '+key)
        boxes[key]=tuple(box)
    return boxes

def route(boxes,a,b,track=0):
    """Common local orthogonal paths; return/skip edges get a lower corridor."""
    ax,ay,aw,ah=boxes[a];bx,by,bw,bh=boxes[b]
    ac=(ax+aw/2,ay+ah/2);bc=(bx+bw/2,by+bh/2)
    if abs(ac[1]-bc[1])<1 and bx>=ax+aw:
        blocking=any(ax+aw<x<bx and abs(y-ay)<ah for k,(x,y,w,h) in boxes.items() if k not in (a,b))
        if not blocking:return dict(ap='r',bp='l',via=[],at=((ax+aw+bx)/2,ac[1]-14))
    if abs(ac[0]-bc[0])<1 and a!=b:
        low,high=sorted((ay,by))
        blocking=any(low<y<high and x<ac[0]<x+w for k,(x,y,w,h) in boxes.items() if k not in (a,b))
        if not blocking:
            down=by>ay
            return dict(ap='b' if down else 't',bp='t' if down else 'b',via=[],at=(ac[0],(max(ay,by)+min(ay+ah,by+bh))/2))
    if bx>=ax+aw and ay!=by:
        mid=(ax+aw+bx)/2
        return dict(ap='r',bp='l',via=[(mid,ac[1]),(mid,bc[1])],at=(mid,(ac[1]+bc[1])/2))
    y=max(y+h for x,y,w,h in boxes.values())+70+track*36
    if a==b:
        return dict(ap='r',bp='b',via=[(ax+aw+45,ac[1]),(ax+aw+45,y),(ac[0],y)],at=(ax+aw+45,y-12))
    return dict(ap='b',bp='b',via=[(ac[0],y),(bc[0],y)],at=((ac[0]+bc[0])/2,y-12))

def build_report(report,out):
    """Render supplied meaning, not inferred user intent; check the emitted artifact."""
    specs=report['views'];root=report['root'];data=report['data'];perspective=data.get('perspective')
    check_perspective(perspective)
    children={k:{node:n['child'] for node,n in s['nodes'].items() if n.get('child')} for k,s in specs.items()}
    scenes={};boxes={};findings=[]
    def remember(view,target,title,row):
        entries=summary_findings(row)
        if entries:
            values=detail_cells(row)
            context={key:{field:values[key].get(field,'') for field in ('origin','source')} for key in ('specified','choice')}
            context['impact']=values['impact']
            context['pending_label']=pending_label(row)
            findings.append(dict(view=specs[view]['title'],target=view+'--'+target,title=title,findings=entries,context=context))
    for key,spec in specs.items():
        boxes[key]=arrangement(spec,key!=root)
        s=Scene(spec['title']);s.level_label=spec.get('level_label');scenes[key]=s
        # Establish keys before validating hierarchy; drawing happens afterwards.
        s.bounds=boxes[key].copy();s.labels={k:n['label'] for k,n in spec['nodes'].items()}
    order,depth,owners=validate(scenes,children,root)
    source=['<h2>项目语义</h2>'+''.join('<h3>'+label+'</h3>'+cell_html(data.get('project',{}).get(k)) for k,label in PROJECT)]
    for key in order:
        spec=specs[key];s=scenes[key];b=boxes[key];edges=spec.get('edges',[])
        paths=[]
        for i,e in enumerate(edges):
            if e['from'] not in b or e['to'] not in b:raise ValueError('Unknown edge endpoint in '+key)
            paths.append(e.get('route') or route(b,e['from'],e['to'],i))
        bottom=max(y+h for x,y,w,h in b.values());right=max(x+w for x,y,w,h in b.values())
        for p in paths:
            for x,y in p.get('via',[]):bottom=max(bottom,y+20);right=max(right,x)
        handoffs=[];used={'in':[],'out':[]}
        for h in spec.get('handoffs',[]):
            direction=h['direction'];inner=h['inner']
            if key not in owners:raise ValueError('Root uses ordinary edges for external interactions')
            if direction not in used or inner not in b:raise ValueError('Invalid handoff in '+key)
            x,y,w,height=b[inner];cy=y+height/2
            boundary_edge=min(v[0] for v in b.values()) if direction=='in' else max(v[0]+v[2] for v in b.values())
            default=(x==boundary_edge if direction=='in' else x+w==boundary_edge)
            custom=h.get('route')
            if custom:r=dict(custom);cy=r.get('y',cy)
            elif default and all(abs(cy-v)>100 for v in used[direction]):r={}
            else:
                cy=bottom+100;ip='b';cx=x+w/2;upper=min(v[1] for v in b.values())-45
                blocked=any(crosses((cx,y+height),(cx,cy),box) for key,box in b.items() if key!=inner)
                if blocked and all(abs(upper-v)>75 for v in used[direction]) and not any(crosses((cx,upper),(cx,y),box) for key,box in b.items() if key!=inner):
                    cy=upper;ip='t'
                r=dict(y=cy,ip=ip,via=[(cx,cy)])
            used[direction].append(cy);bottom=max(bottom,cy+45)
            for px,py in r.get('via',[]):bottom=max(bottom,py+20);right=max(right,px)
            handoffs.append((h,r))
        for group in spec.get('groups',[]):
            members=group['members']
            if not members or any(k not in b for k in members):raise ValueError('Invalid group members in '+key)
            gx=min(b[k][0] for k in members)-25;gy=min(b[k][1] for k in members)-65
            gw=max(b[k][0]+b[k][2] for k in members)-gx+25;gh=max(b[k][1]+b[k][3] for k in members)-gy+25
            s.frame(group['key'],group['label'],gx,gy,gw,gh,detail_html(group,perspective,title=False),specification=specification_state(group),pending=pending_state(group),violation=violation_state(group));bottom=max(bottom,gy+gh)
            remember(key,group['key'],group['label'],group)
        for node,n in spec['nodes'].items():
            s.node(node,n['label'],*b[node],body=detail_html(n,perspective,title=False),shape=n.get('shape','box'),specification=specification_state(n),pending=pending_state(n),violation=violation_state(n))
            remember(key,node,n['label'],n)
        for i,(e,p) in enumerate(zip(edges,paths),1):
            s.edge(e['from'],e['to'],e.get('label',''),kind=e.get('kind','relation'),dashed=e.get('conditional',False),body=detail_html(e,perspective,title=False),specification=specification_state(e),pending=pending_state(e),violation=violation_state(e),**p)
            remember(key,'relation-'+str(i),e.get('label') or s.labels[e['from']]+' → '+s.labels[e['to']],e)
        if key in owners:
            outgoing=max((text_width('出 · '+h['label'],13)+30 for h in spec.get('handoffs',[]) if h['direction']=='out'),default=90)
            parent,owner=owners[key];frame_right=right+max(260,outgoing)
            expansion=Expansion(s,owner=(parent,scenes[parent],owner),box=(240,55,frame_right-240,bottom+60-55),input_gap=spec.get('input_gap',''),output_gap=spec.get('output_gap',''))
            for i,(h,r) in enumerate(handoffs,len(edges)+1):
                outer=h['outer']
                if isinstance(outer,(tuple,list)):outer=(outer[0],scenes[outer[0]],outer[1])
                expansion.handoff(h['direction'],h['inner'],outer,h['label'],body=detail_html(h,perspective,title=False),condition=h.get('condition',''),kind=h.get('kind','data'),specification=specification_state(h),pending=pending_state(h),violation=violation_state(h),**r)
                remember(key,'relation-'+str(i),('入口 · ' if h['direction']=='in' else '出口 · ')+h['label'],h)
            s.width=frame_right+240;s.height=bottom+180
        else:s.width=max(1000,right+80);s.height=bottom+135
        source.append('<h2>'+esc(spec['title'])+'</h2>'+module_html({'fields':spec.get('fields',{})}))
    data=dict(data,source_html=''.join(source)+data.get('source_html',''))
    result=write_layers(out,scenes=scenes,children=children,root=root,data=data,summary=report.get('summary',''),findings=findings)
    result['checks']=check_report(Path(out)/'index.html')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',help='Trusted report.py defining REPORT, or index.html with --check')
    parser.add_argument('output',nargs='?');parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    if args.check:
        print(check_report(args.source))
    else:
        if not args.output:parser.error('Provide an output directory')
        print(build_report(runpy.run_path(args.source)['REPORT'],args.output))
