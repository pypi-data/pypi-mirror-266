import io
import os
import re
from enum import Enum
from dataclasses import dataclass
import functools

import numpy as np
import pandas as pd
import networkx as nx
from matplotlib import pyplot as plt


@dataclass(frozen=True)
class Sheet:
    name: str
    transpose: bool

class Kind(Enum):
    HAZARD = 'H'
    CAUSE = 'CA'
    CONTROL = 'CO'


@dataclass(frozen=True)
@functools.total_ordering
class Node:
    kind: Kind
    number: int

    def to_str(self) -> str:
        return f'{self.kind.value}-{str(self.number).zfill(ZERO_PADDING_DIGITS)}'

    @classmethod
    def from_str(cls, string: str):
        match = re.match(NODE_MATCHER, string)
        if not match: raise Exception(f'{string} couldn\'t be parsed as a node')

        return cls(
            KIND_STR_DICT[match['kind']],
            int(match['number']),
        )

    def __lt__(self, other) -> bool:
        self.number < other.number


OUTPUT_DIR = './output'
if not os.path.exists('./output'): os.system(f'mkdir {OUTPUT_DIR}')
ZERO_PADDING_DIGITS = 2
RENDERING_DPI = 480

NODE_MATCHER = re.compile(r'^(?P<kind>H|CA|CO)-?(?P<number>\d+)$')
MAPPING_MATCHER = re.compile('^\s*[Y]\s*$', re.I)

KIND_STR_DICT = {
    'H': Kind.HAZARD,
    'CA': Kind.CAUSE,
    'CO': Kind.CONTROL,
}

KIND_COLOURS = {
    Kind.HAZARD: '#d2476b',
    Kind.CAUSE: '#7d5594',
    Kind.CONTROL: '#2762bc',
}


class HazardMap:
    def __init__(self, workbook_path: str):
        self.WORKBOOK_NAME = self.parse_workbook_filename(workbook_path)

        self.graph = nx.Graph()

    def parse_workbook_filename(self, workbook_path: str) -> str:
        workbook_filename = os.path.basename(workbook_path)
        workbook_filename_parts = workbook_filename.split('.')
        if workbook_filename_parts[-1] == 'xlsx': 
            return '.'.join(workbook_filename_parts[:-1])
        else:
            raise Exception('Please upload an xlsx file')

    def extract_sheet_mappings(self, sheets: list[Sheet]):
        for sheet in sheets:
            df = pd.read_excel(self.WORKBOOK_NAME, sheet.name, index_col=0)
            if sheet.transpose: df = df.T

            df.apply(self._extract_individual_mappings, axis=1)

    def _extract_individual_mappings(self, row: pd.Series):
        map_from = Node.from_str(row.name)

        row = row.dropna()
        mapped = row[row.str.match(MAPPING_MATCHER)].index.str.strip().to_list()
        mapped_typed = [Node.from_str(node_str) for node_str in mapped]
        
        for map_to in mapped_typed: self.graph.add_edge(map_from, map_to)

    def write_to_file(self):
        with pd.ExcelWriter(
            f'{OUTPUT_DIR}/{self.WORKBOOK_NAME}-hazard_log_format.xlsx',
        ) as writer:
            for hazard in self.filter_node_set_for_kind(
                self.graph.nodes, 
                Kind.HAZARD,
            ):
                cause_control_mappings = []
                for cause in self.filter_node_set_for_kind(
                    self.graph[hazard], 
                    Kind.CAUSE,
                ):
                    for control in self.filter_node_set_for_kind(
                        self.graph[cause], 
                        Kind.CONTROL,
                    ):
                        cause_control_mappings.append((cause.to_str(), control.to_str()))
                df = (
                    pd.DataFrame(
                        data=cause_control_mappings, 
                        columns=['cause', 'control'],
                    )
                    .set_index('cause', append=True)
                    .reorder_levels([1, 0])
                    .to_excel(writer, sheet_name=hazard.to_str())
                )

    def filter_node_set_for_kind(self, node_set: set, kind: Kind) -> list[Node]:
        return sorted([node for node in node_set if node.kind == kind])

    def draw_graph(self) -> (plt.Figure, plt.Axes):        
        self.fig, self.ax = plt.subplots(
            frameon=False,
            figsize=(9, 7),
            dpi=RENDERING_DPI,
        )
        self.ax.axis('off')
    
        nx.draw_networkx(
            self.graph,
            pos=nx.kamada_kawai_layout(self.graph),
            node_color=[
                KIND_COLOURS.get(node.kind, '#53676c') 
                for node in self.graph.nodes
            ],
            labels={node: node.to_str() for node in self.graph.nodes},
            node_size=self._define_node_sizes((100, 250)),
            font_size=3,
            alpha=0.9,
            edge_color=(0.5, 0.5, 0.5, 0.9),
            width=0.5,
            ax=self.ax,
        )

        return self.fig, self.ax

    def _define_node_sizes(
        self, 
        size_limits: tuple[float, float],
    ) -> list[float]:
        degrees = self.graph.degree()
        large_connect = np.percentile([n_connections for node, n_connections in degrees], 97)
        add_size_per_connect = (size_limits[1] - size_limits[0]) / large_connect

        return [
            min([
                size_limits[0] + add_size_per_connect*n_connections,
                size_limits[1],
            ])
            for node, n_connections in degrees
        ]

    def save_graph(self): 
        if not hasattr(self, 'fig'):
            self.draw_graph()

        filename = (
            f'{OUTPUT_DIR}/{self.WORKBOOK_NAME}'
            '-graph_rendering'
            f'-{str(hash(self.graph))[-4:]}'
            '.png'
        )

        plt.savefig(filename, transparent=True, dpi=RENDERING_DPI)

    def get_kind_connection_counts(self, kind: Kind) -> pd.DataFrame:
        comparison_kinds = [Kind.HAZARD, Kind.CAUSE, Kind.CONTROL]
        
        counts = [
            tuple([node.to_str()] + [
                    len(self.filter_node_set_for_kind(
                        self.graph.neighbors(node), 
                        comp_kind,
                    ))
                    for comp_kind in comparison_kinds
                ])
            for node in self.filter_node_set_for_kind(hazard_map.graph.nodes, kind)
        ]
            
        df = (
            pd.DataFrame(
                data=counts, 
                columns=['node'] + [kind.name.lower() for kind in comparison_kinds]
            )
            .set_index('node')
        )
        df = df.drop(columns=[column for column in df.columns if df[column].sum() == 0])
        
        if len(df.columns) > 1:
            df['total'] = df.apply(np.sum, axis=1)
            df = df.sort_values('total', ascending=False)
        else:
            df = df.sort_values(df.columns[0], ascending=False)
            
        return df
    
