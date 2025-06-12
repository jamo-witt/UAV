# -*- coding: utf-8 -*-
"""
Created on Sun Jun  1 21:23:07 2025

@author: jamow
"""

import cv2
import numpy as np
import glob

# Configuratie
foto_pad = "kalibratie_fotos2"
hoekpunten = (8, 5)  # Aantal INTERNE hoekpunten (witte vakjes -1)
vierkantgrootte = 1.0  # Fysieke grootte van een vierkant in eenheden naar keuze

# Voorbereid objectpunten
objp = np.zeros((hoekpunten[0] * hoekpunten[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:hoekpunten[0], 0:hoekpunten[1]].T.reshape(-1, 2)
objp *= vierkantgrootte

object_points = []  # 3D punten in de echte wereld
image_points = []   # 2D punten in beeldvlak

# Verzamel alle kalibratiefoto's
beelden = glob.glob(f"{foto_pad}/calib_*.jpg")

if not beelden:
    print("Geen kalibratiefoto's gevonden!")
    exit()

# Verwerk elke afbeelding
for i, fname in enumerate(beelden):
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    print(f"Verwerken {fname} ({i+1}/{len(beelden)})")
    
    # Zoek schaakbordhoekpunten
    ret, hoeken = cv2.findChessboardCorners(gray, hoekpunten, None)
    
    if ret:
        # Verfijn hoekpuntlocaties
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        hoeken_subpix = cv2.cornerSubPix(gray, hoeken, (11, 11), (-1, -1), criteria)
        
        object_points.append(objp)
        image_points.append(hoeken_subpix)
        
        # Teken hoekpunten voor visualisatie
        cv2.drawChessboardCorners(img, hoekpunten, hoeken_subpix, ret)
        cv2.imwrite(f"{foto_pad}/detected_{i:02d}.jpg", img)
        print(f"  ? {len(hoeken_subpix)} hoekpunten gedetecteerd")
    else:
        print(f"  ? Geen hoekpunten gevonden")

# Kalibreer camera
print("\nKalibratie gestart...")
ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
    object_points, image_points, gray.shape[::-1], None, None
)

# Sla resultaten op
np.savez("calibratie_data.npz", 
         camera_matrix=camera_matrix, 
         dist_coeffs=dist_coeffs)

print("\nKalibratie voltooid!")
print("Camera matrix:\n", camera_matrix)
print("Vervormingscoëfficiënten:\n", dist_coeffs.ravel())
print("Resultaten opgeslagen in calibratie_data.npz")