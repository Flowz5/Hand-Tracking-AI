"""
=============================================================================
📁 PROJET : HAND TRACKER v2
📅 DATE   : 12 Février 2026
👤 DEV    : Gemini / Léo
=============================================================================

📜 LOG (Nuit du 12/02/2026) :
-----------------------------
[20:04] Init projet + install MediaPipe.
[21:15] Detection ok, mais le pouce fait n'importe quoi.
[22:42] Galère sur l'inversion Gauche/Droite.
[00:15] Fix : utiliser coord X du petit doigt vs index pour détecter le dos de la main.
[03:20] Ajout du flip miroir, sinon c'est inmaniable.
[04:47] Code nettoyé. Tout marche. Dodo.
=============================================================================
"""

import cv2
import mediapipe as mp


def main():
    cap = cv2.VideoCapture(0)

    mp_hands = mp.solutions.hands
    # Confiance à 0.75 pour éviter les faux positifs (bruit de fond)
    hands = mp_hands.Hands(
        max_num_hands=2,
        min_detection_confidence=0.75,
        min_tracking_confidence=0.5
    )
    mp_draw = mp.solutions.drawing_utils

    # Index, Majeur, Annulaire, Auriculaire
    finger_tips_ids = [8, 12, 16, 20]

    while True:
        success, img = cap.read()
        if not success: break

        # Important : Miroir horizontal pour que ça soit naturel à l'écran
        img = cv2.flip(img, 1)

        # MediaPipe veut du RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        if results.multi_hand_landmarks:
            # Zip pour avoir les points + l'info Gauche/Droite en même temps
            for hand_lms, hand_info in zip(results.multi_hand_landmarks, results.multi_handedness):

                lm_list = []
                h, w, c = img.shape

                # Récup coords pixels
                for id, lm in enumerate(hand_lms.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append([id, cx, cy])

                # --- 1. Orientation ---
                hand_label = hand_info.classification[0].label  # "Left" ou "Right"

                # Détection Paume vs Dos (Palm vs Back)
                # On compare X de l'Index (5) et du Petit doigt (17)
                if hand_label == "Right":
                    # Si Index à gauche du Petit doigt = Paume
                    facing = "Palm" if lm_list[5][1] < lm_list[17][1] else "Back"
                else:
                    # Inverse pour main gauche
                    facing = "Palm" if lm_list[5][1] > lm_list[17][1] else "Back"

                # --- 2. Comptage ---
                fingers = []

                # POUCE : C'est le seul compliqué
                # La logique s'inverse selon la main ET l'orientation (dos/face)
                thumb_tip_x = lm_list[4][1]
                thumb_base_x = lm_list[3][1]

                # Droite-Paume OU Gauche-Dos : Pouce vers la gauche (<)
                if (hand_label == "Right" and facing == "Palm") or (hand_label == "Left" and facing == "Back"):
                    fingers.append(1 if thumb_tip_x < thumb_base_x else 0)
                # Autres cas : Pouce vers la droite (>)
                else:
                    fingers.append(1 if thumb_tip_x > thumb_base_x else 0)

                # 4 AUTRES DOIGTS : Simple check vertical (Y)
                # Rappel : Y=0 est en haut, donc < veut dire "plus haut"
                for id in finger_tips_ids:
                    fingers.append(1 if lm_list[id][2] < lm_list[id - 2][2] else 0)

                # --- 3. Rendu ---
                total_fingers = fingers.count(1)

                mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)

                # Info texte au poignet
                wrist_x, wrist_y = lm_list[0][1], lm_list[0][2]
                cv2.putText(img, f"{hand_label} {facing}: {total_fingers}",
                            (wrist_x, wrist_y - 10), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)

        cv2.imshow("Hand Tracker v2", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()