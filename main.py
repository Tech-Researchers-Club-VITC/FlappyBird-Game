import cv2
import random
import mediapipe as mp
import pygame

# Initialize constants and variables
width, height = 640, 480
bird_x, bird_y = width // 4, height // 2
bird_velocity = 0
gravity = 0.6
gap = 250
pipes = []
score = 0
pipe_speed = 8
frame_rate = 60
warning_timer = 0
show_warning = False

# Initialize webcam capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, frame_rate)

# Initialize Mediapipe hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Initialize Pygame for audio and load all Audio files
pygame.mixer.init()
game_over_sound = pygame.mixer.Sound("music.wav")
main_menu_music = pygame.mixer.Sound("main_menu_music.wav")


# Load bird image
bird_image = cv2.imread("cartoon_bird.png")  # Replace with the path to your bird image
bird_image = cv2.resize(bird_image, (40, 40))  # Resize the bird image

# Replace the draw_bird function
def draw_bird(frame):
    # Calculate the coordinates to place the bird image centered around bird_x and bird_y
    bird_x_position = bird_x - bird_image.shape[1] // 2
    bird_y_position = int(bird_y - bird_image.shape[0] // 2)
    
    # Place the bird image on the frame
    frame[bird_y_position : bird_y_position + bird_image.shape[0], 
          bird_x_position : bird_x_position + bird_image.shape[1]] = bird_image



# Function to draw pipes on frame
def draw_pipes(frame):
    pipe_color = (0, 150, 0)  # Pipe color (green)

    for pipe in pipes:
        # Calculate the dimensions and coordinates for the top and bottom pipes
        top_pipe_rect = (pipe[0], 0, 50, pipe[1])
        bottom_pipe_rect = (pipe[0], pipe[1] + gap, 50, height - (pipe[1] + gap))

        # Draw the top and bottom pipes using rectangles
        cv2.rectangle(frame, (top_pipe_rect[0], top_pipe_rect[1]), (top_pipe_rect[0] + top_pipe_rect[2], top_pipe_rect[1] + top_pipe_rect[3]), pipe_color, -1)
        cv2.rectangle(frame, (bottom_pipe_rect[0], bottom_pipe_rect[1]), (bottom_pipe_rect[0] + bottom_pipe_rect[2], bottom_pipe_rect[1] + bottom_pipe_rect[3]), pipe_color, -1)

# Function to move pipes and update score
def move_pipes():
    global score
    for pipe in pipes:
        pipe[0] -= pipe_speed
        if pipe[0] + 50 < 0:
            pipes.remove(pipe)
            pipes.append([width, random.randint(50, height - gap - 50)])
            score += 1

def main_menu():
    video_path = "background.gif"  # Replace with the actual path to your video file
    cap = cv2.VideoCapture(video_path)
    pygame.mixer.Sound.play(main_menu_music, loops=-1)
    cv2.namedWindow("Main Menu")
    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset video to the beginning for looping
            continue
        cv2.putText(frame, "Gesture-Controlled Bird Game", (width // 4 - 20, height // 3), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
        cv2.putText(frame, "Press 's' to Start", (width // 3 + 20, height // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
        cv2.putText(frame, "Press 'q' to Quit", (width // 3 + 50, height // 2 + 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255,0), 2)
        with open("high_score.txt", "r") as file:
            high_score = int(file.read())
        cv2.putText(frame, f"High Score: {high_score}", (width // 3 + 50, height // 2 + 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        cv2.imshow("Main Menu", frame)

        key = cv2.waitKey(1)
        if key == ord('s'):
            pygame.mixer.Sound.stop(main_menu_music)
            cap.release()
            cv2.destroyWindow("Main Menu")
            break
        elif key == ord('q'):
            pygame.mixer.Sound.stop(main_menu_music)
            cap.release()
            cv2.destroyAllWindows()
            import sys
            sys.exit()

# Run the main menu
main_menu()

def pause():
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.putText(frame, "PAUSED", (width // 2-100, height // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(frame, "Press x to Resume", (width // 2-100, height // 2-40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(frame, "Press e to Exit", (width // 2-100, height // 2-80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.imshow("Gesture-Controlled Bird Movement", frame)
        if cv2.waitKey(1) & 0xFF == ord('x'):
            break
        if cv2.waitKey(1) & 0xFF == ord('e'):
            import os
            os._exit()



def game_over():
    video_path = "game_over.gif"
    cap = cv2.VideoCapture(video_path)
    pygame.mixer.Sound.play(game_over_sound)
    cv2.namedWindow("Game Over")
    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        cv2.putText(frame, "Press r to Retry...", (100,100),cv2.FONT_HERSHEY_SIMPLEX,1, (255,255,255),2)
        cv2.imshow("Game Over", frame)

        if cv2.waitKey(1) & 0xFF == ord('r'):
            pygame.mixer.Sound.stop(main_menu_music)
            cap.release()
            cv2.destroyWindow("Game Over")
            break


def draw_warning_text(frame):
    cv2.putText(frame, "Multiple fingers detected Bird confused", (width // 4 -140, height // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

def track_high_score(score):
    try:
        with open("high_score.txt", "r") as file:
            high_score = int(file.read())
            if score > high_score:
                with open("high_score.txt", "w") as file:
                    file.write(str(score))
    except FileNotFoundError:
        with open("high_score.txt", "w") as file:
            file.write(str(score))

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(frame_rgb)
    if results.multi_hand_landmarks:
        if len(results.multi_hand_landmarks) > 1:
            show_warning = True
            warning_timer = cv2.getTickCount()

        else:
            for hand_landmarks in results.multi_hand_landmarks:
                landmark_y = int(hand_landmarks.landmark[8].y * height)
                bird_y = landmark_y

    if show_warning and (cv2.getTickCount() - warning_timer) / cv2.getTickFrequency() > 3:
        show_warning = False

    if show_warning:
        draw_warning_text(frame)

    bird_velocity += gravity
    bird_y += bird_velocity*0.95

    if bird_y > height - 20:
        bird_y = height - 20
        bird_velocity = 0
    if bird_y < 0:
        bird_y = 0
        bird_velocity = 0

    if len(pipes) == 0 or pipes[-1][0] < width - 200:
        pipes.append([width, random.randint(50, height - gap - 50)])

    move_pipes()

    draw_pipes(frame)
    draw_bird(frame)

    for pipe in pipes:
        if pipe[0] < bird_x + 20 and pipe[0] + 50 > bird_x and (bird_y < pipe[1] or bird_y > pipe[1] + gap):
            pygame.mixer.Sound.play(game_over_sound)  # Play game over sound
            bird_y = height // 2
            pipes = []
            score = 0
            cv2.destroyWindow("Gesture-Controlled Bird Movement")
            game_over()

    track_high_score(score)

    with open("high_score.txt", "r") as file:
        high_score = int(file.read())
    cv2.putText(frame, f"High Score: {high_score}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.putText(frame, f"Score: {score}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX,1,(0, 0,0),2)
    cv2.putText(frame, "Press 'p' to pause", (10,90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 2)

    cv2.imshow("Gesture-Controlled Bird Movement", frame)

    if cv2.waitKey(1) & 0xFF == ord('p'):
        pause()

