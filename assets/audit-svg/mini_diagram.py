"""Small terminal-detail diagrams; explicit lanes/edges, no semantic inference."""
from components import esc, rect, txt, wrap


def mini_html(graph, render_cell):
    nodes = graph['nodes']; lanes = graph['lanes']; boxes = {}
    width = 160; height = max(64, max(len(wrap(n['label'], 136, 14))*19+30 for n in nodes.values()))
    gap = max(52, max((len(e.get('label', ''))*14+24 for e in graph.get('edges', [])), default=0))
    for r, lane in enumerate(lanes):
        for c, key in enumerate(lane):
            if key is None: continue
            if key not in nodes or key in boxes: raise ValueError('Invalid mini-diagram node placement: '+str(key))
            boxes[key] = (12+c*(width+gap), 28+r*(height+72), width, height)
    if not nodes or set(boxes) != set(nodes): raise ValueError('Mini diagram must place every node once')
    parts = []; details = []; bottoms = [y+h for x,y,w,h in boxes.values()]
    for i,e in enumerate(graph.get('edges', [])):
        a,b=e['from'],e['to']
        if a not in boxes or b not in boxes: raise ValueError('Unknown mini-diagram endpoint')
        # Reuse the main orthogonal routing rule; geometry does not infer edges.
        from flow import route
        routed=route(boxes,a,b,i)
        port=lambda box,p: {'l':(box[0],box[1]+box[3]/2),'r':(box[0]+box[2],box[1]+box[3]/2),'t':(box[0]+box[2]/2,box[1]),'b':(box[0]+box[2]/2,box[1]+box[3])}[p]
        points=[port(boxes[a],routed['ap']),*routed['via'],port(boxes[b],routed['bp'])]
        bottoms.extend(y+20 for x,y in points)
        key='edge-'+str(i); x,y=points[-1]; px,py=points[-2]
        dx,dy=x-px,y-py; length=max(1,(dx*dx+dy*dy)**.5); ux,uy=dx/length,dy/length
        path='M'+' L'.join(f'{xx},{yy}' for xx,yy in points)
        label=e.get('label') or nodes[a]['label']+' → '+nodes[b]['label']
        state=e.get('specification','unreviewed')
        if state not in ('specified','unspecified','unreviewed','context'):raise ValueError('Unknown mini-diagram edge state')
        color='#ad740d' if state=='unspecified' else '#526c60'
        parts.append(f'<g class="mini-select mini-edge" data-mini-select="{key}" data-meaning="{state}" data-pending="{str(bool(e.get("pending"))).lower()}" tabindex="0" role="button" aria-label="{esc(label)}"><path d="{path}" fill="none" stroke="transparent" stroke-width="18"/><path class="edge-line" d="{path}" fill="none" stroke="{color}" stroke-width="1.5"/>'+ ('' if e.get('kind')=='constraint' else f'<path d="M{x},{y} L{x-8*ux+4*uy},{y-8*uy-4*ux} L{x-8*ux-4*uy},{y-8*uy+4*ux} Z" fill="{color}"/>'))
        if e.get('label'):
            lx,ly=routed['at']; parts.append(f'<text x="{lx}" y="{ly}" text-anchor="middle" font-size="13" fill="{color}">{esc(e["label"])}</text>')
        badge='Agent 补充' if state=='unspecified' else '未核查' if state=='unreviewed' else ''
        if badge:
            lx,ly=routed['at'];parts.append(f'<text x="{lx}" y="{ly-17}" text-anchor="middle" font-size="11" fill="{color}">{esc(badge)}</text>')
        if e.get('pending'):
            lx,ly=routed['at'];parts.append(f'<text x="{lx}" y="{ly-32}" text-anchor="middle" font-size="11" fill="#7652a0">方案待定</text>')
        parts.append('</g>');details.append((key,label,e))
    for key,n in nodes.items():
        x,y,w,h=boxes[key]; state=n.get('specification','unreviewed')
        if state not in ('specified','unspecified','unreviewed','context'): raise ValueError('Unknown mini-diagram state')
        fill,stroke={'specified':('#eaf4ee','#89aa96'),'unspecified':('#fff0ce','#ad740d'),'unreviewed':('#fff','#687782'),'context':('#f2f4f5','#c5cfd4')}[state]
        label_lines=wrap(n['label'],w-24,14); top=y+h/2+5-(len(label_lines)-1)*9.45
        parts.append(f'<g class="mini-select" data-mini-select="node-{esc(key)}" data-meaning="{state}" data-pending="{str(bool(n.get("pending"))).lower()}" tabindex="0" role="button" aria-label="{esc(n["label"])}">'+rect(x,y,w,h,fill,stroke,9,'2 4' if state=='unreviewed' else '')+txt(n['label'],x+12,top,w-24,14,'#263b35',500)[0])
        badge='Agent 补充' if state=='unspecified' else '未核查' if state=='unreviewed' else ''
        if badge:parts.append(txt(badge,x+5,y-8,w-10,11,stroke)[0])
        if n.get('pending'):parts.append(f'<text x="{x+w-5}" y="{y-8}" text-anchor="end" font-size="11" fill="#7652a0">方案待定</text>')
        parts.append('</g>');details.append(('node-'+key,n['label'],n))
    w=max(x+ww for x,y,ww,h in boxes.values())+12;h=max(bottoms)+15
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" class="mini-diagram" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="group" aria-label="{esc(graph.get("label","详情简图"))}"><title>{esc(graph.get("label","详情简图"))}</title><style>.mini-diagram text{{font-family:system-ui,-apple-system,"PingFang SC",sans-serif}}</style>'+''.join(parts)+'</svg>'
    prose=[]
    for key,label,item in details:
        prose.append('<details class="mini-item" data-mini-detail="'+esc(key)+'" hidden><summary>'+esc(label)+'</summary>'+render_cell(item.get('detail'), '缺少：尚未提供本项说明与来源。')+'</details>')
    legend='绿：已有要求；橙：Agent 补充；灰点线：未核查；灰底：材料／结果；待定：方案未选。绿不表示实现通过；蓝框为当前选中。'
    return '<div class="mini-flow"><div class="mini-scroll">'+svg+'</div><p class="mini-legend">'+legend+'</p>'+''.join(prose)+'</div>'
