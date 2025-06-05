import pygame
import random
from engine import *


class Game:
    def __init__(self):
        self.WIDTH = 1000
        self.HEIGHT = 1000

        # pygame 셋팅
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("D2Coding", 15)

        # 데이터 호출
        self.map_data = load_map("./map/map1.dat")
        self.points = self.map_data.nodes
        self.spawn_options = [
            (-150, 500, 1),
            (500, -150, 2),
        ]

        self.cars: list[Car] = []

    def main_loop(self, debug_string):
        debug_string.clear()
        self.screen.fill(Color.WHITE)

        # --- 이벤트 처리 파트 -----------------------------------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            # 신호등 클릭여부 검사
            elif event.type == pygame.MOUSEBUTTONUP:
                for _, point in self.points.items():
                    if point.is_juction and point.rect.collidepoint(event.pos):
                        point.toggle()

        # --- 로직 파트 ------------------------------------------------------------------------------------------------
        if random.random() < 0.01:
            spawn_x, spawn_y, path_id = random.choice(self.spawn_options)
            self.cars.append(Car(Point(spawn_x, spawn_y), self.map_data.paths[path_id]))

        # --- 그리기 파트 ----------------------------------------------------------------------------------------------
        # 도로 그리기
        for _, link in self.map_data.links.items():
            pygame.draw.line(self.screen,
                             Color.BLACK,
                             link.get_start_pos(),
                             link.get_end_pos(),
                             30)

        # 신호등 그리기
        for _, point in self.points.items():
            point.draw(self.screen)

        # 차량 업데이트 및 그리기
        for n, vehicle in enumerate(self.cars):
            if vehicle.disabled:
                self.cars.pop(n)
            vehicle.update()
            vehicle.draw(self.screen)
            debug_string.append(f"car {n}")
            vehicle.debug(debug_string)

        # 디버깅용 텍스트 출력
        y_offset = 10
        for line in debug_string:
            text_surface = self.font.render(line, True, (0, 0, 0))  # 검정 텍스트
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 15

        # --- 그리기 종료 ----------------------------------------------------------------------------------------------
        pygame.display.flip()
        self.clock.tick(60)

    def main(self):
        debug_string = []

        # 메인 루프
        while 1:
            if self.main_loop(debug_string):
                break
        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.main()
