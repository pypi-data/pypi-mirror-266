from typing import Dict, Tuple
from uuid import uuid4

import networkx as nx


def _split_measure(value: str):
    digits = [c for c in value if not c.isalpha()]
    letters = [c for c in value if c.isalpha()]

    return float(''.join(digits)), ''.join(letters)


def _scale_measure(attr: str, value: str, scale: float = 2.0, offset: float = 0.3):
    num, unit = _split_measure(value)
    return f'`${{{num} / ({attr}.size * {scale}) + {offset}}}{unit}`'


def graph_to_html(graph: nx.Graph, layout: Dict,
                  weights: str = None,
                  display_height: str = '40rem', max_width: str = '100%',
                  node_width: str = '10rem', node_height: str = '2rem') -> Tuple[str, str]:
    nodes = list(graph.nodes())
    adj = nx.to_numpy_array(graph)

    min_x, max_x, min_y, max_y = None, None, None, None
    for (px, py) in layout.values():
        if min_x is None or px < min_x:
            min_x = px
        if max_x is None or px > max_x:
            max_x = px
        if min_y is None or py < min_y:
            min_y = py
        if max_y is None or py > max_y:
            max_y = py

    nodes_html = []
    nodes_positions = {}

    for key, (px, py) in layout.items():
        left = (px - min_x) / (max_x - min_x) * 100 if min_x < max_x else 50
        top = (py - min_y) / (max_y - min_y) * 100

        nodes_html.append(f'''
            <div class="node"
                 style="left: calc({left}% - {node_width} / 2); top: calc({top}% - {node_height} / 2)"
                 :style="frame.node_{key}">
                {{{{frame.name_{key}}}}}
            </div>
        ''')
        nodes_positions[key] = (left, top)

    lines_svg_defs = []
    lines_svg = []

    for row_i, (row, source_node) in enumerate(zip(adj, nodes)):
        for col_i, (value, target_node) in enumerate(zip(row, nodes)):
            if value and row_i < col_i:
                id = str(uuid4()).replace('-', '')
                x1, y1 = nodes_positions[source_node]
                x2, y2 = nodes_positions[target_node]

                if x2 < x1:
                    x1, y1, x2, y2 = x2, y2, x1, y1
                    arrow = 'marker-start'
                    orient = 'auto-start-reverse'
                else:
                    arrow = 'marker-end'
                    orient = 'auto'

                attr = f'frame.edge_{source_node}_{target_node}'

                if isinstance(graph, nx.DiGraph):
                    marker_id = str(uuid4()).replace('-', '')

                    lines_svg_defs.append(f'''
                        <marker id="head-{marker_id}" orient="{orient}"
                                v-bind="{{ 'refX': {_scale_measure(attr, node_width)} }}" refY="5"
                                markerHeight="40" markerWidth="50">
                            <path :fill="{attr}.backgroundColor" d="M0,0 V10 L5,5 Z" />
                        </marker>
                    ''')
                    lines_svg.append(f'''
                        <line id="{id}" 
                              x1="{x1}%" y1="{y1}%" x2="{x2}%" y2="{y2}%"
                              :stroke-width="{attr}.size ?? 2" :stroke="{attr}.backgroundColor"
                              {arrow}="url(#head-{marker_id})" />
                    ''')
                else:
                    lines_svg.append(f'''
                        <line id="{id}" 
                              x1="{x1}%" y1="{y1}%" x2="{x2}%" y2="{y2}%"
                              :stroke-width="{attr}.size ?? 2" :stroke="{attr}.backgroundColor" />
                    ''')

                if weights is not None:
                    weight = graph.get_edge_data(source_node, target_node)[weights]
                else:
                    weight = f'{{{{{attr}.text}}}}'

                lines_svg.append(f'''
                    <text font-size="10" :stroke="{attr}.color">
                        <textPath href="#{id}" startOffset="50%" text-anchor="middle">{weight}</textPath>
                    </text>
                ''')

    nodes_html_str = '\n'.join(nodes_html)
    lines_svg_devs_str = '\n'.join(lines_svg_defs)
    lines_svg_str = '\n'.join(lines_svg)

    lines_svg_str += '<textPath path="M0%,0% L20%,20%">?</textPath>'

    return f'''
        <div class="node-wrapper">
            <div class="node-container">
                <svg style="overflow: visible">
                    <defs>
                        {lines_svg_devs_str}
                    </defs>

                    {lines_svg_str}
                </svg>
    
                {nodes_html_str}
            </div>
        </div>
    ''', f'''
        .node-wrapper {{
            padding: calc({node_height} / 2) calc({node_width} / 2);
            box-sizing: border-box;
        }}
    
        .node-container {{
            width: 100%;
            max-width: {max_width};
            height: {display_height};
            position: relative;
        }}

        .node-container svg {{
            width: 100%;
            height: {display_height};
        }}

        .node-container .node {{
            position: absolute;
            width: {node_width};
            height: {node_height};
            background-color: red;
            
            display: flex;
            justify-content: center;
            align-items: center;

            border-radius: calc({node_height} / 2);
        }}
    '''
