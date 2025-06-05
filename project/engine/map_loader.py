from dataclasses import dataclass
from .point import Point, Link, Path


@dataclass
class MapData:
    nodes: dict[int, Point]
    links: dict[int, Link]
    paths: dict[int, Path]


def load_map(file_path) -> MapData:
    nodes: dict[int, Point] = {}
    links: dict[int, Link] = {}
    paths: dict[int, Path] = {}

    with open(file_path, 'r') as f:
        for ln in f:
            ln = ln.strip()

            if ln.startswith("N"):
                _, node_id, coords = ln.split()
                x, y = coords.split(',')
                nodes[int(node_id)] = Point(int(x), int(y))

            elif ln.startswith("T"):
                _, node_id, coords = ln.split()
                x, y = coords.split(',')
                nodes[int(node_id)] = Point(int(x), int(y), is_juction=True)

            elif ln.startswith("L"):
                _, link_id, node_ids = ln.split()
                start_id, end_id = node_ids.split(',')
                links[int(link_id)] = Link(nodes[int(start_id)], nodes[int(end_id)])

            elif ln.startswith("P"):
                _, path_id, link_ids = ln.split()
                paths[int(path_id)] = Path()
                for link_id in link_ids.split(','):
                    paths[int(path_id)].add_link(links[int(link_id)])

            else:
                continue

    return MapData(nodes=nodes, links=links, paths=paths)

