# P1A1\_Grupo\_7 — Laboratorio Estructural Digital

**Proyecto:** Laboratorio Estructural Digital del Edificio de Ingeniería  
**Curso:** Métodos Computacionales en Obras Civiles  
**Universidad:** Universidad de los Andes  
**Semestre:** Noveno semestre, 2026

---

## Descripción

Desarrollo de un laboratorio estructural digital 3D del Edificio de Ingeniería de la Universidad de los Andes. El proyecto combina:

- Análisis estructural 3D con **OpenSees/OpenSeesPy**
- Idealización a partir de planos reales (AutoCAD)
- Cargas gravitacionales mediante áreas tributarias
- Carga viva y sismo pseudoestático
- Análisis no lineal de secciones de hormigón armado
- Visualización en **Unity**
- Uso documentado de agentes de IA

---

## Estructura del Proyecto

```
P1A1_Grupo_7/
├── README.md                       # Este archivo
├── AGENTS.md                       # Instrucciones para agentes de IA
├── .gitignore
│
├── benchmark_3d.py                 # Modelo 3D principal en OpenSeesPy
├── extract_elements.py             # Extracción de datos de elementos
├── extract_dims.py                 # Extracción de cotas de planos DXF
├── read_planos.py                  # Lectura de archivos DXF
├── error_section.py                # Demo: error de sección
├── error_support.py                # Demo: error de apoyo
│
├── reports/
│   ├── semana01.md                 # Informe Semana 1 (Markdown)
│   └── semana01.tex                # Informe Semana 1 (LaTeX para Overleaf)
│
├── results/
│   └── benchmark_results.json      # Resultados del modelo 3D
│
├── Planos/
│   ├── *.dwg                       # Planos originales AutoCAD
│   └── *.dxf                       # Planos convertidos a DXF
│
├── Enunciado general.txt           # Enunciado del proyecto
├── Primera entrega.txt             # Requisitos de la primera entrega
├── Cronograma.txt                  # Cronograma del proyecto
├── Trabajo con IA.txt              # Guía de trabajo con IA
└── resumen_estructural.md          # Resumen de geometría del edificio
```

---

## Requisitos

### Python 3.12+

```bash
# Instalar Python 3.12 (OpenSeesPy no soporta 3.14 aún)
winget install Python.Python.3.12
```

### Paquetes necesarios

```bash
"C:\Users\edfev\AppData\Local\Programs\Python\Python312\python.exe" -m pip install openseespy ezdxf
```

### Node.js (para conversión DWG → DXF)

```bash
winget install OpenJS.NodeJS.LTS
```

---

## Uso

### Ejecutar el modelo 3D

```bash
"C:\Users\edfev\AppData\Local\Programs\Python\Python312\python.exe" benchmark_3d.py
```

**Salida:** Archivo `results/benchmark_results.json` con desplazamientos, reacciones y fuerzas internas.

### Extraer datos de elementos

```bash
"C:\Users\edfev\AppData\Local\Programs\Python\Python312\python.exe" extract_elements.py
```

### Demostrar errores deliberados

```bash
"C:\Users\edfev\AppData\Local\Programs\Python\Python312\python.exe" error_section.py
"C:\Users\edfev\AppData\Local\Programs\Python\Python312\python.exe" error_support.py
```

---

## Datos del Modelo

| Parámetro | Valor |
|-----------|-------|
| Dimensiones en planta | 45.0 m × 25.8 m |
| Altura total | 28.5 m |
| Niveles | 9 (fundación + 8 pisos) |
| Nodos | 432 |
| Elementos | 1,040 (384 columnas + 656 vigas) |
| Casos de carga | G, Q, E_X, E_Y |
| Material | Hormigón f'c = 28 MPa |
| Unidades | m, kN, kPa |

### Resultados principales

| Caso | U_X máx (mm) | U_Y máx (mm) | U_Z máx (mm) | Equilibrio |
|------|-------------|-------------|-------------|------------|
| G | 1.6 | 2.9 | 11.5 | ✓ |
| Q | 0.7 | 1.3 | 2.4 | ✓ |
| E_X | 3.4 | 0.0 | 0.1 | ✓ |
| E_Y | 0.0 | 2.3 | 0.1 | ✓ |

---

## Entregas

| Semana | Fecha | Entregable | Puntos |
|--------|-------|------------|--------|
| 0 | 20 ago | LAB 0: modelo 2D mínimo | 5 |
| 1 | 27–28 ago | Benchmark 3D + verificación | 30 |
| 2 | 3–4 sep | Edificio completo + Unity | 30 |
| 3 | 10–11 sep | Carga viva + sismo + capacidad RC | 30 |
| 4 | 17–18 sep | Integración en Unity | 30 |
| 5 | 24–25 sep | Interactividad + modificación | 30 |
| 6 | 1–2 oct | AR básica | 30 |
| 7 | 8–9 oct | Demo final + informe | 90 |

---

## Grupo

| Integrante | GitHub |
|------------|--------|
| [Nombre 1] | [@usuario1](https://github.com/usuario1) |
| [Nombre 2] | [@usuario2](https://github.com/usuario2) |
| [Nombre 3] | [@usuario3](https://github.com/usuario3) |

---

## Licencia

Proyecto académico — Universidad de los Andes, 2026.
