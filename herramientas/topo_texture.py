"""Textura topográfica clara: fondo blanco, sombreado suave, curvas de nivel y mar azul pálido."""
import json, numpy as np
from PIL import Image
from scipy import ndimage
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from shapely.geometry import shape

W, S, E, N = -84.375, -5.615985819155333, -64.6875, 16.636191878397657
OUT_W, OUT_H = 4096, 4630  # ~530 m/píxel

dem = np.asarray(Image.open("/home/claude/review/data/relieve.png").convert("L")).astype(float) * 25
dem = ndimage.zoom(dem, (OUT_H / dem.shape[0], OUT_W / dem.shape[1]), order=3)
dem = ndimage.gaussian_filter(dem, 1.4)
dem[dem < 0] = 0

# sombreado (luz NO, 45°); celda ~530 m, exagerado x2 para leer el relieve
cell = (E - W) / OUT_W * 111320 * np.cos(np.radians(5))
gy, gx = np.gradient(dem * 2.0, cell)
slope = np.pi / 2 - np.arctan(np.hypot(gx, gy))
aspect = np.arctan2(-gx, gy)
az, alt = np.radians(315), np.radians(45)
shade = np.sin(alt) * np.sin(slope) + np.cos(alt) * np.cos(slope) * np.cos(az - aspect)
shade = np.clip(shade, 0, 1)

# tinte hipsométrico muy sutil (casi blanco) para que lo alto se distinga sin oscurecer
tint = LinearSegmentedColormap.from_list("t", [
    (0.00, "#FFFFFF"), (0.05, "#FDFDFA"), (0.18, "#F7F3E8"), (0.40, "#EFE7D6"), (0.65, "#E9DECB"), (1.00, "#F6F4F1")])
base = tint(np.clip(dem / 5800, 0, 1))[..., :3]
k = np.clip(1.0 + 0.75 * (shade - np.sin(alt)), 0.45, 1.06)  # plano = blanco
rgb = base * k[..., None]

fig = plt.figure(figsize=(OUT_W / 100, OUT_H / 100), dpi=100)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
ax.set_xlim(W, E); ax.set_ylim(S, N)
# mar
ax.add_patch(plt.Rectangle((W, S), E - W, N - S, color="#DDEBF2", zorder=0))
# tierra recortada por los países (línea de costa precisa)
fc = json.load(open("/home/claude/raw/ne_10m_admin_0_countries.geojson"))
from matplotlib.path import Path
from matplotlib.patches import PathPatch
verts, codes = [], []
for f in fc["features"]:
    g = shape(f["geometry"])
    if not g.intersects(shape({"type": "Polygon", "coordinates": [[[W, S], [E, S], [E, N], [W, N], [W, S]]]})): continue
    for poly in (g.geoms if g.geom_type == "MultiPolygon" else [g]):
        xy = list(poly.exterior.coords)
        verts += xy; codes += [Path.MOVETO] + [Path.LINETO] * (len(xy) - 2) + [Path.CLOSEPOLY]
land = PathPatch(Path(verts, codes), facecolor="none", edgecolor="none")
ax.add_patch(land)
im = ax.imshow(rgb, extent=(W, E, S, N), origin="upper", interpolation="bilinear", zorder=1)
im.set_clip_path(land)
# curvas de nivel: cada 250 m finas, cada 1000 m maestras
X = np.linspace(W, E, OUT_W); Y = np.linspace(N, S, OUT_H)
c1 = ax.contour(X, Y, dem, levels=[l for l in range(250, 6000, 250) if l % 1000], colors="#B89A78", linewidths=0.35, alpha=0.55, zorder=2)
c2 = ax.contour(X, Y, dem, levels=list(range(1000, 6000, 1000)), colors="#9C7650", linewidths=0.75, alpha=0.75, zorder=2)
for c in (c1, c2): c.set_clip_path(land)
# costa y fronteras
for f in fc["features"]:
    g = shape(f["geometry"])
    for poly in (g.geoms if g.geom_type == "MultiPolygon" else [g]):
        x, y = poly.exterior.xy
        col = f["properties"]["ADM0_A3"] == "COL"
        ax.plot(x, y, color="#5E8FA8", lw=0.7, zorder=3)
# frontera de Colombia más marcada
col = [f for f in fc["features"] if f["properties"]["ADM0_A3"] == "COL"][0]
g = shape(col["geometry"])
for poly in (g.geoms if g.geom_type == "MultiPolygon" else [g]):
    x, y = poly.exterior.xy; ax.plot(x, y, color="#7B6A5A", lw=1.1, ls=(0, (4, 2)), zorder=3)
fig.savefig("/home/claude/review/data/textura.jpg", dpi=100, pil_kwargs={"quality": 84})
im = Image.open("/home/claude/review/data/textura.jpg"); print(im.size)
im.crop((1500, 1300, 2500, 2300)).save("/tmp/claude-0/-home-claude/1d926d95-0395-52ae-8b9b-2263bdb89671/scratchpad/topo_zoom.jpg")
im.resize((512, 579)).save("/tmp/claude-0/-home-claude/1d926d95-0395-52ae-8b9b-2263bdb89671/scratchpad/topo_all.jpg")
import os; print(os.path.getsize("/home/claude/review/data/textura.jpg"))
