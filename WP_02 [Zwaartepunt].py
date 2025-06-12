# -*- coding: utf-8 -*-
"""
Zwaartepunt berekening voor UAV 
"""

import matplotlib.pyplot as plt

# Afmetingen van het object
a = 414  # Hoogte
b = 304  # Breedte

# Bereken x en y lijnen van de driehoek
x = (2/3) * a + (1/6) * b
y = (2/3) * a - (1/6) * b

# Totale oppervlaktes 

Opp_A1 = b*(a-x) + 0.5*b*(x-y)
Opp_A2 = 0.5*b*y+0.25*b*(x-y)
Opp_A3 = 0.5*b*y+0.25*b*(x-y)
Opp_UAV = a*b


# --- A1 Berekening (Bovenste rechthoek + driehoek) ---
# Oppervlakken
Opp_A1_RH = b * (a - x)                   # Rechthoek
Opp_A1_DH = 0.5 * b * (x - y)             # Driehoek

# Zwaartepunten componenten
ZP_A1_RH = [0.5 * b, (a - x)/2 + x]           # Zwaartepunt Rechthoek
ZP_A1_DH = [0.5 * b, y + (2/3)*(x-y)]     # Zwaartepunt Driehoek

# Gecombineerd zwaartepunt A1
ZP_A1x = (Opp_A1_RH * ZP_A1_RH[0] + Opp_A1_DH * ZP_A1_DH[0]) / (Opp_A1_RH + Opp_A1_DH)
ZP_A1y = (Opp_A1_RH * ZP_A1_RH[1] + Opp_A1_DH * ZP_A1_DH[1]) / (Opp_A1_RH + Opp_A1_DH)
ZP_A1 = [ZP_A1x, ZP_A1y]

# --- A2 Berekening (Linker onderdeel) ---
# Oppervlakken 
Opp_A2_RH = (0.5 * b) * y                 # Rechthoek
Opp_A2_DH = 0.5 * (0.5 * b) * (x - y)     # Driehoek

# Zwaartepunten componenten
ZP_A2_RH = [0.25 * b, 0.5 * y]            # Rechthoek
ZP_A2_DH = [(1/3) * 0.5 * b, y + (1/3)*(x-y)]  # Driehoek

# Gecombineerd zwaartepunt A2
ZP_A2x = (Opp_A2_RH * ZP_A2_RH[0] + Opp_A2_DH * ZP_A2_DH[0]) / (Opp_A2_RH + Opp_A2_DH)
ZP_A2y = (Opp_A2_RH * ZP_A2_RH[1] + Opp_A2_DH * ZP_A2_DH[1]) / (Opp_A2_RH + Opp_A2_DH)
ZP_A2 = [ZP_A2x, ZP_A2y]

# --- A3 Berekening (Rechter onderdeel - gespiegelde A2) ---
# Oppervlakken (zelfde als A2)
Opp_A3_RH = Opp_A2_RH
Opp_A3_DH = Opp_A2_DH

# Zwaartepunten (gespiegeld t.o.v. A2)
ZP_A3_RH = [b - 0.25 * b, 0.5 * y]        # Rechthoek gespiegeld
ZP_A3_DH = [b - (1/3) * 0.5 * b, y + (1/3)*(x-y)]  # Driehoek gespiegeld

# Gecombineerd zwaartepunt A3
ZP_A3x = (Opp_A3_RH * ZP_A3_RH[0] + Opp_A3_DH * ZP_A3_DH[0]) / (Opp_A3_RH + Opp_A3_DH)
ZP_A3y = (Opp_A3_RH * ZP_A3_RH[1] + Opp_A3_DH * ZP_A3_DH[1]) / (Opp_A3_RH + Opp_A3_DH)
ZP_A3 = [ZP_A3x, ZP_A3y]

# Totaal zwaartepunt

ZP_UAVx = (Opp_A1 * ZP_A1[0] + Opp_A2 * ZP_A2[0] + Opp_A3 * ZP_A3[0] ) / Opp_UAV
ZP_UAVy = (Opp_A1 * ZP_A1[1] + Opp_A2 * ZP_A2[1] + Opp_A3 * ZP_A3[1] ) / Opp_UAV
ZP_UAV = [ZP_UAVx, ZP_UAVy]


# Print resultaten


print(f"A is {a}")
print(f"B is {b}")
print(f"x is {x}")
print(f"y is {y}")
print(f"Gecombineerd ZP A1: ({ZP_A1[0]:.2f}, {ZP_A1[1]:.2f})")
print(f"Gecombineerd ZP A2: ({ZP_A2[0]:.2f}, {ZP_A2[1]:.2f})")
print(f"Gecombineerd ZP A3: ({ZP_A3[0]:.2f}, {ZP_A3[1]:.2f})")
print(f"Gecombineerd ZP UAV: ({ZP_UAV[0]:.2f}, {ZP_UAV[1]:.2f})")

# Plot
fig, ax = plt.subplots(figsize=(10, 8))
ax.set_xlim(0, b)
ax.set_ylim(0, a)
ax.set_aspect('equal')
ax.grid(True)
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
ax.set_title('UAV Zwaartepunten')

# Teken de vorm
ax.plot([0, b/2, b], [x, y, x], 'k-', linewidth=2)  # Driehoekige bovenkant
ax.plot([b/2, b/2], [0, y], 'k-', linewidth=2)     # Verticale scheidingslijn

# Plot zwaartepunten
ax.plot(ZP_A1[0], ZP_A1[1], 'mo', label='ZP A1', markersize=8)
ax.plot(ZP_A2[0], ZP_A2[1], 'bo', label='ZP A2', markersize=8)
ax.plot(ZP_A3[0], ZP_A3[1], 'go', label='ZP A3', markersize=8)
ax.plot(ZP_UAV[0], ZP_UAV[1], 'rx', label='ZP UAV', markersize=20)

# Plot component zwaartepunten
ax.plot(ZP_A1_RH[0], ZP_A1_RH[1], 'mx', markersize=6)
ax.plot(ZP_A1_DH[0], ZP_A1_DH[1], 'mx', markersize=6)
ax.plot(ZP_A2_RH[0], ZP_A2_RH[1], 'bx', markersize=6)
ax.plot(ZP_A2_DH[0], ZP_A2_DH[1], 'bx', markersize=6)
ax.plot(ZP_A3_RH[0], ZP_A3_RH[1], 'gx', markersize=6)
ax.plot(ZP_A3_DH[0], ZP_A3_DH[1], 'gx', markersize=6)

ax.legend()
plt.tight_layout()
plt.show()