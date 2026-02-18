"""
=============================================================================
📁 PROJET : HAND TRACKER & PAINTER
📅 DATE   : Février 2026
👤 DEV    : Gemini / Léo
=============================================================================

📜 LOG :
--------
[18:00] Coup de propre sur l'interface. 
        - Webcam poussée en 720p 60fps.
        - Ajout de l'Anti-Aliasing (LINE_AA) pour que les traits soient lisses.
        - Pinceau affiné (épaisseur 5).
        - Ajout d'une barre de statut UI en haut. Fait moins "tuto" et plus "appli".
=============================================================================
"""

import cv2
import numpy as np
import mediapipe as mp

def main():
    # --- CONFIGURATION DESSIN ---
    draw_color = (0, 0, 255) # Rouge
    brush_thickness = 5      # Pinceau beaucoup plus fin
    xp, yp = 0, 0
    img_canvas = None

    # --- CONFIGURATION WEBCAM ---
    cap = cv2.VideoCapture(0)
    # Forcer la HD et les FPS pour la fluidité
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 60)

    # --- CONFIGURATION MEDIAPIPE ---
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.85)
    mp_draw = mp.solutions.drawing_utils
    finger_tips_ids = [8, 12, 16, 20]

    while True:
        success, img = cap.read()
        if not success: break

        # Miroir horizontal
        img = cv2.flip(img, 1)
        h, w, c = img.shape

        if img_canvas is None:
            img_canvas = np.zeros((h, w, 3), np.uint8)

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)
        
        # --- 1. LOGIQUE DE DESSIN ---
        if results.multi_hand_landmarks:
            hand_lms = results.multi_hand_landmarks[0]
            hand_info = results.multi_handedness[0]

            lm_list = []
            for id, lm in enumerate(hand_lms.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy])

            hand_label = hand_info.classification[0].label
            if hand_label == "Right":
                facing = "Palm" if lm_list[5][1] < lm_list[17][1] else "Back"
            else:
                facing = "Palm" if lm_list[5][1] > lm_list[17][1] else "Back"

            fingers = []
            thumb_tip_x, thumb_base_x = lm_list[4][1], lm_list[3][1]
            if (hand_label == "Right" and facing == "Palm") or (hand_label == "Left" and facing == "Back"):
                fingers.append(1 if thumb_tip_x < thumb_base_x else 0)
            else:
                fingers.append(1 if thumb_tip_x > thumb_base_x else 0)
                
            for id in finger_tips_ids:
                fingers.append(1 if lm_list[id][2] < lm_list[id - 2][2] else 0)

            # Bout de l'index
            x1, y1 = lm_list[8][1:] 

            # Mode Dessin : Index levé (1) et Majeur baissé (0)
            if fingers[1] == 1 and fingers[2] == 0:
                # Indicateur visuel du pinceau plus discret et lissé (LINE_AA)
                cv2.circle(img, (x1, y1), 8, draw_color, cv2.FILLED, cv2.LINE_AA) 
                
                if xp == 0 and yp == 0:
                    xp, yp = x1, y1

                # Dessin de la ligne avec cv2.LINE_AA pour la rendre "douce"
                cv2.line(img_canvas, (xp, yp), (x1, y1), draw_color, brush_thickness, cv2.LINE_AA)
                xp, yp = x1, y1
            else:
                xp, yp = 0, 0

        # --- 2. FUSION DES IMAGES ---
        img_gray = cv2.cvtColor(img_canvas, cv2.COLOR_BGR2GRAY)
        _, img_inv = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY_INV)
        img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, img_inv)
        img = cv2.bitwise_or(img, img_canvas)

        # --- 3. RENDU ESTHÉTIQUE ---
        # Affichage du squelette (par dessus le dessin)
        if results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, results.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)

        # Ajout d'une "UI Bar" élégante en haut
        # Un rectangle noir semi-transparent (astuce : on dessine sur un overlay)
        overlay = img.copy()
        cv2.rectangle(overlay, (0, 0), (w, 50), (20, 20, 20), cv2.FILLED)
        alpha = 0.7  # Transparence à 70%
        img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
        
        # Texte de l'UI bien net
        cv2.putText(img, "Hand Painter | Index: Dessiner | Quitter: Q", 
                    (20, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

        # --- 4. AFFICHAGE FINAL ---
        cv2.imshow("Hand Painter Alpha", img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()