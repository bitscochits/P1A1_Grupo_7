# Lab Benchmark 3D

Marco estructural simple para el laboratorio de la Semana 1.

## Modelo

- **Geometria**: 4.0 m x 4.0 m, 1 piso (3.0 m)
- **Columnas**: 4 x 30x30 cm (fijas en base)
- **Vigas**: 4 x 25x50 cm (2 en X, 2 en Y)
- **Losa**: 15 cm (descarga tributaria sobre vigas)
- **Material**: Hormigon f'c = 21 MPa, Ec = 21551 MPa
- **Unidades**: m, kN, kPa

## Cargas

- **Carga muerta (G)**: Peso propio losa (3.75 kN/m2) + acabados (1.5 kN/m2) + peso vigas
- **Carga viva (Q)**: 2.0 kN/m2
- **Sismo (EX)**: 50 kN por nodo del techo

## Archivos

- `benchmark_3d.py` - Modelo principal OpenSeesPy
- `verify.py` - Verificacion manual de resultados
- `plot_geometry.py` - Graficas de geometria, cargas y GDL
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
- **Columna**: V3 = 33.50 kN (compresion)
