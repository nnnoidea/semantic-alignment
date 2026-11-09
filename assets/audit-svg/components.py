"""SVG primitives and selectable elements for the layered viewer."""

import html,re

esc=lambda value:html.escape(str(value),quote=True)

def wrap(text,width,size):
    lines=[];line='';used=0
    for c in text:
        cost=size*(1 if ord(c)>255 else .57)
        if used+cost>width and line:lines.append(line);line='';used=0
        line+=c;used+=cost
    if line:lines.append(line)
    return lines or ['']

def txt(text,x,y,width,size=20,color='#253c36',weight=400):
    lines=wrap(text,width,size)
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}">'+''.join(f'<tspan x="{x}" dy="{0 if i==0 else size*1.35}">{esc(t)}</tspan>' for i,t in enumerate(lines))+'</text>',len(lines)*size*1.35

def rect(x,y,w,h,fill,stroke,rx=6,dash=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="2"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>'

class Diagram:
    def __init__(self):
        self.inspectors=[]
        self._emitted=set();self._detail_keys=set();self._relation_count=0
    def node_start(self,id,label,bounds,kind):
        assert id not in self._emitted,f'Duplicate diagram node: {id}'
        self._emitted.add(id)
        return f'<g id="svg-{id}" class="node {kind}" data-key="{id}" tabindex="0" role="button" aria-label="{esc(label)}" data-box="{",".join(map(str,bounds))}"><title>{esc(label)}</title>'
    def inspector(self,id,title,body):
        assert id not in self._detail_keys,f'Duplicate inspector: {id}'
        self._detail_keys.add(id)
        self.inspectors.append(f'<article class="inspect-content" id="inspect-{id}" hidden><h2>{esc(title)}</h2>{body}</article>')
    def relation(self,label,points,*,color,marker='',dash='',body='',label_at=None,annotation=''):
        self._relation_count+=1;key='relation-'+str(self._relation_count)
        xs,ys=zip(*points);bounds=(min(xs),min(ys),max(1,max(xs)-min(xs)),max(1,max(ys)-min(ys)))
        path='M'+' L'.join(f'{x},{y}' for x,y in points)
        out=self.node_start(key,label,bounds,'relation-node')+'<desc>'+esc(html.unescape(re.sub('<[^>]*>',' ',body)))+'</desc>'
        out+=f'<path class="edge-hit" d="{path}" fill="none" stroke="transparent" stroke-width="16" pointer-events="stroke"/>'
        out+=f'<path class="edge-line" d="{path}" fill="none" stroke="{color}" stroke-width="2.4"{dash}{marker}/>'
        if label_at:
            x,y=label_at
            out+=f'<text x="{x}" y="{y}" text-anchor="middle" font-size="15" fill="{color}" paint-order="stroke" stroke="#fcfdfb" stroke-width="5" stroke-linejoin="round">{esc(label)}</text>'
        out+=annotation+'</g>'
        self.inspector(key,label,body or '<p>缺少：尚未提供这条关系的具体含义和来源。</p>')
        return out

EDGE_COLORS={'flow':'#415c69','data':'#397dab','constraint':'#8296a7','error':'#b66050'}
