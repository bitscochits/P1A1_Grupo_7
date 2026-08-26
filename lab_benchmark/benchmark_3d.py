#!/usr/bin/env python3
"""
LAB Benchmark 3D - Marco estructural simple
============================================
4 columnas, 4 vigas (2 por direccion), losa con descarga tributaria.

Geometria:
  Planta: 4.0 m x 4.0 m
  Altura: 3.0 m (1 piso)

Secciones:
  Columnas: 30 x 30 cm
  Vigas:    25 x 50 cm
  Losa:     15 cm

Material:
  Hormigon f'c = 21 MPa  ->  Ec = 4700*sqrt(21) = 21551 MPa

Unidades: m, kN, kPa
"""

import openseespy.opensees as ops
import json
import math
import os

# ============================================================
# 1. DATOS GEOMETRICOS
# ============================================================
X = [0.0, 4.0]   # 2 ejes en X -> 1 vano
Y = [0.0, 4.0]   # 2 ejes en Y -> 1 vano
Z = [0.0, 3.0]   # Niveles: base (0) y techo (3)

nX, nY = len(X), len(Y)
nNivel = len(Z)
nNodosPorPiso = nX * nY  # 4

# ============================================================
# 2. MATERIAL Y SECCIONES
# ============================================================
fpc = 21.0                              # MPa
Ec  = 4700.0 * math.sqrt(fpc) * 1000   # MPa -> kPa
Gc  = Ec / (2.0 * (1.0 + 0.2))         # kPa
gamma = 25.0                            # kN/m3

# Columnas 30x30 cm
col_b, col_h = 0.30, 0.30
A_col  = col_b * col_h
Iy_col = col_b * col_h**3 / 12.0
Iz_col = col_h * col_b**3 / 12.0
J_col  = min(Iy_col, Iz_col) * 0.3

# Vigas 25x50 cm
v_b, v_h = 0.25, 0.50
A_vig  = v_b * v_h
Iy_vig = v_b * v_h**3 / 12.0
Iz_vig = v_h * v_b**3 / 12.0
J_vig  = min(Iy_vig, Iz_vig) * 0.3

# Losa 15 cm
t_losa = 0.15

# ============================================================
# 3. CARGAS
# ============================================================
q_losa = gamma * t_losa + 1.5   # 5.25 kN/m2 (peso propio + acabados)
q_viva = 2.0                    # kN/m2

# ============================================================
# 4. FUNCIONES
# ============================================================
def construir_modelo():
    """Construye el modelo 3D completo. Retorna coords y tags de elementos."""
    ops.wipe()
    ops.model('basic', '-ndm', 3, '-ndf', 6)

    # Material
    ops.uniaxialMaterial('Elastic', 1, Ec)

    # Transformaciones geometricas
    # Columnas: eje local x vertical (+Z global), vecyz en +X
    ops.geomTransf('Linear', 1, 1, 0, 0)
    # Vigas X: eje local x en +X, vecyz en +Z
    ops.geomTransf('Linear', 2, 0, 0, 1)
    # Vigas Y: eje local x en +Y, vecyz en +Z
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

    # --- APOYOS FIJOS en base ---
    for i in range(1, nNodosPorPiso + 1):
        ops.fix(i, 1, 1, 1, 1, 1, 1)

    # --- ELEMENTOS ---
    tag = 1
    columnas = []
    vigas_x  = []
    vigas_y  = []

    # Columnas (nivel 0 -> nivel 1)
    for ix in range(nX):
        for iy in range(nY):
            n1 = 1 + ix * nY + iy
            n2 = 1 + nNodosPorPiso + ix * nY + iy
            ops.element('elasticBeamColumn', tag, n1, n2,
                        A_col, Ec, Gc, J_col, Iy_col, Iz_col, 1)
            columnas.append(tag)
            tag += 1

    # Vigas en X
    for iy in range(nY):
        n1 = 1 + nNodosPorPiso + 0 * nY + iy
        n2 = 1 + nNodosPorPiso + 1 * nY + iy
        ops.element('elasticBeamColumn', tag, n1, n2,
                    A_vig, Ec, Gc, J_vig, Iy_vig, Iz_vig, 2)
        vigas_x.append(tag)
        tag += 1

    # Vigas en Y
    for ix in range(nX):
        n1 = 1 + nNodosPorPiso + ix * nY + 0
        n2 = 1 + nNodosPorPiso + ix * nY + 1
        ops.element('elasticBeamColumn', tag, n1, n2,
                    A_vig, Ec, Gc, J_vig, Iy_vig, Iz_vig, 3)
        vigas_y.append(tag)
        tag += 1

    return coords, columnas, vigas_x, vigas_y


def aplicar_carga_gravedad(q, incluir_peso_vigas=False):
    """Descarga losa sobre vigas por areas tributarias.
    
    La carga de losa se aplica UNA SOLA VEZ por nodo (via vigas X).
    Cada nodo es compartido por 1 viga X y 1 viga Y, pero el area 
    tributaria de la losa es la misma, no se duplica.
    
    Si incluir_peso_vigas=True, tambien agrega el peso propio de las vigas.
    """
    Lx = X[1] - X[0]
    Ly = Y[1] - Y[0]

    # --- Carga de losa sobre vigas X (tributario: Ly/2) ---
    for iy in range(nY):
        trib_w = q * Ly / 2.0
        F = trib_w * Lx / 2.0
        n1 = 1 + nNodosPorPiso + 0 * nY + iy
        n2 = 1 + nNodosPorPiso + 1 * nY + iy
        ops.load(n1, 0.0, 0.0, -F, 0.0, 0.0, 0.0)
        ops.load(n2, 0.0, 0.0, -F, 0.0, 0.0, 0.0)

    # --- Peso propio de solo si se solicita ---
    if incluir_peso_vigas:
        w_viga = gamma * A_vig  # kN/m

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
    """Configura analisis estatico y resuelve."""
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
    """Extrae desplazamientos, reacciones y fuerzas de elementos."""
    disp = {}
    for nid in coords:
        disp[nid] = [ops.nodeDisp(nid, i) for i in range(1, 7)]

    reac = {}
    for nid in range(1, nNodosPorPiso + 1):
        reac[nid] = [ops.nodeReaction(nid, i) for i in range(1, 7)]

    return disp, reac


# ============================================================
# 5. EJECUCION
# ============================================================
print("=" * 60)
print("  LAB BENCHMARK 3D - Marco simple 4x4 m, 1 piso")
print("=" * 60)

# --- CASO G: Carga muerta ---
print("\n[1] Construyendo modelo...")
coords, cols, vx, vy = construir_modelo()
nodos_piso1 = list(range(nNodosPorPiso + 1, 2 * nNodosPorPiso + 1))

print(f"    Nodos:    {len(coords)}")
print(f"    Columnas: {len(cols)}")
print(f"    Vigas X:  {len(vx)}")
print(f"    Vigas Y:  {len(vy)}")
print(f"    Total:    {len(cols) + len(vx) + len(vy)} elementos")

print("\n[2] Aplicando carga muerta (G)...")
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)
aplicar_carga_gravedad(q_losa, incluir_peso_vigas=True)
ok_G = resolver()
disp_G, reac_G = extraer_resultados(coords)
fuerzas_G = {}
for etag in cols + vx + vy:
    fuerzas_G[etag] = [round(f, 4) for f in ops.eleForce(etag)]
print(f"    Convergencia: {'OK' if ok_G == 0 else 'FALLO'}")

# --- CASO Q: Carga viva ---
print("\n[3] Aplicando carga viva (Q)...")
construir_modelo()
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)
aplicar_carga_gravedad(q_viva)
ok_Q = resolver()
disp_Q, reac_Q = extraer_resultados(coords)
print(f"    Convergencia: {'OK' if ok_Q == 0 else 'FALLO'}")

# --- CASO EX: Sismo en X ---
print("\n[4] Aplicando carga lateral EX...")
construir_modelo()
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)
F_sismo = 50.0  # kN
for nid in nodos_piso1:
    ops.load(nid, F_sismo, 0.0, 0.0, 0.0, 0.0, 0.0)
ok_EX = resolver()
disp_EX, reac_EX = extraer_resultados(coords)
print(f"    Convergencia: {'OK' if ok_EX == 0 else 'FALLO'}")

# ============================================================
# 6. VERIFICACION
# ============================================================
print("\n" + "=" * 60)
print("  VERIFICACION DE EQUILIBRIO")
print("=" * 60)

Lx = X[1] - X[0]
Ly = Y[1] - Y[0]
area_losa = Lx * Ly

peso_losa     = gamma * t_losa * area_losa
peso_acabados = 1.5 * area_losa
peso_vigas    = 4 * gamma * A_vig * Lx
carga_G_total = peso_losa + peso_acabados + peso_vigas
carga_Q_total = q_viva * area_losa

sum_Rz_G = sum(reac_G[n][2] for n in reac_G)
sum_Rz_Q = sum(reac_Q[n][2] for n in reac_Q)

print(f"\n  Carga muerta (G):")
print(f"    Peso losa:        {peso_losa:>10.2f} kN")
print(f"    Peso acabados:    {peso_acabados:>10.2f} kN")
print(f"    Peso vigas:       {peso_vigas:>10.2f} kN")
print(f"    TOTAL aplicado:   {carga_G_total:>10.2f} kN (hacia abajo)")
print(f"    SUM reacciones:   {sum_Rz_G:>10.2f} kN (hacia arriba)")
error_G = abs(carga_G_total - sum_Rz_G)
print(f"    Error equilibrio: {error_G:>10.6f} kN")

print(f"\n  Carga viva (Q):")
print(f"    TOTAL aplicado:   {carga_Q_total:>10.2f} kN (hacia abajo)")
print(f"    SUM reacciones:   {sum_Rz_Q:>10.2f} kN (hacia arriba)")
error_Q = abs(carga_Q_total - sum_Rz_Q)
print(f"    Error equilibrio: {error_Q:>10.6f} kN")

# --- Desplazamientos ---
print("\n" + "=" * 60)
print("  DESPLAZAMIENTOS NODO TECHO")
print("=" * 60)
print(f"  {'Nodo':<6} {'X(m)':<8} {'Y(m)':<8} {'UZ_G(mm)':<12} {'UZ_Q(mm)':<12} {'UX_EX(mm)':<12}")
for nid in nodos_piso1:
    cx, cy, cz = coords[nid]
    uz_g  = disp_G[nid][2] * 1000
    uz_q  = disp_Q[nid][2] * 1000
    ux_ex = disp_EX[nid][0] * 1000
    print(f"  {nid:<6} {cx:<8.1f} {cy:<8.1f} {uz_g:<12.4f} {uz_q:<12.4f} {ux_ex:<12.4f}")

# --- Fuerzas internas ---
print("\n" + "=" * 60)
print("  FUERZAS INTERNAS (Caso G)")
print("=" * 60)
print(f"  {'Elem':<6} {'Tipo':<10} {'P_i(kN)':<12} {'V2_i(kN)':<12} {'V3_i(kN)':<12} {'M2_i':<12}")
for etag in cols + vx + vy:
    f = fuerzas_G[etag]
    tipo = "Col" if etag in cols else ("VigX" if etag in vx else "VigY")
    print(f"  {etag:<6} {tipo:<10} {f[0]:<12.4f} {f[1]:<12.4f} {f[2]:<12.4f} {f[4]:<12.4f}")

# ============================================================
# 7. GUARDAR RESULTADOS
# ============================================================
os.makedirs('results', exist_ok=True)

resultados = {
    'model_info': {
        'description': 'Marco 3D simple: 4 columnas, 4 vigas, losa',
        'geometry': {
            'plan_x_m': Lx,
            'plan_y_m': Ly,
            'height_m': Z[1] - Z[0],
            'n_columns': len(cols),
            'n_beams_x': len(vx),
            'n_beams_y': len(vy),
        },
        'sections': {
            'column': f'{col_b*100:.0f}x{col_h*100:.0f} cm',
            'beam': f'{v_b*100:.0f}x{v_h*100:.0f} cm',
            'slab': f'{t_losa*100:.0f} cm',
        },
        'material': {
            'fpc_MPa': fpc,
            'Ec_kPa': round(Ec, 0),
            'gamma_kN_m3': gamma,
        },
        'loads': {
            'q_dead_kN_m2': q_losa,
            'q_live_kN_m2': q_viva,
        },
        'units': 'm, kN, kPa',
    },
    'nodes': {str(k): list(v) for k, v in coords.items()},
    'elements': {
        'columns': cols,
        'beams_x': vx,
        'beams_y': vy,
    },
    'load_cases': {
        'G': {
            'applied_kN': round(carga_G_total, 2),
            'reaction_kN': round(sum_Rz_G, 2),
            'error_kN': round(abs(carga_G_total - sum_Rz_G), 6),
            'displacements': {str(k): [round(v[i], 8) for i in range(3)] for k, v in disp_G.items()},
            'reactions': {str(k): [round(v[i], 4) for i in range(3)] for k, v in reac_G.items()},
        },
        'Q': {
            'applied_kN': round(carga_Q_total, 2),
            'reaction_kN': round(sum_Rz_Q, 2),
            'error_kN': round(abs(carga_Q_total - sum_Rz_Q), 6),
            'displacements': {str(k): [round(v[i], 8) for i in range(3)] for k, v in disp_Q.items()},
            'reactions': {str(k): [round(v[i], 4) for i in range(3)] for k, v in reac_Q.items()},
        },
        'EX': {
            'applied_kN': F_sismo * 4,
            'displacements': {str(k): [round(v[i], 8) for i in range(3)] for k, v in disp_EX.items()},
            'reactions': {str(k): [round(v[i], 4) for i in range(3)] for k, v in reac_EX.items()},
        },
    },
}

with open('results/lab_results.json', 'w') as f:
    json.dump(resultados, f, indent=2)

print(f"\nResultados guardados en results/lab_results.json")
print("\n" + "=" * 60)
print("  FIN DEL LABORATORIO")
print("=" * 60)
