"""Semantic context, source cells and detail panels for layered reports."""

from components import esc

PROJECT = [('goal','目标'),('scope','范围与不做什么'),('constraints','共同约束'),('acceptance','验收依据')]

MODULE = [('purpose','职责'),('inputs','输入／触发'),('outputs','输出／影响'),('behavior','行为／规则'),('boundaries','边界／例外'),('acceptance','验收依据')]

DETAIL_FIELDS = [('specified','用户要求'),('choice','实际做法'),('impact','影响与取舍')]
COMPARISON_KINDS = {'violation':'违反用户限制','match':'已核对一致','mismatch':'偏离／未实现','addition':'Agent 补充','unverified':'实现未核实'}
FINDING_KINDS = {**COMPARISON_KINDS,'unreviewed':'约定未核查','pending':'方案待定'}

def comparison_spans(comparisons,values):
    """Locate author-checked meaning pairs without changing or diffing the prose."""
    spans={'specified':[],'choice':[]}
    for i,c in enumerate(comparisons,1):
        kind=c.get('kind');note=c.get('note')
        if not isinstance(c.get('title'),str) or not c['title'].strip():raise ValueError('Comparison needs a concrete finding title')
        if kind not in COMPARISON_KINDS or not isinstance(note,str) or not note.strip():
            raise ValueError('Comparison needs a known kind and a concrete note')
        if kind=='match' and not all(c.get(k) for k in spans):raise ValueError('A match needs both requirement and actual text')
        if kind=='violation' and (not all(c.get(k) for k in spans) or not isinstance(c.get('constraint_source'),str) or not c['constraint_source'].strip()):
            raise ValueError('A restriction violation needs both fragments and the user restriction source')
        if kind=='addition' and (c.get('specified') or not c.get('choice')):raise ValueError('An addition marks only the actual choice')
        if not any(c.get(k) for k in spans):raise ValueError('Comparison needs a text fragment')
        for key in spans:
            quote=c.get(key)
            if not quote:continue
            text=values[key]['text']
            if not isinstance(quote,str) or text.count(quote)!=1:
                raise ValueError('Comparison fragment must occur exactly once in '+key+': '+str(quote))
            start=text.index(quote);spans[key].append((start,start+len(quote),kind,i,note))
    for key,items in spans.items():
        items.sort();end=0
        for start,stop,*_ in items:
            if start<end:raise ValueError('Overlapping comparison fragments in '+key)
            end=stop
    return spans

def comparison_text(text,spans):
    out=[];end=0
    for start,stop,kind,number,note in spans:
        title=str(number)+' · '+COMPARISON_KINDS[kind]+'：'+note
        out.extend([esc(text[end:start]),'<mark class="comparison-mark '+kind+'" title="'+esc(title)+'">',esc(text[start:stop]),'<sup class="comparison-index">'+str(number)+'</sup></mark>']);end=stop
    return ''.join(out)+esc(text[end:])

def cell(value, default='缺少'):
    if not value:
        return {'text':default, 'origin':'未提供', 'source':'', 'context':''}
    if isinstance(value, str):
        return {'text':value, 'origin':'Agent 归纳', 'source':'', 'context':''}
    return dict(text=value.get('text') or default, origin=value.get('origin','来源未标明'),
                source=value.get('source',''), context=value.get('context',''), missing=value.get('missing',''), diagram=value.get('diagram'))

def specification_state(row):
    """A named source gap is evidence; a blank input is not a completed review."""
    state=row.get('specification')
    if state is None:state='unspecified' if cell(row.get('specified')).get('missing') else 'unreviewed'
    if state not in ('specified','unspecified','unreviewed'):raise ValueError('Unknown specification state: '+str(state))
    states={state}|{v.get('specification','unreviewed') for v in diagram_items(row)}
    if any(c.get('kind')=='addition' for c in row.get('comparisons',[])):states.add('unspecified')
    if {'unspecified','unreviewed'}<=states:return 'mixed'
    if 'unspecified' in states:return 'unspecified'
    if 'unreviewed' in states:return 'unreviewed'
    return state

def diagram_items(row):
    for key in ('specified','choice'):
        value=row.get(key)
        graph=value.get('diagram') if isinstance(value,dict) else None
        if graph:
            yield from graph['nodes'].values()
            yield from graph.get('edges',[])

def pending_state(row):
    return bool(row.get('pending') or any(v.get('pending') for v in diagram_items(row)))

def pending_label(row):
    return '方案待定' if row.get('pending') else ('含待定方案' if pending_state(row) else '')

def pending_badge(label):
    return '<span class="comparison-key pending">'+esc(label)+'</span>' if label else ''

def violation_state(row):
    return any(c.get('kind')=='violation' for c in row.get('comparisons',[]))

def missing_text(value):
    text=value.get('text') if isinstance(value,dict) else value
    return not isinstance(text,str) or not text.strip()

def cell_html(value, default='缺少', *, spans=()):
    c=cell(value,default)
    source=''
    if c['source'] or c['context'] or c['origin'] not in ('未提供','来源未标明'):
        source='<details class="source-note"><summary>来源 · '+esc(c['origin'])+'</summary>'+('<p class="citation">'+esc(c['source'])+'</p>' if c['source'] else '<p class="citation">未提供具体出处。</p>')+''.join('<p>'+esc(p)+'</p>' for p in c['context'].split('\n\n') if p)+'</details>'
    return '<p class="source-text">'+comparison_text(c['text'],spans)+'</p>'+('<p><b>缺少：</b>'+esc(c['missing'])+'</p>' if c.get('missing') else '')+source

def check_perspective(value):
    if value not in (None,'realization'):
        raise ValueError('Only current semantics and implementation comparison are supported')

def detail_cells(row, perspective=None):
    """Normalize presentation fields without inventing specification or effects."""
    check_perspective(perspective)
    specified=cell(row.get('specified'));missing=specified.pop('missing','')
    unspecified=row.get('unspecified') or {'text':missing,'origin':'Agent 对来源缺口的归纳','source':specified['source']}
    # Keep specification gaps beside the corresponding choice and source.
    choice=cell(row.get('choice'),'未核实：尚未提供实际做法。')
    if missing_text(row.get('choice')):choice['text']='未核实：尚未提供实际做法。'
    if row.get('unspecified') or missing:
        gap=cell(unspecified)
        choice['context']='\n\n'.join(v for v in (choice['context'],'选择的约定边界：'+gap['text'],gap.get('source'),gap.get('context')) if v)
    return dict(purpose=cell(row.get('purpose'),'本项作用尚未说明。'),
                specified=specified,choice=choice,
                impact=cell(row.get('impact'),'缺少：尚未分析影响与取舍。'))

def detail_html(row, perspective=None, *, title=True):
    """Lead with findings; retain complete wording, diagrams and evidence below."""
    values=detail_cells(row,perspective)
    comparisons=row.get('comparisons',[]);spans=comparison_spans(comparisons,values)
    out='<section class="semantic-detail">'+('<h3>'+esc(row.get('name','缺少：尚未梳理具体事项'))+'</h3>' if title else '')
    findings=summary_findings(row)
    if findings:out+=review_findings_html(findings,values)
    matches=[dict(c,number=i) for i,c in enumerate(comparisons,1) if c['kind']=='match']
    if matches:
        matched=''.join(review_finding_html(c,values) for c in matches)
        out+=('<details class="review-matches"><summary>已核对一致的部分（'+str(len(matches))+'）</summary>'+matched+'</details>') if findings else matched
    if not findings and not matches:out+='<p class="review-empty">本项尚未提供逐项对照；展开下方原文查看已记录的要求与做法。</p>'
    if pending_state(row):out+='<p class="choice-status">'+pending_badge(pending_label(row))+'</p>'
    out+='<details class="detail-evidence"><summary>完整原文、来源与取舍</summary><div class="detail-purpose">'+cell_html(values['purpose'])+'</div>'
    if comparisons:
        out+='<p class="comparison-legend">文字标色：'+''.join('<span class="comparison-key '+kind+'">'+label+'</span> ' for kind,label in COMPARISON_KINDS.items())+'。同一编号对应同一事项；未标色正文未作片段对照。</p>'
    out+='<dl class="detail-fields">'
    for key,label in DETAIL_FIELDS:
        if key in ('specified','choice') and values[key].get('diagram'):
            from mini_diagram import mini_html
            prose=cell_html(values[key],spans=spans[key])
            body=mini_html(values[key]['diagram'],cell_html)+(prose if spans[key] else '<details class="source-note"><summary>完整原文与来源</summary>'+prose+'</details>')
        else:body=cell_html(values[key],spans=spans.get(key,()))
        if key=='choice' and not comparisons:
            state=specification_state(row)
            status_label={'specified':'已有明确约定（限本项）','unspecified':'含 Agent 补充的选择','unreviewed':'约定范围尚未核查','mixed':'含 Agent 补充的选择 · 仍有未核查细节'}[state]
            body='<p class="choice-status '+state+'">'+status_label+(' · '+pending_label(row) if pending_state(row) else '')+'</p>'+body
        if key=='choice' and comparisons:
            if pending_state(row):body='<p class="choice-status">'+pending_badge(pending_label(row))+'</p>'+body
            body+='<ol class="comparison-notes">'+''.join('<li><span class="comparison-key '+c['kind']+'">'+COMPARISON_KINDS[c['kind']]+'</span> '+esc(c['note'])+('<p class="citation">限制依据：'+esc(c['constraint_source'])+'</p>' if c['kind']=='violation' else '')+'</li>' for c in comparisons)+'</ol>'
        out+='<div><dt>'+label+'</dt><dd>'+body+'</dd></div>'
    out+='</dl></details></section>'
    for link in row.get('links',[]):
        out+='<p><a class="detail-reference" href="#'+esc(link['target'])+'">'+esc(link['label'])+'</a></p>'
    return out

def summary_findings(row):
    """Collect explicit findings, missing evidence and every marked mini item."""
    findings=[dict(c,number=i) for i,c in enumerate(row.get('comparisons',[]),1) if c['kind']!='match']
    kinds={c['kind'] for c in findings};values=detail_cells(row)
    state=row.get('specification') or ('unspecified' if cell(row.get('specified')).get('missing') else 'unreviewed')
    if state=='unspecified' and 'addition' not in kinds:
        findings.append(dict(kind='addition',title='本项有尚未逐项概括的补充选择',choice=values['choice']['text'],note='本项已标为含未指定选择，尚未拆分为逐项文字对照；完整实际做法仍保留。'))
    if state=='unreviewed':
        findings.append(dict(kind='unreviewed',title='本项的用户约定范围尚未核查',note='约定范围尚未核查，不能判断哪些细节是用户未指定的。'))
    if missing_text(row.get('choice')) and not any(c['kind']=='unverified' and c.get('choice')==values['choice']['text'] for c in findings):
        findings.append(dict(kind='unverified',title='本项尚未提供实际做法',choice=values['choice']['text'],note='缺少实际做法或实现证据；这不改变用户约定是否明确。'))
    for key,label in DETAIL_FIELDS[:2]:
        graph=values[key].get('diagram')
        if not graph:continue
        for item in [*graph['nodes'].values(),*graph.get('edges',[])]:
            state=item.get('specification','unreviewed');name=item.get('label') or item.get('from','')+' → '+item.get('to','')
            detail=cell(item.get('detail'),'未核实：尚未提供简图说明。')
            start=len(findings)
            if state in ('unspecified','unreviewed'):
                findings.append(dict(kind='addition' if state=='unspecified' else 'unreviewed',title=item.get('title') or ('简图中的补充选择：' if state=='unspecified' else '简图中的约定尚未核查：')+name,choice=label+'简图 · '+name+'：'+detail['text'],note='逐项保留简图已标出的选择或未核查范围，不由正文的单条标注替代。',source=detail['source'],impact=item.get('impact')))
            if missing_text(item.get('detail')):
                findings.append(dict(kind='unverified',title='简图“'+name+'”缺少说明与证据',note=label+'简图“'+name+'”缺少具体说明和证据。'))
            if item.get('pending'):
                if len(findings)==start:
                    findings.append(dict(kind='pending',title='简图中的方案尚未确定：'+name,choice=label+'简图 · '+name+'：'+detail['text'],note='本简图项标为方案待定；此状态不改变约定范围或实现核实情况。',source=detail['source'],impact=item.get('impact')))
                for finding in findings[start:]:finding['pending']=True
    if row.get('pending') and not findings:
        findings.append(dict(kind='pending',title='本项方案尚未确定',choice=values['choice']['text'],note='本项标为方案待定；此状态不改变约定范围或实现核实情况。'))
    return findings

def review_finding_html(c,context=None):
    """The same finding layout serves summary and node details."""
    context=context or {};kind=c['kind'];heading=esc(c['title'])
    number=' · 对照 '+str(c['number']) if c.get('number') else ''
    status=pending_badge('方案待定') if c.get('pending') and kind!='pending' else ''
    badge='<span class="comparison-key '+kind+'">'+FINDING_KINDS[kind]+number+'</span>'+status
    impact=c.get('impact') or context.get('impact')
    evidence=('<div class="review-impact"><b>'+('影响与取舍' if c.get('impact') else '本项整体影响与取舍')+'</b>'+cell_html(impact)+'</div>' if impact else '<p class="review-unknown">影响与取舍尚未说明。</p>')
    evidence+='<p><b>判断依据：</b>'+esc(c['note'])+'</p>'
    if c.get('constraint_source'):evidence+='<p class="citation">限制依据：'+esc(c['constraint_source'])+'</p>'
    if c.get('source'):evidence+='<p class="citation">来源：'+esc(c['source'])+'</p>'
    for key,label in DETAIL_FIELDS[:2]:
        source=cell(context.get(key))
        if source['source']:evidence+='<p class="citation">'+label+' · '+esc(source['origin'])+'：'+esc(source['source'])+'</p>'
    if kind=='addition':
        actual='<p class="source-text">'+esc(c.get('choice','具体做法尚未提供。'))+'</p>'
        return '<details class="review-choice"><summary><span class="review-choice-dot" aria-hidden="true">•</span><strong>'+heading+'</strong>'+status+'</summary><div class="review-choice-body">'+actual+evidence+'</div></details>'
    pair=''
    for key,label in [('specified','用户要求'),('choice','实际做法')]:
        if c.get(key):pair+='<div class="review-side '+key+'"><span class="review-quote-label">'+label+'</span><blockquote>'+esc(c[key])+'</blockquote></div>'
    return '<section class="review-finding '+kind+(' constraint-alert' if kind=='violation' else '')+'">'+badge+'<h3 class="review-title">'+heading+'</h3>'+('<div class="review-pair">'+pair+'</div>' if pair else '')+'<details class="review-evidence"><summary>影响、判断依据与来源</summary>'+evidence+'</details></section>'

def review_findings_html(findings,context=None):
    main=[c for c in findings if c['kind'] in ('violation','mismatch')]
    main.sort(key=lambda c:c['kind']!='violation')
    added=[c for c in findings if c['kind']=='addition']
    out='<div class="review-grid'+(' review-paired' if main and added else '')+'">'
    if main:out+='<div class="review-primary">'+''.join(review_finding_html(c,context) for c in main)+'</div>'
    if added:out+='<section class="review-additions"><h3>Agent 自行补充</h3>'+''.join(review_finding_html(c,context) for c in added)+'</section>'
    out+='</div>'
    for kind in ('unreviewed','unverified','pending'):
        items=[c for c in findings if c['kind']==kind]
        if items:out+='<section class="review-status"><h3>'+FINDING_KINDS[kind]+'</h3>'+''.join(review_finding_html(c,context) for c in items)+'</section>'
    return out

def summary_html(items):
    """A skim route over the same findings, with links to their original context."""
    labels={'violation':'违反用户限制 · 优先看','mismatch':'其他偏离或遗漏','addition':'Agent 补充的选择','unreviewed':'约定未核查','unverified':'实现未核实','pending':'其他待定方案'}
    empty={'violation':'当前已核对结果没有列出违反用户限制的项；未核实范围另列，不代表全部限制都已验证。','mismatch':'当前已标注结果未列出其他偏离或遗漏；不代表所有要求均已核实。','addition':'当前已标注结果未列出补充选择；不代表全部细节均由用户指定。','unverified':'当前输入未单列未核实事项；检查范围与局限仍见原报告。'}
    counts={kind:sum(c['kind']==kind for item in items for c in item['findings']) for kind in labels}
    labels={kind:label for kind,label in labels.items() if counts[kind] or kind not in ('unreviewed','pending')}
    out='<nav class="summary-counts" aria-label="按发现类型查看">'+''.join('<a class="comparison-key '+kind+'" href="#'+kind+'">'+label+' <b>'+str(counts[kind])+'</b></a>' for kind,label in labels.items())+'</nav>'
    out+='<p class="summary-scope">数字为已记录的摘要项数，不是缺陷总数。仅汇总已有检查结果；未标注内容不判为一致，补充选择不自动等于错误。</p>'
    for kind,label in labels.items():
        out+='<section class="finding-section" id="'+kind+'"><h2>'+label+'</h2>'
        if kind=='pending':out+='<p class="summary-scope">此处仅列没有其他发现类型的待定项；已有发现的待定状态标在对应条目或组上。</p>'
        if not counts[kind]:out+='<p class="summary-empty">'+empty[kind]+'</p>'
        for item in items:
            findings=[c for c in item['findings'] if c['kind']==kind]
            if not findings:continue
            target=item['target'];out+='<article class="finding-group" id="summary-'+esc(target)+'-'+kind+'"><header><span>'+esc(item['view'])+'</span><h3>'+esc(item['title'])+'</h3>'+pending_badge(item.get('context',{}).get('pending_label',''))+'<a href="index.html#inspect-'+esc(target)+'">图中详情与来源 →</a></header><div class="finding-items">'+''.join(review_finding_html(c,item.get('context')) for c in findings)+'</div></article>'
        out+='</section>'
    return out,counts
