from PIL import Image, ImageDraw, ImageFilter

SS = 5                      # supersample factor
S = 180                     # final icon size (apple-touch-icon)
N = S * SS

def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def rounded(draw, box, r, fill):
    draw.rounded_rectangle(box, radius=r, fill=fill)

def make(size_out):
    img = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)

    # --- purple gradient background (full bleed; iOS adds its own rounded mask) ---
    top, bot = (181, 124, 255), (84, 47, 168)
    for y in range(N):
        dr.line([(0, y), (N, y)], fill=lerp(top, bot, y / N))

    # subtle inner vignette panel for depth
    pad = int(N * 0.10)
    panel = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    pdr = ImageDraw.Draw(panel)
    pdr.rounded_rectangle([pad, pad, N - pad, N - pad], radius=int(N * 0.18),
                          fill=(40, 22, 70, 90))
    panel = panel.filter(ImageFilter.GaussianBlur(N * 0.02))
    img.alpha_composite(panel)

    # --- tetromino (S-piece) of glossy blocks, on-theme purples/pinks ---
    cell = int(N * 0.205)
    gap = int(cell * 0.10)
    # S-piece offsets (col,row) and a cute purple-family palette
    pieces = [((1, 0), (255, 93, 158)),   # pink
              ((2, 0), (227, 160, 255)),  # lilac
              ((0, 1), (138, 92, 255)),   # violet
              ((1, 1), (192, 97, 255))]   # purple
    grid_w = 3 * cell
    grid_h = 2 * cell
    ox = (N - grid_w) // 2
    oy = (N - grid_h) // 2 + int(N * 0.03)

    # glow layer (blurred filled blocks)
    glow = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    gdr = ImageDraw.Draw(glow)
    for (cx, cy), col in pieces:
        x0 = ox + cx * cell + gap
        y0 = oy + cy * cell + gap
        x1 = ox + (cx + 1) * cell - gap
        y1 = oy + (cy + 1) * cell - gap
        gdr.rounded_rectangle([x0, y0, x1, y1], radius=int(cell * 0.28),
                              fill=col + (255,))
    glow = glow.filter(ImageFilter.GaussianBlur(N * 0.025))
    img.alpha_composite(glow)

    # solid blocks + glossy highlight
    for (cx, cy), col in pieces:
        x0 = ox + cx * cell + gap
        y0 = oy + cy * cell + gap
        x1 = ox + (cx + 1) * cell - gap
        y1 = oy + (cy + 1) * cell - gap
        rounded(dr, [x0, y0, x1, y1], int(cell * 0.28), col + (255,))
        w = x1 - x0
        dr.rounded_rectangle([x0 + w * 0.16, y0 + w * 0.14,
                              x0 + w * 0.60, y0 + w * 0.42],
                             radius=int(w * 0.18), fill=(255, 255, 255, 120))

    # --- little white heart, top-right ---
    hl = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hl)
    hx, hy, hr = int(N * 0.72), int(N * 0.26), int(N * 0.052)
    hd.ellipse([hx - hr * 2, hy - hr, hx, hy + hr], fill=(255, 255, 255, 235))
    hd.ellipse([hx, hy - hr, hx + hr * 2, hy + hr], fill=(255, 255, 255, 235))
    hd.polygon([(hx - hr * 2, hy + hr * 0.35), (hx + hr * 2, hy + hr * 0.35),
                (hx, hy + hr * 2.4)], fill=(255, 255, 255, 235))
    img.alpha_composite(hl)

    return img.resize((size_out, size_out), Image.LANCZOS)

make(S).save("apple-touch-icon.png")
make(512).save("icon-512.png")
print("wrote apple-touch-icon.png (180) and icon-512.png")
