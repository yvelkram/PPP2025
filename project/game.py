import pygame

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
        map_data = load_map("./map/map1.dat")
        self.points = map_data.nodes

        # 차량 생성 (왼쪽 → 오른쪽 → 아래)
        self.cars = [Car(Point(10, 190), map_data.paths[1])]


    def main(self):
        debug_string = []

        # 메인 루프
        running = True
        while running:
            debug_string.clear()
            self.screen.fill(Color.WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # 신호등 클릭여부 검사
                elif event.type == pygame.MOUSEBUTTONUP:
                    for _, point in self.points.items():
                        if point.is_juction and point.rect.collidepoint(event.pos):
                            point.toggle()

            # 신호등 그리기
            for _, point in self.points.items():
                point.draw(self.screen)

            # 차량 업데이트 및 그리기
            for n, vehicle in enumerate(self.cars):
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

            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.main()

