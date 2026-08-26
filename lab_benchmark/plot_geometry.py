#!/usr/bin/env python3
"""
VISUALIZACIÓN — Laboratorio Benchmark 3D
==========================================
Gráfica de geometría, ejes y cargas.
"""

import matplotlib
matplotlib.use('Agg')  # Backend sin GUI
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mpl_toolkits.mplot3d import Axes3D
import json
import os

# ============================================================
# 1. PLANTA — Geometría y ejes
# ============================================================
print("Generando gráficas...")

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# --- Planta (vista superior) ---
ax1 = axes[0]
ax1.set_title('PLANTA — Geometría y Ejes', fontsize=13, fontweight='bold')
ax1.set_xlabel('X (m)')
ax1.set_ylabel('Y (m)')

# Columnas (puntos)
col_x = [0, 4, 0, 4]
col_y = [0, 0, 4, 4]
ax1.scatter(col_x, col_y, s=200, c='black', zorder=5, label='Columnas')
for i, (cx, cy) in enumerate(zip(col_x, col_y)):
    ax1.annotate(f'C{i+1}\n(0,0)', (cx, cy), textcoords="offset points",
                 xytext=(8, 8), fontsize=9)

# Vigas X
ax1.plot([0, 4], [0, 0], 'b-', linewidth=3, label='Viga X')
ax1.plot([0, 4], [4, 4], 'b-', linewidth=3)

# Vigas Y
ax1.plot([0, 0], [0, 4], 'r-', linewidth=3, label='Viga Y')
ax1.plot([4, 4], [0, 4], 'r-', linewidth=3)

# Ejes (líneas punteadas)
for x in [0, 4]:
    ax1.axvline(x=x, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
for y in [0, 4]:
    ax1.axhline(y=y, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)

# Etiquetas de ejes
ax1.text(0, -0.5, 'Eje 1', ha='center', fontsize=10, color='gray')
ax1.text(4, -0.5, 'Eje 2', ha='center', fontsize=10, color='gray')
ax1.text(-0.5, 0, 'Eje A', va='center', fontsize=10, color='gray', rotation=90)
ax1.text(-0.5, 4, 'Eje B', va='center', fontsize=10, color='gray', rotation=90)

# Dimensión
ax1.annotate('', xy=(4, -0.8), xytext=(0, -0.8),
             arrowprops=dict(arrowstyle='<->', color='green'))
ax1.text(2, -1.1, '4.0 m', ha='center', fontsize=10, color='green')
ax1.annotate('', xy=(-0.8, 4), xytext=(-0.8, 0),
             arrowprops=dict(arrowstyle='<->', color='green'))
ax1.text(-1.1, 2, '4.0 m', va='center', fontsize=10, color='green', rotation=90)

ax1.set_xlim(-1.5, 5.5)
ax1.set_ylim(-1.5, 5.5)
ax1.set_aspect('equal')
ax1.legend(loc='upper right')
ax1.grid(True, alpha=0.3)

# --- Alzado (vista lateral) ---
ax2 = axes[1]
ax2.set_title('ALZADO — Eje 1 (X-Z)', fontsize=13, fontweight='bold')
ax2.set_xlabel('X (m)')
ax2.set_ylabel('Z (m)')

# Columnas
ax2.plot([0, 0], [0, 3], 'k-', linewidth=4, label='Columna')
ax2.plot([4, 4], [0, 3], 'k-', linewidth=4)

# Viga
ax2.plot([0, 4], [3, 3], 'b-', linewidth=4, label='Viga X')

# Apoyo (triángulo)
tri = patches.RegularPolygon((0, 0), 3, radius=0.3, orientation=0,
                              facecolor='gray', edgecolor='black')
ax2.add_patch(tri)
tri2 = patches.RegularPolygon((4, 0), 3, radius=0.3, orientation=0,
                               facecolor='gray', edgecolor='black')
ax2.add_patch(tri2)

# Cota altura
ax2.annotate('', xy=(-0.5, 3), xytext=(-0.5, 0),
             arrowprops=dict(arrowstyle='<->', color='green'))
ax2.text(-0.8, 1.5, '3.0 m', va='center', fontsize=10, color='green', rotation=90)

# Cota vano
ax2.annotate('', xy=(4, -0.5), xytext=(0, -0.5),
             arrowprops=dict(arrowstyle='<->', color='green'))
ax2.text(2, -0.8, '4.0 m', ha='center', fontsize=10, color='green')

# Niveles
ax2.text(-0.3, 0, 'Nivel 0', fontsize=9, color='red')
ax2.text(-0.3, 3, 'Nivel 1', fontsize=9, color='red')

# Losa
ax2.fill_between([0, 4], 3, 3.15, alpha=0.3, color='blue', label='Losa 15 cm')

ax2.set_xlim(-1.5, 5.5)
ax2.set_ylim(-1, 4)
ax2.set_aspect('equal')
ax2.legend(loc='upper right')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('results/geometry.png', dpi=150, bbox_inches='tight')
print("  ✓ results/geometry.png")

# ============================================================
# 2. DIAGRAMA DE CARGAS
# ============================================================
fig2, ax3 = plt.subplots(1, 1, figsize=(8, 6))
ax3.set_title('CARGAS — Vista lateral (carga muerta)', fontsize=13, fontweight='bold')
ax3.set_xlabel('X (m)')
ax3.set_ylabel('Z (m)')

# Estructura
ax3.plot([0, 0], [0, 3], 'k-', linewidth=4)
ax3.plot([4, 4], [0, 3], 'k-', linewidth=4)
ax3.plot([0, 4], [3, 3], 'b-', linewidth=4)

# Apoyos
tri = patches.RegularPolygon((0, 0), 3, radius=0.2, orientation=0,
                              facecolor='gray', edgecolor='black')
ax3.add_patch(tri)
tri2 = patches.RegularPolygon((4, 0), 3, radius=0.2, orientation=0,
                               facecolor='gray', edgecolor='black')
ax3.add_patch(tri2)

# Flechas de carga (distribuida sobre la viga)
n_flechas = 8
for i in range(n_flechas + 1):
    x = i * 4.0 / n_flechas
    ax3.annotate('', xy=(x, 3), xytext=(x, 3.8),
                 arrowprops=dict(arrowstyle='->', color='red', lw=1.5))

# Etiqueta
ax3.text(2, 4.0, f'q = {25*0.15 + 1.5:.2f} kN/m² (losa + acabados)',
         ha='center', fontsize=10, color='red')

# Losa
ax3.fill_between([0, 4], 3, 3.15, alpha=0.3, color='blue', label='Losa 15 cm')

ax3.set_xlim(-1, 5)
ax3.set_ylim(-1, 5)
ax3.set_aspect('equal')
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('results/loads.png', dpi=150, bbox_inches='tight')
print("  ✓ results/loads.png")

# ============================================================
# 3. ESQUEMA DE GDL
# ============================================================
fig3, ax4 = plt.subplots(1, 1, figsize=(8, 6))
ax4.set_title('GDL POR NODO — 6 grados de libertad', fontsize=13, fontweight='bold')
ax4.set_xlim(-2, 6)
ax4.set_ylim(-2, 5)
ax4.set_aspect('equal')
ax4.grid(True, alpha=0.3)

# Nodo
ax4.plot(2, 2, 'ko', markersize=12, zorder=5)
ax4.text(2, 2.3, 'Nodo', ha='center', fontsize=11, fontweight='bold')

# Traslaciones (flechas sólidas)
ax4.annotate('', xy=(4, 2), xytext=(2, 2),
             arrowprops=dict(arrowstyle='->', color='blue', lw=2))
ax4.text(4.2, 2, 'UX (1)', fontsize=10, color='blue')

ax4.annotate('', xy=(2, 4), xytext=(2, 2),
             arrowprops=dict(arrowstyle='->', color='blue', lw=2))
ax4.text(2, 4.2, 'UY (2)', fontsize=10, color='blue', ha='center')

ax4.annotate('', xy=(3, 3.5), xytext=(2, 2),
             arrowprops=dict(arrowstyle='->', color='blue', lw=2))
ax4.text(3.2, 3.7, 'UZ (3)', fontsize=10, color='blue')

# Rotaciones (arcos)
arc_rx = patches.Arc((2, 2), 1.5, 1.5, angle=0, theta1=30, theta2=150,
                      color='red', lw=2)
ax4.add_patch(arc_rx)
ax4.text(1, 3.2, 'θX (4)', fontsize=10, color='red')

arc_ry = patches.Arc((2, 2), 1.5, 1.5, angle=0, theta1=-60, theta2=60,
                      color='red', lw=2)
ax4.add_patch(arc_ry)
ax4.text(3.2, 1.2, 'θY (5)', fontsize=10, color='red')

arc_rz = patches.Arc((2, 2), 2.0, 2.0, angle=0, theta1=200, theta2=340,
                      color='red', lw=2)
ax4.add_patch(arc_rz)
ax4.text(2, -0.2, 'θZ (6)', fontsize=10, color='red', ha='center')

# Leyenda
ax4.plot([], [], 'b-', linewidth=2, label='Traslaciones (DOF 1-3)')
ax4.plot([], [], 'r-', linewidth=2, label='Rotaciones (DOF 4-6)')
ax4.legend(loc='lower left', fontsize=10)

plt.tight_layout()
plt.savefig('results/gdl.png', dpi=150, bbox_inches='tight')
print("  ✓ results/gdl.png")

print("\n✓ Todas las gráficas generadas en results/")
