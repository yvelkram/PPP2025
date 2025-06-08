from dataclasses import dataclass
from .point import Point, Link, Path


@dataclass
class MapData:
    nodes: dict[int, Point]  # 노드 리스트 (신호등, 스폰점 포함)
    links: dict[int, Link]   # 링크 리스트
    paths: dict[int, Path]   # 경로 리스트


def load_map(file_path) -> MapData:
    """
    맵 데이터 불러와서 파싱하는 함수
    :param file_path: 파일 경로
    :return: 노드, 링크, 경로가 구조화된 딕셔너리 데이터
    """
    nodes: dict[int, Point] = {}
    links: dict[int, Link] = {}
    paths: dict[int, Path] = {}

    with open(file_path, 'r') as f:
        for ln in f:
            ln = ln.strip()

            if ln.startswith("N"):  # 일반 노드
                _, node_id, coords = ln.split()
                x, y = coords.split(',')
                nodes[int(node_id)] = Point(int(x), int(y))
            elif ln.startswith("T"):  # 신호등 노드
                _, node_id, coords = ln.split()
                x, y = coords.split(',')
                nodes[int(node_id)] = Point(int(x), int(y), is_juction=True)
            elif ln.startswith("S"):  # 차량 스폰 노드
                _, node_id, coords = ln.split()
                x, y = coords.split(',')
                nodes[int(node_id)] = Point(int(x), int(y), is_spawn=True)

            elif ln.startswith("L"):  # 링크
                _, link_id, node_ids = ln.split()
                start_id, end_id = node_ids.split(',')
                links[int(link_id)] = Link(nodes[int(start_id)], nodes[int(end_id)])

            elif ln.startswith("P"):  # 경로
                _, path_id, link_ids = ln.split()
                paths[int(path_id)] = Path()
                for link_id in link_ids.split(','):
                    paths[int(path_id)].add_link(links[int(link_id)])

            else:  # 아무것도 아닌 줄
                continue

    return MapData(nodes=nodes, links=links, paths=paths)


def get_spawn_point(paths: dict[int, Path]) -> list[tuple[int, int, int]]:
    """
    스폰지점으로 설정된 점만 따로 추출해서 내보내줌
    :param paths: 전체 경로 데이터
    :return: (좌표, 좌표, 경로번호)
    """

    spawn_point = []
    for n, path in paths.items():
        for point in path.get_nodes():
            if point.is_spawn:
                spawn_point.append((point.x, point.y, n))

    return spawn_point
