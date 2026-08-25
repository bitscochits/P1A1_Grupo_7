#!/usr/bin/env python3
"""
Extract detailed element info and forces from the 3D benchmark model.
Load case G (dead load) only.
"""
import openseespy.opensees as ops
import math

# =============================================================================
# GEOMETRY DATA (copied from benchmark_3d.py)
# =============================================================================
X_axes = [8.02, 11.32, 14.72, 18.02, 28.02, 38.02, 48.02, 53.02]
Y_axes = [46.92, 50.26, 55.20, 60.20, 65.22, 72.75]
heights = [0.0, 4.0, 7.5, 11.0, 14.5, 18.0, 21.5, 25.0, 28.5]

nX = len(X_axes)
nY = len(Y_axes)
nLevels = len(heights)
nNodesPerFloor = nX * nY

# =============================================================================
# MATERIAL AND SECTION DATA
# =============================================================================
fpc = 28.0
Ec = 4700.0 * math.sqrt(fpc) * 1000.0
Gc = Ec / (2.0 * (1.0 + 0.2))

col_b, col_h = 0.50, 0.50
beamX_b, beamX_h = 0.30, 0.60
beamY_b, beamY_h = 0.30, 0.80
slab_t = 0.25
gamma = 25.0

A_col = col_b * col_h
Iy_col = col_b * col_h**3 / 12.0
Iz_col = col_h * col_b**3 / 12.0
J_col = min(Iy_col, Iz_col) * 0.3

A_beamX = beamX_b * beamX_h
Iy_beamX = beamX_b * beamX_h**3 / 12.0
Iz_beamX = beamX_h * beamX_b**3 / 12.0
J_beamX = min(Iy_beamX, Iz_beamX) * 0.3

A_beamY = beamY_b * beamY_h
Iy_beamY = beamY_b * beamY_h**3 / 12.0
Iz_beamY = beamY_h * beamY_b**3 / 12.0
J_beamY = min(Iy_beamY, Iz_beamY) * 0.3

w_slab_dead = gamma * slab_t + 1.5
w_live_val = 2.0

# GeomTransf vecxz vectors (same as benchmark_3d.py)
# transf 1 (columns): vecxz = (1, 0, 0)
# transf 2 (X-beams):  vecxz = (0, 0, 1)
# transf 3 (Y-beams):  vecxz = (0, 0, 1)


def build_model():
    """Build the full model (identical to benchmark_3d.py)."""
    ops.wipe()
    ops.model('basic', '-ndm', 3, '-ndf', 6)

    ops.uniaxialMaterial('Elastic', 1, Ec)

    ops.geomTransf('Linear', 1, 1, 0, 0)
    ops.geomTransf('Linear', 2, 0, 0, 1)
    ops.geomTransf('Linear', 3, 0, 0, 1)

    node_coords = {}
    nid = 1
    for lev in range(nLevels):
        z = heights[lev]
        for ix in range(nX):
            for iy in range(nY):
                node_coords[nid] = (X_axes[ix], Y_axes[iy], z)
                ops.node(nid, X_axes[ix], Y_axes[iy], z)
                nid += 1

    for i in range(1, nNodesPerFloor + 1):
        ops.fix(i, 1, 1, 1, 1, 1, 1)

    elem_counter = 1
    col_list = []
    xbeam_list = []
    ybeam_list = []

    for lev in range(nLevels - 1):
        for ix in range(nX):
            for iy in range(nY):
                bot = lev * nNodesPerFloor + ix * nY + iy + 1
                top = (lev + 1) * nNodesPerFloor + ix * nY + iy + 1
                ops.element('elasticBeamColumn', elem_counter, bot, top,
                            A_col, Ec, Gc, J_col, Iy_col, Iz_col, 1)
                col_list.append(elem_counter)
                elem_counter += 1

    for lev in range(1, nLevels):
        for ix in range(nX - 1):
            for iy in range(nY):
                n1 = lev * nNodesPerFloor + ix * nY + iy + 1
                n2 = lev * nNodesPerFloor + (ix + 1) * nY + iy + 1
                ops.element('elasticBeamColumn', elem_counter, n1, n2,
                            A_beamX, Ec, Gc, J_beamX, Iy_beamX, Iz_beamX, 2)
                xbeam_list.append(elem_counter)
                elem_counter += 1

    for lev in range(1, nLevels):
        for ix in range(nX):
            for iy in range(nY - 1):
                n1 = lev * nNodesPerFloor + ix * nY + iy + 1
                n2 = lev * nNodesPerFloor + ix * nY + (iy + 1) + 1
                ops.element('elasticBeamColumn', elem_counter, n1, n2,
                            A_beamY, Ec, Gc, J_beamY, Iy_beamY, Iz_beamY, 3)
                ybeam_list.append(elem_counter)
                elem_counter += 1

    for lev in range(1, nLevels):
        master = lev * nNodesPerFloor + 1
        for ix in range(nX):
            for iy in range(nY):
                slave = lev * nNodesPerFloor + ix * nY + iy + 1
                if slave != master:
                    ops.equalDOF(master, slave, 1, 2, 6)

    return node_coords, col_list, xbeam_list, ybeam_list


def apply_gravity(pattern_tag, use_self_weight, apply_live):
    """Apply gravity loads (identical to benchmark_3d.py)."""
    for lev in range(1, nLevels):
        for ix in range(nX - 1):
            dx = X_axes[ix + 1] - X_axes[ix]
            for iy in range(nY):
                if iy == 0:
                    tw = (Y_axes[1] - Y_axes[0]) / 2.0
                elif iy == nY - 1:
                    tw = (Y_axes[-1] - Y_axes[-2]) / 2.0
                else:
                    tw = (Y_axes[iy + 1] - Y_axes[iy - 1]) / 2.0

                w = 0.0
                if apply_live:
                    w += w_live_val * tw * 0.5
                elif use_self_weight:
                    w += w_slab_dead * tw * 0.5
                    w += gamma * beamX_b * beamX_h

                if w > 0.0:
                    n1 = lev * nNodesPerFloor + ix * nY + iy + 1
                    n2 = lev * nNodesPerFloor + (ix + 1) * nY + iy + 1
                    F = w * dx / 2.0
                    ops.load(n1, 0.0, 0.0, -F, 0.0, 0.0, 0.0)
                    ops.load(n2, 0.0, 0.0, -F, 0.0, 0.0, 0.0)

        for ix in range(nX):
            if ix == 0:
                tw = (X_axes[1] - X_axes[0]) / 2.0
            elif ix == nX - 1:
                tw = (X_axes[-1] - X_axes[-2]) / 2.0
            else:
                tw = (X_axes[ix + 1] - X_axes[ix - 1]) / 2.0

            for iy in range(nY - 1):
                dy = Y_axes[iy + 1] - Y_axes[iy]
                w = 0.0
                if apply_live:
                    w += w_live_val * tw * 0.5
                elif use_self_weight:
                    w += w_slab_dead * tw * 0.5
                    w += gamma * beamY_b * beamY_h

                if w > 0.0:
                    n1 = lev * nNodesPerFloor + ix * nY + iy + 1
                    n2 = lev * nNodesPerFloor + ix * nY + (iy + 1) + 1
                    F = w * dy / 2.0
                    ops.load(n1, 0.0, 0.0, -F, 0.0, 0.0, 0.0)
                    ops.load(n2, 0.0, 0.0, -F, 0.0, 0.0, 0.0)

    if use_self_weight:
        for lev in range(nLevels - 1):
            h = heights[lev + 1] - heights[lev]
            W = gamma * A_col * h
            for ix in range(nX):
                for iy in range(nY):
                    n_bot = lev * nNodesPerFloor + ix * nY + iy + 1
                    n_top = (lev + 1) * nNodesPerFloor + ix * nY + iy + 1
                    ops.load(n_bot, 0.0, 0.0, -W / 2.0, 0.0, 0.0, 0.0)
                    ops.load(n_top, 0.0, 0.0, -W / 2.0, 0.0, 0.0, 0.0)


def compute_local_axes(ni_coord, nj_coord, vecxz):
    """Compute local x, y, z unit vectors for a frame element."""
    def norm(v):
        return (v[0]**2 + v[1]**2 + v[2]**2) ** 0.5

    def sub(a, b):
        return (a[0]-b[0], a[1]-b[1], a[2]-b[2])

    def scale(a, s):
        return (a[0]*s, a[1]*s, a[2]*s)

    def dot(a, b):
        return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

    def cross(a, b):
        return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

    d = sub(nj_coord, ni_coord)
    n = norm(d)
    local_x = (d[0]/n, d[1]/n, d[2]/n)

    vxz = (float(vecxz[0]), float(vecxz[1]), float(vecxz[2]))
    proj = dot(vxz, local_x)
    local_z = sub(vxz, scale(local_x, proj))
    nz = norm(local_z)
    local_z = (local_z[0]/nz, local_z[1]/nz, local_z[2]/nz)

    local_y = cross(local_z, local_x)
    ny = norm(local_y)
    local_y = (local_y[0]/ny, local_y[1]/ny, local_y[2]/ny)

    return local_x, local_y, local_z


def setup_analysis():
    ops.system('BandSPD')
    ops.numberer('RCM')
    ops.constraints('Plain')
    ops.integrator('LoadControl', 1.0)
    ops.algorithm('Linear')
    ops.analysis('Static')


# =============================================================================
# MAIN
# =============================================================================
print("=" * 72)
print("EXTRACTION OF ELEMENT INFORMATION AND FORCES")
print("Load Case G (Dead Load) - Benchmark 3D Model")
print("=" * 72)
print()

print("Building model...")
node_coords, col_list, xbeam_list, ybeam_list = build_model()
total_nodes = len(node_coords)
nColumns = len(col_list)
nXbeams = len(xbeam_list)
nYbeams = len(ybeam_list)
print(f"  Nodes: {total_nodes}  |  Columns: {nColumns}  |  "
      f"X-beams: {nXbeams}  |  Y-beams: {nYbeams}")
print(f"  Total elements: {nColumns + nXbeams + nYbeams}")
print()

support_nodes = list(range(1, nNodesPerFloor + 1))

# --- Identify the 3 target elements ---
col_tag = col_list[0]       # first column: lev=0, ix=0, iy=0 -> tag 1
xbeam_tag = xbeam_list[0]   # first X-beam at level 1 -> tag 385
ybeam_tag = ybeam_list[0]   # first Y-beam at level 1 -> tag 721

print("Target elements:")
print(f"  Column  : tag {col_tag}")
print(f"  X-beam  : tag {xbeam_tag}")
print(f"  Y-beam  : tag {ybeam_tag}")
print()

# --- Run load case G ---
setup_analysis()
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)
apply_gravity(1, use_self_weight=True, apply_live=False)
ok = ops.analyze(1)
print(f"Analysis convergence: {'OK' if ok == 0 else 'FAILED'}")
ops.reactions()
print()

# =============================================================================
# HELPER: Print element details
# =============================================================================
vecxz_map = {
    'Column': (1, 0, 0),
    'X-beam': (0, 0, 1),
    'Y-beam': (0, 0, 1),
}

section_map = {
    'Column': (A_col, Iy_col, Iz_col, col_b, col_h),
    'X-beam': (A_beamX, Iy_beamX, Iz_beamX, beamX_b, beamX_h),
    'Y-beam': (A_beamY, Iy_beamY, Iz_beamY, beamY_b, beamY_h),
}

transf_map = {
    'Column': 1,
    'X-beam': 2,
    'Y-beam': 3,
}

elements_info = [
    ('Column', col_tag),
    ('X-beam', xbeam_tag),
    ('Y-beam', ybeam_tag),
]

all_element_results = []

for label, etag in elements_info:
    ni, nj = ops.eleNodes(etag)
    ci = node_coords[ni]
    cj = node_coords[nj]
    length = ((cj[0] - ci[0])**2 + (cj[1] - ci[1])**2 + (cj[2] - ci[2])**2)**0.5
    transf = transf_map[label]
    vecxz = vecxz_map[label]
    lx, ly, lz = compute_local_axes(ci, cj, vecxz)
    A_sec, Iy_sec, Iz_sec, b_sec, h_sec = section_map[label]
    forces = ops.eleForce(etag)
    fi = forces[:6]
    fj = forces[6:12]

    print("=" * 72)
    print(f"  ELEMENT: {label} (tag {etag})   |   geomTransf {transf}")
    print("=" * 72)

    print(f"\n  Nodes:  i = {ni}   j = {nj}")
    print(f"\n  Coordinates (m):")
    print(f"    Node {ni:>5d}:  x = {ci[0]:10.4f}   y = {ci[1]:10.4f}   z = {ci[2]:10.4f}")
    print(f"    Node {nj:>5d}:  x = {cj[0]:10.4f}   y = {cj[1]:10.4f}   z = {cj[2]:10.4f}")

    print(f"\n  Element length:  {length:.6f} m")

    print(f"\n  Local axes (unit vectors):")
    print(f"    vecxz = ({vecxz[0]}, {vecxz[1]}, {vecxz[2]})")
    print(f"    local x = ({lx[0]:+.10f}, {lx[1]:+.10f}, {lx[2]:+.10f})")
    print(f"    local y = ({ly[0]:+.10f}, {ly[1]:+.10f}, {ly[2]:+.10f})")
    print(f"    local z = ({lz[0]:+.10f}, {lz[1]:+.10f}, {lz[2]:+.10f})")

    print(f"\n  Cross-section properties:")
    print(f"    Section:  {b_sec*100:.0f} cm x {h_sec*100:.0f} cm")
    print(f"    A  = {A_sec:.6f} m^2")
    print(f"    Iy = {Iy_sec:.10f} m^4")
    print(f"    Iz = {Iz_sec:.10f} m^4")
    print(f"    J  = {min(Iy_sec, Iz_sec)*0.3:.10f} m^4")

    print(f"\n  Internal forces - i-end (node {ni}):")
    print(f"    P  = {fi[0]:>+14.4f} kN")
    print(f"    V2 = {fi[1]:>+14.4f} kN")
    print(f"    V3 = {fi[2]:>+14.4f} kN")
    print(f"    T  = {fi[3]:>+14.4f} kN*m")
    print(f"    M2 = {fi[4]:>+14.4f} kN*m")
    print(f"    M3 = {fi[5]:>+14.4f} kN*m")

    print(f"\n  Internal forces - j-end (node {nj}):")
    print(f"    P  = {fj[0]:>+14.4f} kN")
    print(f"    V2 = {fj[1]:>+14.4f} kN")
    print(f"    V3 = {fj[2]:>+14.4f} kN")
    print(f"    T  = {fj[3]:>+14.4f} kN*m")
    print(f"    M2 = {fj[4]:>+14.4f} kN*m")
    print(f"    M3 = {fj[5]:>+14.4f} kN*m")

    all_element_results.append((label, etag, ni, nj, length, fi, fj))
    print()

# =============================================================================
# SUPPORT REACTIONS
# =============================================================================
print("=" * 72)
print("  SUPPORT REACTIONS - Load Case G (first 4 supports)")
print("=" * 72)
print(f"  {'Node':>6s}  {'Rx (kN)':>12s}  {'Ry (kN)':>12s}  {'Rz (kN)':>12s}"
      f"  {'Mx (kN·m)':>12s}  {'My (kN·m)':>12s}  {'Mz (kN·m)':>12s}")
print("  " + "-" * 86)
for nid in support_nodes[:4]:
    rx = ops.nodeReaction(nid, 1)
    ry = ops.nodeReaction(nid, 2)
    rz = ops.nodeReaction(nid, 3)
    mx = ops.nodeReaction(nid, 4)
    my = ops.nodeReaction(nid, 5)
    mz = ops.nodeReaction(nid, 6)
    print(f"  {nid:>6d}  {rx:>+12.2f}  {ry:>+12.2f}  {rz:>+12.2f}"
          f"  {mx:>+12.2f}  {my:>+12.2f}  {mz:>+12.2f}")

print()

# Total vertical reactions across ALL supports
total_Rz = sum(ops.nodeReaction(nid, 2) for nid in support_nodes)
# Wait - for 3D model with equalDOF constraints, some reactions go to master.
# Let me get the raw reactions.
print(f"  Total vertical reaction (sum Rz of all supports): "
      f"{sum(ops.nodeReaction(nid, 3) for nid in support_nodes):.2f} kN")
print()

# =============================================================================
# SUMMARY TABLE
# =============================================================================
print("=" * 72)
print("  SUMMARY TABLE")
print("=" * 72)
header = (f"  {'Element':<10s} {'Type':<10s} {'i-j':>12s} "
          f"{'L(m)':>8s} {'P(kN)':>10s} {'V2(kN)':>10s} {'V3(kN)':>10s} "
          f"{'M2(kN·m)':>10s} {'M3(kN·m)':>10s}")
print(header)
print("  " + "-" * 96)

for label, etag, ni, nj, length, fi, fj in all_element_results:
    P_i = fi[0]
    V2_i = fi[1]
    V3_i = fi[2]
    M2_i = fi[4]
    M3_i = fi[5]
    nodes_str = f"{ni}-{nj}"
    print(f"  {etag:<10d} {label:<10s} {nodes_str:>12s} "
          f"{length:>8.3f} {P_i:>+10.2f} {V2_i:>+10.2f} {V3_i:>+10.2f} "
          f"{M2_i:>+10.2f} {M3_i:>+10.2f}")

print()
print("  Forces shown at i-end (node i).")
print("  Sign convention: P=axial(+tension), V2/V3=shear, M2/M3=moment")
print()
print("=" * 72)
print("DONE")
print("=" * 72)
