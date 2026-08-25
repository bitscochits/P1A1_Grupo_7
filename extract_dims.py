import ezdxf

fpath = r"C:\Users\edfev\OneDrive\Desktop\UAndes\noveno semestre\Métodos computacionales en obras civiles\P1\Planos\2017_67-100.dxf"
doc = ezdxf.readfile(fpath)
msp = doc.modelspace()

# Extract ALL dimension entities and their text
dims = list(msp.query("DIMENSION"))
print(f"Total DIMENSION entities: {len(dims)}\n")

for i, d in enumerate(dims):
    layer = d.dxf.layer
    # Try to get dimension text
    dimtext = ""
    if d.dxf.hasattr('dimtext'):
        dimtext = d.dxf.dimtext
    
    # Get points
    defpt = None
    defpt2 = None
    defpt3 = None
    if d.dxf.hasattr('defpoint'):
        defpt = (d.dxf.defpoint.x, d.dxf.defpoint.y)
    if d.dxf.hasattr('defpoint2'):
        defpt2 = (d.dxf.defpoint2.x, d.dxf.defpoint2.y)
    if d.dxf.hasattr('defpoint3'):
        defpt3 = (d.dxf.defpoint3.x, d.dxf.defpoint3.y)
    
    # Compute distance if possible
    dist = None
    if defpt and defpt2:
        dx = defpt2[0] - defpt[0]
        dy = defpt2[1] - defpt[1]
        dist = (dx**2 + dy**2)**0.5
    
    print(f"[{i:3d}] layer={layer:<20} dimtext=\"{dimtext}\" defpt={defpt} defpt2={defpt2} dist={dist:.2f}" if dist else f"[{i:3d}] layer={layer:<20} dimtext=\"{dimtext}\" defpt={defpt}")

# Also extract beam labels
print("\n--- BEAM LABELS (text with '/') ---")
texts = list(msp.query("TEXT"))
mtexts = list(msp.query("MTEXT"))
for t in texts:
    if '/' in t.dxf.text:
        print(f"  ({t.dxf.insert.x:.1f},{t.dxf.insert.y:.1f}) layer={t.dxf.layer} \"{t.dxf.text}\"")
for mt in mtexts:
    txt = mt.text.replace('\n', ' ')
    if '/' in txt:
        print(f"  ({mt.dxf.insert.x:.1f},{mt.dxf.insert.y:.1f}) layer={mt.dxf.layer} \"{txt[:100]}\"")

# Extract column-related text
print("\n--- COLUMN/WALL TEXT ---")
for t in texts:
    txt = t.dxf.text.upper()
    if any(k in txt for k in ['PILAR', 'COL', 'MURO', 'h=', 'H=', 'LOSA', 'EJE']):
        print(f"  ({t.dxf.insert.x:.1f},{t.dxf.insert.y:.1f}) layer={t.dxf.layer} \"{t.dxf.text}\"")
for mt in mtexts:
    txt = mt.text.replace('\n', ' ').upper()
    if any(k in txt for k in ['PILAR', 'COL', 'MURO', 'h=', 'H=', 'LOSA', 'EJE']):
        print(f"  ({mt.dxf.insert.x:.1f},{mt.dxf.insert.y:.1f}) layer={mt.dxf.layer} \"{mt.text[:100]}\"")

# Grid axis circles - group by position
print("\n--- AXIS BUBBLES (RLE-EJE) ---")
circles = list(msp.query("CIRCLE"))
axis_circles = [c for c in circles if c.dxf.layer == "RLE-EJE"]
print(f"Total axis bubbles: {len(axis_circles)}")

# Group by approximate X (vertical axes)
x_groups = {}
for c in axis_circles:
    x = round(c.dxf.center.x, -1)  # round to nearest 10
    x_groups.setdefault(x, []).append((c.dxf.center.x, c.dxf.center.y))

print("\nVertical axes (grouped by X):")
for x in sorted(x_groups.keys()):
    pts = sorted(x_groups[x], key=lambda p: p[1])
    print(f"  X~{x:.0f}: {[(f'{px:.1f},{py:.1f}') for px,py in pts]}")

# Group by approximate Y (horizontal axes)
y_groups = {}
for c in axis_circles:
    y = round(c.dxf.center.y, -1)
    y_groups.setdefault(y, []).append((c.dxf.center.x, c.dxf.center.y))

print("\nHorizontal axes (grouped by Y):")
for y in sorted(y_groups.keys()):
    pts = sorted(y_groups[y], key=lambda p: p[0])
    print(f"  Y~{y:.0f}: {[(f'{px:.1f},{py:.1f}') for px,py in pts]}")
