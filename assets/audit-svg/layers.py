"""Bounded SVG drill-down. Scenes/links are rendering inputs, not semantic records."""
from pathlib import Path
from string import Template
import copy,html,re,xml.etree.ElementTree as ET
from architecture import LEGEND,EXTRA,EDGE_LEGEND,MARKS,marks_svg
from components import esc,rect,txt,wrap,EDGE_COLORS
from semantic_template import check_perspective,summary_html

NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)
tag=lambda name:'{'+NS+'}'+name
LEVELS=('用户约定','实际流程','关键步骤')
BOUNDARY_LEGEND='内部展开外框＝上层所选节点整体；淡色“上层”框＝上下文引用；边界圆点＝入口／出口，不是执行步骤；HTML 中点引用定位上层节点。'

class Expansion:
    """Draw an owned boundary and explicit handoffs; never infer a runtime contract."""
    def __init__(self,scene,*,owner,box,input_gap='',output_gap=''):
        self.scene=scene;self.owner=owner;self.box=box;self.handoffs=[]
        self.gaps={'in':input_gap,'out':output_gap};scene.expansion=self
        view,parent,key=owner;x,y,w,h=box
        self.title=parent.labels[key]
        scene.back.insert(0,rect(x,y,w,h,'#f4f6f4','#a6bdb1',18).replace('<rect ',f'<rect class="expansion-boundary" data-box="{x},{y},{w},{h}" ',1))
        scene.front.append(f'<a class="expansion-owner" href="#{esc(view+"--"+key)}" aria-label="返回上层节点：{esc(self.title)}"><title>整个外框对应上层所选节点，不是新增执行步骤</title>'+txt(self.title+' · 内部展开',x+20,y+32,w-40,21,'#315443',650)[0]+'</a>')
        gaps=[('入口' if k=='in' else '出口')+'对应缺少：'+v for k,v in self.gaps.items() if v]
        if gaps:scene.front.append(txt('；'.join(gaps),x+20,y+h-16,w-40,13,'#687782')[0])

    def handoff(self,direction,inner,outer,label,*,body,y=None,ip=None,via=(),kind='data',condition='',specification=None,pending=False,violation=False):
        """outer: parent-local key, or (ancestor view, Scene, key). Layout is explicit.

        Default paths run left→right. y/ip/via route additional signals or exits.
        The port is part of the relation, not another process or diagram level.
        """
        if direction not in ('in','out'):raise ValueError('Handoff direction must be in/out')
        if kind not in EDGE_COLORS:raise ValueError('Unknown handoff kind')
        scene=self.scene;x,top,w,h=self.box;incoming=direction=='in'
        view,parent,key=(*self.owner[:2],outer) if isinstance(outer,str) else outer
        target=view+'--'+key;outer_label=parent.labels[key]
        nx,ny,nw,nh=scene.bounds[inner];ip=ip or ('l' if incoming else 'r')
        point={'l':(nx,ny+nh/2),'r':(nx+nw,ny+nh/2),'t':(nx+nw/2,ny),'b':(nx+nw/2,ny+nh)}[ip]
        cy=point[1] if y is None else y;bx=x if incoming else x+w
        cx=x-220 if incoming else x+w+60;cw=160
        note='上层'+(' · '+condition if condition else '')
        note_height=len(wrap(note,cw-24,12))*16.2
        label_lines=len(wrap(outer_label,cw-24,17));ch=max(66,45+note_height+(label_lines-1)*22.95)
        context=(cx+cw,cy) if incoming else (cx,cy)
        points=[context,(bx,cy),*via,point] if incoming else [point,*via,(bx,cy),context]
        link=lambda ref,text:'<a href="#'+esc(ref)+'">'+esc(text)+'</a>'
        inner_link=link(inner,scene.labels[inner]);outer_link=link(target,outer_label)
        sep=' — ' if kind=='constraint' else ' → '
        endpoints=outer_link+sep+inner_link if incoming else inner_link+sep+outer_link
        marker='' if kind=='constraint' else f' marker-end="url(#{kind}-arrow)"'
        line=scene.d.relation(('入口 · ' if incoming else '出口 · ')+label,points,color=EDGE_COLORS[kind],marker=marker,dash=' stroke-dasharray="6 5"' if condition or kind in ('constraint','error') else '',body='<p>'+endpoints+'</p>'+body)
        port_label=('入 · ' if incoming else '出 · ')+label
        # Labels live inside the boundary corridor, away from upper references.
        text_width=sum(13*(1 if ord(c)>255 else .57) for c in port_label)
        tx=bx+12 if incoming else bx-12-text_width
        port=f'<g class="boundary-port"><title>{esc(port_label)}</title><circle cx="{bx}" cy="{cy}" r="6" fill="#fff" stroke="{EDGE_COLORS[kind]}" stroke-width="2"/>'+txt(port_label,tx,cy-17,text_width+1,13,EDGE_COLORS[kind])[0]+marks_svg(tx,cy-48,max(220,text_width),specification,pending,violation)+'</g>'
        scene.lines.append(line[:-4]+port+'</g>')
        # These are linked context references, not duplicate operations/choices.
        scene.front.append(f'<a class="upper-context" data-box="{cx},{cy-ch/2},{cw},{ch}" href="#{esc(target)}" aria-label="定位上层：{esc(outer_label)}"><title>上层已有节点的引用</title>'+rect(cx,cy-ch/2,cw,ch,'#f2f4f5','#c5cfd4',9)+txt(note,cx+12,cy-ch/2+16,cw-24,12,'#687782')[0]+txt(outer_label,cx+12,cy-ch/2+33+note_height,cw-24,17,'#415c69',550)[0]+'</a>')
        self.handoffs.append((direction,inner,view,parent,key))

def validate_expansions(scenes,owners):
    for child,(parent,key) in owners.items():
        boundary=getattr(scenes[child],'expansion',None)
        if boundary is None:raise ValueError('Child scene needs an Expansion boundary: '+child)
        if boundary.owner!=(parent,scenes[parent],key):raise ValueError('Expansion owner disagrees with children: '+child)
        ancestors=set();cursor=child
        while cursor in owners:
            cursor=owners[cursor][0];ancestors.add(cursor)
        for direction,inner,view,context,outer in boundary.handoffs:
            if view not in ancestors or scenes.get(view) is not context or outer not in context.bounds:
                raise ValueError('Handoff must reference an existing ancestor node: '+view+'--'+outer)
        for direction in ('in','out'):
            if not any(h[0]==direction for h in boundary.handoffs) and not boundary.gaps[direction]:
                raise ValueError('Supply a '+direction+' handoff or an explicit boundary gap: '+child)

def validate(scenes,children,root):
    if root not in scenes:raise ValueError('Root scene is missing')
    if any(not re.fullmatch(r'[a-zA-Z][\w-]*',k) or '--' in k for k in scenes):raise ValueError('Use simple scene names without --')
    owners={}
    for parent,links in children.items():
        if parent not in scenes:raise ValueError('Unknown parent scene: '+parent)
        for node,child in links.items():
            if node not in scenes[parent].bounds:raise ValueError('Child views must attach to an existing node/frame: '+node)
            if child not in scenes:raise ValueError('Unknown child scene: '+child)
            if child==root or child in owners:raise ValueError('Each child scene needs one owner; shared flows use reference links')
            owners[child]=(parent,node)
    order=[];depth={}
    def visit(key,level):
        if level>3:raise ValueError('At most three diagram levels; use terminal details for deeper information')
        if key in depth:raise ValueError('Cyclic scene hierarchy')
        depth[key]=level;order.append(key)
        for child in children.get(key,{}).values():visit(child,level+1)
    visit(root,1)
    if set(order)!=set(scenes):raise ValueError('Unreachable scenes: '+', '.join(sorted(set(scenes)-set(order))))
    return order,depth,owners

def qualify_html(html,scene,keys):
    # Only local diagram targets are rewritten; report anchors and URLs survive.
    for key in sorted(keys,key=len,reverse=True):
        html=html.replace('id="inspect-'+esc(key)+'"','id="inspect-'+esc(scene+'--'+key)+'"')
        html=html.replace('href="#'+esc(key)+'"','href="#'+esc(scene+'--'+key)+'"')
    return html

def render_scenes(scenes,children,order):
    roots={key:ET.fromstring(scenes[key].svg()) for key in order}
    for key in reversed(order):
        root=roots[key];nodes={n.get('data-key'):n for n in root.iter() if n.get('data-key')}
        for node_key,child in children.get(key,{}).items():
            node=nodes[node_key]
            states={n.get('data-meaning') for n in roots[child].iter() if n.get('data-meaning')}
            states|={n.get('data-meaning') for n in node.iter() if n.get('data-meaning')}
            for n in list(node):
                if n.get('class')=='meaning-mark':node.remove(n)
            spec='mixed' if {'unspecified','unreviewed'}<=states else 'unspecified' if 'unspecified' in states else 'unreviewed' if 'unreviewed' in states else None
            x,y,w,h=map(float,node.get('data-box').split(','))
            shape=next((n for n in node if n.tag in (tag('rect'),tag('path')) and n.get('fill') not in ('transparent','none')),None)
            if shape is not None and (spec or 'violation' in states):
                shape.set('stroke',MARKS['violation' if 'violation' in states else 'unspecified' if spec=='mixed' else spec][2])
                if spec=='unreviewed' and 'violation' not in states:shape.set('stroke-dasharray','2 4')
                else:shape.attrib.pop('stroke-dasharray',None)
            for mark in ET.fromstring('<g xmlns="'+NS+'">'+marks_svg(x,y,w,spec,'pending' in states,'violation' in states)+'</g>'):node.append(mark)
            node.set('data-child',child);node.set('data-descendant-states',' '.join(sorted(states)))
            node.set('aria-expanded','false');node.set('aria-controls','view-'+child)
            node.set('aria-label',node.get('aria-label','')+'；展开内部流程'+('；含违反用户限制的项' if 'violation' in states else '')+('；含未指定细节' if 'unspecified' in states else '')+('；含未核查细节' if 'unreviewed' in states else '')+('；含待定方案' if 'pending' in states else ''))
            ET.SubElement(node,tag('text'),{'class':'drill-hint','x':str(x+w-12),'y':str(y+h-8),'text-anchor':'end','font-size':'11','fill':'#48745f'}).text='展开 ↓'
    result={}
    for key,root in roots.items():
        idmap={n.get('id'):key+'--'+n.get('id') for n in root.iter() if n.get('id')}
        for n in root.iter():
            if n.get('data-key'):idmap[n.get('id')]='svg-'+key+'--'+n.get('data-key')
        for n in root.iter():
            if n.get('id'):n.set('id',idmap[n.get('id')])
            if n.get('data-key'):n.set('data-key',key+'--'+n.get('data-key'))
            if n.get('aria-labelledby'):n.set('aria-labelledby',' '.join(idmap.get(v,v) for v in n.get('aria-labelledby').split()))
            for attr,value in list(n.attrib.items()):
                if attr.endswith('href') and value.startswith('#') and value[1:] in scenes[key].d._emitted:n.set(attr,'#'+key+'--'+value[1:])
                if 'url(#' in value:n.set(attr,re.sub(r'url\(#([^)]*)\)',lambda m:'url(#'+idmap[m[1]]+')',value))
        result[key]=root
    return result

def prepare_details(scenes,order):
    """Resolve explicit references and provide returns to their entry points."""
    bodies={};titles={};references={};by_view={}
    for view in order:
        by_view[view]=[]
        for original in scenes[view].d.inspectors:
            body=qualify_html(original,view,scenes[view].d._emitted)
            key=html.unescape(re.search(r'id="inspect-([^"]+)"',body)[1])
            bodies[key]=body;by_view[view].append(key)
            titles[key]=re.search(r'<h2>(.*?)</h2>',body,re.S)[1]
            references[key]=dict.fromkeys(html.unescape(target) for target in re.findall(r'<a class="detail-reference" href="#([^"]+)"',body))
    for source,targets in references.items():
        for target in targets:
            if target in bodies and source!=target and source not in references[target]:
                link='<p><a class="detail-return" href="#'+esc(source)+'">返回：'+titles[source]+'</a></p>'
                bodies[target]=bodies[target][:-len('</article>')]+link+'</article>'
    return {view:[bodies[key] for key in keys] for view,keys in by_view.items()}

def write_layers(out,*,scenes,children,root,data,summary='',findings=()):
    """Write offline HTML + one complete SVG per view. No server or dependencies."""
    check_perspective(data.get('perspective'))
    order,depth,owners=validate(scenes,children,root)
    validate_expansions(scenes,owners)
    trees=render_scenes(scenes,children,order)
    details=prepare_details(scenes,order)
    summary_targets={item['target']:'summary-'+item['target']+'-'+('violation' if any(c['kind']=='violation' for c in item['findings']) else item['findings'][0]['kind']) for item in findings}
    out=Path(out);out.mkdir(parents=True,exist_ok=True);assets=Path(__file__).parent
    views=[];inspectors=[];full=[]
    for key in order:
        scene=scenes[key];tree=trees[key]
        ET.SubElement(tree,tag('desc')).text='展开 ↓ 表示在 HTML 中展开下一层；独立 SVG 是当前层的静态视图。'
        legend_node=next(n for n in tree if n.get('class')=='diagram-legend')
        legend_node.append(ET.fromstring(txt(BOUNDARY_LEGEND,35,scene.height+2,scene.width-70,12,'#748479')[0]))
        tree.set('height',str(scene.height+24));tree.set('viewBox',f'0 0 {scene.width} {scene.height+24}')
        (out/(key+'.svg')).write_text(ET.tostring(tree,encoding='unicode'))
        embedded=copy.deepcopy(tree)
        for n in list(embedded):
            if n.get('class')=='diagram-legend':embedded.remove(n)
        h=scene.height-92;embedded.set('height',str(h));embedded.set('viewBox',f'0 0 {scene.width} {h}')
        owner='--'.join(owners[key]) if key in owners else ''
        owner_attr=' data-owner="'+esc(owner)+'"' if owner else ''
        level_label=getattr(scene,'level_label',None) or LEVELS[depth[key]-1]
        views.append(f'<section class="flow-level" id="view-{key}" data-view="{key}" data-depth="{depth[key]}"{owner_attr}'+(' hidden' if key!=root else '')+'><header><span class="level-label">'+str(depth[key])+' / '+esc(level_label)+'</span><h2>'+esc(scene.title)+'</h2></header><div class="diagram-shell"><div class="canvas-wrap"><div class="zoom-controls" role="group" aria-label="本层图形缩放"><button data-zoom="in" aria-label="放大本层图">＋</button><button data-zoom="out" aria-label="缩小本层图">−</button></div><div class="flow-canvas" tabindex="0" aria-label="可滚动和缩放，选择节点展开或查看详情">'+ET.tostring(embedded,encoding='unicode')+'</div></div></div><details class="parent-context" hidden><summary>所选节点的说明与来源</summary><div class="parent-detail"></div></details></section>')
        full.append('<section><h2>'+esc(scene.title)+'</h2>')
        for body in details[key]:
            target=re.search(r'id="inspect-([^"]+)"',body).group(1)
            if target in summary_targets:
                body=body[:-len('</article>')]+'<p><a class="summary-return" href="summary.html#'+esc(summary_targets[target])+'">查看本项差异汇总</a></p></article>'
            inspectors.append(body)
            # Full reading route preserves every field, including hidden branches.
            heading=re.search(r'<h2>(.*?)</h2>',body,re.S).group(1)
            content=re.sub(r'^<article[^>]*><h2>.*?</h2>|</article>$','',body,flags=re.S)
            full.append('<details class="source-item"><summary>'+heading+'</summary>'+content+'</details>')
        full.append('</section>')
    perspective=data.get('perspective')
    label='实现对照 · 用户要求与实际做法' if perspective=='realization' else ''
    legend='<details class="map-notes"><summary>图例与范围</summary><p>'+esc(data.get('scope','范围：缺少'))+'</p>'+''.join('<p>'+esc(desc)+'</p>' for _,_,desc in LEGEND)+'<p>'+esc(EXTRA+' '+EDGE_LEGEND)+'</p><p>'+esc(BOUNDARY_LEGEND)+'</p><p>展开 ↓：点击在下方展开内部流程；每层保留一条选择路径，最多三层图。上层角标提示下层内容，完整细节仍可从下方原文入口读取。</p></details>'
    page=Template((assets/'layers.html').read_text()).substitute(title=esc(data.get('title',scenes[root].title)),date=esc(data.get('date','')),summary=('<p>'+label+'</p>' if label else '')+summary+'<p>点击“展开 ↓”进入下一层；点击其他节点或关系查看要求与做法简图、具体说明和来源。</p>',legend=legend,views=''.join(views),inspectors=''.join(inspectors),report=data.get('source_html','')+''.join(full),css=(assets/'viewer.css').read_text(),js=(assets/'viewer.js').read_text())
    (out/'index.html').write_text(page)
    findings_html,counts=summary_html(findings)
    summary_context=summary.replace('href="#','href="index.html#').replace("href='#","href='index.html#")
    summary_page='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>差异汇总 · '+esc(data.get('title',scenes[root].title))+'</title><style>'+(assets/'viewer.css').read_text()+'</style></head><body class="findings-page"><header class="summary-header"><p>'+esc(data.get('date',''))+'</p><h1>差异汇总</h1><nav class="report-nav" aria-label="报告阅读方式"><a href="summary.html" aria-current="page">差异汇总</a><a href="index.html">逐层查看</a></nav><p>'+esc(data.get('title',scenes[root].title))+'</p><details><summary>检查范围与验证局限</summary><p>'+esc(data.get('scope','范围：缺少'))+'</p>'+summary_context+'<p><a href="index.html#source-report">完整报告与证据</a></p></details></header><main>'+findings_html+'</main></body></html>'
    (out/'summary.html').write_text(summary_page)
    return {'views':len(order),'max_depth':max(depth.values()),'nodes':sum(len(s.d._emitted) for s in scenes.values()),'summary':counts}
