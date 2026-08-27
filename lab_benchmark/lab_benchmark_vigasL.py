#!/usr/bin/env python3
"""
LAB Benchmark 3D - Marco con vigas en L (losa colaborante ACI)
================================================================
CAMBIO RESPECTO AL ORIGINAL:
  Las 4 vigas ya NO son rectangulares 25x50. Ahora son secciones L
  que representan la LOSA COLABORANTE segun ACI (ancho de ala = luz/4).
  El ala de losa va ARRIBA, lo que sube el centroide y aumenta la
  rigidez vertical (flexion por gravedad) x1.78 respecto a la viga sola.

  Las COLUMNAS L 30x30 se mantienen intactas (Iy=Iz iguales).

SECCION L DE VIGA (calculada geometricamente, no inventada):
  Alma:  25 x 35 cm (parte que sobresale bajo la losa)
  Ala:   100 x 15 cm (losa colaborante ACI = luz/4 = 4.0/4 = 1.0 m)
  A     = 0.237500 m2
  I_grav= 4.62843e-3 m4  (flexion vertical, centroide corrido)
  I_lat = 2.07271e-2 m4  (flexion lateral, ala ancha)
  J     = 2.03909e-3 m4

ORIENTACION (lo critico):
  - Vigas en X: el ala corre a lo largo de X. El plano de gravedad
    usa I_grav. Se orienta con vecxz adecuado.
  - Vigas en Y: idem, ala a lo largo de Y.
  En ambas, la inercia de gravedad (I_grav) queda en el plano vertical.

Unidades: m, kN, kPa
"""

import openseespy.opensees as ops
import json
import math
import os

# ============================================================
# 1. DATOS GEOMETRICOS
# ============================================================
X = [0.0, 4.0]
Y = [0.0, 4.0]
Z = [0.0, 3.0]
nX, nY, nNivel = len(X), len(Y), len(Z)
nNodosPorPiso = nX * nY

# ============================================================
# 2. MATERIAL Y SECCIONES
# ============================================================
fpc   = 25.0                              # G-25 -> f'c = 25 MPa
Ec    = 4700.0 * math.sqrt(fpc) * 1000.0  # kPa
Gc    = Ec / (2.0 * (1.0 + 0.2))
gamma = 25.0

# --- Columna L 30x30, espesor 15 (SIN CAMBIOS) ---
col_leg, col_t = 0.30, 0.15
A_col  = col_leg**2 - (col_leg - col_t)**2   # 0.0675
Iy_col = 4.6375e-5
Iz_col = 4.6375e-5
J_col  = 1.39125e-5

# --- VIGA EN L: losa colaborante ACI (ala = luz/4) ---
# Geometria de la L
alma_b   = 0.25          # ancho alma
peralte  = 0.50          # peralte total (incluye espesor losa)
t_losa   = 0.15          # espesor losa = espesor del ala
luz      = 4.0
b_ala    = luz / 4.0     # ACI: ancho colaborante = 1.0 m
h_alma   = peralte - t_losa   # 0.35 m (alma bajo la losa)

# Propiedades compuestas (calculadas por composicion de rectangulos)
A_vig  = 0.237500        # m2
Iy_vig = 2.07271107e-02  # inercia LATERAL (ala ancha) -> eje debil-vertical local
Iz_vig = 4.62842654e-03  # inercia de GRAVEDAD (centroide corrido) -> flexion vertical
J_vig  = 2.03909066e-03  # torsion (suma St. Venant)
# NOTA: Iz_vig es la que gobierna la deflexion por peso. Es 1.78x la viga sola.

t_losa_carga = 0.15      # para cargas de losa

# ============================================================
# 3. CARGAS
# ============================================================
q_losa = gamma * t_losa_carga + 1.5   # 5.25 kN/m2
q_viva = 2.0

# ============================================================
# 4. FUNCIONES
# ============================================================

def construir_modelo():
    """Construye el modelo 3D. Vigas en L con orientacion correcta."""
    ops.wipe()
    ops.model('basic', '-ndm', 3, '-ndf', 6)
    ops.uniaxialMaterial('Elastic', 1, Ec)

    # --- TRANSFORMACIONES GEOMETRICAS ---
    # geomTransf('Linear', tag, vecxz_x, vecxz_y, vecxz_z)
    # El vector vecxz define el plano local x-z; junto con el eje del
    # elemento fija que direccion es el eje local y (perpendicular).
    #
    # Columnas (eje elemento vertical, +Z global):
    ops.geomTransf('Linear', 1, 1, 0, 0)
    #
    # Vigas en X (eje elemento +X global):
    #   Queremos que la inercia de gravedad (Iz_vig) flexione en plano vertical.
    #   Con vecxz = (0,0,1): eje local z queda vertical, eje local y horizontal.
    #   En elasticBeamColumn, Iz flexiona en plano local x-y (horizontal aqui)
    #   e Iy en plano local x-z (vertical aqui).
    #   Por eso para vigas asignaremos las inercias en el ORDEN correcto abajo.
    ops.geomTransf('Linear', 2, 0, 0, 1)
    #
    # Vigas en Y (eje elemento +Y global):
    ops.geomTransf('Linear', 3, 0, 0, 1)

    # --- NODOS ---
    coords = {}
    nid = 1
    for iz in range(nNivel):
        for ix in range(nX):
            for iy in range(nY):
                coords[nid] = (X[ix], Y[iy], Z[iz])
                ops.node(nid, X[ix], Y[iy], Z[iz])
                nid += 1

    # --- APOYOS EMPOTRADOS EN BASE ---
    for i in range(1, nNodosPorPiso + 1):
        ops.fix(i, 1, 1, 1, 1, 1, 1)

    # --- ELEMENTOS ---
    tag = 1
    columnas, vigas_x, vigas_y = [], [], []

    # COLUMNAS (L 30x30, Iy=Iz)
    for ix in range(nX):
        for iy in range(nY):
            n1 = 1 + ix * nY + iy
            n2 = 1 + nNodosPorPiso + ix * nY + iy
            ops.element('elasticBeamColumn', tag, n1, n2,
                        A_col, Ec, Gc, J_col, Iy_col, Iz_col, 1)
            columnas.append(tag)
            tag += 1

    # VIGAS EN X (seccion L, ala a lo largo de X)
    # Con geomTransf 2 (vecxz=0,0,1): plano local x-z es VERTICAL.
    # => la inercia que flexiona por gravedad es Iy (plano x-z).
    # Por eso pasamos Iy = Iz_vig (gravedad) e Iz = Iy_vig (lateral).
    for iy in range(nY):
        n1 = 1 + nNodosPorPiso + 0 * nY + iy
        n2 = 1 + nNodosPorPiso + 1 * nY + iy
        ops.element('elasticBeamColumn', tag, n1, n2,
                    A_vig, Ec, Gc, J_vig,
                    Iz_vig,   # <- Iy_local = inercia de GRAVEDAD
                    Iy_vig,   # <- Iz_local = inercia lateral
                    2)
        vigas_x.append(tag)
        tag += 1

    # VIGAS EN Y (seccion L, ala a lo largo de Y)
    for ix in range(nX):
        n1 = 1 + nNodosPorPiso + ix * nY + 0
        n2 = 1 + nNodosPorPiso + ix * nY + 1
        ops.element('elasticBeamColumn', tag, n1, n2,
                    A_vig, Ec, Gc, J_vig,
                    Iz_vig,   # <- Iy_local = inercia de GRAVEDAD
                    Iy_vig,   # <- Iz_local = inercia lateral
                    3)
        vigas_y.append(tag)
        tag += 1

    return coords, columnas, vigas_x, vigas_y


def aplicar_carga_gravedad(q, incluir_peso_vigas=False):
    """Carga de losa por areas tributarias (losa cuadrada -> triangulos)."""
    Lx = X[1] - X[0]
    Ly = Y[1] - Y[0]

    F_corner = q * Lx * Ly / 8.0

    # Vigas X
    for iy in range(nY):
        n1 = 1 + nNodosPorPiso + 0 * nY + iy
        n2 = 1 + nNodosPorPiso + 1 * nY + iy
        ops.load(n1, 0.0, 0.0, -F_corner, 0.0, 0.0, 0.0)
        ops.load(n2, 0.0, 0.0, -F_corner, 0.0, 0.0, 0.0)

    # Vigas Y
    for ix in range(nX):
        n1 = 1 + nNodosPorPiso + ix * nY + 0
        n2 = 1 + nNodosPorPiso + ix * nY + 1
        ops.load(n1, 0.0, 0.0, -F_corner, 0.0, 0.0, 0.0)
        ops.load(n2, 0.0, 0.0, -F_corner, 0.0, 0.0, 0.0)

    # Peso propio de vigas L (usa area real de la seccion L)
    if incluir_peso_vigas:
        w_viga = gamma * A_vig   # kN/m con el area L completa
        for iy in range(nY):
            F = w_viga * Lx / 2.0
            n1 = 1 + nNodosPorPiso + 0 * nY + iy
            n2 = 1 + nNodosPorPiso + 1 * nY + iy
            ops.load(n1, 0.0, 0.0, -F, 0.0, 0.0, 0.0)
            ops.load(n2, 0.0, 0.0, -F, 0.0, 0.0, 0.0)
        for ix in range(nX):
            F = w_viga * Ly / 2.0
            n1 = 1 + nNodosPorPiso + ix * nY + 0
            n2 = 1 + nNodosPorPiso + ix * nY + 1
            ops.load(n1, 0.0, 0.0, -F, 0.0, 0.0, 0.0)
            ops.load(n2, 0.0, 0.0, -F, 0.0, 0.0, 0.0)


def resolver():
    ops.system('BandSPD')
    ops.numberer('RCM')
    ops.constraints('Plain')
    ops.integrator('LoadControl', 1.0)
    ops.algorithm('Linear')
    ops.analysis('Static')
    ok = ops.analyze(1)
    ops.reactions()
    return ok


def extraer_resultados(coords):
    disp = {nid: [ops.nodeDisp(nid, i) for i in range(1, 7)] for nid in coords}
    reac = {nid: [ops.nodeReaction(nid, i) for i in range(1, 7)]
            for nid in range(1, nNodosPorPiso + 1)}
    return disp, reac


# ============================================================
# 5. EJECUCION
# ============================================================
print("=" * 60)
print("  LAB BENCHMARK 3D - VIGAS EN L (losa colaborante ACI)")
print("=" * 60)

print("\n[1] Construyendo modelo...")
coords, cols, vx, vy = construir_modelo()
nodos_piso1 = list(range(nNodosPorPiso + 1, 2 * nNodosPorPiso + 1))
print(f"    Nodos:    {len(coords)}")
print(f"    Columnas: {len(cols)} (L 30x30)")
print(f"    Vigas X:  {len(vx)} (L losa colaborante)")
print(f"    Vigas Y:  {len(vy)} (L losa colaborante)")

print("\n    SECCION L DE VIGA:")
print(f"      A      = {A_vig:.6f} m2")
print(f"      I_grav = {Iz_vig:.6e} m4  (flexion vertical, +78% vs viga sola)")
print(f"      I_lat  = {Iy_vig:.6e} m4  (flexion lateral)")
print(f"      J      = {J_vig:.6e} m4")

# CASO G
print("\n[2] Carga muerta (G)...")
construir_modelo()
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)
aplicar_carga_gravedad(q_losa, incluir_peso_vigas=True)
ok_G = resolver()
disp_G, reac_G = extraer_resultados(coords)
fuerzas_G = {etag: [round(f, 4) for f in ops.eleForce(etag)]
             for etag in cols + vx + vy}
print(f"    Convergencia: {'OK' if ok_G == 0 else 'FALLO'}")

# CASO Q
print("\n[3] Carga viva (Q)...")
construir_modelo()
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)
aplicar_carga_gravedad(q_viva)
ok_Q = resolver()
disp_Q, reac_Q = extraer_resultados(coords)
print(f"    Convergencia: {'OK' if ok_Q == 0 else 'FALLO'}")

# CASO EX
print("\n[4] Carga lateral EX...")
construir_modelo()
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)
F_sismo = 50.0
for nid in nodos_piso1:
    ops.load(nid, F_sismo, 0.0, 0.0, 0.0, 0.0, 0.0)
ok_EX = resolver()
disp_EX, reac_EX = extraer_resultados(coords)
print(f"    Convergencia: {'OK' if ok_EX == 0 else 'FALLO'}")

# ============================================================
# 6. EQUILIBRIO
# ============================================================
print("\n" + "=" * 60)
print("  VERIFICACION DE EQUILIBRIO")
print("=" * 60)

Lx, Ly = X[1] - X[0], Y[1] - Y[0]
area_losa = Lx * Ly

peso_losa     = gamma * t_losa_carga * area_losa
peso_acabados = 1.5 * area_losa
peso_vigas    = 4 * gamma * A_vig * Lx   # ahora con area L (mas pesada)
carga_G_total = peso_losa + peso_acabados + peso_vigas
carga_Q_total = q_viva * area_losa

sum_Rz_G = sum(reac_G[n][2] for n in reac_G)
sum_Rz_Q = sum(reac_Q[n][2] for n in reac_Q)

print(f"\n  Carga muerta (G):")
print(f"    Peso losa:        {peso_losa:>10.2f} kN")
print(f"    Peso acabados:    {peso_acabados:>10.2f} kN")
print(f"    Peso vigas L:     {peso_vigas:>10.2f} kN")
print(f"    TOTAL aplicado:   {carga_G_total:>10.2f} kN")
print(f"    SUM reacciones:   {sum_Rz_G:>10.2f} kN")
print(f"    Error:            {abs(carga_G_total - sum_Rz_G):>10.6f} kN")

print(f"\n  Carga viva (Q):")
print(f"    TOTAL aplicado:   {carga_Q_total:>10.2f} kN")
print(f"    SUM reacciones:   {sum_Rz_Q:>10.2f} kN")
print(f"    Error:            {abs(carga_Q_total - sum_Rz_Q):>10.6f} kN")

# ============================================================
# 7. DESPLAZAMIENTOS
# ============================================================
print("\n" + "=" * 60)
print("  DESPLAZAMIENTOS NODO TECHO")
print("=" * 60)
print(f"  {'Nodo':<6}{'X':<6}{'Y':<6}{'UZ_G(mm)':<12}{'UZ_Q(mm)':<12}{'UX_EX(mm)':<12}")
for nid in nodos_piso1:
    cx, cy, cz = coords[nid]
    print(f"  {nid:<6}{cx:<6.1f}{cy:<6.1f}"
          f"{disp_G[nid][2]*1000:<12.4f}{disp_Q[nid][2]*1000:<12.4f}"
          f"{disp_EX[nid][0]*1000:<12.4f}")

# ============================================================
# 8. GUARDAR JSON
# ============================================================
os.makedirs('results', exist_ok=True)
resultados = {
    'model_info': {
        'description': 'Marco 3D: 4 columnas L + 4 vigas L (losa colaborante ACI luz/4)',
        'viga_L': {
            'ala_ancho_m': b_ala, 'ala_espesor_m': t_losa,
            'alma_b_m': alma_b, 'alma_h_neta_m': h_alma,
            'A_m2': A_vig, 'I_gravedad_m4': Iz_vig,
            'I_lateral_m4': Iy_vig, 'J_m4': J_vig,
            'criterio_ala': 'ACI luz/4 = 1.0 m',
        },
        'material': {'fpc_MPa': fpc, 'Ec_kPa': round(Ec, 0), 'gamma': gamma},
        'units': 'm, kN, kPa',
    },
    'nodes': {str(k): list(v) for k, v in coords.items()},
    'elements': {'columns': cols, 'beams_x': vx, 'beams_y': vy},
    'load_cases': {
        'G': {'applied_kN': round(carga_G_total, 2),
              'reaction_kN': round(sum_Rz_G, 2),
              'error_kN': round(abs(carga_G_total - sum_Rz_G), 6),
              'displacements': {str(k): [round(v[i], 8) for i in range(3)]
                                for k, v in disp_G.items()},
              'reactions': {str(k): [round(v[i], 4) for i in range(3)]
                            for k, v in reac_G.items()}},
        'Q': {'applied_kN': round(carga_Q_total, 2),
              'reaction_kN': round(sum_Rz_Q, 2),
              'error_kN': round(abs(carga_Q_total - sum_Rz_Q), 6),
              'displacements': {str(k): [round(v[i], 8) for i in range(3)]
                                for k, v in disp_Q.items()},
              'reactions': {str(k): [round(v[i], 4) for i in range(3)]
                            for k, v in reac_Q.items()}},
        'EX': {'applied_kN': F_sismo * 4,
               'displacements': {str(k): [round(v[i], 8) for i in range(3)]
                                 for k, v in disp_EX.items()},
               'reactions': {str(k): [round(v[i], 4) for i in range(3)]
                             for k, v in reac_EX.items()}},
    },
}
with open('results/lab_results_vigasL.json', 'w') as f:
    json.dump(resultados, f, indent=2)

print(f"\nResultados guardados en results/lab_results_vigasL.json")
print("=" * 60)
print("  FIN")
print("=" * 60)
