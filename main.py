from unittest import case
import pygame
import random
import csv
import statistics
from population import Population
from car import (
    CAR_SIZE,
    WIDTH,
    HEIGHT,
    COLOR_BG,
    COLOR_OBSTACLE,
    COLOR_TEXT,
    FPS,
    COLOR_TARGET,
)
from obstacle import Obstacle

MAX_GENS = 1000
SPAWN_FRAMES = 30


def run_simulation():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Neuroevolucion")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)

    trainning = 0
    while True:
        screen.fill(COLOR_BG)
        text_surface = font.render(
            "Pulsa un numero para | 1: Entrenar | 2: Simular el mejor controlador", True, COLOR_TEXT
        )
        screen.blit(
            text_surface,
            (
                WIDTH // 2 - text_surface.get_width() // 2,
                HEIGHT // 2 - text_surface.get_height() // 2,
            ),
        )
        text_quit = font.render(
            "Pulsa la tecla Q para salir", True, COLOR_TEXT
        )
        screen.blit(
            text_quit,
            (
                WIDTH // 2 - text_quit.get_width() // 2,
                HEIGHT - 100,
            ),
        )
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    trainning = 1
                    break
                elif event.key == pygame.K_2:
                    trainning = 2
                    break
                elif event.key == pygame.K_q:
                    trainning = 3
                else:
                    trainning = 4
                    break

        match trainning:
            case 1:
                frame_count = 0
                turbo = 0

                population = Population(size=300, load_file="weights_final.npy")
                obstacles = []
                running = True
                csv_file = open("training_metrics.csv", "w", newline="")
                csv_writer = csv.writer(csv_file, delimiter=';')
                csv_writer.writerow([
                    "Generacion",
                    "Score_max",
                    "Score_min",
                    "Score_promedio",
                    "SD_score",
                    "Tvida_max",
                    "Tvida_min",
                    "Tvida_promedio",
                    "SD_tvida"
                ])
                while running:
                    if population.generation > MAX_GENS:
                        print("Generaciones maximas alcanzadas")
                        best_car = max(population.cars, key=lambda c: c.score)
                        best_car.controller.save_model()
                        running = False

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_TAB:
                                turbo = (turbo + 1) % 3
                            if event.key == pygame.K_s:
                                best_car = max(population.cars, key=lambda c: c.score)
                                best_car.controller.save_model()
                                print("Modelo guardado con exito")
                            if event.key == pygame.K_q:
                                best_car = max(population.cars, key=lambda c: c.score)
                                best_car.controller.save_model()
                                print("Modelo guardado con exito")
                                running = False
                            if event.key == pygame.K_c:
                                print("Entrenamiento cancelado")
                                running = False

                    if not population.is_extinct():
                        frame_count += 1
                        if frame_count >= SPAWN_FRAMES:
                            obstacles.append(Obstacle())
                            frame_count = 0
                        for obs in obstacles:
                            obs.update()
                        obstacles = [
                            obs for obs in obstacles if not obs.is_off_screen()
                        ]
                        obstacle_rects = [obs.rect for obs in obstacles]

                        population.update(obstacle_rects)

                    else:
                        scores = [c.score for c in population.cars]
                        lifetimes = [c.lifetime for c in population.cars]

                        score_max = max(scores)
                        score_min = min(scores)
                        score_avg = sum(scores)/len(scores)
                        sd_score = statistics.stdev(scores) if len(scores) > 1 else 0

                        vida_max = max(lifetimes)
                        vida_min = min(lifetimes)
                        vida_avg = sum(lifetimes)/len(lifetimes)
                        sd_vida = statistics.stdev(lifetimes) if len(lifetimes) > 1 else 0
                        
                        csv_writer.writerow([
                            population.generation,
                            int(score_max),
                            int(score_min),
                            int(score_avg),
                            int(sd_score),
                            int(vida_max),
                            int(vida_min),
                            int(vida_avg),
                            int(sd_vida)
                        ])
                        csv_file.flush()
                        
                        population.evolve()
                        
                        obstacles = []
                        frame_count = 0
                        if turbo != 1:
                            pygame.time.delay(2000)

                    match turbo:
                        case 0:
                            screen.fill(COLOR_BG)

                            for obs in obstacles:
                                obs.draw(screen)

                            population.draw(screen)

                            alive_count = sum([1 for c in population.cars if c.alive])
                            status = f"Modo generacion | Gen: {population.generation} | Vivos: {alive_count} | Pulsa TAB para modo rapido"
                            screen.blit(font.render(status, True, COLOR_TEXT), (10, 10))
                            screen.blit(font.render("Pulsa la tecla | C: Cancelar | S: Guardar | Q: Guardar y salir", True, COLOR_TEXT), (10, HEIGHT - 40))
                            
                            pygame.display.flip()
                            clock.tick(FPS)
                        case 1:
                            if frame_count % 100 == 0:
                                screen.fill((0, 0, 0))
                                status = f"Modo rapido | Gen: {population.generation} | Pulsa TAB para modo lider"
                                text_status = font.render(status, True, COLOR_TEXT)
                                screen.blit(
                                    text_status,
                                    (
                                        WIDTH // 2 - text_status.get_width() // 2,
                                        HEIGHT // 2 - text_status.get_height() // 2,
                                    ),
                                )
                                
                                text_save = font.render(
                                    "Pulsa la tecla | C: Cancelar | S: Guardar | Q: Guardar y salir", True, COLOR_TEXT
                                )
                                screen.blit(
                                    text_save,
                                    (
                                        WIDTH // 2 - text_save.get_width() // 2,
                                        HEIGHT - 100,
                                    ),
                                )
                                
                                pygame.display.flip()

                        case 2:
                            screen.fill(COLOR_BG)

                            for obs in obstacles:
                                obs.draw(screen)

                            leader = population.get_best_car()
                            if leader is not None:
                                leader.draw(screen, show_sensors=True)
                                pygame.draw.rect(screen, COLOR_TARGET, leader.target)
                                status = f"Modo lider | Score: {leader.score:.2f} | Pulsa TAB para modo generacion"
                                screen.blit(
                                    font.render(status, True, COLOR_TEXT), (10, 10)
                                )
                                screen.blit(font.render("Pulsa la tecla | C: Cancelar | S: Guardar | Q: Guardar y salir", True, COLOR_TEXT), (10, HEIGHT - 40))

                            pygame.display.flip()
                            clock.tick(FPS)

                csv_file.close()
                print("Metricas guardadas correctamente")
                pygame.quit()
                break
            case 2:
                running = True
                
                population = Population(size=1, load_file="weights_final.npy")
                leader = population.cars[0]
                obstacles = []
                frame_count = 0

                while running:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_q:
                                running = False


                    if leader.alive:
                        frame_count += 1
                        if frame_count >= SPAWN_FRAMES:
                            obstacles.append(Obstacle())
                            frame_count = 0
                        for obs in obstacles:
                            obs.update()
                        obstacles = [
                            obs for obs in obstacles if not obs.is_off_screen()
                        ]
                        obstacle_rects = [obs.rect for obs in obstacles]

                        leader.update(obstacle_rects)
                    else:
                        leader.reset()
                        pygame.time.delay(1000)

                    screen.fill(COLOR_BG)

                    for obs in obstacles:
                        obs.draw(screen)

                    leader.draw(screen, show_sensors=True)
                    pygame.draw.rect(screen, COLOR_TARGET, leader.target)

                    status = f"Score: {leader.score:.2f}"
                    screen.blit(font.render(status, True, COLOR_TEXT), (10, 10))
                    screen.blit(font.render("Pulsa la tecla Q para salir", True, COLOR_TEXT), (10, HEIGHT - 40))

                    pygame.display.flip()
                    clock.tick(FPS/2)

                pygame.quit() 
                break
            case 3:
                pygame.quit() 
                break
            case 4:
                print("Opcion no valida")
                trainning = 0


if __name__ == "__main__":
    run_simulation()
