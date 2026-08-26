# Lab Benchmark 3D

Marco estructural simple para el laboratorio de la Semana 1.

## Modelo

- **Geometria**: 4.0 m x 4.0 m, 1 piso (3.0 m)
- **Columnas**: 4 x tipo L 30x30 cm (espesor 15 cm)
- **Vigas**: 4 x 25x50 cm (2 en X, 2 en Y)
- **Losa**: 15 cm (descarga tributaria triangular/trapezoidal)
- **Material**: Hormigon f'c = 21 MPa, Ec = 21551 MPa
- **Unidades**: m, kN, kPa

## Cargas

- **Carga muerta (G)**: Peso propio losa (3.75 kN/m2) + acabados (1.5 kN/m2) + peso vigas
- **Carga viva (Q)**: 2.0 kN/m2
- **Sismo (EX)**: 50 kN por nodo del techo

## Areas tributarias

Para losa cuadrada (4x4 m):
- Vigas X: triangulos de base 4m, altura 2m (4 m2 por viga)
- Vigas Y: triangulos de base 4m, altura 2m (4 m2 por viga)
- Cada nodo esquina recibe: q * Lx * Ly / 8 = 10.50 kN

## Columna tipo L

Seccion L 30x30 cm, espesor 15 cm:
- Area: 675 cm2 = 0.0675 m2
- Iy = Iz = 46375 cm4 = 4.64e-5 m4
- Centroide: (12.5, 12.5) cm desde la esquina

## Archivos

- `benchmark_3d.py` - Modelo principal OpenSeesPy
- `verify.py` - Verificacion manual de resultados
- `plot_geometry.py` - Graficas de geometria, areas tributarias, seccion L, GDL
- `results/` - Resultados JSON y graficas PNG

## Como ejecutar

```bash
# Modelo principal
py -3.12 benchmark_3d.py

# Verificacion manual
py -3.12 verify.py

# Graficas
py -3.12 plot_geometry.py
```

## Resultados

- **Equilibrio G**: 134.00 kN aplicados = 134.00 kN reacciones (error = 0)
- **Equilibrio Q**: 32.00 kN aplicados = 32.00 kN reacciones (error = 0)
- **Columna L**: V3 = 33.50 kN (compresion)
- **UX sismo**: 114.0 mm
