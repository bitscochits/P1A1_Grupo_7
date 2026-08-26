#!/usr/bin/env python3
# shebang: le dice al sistema operativo que use Python para ejecutar este archivo

"""
LAB Benchmark 3D - Marco estructural con columnas tipo L
========================================================
Descripcion general:
  Este script construye un modelo estructural 3D en OpenSeesPy.
 Representa un marco de un piso con 4 columnas tipo L, 4 vigas
  y una losa que descarga sobre las vigas por areas tributarias.

Geometria:
  Planta: 4.0 m x 4.0 m (un vano en cada direccion)
  Altura: 3.0 m (un solo piso)

Secciones:
  Columnas: tipo L 30x30 cm (espesor 15 cm)
  Vigas:    25 x 50 cm
  Losa:     15 cm

Material:
  Hormigon f'c = 21 MPa  ->  Ec = 4700*sqrt(21) = 21551 MPa

Unidades: metros (m), kilonewtons (kN), kilopascales (kPa)
"""

# ============================================================
# IMPORTACIONES
# ============================================================
import openseespy.opensees as ops  # libreria de analisis estructural OpenSees
import json                         # para guardar resultados en formato JSON
import math                         # para operaciones matematicas (sqrt)
import os                           # para crear carpetas (makedirs)

# ============================================================
# 1. DATOS GEOMETRICOS
# ============================================================
# Coordenadas de los ejes de la estructura en cada direccion
X = [0.0, 4.0]   # dos ejes en X: Eje1 en x=0, Eje2 en x=4  -> 1 vano de 4m
Y = [0.0, 4.0]   # dos ejes en Y: EjeA en y=0, EjeB en y=4  -> 1 vano de 4m
Z = [0.0, 3.0]   # niveles: base en z=0, techo en z=3        -> altura de 3m

# Cantidad de ejes en cada direccion
nX = len(X)           # 2 ejes en X
nY = len(Y)           # 2 ejes en Y
nNivel = len(Z)       # 2 niveles (base + techo)

# Total de nodos por piso = ejesX * ejesY = 2 * 2 = 4 nodos
nNodosPorPiso = nX * nY  # = 4

# ============================================================
# 2. MATERIAL Y SECCIONES
# ============================================================

# --- Material: Hormigon f'c = 21 MPa ---
fpc = 21.0                              # resistencia a compresion del hormigon (MPa)
Ec  = 4700.0 * math.sqrt(fpc) * 1000   # modulo de elasticidad segun ACI: 4700*sqrt(f'c)
                                        # se multiplica por 1000 para convertir MPa a kPa
Gc  = Ec / (2.0 * (1.0 + 0.2))         # modulo de corte: G = E / (2*(1+nu))
                                        # asumimos nu = 0.2 (coeficiente de Poisson)
gamma = 25.0                            # peso unitario del hormigon armado (kN/m3)

# --- Columna tipo L 30x30 cm, espesor 15 cm ---
# La seccion L se forma recortando un cuadrado 15x15 de una esquina de un cuadrado 30x30
#
#   +--------+  30 cm
#   |   15x15|
#   |   +----+  15 cm
#   |   |
#   +---+  15 cm   15 cm
#
# Propiedades calculadas de esta seccion:
col_leg = 0.30     # longitud exterior del brazo L (m)
col_t   = 0.15     # espesor del brazo L (m)

# Area de la seccion L: area total menos el recorte
# A = 30*30 - 15*15 = 900 - 225 = 675 cm2 = 0.0675 m2
A_col  = col_leg**2 - (col_leg - col_t)**2  # = 0.0675 m2

# Momentos de inercia (iguales por simetria de la L)
Iy_col = 4.6375e-5   # momento de inercia respecto al eje Y local (m4)
Iz_col = 4.6375e-5   # momento de inercia respecto al eje Z local (m4)

# Momento torsional: se aproxima como 30% del menor I (regla practica)
J_col  = 1.39125e-5  # constante de torsion (m4)

# --- Viga 25x50 cm ---
v_b = 0.25  # ancho de la viga (m) - eje local z
v_h = 0.50  # altura de la viga (m) - eje local y

A_vig  = v_b * v_h           # area de la seccion = 0.25 * 0.50 = 0.125 m2
Iy_vig = v_b * v_h**3 / 12.0 # inercia fuerte: b*h^3/12 (flexion en el plano fuerte)
Iz_vig = v_h * v_b**3 / 12.0 # inercia debil: h*b^3/12 (flexion fuera del plano)
J_vig  = min(Iy_vig, Iz_vig) * 0.3  # torsion: 30% del menor I

# --- Losa 15 cm ---
t_losa = 0.15  # espesor de la losa (m)

# ============================================================
# 3. CARGAS
# ============================================================
# Carga muerta (G) = peso propio losa + acabados
# Peso propio losa: 25 kN/m3 * 0.15 m = 3.75 kN/m2
# Acabados: 1.5 kN/m2 (pisos, contrapisos, ceramica, etc.)
q_losa = gamma * t_losa + 1.5   # = 5.25 kN/m2

# Carga viva (Q) segun usos (oficina/educacion)
q_viva = 2.0  # kN/m2

# ============================================================
# 4. FUNCIONES
# ============================================================

def construir_modelo():
    """
    Construye el modelo 3D completo en OpenSees.
    
    Esta funcion:
    1. Limpia el modelo anterior (wipe)
    2. Define el tipo de modelo (3D, 6 GDL por nodo)
    3. Crea el material y transformaciones geometricas
    4. Crea los nodos en las posiciones correctas
    5. Fija los apoyos en la base
    6. Crea los elementos (columnas y vigas)
    
    Retorna:
        coords: diccionario {id_nodo: (x, y, z)}
        columnas: lista de tags de columnas
        vigas_x: lista de tags de vigas en X
        vigas_y: lista de tags de vigas en Y
    """
    
    # Limpiar cualquier modelo anterior en memoria
    ops.wipe()  # borra todo el modelo previo de OpenSees
    
    # Crear modelo basico 3D con 6 grados de libertad por nodo
    # -ndm 3: tres dimensiones (x, y, z)
    # -ndf 6: seis GDL por nodo (3 traslaciones + 3 rotaciones)
    ops.model('basic', '-ndm', 3, '-ndf', 6)
    
    # Material elástico unidimensional con modulo Ec
    # Se usa para las vigas y columnas (elasticBeamColumn requiere un material)
    ops.uniaxialMaterial('Elastic', 1, Ec)  # tag=1, rigididad=Ec
    
    # --- TRANSFORMACIONES GEOMETRICAS ---
    # Definen como se mapea el eje local del elemento al sistema global
    # Params: geomTransf tag vecyz_x vecyz_y vecyz_z
    # vecyz es el vector que define el plano yz local
    
    # Transformacion 1: COLUMNAS (eje local vertical, eje x local en +Z global)
    # El vector vecyz apunta en +X global, asi el eje y local queda en +X
    ops.geomTransf('Linear', 1, 1, 0, 0)  # tag=1, vecyz=(1,0,0)
    
    # Transformacion 2: VIGAS EN X (eje local en +X global)
    # El vector vecyz apunta en +Z global, asi el eje y local queda en +Z
    ops.geomTransf('Linear', 2, 0, 0, 1)  # tag=2, vecyz=(0,0,1)
    
    # Transformacion 3: VIGAS EN Y (eje local en +Y global)
    # El vector vecyz apunta en +Z global, asi el eje y local queda en +Z
    ops.geomTransf('Linear', 3, 0, 0, 1)  # tag=3, vecyz=(0,0,1)
    
    # --- CREACION DE NODOS ---
    # Numeracion: se recorre nivel -> ix -> iy
    # Piso 0 (base):     nodos 1, 2, 3, 4
    # Piso 1 (techo):    nodos 5, 6, 7, 8
    
    coords = {}   # diccionario para guardar coordenadas {id: (x,y,z)}
    nid = 1       # contador de id de nodo, empieza en 1
    
    for iz in range(nNivel):       # recorre niveles: 0 (base), 1 (techo)
        for ix in range(nX):       # recorre ejes X: 0 (x=0), 1 (x=4)
            for iy in range(nY):   # recorre ejes Y: 0 (y=0), 1 (y=4)
                # Guardar coordenadas en el diccionario
                coords[nid] = (X[ix], Y[iy], Z[iz])
                # Crear el nodo en OpenSees con sus coordenadas (x, y, z)
                ops.node(nid, X[ix], Y[iy], Z[iz])
                nid += 1  # siguiente id
    
    # --- APOYOS: fijos en la base (todos los GDL restringidos) ---
    # Los nodos 1, 2, 3, 4 (nivel 0) son apoyos fijos
    # fix(nodeTag, dofx, dofy, dofz, dofrx, dofry, dofrz)
    # 1 = restringido (fijo), 0 = libre
    for i in range(1, nNodosPorPiso + 1):  # nodos 1 a 4
        ops.fix(i, 1, 1, 1, 1, 1, 1)  # todos los GDL fijos
    
    # --- CREACION DE ELEMENTOS ---
    tag = 1        # tag del siguiente elemento
    columnas = []  # lista para guardar tags de columnas
    vigas_x  = []  # lista para guardar tags de vigas en X
    vigas_y  = []  # lista para guardar tags de vigas en Y
    
    # --- COLUMNAS: conectan base (nivel 0) con techo (nivel 1) ---
    # Numeracion de nodos base: 1, 2, 3, 4
    # Numeracion de nodos techo: 5, 6, 7, 8
    for ix in range(nX):       # recorre columnas en X
        for iy in range(nY):   # recorre columnas en Y
            # Nodo base: posicion en la grilla de nodos
            n1 = 1 + ix * nY + iy             # nodo del piso 0
            # Nodo tope: misma posicion pero en piso 1
            n2 = 1 + nNodosPorPiso + ix * nY + iy  # nodo del piso 1
            
            # Crear elemento: elasticBeamColumn
            # Params: tag, nodo_i, nodo_j, A, E, G, J, Iy, Iz, transfTag
            ops.element('elasticBeamColumn', tag, n1, n2,
                        A_col, Ec, Gc, J_col, Iy_col, Iz_col, 1)
            columnas.append(tag)  # guardar tag de esta columna
            tag += 1  # siguiente tag
    
    # --- VIGAS EN X: conectan nodos con mismo Y, distinto X ---
    # Para cada eje Y, hay una viga que va de X=0 a X=4
    for iy in range(nY):  # recorre ejes Y: 0 y 1
        # Nodo inicio: piso 1, X=0, Y=Y[iy]
        n1 = 1 + nNodosPorPiso + 0 * nY + iy  # nodo en (0, Y[iy], 3)
        # Nodo fin: piso 1, X=4, Y=Y[iy]
        n2 = 1 + nNodosPorPiso + 1 * nY + iy  # nodo en (4, Y[iy], 3)
        
        # Crear viga con transformacion 2 (eje local en +X)
        ops.element('elasticBeamColumn', tag, n1, n2,
                    A_vig, Ec, Gc, J_vig, Iy_vig, Iz_vig, 2)
        vigas_x.append(tag)  # guardar tag de esta viga X
        tag += 1
    
    # --- VIGAS EN Y: conectan nodos con mismo X, distinto Y ---
    # Para cada eje X, hay una viga que va de Y=0 a Y=4
    for ix in range(nX):  # recorre ejes X: 0 y 1
        # Nodo inicio: piso 1, X=X[ix], Y=0
        n1 = 1 + nNodosPorPiso + ix * nY + 0  # nodo en (X[ix], 0, 3)
        # Nodo fin: piso 1, X=X[ix], Y=4
        n2 = 1 + nNodosPorPiso + ix * nY + 1  # nodo en (X[ix], 4, 3)
        
        # Crear viga con transformacion 3 (eje local en +Y)
        ops.element('elasticBeamColumn', tag, n1, n2,
                    A_vig, Ec, Gc, J_vig, Iy_vig, Iz_vig, 3)
        vigas_y.append(tag)  # guardar tag de esta viga Y
        tag += 1
    
    # Retornar toda la informacion del modelo
    return coords, columnas, vigas_x, vigas_y


def aplicar_carga_gravedad(q, incluir_peso_vigas=False):
    """
    Aplica carga gravitacional (hacia abajo) sobre la losa.
    
    Metodo de areas tributarias:
    La carga de la losa se distribuye a las vigas del contorno usando
    areas tributarias triangulares y trapeciales.
    
    Para una losa cuadrada (Lx = Ly = 4m), ambas direcciones reciben
    triangulos de area = Lx*Ly/4 = 4 m2 cada uno.
    
    Cada nodo esquina recibe: q * Lx * Ly / 8
    La suma total de todas las cargas nodales = q * Lx * Ly (carga total losa)
    
    Args:
        q: carga uniforme sobre la losa (kN/m2)
        incluir_peso_vigas: si True, agrega el peso propio de las vigas
    """
    
    # Dimensiones del vano
    Lx = X[1] - X[0]  # longitud en X = 4.0 m
    Ly = Y[1] - Y[0]  # longitud en Y = 4.0 m
    
    # --- CARGA DE LOSA SOBRE VIGAS EN X (TRIANGULAR) ---
    # Cada viga en X (Y=0 y Y=4) recibe un triangulo tributario
    # El triangulo tiene: base = Lx, altura = Ly/2
    # Area del triangulo = Lx * Ly / 2
    # Cada nodo extremo de la viga recibe la mitad del triangulo
    # Carga por nodo esquina = q * Lx * Ly / 8
    
    # Calcular carga nodal para esquinas
    F_tri_corner = q * Lx * Ly / 8.0  # kN por nodo esquina
    
    # Aplicar carga a las vigas en X
    for iy in range(nY):  # recorre los 2 ejes Y
        # Nodo esquina X=0 (inicio de la viga)
        n1 = 1 + nNodosPorPiso + 0 * nY + iy  # nodo en (0, Y[iy], 3)
        # Nodo esquina X=4 (fin de la viga)
        n2 = 1 + nNodosPorPiso + 1 * nY + iy  # nodo en (4, Y[iy], 3)
        
        # Aplicar carga puntual vertical hacia abajo (-Z)
        # ops.load(nodeTag, fx, fy, fz, mx, my, mz)
        ops.load(n1, 0.0, 0.0, -F_tri_corner, 0.0, 0.0, 0.0)  # nodo inicio
        ops.load(n2, 0.0, 0.0, -F_tri_corner, 0.0, 0.0, 0.0)  # nodo fin
    
    # --- CARGA DE LOSA SOBRE VIGAS EN Y (TRAPEZOIDAL) ---
    # Cada viga en Y (X=0 y X=4) recibe un trapecio tributario
    # Para losa cuadrada, el trapecio se convierte en triangulo igual
    # Cada nodo esquina recibe: q * Lx * Ly / 8
    
    # Calcular carga nodal para esquinas
    F_trap_corner = q * Lx * Ly / 8.0  # kN por nodo esquina
    
    # Aplicar carga a las vigas en Y
    for ix in range(nX):  # recorre los 2 ejes X
        # Nodo esquina Y=0 (inicio de la viga)
        n1 = 1 + nNodosPorPiso + ix * nY + 0  # nodo en (X[ix], 0, 3)
        # Nodo esquina Y=4 (fin de la viga)
        n2 = 1 + nNodosPorPiso + ix * nY + 1  # nodo en (X[ix], 4, 3)
        
        # Aplicar carga puntual vertical hacia abajo (-Z)
        ops.load(n1, 0.0, 0.0, -F_trap_corner, 0.0, 0.0, 0.0)
        ops.load(n2, 0.0, 0.0, -F_trap_corner, 0.0, 0.0, 0.0)
    
    # --- PESO PROPIO DE LAS VIGAS (solo si se solicita) ---
    if incluir_peso_vigas:
        # Peso lineal de la viga = peso_unitario * area_seccion
        w_viga = gamma * A_vig  # kN/m = 25 * 0.125 = 3.125 kN/m
        
        # Vigas en X: peso distribuido = w_viga, longitud = Lx
        for iy in range(nY):
            # Carga nodal = w * L / 2 (media viga a cada extremo)
            F = w_viga * Lx / 2.0  # = 3.125 * 4 / 2 = 6.25 kN por nodo
            n1 = 1 + nNodosPorPiso + 0 * nY + iy  # nodo inicio
            n2 = 1 + nNodosPorPiso + 1 * nY + iy  # nodo fin
            ops.load(n1, 0.0, 0.0, -F, 0.0, 0.0, 0.0)
            ops.load(n2, 0.0, 0.0, -F, 0.0, 0.0, 0.0)
        
        # Vigas en Y: peso distribuido = w_viga, longitud = Ly
        for ix in range(nX):
            F = w_viga * Ly / 2.0  # = 6.25 kN por nodo
            n1 = 1 + nNodosPorPiso + ix * nY + 0  # nodo inicio
            n2 = 1 + nNodosPorPiso + ix * nY + 1  # nodo fin
            ops.load(n1, 0.0, 0.0, -F, 0.0, 0.0, 0.0)
            ops.load(n2, 0.0, 0.0, -F, 0.0, 0.0, 0.0)


def resolver():
    """
    Configura y ejecuta el analisis estatico lineal.
    
    Pasos del analisis:
    1. Definir el sistema de ecuaciones (matriz de rigidez)
    2. Numerar los nodos (orden de las ecuaciones)
    3. Aplicar restricciones (apoyos)
    4. Definir el integrador (carga incremental)
    5. Seleccionar algoritmo de resolucion
    6. Ejecutar el analisis
    
    Retorna:
        ok: 0 si convergio, != 0 si fallo
    """
    
    # Sistema de ecuaciones: banda SPD (simetrico positivo definido)
    # Eficiente para modelos pequenos con estructura de banda
    ops.system('BandSPD')
    
    # Numerador: RCM (Reverse Cuthill-McKee)
    # Reordena los nodos para reducir el ancho de banda de la matriz
    ops.numberer('RCM')
    
    # Restricciones: Plain (sin multiplicadores de restriccion)
    # Simple: solo apoyos fijos, sin joints restrains
    ops.constraints('Plain')
    
    # Integrador: LoadControl con paso deltaLambda = 1.0
    # Aplica la carga completa en un solo paso
    ops.integrator('LoadControl', 1.0)
    
    # Algoritmo: Lineal (no necesita iteracion porque el modelo es lineal)
    ops.algorithm('Linear')
    
    # Tipo de analisis: estatico (no dinamico)
    ops.analysis('Static')
    
    # Ejecutar 1 paso de analisis
    ok = ops.analyze(1)  # retorna 0 si convergio
    
    # Calcular reacciones en los apoyos
    ops.reactions()
    
    return ok  # 0 = exitoso


def extraer_resultados(coords):
    """
    Extrae desplazamientos y reacciones del modelo resuelto.
    
    Args:
        coords: diccionario de coordenadas {id_nodo: (x,y,z)}
    
    Returns:
        disp: diccionario {id_nodo: [ux, uy, uz, rx, ry, rz]}
        reac: diccionario {id_nodo: [fx, fy, fz, mx, my, mz]} (solo apoyos)
    """
    
    # Extraer desplazamientos de TODOS los nodos
    disp = {}
    for nid in coords:  # recorre todos los nodos
        # nodeDisp(nodeTag, dof) retorna el desplazamiento en cada GDL
        # DOF 1=UX, 2=UY, 3=UZ, 4=RX, 5=RY, 6=RZ
        disp[nid] = [ops.nodeDisp(nid, i) for i in range(1, 7)]
    
    # Extraer reacciones SOLO en los apoyos (nodos 1 a 4)
    reac = {}
    for nid in range(1, nNodosPorPiso + 1):  # nodos 1, 2, 3, 4
        # nodeReaction(nodeTag, dof) retorna la reaccion en cada GDL
        reac[nid] = [ops.nodeReaction(nid, i) for i in range(1, 7)]
    
    return disp, reac


# ============================================================
# 5. EJECUCION PRINCIPAL
# ============================================================

# Imprimir titulo
print("=" * 60)  # linea separadora
print("  LAB BENCHMARK 3D - Columnas L, tributarios tri/trapecio")
print("=" * 60)

# --- CASO G: CARGA MUERTA ---
print("\n[1] Construyendo modelo...")

# Construir el modelo (nodos, apoyos, elementos)
coords, cols, vx, vy = construir_modelo()

# Identificar nodos del piso superior (techo)
# Nodos base: 1 a 4, Nodos techo: 5 a 8
nodos_piso1 = list(range(nNodosPorPiso + 1, 2 * nNodosPorPiso + 1))
# = [5, 6, 7, 8]

# Imprimir resumen del modelo
print(f"    Nodos:    {len(coords)}")      # 8 nodos totales
print(f"    Columnas: {len(cols)} (tipo L)")  # 4 columnas
print(f"    Vigas X:  {len(vx)}")           # 2 vigas en X
print(f"    Vigas Y:  {len(vy)}")           # 2 vigas en Y
print(f"    Total:    {len(cols) + len(vx) + len(vy)} elementos")  # 8 elementos

print("\n[2] Aplicando carga muerta (G)...")

# Definir serie temporal: carga incremental lineal
ops.timeSeries('Linear', 1)  # tag=1, variacion lineal

# Definir patron de carga: plano, usa serie temporal 1
ops.pattern('Plain', 1, 1)  # tag=1, seriesTag=1

# Aplicar carga muerta (losa + acabados + peso vigas)
aplicar_carga_gravedad(q_losa, incluir_peso_vigas=True)

# Resolver el analisis
ok_G = resolver()  # retorna 0 si OK

# Extraer resultados del caso G
disp_G, reac_G = extraer_resultados(coords)

# Extraer fuerzas internas de todos los elementos
fuerzas_G = {}
for etag in cols + vx + vy:  # recorre todos los elementos
    # eleForce(elementTag) retorna [P, V2, V3, T, M2, M3] en el nodo i
    fuerzas_G[etag] = [round(f, 4) for f in ops.eleForce(etag)]

# Imprimir si convergio
print(f"    Convergencia: {'OK' if ok_G == 0 else 'FALLO'}")

# --- CASO Q: CARGA VIVA ---
print("\n[3] Aplicando carga viva (Q)...")

# Reconstruir modelo limpio (wipe + crear de nuevo)
construir_modelo()

# Configurar patron de carga
ops.timeSeries('Linear', 1)  # serie temporal 1
ops.pattern('Plain', 1, 1)   # patron 1

# Aplicar solo carga viva (sin peso de vigas)
aplicar_carga_gravedad(q_viva)

# Resolver
ok_Q = resolver()

# Extraer resultados
disp_Q, reac_Q = extraer_resultados(coords)
print(f"    Convergencia: {'OK' if ok_Q == 0 else 'FALLO'}")

# --- CASO EX: SISMO EN DIRECCION X ---
print("\n[4] Aplicando carga lateral EX...")

# Reconstruir modelo limpio
construir_modelo()

# Configurar patron de carga
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

# Carga lateral: 50 kN en +X en cada nodo del techo
F_sismo = 50.0  # kN

# Aplicar carga en los 4 nodos del piso 1
for nid in nodos_piso1:  # nodos 5, 6, 7, 8
    # Carga en X: 50 kN, todo lo demas en 0
    ops.load(nid, F_sismo, 0.0, 0.0, 0.0, 0.0, 0.0)

# Resolver
ok_EX = resolver()

# Extraer resultados
disp_EX, reac_EX = extraer_resultados(coords)
print(f"    Convergencia: {'OK' if ok_EX == 0 else 'FALLO'}")

# ============================================================
# 6. VERIFICACION DE EQUILIBRIO
# ============================================================
print("\n" + "=" * 60)
print("  VERIFICACION DE EQUILIBRIO")
print("=" * 60)

# Calcular dimensiones del vano
Lx = X[1] - X[0]  # 4.0 m
Ly = Y[1] - Y[0]  # 4.0 m
area_losa = Lx * Ly  # 16.0 m2

# --- Carga muerta total (aplicada manualmente) ---
peso_losa     = gamma * t_losa * area_losa    # peso propio: 25*0.15*16 = 60 kN
peso_acabados = 1.5 * area_losa               # acabados: 1.5*16 = 24 kN
peso_vigas    = 4 * gamma * A_vig * Lx        # 4 vigas: 4*25*0.125*4 = 50 kN
carga_G_total = peso_losa + peso_acabados + peso_vigas  # 60+24+50 = 134 kN

# --- Carga viva total ---
carga_Q_total = q_viva * area_losa  # 2.0*16 = 32 kN

# --- Sumar reacciones verticales (Z) en todos los apoyos ---
# Las reacciones son positivas hacia arriba (+Z)
sum_Rz_G = sum(reac_G[n][2] for n in reac_G)  # suma Fz en nodos 1-4
sum_Rz_Q = sum(reac_Q[n][2] for n in reac_Q)

# Imprimir verificacion G
print(f"\n  Carga muerta (G):")
print(f"    Peso losa:        {peso_losa:>10.2f} kN")       # 60.00
print(f"    Peso acabados:    {peso_acabados:>10.2f} kN")   # 24.00
print(f"    Peso vigas:       {peso_vigas:>10.2f} kN")      # 50.00
print(f"    TOTAL aplicado:   {carga_G_total:>10.2f} kN")   # 134.00
print(f"    SUM reacciones:   {sum_Rz_G:>10.2f} kN")        # 134.00
print(f"    Error equilibrio: {abs(carga_G_total - sum_Rz_G):>10.6f} kN")  # 0.00

# Imprimir verificacion Q
print(f"\n  Carga viva (Q):")
print(f"    TOTAL aplicado:   {carga_Q_total:>10.2f} kN")   # 32.00
print(f"    SUM reacciones:   {sum_Rz_Q:>10.2f} kN")        # 32.00
print(f"    Error equilibrio: {abs(carga_Q_total - sum_Rz_Q):>10.6f} kN")  # 0.00

# --- AREAS TRIBUTARIAS ---
print("\n" + "=" * 60)
print("  AREAS TRIBUTARIAS")
print("=" * 60)

# Carga por nodo esquina (formula general)
F_nodo = q_losa * Lx * Ly / 8.0  # = 5.25*4*4/8 = 10.50 kN

# Verificar tipo de tributario segun geometria
if abs(Lx - Ly) < 1e-6:  # losa cuadrada
    area_tri = Lx * Ly / 4.0    # = 4.0 m2 por triangulo
    area_trap = area_tri         # igual para cuadrada
    tipo_trib = "Losa cuadrada: ambas direcciones son TRIANGULOS"
else:  # losa rectangular
    area_tri = 0.5 * Lx * (Ly / 2.0)            # triangulo
    area_trap = 0.5 * (Ly + Ly/2) * (Lx/2)      # trapecio
    tipo_trib = "Losa rectangular: X=triangulo, Y=trapecio"

# Imprimir resultados de tributarios
print(f"\n  {tipo_trib}")
print(f"\n  Vigas X (TRIANGULARES):")
print(f"    Cada nodo esquina recibe: {F_nodo:.2f} kN")
print(f"    Area por viga: {area_tri:.2f} m2")
print(f"\n  Vigas Y (TRIANGULARES/TRAPEZOIDALES):")
print(f"    Cada nodo esquina recibe: {F_nodo:.2f} kN")
print(f"    Area por viga: {area_trap:.2f} m2")

# --- DESPLAZAMIENTOS ---
print("\n" + "=" * 60)
print("  DESPLAZAMIENTOS NODO TECHO")
print("=" * 60)

# Imprimir encabezado de tabla
print(f"  {'Nodo':<6} {'X(m)':<8} {'Y(m)':<8} {'UZ_G(mm)':<12} {'UZ_Q(mm)':<12} {'UX_EX(mm)':<12}")

# Recorrer nodos del techo
for nid in nodos_piso1:  # nodos 5, 6, 7, 8
    cx, cy, cz = coords[nid]        # coordenadas del nodo
    uz_g  = disp_G[nid][2] * 1000   # desplazamiento Z en G (convertir m -> mm)
    uz_q  = disp_Q[nid][2] * 1000   # desplazamiento Z en Q
    ux_ex = disp_EX[nid][0] * 1000  # desplazamiento X en EX
    print(f"  {nid:<6} {cx:<8.1f} {cy:<8.1f} {uz_g:<12.4f} {uz_q:<12.4f} {ux_ex:<12.4f}")

# --- FUERZAS INTERNAS ---
print("\n" + "=" * 60)
print("  FUERZAS INTERNAS (Caso G)")
print("=" * 60)

# Imprimir encabezado
print(f"  {'Elem':<6} {'Tipo':<10} {'P_i(kN)':<12} {'V2_i(kN)':<12} {'V3_i(kN)':<12} {'M2_i':<12}")

# Recorrer todos los elementos
for etag in cols + vx + vy:
    f = fuerzas_G[etag]  # [P, V2, V3, T, M2, M3]
    # Identificar tipo de elemento
    tipo = "ColL" if etag in cols else ("VigX" if etag in vx else "VigY")
    # Imprimir: tag, tipo, fuerza axial, cortante 2, cortante 3, momento 2
    print(f"  {etag:<6} {tipo:<10} {f[0]:<12.4f} {f[1]:<12.4f} {f[2]:<12.4f} {f[4]:<12.4f}")

# ============================================================
# 7. GUARDAR RESULTADOS EN JSON
# ============================================================
# Crear carpeta results si no existe
os.makedirs('results', exist_ok=True)

# Construir diccionario de resultados
resultados = {
    'model_info': {  # informacion general del modelo
        'description': 'Marco 3D: 4 columnas L, 4 vigas, losa tributaria tri/trapecio',
        'geometry': {  # geometria
            'plan_x_m': Lx,           # dimension en X
            'plan_y_m': Ly,           # dimension en Y
            'height_m': Z[1] - Z[0],  # altura = 3.0 m
            'n_columns': len(cols),    # numero de columnas
            'n_beams_x': len(vx),     # numero de vigas en X
            'n_beams_y': len(vy),     # numero de vigas en Y
        },
        'sections': {  # secciones
            'column': f'L {col_leg*100:.0f}x{col_leg*100:.0f} cm, espesor {col_t*100:.0f} cm',
            'column_area_m2': round(A_col, 6),  # area columna
            'column_Iy_m4': Iy_col,              # inercia Y columna
            'column_Iz_m4': Iz_col,              # inercia Z columna
            'beam': f'{v_b*100:.0f}x{v_h*100:.0f} cm',  # seccion viga
            'slab': f'{t_losa*100:.0f} cm',               # espesor losa
        },
        'material': {  # material
            'fpc_MPa': fpc,                    # resistencia
            'Ec_kPa': round(Ec, 0),            # modulo elasticidad
            'gamma_kN_m3': gamma,               # peso unitario
        },
        'loads': {  # cargas
            'q_dead_kN_m2': q_losa,            # carga muerta
            'q_live_kN_m2': q_viva,            # carga viva
            'tributary_method': 'Triangular (vigas X) + Trapezoidal (vigas Y)',
        },
        'units': 'm, kN, kPa',  # unidades
    },
    'nodes': {str(k): list(v) for k, v in coords.items()},  # coordenadas nodos
    'elements': {  # elementos
        'columns': cols,   # tags de columnas
        'beams_x': vx,     # tags de vigas X
        'beams_y': vy,     # tags de vigas Y
    },
    'load_cases': {  # casos de carga
        'G': {  # carga muerta
            'applied_kN': round(carga_G_total, 2),        # carga aplicada
            'reaction_kN': round(sum_Rz_G, 2),            # suma de reacciones
            'error_kN': round(abs(carga_G_total - sum_Rz_G), 6),  # error
            'displacements': {  # desplazamientos
                str(k): [round(v[i], 8) for i in range(3)]  # solo UX, UY, UZ
                for k, v in disp_G.items()
            },
            'reactions': {  # reacciones
                str(k): [round(v[i], 4) for i in range(3)]  # solo Fx, Fy, Fz
                for k, v in reac_G.items()
            },
        },
        'Q': {  # carga viva
            'applied_kN': round(carga_Q_total, 2),
            'reaction_kN': round(sum_Rz_Q, 2),
            'error_kN': round(abs(carga_Q_total - sum_Rz_Q), 6),
            'displacements': {
                str(k): [round(v[i], 8) for i in range(3)]
                for k, v in disp_Q.items()
            },
            'reactions': {
                str(k): [round(v[i], 4) for i in range(3)]
                for k, v in reac_Q.items()
            },
        },
        'EX': {  # sismo en X
            'applied_kN': F_sismo * 4,  # 50*4 = 200 kN total
            'displacements': {
                str(k): [round(v[i], 8) for i in range(3)]
                for k, v in disp_EX.items()
            },
            'reactions': {
                str(k): [round(v[i], 4) for i in range(3)]
                for k, v in reac_EX.items()
            },
        },
    },
}

# Guardar en archivo JSON
with open('results/lab_results.json', 'w') as f:
    json.dump(resultados, f, indent=2)  # indent=2 para formato legible

# Imprimir confirmacion
print(f"\nResultados guardados en results/lab_results.json")
print("\n" + "=" * 60)
print("  FIN DEL LABORATORIO")
print("=" * 60)
