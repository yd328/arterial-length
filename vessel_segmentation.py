import math
import numpy as np
import voxel

INF = 10**6

def _search(volume, vessel, que):
    W, H, D = volume.shape
    region = []
    while len(que) > 0:
        cx, cy, cz = que.pop(0)
        region.append((cx, cy, cz))
        for dx, dy, dz in voxel.neighbor6():
            nx, ny, nz = cx+dx, cy+dy, cz+dz
            if (0 <= nx < W) and (0 <= ny < H) and (0 <= nz < D) and (0 < volume[nx, ny, nz]):
                vessel[nx, ny, nz] = volume[nx, ny, nz]
                volume[nx, ny, nz] = 0
                que.append((nx, ny, nz))
    return region

def extract(_volume, factor=2.7):
    volume = _volume.copy()
    W, H, D = volume.shape
    for z in range(D):
        img = volume[:,:,z]
        img[img < (np.mean(img) + factor * np.std(img))] = 0
    vessel = np.zeros(volume.shape)
    for z in range(D/2):
        for y in range(H/4, 3*H/4):
            for x in range(W/4, 3*W/4):
                if volume[x, y, z] > 0:
                    region = _search(volume, vessel, [(x, y, z)])
                    if len(region) < W + H:
                        for pos in region:
                            vessel[pos] = 0
    return vessel

def calc_length(path, spacing):
    length = 0
    for i in range(len(path)-1):
        sx, sy, sz = path[i]
        tx, ty, tz = path[i+1]
        dx, dy, dz = (tx - sx) * spacing[0], (ty - sy) * spacing[1], (tz - sz) * spacing[2]
        length += math.sqrt(dx**2 + dy**2 + dz**2)
    return length

def calc_dist(vessel, sx, sy, sz, tx, ty, tz):
    eps = 1e-5
    vessel_radius = calc_radius(vessel)
    dist = np.full(vessel.shape, INF, dtype=np.float32)
    W, H, D = vessel.shape
    xs, ys, zs = np.where(vessel > 0)
    que = [(sx, sy, sz)]
    dist[sx, sy, sz] = 0
    parent = {}
    while len(que) > 0:
        # que.sort(key=lambda pos: dist[pos])
        cx, cy, cz = que.pop(0)
        if (cx == tx) and (cy == ty) and (cz == tz):
            break
        for dx, dy, dz in voxel.neighbor26():
            nx, ny, nz = cx+dx, cy+dy, cz+dz
            d = math.sqrt(dx**2 + dy**2 + dz**2)
            if (0 <= nx < W) and (0 <= ny < H) and (0 <= nz < D) and (vessel[nx, ny, nz] > 0):
                penalty = 0
                if vessel_radius[cx, cy, cz] > vessel_radius[nx, ny, nz]:
                    penalty = 1
                elif vessel_radius[cx, cy, cz] < vessel_radius[nx, ny, nz]:
                    penalty = -1
                cost = dist[cx, cy, cz] + d + 0.8 * penalty
                if (cost + eps < dist[nx, ny, nz]):
                    dist[nx, ny, nz] = cost
                    que.append((nx, ny, nz))
                    parent[nx, ny, nz] = (cx, cy, cz)
    if not (tx, ty, tz) in parent:
        return []
    path = [(tx, ty, tz)]
    x, y, z = path[0]
    while not ((x == sx)  and (y == sy) and (z == sz)):
        x, y, z = parent[(x, y, z)]
        path.append((x, y, z))
    path.append((sx, sy, sz))
    return path[::-1]

def calc_radius(vessel):
    W, H, D = vessel.shape
    res = np.zeros(vessel.shape, dtype=np.int16)
    xs, ys, zs = np.where(vessel > 0)
    for x, y, z in zip(xs, ys, zs):
        res[x, y, z] = 1
        for d in range(1, 10):
            ok = True
            for dx, dy, dz in voxel.neighbor6():
                nx, ny, nz = x + d*dx, y + d*dy, z + d*dz
                if not ((0 <= nx < W) and (0 <= ny < H) and (0 <= nz < D)):
                    ok = False
                    break
                elif vessel[nx, ny, nz] <= 0:
                    ok = False
                    break
            if not ok:
                break
            res[x, y, z] = d
    return res

def calc_path(slices, sx, sy, sz, tx, ty, tz):
    W, H, D = slices.volume.shape
    path = []
    if (0 <= sx < W) and (0 <= sy < H) and (0 <= sz < D) and (0 <= tx < W) and (0 <= ty < H) and (0 <= tz < D):
        factor = 2.7
        for i in range(10):
            print "FACTOR = %.3f" % factor
            vessel = vessel_segmentation.extract(slices.volume, factor)
            if (vessel[sx, sy, sz] > 0) and (vessel[tx, ty, tz] > 0):
                path = vessel_segmentation.calc_dist(vessel, sx, sy, sz, tx, ty, tz)
            if len(path) > 0:
                break
            factor *= 0.96
    if len(path) > 0:
        length = vessel_segmentation.calc_length(path, slices.spacing)
    else:       
        length = -1
    result = []
    for x, y, z in path:
        result.append({
            "x": x, "y": y, "z": z,
            "sop_instance_uid": slices.mra_slices[z].SOPInstanceUID,
        })
	return {
        "length": length,
        "path": result
	}


