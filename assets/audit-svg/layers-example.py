# -*- coding: utf-8 -*-
"""Fictional agreement → implementation example; renders a report, never copies files."""
from pathlib import Path
import sys
from flow import build_report,arrangement
SOURCE='layers-example.py · 虚构用户约定与实现，仅展示模板填写'
def cell(text,origin):return dict(text=text,origin=origin,source=SOURCE)
def item(label,purpose,agreement,actual,impact,**extra):
    return dict(label=label,purpose=purpose,
                specified=cell(agreement,'虚构用户约定'),choice=cell(actual,'虚构实现选择；非运行证据'),
                impact=impact,specification='unspecified',**extra)
def edge(a,b,label,agreement,actual,kind='data'):
    return dict(item(label,actual,agreement,actual,'仅表示此虚构实现的关系。'),**{'from':a,'to':b},kind=kind)
def handoff(direction,inner,outer,label,agreement,actual,**extra):
    return dict(item(label,actual,agreement,actual,'整个子框对应上层选中项；边界圆点不是新增步骤。'),direction=direction,inner=inner,outer=outer,**extra)
COPY='把指定的源文件复制到目标位置。'
PRESERVE='复制时不要覆盖已有文件。'
RESULT='告诉我这次复制的结果；失败时说明原因。'
CONTEXT={'purpose':'用虚构文件复制演示约定到实现的阅读路径。','inputs':'指定的源与目标文件。','outputs':'复制或跳过结果。','behavior':'约定在上层；实际分支和选择在下层。','boundaries':'不执行复制，也不证明真实文件系统行为。','acceptance':'仅演示模板；真实项目完成条件未约定。'}
REPORT=dict(root='agreements',data=dict(title='用户约定 → 实际流程 · 模板示例',date='虚构示例',perspective='realization',scope='仅演示模板，不是文件复制产品的运行检查。',project=dict(goal=COPY,scope='单文件复制的虚构例子。',constraints=PRESERVE,acceptance='真实产品验收未约定。'),source_html='<h2 id="example-source">完整示例来源</h2><p>三条虚构约定：复制指定文件、不覆盖已有文件、告知结果且失败时说明原因。假设实现只报告 failed，没有说明失败原因，用于演示红色偏差；另假设竞态下覆盖已有文件，用于演示违反“不覆盖”限制的突出标记；跳过、日志字段与排布是作者补充。不会执行文件复制，标色仅对照本例的假设。</p>'),
 summary='<p>先选约定，再展开实际流程。“复制时不要覆盖已有文件”与“告诉我这次复制的结果”可以精确跳到同一份流程；目标详情会自动提供返回链接。</p>',views={
 'agreements':dict(title='三条用户约定',layout=dict(kind='interaction',lanes=[['copy','preserve'],['result',None]]),nodes={
    'copy':item(COPY.rstrip('。'),'查看复制能力的实际处理过程。',COPY,'示例先处理目标重名，再复制或跳过，最后返回结果。','具体重名策略没有由用户逐项指定。',child='copy-flow'),
    'preserve':item(PRESERVE.rstrip('。'),'定位这条约定影响的实际步骤。',PRESERVE,'示例遇到已有目标就跳过；不存在时普通写入，假设竞态后覆盖已有文件。','用户也可能希望询问或改名；跳过是作者选择。',links=[{'target':'copy-flow--exists','label':'查看同一份重名处理'}]),
    'result':item(RESULT.split('；')[0],'查看共同流程怎样提供结果。',RESULT,'示例返回 copied/skipped 标记；跳过时另写原因日志。','状态字段和日志是作者补足的表达方式。',links=[{'target':'copy-flow--done','label':'查看同一份结果步骤'},{'target':'example-source','label':'查看完整示例来源'}])},
    edges=[edge('preserve','copy','约束目标写入',PRESERVE,'不覆盖约定适用于复制过程。','constraint')],fields=CONTEXT),
 'copy-flow':dict(title='复制能力的实际做法',layout=dict(kind='branch',decision='exists',branches=[['skip'],['write']],merge='done'),nodes={
    'exists':item('目标已存在？','在两种结果之间选择处理路径。',PRESERVE,'示例先检查目标是否存在，稍后使用普通覆盖写入。','检查本身不能消除并发竞争；实际写入还须遵守不覆盖。',shape='decision'),
    'skip':item('跳过并记录','解释用户未指定的跳过与日志策略。',PRESERVE,'已有文件时不写目标，写一条 filename/reason 日志。','保留目标文件；为何选择跳过而非改名是示例作者决定。',child='skip-detail'),
    'write':item('写入并复制','说明目标写入怎样避免覆盖。',PRESERVE,'示例设定：并发创建目标后，普通写入覆盖了已有文件。','真实文件系统和中断行为未核实；这不是可运行复制器。'),
    'done':item('返回结果','把本次结果交回调用方。',RESULT,'返回 copied 或 skipped；写入失败只报告 failed，不返回原因。','这是故意保留的虚构差异，用于演示如何标出未满足的要求。',shape='terminal')},
    edges=[edge('exists','skip','存在',PRESERVE,'存在时跳过。','flow'),edge('exists','write','不存在',PRESERVE,'尝试普通写入并复制；本例假设竞态目标被覆盖。','flow'),edge('skip','done','skipped',RESULT,'返回跳过结果。'),edge('write','done','复制或失败结果',RESULT,'按实际写入结果返回 copied 或失败。')],
    handoffs=[handoff('in','exists','copy','源与目标',COPY,'上层复制约定对应本层输入。'),handoff('out','done','result','本次结果',RESULT,'本层结果对应上层告知结果的约定。')],fields=CONTEXT),
 'skip-detail':dict(title='跳过结果的具体补充',layout=dict(kind='sequence',order=['reason','log']),nodes={
    'reason':item('整理跳过原因','给出为什么没有写入的解释。',RESULT,'原因写为 target_exists，并保留目标文件名。','字段名和错误分类是作者补充。'),
    'log':item('记录并返回','将原因留在日志并提供本次结果。',RESULT,'示例追加 filename/reason 日志，然后返回 skipped。','是否需要长期日志、保存多久未由用户约定；真实存储未核实。')},
    edges=[edge('reason','log','文件名与原因',RESULT,'传递要写入的结果说明。')],
    handoffs=[handoff('in','reason','exists','目标存在',PRESERVE,'上层已有目标分支进入跳过处理。',condition='存在'),handoff('out','log','done','skipped',RESULT,'把处理结果交回上层汇合点。')],fields=CONTEXT)
})
# A reverse local relation uses the clear gap between nodes, rather than a lower corridor.
boxes=arrangement(REPORT['views']['agreements']);x,y,w,h=boxes['copy'];right=boxes['preserve'][0]
REPORT['views']['agreements']['edges'][0]['route']=dict(ap='l',bp='r',via=[],at=((x+w+right)/2,y+h/2-14))
REPORT['views']['skip-detail']['nodes']['log']['choice']['diagram']=dict(label='示例日志选择',lanes=[['name','entry']],nodes={
    'name':dict(label='文件名与原因',specification='context',detail='本次跳过结果。'),
    'entry':dict(label='追加日志',title='将跳过结果写入额外日志',impact='增加一份用户未要求的记录。',specification='unspecified',detail='用户只要求知道结果，没有逐项要求日志。')},edges=[dict(**{'from':'name','to':'entry'},label='记录',title='把文件名和原因传给日志步骤',specification='unspecified',detail='这是示例的日志选择，不是用户指定。')])
REPORT['views']['copy-flow']['nodes']['skip']['comparisons']=[
    dict(kind='match',title='已有目标文件会被跳过',specified='不要覆盖已有文件',choice='已有文件时不写目标',note='本虚构设定中，这部分满足不覆盖要求；不代表真实文件系统验收。'),
    dict(kind='addition',title='额外记录文件名和跳过原因',impact='增加日志写入与保留；日志保存多久仍未约定。',choice='写一条 filename/reason 日志',note='用户没有指定额外日志和字段，这部分由示例作者补充。')]
REPORT['views']['copy-flow']['nodes']['done']['comparisons']=[dict(kind='mismatch',title='失败后只返回状态，没有原因',impact='用户知道失败了，却无法从结果知道失败原因。',specified='失败时说明原因',choice='只报告 failed，不返回原因',note='虚构要求需要原因，假设实现只有失败状态，缺少原因。')]
REPORT['views']['copy-flow']['nodes']['write']['choice']['text']+='真实文件系统和中断行为未核实。'
REPORT['views']['copy-flow']['nodes']['write']['comparisons']=[dict(kind='unverified',title='真实文件系统和中断行为尚未核实',choice='真实文件系统和中断行为未核实',note='这段属于实现验证缺口，不能据此判定用户要求未说明。')]
REPORT['views']['copy-flow']['nodes']['write']['comparisons'].insert(0,dict(kind='violation',title='竞态下已有文件被覆盖',impact='本虚构场景中，原目标内容会被替换，违反不覆盖限制。',specified='不要覆盖已有文件',choice='普通写入覆盖了已有文件',constraint_source=SOURCE+' · PRESERVE',note='仅在本虚构设定中，已设定的覆盖行为违背不覆盖限制；不是本项目或真实复制产品的发现。'))
REPORT['views']['skip-detail']['nodes']['log']['comparisons']=[dict(kind='addition',title='追加一条文件名和原因日志',impact='日志使跳过原因可追溯，同时增加未约定的持久记录。',choice='追加 filename/reason 日志',note='即使详情带小图，补充选择的原文标注也保持可见。')]
# Every known example choice has an authored headline; defaults remain for missing data.
for view,key,title in [('agreements','copy','复制前先检查目标是否重名'),('agreements','preserve','已有目标时选择跳过'),('agreements','result','用状态标记和日志告知结果'),('copy-flow','exists','先检查目标存在，再尝试写入'),('skip-detail','reason','把跳过原因写成 target_exists')]:
    row=REPORT['views'][view]['nodes'][key]
    row['comparisons']=[dict(kind='addition',title=title,choice=row['choice']['text'],note='虚构实现中具体采用的步骤或表达方式，未由该例用户逐项指定。')]
REPORT['views']['copy-flow']['nodes']['write']['specification']='specified'
REPORT['views']['copy-flow']['nodes']['done']['comparisons'].append(dict(kind='addition',title='用 copied 或 skipped 表示成功或跳过',choice='返回 copied 或 skipped',note='状态值是示例作者选择的表达方式。'))
for view,titles in [('agreements',['把不覆盖要求关联到复制过程']),('copy-flow',['目标存在时走跳过分支','目标不存在时尝试普通写入','用 skipped 报告跳过结果','按写入结果返回成功或失败']),('skip-detail',['把文件名和原因交给日志步骤'])]:
    for row,title in zip(REPORT['views'][view]['edges'],titles):
        row['comparisons']=[dict(kind='addition',title=title,choice=row['choice']['text'],note='本例作者定义的步骤关系与结果传递方式；不是实际复制产品证据。')]
for view,titles in [('copy-flow',['用源与目标进入复制处理','把本次复制结果交回上层']),('skip-detail',['目标存在时进入跳过处理','把 skipped 结果交回汇合点'])]:
    for row,title in zip(REPORT['views'][view]['handoffs'],titles):
        row['comparisons']=[dict(kind='addition',title=title,choice=row['choice']['text'],note='虚构图中作者提供的上下层对应，不代表新增实际执行步骤。')]
if __name__=='__main__':
    print(build_report(REPORT,Path(sys.argv[1]) if len(sys.argv)>1 else Path('/tmp/semantic-layered-example')))
