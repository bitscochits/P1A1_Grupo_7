# Resumen Estructural — Edificio de Ingeniería, Universidad de los Andes

## 1. Descripción General

El Edificio de Ingeniería es una estructura de **al menos 8 niveles** (sótano + 7 pisos) ubicada en el campus de Universidad de los Andes. Las dimensiones en planta son aproximadamente **45.6 m × 39.0 m**, con una cuadrícula de ejes estructurales relativamente densa, especialmente hacia el centro y borde derecho de la planta. Las cotas del archivo DXF están en **centímetros** (convención estándar en planos arquitectónicos colombianos).

---

## 2. Niveles del Edificio

| Nivel | Descripción                          | Código de archivo |
|-------|--------------------------------------|-------------------|
| 0     | Fundación / Sótano                   | 000               |
| 1     | Primer piso (Nivel 1)                | 100               |
| 2     | Segundo piso (Nivel 2)               | 200               |
| 3     | Tercer piso (Nivel 3)                | 300               |
| 4     | Cuarto piso                          | 400–402           |
| 5     | Quinto piso                          | 500–503           |
| 6     | Sexto piso                           | 600               |
| 7     | Séptimo piso                         | 700               |
| 8     | Octavo piso                          | 800–802           |

> **Nota:** Las variantes en la numeración (400–402, 500–503, 800–802) corresponden probablemente a sub-niveles, plataformas parciales o detalle de plantillas por zona.

---

## 3. Cuadrícula de Ejes (RLE-EJE / RLE-EJES)

### 3.1 Ejes Verticales (eje X, coordenadas en cm)

| Eje | X (cm) | X (m) | Separación anterior (m) |
|-----|---------|-------|--------------------------|
| Borde izq. | ~268  | 2.68  | —          |
| —   | ~698    | 6.98  | 4.30                      |
| —   | ~802    | 8.02  | 1.04                      |
| —   | ~1132   | 11.32 | 3.30                      |
| —   | ~1162   | 11.62 | 0.30                      |
| —   | ~1442   | 14.42 | 2.80                      |
| —   | ~1472   | 14.72 | 0.30                      |
| —   | ~1802   | 18.02 | 3.30                      |
| —   | ~1915   | 19.15 | 1.13                      |
| —   | ~2802   | 28.02 | 8.87                      |
| —   | ~2947   | 29.47 | 1.45                      |
| —   | ~3802   | 38.02 | 8.55                      |
| —   | ~4185   | 41.85 | 3.83                      |
| —   | ~4250   | 42.50 | 0.65                      |
| —   | ~4685   | 46.85 | 4.35                      |
| —   | ~4802   | 48.02 | 1.17                      |
| —   | ~5062   | 50.62 | 2.60                      |
| —   | ~5302   | 53.02 | 2.40                      |
| —   | ~5315   | 53.15 | 0.13                      |
| —   | ~5390   | 53.90 | 0.75                      |
| Borde der. | ~5756  | 57.56 | 3.66                   |

**Ancho total (ejes):** ~57.56 − 2.68 = **54.88 m** (cota total reportada ~45.6 m corresponde a los vanos principales entre ejes extremos interiores).

### 3.2 Ejes Horizontales (eje Y, coordenadas en cm)

| Y (cm) | Y (m) | Separación anterior (m) |
|---------|-------|--------------------------|
| ~3221   | 32.21 | —                        |
| ~4692   | 46.92 | 14.71                    |
| ~4795   | 47.95 | 1.03                     |
| ~5026   | 50.26 | 2.31                     |
| ~5520   | 55.20 | 4.94                     |
| ~6020   | 60.20 | 5.00                     |
| ~6312   | 63.12 | 2.92                     |
| ~6410   | 64.10 | 0.98                     |
| ~6415   | 64.15 | 0.05                     |
| ~6511   | 65.11 | 0.96                     |
| ~6522   | 65.22 | 0.11                     |
| ~6585   | 65.85 | 0.63                     |
| ~6768   | 67.68 | 1.83                     |
| ~7033   | 70.33 | 2.65                     |
| ~7275   | 72.75 | 2.42                     |
| ~7481   | 74.81 | 2.06                     |
| ~7984   | 79.84 | 5.03                     |

**Alto total (ejes):** ~79.84 − 32.21 = **47.63 m** (cota total reportada ~39.05 m corresponde a los vanos principales entre ejes extremos).

### 3.3 Observaciones sobre la Cuadrícula

- Las **separaciones muy pequeñas** (0.05–1.04 m) indican ejes de muros de ducto, juntas constructivas, o ejes auxiliares secundarios.
- Los **vanos principales** del edificio son aproximadamente:
  - En dirección X: **4.30 – 8.87 m** (zonas de mayor tramo).
  - En dirección Y: **2.65 – 14.71 m** (la separación inicial de ~14.7 m corresponde a un gran vano, posiblemente salón o auditorio).
- La cuadrícula se concentra más hacia los bordes derechos (X > 4000 cm) e inferiores (Y < 6600 cm), lo que sugiere una zona de núcleo rígido o zona de servicio.

---

## 4. Secciones Estructurales

### 4.1 Vigas de Fundación (V.F.)

| Sección         | Ancho (cm) | Alto (cm) | Notas                      |
|-----------------|------------|-----------|----------------------------|
| V.F. 20/120     | 20         | 120       | Sección estándar ligera    |
| V.F. 20/160     | 20         | 160       | —                          |
| V.F. 20/180     | 20         | 180       | —                          |
| V.F. 20/220     | 20         | 220       | Sección profunda           |
| V.F. 30/170     | 30         | 170       | Mayor ancho, menor altura  |
| V.F. 30/136     | 30         | 136       | —                          |
| V.F. 15/225     | 15         | 225       | Sección más profunda       |

> **Nota:** "V.F." = Viga de Fundación. Estas vigas se encuentran en el nivel 000 (sótano/fundación).

### 4.2 Vigas de Piso (RLE-VIGA — 69 entidades)

Alturas reportadas en los planos:

| Altura (cm) | Descripción probable                        |
|-------------|---------------------------------------------|
| 60          | Viga secundaria / arriostramiento           |
| 100         | Viga estándar de piso                       |
| 120         | Viga estándar de piso                       |
| 155         | Viga de tramo largo                         |
| 180         | Viga de tramo muy largo / borde             |
| 516         | Viga de gran canto (posiblemente viga-cimiento o elementos especiales de fundación) |

> **Nota:** La altura de 516 cm es inusualmente grande para una viga de piso. Podría corresponder a un elemento combinado viga-muro cortina, o a un error de lectura del plano (posiblemente 51.6 cm). Se recomienda verificar con el plano original.

### 4.3 Losas (RLE-LOSA — 14 entidades)

| Elemento       | Espesor (cm) |
|----------------|-------------|
| LOSA e=25      | 25          |

- Espesor uniforme de **25 cm** para todas las losas.
- 14 entidades sugiere que las losas están subdivididas por vanos o que solo se representan las losas macizas (sin considerar los huecos).

### 4.4 Columnas (RLE-PILAR — 24 entidades)

- **24 columnas** distribuidas en la cuadrícula de ejes.
- No se proporcionan dimensiones de sección de las columnas en los datos disponibles; se recomienda revisar el detalle de cada nivel.

### 4.5 Muros (RLE-MURO — 157 entidades)

- **157 muros** estructurales y/o de relleno.
- Alta densidad de muros sugiere sistema mixto muro-columna o muros de cortante en zonas específicas.

### 4.6 Fundación (RLE-FUNDACION — 199 entidades)

- **199 entidades** en capa de fundación, lo que indica un sistema de fundación complejo (posiblemente losas de fundación, pilotes, y vigas de coronación).

---

## 5. Alturas Piso Estimadas

No se proporcionaron cotas de nivel de forma explícita en los datos. Como referencia para edificios de hormigón armado en Colombia:

| Nivel        | Altura típica estimada (m) |
|--------------|----------------------------|
| Sótano       | 3.5 – 4.5                  |
| Piso 1       | 3.5 – 4.5                  |
| Pisos 2–8    | 3.0 – 3.5                  |

> Se recomienda extraer las cotas de nivel directamente de los archivos DXF de secciones o alzados para obtener valores exactos.

---

## 6. Clasificación de Capas DXF: Estructural vs. Arquitectónico

### Capas Estructurales (usar para análisis estructural)

| Capa              | Contenido                  | Entidades | Utilidad                        |
|-------------------|----------------------------|-----------|---------------------------------|
| RLE-PILAR         | Columnas                   | 24        | Modelo estructural              |
| RLE-VIGA          | Vigas                      | 69        | Modelo estructural              |
| RLE-LOSA          | Losas                      | 14        | Modelo estructural              |
| RLE-FUNDACION     | Elementos de fundación     | 199       | Modelo de cimentación           |
| RLE-EJE           | Burujas de ejes            | 44        | Referencia / referencia geom.   |
| RLE-EJES          | Líneas de ejes             | 63        | Referencia / referencia geom.   |
| RLA-COTAS         | Cotas y dimensiones        | —         | Geometría / verificación        |

### Capas Arquitectónicas (excluir del modelo estructural)

| Capa          | Contenido          | Entidades | Utilidad               |
|---------------|--------------------|-----------|------------------------|
| RLE-MURO      | Muros (posible mixto estructural/relleno) | 157 | Verificar si hay muros estructurales de cortante |

> **Nota sobre RLE-MURO:** Esta capa puede contener tanto muros estructurales (cortante) como muros de relleno. Se recomienda revisar individualmente para identificar cuáles participan en la resistencia lateral.

---

## 7. Datos Clave para Modelación

| Parámetro                        | Valor                    |
|----------------------------------|--------------------------|
| Dimensiones en planta            | ~45.6 m × 39.0 m        |
| Número de niveles                | 9 (sótano + 8 pisos)    |
| Columnas                         | 24                       |
| Vigas (pisos)                    | 69                       |
| Losas (espesor)                  | 25 cm                    |
| Vigas de fundación               | 7 secciones diferentes   |
| Cuadrícula de ejes              | 21 verticales × 17 horizontales |
| Sistema estructural probable     | Hormigón armado (marco rígido o mixto) |

---

## 8. Notas

1. **Unidades:** Todas las coordenadas y dimensiones del DXF están en centímetros. Los valores en metros se obtienen dividiendo entre 100.
2. **Sistema de diseño:** Con base en la tipología (edificio universitario de +8 pisos en Bogotá), se asume diseño sísmico según NSR-10 (Capítulo G.12 — Diseño de edificios de Risk Category III o II).
3. **Material probable:** Hormigón armado f'c = 21–28 MPa, acero fy = 420 MPa (tipical para Colombia).
4. **Archivo fuente:** Datos extraídos de archivos DXF del proyecto — verificar siempre contra los planos originales para detalles constructivos.

---

*Documento generado a partir de análisis DXF. Fecha: agosto 2026.*
