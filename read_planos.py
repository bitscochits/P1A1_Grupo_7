import ezdxf
import os
import sys

PLANOS_DIR = os.path.join(
    r"C:\Users\edfev\OneDrive\Desktop\UAndes\noveno semestre",
    r"Métodos computacionales en obras civiles\P1\Planos"
)

FILES = ["2017_67-200-S.dxf", "2017_67-000.dxf", "2017_67-100.dxf"]


def analyze_dxf(filepath):
    fname = os.path.basename(filepath)
    print("=" * 90)
    print(f"  ANALYZING: {fname}")
    print("=" * 90)

    doc = ezdxf.readfile(filepath)
    msp = doc.modelspace()

    # --- LAYERS ---
    layers = sorted(doc.layers, key=lambda l: l.dxf.name)
    print(f"\n--- LAYERS ({len(layers)} total) ---")
    for lyr in layers:
        print(f"  {lyr.dxf.name:<40} color={lyr.dxf.color}")

    # --- ENTITY COUNTS ---
    entities_by_type = {}
    for e in msp:
        t = e.dxftype()
        entities_by_type[t] = entities_by_type.get(t, 0) + 1

    print(f"\n--- ENTITY TYPE COUNTS ({sum(entities_by_type.values())} total) ---")
    for t in sorted(entities_by_type.keys()):
        print(f"  {t:<30} {entities_by_type[t]}")

    # --- LINES ---
    lines = list(msp.query("LINE"))
    print(f"\n--- LINE entities ({len(lines)} total) ---")
    if lines:
        xs, ys = [], []
        for ln in lines:
            sx, sy = ln.dxf.start.x, ln.dxf.start.y
            ex, ey = ln.dxf.end.x, ln.dxf.end.y
            xs.extend([sx, ex])
            ys.extend([sy, ey])
        print(f"  X range: [{min(xs):.2f}, {max(xs):.2f}]")
        print(f"  Y range: [{min(ys):.2f}, {max(ys):.2f}]")
        print(f"  Longest lines (by length):")
        by_len = sorted(lines, key=lambda l: l.dxf.start.distance(l.dxf.end), reverse=True)
        for ln in by_len[:20]:
            s, e = ln.dxf.start, ln.dxf.end
            print(f"    layer={ln.dxf.layer:<20} ({s.x:.2f},{s.y:.2f}) -> ({e.x:.2f},{e.y:.2f}) len={s.distance(e):.2f}")
        print(f"  First 30 lines:")
        for ln in lines[:30]:
            s, e = ln.dxf.start, ln.dxf.end
            print(f"    layer={ln.dxf.layer:<20} ({s.x:.2f},{s.y:.2f}) -> ({e.x:.2f},{e.y:.2f})")

    # --- LWPOLYLINE ---
    lwplines = list(msp.query("LWPOLYLINE"))
    print(f"\n--- LWPOLYLINE entities ({len(lwplines)} total) ---")
    if lwplines:
        for i, pl in enumerate(lwplines[:30]):
            pts = [(p[0], p[1]) for p in pl.get_points()]
            print(f"  [{i}] layer={pl.dxf.layer:<20} closed={pl.closed} pts={len(pts)}")
            for p in pts[:10]:
                print(f"       ({p[0]:.2f}, {p[1]:.2f})")
            if len(pts) > 10:
                print(f"       ... ({len(pts) - 10} more points)")

    # --- CIRCLE ---
    circles = list(msp.query("CIRCLE"))
    print(f"\n--- CIRCLE entities ({len(circles)} total) ---")
    if circles:
        for i, c in enumerate(circles[:50]):
            cx, cy, r = c.dxf.center.x, c.dxf.center.y, c.dxf.radius
            print(f"  [{i}] layer={c.dxf.layer:<20} center=({cx:.2f},{cy:.2f}) radius={r:.2f}")

    # --- ARC ---
    arcs = list(msp.query("ARC"))
    print(f"\n--- ARC entities ({len(arcs)} total) ---")
    if arcs:
        for i, a in enumerate(arcs[:20]):
            cx, cy = a.dxf.center.x, a.dxf.center.y
            r = a.dxf.radius
            print(f"  [{i}] layer={a.dxf.layer:<20} center=({cx:.2f},{cy:.2f}) r={r:.2f} start={a.dxf.start_angle:.1f} end={a.dxf.end_angle:.1f}")

    # --- ELLIPSE ---
    ellipses = list(msp.query("ELLIPSE"))
    print(f"\n--- ELLIPSE entities ({len(ellipses)} total) ---")

    # --- SPLINE ---
    splines = list(msp.query("SPLINE"))
    print(f"\n--- SPLINE entities ({len(splines)} total) ---")

    # --- HATCH ---
    hatches = list(msp.query("HATCH"))
    print(f"\n--- HATCH entities ({len(hatches)} total) ---")

    # --- SOLID / 3DFACE ---
    solids = list(msp.query("SOLID"))
    faces = list(msp.query("3DFACE"))
    print(f"\n--- SOLID entities ({len(solids)} total) ---")
    print(f"--- 3DFACE entities ({len(faces)} total) ---")

    # --- TEXT ---
    texts = list(msp.query("TEXT"))
    print(f"\n--- TEXT entities ({len(texts)} total) ---")
    if texts:
        for i, t in enumerate(texts[:60]):
            print(f"  [{i}] layer={t.dxf.layer:<20} pos=({t.dxf.insert.x:.2f},{t.dxf.insert.y:.2f}) h={t.dxf.height:.2f} text=\"{t.dxf.text}\"")

    # --- MTEXT ---
    mtexts = list(msp.query("MTEXT"))
    print(f"\n--- MTEXT entities ({len(mtexts)} total) ---")
    if mtexts:
        for i, mt in enumerate(mtexts[:60]):
            raw = mt.text.replace('\n', ' | ')
            print(f"  [{i}] layer={mt.dxf.layer:<20} pos=({mt.dxf.insert.x:.2f},{mt.dxf.insert.y:.2f}) text=\"{raw[:120]}\"")

    # --- INSERT (BLOCKS) ---
    inserts = list(msp.query("INSERT"))
    print(f"\n--- INSERT (block) entities ({len(inserts)} total) ---")
    block_counts = {}
    for ins in inserts:
        bname = ins.dxf.name
        block_counts[bname] = block_counts.get(bname, 0) + 1
    print(f"  Block name frequencies:")
    for bname, cnt in sorted(block_counts.items(), key=lambda x: -x[1]):
        print(f"    {bname:<40} x{cnt}")

    if inserts:
        print(f"  Sample INSERTs with positions:")
        for i, ins in enumerate(inserts[:50]):
            bname = ins.dxf.name
            ix, iy = ins.dxf.insert.x, ins.dxf.insert.y
            sx = ins.dxf.get('xscale', 1.0) if ins.dxf.hasattr('xscale') else 1.0
            sy = ins.dxf.get('yscale', 1.0) if ins.dxf.hasattr('yscale') else 1.0
            rot = ins.dxf.get('rotation', 0.0) if ins.dxf.hasattr('rotation') else 0.0
            print(f"    [{i}] block={bname:<30} pos=({ix:.2f},{iy:.2f}) scale=({sx:.2f},{sy:.2f}) rot={rot:.1f} layer={ins.dxf.layer}")

    # --- DIMENSION ---
    dims = list(msp.query("DIMENSION"))
    print(f"\n--- DIMENSION entities ({len(dims)} total) ---")
    if dims:
        for i, d in enumerate(dims[:30]):
            dxf_type = d.dxf.get('dimtype', 'unknown')
            print(f"  [{i}] layer={d.dxf.layer:<20} type={dxf_type} defpoint=({d.dxf.defpoint.x:.2f},{d.dxf.defpoint.y:.2f})")

    # --- POINT ---
    points = list(msp.query("POINT"))
    print(f"\n--- POINT entities ({len(points)} total) ---")
    if points:
        for i, p in enumerate(points[:20]):
            print(f"  [{i}] layer={p.dxf.layer:<20} pos=({p.dxf.location.x:.2f},{p.dxf.location.y:.2f})")

    # --- RAY / XLINE ---
    rays = list(msp.query("RAY"))
    xlines = list(msp.query("XLINE"))
    print(f"\n--- RAY entities ({len(rays)} total) ---")
    print(f"--- XLINE entities ({len(xlines)} total) ---")

    # --- BOUNDING BOX ---
    all_x, all_y = [], []
    for e in msp:
        try:
            if e.dxftype() in ("LINE", "LWPOLYLINE", "POLYLINE", "CIRCLE", "ARC", "ELLIPSE", "SPLINE"):
                ext = e.dxf.bounding_box
                if ext is not None:
                    all_x.extend([ext.extmin[0], ext.extmax[0]])
                    all_y.extend([ext.extmin[1], ext.extmax[1]])
            if e.dxftype() == "INSERT":
                all_x.append(e.dxf.insert.x)
                all_y.append(e.dxf.insert.y)
            if e.dxftype() in ("TEXT", "MTEXT"):
                all_x.append(e.dxf.insert.x)
                all_y.append(e.dxf.insert.y)
        except Exception:
            pass

    if all_x and all_y:
        print(f"\n--- BOUNDING BOX ---")
        print(f"  X: [{min(all_x):.2f}, {max(all_x):.2f}]  span={max(all_x)-min(all_x):.2f}")
        print(f"  Y: [{min(all_y):.2f}, {max(all_y):.2f}]  span={max(all_y)-min(all_y):.2f}")

    # --- STRUCTURAL ANALYSIS ---
    print(f"\n{'='*90}")
    print(f"  STRUCTURAL ELEMENT IDENTIFICATION - {fname}")
    print(f"{'='*90}")

    # COLUMNS: circles or specific block inserts
    print("\n  POTENTIAL COLUMNS (circles):")
    col_candidates = []
    for c in circles:
        r = c.dxf.radius
        cx, cy = c.dxf.center.x, c.dxf.center.y
        col_candidates.append((cx, cy, r, c.dxf.layer))
    if col_candidates:
        col_candidates.sort(key=lambda c: (c[1], c[0]))
        for cx, cy, r, layer in col_candidates:
            print(f"    ({cx:.2f}, {cy:.2f}) r={r:.2f} layer={layer}")
    else:
        print("    None found.")

    # GRID/AXIS: look for long horizontal/vertical lines
    print("\n  POTENTIAL GRID/AXIS LINES (>5000 length):")
    for ln in lines:
        length = ln.dxf.start.distance(ln.dxf.end)
        if length > 5000:
            s, e = ln.dxf.start, ln.dxf.end
            print(f"    layer={ln.dxf.layer:<20} ({s.x:.2f},{s.y:.2f})->({e.x:.2f},{e.y:.2f}) len={length:.2f}")

    # TEXT near long lines (axis labels)
    print("\n  TEXT/MTEXT (potential axis labels, dimensions):")
    all_text_entities = texts + mtexts
    for t in all_text_entities:
        txt = t.dxf.text if t.dxftype() == "TEXT" else t.text
        pos = t.dxf.insert
        print(f"    ({pos.x:.2f},{pos.y:.2f}) layer={t.dxf.layer:<20} \"{txt[:80]}\"")

    print()


def main():
    for fname in FILES:
        fpath = os.path.join(PLANOS_DIR, fname)
        if not os.path.exists(fpath):
            print(f"FILE NOT FOUND: {fpath}")
            continue
        try:
            analyze_dxf(fpath)
        except Exception as exc:
            print(f"ERROR analyzing {fname}: {exc}")
            import traceback
            traceback.print_exc()
        print("\n\n")


if __name__ == "__main__":
    main()
