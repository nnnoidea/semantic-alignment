# -*- coding: utf-8 -*-
"""Published dated check; rebuild with the templates in this repository."""
from pathlib import Path
import sys,re,html,posixpath
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
sys.path.insert(0,str(REPO/'assets/audit-svg'))
from flow import build_report
def md_html(text,sourcepath=None):
    out=[];paragraph=[];in_list=False
    def inline(s):
        s=html.escape(s)
        s=re.sub(r'`([^`]+)`',r'<code>\1</code>',s)
        def link(m):
            target=html.unescape(m[2])
            if sourcepath and not re.match(r'[a-z]+:',target):
                file,sep,fragment=target.partition('#')
                p=Path(posixpath.normpath(posixpath.join(posixpath.dirname(sourcepath),file))) if file else Path(sourcepath)
                if str(p) in {path for path,_ in BASELINE}:
                    target='#record-'+p.stem+'-'+fragment if sep else '#record-'+p.stem
                else:target='https://github.com/nnnoidea/semantic-alignment/blob/'+('main/' if str(p).startswith('docs/showcase/') else 'a6689abdd8a642f1eb2ae26625dcc9a59d484ccf/')+p.as_posix()+('#'+fragment if sep else '')
            return '<a href="'+html.escape(target,quote=True)+'">'+m[1]+'</a>'
        return re.sub(r'\[([^\]]+)\]\(([^)]+)\)',link,s)
    def flush():
        if paragraph:out.append('<p style="white-space:pre-wrap">'+inline('\n'.join(paragraph))+'</p>');paragraph.clear()
    anchors={'汇总遗漏了已经披露的选择':'summary-coverage','未提供实际做法，汇总却可能显示零项未核实':'summary-unknown','“图中详情与来源”先展开子图，详情仍关闭':'summary-navigation','产物反查：已识别的具体实现选择':'full-choices','可省附加机制':'optional','精确链接后，目标可能仍在画布外':'navigation-gap','缩写后的标签容易被读成完成结论':'wording-gap','可精简的旧输入分支':'legacy-input','11 个用户约定的核对':'current-coverage','查看、缩放、滚动、打印与样式':'reading'}
    for line in text.splitlines():
        m=re.match(r'^(#{1,6}) (.*)',line)
        if m:
            flush()
            if in_list:out.append('</ul>');in_list=False
            n=min(6,len(m[1])+1)
            if sourcepath:a=' id="record-'+Path(sourcepath).stem+'-'+re.sub(r'[^\w\- ]','',m[2].lower()).replace(' ','-')+'"'
            else:a=' id="'+anchors[m[2]]+'"' if m[2] in anchors else ''
            out.append(f'<h{n}'+a+'>'+inline(m[2])+f'</h{n}>')
        elif line.startswith('- '):
            flush()
            if not in_list:out.append('<ul>');in_list=True
            out.append('<li>'+inline(line[2:])+'</li>')
        elif not line:
            flush()
            if in_list:out.append('</ul>');in_list=False
        else:paragraph.append(line)
    flush()
    if in_list:out.append('</ul>')
    return ''.join(out)

REPORT = {'root': 'agreements',
 'views': {'agreements': {'title': '本次核对的用户约定',
                          'layout': {'kind': 'interaction',
                                     'lanes': [['records', 'check', 'summary'], ['choices', 'package', 'browse']]},
                          'nodes': {'records': {'label': '通过 md 文件来记录语义',
                                                'purpose': '核对“通过 md 文件来记录语义”对应的现状。',
                                                'specified': {'text': '就直接通过md文件来记录语义吧，整体记录，不再是一条一条的',
                                                              'source': '本会话原话或当前语义记录',
                                                              'origin': '用户原话／当前约定（下文按来源区分）'},
                                                'choice': {'text': '本项目入口44行，四份主题正文共11个约定；按目的、限制、用户约定和五字段保存，实际观察在检查/维护资料。\n'
                                                                   '\n'
                                                                   '本轮未重新核查其他项目的全部历史迁移。',
                                                           'source': 'SKILL.md',
                                                           'origin': '2026-11-09 静态核对'},
                                                'impact': '要求中的能力与具体实现选择分开判断；本轮仅检查，未修改正式代码。',
                                                'specification': 'specified',
                                                'comparisons': [{'kind': 'match',
                                                                 'note': '核对记录组织和当前来源分离；不据此证明全部历史迁移无遗漏。',
                                                                 'specified': '就直接通过md文件来记录语义吧，整体记录，不再是一条一条的',
                                                                 'choice': '本项目入口44行，四份主题正文共11个约定；按目的、限制、用户约定和五字段保存，实际观察在检查/维护资料。',
                                                                 'title': '用户约定已按 Markdown 和五字段保存'},
                                                                {'kind': 'unverified',
                                                                 'choice': '本轮未重新核查其他项目的全部历史迁移。',
                                                                 'note': '本项目当前格式一致，不替代其他项目逐项保真检查。',
                                                                 'title': '其他项目的历史迁移未重新核查'}]},
                                    'check': {'label': '是不是按我的要求做的',
                                              'purpose': '核对“是不是按我的要求做的”对应的现状。',
                                              'specified': {'text': '语义检查则是看代码是否符合用户的语义。普通代码审计不属于我们的范畴。',
                                                            'source': '本会话原话或当前语义记录',
                                                            'origin': '用户原话／当前约定（下文按来源区分）'},
                                              'choice': {'text': 'SKILL区分语义检查和普通代码审查，要求从用户约定和真实产物双向核查；规范不是自动执行的语义证明。\n'
                                                                 '\n'
                                                                 '宿主自动触发效果尚未实测。',
                                                         'source': 'SKILL.md',
                                                         'origin': '2026-11-09 静态核对'},
                                              'impact': '要求中的能力与具体实现选择分开判断；本轮仅检查，未修改正式代码。',
                                              'specification': 'specified',
                                              'comparisons': [{'kind': 'match',
                                                               'note': '这里确认任务边界与检查方法已写入指令；本次实作仍发现交付层缺口。',
                                                               'specified': '语义检查则是看代码是否符合用户的语义。普通代码审计不属于我们的范畴。',
                                                               'choice': 'SKILL区分语义检查和普通代码审查，要求从用户约定和真实产物双向核查；规范不是自动执行的语义证明。',
                                                               'title': '检查边界围绕用户意图'},
                                                              {'kind': 'unverified',
                                                               'choice': '宿主自动触发效果尚未实测。',
                                                               'note': '规范边界已核对，真实会话中的触发准确率仍没有本轮运行证据。',
                                                               'title': '自动触发效果尚未实测'}]},
                                    'summary': {'label': '只想看看汇总后的不一致',
                                                'purpose': '从用户的汇总要求进入当前生成和阅读流程。',
                                                'specified': {'text': '我感觉还需要一个汇总页面，毕竟用户也可能懒得仔细看，只想看看汇总后的不一致，这个得单独加 '
                                                                      '用户补充：需要突出显示跟“限制”相违背的差异，因为这是用户最关心的。 '
                                                                      '本轮用户确认：“可以，就按这个改汇总页和节点详情，把规则写进 '
                                                                      'skill，更新模板并同步安装版，再用本项目的报告展示一下效果。”',
                                                              'source': '本会话原话或当前语义记录',
                                                              'origin': '用户原话／当前约定（下文按来源区分）'},
                                                'choice': {'text': '独立summary.html已提供；本轮修复收集、未核实归集和详情跳转，并优先呈现已确认违反用户限制的差异。 '
                                                                   '汇总和节点详情先显示具体发现，再按需查看对照、影响和来源。 '
                                                                   '本轮另查出约定未核查标签及待定摘要提示的边界缺口，见状态对照子图。',
                                                           'source': 'assets/audit-svg/semantic_template.py',
                                                           'origin': '2026-11-09 静态核对'},
                                                'impact': '要求中的能力与具体实现选择分开判断；本轮仅检查，未修改正式代码。',
                                                'specification': 'specified',
                                                'child': 'summary-flow',
                                                'comparisons': [{'kind': 'match',
                                                                 'title': '已提供独立汇总与详情入口',
                                                                 'specified': '我感觉还需要一个汇总页面，毕竟用户也可能懒得仔细看，只想看看汇总后的不一致，这个得单独加 '
                                                                              '用户补充：需要突出显示跟“限制”相违背的差异，因为这是用户最关心的。',
                                                                 'choice': '独立summary.html已提供；本轮修复收集、未核实归集和详情跳转，并优先呈现已确认违反用户限制的差异。',
                                                                 'note': '依据已生成结构及此前检查范围；不由此推断全部行为已经验证。'},
                                                                {'kind': 'match',
                                                                 'title': '汇总和节点详情都先给出具体发现',
                                                                 'specified': '按这个改汇总页和节点详情',
                                                                 'choice': '汇总和节点详情先显示具体发现，再按需查看对照、影响和来源。',
                                                                 'note': '已按用户采纳的设计调整结构；真实浏览器排版仍未实测。'}]},
                                    'choices': {'label': '完整展示所有用户没明说的选择',
                                                'purpose': '把具体实现策略集中供用户查看，不将额外选择一概算作缺陷。',
                                                'specified': {'text': '要完整展示所有用户没明说的选择，不要只挑几个重要的。',
                                                              'source': '本会话原话或当前语义记录',
                                                              'origin': '用户原话／当前约定（下文按来源区分）'},
                                                'choice': {'text': '下层保留输入/写出、布局、来源/状态、查看/样式、输出检查及共享导航的具体做法和数值；依当前源码反查，未知外部行为仍注明。',
                                                           'source': 'assets/audit-svg',
                                                           'origin': '2026-11-09 静态核对'},
                                                'impact': '要求中的能力与具体实现选择分开判断；本轮仅检查，未修改正式代码。',
                                                'specification': 'specified',
                                                'child': 'implementation-choices',
                                                'comparisons': [{'kind': 'match',
                                                                 'title': '已识别的实现选择按主题保留',
                                                                 'specified': '要完整展示所有用户没明说的选择，不要只挑几个重要的。',
                                                                 'choice': '下层保留输入/写出、布局、来源/状态、查看/样式、输出检查及共享导航的具体做法和数值；依当前源码反查，未知外部行为仍注明。',
                                                                 'note': '依据已生成结构及此前检查范围；不由此推断全部行为已经验证。'}]},
                                    'package': {'label': '同步更新已安装的 skill',
                                                'purpose': '核对“同步更新已安装的 skill”对应的现状。',
                                                'specified': {'text': '并同步更新已安装的 skill',
                                                              'source': '本会话原话或当前语义记录',
                                                              'origin': '用户原话／当前约定（下文按来源区分）'},
                                                'choice': {'text': '正式执行包与安装副本16个文件逐字节一致；四份中文审阅文件和代码示例对应。TaskMemory配置enabled=false，未核对所有后台进程。',
                                                           'source': '.',
                                                           'origin': '2026-11-09 静态核对'},
                                                'impact': '要求中的能力与具体实现选择分开判断；本轮仅检查，未修改正式代码。',
                                                'specification': 'specified',
                                                'comparisons': [{'kind': 'match',
                                                                 'note': '限定为本地文件与已读配置事实，宿主自动触发效果仍未实测。',
                                                                 'specified': '并同步更新已安装的 skill',
                                                                 'choice': '正式执行包与安装副本16个文件逐字节一致',
                                                                 'title': '安装副本与正式执行包一致'},
                                                                {'kind': 'unverified',
                                                                 'choice': '未核对所有后台进程',
                                                                 'note': '已读配置停用TaskMemory，不能据此证明所有既有进程均已停止。',
                                                                 'title': '后台进程状态未全量核对'}]},
                                    'browse': {'label': '图能放大缩小滑动',
                                               'purpose': '核对“图能放大缩小滑动”对应的现状。',
                                               'specified': {'text': '图能放大缩小滑动，点击节点或关系后能在下面或侧面展示详细信息，也就够了',
                                                             'source': '本会话原话或当前语义记录',
                                                             'origin': '用户原话／当前约定（下文按来源区分）'},
                                               'choice': {'text': '缩放、滚动、拖动、逐层展开与详情代码具备；入口已移到标题下并放大。真实浏览器中的可发现性、连续点击、窄屏和打印未实测。',
                                                          'source': 'assets/audit-svg/viewer.js',
                                                          'origin': '2026-11-09 静态核对'},
                                               'impact': '要求中的能力与具体实现选择分开判断；本轮仅检查，未修改正式代码。',
                                               'specification': 'specified',
                                               'comparisons': [{'kind': 'unverified',
                                                                'note': '只验证代码与产物结构，当前仍不能声称真实阅读体验通过。',
                                                                'specified': '图能放大缩小滑动，点击节点或关系后能在下面或侧面展示详细信息，也就够了',
                                                                'choice': '缩放、滚动、拖动、逐层展开与详情代码具备；入口已移到标题下并放大。真实浏览器中的可发现性、连续点击、窄屏和打印未实测。',
                                                                'title': '真实浏览器中的查看体验尚未实测'}]}},
                          'edges': [{'from': 'records',
                                     'to': 'check',
                                     'label': '语义作为依据',
                                     'kind': 'data',
                                     'specification': 'specified',
                                     'purpose': '表示报告与证据之间的关系。',
                                     'specified': {'text': '检查发现、图、详情和完整原文互相对应。',
                                                   'source': 'docs/showcase/semantics/audit.md',
                                                   'origin': '当前记录原文'},
                                     'choice': {'text': '语义作为依据', 'source': '本报告组织', 'origin': 'Agent 按源码或报告结构归纳'},
                                     'impact': '关系用于阅读，不替代实现已通过的结论。'},
                                    {'from': 'check',
                                     'to': 'summary',
                                     'label': '检查结果输出',
                                     'kind': 'data',
                                     'specification': 'specified',
                                     'purpose': '表示报告与证据之间的关系。',
                                     'specified': {'text': '检查发现、图、详情和完整原文互相对应。',
                                                   'source': 'docs/showcase/semantics/audit.md',
                                                   'origin': '当前记录原文'},
                                     'choice': {'text': '检查结果输出', 'source': '本报告组织', 'origin': 'Agent 按源码或报告结构归纳'},
                                     'impact': '关系用于阅读，不替代实现已通过的结论。'},
                                    {'from': 'choices',
                                     'to': 'check',
                                     'label': '从产物反查',
                                     'kind': 'data',
                                     'specification': 'specified',
                                     'purpose': '表示报告与证据之间的关系。',
                                     'specified': {'text': '检查发现、图、详情和完整原文互相对应。',
                                                   'source': 'docs/showcase/semantics/audit.md',
                                                   'origin': '当前记录原文'},
                                     'choice': {'text': '从产物反查', 'source': '本报告组织', 'origin': 'Agent 按源码或报告结构归纳'},
                                     'impact': '关系用于阅读，不替代实现已通过的结论。'},
                                    {'from': 'summary',
                                     'to': 'browse',
                                     'label': '按需看详情',
                                     'kind': 'data',
                                     'specification': 'specified',
                                     'purpose': '表示报告与证据之间的关系。',
                                     'specified': {'text': '检查发现、图、详情和完整原文互相对应。',
                                                   'source': 'docs/showcase/semantics/audit.md',
                                                   'origin': '当前记录原文'},
                                     'choice': {'text': '按需看详情', 'source': '本报告组织', 'origin': 'Agent 按源码或报告结构归纳'},
                                     'impact': '关系用于阅读，不替代实现已通过的结论。'},
                                    {'from': 'package',
                                     'to': 'browse',
                                     'label': '提供当前模板',
                                     'kind': 'constraint',
                                     'specification': 'specified',
                                     'purpose': '表示报告与证据之间的关系。',
                                     'specified': {'text': '检查发现、图、详情和完整原文互相对应。',
                                                   'source': 'docs/showcase/semantics/audit.md',
                                                   'origin': '当前记录原文'},
                                     'choice': {'text': '提供当前模板', 'source': '本报告组织', 'origin': 'Agent 按源码或报告结构归纳'},
                                     'impact': '关系用于阅读，不替代实现已通过的结论。'}],
                          'fields': {'purpose': '按当前约定查看本次检查结论。',
                                     'inputs': '本会话及当前用户约定；当前源码与检查证据。',
                                     'outputs': '对应要求的落实、已识别选择、缺口和未核实范围。',
                                     'behavior': '区分用户要求、实际观察与Agent判断；具体对应见图中关系。',
                                     'boundaries': '本轮语义检查不修改产品；不等同普通代码审查或浏览器验收。',
                                     'acceptance': '依当前阶段约定核对；未额外约定的新验收条件保持未约定。'}},
           'summary-flow': {'title': '独立汇总：从已记录发现到阅读详情',
                            'layout': {'kind': 'sequence', 'order': ['collect', 'unknown', 'render', 'link']},
                            'nodes': {'collect': {'label': '收集差异',
                                                  'purpose': '核对“收集差异”对应的现状。',
                                                  'specified': {'text': '要完整展示所有用户没明说的选择，不要只挑几个重要的。',
                                                                'source': '本会话原话或当前语义记录',
                                                                'origin': '用户原话／当前约定（下文按来源区分）'},
                                                  'choice': {'text': '本报告的已识别选择统一进入对照输入，已覆盖缩放、滚轮、编码等原漏项；生成器逐项收集简图节点与边，不以正文已有一条addition代替整个简图。',
                                                             'source': 'assets/audit-svg/semantic_template.py',
                                                             'origin': '2026-11-09 静态核对'},
                                                  'impact': '修复沿用已有用户要求，不新增审批或改变普通节点的展开方式。浏览器效果的验证范围见报告。',
                                                  'specification': 'specified',
                                                  'comparisons': [{'kind': 'match',
                                                                   'specified': '要完整展示所有用户没明说的选择，不要只挑几个重要的。',
                                                                   'choice': '本报告的已识别选择统一进入对照输入，已覆盖缩放、滚轮、编码等原漏项；生成器逐项收集简图节点与边，不以正文已有一条addition代替整个简图。',
                                                                   'note': '通过本报告明细逐项核对和正文A＋简图B反例；自由Markdown仍需作者进入对应输入，并在交付前核对。',
                                                                   'title': '已记录的选择进入同一份汇总'}]},
                                      'unknown': {'label': '保留未核实事项',
                                                  'purpose': '核对“保留未核实事项”对应的现状。',
                                                  'specified': {'text': '缺少语义内容仍显示缺少，未核查、未核实和未约定分别表达。',
                                                                'source': '本会话原话或当前语义记录',
                                                                'origin': '用户原话／当前约定（下文按来源区分）'},
                                                  'choice': {'text': '缺少或仅空白choice正文时，详情保留未核实说明，汇总也保留验证缺口；原有source、context和diagram不会丢失，用户要求仍保持specified。',
                                                             'source': 'assets/audit-svg/semantic_template.py',
                                                             'origin': '2026-11-09 静态核对'},
                                                  'impact': '修复沿用已有用户要求，不新增审批或改变普通节点的展开方式。浏览器效果的验证范围见报告。',
                                                  'specification': 'specified',
                                                  'comparisons': [{'kind': 'match',
                                                                   'specified': '缺少语义内容仍显示缺少，未核查、未核实和未约定分别表达。',
                                                                   'choice': '缺少或仅空白choice正文时，详情保留未核实说明，汇总也保留验证缺口；原有source、context和diagram不会丢失，用户要求仍保持specified。',
                                                                   'note': '原单节点生成反例现得到unverified=1，空白/字典缺正文亦通过；没有把已指定要求改成未指定。',
                                                                   'title': '缺少实际做法时仍显示未核实'}],
                                                  'child': 'status-check'},
                                      'render': {'label': '生成独立汇总',
                                                 'purpose': '核对“生成独立汇总”对应的现状。',
                                                 'specified': {'text': '这个得单独加。',
                                                               'source': '本会话原话或当前语义记录',
                                                               'origin': '用户原话／当前约定（下文按来源区分）'},
                                                 'choice': {'text': '生成独立summary.html；违反用户限制优先，其他偏离/遗漏、Agent补充和未核实分别列出；对照与来源仍能展开查看。',
                                                            'source': 'assets/audit-svg/layers.py:202',
                                                            'origin': '2026-11-09 静态核对'},
                                                 'impact': '要求中的能力与具体实现选择分开判断；本轮仅检查，未修改正式代码。',
                                                 'specification': 'specified',
                                                 'comparisons': [{'kind': 'match',
                                                                  'note': '独立交付和优先呈现已有对应模板；具体分类须由作者基于证据填写。',
                                                                  'specified': '这个得单独加。',
                                                                  'choice': '生成独立summary.html；违反用户限制优先，其他偏离/遗漏、Agent补充和未核实分别列出；对照与来源仍能展开查看。',
                                                                  'title': '汇总优先展示违反用户限制'}]},
                                      'link': {'label': '打开详情与来源',
                                               'purpose': '核对“打开详情与来源”对应的现状。',
                                               'specified': {'text': '点击节点或关系后能在下面或侧面展示详细信息。',
                                                             'source': '本会话原话或当前语义记录',
                                                             'origin': '用户原话／当前约定（下文按来源区分）'},
                                               'choice': {'text': '汇总链接改用#inspect-view--node，打开目标自己的inspector；有child也直接打开本项详情并保留祖先图。普通图节点仍展开子流程。',
                                                          'source': 'assets/audit-svg/viewer.js',
                                                          'origin': '2026-11-09 静态核对'},
                                               'impact': '修复沿用已有用户要求，不新增审批或改变普通节点的展开方式。浏览器效果的验证范围见报告。',
                                               'specification': 'specified',
                                               'comparisons': [{'kind': 'match',
                                                                'specified': '点击节点或关系后能在下面或侧面展示详细信息。',
                                                                'choice': '汇总链接改用#inspect-view--node，打开目标自己的inspector；有child也直接打开本项详情并保留祖先图。普通图节点仍展开子流程。',
                                                                'note': '源码分支、JavaScript语法与生成目标检查通过；真实浏览器点击仍未实测。',
                                                                'title': '汇总链接直接打开该项详情'}]}},
                            'edges': [{'from': 'collect',
                                       'to': 'unknown',
                                       'label': '追加状态兜底',
                                       'kind': 'flow',
                                       'specification': 'specified',
                                       'purpose': '表示报告与证据之间的关系。',
                                       'specified': {'text': '检查发现、图、详情和完整原文互相对应。',
                                                     'source': 'docs/showcase/semantics/audit.md',
                                                     'origin': '当前记录原文'},
                                       'choice': {'text': '追加状态兜底', 'source': '本报告组织', 'origin': 'Agent 按源码或报告结构归纳'},
                                       'impact': '关系用于阅读，不替代实现已通过的结论。'},
                                      {'from': 'unknown',
                                       'to': 'render',
                                       'label': '归集条目',
                                       'kind': 'data',
                                       'specification': 'specified',
                                       'purpose': '表示报告与证据之间的关系。',
                                       'specified': {'text': '检查发现、图、详情和完整原文互相对应。',
                                                     'source': 'docs/showcase/semantics/audit.md',
                                                     'origin': '当前记录原文'},
                                       'choice': {'text': '归集条目', 'source': '本报告组织', 'origin': 'Agent 按源码或报告结构归纳'},
                                       'impact': '关系用于阅读，不替代实现已通过的结论。'},
                                      {'from': 'render',
                                       'to': 'link',
                                       'label': '点击条目后',
                                       'kind': 'data',
                                       'specification': 'specified',
                                       'purpose': '表示报告与证据之间的关系。',
                                       'specified': {'text': '检查发现、图、详情和完整原文互相对应。',
                                                     'source': 'docs/showcase/semantics/audit.md',
                                                     'origin': '当前记录原文'},
                                       'choice': {'text': '点击条目后', 'source': '本报告组织', 'origin': 'Agent 按源码或报告结构归纳'},
                                       'impact': '关系用于阅读，不替代实现已通过的结论。'}],
                            'handoffs': [{'label': '已记录发现',
                                          'kind': 'constraint',
                                          'specification': 'specified',
                                          'purpose': '表示报告与证据之间的关系。',
                                          'specified': {'text': '检查发现、图、详情和完整原文互相对应。',
                                                        'source': 'docs/showcase/semantics/audit.md',
                                                        'origin': '当前记录原文'},
                                          'choice': {'text': '检查时以这些材料建立对应关系，不表示产品自动运行步骤。',
                                                     'source': '本报告组织',
                                                     'origin': 'Agent 按源码或报告结构归纳'},
                                          'impact': '关系用于阅读，不替代实现已通过的结论。',
                                          'direction': 'in',
                                          'inner': 'collect',
                                          'outer': 'check'},
                                         {'label': '对应详情',
                                          'kind': 'constraint',
                                          'specification': 'specified',
                                          'purpose': '表示报告与证据之间的关系。',
                                          'specified': {'text': '检查发现、图、详情和完整原文互相对应。',
                                                        'source': 'docs/showcase/semantics/audit.md',
                                                        'origin': '当前记录原文'},
                                          'choice': {'text': '检查时以这些材料建立对应关系，不表示产品自动运行步骤。',
                                                     'source': '本报告组织',
                                                     'origin': 'Agent 按源码或报告结构归纳'},
                                          'impact': '关系用于阅读，不替代实现已通过的结论。',
                                          'direction': 'out',
                                          'inner': 'link',
                                          'outer': 'browse'}],
                            'fields': {'purpose': '核对汇总的三处缺口。',
                                       'inputs': '本会话及当前用户约定；当前源码与检查证据。',
                                       'outputs': '对应要求的落实、已识别选择、缺口和未核实范围。',
                                       'behavior': '区分用户要求、实际观察与Agent判断；具体对应见图中关系。',
                                       'boundaries': '本轮语义检查不修改产品；不等同普通代码审查或浏览器验收。',
                                       'acceptance': '依当前阶段约定核对；未额外约定的新验收条件保持未约定。'}},
           'implementation-choices': {'title': '已识别实现选择：按作用分组',
                                      'level_label': '实现分工与选择',
                                      'layout': {'kind': 'interaction',
                                                 'lanes': [['load', 'layout', 'viewer'],
                                                           ['meaning', 'links', 'check']]},
                                      'nodes': {'load': {'label': '输入与文件',
                                                         'purpose': '披露输入与文件的具体实现方法、参数和条件。',
                                                         'specified': {'text': '要完整展示所有用户没明说的选择，不要只挑几个重要的。',
                                                                       'source': '本会话原话或当前语义记录',
                                                                       'origin': '用户原话／当前约定（下文按来源区分）'},
                                                         'choice': {'text': 'flow.py：Python 标准库+本地模块；CLI 用 '
                                                                            'argparse，位置参数为可信 report.py 和输出目录，--check '
                                                                            '只检查已有 index.html；runpy.run_path 执行输入整个 '
                                                                            'Python 文件再读取 REPORT，不是安全解析 '
                                                                            'Markdown，也不是沙箱；缺少 output 由 argparse '
                                                                            '报错；异常不做统一转换。输入可包含任何受进程权限允许的 Python '
                                                                            '副作用，能力由“trusted local '
                                                                            'Python”说明暴露，未提供安全隔离承诺。\n'
                                                                            '\n'
                                                                            'flow.py：仅接受 perspective '
                                                                            'None/realization；先取 '
                                                                            'root/data/views，计算每张布局、建立 '
                                                                            'key，再验证层级，随后按遍历顺序绘图；关系 endpoints '
                                                                            '必须存在；先画组框、再节点、再关系、再边界；source_html '
                                                                            '前面自动加项目与每视图语义字段；无字段则显示“缺少”。每视图可覆盖 '
                                                                            'level_label，否则显示“用户约定／实际流程／关键步骤”；名称是呈现用语，不判定语义身份。summary/source_html '
                                                                            '作为可信 HTML直插；source cell 文本转义。具体 HTML '
                                                                            '输入权限未由用户规定。\n'
                                                                            '\n'
                                                                            'layers.py：mkdir(parents=True,exist_ok=True)，依视图写 '
                                                                            '<key>.svg 再写 '
                                                                            'index.html、summary.html，路径相同则覆盖；旧目录其他旧 '
                                                                            'SVG 不删除；Path.read_text/write_text 未指定 '
                                                                            'encoding，使用 Python 平台默认；先落盘再 flow.py '
                                                                            '检查；失败可留下部分/未通过产物，没有临时目录原子发布、自动清理或版本回滚。记录已明确“失败后保留哪些输出尚未约定”，不能虚构发布保证。\n'
                                                                            '\n'
                                                                            'layers.py：本地锚点按最长 key 优先字符串替换；SVG '
                                                                            'id、data-key、aria-labelledby、marker URL 加 '
                                                                            'view 前缀；仅已发出的本地目标被重写，外部 URL/报告锚点保留；共享流程用 '
                                                                            'links 的精确引用及自动返回，不能多父重复展开；视图 key 用 '
                                                                            '[a-zA-Z][\\w-]* 且禁 --。输出独立 SVG静态，HTML '
                                                                            '复制后去掉每图图例，统一 HTML 图例补充说明。无网络资源、无服务。\n'
                                                                            '\n'
                                                                            '输出更新：先逐图SVG、再index.html、再summary.html，最后check_report。汇总共享viewer.css并内联；两HTML相对链接需要并放，报告summary里的本地锚点替换成index.html#。跨页检查仅核对目标存在、ID唯一和主报告链接，不判内容漏项或点击后的打开状态。',
                                                                    'source': 'assets/audit-svg',
                                                                    'origin': '2026-11-09 静态核对'},
                                                         'impact': {'text': '这些选择决定输入怎样执行、文件怎样写入以及失败后保留什么。相同目录可能同时存在被覆盖的新报告和本轮未使用的旧图。',
                                                                    'origin': 'Agent 根据当前实现归纳',
                                                                    'source': '本次报告；对应文件与参数见实际做法'},
                                                         'specification': 'specified',
                                                         'comparisons': [{'kind': 'addition',
                                                                          'choice': 'flow.py：Python 标准库+本地模块',
                                                                          'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                          'title': '生成器使用 Python 标准库和本地模块'},
                                                                         {'kind': 'addition',
                                                                          'choice': 'CLI 用 argparse，位置参数为可信 report.py '
                                                                                    '和输出目录，--check 只检查已有 index.html',
                                                                          'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                          'title': '命令行接收报告输入和输出目录'},
                                                                         {'kind': 'addition',
                                                                          'choice': 'runpy.run_path 执行输入整个 Python '
                                                                                    '文件再读取 REPORT，不是安全解析 '
                                                                                    'Markdown，也不是沙箱',
                                                                          'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                          'title': '报告输入会作为 Python 程序执行',
                                                                          'impact': '报告输入中的 Python 操作会在当前进程权限下执行。'},
                                                                         {'kind': 'addition',
                                                                          'choice': '缺少 output 由 argparse 报错',
                                                                          'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                          'title': '未指定输出目录时直接报错'},
                                                                         {'kind': 'addition',
                                                                          'choice': '异常不做统一转换。输入可包含任何受进程权限允许的 Python '
                                                                                    '副作用，能力由“trusted local '
                                                                                    'Python”说明暴露，未提供安全隔离承诺。',
                                                                          'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                          'title': '输入脚本可以执行当前权限允许的操作'},
                                                                         {'kind': 'addition',
                                                                          'choice': 'flow.py：仅接受 perspective '
                                                                                    'None/realization',
                                                                          'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                          'title': '只接受当前实现对照模式'},
                                                                         {'kind': 'addition',
                                                                          'choice': '先取 root/data/views，计算每张布局、建立 '
                                                                                    'key，再验证层级，随后按遍历顺序绘图',
                                                                          'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                          'title': '先计算布局，再校验层级并绘图'},
                                                                         {'kind': 'addition',
                                                                          'choice': '关系 endpoints 必须存在',
                                                                          'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                          'title': '连线两端必须是已经存在的节点'},
                                                                         {'kind': 'addition',
                                                                          'choice': '先画组框、再节点、再关系、再边界',
                                                                          'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                          'title': '组框、节点、关系和边界依次绘制'},
                                                                         {'kind': 'addition',
                                                                          'choice': 'source_html 前面自动加项目与每视图语义字段',
                                                                          'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                          'title': '全文前面会补入项目及视图的语义字段'},
                                                                         {'kind': 'addition',
                                                                          'choice': '无字段则显示“缺少”。每视图可覆盖 '
                                                                                    'level_label，否则显示“用户约定／实际流程／关键步骤”',
                                                                          'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                          'title': '缺字段会写“缺少”，层级标题可由作者覆盖'},
                                                                         {'kind': 'addition',
                                                                          'choice': '名称是呈现用语，不判定语义身份。summary/source_html '
                                                                                    '作为可信 HTML直插',
                                                                          'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                          'title': '报告摘要和全文接受可信 HTML'},
                                                                         {'kind': 'addition',
                                                                          'choice': 'source cell 文本转义。具体 HTML '
                                                                                    '输入权限未由用户规定。',
                                                                          'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                          'title': '来源单元格按文字转义显示'},
                                                                         {'kind': 'addition',
                                                                          'choice': 'layers.py：mkdir(parents=True,exist_ok=True)，依视图写 '
                                                                                    '<key>.svg 再写 '
                                                                                    'index.html、summary.html，路径相同则覆盖',
                                                                          'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                          'title': '再次生成会覆盖同名报告',
                                                                          'impact': '再次输出到同一路径时，原同名文件会被替换。'},
                                                                         {'kind': 'addition',
                                                                          'choice': '旧目录其他旧 SVG 不删除',
                                                                          'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                          'title': '本轮不用的旧 SVG 会留在输出目录',
                                                                          'impact': '目录中可能保留本轮报告不再使用的旧图。'},
                                                                         {'kind': 'addition',
                                                                          'choice': 'Path.read_text/write_text 未指定 '
                                                                                    'encoding，使用 Python 平台默认',
                                                                          'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                          'title': '文件读写沿用 Python 默认编码'},
                                                                         {'kind': 'addition',
                                                                          'choice': '先落盘再 flow.py 检查',
                                                                          'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                          'title': '报告先写入磁盘，再执行检查'},
                                                                         {'kind': 'addition',
                                                                          'choice': '失败可留下部分/未通过产物，没有临时目录原子发布、自动清理或版本回滚。记录已明确“失败后保留哪些输出尚未约定”，不能虚构发布保证。',
                                                                          'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                          'title': '检查失败不会自动回滚已写出的文件'},
                                                                         {'kind': 'addition',
                                                                          'choice': 'layers.py：本地锚点按最长 key 优先字符串替换',
                                                                          'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                          'title': '本地锚点优先替换较长的键名'},
                                                                         {'kind': 'addition',
                                                                          'choice': 'SVG '
                                                                                    'id、data-key、aria-labelledby、marker '
                                                                                    'URL 加 view 前缀',
                                                                          'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                          'title': 'SVG 标识统一加上视图前缀'},
                                                                         {'kind': 'addition',
                                                                          'choice': '仅已发出的本地目标被重写，外部 URL/报告锚点保留',
                                                                          'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                          'title': '外部地址和全文锚点保留原链接'},
                                                                         {'kind': 'addition',
                                                                          'choice': '共享流程用 links 的精确引用及自动返回，不能多父重复展开',
                                                                          'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                          'title': '共享流程通过引用连接，只有一个展开归属'},
                                                                         {'kind': 'addition',
                                                                          'choice': '视图 key 用 [a-zA-Z][\\w-]* 且禁 '
                                                                                    '--。输出独立 SVG静态，HTML 复制后去掉每图图例，统一 '
                                                                                    'HTML 图例补充说明。无网络资源、无服务。',
                                                                          'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                          'title': '视图名称受限，独立 SVG 是静态输出'},
                                                                         {'kind': 'addition',
                                                                          'choice': '输出更新：先逐图SVG、再index.html、再summary.html，最后check_report。汇总共享viewer.css并内联',
                                                                          'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                          'title': '先写图和两个网页，最后检查产物'},
                                                                         {'kind': 'addition',
                                                                          'choice': '两HTML相对链接需要并放，报告summary里的本地锚点替换成index.html#。跨页检查仅核对目标存在、ID唯一和主报告链接，不判内容漏项或点击后的打开状态。',
                                                                          'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                          'title': '两个网页必须一起保存才能相互跳转'}]},
                                                'layout': {'label': '布局与路由',
                                                           'purpose': '披露布局与路由的具体实现方法、参数和条件。',
                                                           'specified': {'text': '要完整展示所有用户没明说的选择，不要只挑几个重要的。\n'
                                                                                 '\n'
                                                                                 '当前约定摘录：标记不表示实现通过或用户认可。',
                                                                         'source': '本会话原话或当前语义记录；semantic-alignment-project/semantics/audit.md',
                                                                         'origin': '用户原话／当前约定（下文按来源区分）'},
                                                           'choice': {'text': 'flow.py：sequence 一行；branch '
                                                                              '至少两支、一支有内部节点，decision 放首列中间、merge '
                                                                              '放最长支后一列，空支是 bypass；wait '
                                                                              '为两行，worker_start 默认1；interaction 按 '
                                                                              'lanes，None '
                                                                              '留空；每节点必须且只能放一次，位置不推导边。节点宽=文字估宽与40 '
                                                                              'padding，最小220最大320；decision '
                                                                              '文字按0.7可用宽；高度至少80、每行27+44，decision '
                                                                              '至少120；列间隙至少240或边标签估宽+32；child 默认 '
                                                                              'x=240+max(260,入口标签宽)，y=175，root '
                                                                              'x=80,y=125；行间距 height+120；positions '
                                                                              '可逐节点四元组覆盖，非法 key/长度拒绝。\n'
                                                                              '\n'
                                                                              'flow.py、components.py:7–21：字符码>255按1 '
                                                                              'em，其余0.57 '
                                                                              'em估算，不按实际字体测量；逐字符断行，空文返回一空行；txt '
                                                                              '行距1.35倍；rect '
                                                                              '默认圆角6、线宽2。边同排向右/同列无遮挡直连；跨行向右经中间x正交；返回/跳跃走底部 '
                                                                              'maxbottom+70+track×36，自环右侧45再回底边。复杂图仍可 '
                                                                              'route 覆盖，不保证标签和边之间完全无重叠。\n'
                                                                              '\n'
                                                                              'flow.py：handoff优先边界节点且同向端口相隔>100，否则选底部+100走廊；若被节点挡而上方有空间，使用 '
                                                                              'minY−45 '
                                                                              '且端口间隔>75；侧边走廊至少260；组框成员外扩左右25、上65、下25；根宽至少1000且边缘80，高底部+135；child宽 '
                                                                              'frame_right+240，高bottom+180。\n'
                                                                              '\n'
                                                                              'architecture.py：box/terminal/doc/decision四形，doc折角18，terminal半高圆角，其他圆角12；节点字体20、颜色#234839、weight550，节点文字27行距；实际形状只代表作者给定类别；主边线宽2.4、点击透明线宽16。flow深灰#415c69、data蓝#397dab、constraint灰#8296a7无箭头且6/5虚线、error#b66050有箭头虚线；relation默认#51839a蓝箭头；conditional也虚线。其具体颜色、字号、圆角、padding是模板选择，用户只约定使用模板/完整图例。\n'
                                                                              '\n'
                                                                              'architecture.py：七项主图例，违反限制/有依据/组织/未指定/未核查/待定/关联；green不表示通过；橙轮廓未指定、灰点线未核查、紫待定，混合时橙描边兼两个角标；角标文字11、宽len×11+16，溢出则上移22；焦点/选中深蓝#245dce线宽3。定义图例、含未指定细节/细节未核查/方案待定和展开↓为固定中文；角色 '
                                                                              'button、tabindex=0、aria label以及 SVG '
                                                                              'desc由正文去标签而成。',
                                                                      'source': 'assets/audit-svg',
                                                                      'origin': '2026-11-09 静态核对'},
                                                           'impact': {'text': '这些参数决定图的尺寸、换行、间距和连线路径。模板会估算布局；复杂图可能需要作者局部调整。',
                                                                      'origin': 'Agent 根据当前实现归纳',
                                                                      'source': '本次报告；对应文件与参数见实际做法'},
                                                           'specification': 'specified',
                                                           'comparisons': [{'kind': 'addition',
                                                                            'choice': 'flow.py：sequence 一行',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '顺序布局把步骤排成一行'},
                                                                           {'kind': 'addition',
                                                                            'choice': 'branch 至少两支、一支有内部节点，decision '
                                                                                      '放首列中间、merge 放最长支后一列，空支是 bypass',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '分支布局把判断放前面、汇合放后面'},
                                                                           {'kind': 'addition',
                                                                            'choice': 'wait 为两行，worker_start 默认1',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '等待布局默认把工作分支放在第二行'},
                                                                           {'kind': 'addition',
                                                                            'choice': 'interaction 按 lanes，None 留空',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '交互布局允许用空位对齐不同泳道'},
                                                                           {'kind': 'addition',
                                                                            'choice': '每节点必须且只能放一次，位置不推导边。节点宽=文字估宽与40 '
                                                                                      'padding，最小220最大320',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '节点宽度按文字估算并限制在 220–320'},
                                                                           {'kind': 'addition',
                                                                            'choice': 'decision 文字按0.7可用宽',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '判断框只用七成宽度放文字'},
                                                                           {'kind': 'addition',
                                                                            'choice': '高度至少80、每行27+44，decision 至少120',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '节点高度随文字增加，判断框有更高的下限'},
                                                                           {'kind': 'addition',
                                                                            'choice': '列间隙至少240或边标签估宽+32',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '列间距会为连线标签留出空间'},
                                                                           {'kind': 'addition',
                                                                            'choice': 'child 默认 '
                                                                                      'x=240+max(260,入口标签宽)，y=175，root '
                                                                                      'x=80,y=125',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '根图和子图使用不同的默认起点'},
                                                                           {'kind': 'addition',
                                                                            'choice': '行间距 height+120',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '每行节点之间额外留出 120 的间距'},
                                                                           {'kind': 'addition',
                                                                            'choice': 'positions 可逐节点四元组覆盖，非法 '
                                                                                      'key/长度拒绝。',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '作者可以逐个覆盖节点位置'},
                                                                           {'kind': 'addition',
                                                                            'choice': 'flow.py、components.py:7–21：字符码>255按1 '
                                                                                      'em，其余0.57 em估算，不按实际字体测量',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '文字宽度按字符类型估算'},
                                                                           {'kind': 'addition',
                                                                            'choice': '逐字符断行，空文返回一空行',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '文字逐字换行，空文字仍占一行'},
                                                                           {'kind': 'addition',
                                                                            'choice': 'txt 行距1.35倍',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '普通 SVG 文字使用 1.35 倍行距'},
                                                                           {'kind': 'addition',
                                                                            'choice': 'rect 默认圆角6、线宽2。边同排向右/同列无遮挡直连',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '同排或同列且无遮挡时直接连线'},
                                                                           {'kind': 'addition',
                                                                            'choice': '跨行向右经中间x正交',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '跨行向右的连线经中间竖线转弯'},
                                                                           {'kind': 'addition',
                                                                            'choice': '返回/跳跃走底部 '
                                                                                      'maxbottom+70+track×36，自环右侧45再回底边。复杂图仍可 '
                                                                                      'route 覆盖，不保证标签和边之间完全无重叠。',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '返回、跳跃和自环默认走下方通道'},
                                                                           {'kind': 'addition',
                                                                            'choice': 'flow.py：handoff优先边界节点且同向端口相隔>100，否则选底部+100走廊',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '边界交接优先从靠边节点直连'},
                                                                           {'kind': 'addition',
                                                                            'choice': '若被节点挡而上方有空间，使用 minY−45 且端口间隔>75',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '下方受阻时会尝试上方通道'},
                                                                           {'kind': 'addition',
                                                                            'choice': '侧边走廊至少260',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '边界两侧至少留出 260 的通道'},
                                                                           {'kind': 'addition',
                                                                            'choice': '组框成员外扩左右25、上65、下25',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '组框会在成员节点外围增加留白'},
                                                                           {'kind': 'addition',
                                                                            'choice': '根宽至少1000且边缘80，高底部+135',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '根图至少有 1000 的画布宽度'},
                                                                           {'kind': 'addition',
                                                                            'choice': 'child宽 '
                                                                                      'frame_right+240，高bottom+180。',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '子图画布额外保留边界与上下留白'},
                                                                           {'kind': 'addition',
                                                                            'choice': 'architecture.py：box/terminal/doc/decision四形，doc折角18，terminal半高圆角，其他圆角12',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '操作、判断、资料和结果使用四种形状'},
                                                                           {'kind': 'addition',
                                                                            'choice': '节点字体20、颜色#234839、weight550，节点文字27行距',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '主节点使用统一字号、颜色和行距'},
                                                                           {'kind': 'addition',
                                                                            'choice': '实际形状只代表作者给定类别',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '节点形状由报告作者指定'},
                                                                           {'kind': 'addition',
                                                                            'choice': '主边线宽2.4、点击透明线宽16。flow深灰#415c69、data蓝#397dab、constraint灰#8296a7无箭头且6/5虚线、error#b66050有箭头虚线',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '流程、数据、约束和异常使用不同连线样式'},
                                                                           {'kind': 'addition',
                                                                            'choice': 'relation默认#51839a蓝箭头',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '普通关联默认使用蓝色箭头'},
                                                                           {'kind': 'addition',
                                                                            'choice': 'conditional也虚线。其具体颜色、字号、圆角、padding是模板选择，用户只约定使用模板/完整图例。',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '有条件的关系也用虚线表示'},
                                                                           {'kind': 'addition',
                                                                            'choice': 'architecture.py：七项主图例，违反限制/有依据/组织/未指定/未核查/待定/关联',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '图例区分七种图形提示'},
                                                                           {'kind': 'match',
                                                                            'choice': 'green不表示通过',
                                                                            'note': '这是已有用户约定所要求的行为，不再列为Agent额外补充；核对范围限图例含义或层级机制。',
                                                                            'title': '绿色节点不代表实现已经通过',
                                                                            'specified': '标记不表示实现通过或用户认可。'},
                                                                           {'kind': 'addition',
                                                                            'choice': '橙轮廓未指定、灰点线未核查、紫待定，混合时橙描边兼两个角标',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '未指定、未核查和待定分别保留标记'},
                                                                           {'kind': 'addition',
                                                                            'choice': '角标文字11、宽len×11+16，溢出则上移22',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '角标放不下时会向上换行'},
                                                                           {'kind': 'addition',
                                                                            'choice': '焦点/选中深蓝#245dce线宽3。定义图例、含未指定细节/细节未核查/方案待定和展开↓为固定中文',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '选中状态使用深蓝色，提示文案固定为中文'},
                                                                           {'kind': 'addition',
                                                                            'choice': '角色 button、tabindex=0、aria '
                                                                                      'label以及 SVG desc由正文去标签而成。',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '节点支持键盘聚焦并附带文字说明'}]},
                                                'meaning': {'label': '来源与状态',
                                                            'purpose': '披露来源与状态的具体实现方法、参数和条件。',
                                                            'specified': {'text': '要完整展示所有用户没明说的选择，不要只挑几个重要的。\n'
                                                                                  '\n'
                                                                                  '当前约定摘录：小图属于末端详情，不继续递归展开。',
                                                                          'source': '本会话原话或当前语义记录；semantic-alignment-project/semantics/audit.md',
                                                                          'origin': '用户原话／当前约定（下文按来源区分）'},
                                                            'choice': {'text': 'semantic_template.py：project四字段与module六字段固定标签，detail固定用户要求/实际做法/影响与取舍；字符串来源默认“Agent '
                                                                               '归纳”，缺值“缺少/未提供”，dict无origin是“来源未标明”；text为空也变“缺少”；来源或context存在就有折叠来源，无source显示“未提供具体出处”；text及源路径html.escape，context按双换行成段。choice缺值写“未核实：尚未提供实际做法”，purpose缺值“本项作用尚未说明”，impact缺值明确缺少。\n'
                                                                               '\n'
                                                                               'semantic_template.py：specification未写时有 '
                                                                               'specified.missing就 unspecified，否则 '
                                                                               'unreviewed；显式只接受specified/unspecified/unreviewed；父行合并用户要求/实际做法 '
                                                                               'mini图全部节点与边标记，未指定+未核查并存mixed；pending独立来自本行或mini；missing从用户要求框移到choice '
                                                                               'context“选择的约定边界”，旧式内部 unspecified '
                                                                               '输入也进入该context，不多出第四固定详情字段。状态是作者输入的归并，不能据此声称检查实际完成。\n'
                                                                               '\n'
                                                                               'layers.py：子图整体框对应父节点；上层引用淡灰、不重复执行项；入/出都需handoff或gap，外层引用必须是真祖先；边界标“入/出”，默认left/right，condition使虚线，输入输出可指不同祖先；子图标记由所有子内容及父自身汇总，待定独立；父aria文字加展开和状态，点击仅选择分支。\n'
                                                                               '\n'
                                                                               'mini_diagram.py:5–57：末端小图节点宽160、高至少64或按14号字换行×19+30；列距至少52/标签len×14+24，原点12/28，行距height+72；每节点只放一次；复用主route；边点击宽18、线宽1.5、箭头8/4；constraint仅去箭头；可选specified/unspecified/unreviewed/context，默认unreviewed，pending独立；每项详情按本图key匹配，默认隐藏；green/orange/gray四套填充，标签14号，徽标11号；节点/边均键盘可选；小图不会再产生子视图。即使当前报告不用mini，随包机制也已检查披露。\n'
                                                                               '\n'
                                                                               '文字对照：comparisons由Agent填写精确片段，known '
                                                                               'kind、具体title与非空note必填；match需两侧，addition只标实际侧；片段必须唯一、互不重叠，否则ValueError。原文转义后用mark和sup本项编号，标题与正文说明配对；未标色不判为一致。绿色#205b3e/#e7f4ec，红色#9b3038/#fff0ef，橙色#855400/#fff3d8，灰色#586775/#edf0f3；2px下划线，灰色点线。\n'
                                                                               '\n'
                                                                               '旧unspecified别名的外部消费者未全量核查。\n'
                                                                               '\n'
                                                                               '违反限制使用kind=violation，必须同时提供两侧精确片段、非空note及constraint_source；缺字段或片段不唯一/重叠会报错。模板校验输入结构，不自动判定限制适用性或事实真假。\n'
                                                                               '\n'
                                                                               '缺实际正文以missing_text检测None、空字符串、空字典text及纯空白；只替换正文默认值，保留来源、上下文和简图。summary_findings逐项保留简图未指定/未核查节点和边；只有文本完全相同的缺值未核实项避免重复，不做语义去重。\n'
                                                                               '\n'
                                                                               '每个文字对照新增必填title，概括证据支持的具体发现；violation/mismatch默认展示标题及要求/做法对照，addition用可展开短标题列表，未核实独立展示。节点的作用、完整标色正文、来源、简图和取舍放进完整说明折叠区。\n'
                                                                               '\n'
                                                                               '摘要和节点详情共用发现渲染函数；重点差异与补充选择并存时按主次分栏，窄屏堆叠。可选impact描述单条影响，未填写时明确引用本项整体影响，不假造单条后果。',
                                                                       'source': 'assets/audit-svg',
                                                                       'origin': '2026-11-09 静态核对'},
                                                            'impact': {'text': '这些规则影响来源身份、未知状态、旧输入和简图细节如何被保留。它们不证明语义判断本身正确。',
                                                                       'origin': 'Agent 根据当前实现归纳',
                                                                       'source': '本次报告；对应文件与参数见实际做法'},
                                                            'specification': 'specified',
                                                            'comparisons': [{'kind': 'addition',
                                                                             'choice': '字符串来源默认“Agent '
                                                                                       '归纳”，缺值“缺少/未提供”，dict无origin是“来源未标明”',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '未写来源的字符串默认标为 Agent 归纳'},
                                                                            {'kind': 'addition',
                                                                             'choice': 'text为空也变“缺少”',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '空正文显示为“缺少”'},
                                                                            {'kind': 'addition',
                                                                             'choice': '来源或context存在就有折叠来源，无source显示“未提供具体出处”',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '来源和上下文默认放在折叠区'},
                                                                            {'kind': 'addition',
                                                                             'choice': 'text及源路径html.escape，context按双换行成段。choice缺值写“未核实：尚未提供实际做法”，purpose缺值“本项作用尚未说明”，impact缺值明确缺少。',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '正文转义显示，缺失做法和影响明确说明'},
                                                                            {'kind': 'addition',
                                                                             'choice': 'semantic_template.py：specification未写时有 '
                                                                                       'specified.missing就 '
                                                                                       'unspecified，否则 unreviewed',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '未填约定状态时按已知缺口推导'},
                                                                            {'kind': 'addition',
                                                                             'choice': '显式只接受specified/unspecified/unreviewed',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '用户约定状态只有三个显式取值'},
                                                                            {'kind': 'addition',
                                                                             'choice': '父行合并用户要求/实际做法 '
                                                                                       'mini图全部节点与边标记，未指定+未核查并存mixed',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '小图中的未指定和未核查状态会合并到外层'},
                                                                            {'kind': 'addition',
                                                                             'choice': 'pending独立来自本行或mini',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '方案待定独立于用户是否说明'},
                                                                            {'kind': 'addition',
                                                                             'choice': 'missing从用户要求框移到choice '
                                                                                       'context“选择的约定边界”，旧式内部 '
                                                                                       'unspecified '
                                                                                       '输入也进入该context，不多出第四固定详情字段。状态是作者输入的归并，不能据此声称检查实际完成。',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '旧 unspecified 输入别名仍能补充上下文'},
                                                                            {'kind': 'addition',
                                                                             'choice': '上层引用淡灰、不重复执行项',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '上层引用用淡灰色表示'},
                                                                            {'kind': 'addition',
                                                                             'choice': '入/出都需handoff或gap，外层引用必须是真祖先',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '子图需要入口和出口映射或缺少说明'},
                                                                            {'kind': 'addition',
                                                                             'choice': '边界标“入/出”，默认left/right，condition使虚线，输入输出可指不同祖先',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '边界交接可连接不同祖先节点'},
                                                                            {'kind': 'addition',
                                                                             'choice': '子图标记由所有子内容及父自身汇总，待定独立',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '父节点汇总子图及自身的状态'},
                                                                            {'kind': 'addition',
                                                                             'choice': '父aria文字加展开和状态，点击仅选择分支。',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '父节点的无障碍文案包含展开与状态提示'},
                                                                            {'kind': 'addition',
                                                                             'choice': 'mini_diagram.py:5–57：末端小图节点宽160、高至少64或按14号字换行×19+30',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '详情小图的节点使用统一宽度和最小高度'},
                                                                            {'kind': 'addition',
                                                                             'choice': '列距至少52/标签len×14+24，原点12/28，行距height+72',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '详情小图按标签和行高安排间距'},
                                                                            {'kind': 'addition',
                                                                             'choice': '每节点只放一次',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '详情小图每个节点只放置一次'},
                                                                            {'kind': 'addition',
                                                                             'choice': '复用主route',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '详情小图复用主图的连线路由'},
                                                                            {'kind': 'addition',
                                                                             'choice': '边点击宽18、线宽1.5、箭头8/4',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '详情小图扩大连线的点击区域'},
                                                                            {'kind': 'addition',
                                                                             'choice': 'constraint仅去箭头',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '小图约束关系省去箭头'},
                                                                            {'kind': 'addition',
                                                                             'choice': '可选specified/unspecified/unreviewed/context，默认unreviewed，pending独立',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '小图可区分要求、补充、未知和中性材料'},
                                                                            {'kind': 'addition',
                                                                             'choice': '每项详情按本图key匹配，默认隐藏',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '小图的具体说明默认隐藏'},
                                                                            {'kind': 'addition',
                                                                             'choice': 'green/orange/gray四套填充，标签14号，徽标11号',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '小图用颜色、字号和角标区分状态'},
                                                                            {'kind': 'addition',
                                                                             'choice': '节点/边均键盘可选',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '小图的节点和关系也支持键盘选择'},
                                                                            {'kind': 'match',
                                                                             'choice': '小图不会再产生子视图。即使当前报告不用mini，随包机制也已检查披露。',
                                                                             'note': '这是已有用户约定所要求的行为，不再列为Agent额外补充；核对范围限图例含义或层级机制。',
                                                                             'title': '详情小图不会继续生成下一层视图',
                                                                             'specified': '小图属于末端详情，不继续递归展开。'},
                                                                            {'kind': 'addition',
                                                                             'choice': '文字对照：comparisons由Agent填写精确片段，known '
                                                                                       'kind、具体title与非空note必填',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '每个文字对照都要提供具体发现标题'},
                                                                            {'kind': 'addition',
                                                                             'choice': 'match需两侧，addition只标实际侧',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '一致需要双侧引用，补充选择只引用实际侧'},
                                                                            {'kind': 'addition',
                                                                             'choice': '片段必须唯一、互不重叠，否则ValueError。原文转义后用mark和sup本项编号，标题与正文说明配对',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '引用片段必须唯一且不重叠'},
                                                                            {'kind': 'addition',
                                                                             'choice': '未标色不判为一致。绿色#205b3e/#e7f4ec，红色#9b3038/#fff0ef，橙色#855400/#fff3d8，灰色#586775/#edf0f3',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '未标色不表示一致，颜色区分对照类型'},
                                                                            {'kind': 'addition',
                                                                             'choice': '2px下划线，灰色点线。',
                                                                             'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                             'title': '对照片段用下划线和编号标识'},
                                                                            {'kind': 'unverified',
                                                                             'choice': '旧unspecified别名的外部消费者未全量核查。',
                                                                             'note': '清理兼容别名前先确认消费者事实；本轮只核对当前包和当前报告。',
                                                                             'title': '旧输入别名的外部消费者尚未查清'},
                                                                            {'kind': 'addition',
                                                                             'choice': '违反限制使用kind=violation，必须同时提供两侧精确片段、非空note及constraint_source；缺字段或片段不唯一/重叠会报错。模板校验输入结构，不自动判定限制适用性或事实真假。',
                                                                             'note': '具体输入字段、默认处理、视觉编码或路由为Agent实现选择；用户要求是修复缺口并突出违反限制。',
                                                                             'title': '违反限制必须引用两侧片段及限制来源'},
                                                                            {'kind': 'addition',
                                                                             'choice': '缺实际正文以missing_text检测None、空字符串、空字典text及纯空白；只替换正文默认值，保留来源、上下文和简图。summary_findings逐项保留简图未指定/未核查节点和边；只有文本完全相同的缺值未核实项避免重复，不做语义去重。',
                                                                             'note': '具体输入字段、默认处理、视觉编码或路由为Agent实现选择；用户要求是修复缺口并突出违反限制。',
                                                                             'title': '缺正文和简图已知选择会独立进入汇总'},
                                                                            {'kind': 'addition',
                                                                             'title': '每个对照新增必填的发现标题字段',
                                                                             'choice': '每个文字对照新增必填title，概括证据支持的具体发现',
                                                                             'note': '具体发现先行是用户要求；这里披露用必填title字段承载它的实现办法。',
                                                                             'impact': '读者先判断是否值得关注，再展开原文与证据；重建旧报告输入时需要补充发现标题。'},
                                                                            {'kind': 'addition',
                                                                             'title': '汇总与详情共用一套渲染函数',
                                                                             'choice': '摘要和节点详情共用发现渲染函数',
                                                                             'note': '用户要求两处呈现一致；共用函数是本次具体实现选择。'}]},
                                                'viewer': {'label': '查看与样式',
                                                           'purpose': '披露查看与样式的具体实现方法、参数和条件。',
                                                           'specified': {'text': '要完整展示所有用户没明说的选择，不要只挑几个重要的。',
                                                                         'source': '本会话原话或当前语义记录',
                                                                         'origin': '用户原话／当前约定（下文按来源区分）'},
                                                           'choice': {'text': 'viewer.js:3–10,14–38：每图内存中维护 '
                                                                              'scale/manualZoom/drag，初次自动按容器宽fit；缩放范围0.001–20，按钮/键盘+乘4/3、−乘0.75；Ctrl或Meta滚轮缩放，deltaMode行×16/页×canvasHeight，再钳−100…100，指数系数0.005；保持指针处坐标。画布高 '
                                                                              'min(svgheight, max(240, '
                                                                              'viewport×0.58))；resize保留中心、非手动缩放重fit；没有持久localStorage/sessionStorage，所谓“每视图会话位置”仅当前文档内存与scroll位置。\n'
                                                                              '\n'
                                                                              'viewer.js:25–35,52–87：Enter/空格选择；左键且非touch开始拖动，位移绝对值和>5才算移动，避滚动条；window '
                                                                              'move/up/cancel/blur控制拖动；触屏保留原生滚动；点链接不选择图节点。选上层隐藏深层、清除深层选择与父说明克隆；有child在下方展开且复制父详情去id，无child打开统一inspector；关详情保留中心并可恢复焦点；Escape先关详情，否则收起最深子层并焦点回owner；mini选择仅本mini内生效。hash目标自动展开祖先，source-report内锚点逐级打开details；内部链接history.replaceState，不新增历史项。上述是原检查的交互盘点；本次选择与跳转路径已按前文修改，其余缩放与拖动取值保持。\n'
                                                                              '\n'
                                                                              'viewer.js:39–49 + '
                                                                              'viewer.css:13：beforeprint记录原本关闭的完整原文/内部details/图例并打开；afterprint仅恢复这些；各图打印100%宽、自动高，显示所有隐藏flow-level和mini-detail，隐藏工具/主inspector/parent-context；不调用系统打印按钮；实际分页和所有浏览器支持未核实。\n'
                                                                              '\n'
                                                                              'viewer.css:1–13 + '
                                                                              'layers.html:1–8：zh-CN、UTF-8、viewport；body14px/1.6、背景#f7f8f5、正文#263b35、系统字体/PingFang；主列max1180、inspector1140，source正文1.8；hero '
                                                                              'h1 25，局部h2 '
                                                                              '18；主图margin20、图框圆角10；画布min180/max58vh，窄屏≤760时margin8/max55vh、标题17、详情宽calc100%−16；来源11/12px且路径anywhere换行；详情小图保留横滚；图控件是每图＋/−与关闭×；另有汇总／逐层查看按钮、条目详情／返回按钮，以及图例/父说明/完整原文折叠。主题颜色、尺寸、阈值、固定文案均未逐项约定。\n'
                                                                              '\n'
                                                                              '入口样式：主导航标题下、44px最小高度、16px文字、10px/18px内边距、圆角8；当前页背景#315443/白字，另一页#e7f4ec/#205b3e，边框#7fa78d。详情/返回为40px最小高度、14px字、8px/12px内边距、圆角7、白底#205b3e，详情紧邻条目标题；hover浅绿，主导航有2px阴影；原生链接，无新脚本。汇总主列最大1050、15px文字、20/24px边距；四类计数锚点和条目边线按类别着色。\n'
                                                                              '\n'
                                                                              '滚动修订：内容先替换后收起旧分支；当前节点位置及画布中心保留，已可见不滚动；普通展开预览160px，边距16px，原生smooth并尊重prefers-reduced-motion。关系/过大节点先定位文字，初次深链接直接定位；打印时打开主报告原先关闭的详情并在结束后恢复，汇总页用print '
                                                                              'CSS显示details内容。真实跨浏览器结果未测。\n'
                                                                              '\n'
                                                                              '违反限制：汇总排第一、已有项才显示强调边框，先显示具体发现标题和简短对照；完整理由、影响和来源按需展开。文字#991b1b/浅底#fee2e2、3px下划线；图中红色违反限制角标和轮廓，父项汇总后代，原有未指定/未核查/待定独立保留。\n'
                                                                              '\n'
                                                                              '详情专用锚点#inspect-在route中走detailsOnly，先展开祖先，再显示本项inspector并收起其后代；普通#view--node不变，原有按需滚动继续使用。完整原文入口打开目标自身details，返回汇总仍定位该项类别。\n'
                                                                              '\n'
                                                                              '发现卡片采用1px边框、4px左边线、圆角10、18/20px留白，标题21px；违反限制使用#b72e43和6px左边线，其他偏差#ce9299/#b6606b，未核实#7b8792/#f8fafb。对照区按至少200px自动排栏、间隔16；重点与补充并列时用1.35:1且补充至少240px。补充列表浅底#fffbf2、边框#e3d1a7、14px正文，原生details显示短标题和展开箭头。展开后给具体做法、单条或整项影响及依据。窄屏760px以下堆叠，标题19px、留白14；完整原文在独立details内。',
                                                                      'source': 'assets/audit-svg',
                                                                      'origin': '2026-11-09 静态核对'},
                                                           'impact': {'text': '这些选择影响阅读位置、缩放手感、页面密度和打印内容。真实浏览器中的效果与兼容性仍有未实测范围。',
                                                                      'origin': 'Agent 根据当前实现归纳',
                                                                      'source': '本次报告；对应文件与参数见实际做法'},
                                                           'specification': 'specified',
                                                           'comparisons': [{'kind': 'addition',
                                                                            'choice': 'viewer.js:3–10,14–38：每图内存中维护 '
                                                                                      'scale/manualZoom/drag，初次自动按容器宽fit',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '每张图首次打开时自动适合容器宽度'},
                                                                           {'kind': 'addition',
                                                                            'choice': '缩放范围0.001–20，按钮/键盘+乘4/3、−乘0.75',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '缩放限定范围，按钮按固定比例放大缩小'},
                                                                           {'kind': 'addition',
                                                                            'choice': 'Ctrl或Meta滚轮缩放，deltaMode行×16/页×canvasHeight，再钳−100…100，指数系数0.005',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '按 Ctrl 或 Meta 滚轮可围绕光标缩放'},
                                                                           {'kind': 'addition',
                                                                            'choice': '保持指针处坐标。画布高 min(svgheight, '
                                                                                      'max(240, viewport×0.58))',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '缩放保持光标处位置，画布高度随视口变化'},
                                                                           {'kind': 'addition',
                                                                            'choice': 'resize保留中心、非手动缩放重fit',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '窗口变大变小时尽量保留画布中心'},
                                                                           {'kind': 'addition',
                                                                            'choice': '没有持久localStorage/sessionStorage，所谓“每视图会话位置”仅当前文档内存与scroll位置。',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '关闭或重载页面后不会保存图中位置',
                                                                            'impact': '重载后需要重新选择视图或调整位置。'},
                                                                           {'kind': 'addition',
                                                                            'choice': 'viewer.js:25–35,52–87：Enter/空格选择',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': 'Enter 或空格也能选中节点'},
                                                                           {'kind': 'addition',
                                                                            'choice': '左键且非touch开始拖动，位移绝对值和>5才算移动，避滚动条',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '鼠标移动超过阈值后才算拖动画布'},
                                                                           {'kind': 'addition',
                                                                            'choice': 'window move/up/cancel/blur控制拖动',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '鼠标松开或窗口失焦时结束拖动'},
                                                                           {'kind': 'addition',
                                                                            'choice': '触屏保留原生滚动',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '触摸屏保留浏览器原生滚动'},
                                                                           {'kind': 'addition',
                                                                            'choice': '点链接不选择图节点。选上层隐藏深层、清除深层选择与父说明克隆',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '切换上层选择会收起之前的深层内容'},
                                                                           {'kind': 'addition',
                                                                            'choice': '有child在下方展开且复制父详情去id，无child打开统一inspector',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '普通节点点击按是否有子图决定展开方式'},
                                                                           {'kind': 'addition',
                                                                            'choice': '关详情保留中心并可恢复焦点',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '关闭详情后尽量恢复原来的阅读位置'},
                                                                           {'kind': 'addition',
                                                                            'choice': 'Escape先关详情，否则收起最深子层并焦点回owner',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': 'Escape 优先关闭详情，再收起最深层'},
                                                                           {'kind': 'addition',
                                                                            'choice': 'mini选择仅本mini内生效。hash目标自动展开祖先，source-report内锚点逐级打开details',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '深链接展开祖先，小图选择只影响本图'},
                                                                           {'kind': 'addition',
                                                                            'choice': '内部链接history.replaceState，不新增历史项。上述是原检查的交互盘点',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '图内跳转不会新增浏览器历史记录',
                                                                            'impact': '浏览器后退不会逐个恢复这些图内选择。'},
                                                                           {'kind': 'addition',
                                                                            'choice': '本次选择与跳转路径已按前文修改，其余缩放与拖动取值保持。',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '缩放和拖动参数继续沿用既有设置'},
                                                                           {'kind': 'addition',
                                                                            'choice': 'viewer.js:39–49 + '
                                                                                      'viewer.css:13：beforeprint记录原本关闭的完整原文/内部details/图例并打开',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '打印前自动展开完整原文和来源'},
                                                                           {'kind': 'addition',
                                                                            'choice': 'afterprint仅恢复这些',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '打印后恢复原来的折叠状态'},
                                                                           {'kind': 'addition',
                                                                            'choice': '各图打印100%宽、自动高，显示所有隐藏flow-level和mini-detail，隐藏工具/主inspector/parent-context',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '打印时显示全部图层并隐藏操作控件'},
                                                                           {'kind': 'addition',
                                                                            'choice': '不调用系统打印按钮',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '页面没有额外的打印按钮'},
                                                                           {'kind': 'unverified',
                                                                            'choice': '实际分页和所有浏览器支持未核实。',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '打印分页和跨浏览器兼容性尚未核实'},
                                                                           {'kind': 'addition',
                                                                            'choice': 'viewer.css:1–13 + '
                                                                                      'layers.html:1–8：zh-CN、UTF-8、viewport',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '页面声明中文语言和 UTF-8 编码'},
                                                                           {'kind': 'addition',
                                                                            'choice': 'body14px/1.6、背景#f7f8f5、正文#263b35、系统字体/PingFang',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '正文采用系统字体和统一的浅色主题'},
                                                                           {'kind': 'addition',
                                                                            'choice': '主列max1180、inspector1140，source正文1.8',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '主图和详情区域各有最大宽度'},
                                                                           {'kind': 'addition',
                                                                            'choice': 'hero h1 25，局部h2 18',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '页面标题和局部图标题使用不同字号'},
                                                                           {'kind': 'addition',
                                                                            'choice': '主图margin20、图框圆角10',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '主图周围留白，图框使用圆角'},
                                                                           {'kind': 'addition',
                                                                            'choice': '画布min180/max58vh，窄屏≤760时margin8/max55vh、标题17、详情宽calc100%−16',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '窄屏采用较小边距和不同画布高度'},
                                                                           {'kind': 'addition',
                                                                            'choice': '来源11/12px且路径anywhere换行',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '长来源路径允许在任意位置换行'},
                                                                           {'kind': 'addition',
                                                                            'choice': '详情小图保留横滚',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '详情小图可以横向滚动'},
                                                                           {'kind': 'addition',
                                                                            'choice': '图控件是每图＋/−与关闭×',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '图控件保留放大、缩小和关闭'},
                                                                           {'kind': 'addition',
                                                                            'choice': '另有汇总／逐层查看按钮、条目详情／返回按钮，以及图例/父说明/完整原文折叠。主题颜色、尺寸、阈值、固定文案均未逐项约定。',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '导航、图例和原文入口使用按钮或折叠项'},
                                                                           {'kind': 'addition',
                                                                            'choice': '入口样式：主导航标题下、44px最小高度、16px文字、10px/18px内边距、圆角8',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '主导航放在标题下并扩大点击区域'},
                                                                           {'kind': 'addition',
                                                                            'choice': '当前页背景#315443/白字，另一页#e7f4ec/#205b3e，边框#7fa78d。详情/返回为40px最小高度、14px字、8px/12px内边距、圆角7、白底#205b3e，详情紧邻条目标题',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '当前页面和跳转入口使用不同按钮样式'},
                                                                           {'kind': 'addition',
                                                                            'choice': 'hover浅绿，主导航有2px阴影',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '鼠标悬停时增加底色或阴影提示'},
                                                                           {'kind': 'addition',
                                                                            'choice': '原生链接，无新脚本。汇总主列最大1050、15px文字、20/24px边距',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '汇总页使用原生链接和限定宽度'},
                                                                           {'kind': 'addition',
                                                                            'choice': '四类计数锚点和条目边线按类别着色。',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '四类发现的计数入口使用对应颜色'},
                                                                           {'kind': 'addition',
                                                                            'choice': '滚动修订：内容先替换后收起旧分支',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '切换内容时先替换，再收起旧分支'},
                                                                           {'kind': 'addition',
                                                                            'choice': '当前节点位置及画布中心保留，已可见不滚动',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '目标已经可见时不主动滚动'},
                                                                           {'kind': 'addition',
                                                                            'choice': '普通展开预览160px，边距16px，原生smooth并尊重prefers-reduced-motion。关系/过大节点先定位文字，初次深链接直接定位',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '新增内容只按需平滑露出开头'},
                                                                           {'kind': 'addition',
                                                                            'choice': '打印时打开主报告原先关闭的详情并在结束后恢复，汇总页用print '
                                                                                      'CSS显示details内容。真实跨浏览器结果未测。',
                                                                            'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                            'title': '打印时展开内容，结束后恢复原状态'},
                                                                           {'kind': 'addition',
                                                                            'choice': '违反限制：汇总排第一、已有项才显示强调边框，先显示具体发现标题和简短对照；完整理由、影响和来源按需展开。文字#991b1b/浅底#fee2e2、3px下划线；图中红色违反限制角标和轮廓，父项汇总后代，原有未指定/未核查/待定独立保留。',
                                                                            'note': '具体输入字段、默认处理、视觉编码或路由为Agent实现选择；用户要求是修复缺口并突出违反限制。',
                                                                            'title': '违反限制的具体发现始终优先展示'},
                                                                           {'kind': 'addition',
                                                                            'choice': '详情专用锚点#inspect-在route中走detailsOnly，先展开祖先，再显示本项inspector并收起其后代；普通#view--node不变，原有按需滚动继续使用。完整原文入口打开目标自身details，返回汇总仍定位该项类别。',
                                                                            'note': '具体输入字段、默认处理、视觉编码或路由为Agent实现选择；用户要求是修复缺口并突出违反限制。',
                                                                            'title': '汇总入口直接打开本项详情'},
                                                                           {'kind': 'addition',
                                                                            'title': '发现卡片和补充列表采用统一样式',
                                                                            'choice': '发现卡片采用1px边框、4px左边线、圆角10、18/20px留白，标题21px；违反限制使用#b72e43和6px左边线，其他偏差#ce9299/#b6606b，未核实#7b8792/#f8fafb。对照区按至少200px自动排栏、间隔16；重点与补充并列时用1.35:1且补充至少240px。补充列表浅底#fffbf2、边框#e3d1a7、14px正文，原生details显示短标题和展开箭头。展开后给具体做法、单条或整项影响及依据。窄屏760px以下堆叠，标题19px、留白14；完整原文在独立details内。',
                                                                            'note': '尺寸、配色、断点和原生details是Agent的呈现选择；完整原文和条件仍保留。',
                                                                            'impact': '默认阅读更短；较窄空间会改为上下对照，细节需要展开。'}]},
                                                'check': {'label': '检查与示例',
                                                          'purpose': '披露检查与示例的具体实现方法、参数和条件。',
                                                          'specified': {'text': '要完整展示所有用户没明说的选择，不要只挑几个重要的。',
                                                                        'source': '本会话原话或当前语义记录',
                                                                        'origin': '用户原话／当前约定（下文按来源区分）'},
                                                          'choice': {'text': 'check_report.py：stdlib '
                                                                             'HTMLParser收集所有id、锚点、keys、view和inspector；要求唯一id/key、所有#链接可达、每个节点/关系恰一详情且三个dt严格匹配；初始唯一root可见；嵌入SVG用ElementTree解析，检查box在画布/父框内、节点/上下文彼此不重叠、正交边不穿节点、关系标签不盖节点、文字大致不越界；重叠容差2、文字边界容差6，估宽和渲染器相同；非M/L曲线跳过，斜线crosses返回False；只核对输入index.html内SVG，不逐个重读独立SVG文件；检查深度1–3/owner和后代/mini状态传播；错误去重拼成ValueError，显式跨项引用还要求目标详情有返回引用处的链接；全文锚点不要求自动返回。全部通过返回字典。没有浏览器、CSS布局、语义内容真伪、关系标签彼此重叠或完整披露证明。\n'
                                                                             '\n'
                                                                             'layers-example.py：一个三层虚构文件复制例子，三条虚构约定为复制指定文件、不覆盖已有文件、告知结果且失败时说明原因；假设实现只报告 '
                                                                             'failed，并设定竞态覆盖以演示违反不覆盖限制，两者均为虚构例子；演示共享链接、分支、交接和详情小图。跳过、覆盖写入、filename/reason '
                                                                             '日志与 copied/skipped '
                                                                             '都是虚构实现选择，不是实际复制代码或本项目要求。默认输出 '
                                                                             '/tmp/semantic-layered-example，直接执行脚本才生成；不会执行复制。\n'
                                                                             '\n'
                                                                             'agents/openai.yaml:1–4：显示名Semantic '
                                                                             'Alignment、英文短描述和固定默认prompt（检查当前用户约定、独立反查并从约定进入实际流程）；无额外依赖声明、触发验证代码或MCP。三个 '
                                                                             'references和SKILL是执行规范，仍由Agent遵从，模板不会强制语义基线正确。说明摘写/文件分工是Agent实现选择，来源记录中“规则负责位置定义”提供方向，不逐项规定每个英文句子。\n'
                                                                             '\n'
                                                                             '汇总实现：按violation/mismatch/addition/unverified固定顺序，保持原图项顺序、省去match；一项多处发现按局部编号保存。读取已有对照、本项状态、缺正文以及各简图已标条目，计数为摘要项，不自动语义去重；本轮已修复缺正文与简图收集，全文发现由作者逐项对齐输入。先显示具体发现标题，必要对照直接显示，详细说明按需展开；每项链接index.html#inspect-view--key直接打开自身详情，有违反限制时优先返回该类，否则返回该项第一种发现类别，不按点击来源记忆。\n'
                                                                             '\n'
                                                                             '输出检查增加限制违背详情提示与图中角标对应检查，继续检查两页真实锚点；通过不证明语义完整性或浏览器交互。随包虚构复制例子明确设定竞态覆盖来展示violation，不执行真实文件复制。',
                                                                     'source': 'assets/audit-svg',
                                                                     'origin': '2026-11-09 静态核对'},
                                                          'impact': {'text': '这些检查能发现结构和部分几何问题，不能替代来源核对或浏览器验收。随包示例只演示填写与呈现。',
                                                                     'origin': 'Agent 根据当前实现归纳',
                                                                     'source': '本次报告；对应文件与参数见实际做法'},
                                                          'specification': 'specified',
                                                          'comparisons': [{'kind': 'addition',
                                                                           'choice': 'check_report.py：stdlib '
                                                                                     'HTMLParser收集所有id、锚点、keys、view和inspector',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '检查器解析生成 HTML 中的标识和链接'},
                                                                          {'kind': 'addition',
                                                                           'choice': '要求唯一id/key、所有#链接可达、每个节点/关系恰一详情且三个dt严格匹配',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '节点、详情字段和链接目标必须相互对应'},
                                                                          {'kind': 'addition',
                                                                           'choice': '初始唯一root可见',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '页面初始只显示一张根图'},
                                                                          {'kind': 'addition',
                                                                           'choice': '嵌入SVG用ElementTree解析，检查box在画布/父框内、节点/上下文彼此不重叠、正交边不穿节点、关系标签不盖节点、文字大致不越界',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '检查器估算节点、文字和连线的边界关系'},
                                                                          {'kind': 'addition',
                                                                           'choice': '重叠容差2、文字边界容差6，估宽和渲染器相同',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '几何检查允许少量像素误差'},
                                                                          {'kind': 'addition',
                                                                           'choice': '非M/L曲线跳过，斜线crosses返回False',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '复杂曲线和斜线不作完整碰撞检查'},
                                                                          {'kind': 'addition',
                                                                           'choice': '只核对输入index.html内SVG，不逐个重读独立SVG文件',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '检查器不逐个重读独立 SVG 文件'},
                                                                          {'kind': 'addition',
                                                                           'choice': '检查深度1–3/owner和后代/mini状态传播',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '检查器核对层级归属和状态传递'},
                                                                          {'kind': 'addition',
                                                                           'choice': '错误去重拼成ValueError，显式跨项引用还要求目标详情有返回引用处的链接',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '检查失败会合并为一个 ValueError'},
                                                                          {'kind': 'addition',
                                                                           'choice': '全文锚点不要求自动返回。全部通过返回字典。没有浏览器、CSS布局、语义内容真伪、关系标签彼此重叠或完整披露证明。',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '结构检查不会证明语义正确或浏览器效果'},
                                                                          {'kind': 'addition',
                                                                           'choice': 'layers-example.py：一个三层虚构文件复制例子，三条虚构约定为复制指定文件、不覆盖已有文件、告知结果且失败时说明原因',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '随包使用一个虚构文件复制例子'},
                                                                          {'kind': 'addition',
                                                                           'choice': '假设实现只报告 '
                                                                                     'failed，并设定竞态覆盖以演示违反不覆盖限制，两者均为虚构例子',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '虚构例子演示遗漏失败原因和覆盖文件'},
                                                                          {'kind': 'addition',
                                                                           'choice': '演示共享链接、分支、交接和详情小图。跳过、覆盖写入、filename/reason '
                                                                                     '日志与 copied/skipped '
                                                                                     '都是虚构实现选择，不是实际复制代码或本项目要求。默认输出 '
                                                                                     '/tmp/semantic-layered-example，直接执行脚本才生成',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '示例展示分支、交接、来源与日志选择'},
                                                                          {'kind': 'addition',
                                                                           'choice': '不会执行复制。',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '填写示例不会真的复制文件'},
                                                                          {'kind': 'addition',
                                                                           'choice': 'agents/openai.yaml:1–4：显示名Semantic '
                                                                                     'Alignment、英文短描述和固定默认prompt（检查当前用户约定、独立反查并从约定进入实际流程）',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '界面名称、简介和默认提示词固定在元数据里'},
                                                                          {'kind': 'addition',
                                                                           'choice': '无额外依赖声明、触发验证代码或MCP。三个 '
                                                                                     'references和SKILL是执行规范，仍由Agent遵从，模板不会强制语义基线正确。说明摘写/文件分工是Agent实现选择，来源记录中“规则负责位置定义”提供方向，不逐项规定每个英文句子。',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': 'Skill 的执行规则仍需要 Agent 遵守'},
                                                                          {'kind': 'addition',
                                                                           'choice': '汇总实现：按violation/mismatch/addition/unverified固定顺序，保持原图项顺序、省去match',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '汇总先列违反限制，再列其他类型'},
                                                                          {'kind': 'addition',
                                                                           'choice': '一项多处发现按局部编号保存。读取已有对照、本项状态、缺正文以及各简图已标条目，计数为摘要项，不自动语义去重',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '汇总计数按条目计算，不自动语义去重'},
                                                                          {'kind': 'addition',
                                                                           'choice': '本轮已修复缺正文与简图收集，全文发现由作者逐项对齐输入。先显示具体发现标题，必要对照直接显示，详细说明按需展开',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '已识别的全文发现需要进入同一报告输入'},
                                                                          {'kind': 'addition',
                                                                           'choice': '每项链接index.html#inspect-view--key直接打开自身详情，有违反限制时优先返回该类，否则返回该项第一种发现类别，不按点击来源记忆。',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '返回汇总时定位该项的发现类别'},
                                                                          {'kind': 'addition',
                                                                           'choice': '输出检查增加限制违背详情提示与图中角标对应检查，继续检查两页真实锚点；通过不证明语义完整性或浏览器交互。随包虚构复制例子明确设定竞态覆盖来展示violation，不执行真实文件复制。',
                                                                           'note': '具体输入字段、默认处理、视觉编码或路由为Agent实现选择；用户要求是修复缺口并突出违反限制。',
                                                                           'title': '检查器核对限制提示与图中角标对应'}]},
                                                'links': {'label': '共享导航',
                                                          'purpose': '披露共享导航的具体实现方法、参数和条件。',
                                                          'specified': {'text': '要完整展示所有用户没明说的选择，不要只挑几个重要的。',
                                                                        'source': '本会话原话或当前语义记录',
                                                                        'origin': '用户原话／当前约定（下文按来源区分）'},
                                                          'choice': {'text': 'semantic_template.py:detail_html 接收 '
                                                                             'links=[{target,label}]，文本和目标转义后写成 '
                                                                             'detail-reference '
                                                                             '锚点；字段由报告作者填写，不推断哪个实现属于哪条约定。\n'
                                                                             '\n'
                                                                             'layers.py:prepare_details '
                                                                             '在生成期间建立详情正文、标题和引用的内存映射；先限定本层键，再找显式链接。用生成 '
                                                                             'HTML '
                                                                             '的固定标签匹配，不解析用户语义。相同目标按字典键去重；不会凭空生成不存在的目标。对象引用自动补“返回：来源标题”；已有显式反向链接或自引用不重复补。多个约定引用同一步时，每个入口各有一个返回链接；不根据用户点击历史只保留最新来源。\n'
                                                                             '\n'
                                                                             '同一项的正文仍可能保留作者重复填写的正向链接；生成器只避免重复自动返回。目标是全文锚点时不补返回。合格项的导航也复制到完整阅读内容中；调用既有 '
                                                                             'hash 导航展开祖先，没有新增浏览器状态存储或语义账本。\n'
                                                                             '\n'
                                                                             'check_report.py:Index/check_report '
                                                                             '收集详情内锚点，对显式引用的对象目标核对反向可达；检查不判断“关联是否真的合理”，也不要求任意手写 '
                                                                             'HTML '
                                                                             '链接都有反向跳转。缺目标、缺返回会报错，但仍遵循先写文件再检查的既有输出顺序。',
                                                                     'source': 'assets/audit-svg',
                                                                     'origin': '2026-11-09 静态核对'},
                                                          'impact': {'text': '这些选择让共享实现有明确的跳转和返回路径。链接存在不代表关系的含义已经核实。',
                                                                     'origin': 'Agent 根据当前实现归纳',
                                                                     'source': '本次报告；对应文件与参数见实际做法'},
                                                          'specification': 'specified',
                                                          'comparisons': [{'kind': 'addition',
                                                                           'choice': 'semantic_template.py:detail_html '
                                                                                     '接收 '
                                                                                     'links=[{target,label}]，文本和目标转义后写成 '
                                                                                     'detail-reference 锚点',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '报告作者用目标和标签填写精确引用'},
                                                                          {'kind': 'addition',
                                                                           'choice': '字段由报告作者填写，不推断哪个实现属于哪条约定。',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '关联关系由作者提供，不从文字自动推断'},
                                                                          {'kind': 'addition',
                                                                           'choice': 'layers.py:prepare_details '
                                                                                     '在生成期间建立详情正文、标题和引用的内存映射',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '生成时在内存中建立详情与引用映射'},
                                                                          {'kind': 'addition',
                                                                           'choice': '先限定本层键，再找显式链接。用生成 HTML '
                                                                                     '的固定标签匹配，不解析用户语义。相同目标按字典键去重',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '本层键名先限定范围，相同目标按键名去重'},
                                                                          {'kind': 'addition',
                                                                           'choice': '不会凭空生成不存在的目标。对象引用自动补“返回：来源标题”',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '对象引用会自动补充返回来源的链接'},
                                                                          {'kind': 'addition',
                                                                           'choice': '已有显式反向链接或自引用不重复补。多个约定引用同一步时，每个入口各有一个返回链接',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '已有反向链接和自引用不会重复补返回'},
                                                                          {'kind': 'addition',
                                                                           'choice': '不根据用户点击历史只保留最新来源。',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '返回入口不会随用户点击历史改变'},
                                                                          {'kind': 'addition',
                                                                           'choice': '同一项的正文仍可能保留作者重复填写的正向链接',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '作者仍可能填写重复的正向链接'},
                                                                          {'kind': 'addition',
                                                                           'choice': '生成器只避免重复自动返回。目标是全文锚点时不补返回。合格项的导航也复制到完整阅读内容中',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '全文锚点不会自动获得返回链接'},
                                                                          {'kind': 'addition',
                                                                           'choice': '调用既有 hash '
                                                                                     '导航展开祖先，没有新增浏览器状态存储或语义账本。',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '导航沿用原有锚点机制'},
                                                                          {'kind': 'addition',
                                                                           'choice': 'check_report.py:Index/check_report '
                                                                                     '收集详情内锚点，对显式引用的对象目标核对反向可达',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '检查器核对显式对象引用可以返回'},
                                                                          {'kind': 'addition',
                                                                           'choice': '检查不判断“关联是否真的合理”，也不要求任意手写 HTML '
                                                                                     '链接都有反向跳转。缺目标、缺返回会报错，但仍遵循先写文件再检查的既有输出顺序。',
                                                                           'note': '本段披露实现选取的方法、参数或默认；并非将已有能力要求本身判为未指定。具体来源见本项全文和对应源码。',
                                                                           'title': '链接可达不代表关联含义正确'}]}},
                                      'edges': [{'from': 'load',
                                                 'to': 'layout',
                                                 'label': '提供图结构',
                                                 'kind': 'data',
                                                 'specification': 'specified',
                                                 'purpose': '表示报告与证据之间的关系。',
                                                 'specified': {'text': '检查发现、图、详情和完整原文互相对应。',
                                                               'source': 'docs/showcase/semantics/audit.md',
                                                               'origin': '当前记录原文'},
                                                 'choice': {'text': '提供图结构',
                                                            'source': '本报告组织',
                                                            'origin': 'Agent 按源码或报告结构归纳'},
                                                 'impact': '关系用于阅读，不替代实现已通过的结论。'},
                                                {'from': 'layout',
                                                 'to': 'viewer',
                                                 'label': '输出SVG',
                                                 'kind': 'data',
                                                 'specification': 'specified',
                                                 'purpose': '表示报告与证据之间的关系。',
                                                 'specified': {'text': '检查发现、图、详情和完整原文互相对应。',
                                                               'source': 'docs/showcase/semantics/audit.md',
                                                               'origin': '当前记录原文'},
                                                 'choice': {'text': '输出SVG',
                                                            'source': '本报告组织',
                                                            'origin': 'Agent 按源码或报告结构归纳'},
                                                 'impact': '关系用于阅读，不替代实现已通过的结论。'},
                                                {'from': 'meaning',
                                                 'to': 'links',
                                                 'label': '详情与引用',
                                                 'kind': 'data',
                                                 'specification': 'specified',
                                                 'purpose': '表示报告与证据之间的关系。',
                                                 'specified': {'text': '检查发现、图、详情和完整原文互相对应。',
                                                               'source': 'docs/showcase/semantics/audit.md',
                                                               'origin': '当前记录原文'},
                                                 'choice': {'text': '详情与引用',
                                                            'source': '本报告组织',
                                                            'origin': 'Agent 按源码或报告结构归纳'},
                                                 'impact': '关系用于阅读，不替代实现已通过的结论。'},
                                                {'from': 'links',
                                                 'to': 'check',
                                                 'label': '校验目标',
                                                 'kind': 'data',
                                                 'specification': 'specified',
                                                 'purpose': '表示报告与证据之间的关系。',
                                                 'specified': {'text': '检查发现、图、详情和完整原文互相对应。',
                                                               'source': 'docs/showcase/semantics/audit.md',
                                                               'origin': '当前记录原文'},
                                                 'choice': {'text': '校验目标',
                                                            'source': '本报告组织',
                                                            'origin': 'Agent 按源码或报告结构归纳'},
                                                 'impact': '关系用于阅读，不替代实现已通过的结论。'},
                                                {'from': 'viewer',
                                                 'to': 'check',
                                                 'label': '检查生成HTML',
                                                 'kind': 'data',
                                                 'specification': 'specified',
                                                 'purpose': '表示报告与证据之间的关系。',
                                                 'specified': {'text': '检查发现、图、详情和完整原文互相对应。',
                                                               'source': 'docs/showcase/semantics/audit.md',
                                                               'origin': '当前记录原文'},
                                                 'choice': {'text': '检查生成HTML',
                                                            'source': '本报告组织',
                                                            'origin': 'Agent 按源码或报告结构归纳'},
                                                 'impact': '关系用于阅读，不替代实现已通过的结论。'}],
                                      'handoffs': [{'label': '反查当前产物',
                                                    'kind': 'constraint',
                                                    'specification': 'specified',
                                                    'purpose': '表示报告与证据之间的关系。',
                                                    'specified': {'text': '检查发现、图、详情和完整原文互相对应。',
                                                                  'source': 'docs/showcase/semantics/audit.md',
                                                                  'origin': '当前记录原文'},
                                                    'choice': {'text': '检查时以这些材料建立对应关系，不表示产品自动运行步骤。',
                                                               'source': '本报告组织',
                                                               'origin': 'Agent 按源码或报告结构归纳'},
                                                    'impact': '关系用于阅读，不替代实现已通过的结论。',
                                                    'direction': 'in',
                                                    'inner': 'load',
                                                    'outer': 'check'},
                                                   {'label': '形成检查发现',
                                                    'kind': 'constraint',
                                                    'specification': 'specified',
                                                    'purpose': '表示报告与证据之间的关系。',
                                                    'specified': {'text': '检查发现、图、详情和完整原文互相对应。',
                                                                  'source': 'docs/showcase/semantics/audit.md',
                                                                  'origin': '当前记录原文'},
                                                    'choice': {'text': '检查时以这些材料建立对应关系，不表示产品自动运行步骤。',
                                                               'source': '本报告组织',
                                                               'origin': 'Agent 按源码或报告结构归纳'},
                                                    'impact': '关系用于阅读，不替代实现已通过的结论。',
                                                    'direction': 'out',
                                                    'inner': 'check',
                                                    'outer': 'summary'}],
                                      'fields': {'purpose': '各实现组件如何共同提供检查报告；分组由Agent整理，不是新增用户模块。',
                                                 'inputs': '本会话及当前用户约定；当前源码与检查证据。',
                                                 'outputs': '对应要求的落实、已识别选择、缺口和未核实范围。',
                                                 'behavior': '区分用户要求、实际观察与Agent判断；具体对应见图中关系。',
                                                 'boundaries': '本轮语义检查不修改产品；不等同普通代码审查或浏览器验收。',
                                                 'acceptance': '依当前阶段约定核对；未额外约定的新验收条件保持未约定。'}},
           'status-check': {'title': '修复后：状态仍保持原意',
                            'level_label': '关键状态对照',
                            'layout': {'kind': 'interaction', 'lanes': [['unreviewed', 'pending', 'coverage']]},
                            'nodes': {'unreviewed': {'label': '区分两类未核对',
                                                     'purpose': '核对区分两类未核对在各阅读入口中的表达。',
                                                     'specified': {'text': '缺少语义内容仍显示缺少，未核查、未核实和未约定分别表达。',
                                                                   'source': 'docs/showcase/semantics/audit.md',
                                                                   'origin': '当前用户约定摘录'},
                                                     'choice': {'text': '用户约定范围未核查时显示“约定未核查”；缺少实际做法或实现证据时另列“实现未核实”，两者可并存。模板用内部 '
                                                                        'unreviewed 类型承载约定缺口，作者 comparisons '
                                                                        '的五种类型保持不变。约定未核查分区有内容时才显示，沿用灰色标签。',
                                                                'source': 'assets/audit-svg/semantic_template.py · '
                                                                          'summary_findings、review_findings_html 和 '
                                                                          'summary_html；正文及简图分别验证，约定未查不再单独产生实现未核实标签。',
                                                                'origin': '本轮源码核对与真实模板受控输入'},
                                                     'impact': {'text': '读者可区分需要补要求来源还是实现证据；两种未知可同时呈现，不互相替代。',
                                                                'origin': 'Agent 对修复效果的归纳',
                                                                'source': '本轮受控报告输出'},
                                                     'specification': 'specified',
                                                     'comparisons': [{'kind': 'match',
                                                                      'title': '约定未核查使用独立标签',
                                                                      'specified': '缺少语义内容仍显示缺少，未核查、未核实和未约定分别表达。',
                                                                      'choice': '用户约定范围未核查时显示“约定未核查”；缺少实际做法或实现证据时另列“实现未核实”，两者可并存。',
                                                                      'note': 'summary_findings、review_findings_html 和 '
                                                                              'summary_html；正文及简图分别验证，约定未查不再单独产生实现未核实标签。'},
                                                                     {'kind': 'addition',
                                                                      'title': '内部 unreviewed 类型独立承载约定缺口',
                                                                      'choice': '模板用内部 unreviewed 类型承载约定缺口，作者 '
                                                                                'comparisons 的五种类型保持不变。',
                                                                      'note': '这是满足已有状态区分要求的具体实现选择，不代表用户逐项指定了内部类型、分组或样式。'},
                                                                     {'kind': 'addition',
                                                                      'title': '约定未核查分区按需显示并沿用灰色',
                                                                      'choice': '约定未核查分区有内容时才显示，沿用灰色标签。',
                                                                      'note': '这是满足已有状态区分要求的具体实现选择，不代表用户逐项指定了内部类型、分组或样式。'}]},
                                      'pending': {'label': '保留待定状态',
                                                  'purpose': '核对保留待定状态在各阅读入口中的表达。',
                                                  'specified': {'text': '打开详情前就应区分已发现的未指定选择、尚未核查及方案未定。',
                                                                'source': 'docs/showcase/semantics/audit.md',
                                                                'origin': '当前用户约定摘录'},
                                                  'choice': {'text': '摘要保留本项“方案待定”，只有简图内部项待定时显示“含待定方案”，并仅在实际待定的简图发现上标记。没有其他发现的待定项使用内部 '
                                                                     'pending '
                                                                     '类型单列，其他待定状态附在对应组或简图发现上。待定标记沿用紫色，分区只在有单列项时显示，计数仅统计该分区条目。',
                                                             'source': 'assets/audit-svg/semantic_template.py · '
                                                                       'summary_findings、pending_label、flow.remember '
                                                                       '和共用发现渲染；验证 pending '
                                                                       'false/true、仅待定、小图节点与关系及混合兄弟项。',
                                                             'origin': '本轮源码核对与真实模板受控输入'},
                                                  'impact': {'text': '只读摘要也能辨认未定安排；相邻已选方案不会因同组含待定项而被贴上待定标签。',
                                                             'origin': 'Agent 对修复效果的归纳',
                                                             'source': '本轮受控报告输出'},
                                                  'specification': 'specified',
                                                  'comparisons': [{'kind': 'match',
                                                                   'title': '摘要保留待定状态及其范围',
                                                                   'specified': '打开详情前就应区分已发现的未指定选择、尚未核查及方案未定。',
                                                                   'choice': '摘要保留本项“方案待定”，只有简图内部项待定时显示“含待定方案”，并仅在实际待定的简图发现上标记。',
                                                                   'note': 'summary_findings、pending_label、flow.remember '
                                                                           '和共用发现渲染；验证 pending '
                                                                           'false/true、仅待定、小图节点与关系及混合兄弟项。'},
                                                                  {'kind': 'addition',
                                                                   'title': '仅待定项单列，已有发现附带状态',
                                                                   'choice': '没有其他发现的待定项使用内部 pending '
                                                                             '类型单列，其他待定状态附在对应组或简图发现上。',
                                                                   'note': '这是满足已有状态区分要求的具体实现选择，不代表用户逐项指定了内部类型、分组或样式。'},
                                                                  {'kind': 'addition',
                                                                   'title': '待定沿用紫色，计数仅对应单列条目',
                                                                   'choice': '待定标记沿用紫色，分区只在有单列项时显示，计数仅统计该分区条目。',
                                                                   'note': '这是满足已有状态区分要求的具体实现选择，不代表用户逐项指定了内部类型、分组或样式。'}]},
                                      'coverage': {'label': '核对摘要与详情',
                                                   'purpose': '核对核对摘要与详情在各阅读入口中的表达。',
                                                   'specified': {'text': '完整原文、具体取值、条件、出处和上下文保持可达。',
                                                                 'source': 'docs/showcase/semantics/audit.md',
                                                                 'origin': '当前用户约定摘录'},
                                                   'choice': {'text': '此前174个非一致发现标题保留；本轮4项实现选择另行列出。要求和实际片段、原三字段及来源仍可在完整详情中读取。',
                                                              'source': '本轮输入逐项比较、生成HTML和check_report结果',
                                                              'origin': '本轮静态核对与受控输入结果'},
                                                   'impact': {'text': '本轮没有发现标题化或折叠本身删除这些已有内容；范围限当前已记录输入。',
                                                              'source': '本次语义检查',
                                                              'origin': 'Agent 对影响与修复边界的分析'},
                                                   'specification': 'specified',
                                                   'comparisons': [{'kind': 'match',
                                                                    'title': '标题、原文和既有选择仍完整保留',
                                                                    'specified': '完整原文、具体取值、条件、出处和上下文保持可达。',
                                                                    'choice': '此前174个非一致发现标题保留；本轮4项实现选择另行列出。要求和实际片段、原三字段及来源仍可在完整详情中读取。',
                                                                    'note': '逐项保留原报告中的非修复发现，并以真实模板生成输出；不等于浏览器视觉验收。'}]}},
                            'edges': [{'from': 'unreviewed',
                                       'to': 'coverage',
                                       'label': '核对状态标签',
                                       'kind': 'data',
                                       'purpose': '表示状态进入报告呈现的对应关系。',
                                       'specified': {'text': '未核查、未核实和未约定分别表达。',
                                                     'source': 'docs/showcase/semantics/audit.md',
                                                     'origin': '当前记录摘录'},
                                       'choice': {'text': '核对状态标签', 'source': '本报告组织', 'origin': 'Agent 根据状态传递路径归纳'},
                                       'impact': '只表达本次核对的对应，不虚构新的执行步骤。',
                                       'specification': 'specified'},
                                      {'from': 'pending',
                                       'to': 'coverage',
                                       'label': '核对状态保留',
                                       'kind': 'data',
                                       'purpose': '表示状态进入报告呈现的对应关系。',
                                       'specified': {'text': '未核查、未核实和未约定分别表达。',
                                                     'source': 'docs/showcase/semantics/audit.md',
                                                     'origin': '当前记录摘录'},
                                       'choice': {'text': '核对状态保留', 'source': '本报告组织', 'origin': 'Agent 根据状态传递路径归纳'},
                                       'impact': '只表达本次核对的对应，不虚构新的执行步骤。',
                                       'specification': 'specified'}],
                            'handoffs': [{'label': '已有输入状态',
                                          'kind': 'data',
                                          'purpose': '表示状态进入报告呈现的对应关系。',
                                          'specified': {'text': '未核查、未核实和未约定分别表达。',
                                                        'source': 'docs/showcase/semantics/audit.md',
                                                        'origin': '当前记录摘录'},
                                          'choice': {'text': '已有输入状态', 'source': '本报告组织', 'origin': 'Agent 根据状态传递路径归纳'},
                                          'impact': '只表达本次核对的对应，不虚构新的执行步骤。',
                                          'specification': 'specified',
                                          'direction': 'in',
                                          'inner': 'unreviewed',
                                          'outer': 'collect'},
                                         {'label': '摘要中的表达',
                                          'kind': 'data',
                                          'purpose': '表示状态进入报告呈现的对应关系。',
                                          'specified': {'text': '未核查、未核实和未约定分别表达。',
                                                        'source': 'docs/showcase/semantics/audit.md',
                                                        'origin': '当前记录摘录'},
                                          'choice': {'text': '摘要中的表达', 'source': '本报告组织', 'origin': 'Agent 根据状态传递路径归纳'},
                                          'impact': '只表达本次核对的对应，不虚构新的执行步骤。',
                                          'specification': 'specified',
                                          'direction': 'out',
                                          'inner': 'coverage',
                                          'outer': 'render'}],
                            'fields': {'purpose': '核对新呈现方式中的状态身份与完整性。',
                                       'inputs': '当前已给出的约定状态、实际做法及独立pending标记。',
                                       'outputs': '分别呈现约定核查、实现核实和待定状态，并核对既有内容保留。',
                                       'behavior': '依现有约定分别判断，不从颜色或成功生成推断语义正确。',
                                       'boundaries': '受控输入只验证模板状态传递；不表示本项目真有未定业务方案。',
                                       'acceptance': '未核查、未核实、未指定和待定应保持各自含义。'}}},
 'data': {'title': 'Semantic Alignment · 状态表达修复复核',
          'date': '2026-11-09 · 两项状态修复',
          'scope': '修复最新语义检查确认的约定核查标签和待定状态摘要遗漏；保留此前已识别选择及验证范围，不扩展为全面代码审计。',
          'perspective': 'realization',
          'project': {'goal': '帮助用户发现Agent有没有自作主张。',
                      'scope': '本项目当前报告模板的两项状态修复及其呈现；其他选择沿用已有核对范围。',
                      'constraints': '原话优先、完整披露、用户含义与实际观察分开；不把未指定自动当作错误。',
                      'acceptance': '按当前11个用户约定主题及本会话追加要求核对。'}},
 'summary': '<p>两项已确认的状态问题已修复：约定未核查与实现未核实分别呈现；待定提示进入汇总，内部待定只标对应子项。</p><p>36个受控报告验证了独立与组合状态。此前174个非一致发现标题保持；本轮4项具体落地选择另行披露。受控输入不代表本项目有未定业务方案。</p><p>源码、英文执行说明及中文审阅说明同步更新；真实浏览器布局、点击手感和打印仍未实测。历史检查报告保留。</p><p>公开快照：保留2026-11-09检查时的发现和基线；后续移除中文审阅稿、公开资料与下载设置不在这次检查范围内。文件地址已规范化，本地未公开的历史材料以文字标识。</p>'}
BASELINE = [('docs/showcase/SEMANTICS.md',
  '# Semantic Alignment\n'
  '\n'
  '## 目的\n'
  '\n'
  '以用户当前有效的语义为依据开展语义检查，帮助用户发现 Agent 在实现过程中是否自作主张：要求是否兑现、哪些细节由 Agent 自行补足。可视化是检查结果的输出方式。\n'
  '\n'
  '## 限制\n'
  '\n'
  '语义记录只保存用户表达或已接受的含义。“最终期望”和“当前阶段约定”都是用户语义，不是真实实现或完成状态；检查须另查产物。用户明确留到后续的能力仍保留，但不判成本阶段遗漏。\n'
  '\n'
  '用户原话：“在记录语义文件时，需要尽可能用用户原话，在可视化时也是，如果太长的话则稍微压缩，这样便于用户理解”。\n'
  '\n'
  '使用 Markdown 正文，按用户关心的对象或能力分组；不建立逐条语义对象、JSON 账本、开发历史、常驻覆盖缓存或长期备选方案库。未知约定写“未约定”，不替用户补目标、阶段安排和完成条件。\n'
  '\n'
  '本项目的语义记录和维护资料保留在 Skill 安装包之外；未进入安装包不构成删除理由。英文为正式 Skill，中文仅用于审阅。\n'
  '\n'
  '以下主题分组，以及各主题的关联约定和关联文件，均为 Agent 按当前约定整理的导航索引；分组和文件拆分不自动定义实现模块。文件存在和路径关联不证明已实现，也不自动成为用户限定的实现路径。\n'
  '\n'
  '## 用户约定\n'
  '\n'
  '以下按主题索引约定正文；共同限制适用于相关主题，具体约定见链接。\n'
  '\n'
  '### [触发与任务范围](semantics/activation.md)\n'
  '\n'
  '- [长期语义维护](semantics/activation.md#长期语义维护)\n'
  '- [语义检查入口](semantics/activation.md#语义检查入口)\n'
  '\n'
  '### [语义记录](semantics/records.md)\n'
  '\n'
  '- [记录结构与文件组织](semantics/records.md#记录结构与文件组织)\n'
  '- [当前含义更新](semantics/records.md#当前含义更新)\n'
  '- [记录迁移](semantics/records.md#记录迁移)\n'
  '\n'
  '### [语义检查](semantics/audit.md)\n'
  '\n'
  '- [要求与产物双向对照](semantics/audit.md#要求与产物双向对照)\n'
  '- [全部选择披露](semantics/audit.md#全部选择披露)\n'
  '- [可省附加机制](semantics/audit.md#可省附加机制)\n'
  '- [修复确认](semantics/audit.md#修复确认)\n'
  '- [结果呈现与交付](semantics/audit.md#结果呈现与交付)\n'
  '\n'
  '### [Skill 说明与交付](semantics/packaging.md)\n'
  '\n'
  '- [说明与版本](semantics/packaging.md#说明与版本)\n'),
 ('docs/showcase/semantics/activation.md',
  '# 触发与任务范围\n'
  '\n'
  '## 目的\n'
  '\n'
  '识别需要语义检查的任务，并维护检查所需的用户语义依据，保持日常工作轻量。\n'
  '\n'
  '## 限制\n'
  '\n'
  '普通代码审查和独立画图请求不属于本 Skill；只出现“检查”一词、代码复杂、已有语义文件或存在未指定细节，都不足以触发语义检查。\n'
  '\n'
  '## 用户约定\n'
  '\n'
  '### 长期语义维护\n'
  '\n'
  '**最终期望：** 持续保存用户的有效意图，作为语义检查的基准。\n'
  '\n'
  '**当前阶段约定：** 为检查维护依据：建立、改变或纠正长期行为、接口、架构约束、运行规则或完成要求时更新记录；用户明确要求维护或澄清语义时也启用。改动小也应保存已接受的长期变化，但只处理受影响含义；维护记录不自动开展完整检查。\n'
  '\n'
  '按既定设计补实现、恢复已有约定的 bug 修复、内部重构、测试调试、查找仓库、提交、安装、临时实验和普通写作默认不触发。未触发时仍可按需读取并遵守既有语义；读取不等于启动维护或检查。\n'
  '\n'
  '**本阶段完成条件：** 未单独约定；按当前阶段约定核对。\n'
  '\n'
  '**关联约定：** 将已接受的长期变更交给[当前含义更新](records.md#当前含义更新)保存。\n'
  '\n'
  '**关联文件：** [SKILL.md](../../../SKILL.md)：任务入口、语义检查边界和记录格式说明。\n'
  '\n'
  '### 语义检查入口\n'
  '\n'
  '**最终期望：** 用户能要求检查实现是否符合自己的语义。\n'
  '\n'
  '**当前阶段约定：** '
  '明确提出语义检查，或上下文在问“有没有自作主张”“是不是按我的要求做的”等意图对照问题时，开展语义检查及结果交付，不要求出现“语义”关键词。代码检查服务于查明实际行为，逻辑缺陷作为解释语义偏差的证据；不承担普通代码审查的流程和交付。没有现成语义记录时也可根据当前用户要求和可用来源检查，缺少依据如实说明。修改既有检查图属于报告交付环节，不另开独立可视化流程，也不因改图而声称重新验收产品。\n'
  '\n'
  '**本阶段完成条件：** 未单独约定；按当前阶段约定核对。\n'
  '\n'
  '**关联约定：** 按本次范围启动[要求与产物双向对照](audit.md#要求与产物双向对照)；将发现交给[结果呈现与交付](audit.md#结果呈现与交付)呈现。\n'
  '\n'
  '**关联文件：** '
  '[SKILL.md](../../../SKILL.md)：任务入口、语义检查边界和记录格式说明；[audit-presentation.md](../../../references/audit-presentation.md)：双向核查、选择披露、修复信息和交付规则。\n'),
 ('docs/showcase/semantics/audit.md',
  '# 语义检查\n'
  '\n'
  '## 目的\n'
  '\n'
  '帮助用户发现 Agent 在实现过程中是否偏离要求、补足了哪些用户未明说的选择；核对要求兑现，并交付可查证的检查结果。\n'
  '\n'
  '## 限制\n'
  '\n'
  '本主题比较用户语义与真实产物，不承担普通代码审查。可视化属于检查结果的呈现与交付，不是独立功能模块或任务入口；不提供实现前推演。以当前阶段约定、完成条件和适用限制核对本阶段；明确留到后续的最终目标保留为后续范围。未指定不等于错误、用户禁止或删除授权。\n'
  '\n'
  '用户语义、Agent 组织或推断、真实实现和证据保持不同身份。图只呈现有依据的关系，不把尚未选择的办法画成实际流程。图和渲染输入不是新的语义基线、对象账本或覆盖缓存。\n'
  '\n'
  '## 用户约定\n'
  '\n'
  '### 要求与产物双向对照\n'
  '\n'
  '**最终期望：** 找出所有与用户语义不一致的地方，包括遗漏、偏离和用户未提到的内容。\n'
  '\n'
  '**当前阶段约定：** '
  '逐项核对当前约定正文中的行为、条件、例外及适用的上层限制，完成条件作为补充；同时从真实产物独立反查要求之外的行为。覆盖当前范围内入口、分支、配置、辅助组件、依赖默认值、失败恢复、部分副作用和随包提供的未启用机制。\n'
  '\n'
  '必须展示实际怎样落地，以及未实现、未核实的部分。语义记录的当前阶段约定不是实际实现；代码、测试和 Agent 自述也不是用户接受或决策理由的证明，来源不明时说明未知。\n'
  '\n'
  '**本阶段完成条件：** 用户要求的兑现情况和未约定实现均能查阅；未检查区域明确保留，不据局部核对声称完整。\n'
  '\n'
  '**关联约定：** 由[语义检查入口](activation.md#语义检查入口)确定本次检查任务；把反查出的未指定内容交给[全部选择披露](#全部选择披露)；把发现和证据交给[结果呈现与交付](#结果呈现与交付)。\n'
  '\n'
  '**关联文件：** '
  '[audit-presentation.md](../../../references/audit-presentation.md)：双向核查、选择披露、修复信息和交付规则；[SKILL.md](../../../SKILL.md)：任务入口、语义检查边界和记录格式说明。\n'
  '\n'
  '### 全部选择披露\n'
  '\n'
  '**最终期望：** 用户能够看到 Agent 真实决定了什么，不仅是几个显眼例子。\n'
  '\n'
  '**当前阶段约定：** 披露每个具体规则、取值、条件、先后顺序、输出和副作用，包含默认值、存储与数据流、算法、依赖、内部结构、触发、失败处理、界面文案、样式与交互。必要、合理、惯常、继承而来或影响很小，都不能成为隐藏理由。\n'
  '\n'
  '例如只要求“文件复制器”时，覆盖、递归、链接、元数据、并发、校验和半途失败处理仍是未约定内容。按主题分组可合并重复说明，但须保留各自条件与后果；简洁不缩小发现与披露范围。\n'
  '\n'
  '核对真实产物中的选择在报告中的落点，修正概括压掉的细节及同类遗漏；摘要、详情和附录保持一致。继承行为查明或标明未核实，“只读”等名称不证明无副作用，验证结果不证明决定来源。临时笔记按需使用，不转为常驻语义账本。\n'
  '\n'
  '**本阶段完成条件：** 全部已检查选择及未完成范围均可追溯；完整性不能由已读文件数、缺陷数或措辞自信证明。\n'
  '\n'
  '**关联约定：** 细化[要求与产物双向对照](#要求与产物双向对照)中对实现选择的核查范围；向[结果呈现与交付](#结果呈现与交付)提供每项选择、条件和后果。\n'
  '\n'
  '**关联文件：** '
  '[audit-presentation.md](../../../references/audit-presentation.md)：双向核查、选择披露、修复信息和交付规则；[view-content.md](../../../references/view-content.md)：报告内容、语义来源与记录到图的含义对应。\n'
  '\n'
  '### 可省附加机制\n'
  '\n'
  '**最终期望：** 优先让用户看见没有细说、整层不加也不影响所需能力的机制及其代价。\n'
  '\n'
  '**当前阶段约定：** 有证据时突出可省附加层，说明去掉后仍能做什么、失去什么、移除边界、前提、兼容牵连和资源影响；其他默认值及必须选一种的实现仍完整披露。\n'
  '\n'
  '检查真实生产方、消费者和失败路径，区分移除机制与另选替代方案。SHA-256 '
  '是示例而非可删规则：可能是附加检测，也可能承担用户要求的来源身份。正常输入对照成功不足以证明所有场景无影响，不虚构收益、节省量或必要性评分；探索原型不等于可交付变更。\n'
  '\n'
  '**本阶段完成条件：** 用户可据保留能力、损失及未知后果判断取舍；证据不足时不确信推荐删除。\n'
  '\n'
  '**关联约定：** 从[全部选择披露](#全部选择披露)的选择中识别可整层省去的候选；向[修复确认](#修复确认)提供移除边界及未定后果。\n'
  '\n'
  '**关联文件：** [audit-presentation.md](../../../references/audit-presentation.md)：双向核查、选择披露、修复信息和交付规则。\n'
  '\n'
  '### 修复确认\n'
  '\n'
  '**最终期望：** 检查后说明修复需要哪些信息、其中哪些真正需要用户决定。\n'
  '\n'
  '**当前阶段约定：** 先复用用户已有意图、回答和授权，并调查可查事实；只询问影响修复目标、范围、完成要求或重要后果的未定事项。说明不确定性、具体问题、可比较方案、不同答案的影响和依赖工作，有依据时给建议。\n'
  '\n'
  '恢复明确要求及普通实现判断不增加统一审批；无新增确认点时简短说明。未约定内容不会因无需询问而从报告中消失，也不会自动获得删除授权。\n'
  '\n'
  '即使只要求检查，也应给出这项判断。等待必要回答时继续已授权且独立的工作，只暂停依赖答案的部分；已有授权不重复询问。确需额外授权时先完成可做的准备，确认后将被接受的长期决定写回语义。\n'
  '\n'
  '**本阶段完成条件：** 修复所需的真正未定信息和决策明确，用户可判断具体选项；没有新增确认点时如实说明。\n'
  '\n'
  '**关联约定：** 把用户接受的修复约定交给[当前含义更新](records.md#当前含义更新)保存；向[结果呈现与交付](#结果呈现与交付)提供真正需要决定的问题及其影响。\n'
  '\n'
  '**关联文件：** [audit-presentation.md](../../../references/audit-presentation.md)：双向核查、选择披露、修复信息和交付规则。\n'
  '\n'
  '### 结果呈现与交付\n'
  '\n'
  '**最终期望：** 用户先看清检查发现的整体关系，再逐层理解真实做法、未指定选择及其影响；完整要求、细节和来源可查，呈现模板可供不同项目复用。\n'
  '\n'
  '**当前阶段约定：** 可视化是语义检查结果的输出方式，以已核查的发现和证据组织报告，继承该次检查的范围与验证局限。\n'
  '\n'
  '明确要求语义检查时，默认提供本地交互 HTML／SVG 及可编辑检查 Markdown，用户指定其他格式时遵循。可视化为主要阅读入口，Markdown '
  '按约定及其实际实现关系组织完整发现与证据，服务图、详情和原文查阅，不单独规定长报告的线性阅读顺序。\n'
  '\n'
  '用户补充：“我感觉还需要一个汇总页面，毕竟用户也可能懒得仔细看，只想看看汇总后的不一致，这个得单独加”。另外提供独立的差异汇总页面，便于用户快速查看检查发现。\n'
  '\n'
  '用户补充：“需要突出显示跟‘限制’相违背的差异，因为这是用户最关心的”。优先突出已经确认违背用户限制的差异，并保留对应的限制、实际做法和来源；未指定内容仍按原约定披露，不自动等于违反限制。\n'
  '\n'
  '默认阅读路径为“用户约定 → 对应的实际流程 → '
  '关键步骤、选择与证据”；共同范围、结论、验证局限集中说明，附录、已检查及未检查范围和复用证据日期均可查阅。全部实现组及未约定选择保留，不能只选重要例子；完整内容也应适于阅读和打印。\n'
  '\n'
  '只有有用且目标存在时才链接其他视图。来源、用户阶段约定与真实实现保持不同身份，未指定实现不因放进要求框而成为用户同意的内容。更改呈现不代表重新验证底层产品。\n'
  '\n'
  '#### 范围与内容\n'
  '\n'
  '检查报告在本次检查范围内选择项目总览、单模块或多模块模式。项目总览粗略展示边界和主关系；单模块展示内部职责、过程、分支和选择；多模块展示主要交互及相关内部过程。通常聚焦最新修改模块，同时保留理解所需上下文；范围确实不明时才询问，不自动生成所有模式或组合。检查范围与阅读入口分开：范围内默认按相关约定进入，用户明确要求架构／流程总览时可从该视图进入，约定仍是判断依据。\n'
  '\n'
  '以用户语义为骨架，互补要求同层关联，细化或归属用嵌套表达。大框与同层节点之间应有明确的过程、信息或约束关系，保留操作、判断、等待恢复、输入输出、返回及相关异常，不能只堆卡片或把清单连成流程。非执行规则画关系，不暗示自动状态机或工具执行顺序。\n'
  '\n'
  '图上标题、节点、关系标签和详情中的用户要求，均遵循项目共同限制中的原话规则；过长时稍微压缩，详情或来源保留完整措辞。原话不可得时引用连续语义记录原文，说明出处；Agent '
  '整理的分组、缩写和实现观察保留各自身份、条件与例外。共享实现保留一个主要说明，相关约定精确链接到对应步骤，并可返回；不为不同约定重复整章实现。未实现要求和无明确用户要求的配套实现都保留。\n'
  '\n'
  '最终期望与当前阶段约定均进入“用户要求”，真实实现须另行核查。已明确延期的功能显示为后续范围；关联文件仅用于定位。缺少语义内容仍显示缺少，未核查、未核实和未约定分别表达。\n'
  '\n'
  '#### 层级展开\n'
  '\n'
  '最多三层：用户约定、对应的实际流程、按需关键步骤；简单内容可以更早结束，具体参数与证据进入末端详情。每张局部图保持简洁，重要完成条件、等待、返回和失败仍可见，完整内容不因简化而丢失。\n'
  '\n'
  '初始只显示主图；选中约定或步骤后在下方展开，保留祖先图和选中状态。每层保留一条分支，切换上层时替换后代。末端节点与关系显示详情，父节点自己的说明和来源仍可折叠查阅。\n'
  '\n'
  '子图外框对应整个父节点职责，说明本层从上层哪里进入、携带什么输入，结果或影响接回哪里；用必要的上层引用和边界连接表达，不重画整个上层，也不虚构执行步骤。上下层输入输出与完成条件一致，区分返回、异步影响和完成；对应关系不明时明确缺少。\n'
  '\n'
  '#### 详情与状态\n'
  '\n'
  '汇总页和节点详情采用用户认可的读法：“具体发现 → 简短对照 → '
  '按需查看证据”。每项发现先用一句用户立即能理解的具体事实做标题；违反限制／要求未兑现给出用户要求与真实做法的简短对照，Agent自行补充直接列出具体决定，点开再看影响；尚未核实单独标明。颜色用于强调已有结论，不能代替说明差异。\n'
  '\n'
  '作用、长原文、来源、详细取舍及完整“用户要求、实际做法、影响与取舍”保留在展开内容中，作用仍须具体。适合关系、分支或映射的内容保留简单小图，节点和关系可点开说明；没有可表达关系时不制造流程。小图属于末端详情，不继续递归展开。\n'
  '\n'
  '用户补充：“用户要求、实际做法，这两点内的文字能否通过颜色来表示是哪部分做的跟用户要求的不一样、不一样的点在哪”。文字标色应能让用户看出具体哪部分不同、不同在哪里。\n'
  '\n'
  '用户未指定的具体选择直接标在实际步骤或关系上，并保留影响和约定边界；不设独立“用户未指定”字段，也不要求用户自行推断全部差异。“对齐情况”“待用户决定”“是否询问／下一步”不作为固定详情字段，总体检查结论和修复问题留在报告中；具体发现直接呈现。\n'
  '\n'
  '节点和关系的用户要求引用约定，实际观察放在实际做法中。要求明确但行为未验证时，实际做法注明未核实，不改写成约定尚未核查。打开详情前就应区分已发现的未指定选择、尚未核查及方案未定；Agent '
  '已选择实现不消除未指定状态。缺资料不证明用户没说，标记不表示实现通过或用户认可。父模块提示下层状态，已识别数量与未核查范围分别表达，不能误导为每个子项都同样缺少。\n'
  '\n'
  '完整原文、具体取值、条件、出处和上下文保持可达；未知实现写未核实，作用或影响无资料时明确缺少。图例解释所有实际使用的颜色、线型、形状和交互标识，在 HTML 与独立 SVG 中完整提供。\n'
  '\n'
  '#### 模板与浏览\n'
  '\n'
  '提供原生 SVG、HTML 骨架、样式、交互、常见流程布局和统一生成／检查入口。各项目提供自己的内容、关系、来源和父子交接，不照搬示例的模块数量；模板负责绘制与常见布局，特殊位置可以局部调整，不承诺所有复杂图都自动美观。\n'
  '\n'
  '查看器保留图的放大缩小、原生上下滚动、放大后的横向滚动、拖动、节点和关系选择及关闭详情；主界面简洁，不再提供定位下拉、搜索、定位匹配、适合宽度／全图、独立窗口、下载工具栏和缩放百分比。完整原文入口继续保留，来源路径可读。\n'
  '\n'
  '用户反馈：“每次点击节点，画面跳转太突兀了”；需要改善点击后的跳转体验。\n'
  '\n'
  '用户反馈：“这个按钮太小太偏了，很容易被忽略”；报告中的关键入口应醒目、便于发现。\n'
  '\n'
  '仅保留当前分层可视化生成链路和填写示例，删除旧版平面图、表格输出及其兼容逻辑；当前链路使用的共享组件保留。已生成的报告保留其当时身份，不自动当作当前设计。\n'
  '\n'
  '生成产物自包含，不新增 MCP 或常驻服务。保留实际输出的链接、详情、展开路径及明显布局问题检查；删除开发回归脚本、内嵌自测和模拟 DOM 测试。输出检查不等于语义完整性、真实浏览器效果或真实产品验收。\n'
  '\n'
  '**本阶段完成条件：** 检查发现、图、详情和完整原文互相对应；整体关系、父子交接及语义状态清楚，全部已核查内容与验证局限可访问。检查失败后应保留哪些输出尚未约定，不虚构发布保证。\n'
  '\n'
  '**关联约定：** '
  '接收[要求与产物双向对照](#要求与产物双向对照)的发现；接收[全部选择披露](#全部选择披露)的完整选择明细；接收[修复确认](#修复确认)的决策信息；依据[记录结构与文件组织](records.md#记录结构与文件组织)引用用户语义并保留阶段区别；使用[说明与版本](packaging.md#说明与版本)维护的模板与工具。\n'
  '\n'
  '**关联文件：** '
  '[audit-presentation.md](../../../references/audit-presentation.md)：双向核查、选择披露、修复信息和交付规则；[view-content.md](../../../references/view-content.md)：报告内容、语义来源与记录到图的含义对应；[template-usage.md](../../../references/template-usage.md)：报告输入与生成方法；[flow.py](../../../assets/audit-svg/flow.py)：布局与生成／输出检查入口；[layers.py](../../../assets/audit-svg/layers.py)：分层展开、父职责边界及上下层交接；[semantic_template.py](../../../assets/audit-svg/semantic_template.py)：语义字段、详情与状态汇总；[mini_diagram.py](../../../assets/audit-svg/mini_diagram.py)：详情中的简图；[check_report.py](../../../assets/audit-svg/check_report.py)：生成报告的结构、状态标记与基础几何检查；[viewer.js](../../../assets/audit-svg/viewer.js)：节点选择、缩放滚动、展开与打印交互。\n'),
 ('docs/showcase/semantics/packaging.md',
  '# Skill 说明与交付\n'
  '\n'
  '## 目的\n'
  '\n'
  '让 Agent 以简短、职责明确的说明使用现有能力，让用户方便审阅当前约定。\n'
  '\n'
  '## 限制\n'
  '\n'
  '项目语义与开发维护资料存放在安装包之外并予以保留。说明中只保留影响判断、操作或本 Skill 特有边界的内容，删去通用常识、重复论证、冗长例子及已被当前规则覆盖的历史禁令。\n'
  '\n'
  '## 用户约定\n'
  '\n'
  '### 说明与版本\n'
  '\n'
  '**最终期望：** Skill 的说明与模板容易理解、可复用，用户能审阅其含义。\n'
  '\n'
  '**当前阶段约定：** 能一句话说清的规则用一句话。入口围绕语义检查及其记录依据组织；检查说明负责核查与结果交付，报告内容与来源、报告模板使用两份说明辅助交付。规则在负责位置定义，其余引用。\n'
  '\n'
  'README 也应服务于本项目的设计目的，并考虑哪些用户真正需要它。用户原话：“需要满足我们的设计目的，想想会有哪些用户需要这个”。 README '
  '要有吸引力，用户要求：“开头两句要直击问题，然后简单说我们怎么解决，然后要附图”。\n'
  '\n'
  '模板说明只解释选择模板、输入字段及其含义、生成和检查。颜色、线型、尺寸、布局和交互由现有模板提供，不另写一套手工绘图规范或完整底层 API 清单；需要例外调整时按需查阅实现。\n'
  '\n'
  '英文为正式来源和安装版本，中文按文件对应，供用户审阅，不参与安装或触发；代码示例和 API 标识保持原文。修改后同步安装副本与中文稿。安装包只保留当前出图链路、必要输出检查和模板填写示例，删除旧版兼容及开发测试。\n'
  '\n'
  '停用 TaskMemory MCP，日常语义维护使用文件，不恢复旧工具或新增常驻服务。说明精简保留完整披露、来源区分、从产物反查与当前语义一致性。\n'
  '\n'
  '**本阶段完成条件：** 各份说明职责明确且无重复定义，英文、安装副本和中文含义对应；语义记录独立保留。\n'
  '\n'
  '**关联约定：** '
  '依[记录结构与文件组织](records.md#记录结构与文件组织)保留独立项目记录；为[结果呈现与交付](audit.md#结果呈现与交付)提供当前模板、说明及工具；在说明精简时保留[全部选择披露](audit.md#全部选择披露)的范围与来源要求。\n'
  '\n'
  '**关联文件：** [README.md](../../../README.md)：面向使用者的项目说明；README '
  '中文审阅稿（历史本地资料，未公开）：对应英文介绍；[SKILL.md](../../../SKILL.md)：任务入口、语义检查边界和记录格式说明；[view-content.md](../../../references/view-content.md)：报告内容、语义来源与记录到图的含义对应；[template-usage.md](../../../references/template-usage.md)：报告输入与生成方法；[audit-presentation.md](../../../references/audit-presentation.md)：双向核查、选择披露、修复信息和交付规则；中文审阅稿（历史本地资料，未公开）：与英文对应的用户审阅文本；[MAINTENANCE.md](../MAINTENANCE.md)：独立保存实现观察及维护资料。\n'),
 ('docs/showcase/semantics/records.md',
  '# 语义记录\n'
  '\n'
  '## 目的\n'
  '\n'
  '用明确、可直接修改的 Markdown 保存用户当前有效的语义，便于按范围检索和使用。\n'
  '\n'
  '## 限制\n'
  '\n'
  '遵循[项目共同限制](../SEMANTICS.md#限制)。正文保留完整条件、例外和约定含义；考虑常见工具的搜索、分段读取及局部修改能力，但不规定阅读工具、固定顺序或每次整节重读。\n'
  '\n'
  '## 用户约定\n'
  '\n'
  '### 记录结构与文件组织\n'
  '\n'
  '**最终期望：** 让用户和 Agent 能区分完整目标、本阶段要做什么，以及各约定之间的关联。\n'
  '\n'
  '**当前阶段约定：** 采用“目的、限制、用户约定”的组织方式。约定按用户关心的对象或能力分组，不要求固定经过“项目 → 模块 → '
  '功能”的层级。每个约定主题保留“最终期望、当前阶段约定、本阶段完成条件、关联约定、关联文件”五个字段；主题可以是整体职责，也可以是具体行为，有明确细化关系时再展开。\n'
  '\n'
  '用户明确的模块边界和功能关系仍属于约定；Agent '
  '为阅读而作的分组标明整理身份。共同限制放在上层，主题特有限制就近写。格式说明须逐项解释各部分记录什么、各字段之间的区别及未约定时的写法，而不只提供标题。本阶段将已认可的组织方式用于正式 Skill，并同步安装版和中文审阅稿。\n'
  '\n'
  '最终期望与当前阶段约定都来自用户；没有明确区分时保留未约定，不推演未来安排。完成条件已写在约定中时可引用，没说则标明未约定。实际实现、检查结果和 Agent 自行选择的实现细节放在检查或维护资料中。\n'
  '\n'
  '关联文件支持多个文件或目录，区分用户明确指定的路径与 Agent 整理的索引；文件路径不证明实现。关联约定说明有依据的依赖、输入输出、细化或共同约束，不凭目录排布推断流程。\n'
  '\n'
  '语义记录在 100 行以内使用单文件，超过 100 行时可以按主题拆分；不限制拆出文件的大小。入口保留共同含义和约定索引，索引不重复正文；说明中明确主文件和拆出文件的存放位置。文件边界用于存储，不自动成为模块边界。\n'
  '\n'
  '**本阶段完成条件：** 结构明确，两类用户语义与真实实现分开；本次修改后须确认结果可视化仍可使用这些记录。\n'
  '\n'
  '**关联约定：** 向[结果呈现与交付](audit.md#结果呈现与交付)提供用户原文和结构；向[要求与产物双向对照](audit.md#要求与产物双向对照)提供用户语义基线。\n'
  '\n'
  '**关联文件：** '
  '[SKILL.md](../../../SKILL.md)：任务入口、语义检查边界和记录格式说明；[本项目入口](../SEMANTICS.md)：当前用户语义入口与主题索引；[view-content.md](../../../references/view-content.md)：报告内容、语义来源与记录到图的含义对应。\n'
  '\n'
  '### 当前含义更新\n'
  '\n'
  '**最终期望：** 记录直接表达当前共识，读者无需追溯设计演变。\n'
  '\n'
  '**当前阶段约定：** 新约定替换已被取代的说法并同步受影响引用；保留未被取消的条件、例外和其他要求。保留变体写明适用条件，未解决的意图冲突保持明确，不能用“兼容”掩盖矛盾。\n'
  '\n'
  '阶段推进时更新当前阶段约定；用户改变完整目标时更新最终期望，不追加开发历史。不把实际产物反写为用户要求，也不因实现存在或测试通过就视为用户接受。带日期的检查与示例保持其证据身份，不直接充当当前用户语义。\n'
  '\n'
  '**本阶段完成条件：** 受影响含义形成一致的当前描述，保留本次未取消的要求；仍有冲突时说明未完成处。\n'
  '\n'
  '**关联约定：** 接收[长期语义维护](activation.md#长期语义维护)识别的长期变更；保存[修复确认](audit.md#修复确认)中用户已接受的新约定。\n'
  '\n'
  '**关联文件：** [SKILL.md](../../../SKILL.md)：任务入口、语义检查边界和记录格式说明；[本项目入口](../SEMANTICS.md)：当前用户语义入口与主题索引。\n'
  '\n'
  '### 记录迁移\n'
  '\n'
  '**最终期望：** 改变记录形式时不遗漏有效要求，也不改变原意。\n'
  '\n'
  '**当前阶段约定：** 以当前有效用户含义为基准，核对所有条件、例外、阶段边界及未解决约定；按主题合并重复内容。实现资料与语义分开保留，不能把它们冒充用户认可，也不能因格式迁移而丢失资料。\n'
  '\n'
  '停止旧生成器覆盖新正文；删除旧记录遵循实际授权，不把未安装或未知术语等同于无用。一次性核对和恢复备份不进入日常上下文；其他项目按实际请求处理。\n'
  '\n'
  '**本阶段完成条件：** 全部有效要求保留且原意不变；本项目记录完成新格式转换并确认结果可视化仍可使用这些记录。\n'
  '\n'
  '**关联约定：** 采用[记录结构与文件组织](#记录结构与文件组织)作为目标格式；按[说明与版本](packaging.md#说明与版本)将用户语义与安装资料分开保留。\n'
  '\n'
  '**关联文件：** '
  '[本项目入口](../SEMANTICS.md)：当前用户语义入口与主题索引；[MAINTENANCE.md](../MAINTENANCE.md)：独立保存实现观察及维护资料；[SKILL.md](../../../SKILL.md)：任务入口、语义检查边界和记录格式说明。\n')]

REPORT['data']['source_html']='<section id="complete-report">'+md_html((HERE/'report.md').read_text())+'</section><section id="full-records"><h2>本次完整用户记录基线</h2>'+''.join('<details id="record-'+Path(path).stem+'"><summary>'+html.escape(path)+'</summary>'+md_html(text,path)+'</details>' for path,text in BASELINE)+'</section>'
if __name__=='__main__':print(build_report(REPORT,HERE))
