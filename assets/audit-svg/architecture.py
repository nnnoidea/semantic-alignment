"""SVG scenes for the layered report generator."""

import re

from components import Diagram, rect, txt, esc, wrap, EDGE_COLORS

from semantic_template import cell_html, MODULE

LEGEND=[
 ('#fee2e2','违反限制','红色“违反限制”角标和轮廓：有证据的实际做法违背具体用户限制，优先查看；父项可汇总后代标记，不代表每个子项都违反。'),
 ('#eaf4ee','有依据','绿色节点：有语义依据的能力／对象，标签尽量沿用用户原话，过长时略作压缩；点击查看原文、来源和 Agent 整理说明；不是实现通过。'),
 ('#f2f4f5','组织','灰色外框：Agent 整理的主题或职责范围；嵌套表示归属。'),
 ('#fff0ce','未指定','橙色轮廓＋“含未指定细节”：已识别出用户未约定的具体选择；Agent 已选方案仍保留此标记，不代表缺陷或必须提问。'),
 ('#edf0f3','未核查','灰色点线＋“细节未核查”：Agent 尚未确定哪些细节已被用户说明，不计入已发现的未指定细节。空输入和未梳理不自动算用户没说。'),
 ('#eee5fb','待定','紫色“方案待定”：尚未确定采用什么方案；独立于用户是否说明，可与橙色或灰色标记共存。'),
 ('#eaf0fa','关联','蓝色箭头：按标签理解信息、调用、返回或依赖方向，不自动表示运行先后。深色箭头表示有依据的流程；灰色无向虚线表示约束或附注；红色虚线箭头表示异常路径。其他虚线箭头表示有条件。'),
]

EXTRA='折角页＝信息产物；圆角框＝操作／组件；胶囊＝入口／结果；菱形＝判断；展开 ↓＝在 HTML 下方展开。深蓝轮廓＝选中／焦点；点击节点或关系看详情。'

EDGE_LEGEND='深色→＝流程；蓝色→＝信息／调用／返回；灰色无向虚线＝约束／附注；红色虚线→＝异常；其他虚线→＝有条件。条件与来源点线可查。'

MARKS={
 'violation':('违反限制','#fee2e2','#991b1b'),
 'unspecified':('含未指定细节','#fff0ce','#ad740d'),
 'unreviewed':('细节未核查','#edf0f3','#687782'),
 'pending':('方案待定','#eee5fb','#7652a0'),
}

def marks_svg(x,y,w,specification=None,pending=False,violation=False):
    states=(['violation'] if violation else [])+(['unspecified','unreviewed'] if specification=='mixed' else [specification] if specification in MARKS else [])+(['pending'] if pending else [])
    cursor=x+w;items=[]
    for state in reversed(states):
        label,fill,stroke=MARKS[state];width=len(label)*11+16
        if cursor-width<x and cursor<x+w:cursor=x+w;y-=22
        cursor-=width
        items.append(f'<g class="meaning-mark" data-meaning="{state}"><title>{esc(label)}</title>'+rect(cursor,y-10,width,18,fill,stroke,4)+f'<text x="{cursor+width/2}" y="{y+3}" text-anchor="middle" font-size="11" font-weight="600" fill="{stroke}">{label}</text></g>');cursor-=5
    return ''.join(items)

def module_html(module):
    return '<p>标签尽量沿用用户原话；缩写与 Agent 整理的内容在来源中说明。</p>'+''.join('<h3>'+label+'</h3>'+cell_html(module.get('fields',{}).get(k)) for k,label in MODULE)

class Scene:
    def __init__(self,title,width=1280,height=760):
        self.title=title;self.width=width;self.height=height;self.d=Diagram()
        self.back=[];self.lines=[];self.front=[];self.bounds={};self.labels={}
    def text(self,s,x,y,w=300,size=20,color='#234839',weight=500):
        return txt(s,x,y,w*.95,size,color,weight)[0]
    def node(self,key,label,x,y,w=170,h=70,body='',shape='box',*,specification=None,pending=False,violation=False):
        self.bounds[key]=(x,y,w,h);self.labels[key]=label
        if specification not in (None,'specified','unspecified','unreviewed','mixed'):raise ValueError('Unknown specification state')
        fill='#fff' if specification=='unreviewed' else '#eaf4ee'
        stroke=MARKS['unspecified' if specification=='mixed' else specification][2] if specification in MARKS or specification=='mixed' else '#89aa96'
        if violation:stroke=MARKS['violation'][2]
        dash='2 4' if specification=='unreviewed' and not violation else ''
        if shape=='doc':
            form=f'<path d="M{x},{y} H{x+w-18} L{x+w},{y+18} V{y+h} H{x} Z M{x+w-18},{y} V{y+18} H{x+w}" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>'
        elif shape=='decision':
            form=f'<path d="M{x+w/2},{y} L{x+w},{y+h/2} L{x+w/2},{y+h} L{x},{y+h/2} Z" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>'
        else:form=rect(x,y,w,h,fill,stroke,h/2 if shape=='terminal' else 12,dash)
        if shape in ('doc','decision') and dash:form=form.replace('stroke-width="1.6"','stroke-width="1.6" stroke-dasharray="'+dash+'"')
        lines=wrap(label,w*.7 if shape=='decision' else w-36,20)
        label_y=y+h/2+7-(len(lines)-1)*13.5
        label_svg=f'<text x="{x+w/2}" y="{label_y}" text-anchor="middle" font-size="20" fill="#234839" font-weight="550">'+''.join(f'<tspan x="{x+w/2}" dy="{0 if i==0 else 27}">{esc(line)}</tspan>' for i,line in enumerate(lines))+'</text>'
        item=self.d.node_start(key,label,(x,y,w,h),'architecture-node')+'<desc>'+esc(re.sub('<[^>]*>',' ',body))+'</desc>'+form+label_svg+marks_svg(x,y,w,specification,pending,violation)+'</g>'
        self.front.append(item);self.d.inspector(key,label,body or '<p>缺少：尚未提供该节点的语义来源。</p>')
        return key
    def frame(self,key,title,x,y,w,h,body='',*,specification=None,pending=False,violation=False):
        self.bounds[key]=(x,y,w,h);self.labels[key]=title
        self.back.append(rect(x,y,w,h,'#f4f6f4','#bccbc1',18))
        self.front.append(self.d.node_start(key,title,(x,y,w,h),'architecture-frame')+rect(x+2,y+2,w-4,48,'transparent','none',16)+self.text(title,x+20,y+32,w-65,21,'#315443',650)+marks_svg(x,y,w,specification,pending,violation)+'</g>')
        self.d.inspector(key,title,body or '<p>Agent 组织的模块边界。</p>')
    def edge(self,a,b,label='',ap='r',bp='l',via=(),dashed=False,at=None,body='',kind='relation',*,specification=None,pending=False,violation=False):
        """Draw a typed flow, exchange or association with its source-backed detail."""
        if kind not in ('relation',*EDGE_COLORS):raise ValueError('Unknown relationship kind: '+kind)
        def port(key,p):
            x,y,w,h=self.bounds[key];return {'r':(x+w,y+h/2),'l':(x,y+h/2),'t':(x+w/2,y),'b':(x+w/2,y+h)}[p]
        points=[port(a,ap),*via,port(b,bp)]
        dash=' stroke-dasharray="6 5"' if dashed or kind in ('constraint','error') else ''
        color=EDGE_COLORS.get(kind,'#51839a')
        marker='' if kind=='constraint' else ' marker-end="url(#'+('arrow' if kind=='relation' else kind+'-arrow')+')"'
        label_at=at or ((points[0][0]+points[-1][0])/2,(points[0][1]+points[-1][1])/2-10)
        separator=' — ' if kind=='constraint' else ' → '
        title=label or self.labels[a]+separator+self.labels[b]
        endpoints='<p><a href="#'+esc(a)+'">'+esc(self.labels[a])+'</a>'+separator+'<a href="#'+esc(b)+'">'+esc(self.labels[b])+'</a></p>'
        detail=endpoints+'<p>'+esc(label or '关系含义：缺少')+'</p>'+(body or '<p>Agent 整理的关系；缺少单独的来源说明，请结合两端语义核对。</p>')
        annotation=marks_svg(label_at[0]-110,label_at[1]-22,220,specification,pending,violation)
        self.lines.append(self.d.relation(title,points,color=color,marker=marker,dash=dash,label_at=label_at if label else None,body=detail,annotation=annotation))
    def svg(self):
        assert self.d._emitted==self.d._detail_keys
        style="text{font-family:system-ui,-apple-system,'PingFang SC',sans-serif}.node{cursor:pointer}.node:focus{outline:none}.edge-hit{stroke:transparent!important;stroke-width:16px!important;pointer-events:stroke}.edge-line{pointer-events:none}.relation-node text{cursor:pointer}.node:focus>rect,.node.selected>rect,.node:focus>path,.node.selected>path{stroke:#245dce;stroke-width:3;stroke-dasharray:none}"
        legend_y=self.height-92;legend=[]
        for i,(color,label,_) in enumerate(LEGEND):
            x=35+i*120;legend.append(rect(x,legend_y,18,18,color,'#a3b4a8',4,'2 3' if label=='未核查' else '')+self.text(label,x+27,legend_y+15,90,14))
        legend.append(self.text('红色角标＝违反用户限制；橙＝用户未指定；灰＝Agent未核查；紫＝方案待定。绿不表示所有细节已约定，也不表示实现通过。',35,legend_y+36,self.width-70,12,'#748479'))
        legend.append(self.text(EXTRA,35,legend_y+55,self.width-70,12,'#748479'))
        legend.append(self.text(EDGE_LEGEND,35,legend_y+73,self.width-70,12,'#748479'))
        markers=''.join(f'<marker id="{key}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10z" fill="{color}"/></marker>' for key,color in [('arrow','#51839a'),*((kind+'-arrow',color) for kind,color in EDGE_COLORS.items() if kind!='constraint')])
        return f'<svg xmlns="http://www.w3.org/2000/svg" id="semantic-svg" width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}" role="group" aria-labelledby="diagram-title"><title id="diagram-title">{esc(self.title)}</title><style>{style}</style><defs>{markers}</defs><rect width="100%" height="100%" fill="#fcfdfb"/>'+''.join(self.back+self.lines+self.front)+'<g class="diagram-legend">'+''.join(legend)+'</g></svg>'
