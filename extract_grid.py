import ezdxf
import math
from collections import defaultdict

DXF_PATH = r"C:\Users\edfev\OneDrive\Desktop\UAndes\noveno semestre\Métodos computacionales en obras civiles\P1\Planos\2017_67-100.dxf"

doc = ezdxf.readfile(DXF_PATH)
msp = doc.modelspace()

# =============================================================================
# 1) DIMENSION entities
# =============================================================================
print("=" * 80)
print("SECTION 1: DIMENSION ENTITIES")
print("=" * 80)

dim_count = 0
for e in msp.query("DIMENSION"):
    dim_count += 1
    layer = e.dxf.layer
    dimtext = ""
    try:
        dimtext = e.dxf.dimtext
    except Exception:
        pass
    defpoints = []
    for attr in ["defpoint", "defpoint2", "defpoint3"]:
        try:
            pt = getattr(e.dxf, attr)
            defpoints.append((attr, pt))
        except Exception:
            pass

    # Compute distance between defpoint and defpoint2 if dimtext is empty
    computed = ""
    if (not dimtext or dimtext.strip() == "") and len(defpoints) >= 2:
        p1 = defpoints[0][1]
        p2 = defpoints[1][1]
        dist = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        computed = f"{dist:.2f}"

    print(f"  DIM #{dim_count}  Layer: {layer}")
    for name, pt in defpoints:
        print(f"    {name}: ({pt[0]:.3f}, {pt[1]:.3f}, {pt[2]:.3f})")
    if dimtext and dimtext.strip():
        print(f"    dimtext: {dimtext.strip()}")
    if computed:
        print(f"    computed dist(p1,p2): {computed}")
    print()

if dim_count == 0:
    print("  No DIMENSION entities found in modelspace.\n")

print(f"Total DIMENSION entities: {dim_count}\n")

# =============================================================================
# 2) TEXT and MTEXT entities - filtered
# =============================================================================
print("=" * 80)
print("SECTION 2: TEXT / MTEXT ENTITIES (filtered)")
print("=" * 80)

axis_labels = []
beam_sections = []
heights = []
slab_info = []
column_info = []
wall_info = []
axis_info = []

for e in msp.query("TEXT MTEXT"):
    layer = e.dxf.layer
    try:
        text = e.dxf.text if e.dxftype() == "TEXT" else e.plain_text()
    except Exception:
        try:
            text = e.dxf.text
        except Exception:
            text = ""
    text = text.strip()
    if not text:
        continue

    insert = None
    try:
        insert = e.dxf.insert
    except Exception:
        pass

    info = f"  Layer: {layer}, Insert: {insert}, Text: \"{text}\""

    # Single letter or short number -> axis label candidate
    if len(text) <= 3 and text.isalnum():
        axis_labels.append(info)

    # Beam sections
    if "/" in text:
        beam_sections.append(info)

    # Heights
    if "h=" in text.lower() or "H=" in text:
        heights.append(info)

    # Slab info
    if "LOSA" in text.upper() or "e=" in text.lower():
        slab_info.append(info)

    # Column info
    txt_up = text.upper()
    if "PILAR" in txt_up or txt_up.startswith("COL") or txt_up.startswith("C") and len(text) <= 4:
        column_info.append(info)

    # Wall info
    if "MURO" in txt_up:
        wall_info.append(info)

    # Axis info
    if "EJE" in txt_up or "EJES" in txt_up:
        axis_info.append(info)

print("\n--- Axis Labels (short text, likely labels) ---")
for x in axis_labels[:200]:
    print(x)
print(f"  ({len(axis_labels)} total)\n")

print("--- Beam Sections (containing '/') ---")
for x in beam_sections[:100]:
    print(x)
print(f"  ({len(beam_sections)} total)\n")

print("--- Heights (containing 'h=' or 'H=') ---")
for x in heights[:100]:
    print(x)
print(f"  ({len(heights)} total)\n")

print("--- Slab Info (containing 'LOSA' or 'e=') ---")
for x in slab_info[:100]:
    print(x)
print(f"  ({len(slab_info)} total)\n")

print("--- Column Info (containing 'PILAR'/'COL'/'C') ---")
for x in column_info[:100]:
    print(x)
print(f"  ({len(column_info)} total)\n")

print("--- Wall Info (containing 'MURO') ---")
for x in wall_info[:100]:
    print(x)
print(f"  ({len(wall_info)} total)\n")

print("--- Axis Text (containing 'EJE'/'EJES') ---")
for x in axis_info[:100]:
    print(x)
print(f"  ({len(axis_info)} total)\n")

# =============================================================================
# 3) CIRCLE entities on RLE-EJE layer (axis bubbles)
# =============================================================================
print("=" * 80)
print("SECTION 3: CIRCLES ON AXIS BUBBLE LAYERS (RLE-EJE etc.)")
print("=" * 80)

eje_circles = []
for e in msp.query("CIRCLE"):
    layer = e.dxf.layer.upper()
    if "EJE" in layer or "EJES" in layer or layer == "RLE-EJE":
        center = e.dxf.center
        radius = e.dxf.radius
        eje_circles.append((center, radius, layer))
        print(f"  Layer: {e.dxf.layer}, Center: ({center[0]:.3f}, {center[1]:.3f}, {center[2]:.3f}), Radius: {radius:.3f}")

print(f"\nTotal axis bubble circles: {len(eje_circles)}\n")

# =============================================================================
# 4) LINE entities on axis-related layers
# =============================================================================
print("=" * 80)
print("SECTION 4: LINES ON AXIS-RELATED LAYERS")
print("=" * 80)

eje_lines = []
for e in msp.query("LINE"):
    layer = e.dxf.layer.upper()
    if "EJE" in layer or "EJES" in layer:
        start = e.dxf.start
        end = e.dxf.end
        eje_lines.append((start, end, e.dxf.layer))
        print(f"  Layer: {e.dxf.layer}, Start: ({start[0]:.3f}, {start[1]:.3f}), End: ({end[0]:.3f}, {end[1]:.3f})")

print(f"\nTotal axis lines: {len(eje_lines)}\n")

# =============================================================================
# 5) ALL layers summary
# =============================================================================
print("=" * 80)
print("SECTION 5: ALL LAYERS SUMMARY")
print("=" * 80)

layers = defaultdict(int)
for e in msp:
    layers[e.dxf.layer] += 1

for lyr in sorted(layers.keys()):
    print(f"  {lyr}: {layers[lyr]} entities")
print(f"\nTotal layers: {len(layers)}")
print(f"Total entities: {sum(layers.values())}\n")

# =============================================================================
# 6) GRID RECONSTRUCTION from axis bubble circles
# =============================================================================
print("=" * 80)
print("SECTION 6: GRID RECONSTRUCTION FROM AXIS BUBBLES")
print("=" * 80)

if not eje_circles:
    print("  No axis bubble circles found. Trying to use TEXT entities as grid markers...\n")
    # Fallback: try to use short text entities as grid markers
    grid_points = []
    for e in msp.query("TEXT MTEXT"):
        try:
            text = e.dxf.text.strip() if e.dxftype() == "TEXT" else e.plain_text().strip()
            insert = e.dxf.insert
            if len(text) <= 3 and text.isalnum() and text:
                grid_points.append((text, insert, e.dxf.layer))
        except Exception:
            pass

    if grid_points:
        print(f"  Found {len(grid_points)} short text entities that could be grid labels:")
        for txt, pt, lyr in grid_points:
            print(f"    Text: \"{txt}\"  Pos: ({pt[0]:.3f}, {pt[1]:.3f})  Layer: {lyr}")

# Extract centers from axis bubbles
centers = [(c[0], c[1]) for c, r, l in eje_circles]

if centers:
    # Group by approximate X (vertical axes)
    TOLERANCE = 500  # mm tolerance for grouping
    x_groups = defaultdict(list)
    for cx, cy in centers:
        placed = False
        for key in list(x_groups.keys()):
            if abs(cx - key) < TOLERANCE:
                x_groups[key].append((cx, cy))
                placed = True
                break
        if not placed:
            x_groups[cx].append((cx, cy))

    y_groups = defaultdict(list)
    for cx, cy in centers:
        placed = False
        for key in list(y_groups.keys()):
            if abs(cy - key) < TOLERANCE:
                y_groups[key].append((cx, cy))
                placed = True
                break
        if not placed:
            y_groups[cy].append((cx, cy))

    print("\n  --- Vertical Axis Lines (grouped by X coordinate) ---")
    for x_key in sorted(x_groups.keys()):
        pts = x_groups[x_key]
        y_vals = sorted(set(p[1] for p in pts))
        print(f"    X ~ {x_key:.1f}  (Y values: {[f'{y:.1f}' for y in y_vals]}, {len(pts)} bubbles)")

    print("\n  --- Horizontal Axis Lines (grouped by Y coordinate) ---")
    for y_key in sorted(y_groups.keys()):
        pts = y_groups[y_key]
        x_vals = sorted(set(p[0] for p in pts))
        print(f"    Y ~ {y_key:.1f}  (X values: {[f'{x:.1f}' for x in x_vals]}, {len(pts)} bubbles)")

    print(f"\n  Grid structure:")
    print(f"    Vertical axes (by X): {len(x_groups)}")
    print(f"    Horizontal axes (by Y): {len(y_groups)}")

    # Print bounding box
    all_x = [p[0] for p in centers]
    all_y = [p[1] for p in centers]
    print(f"\n  Bounding box of axis bubbles:")
    print(f"    X range: {min(all_x):.1f} to {max(all_x):.1f} (span: {max(all_x) - min(all_x):.1f})")
    print(f"    Y range: {min(all_y):.1f} to {max(all_y):.1f} (span: {max(all_y) - min(all_y):.1f})")
else:
    print("  No axis bubble centers available for grid reconstruction.\n")

# =============================================================================
# 7) EXTRA: Check for INSERT (block) entities that might be axis bubbles
# =============================================================================
print("=" * 80)
print("SECTION 7: INSERT (BLOCK) ENTITIES ON EJE-RELATED LAYERS")
print("=" * 80)

eje_inserts = 0
for e in msp.query("INSERT"):
    layer = e.dxf.layer.upper()
    if "EJE" in layer or "EJES" in layer or "EJ" in layer:
        eje_inserts += 1
        insert = e.dxf.insert
        print(f"  Block: {e.dxf.name}, Layer: {e.dxf.layer}, Insert: ({insert[0]:.3f}, {insert[1]:.3f})")

if eje_inserts == 0:
    # Check all INSERT blocks for context
    block_names = set()
    for e in msp.query("INSERT"):
        block_names.add(e.dxf.name)
    print(f"  No inserts on EJE layers. All block names in drawing: {sorted(block_names)}")

print(f"\nTotal EJE-related inserts: {eje_inserts}")

# =============================================================================
# 8) EXTRA: Check for ARC entities on axis layers
# =============================================================================
print("\n" + "=" * 80)
print("SECTION 8: ARC / LWPOLYLINE / POLYLINE ON EJE LAYERS")
print("=" * 80)

for etype in ["ARC", "LWPOLYLINE", "POLYLINE"]:
    for e in msp.query(etype):
        layer = e.dxf.layer.upper()
        if "EJE" in layer or "EJES" in layer:
            print(f"  {etype} on layer {e.dxf.layer}")

print("\n" + "=" * 80)
print("DONE")
print("=" * 80)
