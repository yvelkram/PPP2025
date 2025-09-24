import pygame
import random
from engine import *


# todo : 스코어 시스템 만들기
# todo 1. 남은 초시간 계산하기
# todo 2. 목표 대수 보여주기


class Game:
    def __init__(self):
        self.WIDTH = 1000
        self.HEIGHT = 1000
        self.zoom = 30

        # pygame 셋팅
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("D2Coding", 15)

        # --- 맵 데이터 ------------------------------------------------------------------------------------------------
        self.map_data = load_map("./map/map2.dat")
        self.spawn_options = get_spawn_point(self.map_data.paths)

        # --- 변수 -----------------------------------------------------------------------------------------------------
        self.cars: list[Car] = []
        self.car_num = 0
        self.tick = 60

    def main_loop(self, debug_string) -> bool:
        debug_string.clear()
        debug_string.append(f"tickspeed : {self.tick}")
        self.screen.fill(Color.WHITE)

        # --- 이벤트 처리 파트 -----------------------------------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            # 마우스 클릭 이벤트
            if event.type == pygame.MOUSEBUTTONUP:
                # 신호등 검사 로직
                for _, point in self.map_data.nodes.items():
                    if point.is_juction and point.rect.collidepoint(event.pos):
                        point.toggle()
                # 교착상태 해결용 차량 클릭 폭파 로직
                for car in self.cars:
                    if point_in_polygon(pygame.Vector2(event.pos), car.shape):
                        car.disabled = True
            # 게임 속도 조절
            # 위/아래 화살표 : 10단위 조절 | 좌/우 화살표 : 1단위 조절 | HOME : 기본값 | END : 최솟값
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self.tick += 10
                if event.key == pygame.K_DOWN:
                    self.tick -= 10
                if event.key == pygame.K_RIGHT:
                    self.tick += 1
                if event.key == pygame.K_LEFT:
                    self.tick -= 1
                if event.key == pygame.K_HOME:
                    self.tick = 60
                if event.key == pygame.K_END:
                    self.tick = 0

        # --- 로직 파트 ------------------------------------------------------------------------------------------------
        # 틱 속도가 음수일 경우 복귀
        if self.tick < 1:
            self.tick = 1

        # 차량 스폰 (랜덤 확률)
        if random.random() < self.map_data.spawnrate:
            spawn_x, spawn_y, path_id = random.choice(self.spawn_options)
            self.cars.append(Car(self.car_num, Point(spawn_x, spawn_y), self.map_data.paths[path_id], self.zoom))
            self.car_num += 1

        # 신호등 황색불 업데이트
        for _, point in self.map_data.nodes.items():
            point.update()

        # --- 그리기 파트 ----------------------------------------------------------------------------------------------
        # 도로 그리기
        for _, link in self.map_data.links.items():
            pygame.draw.line(self.screen,
                             Color.BLACK,
                             link.get_start_pos(),
                             link.get_end_pos(),
                             self.zoom)
        # 도로 빈칸채우기
        for _, point in self.map_data.nodes.items():
            pygame.draw.circle(self.screen,
                               Color.BLACK,
                               point.get_pos(),
                               self.zoom * 0.45)

        # 차량 업데이트 및 그리기
        for n, vehicle in enumerate(self.cars):
            if vehicle.disabled:  # 차가 비활성화 되면 제거
                self.cars.pop(n)
            vehicle.update(self.cars)  # 차량 업데이트
            vehicle.draw(self.screen)
            # vehicle.debug(debug_string)
            # vehicle.debug_draw_sensor(self.screen)

        # 신호등 그리기
        for _, point in self.map_data.nodes.items():
            point.draw(self.screen, self.zoom)

        # 디버깅용 텍스트 출력
        y_offset = 10
        for line in debug_string:
            text_surface = self.font.render(line, True, (0, 0, 0))  # 검정 텍스트
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 15

        # --- 그리기 종료 ----------------------------------------------------------------------------------------------
        pygame.display.flip()
        self.clock.tick(self.tick)

        return False


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
