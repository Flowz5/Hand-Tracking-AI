"""
=============================================================================
📁 PROJET : HAND TRACKER & PAINTER
📅 DATE   : 12-18 Février 2026
👤 DEV    : Léo
=============================================================================

📜 LOG :
--------
[12/02 20:04] Init projet + install MediaPipe.
[12/02 21:15] Détection ok. Le pouce bugue.
[12/02 22:42] Galère sur l'inversion Gauche/Droite.
[13/02 00:15] Fix : utiliser X du petit doigt vs index pour détecter le dos de la main.
[13/02 03:20] Ajout du flip miroir.
[14/02 11:15] Création du "Canvas" (calque noir).
[14/02 12:30] Fix des pointillés : mémoriser xp, yp pour faire cv2.line().
[14/02 13:10] Fusion canvas + webcam avec bitwise operations. C'est propre.
[15/02 18:00] Push UI : 720p 60fps, Anti-Aliasing (LINE_AA), UI Bar en overlay.
[16/02 19:15] Ajout Gomme (Pouce+Index+Majeur). Centre = base du majeur.
[18/02 17:40] UX : Impossible d'écrire des mots séparés. Il faut un mode "hover".
[18/02 18:03] Ajout mode Déplacement (Pouce+Index). Crayon levé = cercle vide. Ça change tout.
=============================================================================
"""

import cv2
import numpy as np
import mediapipe as mp

def main():
    # --- CONFIG DESSIN ---
    draw_color = (0, 0, 255) # BGR: Rouge
    brush_thickness = 5      
    eraser_radius = 60       
    xp, yp = 0, 0
    img_canvas = None

    # --- CONFIG CAM ---
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 60)

    # --- CONFIG MP ---
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.85)
    mp_draw = mp.solutions.drawing_utils
    finger_tips_ids = [8, 12, 16, 20]

    while True:
        success, img = cap.read()
        if not success: break

        # Miroir pour l'UX
        img = cv2.flip(img, 1)
        h, w, c = img.shape

        # Init canvas au premier frame
        if img_canvas is None:
            img_canvas = np.zeros((h, w, 3), np.uint8)

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)
        
        # --- 1. TRACKING ---
        if results.multi_hand_landmarks:
            hand_lms = results.multi_hand_landmarks[0]
            hand_info = results.multi_handedness[0]

            lm_list = []
            for id, lm in enumerate(hand_lms.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy])

            # Détection Paume/Dos (Fix du 13/02)
            hand_label = hand_info.classification[0].label
            if hand_label == "Right":
                facing = "Palm" if lm_list[5][1] < lm_list[17][1] else "Back"
            else:
                facing = "Palm" if lm_list[5][1] > lm_list[17][1] else "Back"

            # Check état des doigts (1=levé, 0=plié)
            fingers = []
            
            # Pouce (Logique dynamique)
            thumb_tip_x, thumb_base_x = lm_list[4][1], lm_list[3][1]
            if (hand_label == "Right" and facing == "Palm") or (hand_label == "Left" and facing == "Back"):
                fingers.append(1 if thumb_tip_x < thumb_base_x else 0)
            else:
                fingers.append(1 if thumb_tip_x > thumb_base_x else 0)
                
            # Autres doigts (Axe Y)
            for id in finger_tips_ids:
                fingers.append(1 if lm_list[id][2] < lm_list[id - 2][2] else 0)

            # Positions utiles
            x1, y1 = lm_list[8][1:]         # Index tip
            x_palm, y_palm = lm_list[9][1:] # Base majeur

            # --- 2. MODES D'INTERACTION ---
            
            # Mode Dessin : Index seul [0, 1, 0, 0, 0]
            if fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
                cv2.circle(img, (x1, y1), 8, draw_color, cv2.FILLED, cv2.LINE_AA) 
                
                if xp == 0 and yp == 0:
                    xp, yp = x1, y1

                cv2.line(img_canvas, (xp, yp), (x1, y1), draw_color, brush_thickness, cv2.LINE_AA)
                xp, yp = x1, y1

            # Mode Hover : Pouce + Index [1, 1, 0, 0, 0]
            elif fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
                # Curseur creux, pas de tracé
                cv2.circle(img, (x1, y1), 8, draw_color, 2, cv2.LINE_AA) 
                xp, yp = 0, 0 # Reset point de départ

            # Mode Gomme : Pouce + Index + Majeur [1, 1, 1, 0, 0]
            elif fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
                cv2.circle(img, (x_palm, y_palm), eraser_radius, (255, 255, 255), 2, cv2.LINE_AA)
                # Efface sur le canvas avec du noir
                cv2.circle(img_canvas, (x_palm, y_palm), eraser_radius, (0, 0, 0), cv2.FILLED)
                xp, yp = 0, 0

            # Mode Repos
            else:
                xp, yp = 0, 0

        # --- 3. BLENDING ---
        # Superposition du dessin sur la vidéo via masque binaire
        img_gray = cv2.cvtColor(img_canvas, cv2.COLOR_BGR2GRAY)
        _, img_inv = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY_INV)
        img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, img_inv)
        img = cv2.bitwise_or(img, img_canvas)

        # --- 4. RENDER UI ---
        if results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, results.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)

        # Top Bar
        overlay = img.copy()
        cv2.rectangle(overlay, (0, 0), (w, 50), (20, 20, 20), cv2.FILLED)
        alpha = 0.7  
        img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
        
        cv2.putText(img, "Index: Dessiner | Pouce+Index: Deplacer | P+I+M: Gomme", 
                    (20, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

        # Affichage
        cv2.imshow("Hand Painter V1", img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()