import math
import numpy as np
import cairosvg

W = 297.0
H = 210.0
X_MIN = 20.0
X_MAX = W - 5.0 # 292.0
Y_MIN = 5.0
Y_MAX = H - 5.0 # 205.0

STAMP_W = 185.0
STAMP_H = 55.0
STAMP_X = X_MAX - STAMP_W # 107.0
STAMP_Y = Y_MAX - STAMP_H # 150.0

def get_defs():
    return """
    <defs>
      <style>
        .thk { stroke: #000000; stroke-width: 0.65; fill: none; stroke-linecap: round; stroke-linejoin: round; }
        .thn { stroke: #000000; stroke-width: 0.22; fill: none; }
        .axs { stroke: #0066cc; stroke-width: 0.22; stroke-dasharray: 6, 2, 1, 2; fill: none; }
        .pit { stroke: #d00000; stroke-width: 0.32; stroke-dasharray: 5, 2; fill: none; }
        .dim { stroke: #000000; stroke-width: 0.2; fill: none; }
        .txt { font-family: 'DejaVu Sans', 'Arial', sans-serif; fill: #000000; }
        .txt-b { font-family: 'DejaVu Sans', 'Arial', sans-serif; font-weight: bold; fill: #000000; }
        .hatch { stroke: #444444; stroke-width: 0.22; fill: none; }
      </style>
      <pattern id="hatch-pat" width="4" height="4" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
        <line x1="0" y1="0" x2="0" y2="4" stroke="#444" stroke-width="0.3" />
      </pattern>
    </defs>
    """

def draw_arrow_line(x1, y1, x2, y2, arrow_start=True, arrow_end=True, al=2.5, aw=0.75):
    lines = [f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" class="dim" />']
    dx = x2 - x1
    dy = y2 - y1
    L = math.hypot(dx, dy)
    if L < 1e-4:
        return ""
    ux = dx / L
    uy = dy / L
    nx = -uy
    ny = ux
    if arrow_start:
        p_tip = (x1, y1)
        p_b1 = (x1 + al*ux + aw*nx, y1 + al*uy + aw*ny)
        p_b2 = (x1 + al*ux - aw*nx, y1 + al*uy - aw*ny)
        lines.append(f'<polygon points="{p_tip[0]:.2f},{p_tip[1]:.2f} {p_b1[0]:.2f},{p_b1[1]:.2f} {p_b2[0]:.2f},{p_b2[1]:.2f}" fill="#000" />')
    if arrow_end:
        p_tip = (x2, y2)
        p_b1 = (x2 - al*ux + aw*nx, y2 - al*uy + aw*ny)
        p_b2 = (x2 - al*ux - aw*nx, y2 - al*uy - aw*ny)
        lines.append(f'<polygon points="{p_tip[0]:.2f},{p_tip[1]:.2f} {p_b1[0]:.2f},{p_b1[1]:.2f} {p_b2[0]:.2f},{p_b2[1]:.2f}" fill="#000" />')
    return "\n".join(lines)

def draw_frame_and_stamp(title, line2, subtitle, part_no, material, scale_str="1:4"):
    s = []
    # Outer sheet
    s.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#ffffff" stroke="none" />')
    # Inner border
    s.append(f'<rect x="{X_MIN}" y="{Y_MIN}" width="{X_MAX - X_MIN}" height="{Y_MAX - Y_MIN}" class="thk" />')
    
    # Title block (185x55)
    x0, y0 = STAMP_X, STAMP_Y
    s.append(f'<rect x="{x0}" y="{y0}" width="{STAMP_W}" height="{STAMP_H}" class="thk" />')
    
    # Standard GOST 2.104 lines:
    s.append(f'<line x1="{x0}" y1="{y0+15}" x2="{x0+65}" y2="{y0+15}" class="thk" />')
    s.append(f'<line x1="{x0}" y1="{y0+20}" x2="{X_MAX}" y2="{y0+20}" class="thk" />')
    s.append(f'<line x1="{x0}" y1="{y0+35}" x2="{x0+65}" y2="{y0+35}" class="thk" />')
    s.append(f'<line x1="{x0}" y1="{y0+40}" x2="{X_MAX}" y2="{y0+40}" class="thk" />')
    
    for dy in [25, 30, 45, 50]:
        s.append(f'<line x1="{x0}" y1="{y0+dy}" x2="{x0+65}" y2="{y0+dy}" class="thn" />')
        
    s.append(f'<line x1="{x0+7}" y1="{y0+20}" x2="{x0+7}" y2="{Y_MAX}" class="thn" />')
    s.append(f'<line x1="{x0+17}" y1="{y0+20}" x2="{x0+17}" y2="{Y_MAX}" class="thn" />')
    s.append(f'<line x1="{x0+40}" y1="{y0+20}" x2="{x0+40}" y2="{Y_MAX}" class="thn" />')
    s.append(f'<line x1="{x0+55}" y1="{y0+20}" x2="{x0+55}" y2="{Y_MAX}" class="thn" />')
    s.append(f'<line x1="{x0+65}" y1="{y0}" x2="{x0+65}" y2="{Y_MAX}" class="thk" />')
    
    # Part number in top-right box
    s.append(f'<line x1="{x0+65}" y1="{y0+15}" x2="{X_MAX}" y2="{y0+15}" class="thk" />')
    s.append(f'<text x="{x0+125}" y="{y0+10.5}" class="txt-b" font-size="4.2px" text-anchor="middle">{part_no}</text>')
    
    # Title box (between x0+65 and x0+135, width 70mm, center at x0+100)
    s.append(f'<text x="{x0+100}" y="{y0+23.5}" class="txt-b" font-size="3.2px" text-anchor="middle">{title}</text>')
    if line2:
        s.append(f'<text x="{x0+100}" y="{y0+29}" class="txt-b" font-size="2.7px" text-anchor="middle">{line2}</text>')
    if subtitle:
        s.append(f'<text x="{x0+100}" y="{y0+34.5}" class="txt" font-size="2.2px" text-anchor="middle">{subtitle}</text>')
    
    # Material box (between x0+65 and x0+135, bottom cell, center at x0+100)
    s.append(f'<text x="{x0+100}" y="{y0+47.5}" class="txt" font-size="2.6px" text-anchor="middle">{material}</text>')
    
    # Scale and weight cells (from x0+135 to x0+185)
    s.append(f'<line x1="{x0+135}" y1="{y0+15}" x2="{x0+135}" y2="{y0+40}" class="thn" />')
    s.append(f'<line x1="{x0+150}" y1="{y0+15}" x2="{x0+150}" y2="{y0+40}" class="thn" />')
    s.append(f'<line x1="{x0+167}" y1="{y0+15}" x2="{x0+167}" y2="{y0+40}" class="thn" />')
    s.append(f'<text x="{x0+142.5}" y="{y0+19}" class="txt" font-size="2.2px" text-anchor="middle">Лит.</text>')
    s.append(f'<text x="{x0+158.5}" y="{y0+19}" class="txt" font-size="2.2px" text-anchor="middle">Масса</text>')
    s.append(f'<text x="{x0+176}" y="{y0+19}" class="txt" font-size="2.2px" text-anchor="middle">Масштаб</text>')
    s.append(f'<text x="{x0+142.5}" y="{y0+29}" class="txt-b" font-size="3.2px" text-anchor="middle">И</text>')
    s.append(f'<text x="{x0+158.5}" y="{y0+29}" class="txt" font-size="3.2px" text-anchor="middle">—</text>')
    s.append(f'<text x="{x0+176}" y="{y0+29}" class="txt-b" font-size="3.5px" text-anchor="middle">{scale_str}</text>')
    
    s.append(f'<line x1="{x0+135}" y1="{y0+40}" x2="{x0+135}" y2="{Y_MAX}" class="thn" />')
    s.append(f'<text x="{x0+150}" y="{y0+46}" class="txt" font-size="2.2px" text-anchor="middle">Лист 1</text>')
    s.append(f'<text x="{x0+170}" y="{y0+46}" class="txt" font-size="2.2px" text-anchor="middle">Листов 1</text>')
    
    labels = ["Разраб.", "Пров.", "Т. контр.", "Н. контр.", "Утв."]
    for i, lbl in enumerate(labels):
        s.append(f'<text x="{x0+2}" y="{y0+24 + i*5}" class="txt" font-size="2.2px">{lbl}</text>')
        
    return "\n".join(s)

# Load profile for supported sprocket
profile_support = np.load('/home/user/profile_df378.npy')

# Generate profile for standard sprocket (df=351.9)
Ra = 204.4
Rf_std = 351.9 / 2.0
z = 24
gamma_deg = 15.0
gamma_rad = math.radians(gamma_deg)
half_gamma = gamma_rad / 2.0
w_top = 6.97
r_tip = 1.6
r_root = 3.0
alpha = math.radians(20.0)

x_c_tip = (w_top / 2.0) - r_tip * math.tan(alpha / 2.0)
y_c_tip = Ra - r_tip
pt_top_tan_r = np.array([x_c_tip, Ra])
pt_top_tan_l = np.array([-x_c_tip, Ra])
pt_flank_tan_r = np.array([x_c_tip + r_tip * math.cos(alpha), y_c_tip + r_tip * math.sin(alpha)])
pt_flank_tan_l = np.array([-pt_flank_tan_r[0], pt_flank_tan_r[1]])
n_flank_r = np.array([math.cos(alpha), math.sin(alpha)])
d_line = np.dot(pt_flank_tan_r, n_flank_r)

val_std = (d_line + r_root) / (Rf_std + r_root)
theta_std = math.asin(val_std) - alpha
C_root_r_std = (Rf_std + r_root) * np.array([math.sin(theta_std), math.cos(theta_std)])
C_root_l_std = np.array([-C_root_r_std[0], C_root_r_std[1]])
pt_root_flank_tan_r_std = C_root_r_std - r_root * n_flank_r
pt_root_flank_tan_l_std = np.array([-pt_root_flank_tan_r_std[0], pt_root_flank_tan_r_std[1]])
pt_root_circle_tan_r_std = Rf_std * np.array([math.sin(theta_std), math.cos(theta_std)])
pt_root_circle_tan_l_std = np.array([-pt_root_circle_tan_r_std[0], pt_root_circle_tan_r_std[1]])

pts_tooth_std = []
for a in np.linspace(-half_gamma, -theta_std, 8):
    pts_tooth_std.append([Rf_std * math.sin(a), Rf_std * math.cos(a)])
ang_r_start = math.atan2(pt_root_circle_tan_l_std[1] - C_root_l_std[1], pt_root_circle_tan_l_std[0] - C_root_l_std[0])
ang_r_end = math.atan2(pt_root_flank_tan_l_std[1] - C_root_l_std[1], pt_root_flank_tan_l_std[0] - C_root_l_std[0])
for a in np.linspace(ang_r_start, ang_r_end, 8):
    pts_tooth_std.append([C_root_l_std[0] + r_root * math.cos(a), C_root_l_std[1] + r_root * math.sin(a)])
for t in np.linspace(0, 1, 8):
    pts_tooth_std.append((1-t)*pt_root_flank_tan_l_std + t*pt_flank_tan_l)
c_tip_l = np.array([-x_c_tip, y_c_tip])
ang_t_start = math.atan2(pt_flank_tan_l[1] - c_tip_l[1], pt_flank_tan_l[0] - c_tip_l[0])
ang_t_end = math.atan2(pt_top_tan_l[1] - c_tip_l[1], pt_top_tan_l[0] - c_tip_l[0])
for a in np.linspace(ang_t_start, ang_t_end, 8):
    pts_tooth_std.append([c_tip_l[0] + r_tip * math.cos(a), c_tip_l[1] + r_tip * math.sin(a)])
for t in np.linspace(0, 1, 6):
    pts_tooth_std.append((1-t)*pt_top_tan_l + t*pt_top_tan_r)
c_tip_r = np.array([x_c_tip, y_c_tip])
ang_t2_start = math.atan2(pt_top_tan_r[1] - c_tip_r[1], pt_top_tan_r[0] - c_tip_r[0])
ang_t2_end = math.atan2(pt_flank_tan_r[1] - c_tip_r[1], pt_flank_tan_r[0] - c_tip_r[0])
for a in np.linspace(ang_t2_start, ang_t2_end, 8):
    pts_tooth_std.append([c_tip_r[0] + r_tip * math.cos(a), c_tip_r[1] + r_tip * math.sin(a)])
for t in np.linspace(0, 1, 8):
    pts_tooth_std.append((1-t)*pt_flank_tan_r + t*pt_root_flank_tan_r_std)
ang_r2_start = math.atan2(pt_root_flank_tan_r_std[1] - C_root_r_std[1], pt_root_flank_tan_r_std[0] - C_root_r_std[0])
ang_r2_end = math.atan2(pt_root_circle_tan_r_std[1] - C_root_r_std[1], pt_root_circle_tan_r_std[0] - C_root_r_std[0])
for a in np.linspace(ang_r2_start, ang_r2_end, 8):
    pts_tooth_std.append([C_root_r_std[0] + r_root * math.cos(a), C_root_r_std[1] + r_root * math.sin(a)])
for a in np.linspace(theta_std, half_gamma, 8):
    pts_tooth_std.append([Rf_std * math.sin(a), Rf_std * math.cos(a)])

full_profile_std = []
for k in range(z):
    rot = k * gamma_rad
    cos_k = math.cos(rot)
    sin_k = math.sin(rot)
    for p_t in pts_tooth_std:
        rx = p_t[0] * cos_k - p_t[1] * sin_k
        ry = p_t[0] * sin_k + p_t[1] * cos_k
        full_profile_std.append([rx, ry])
profile_std = np.array(full_profile_std)


# -------------------------------------------------------------
# DRAWING 1 & 2: SPROCKETS (SUPPORT & STANDARD)
# -------------------------------------------------------------
def make_sprocket_a4(df_val, part_name, line2, part_no, sub_title, is_support=True):
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 297.0 210.0" width="297.0mm" height="210.0mm">']
    svg.append(get_defs())
    mat = "СВМПЭ РЕ-1000 / Капролон / 09Г2С"
    svg.append(draw_frame_and_stamp(part_name, line2, sub_title, part_no, mat, "1:4"))
    
    scale = 0.25
    cx, cy = 76.0, 100.0
    prof = profile_support if is_support else profile_std
    
    # Sprocket polyline
    pts_str = " ".join([f"{cx + pt[0]*scale:.2f},{cy - pt[1]*scale:.2f}" for pt in prof])
    svg.append(f'<polygon points="{pts_str}" class="thk" fill="#ffffff" />')
    
    # Pitch circle
    r_pitch_sc = (386.9 / 2.0) * scale
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_pitch_sc:.2f}" class="pit" />')
    
    # Central bore
    r_bore_sc = (75.0 / 2.0) * scale
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_bore_sc:.2f}" class="thk" fill="#ffffff" />')
    
    # Bolt holes PCD
    r_pcd_sc = (95.0 / 2.0) * scale
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_pcd_sc:.2f}" class="axs" />')
    
    # 9 bolt holes
    r_hole_sc = (9.5 / 2.0) * scale
    for i in range(9):
        ang = math.radians(90.0 - i * 40.0)
        bx = cx + r_pcd_sc * math.cos(ang)
        by = cy - r_pcd_sc * math.sin(ang)
        svg.append(f'<circle cx="{bx:.2f}" cy="{by:.2f}" r="{r_hole_sc:.2f}" class="thk" fill="#ffffff" />')
        svg.append(f'<line x1="{bx-1.8:.2f}" y1="{by:.2f}" x2="{bx+1.8:.2f}" y2="{by:.2f}" class="thn" />')
        svg.append(f'<line x1="{bx:.2f}" y1="{by-1.8:.2f}" x2="{bx:.2f}" y2="{by+1.8:.2f}" class="thn" />')
        
    # Main centerlines
    svg.append(f'<line x1="{cx - 56}" y1="{cy}" x2="{cx + 56}" y2="{cy}" class="axs" />')
    svg.append(f'<line x1="{cx}" y1="{cy - 56}" x2="{cx}" y2="{cy + 56}" class="axs" />')
    
    # Detail A circle
    r_tip_sc = (408.8 / 2.0) * scale
    svg.append(f'<circle cx="{cx}" cy="{cy - r_tip_sc}" r="7.0" class="thn" stroke-dasharray="3, 1.5" />')
    svg.append(f'<text x="{cx + 6}" y="{cy - r_tip_sc - 6}" class="txt-b" font-size="3.5px">A</text>')
    
    # Section line Б-Б
    svg.append(f'<line x1="{cx - 3.5}" y1="{cy - 53}" x2="{cx + 3.5}" y2="{cy - 53}" stroke="#000" stroke-width="0.8" />')
    svg.append(f'<line x1="{cx}" y1="{cy - 53}" x2="{cx}" y2="{cy - 49}" stroke="#000" stroke-width="0.8" />')
    svg.append(f'<text x="{cx - 4.5}" y="{cy - 50}" class="txt-b" font-size="3.8px">Б</text>')
    
    svg.append(f'<line x1="{cx - 3.5}" y1="{cy + 53}" x2="{cx + 3.5}" y2="{cy + 53}" stroke="#000" stroke-width="0.8" />')
    svg.append(f'<line x1="{cx}" y1="{cy + 53}" x2="{cx}" y2="{cy + 49}" stroke="#000" stroke-width="0.8" />')
    svg.append(f'<text x="{cx - 4.5}" y="{cy + 55}" class="txt-b" font-size="3.8px">Б</text>')
    
    # Front view dimension leaders (pointing inward towards shelf [23, 62])
    ang_da = math.radians(135.0)
    p_da_x = cx + r_tip_sc * math.cos(ang_da)
    p_da_y = cy - r_tip_sc * math.sin(ang_da)
    svg.append(f'<polyline points="{p_da_x:.2f},{p_da_y:.2f} 25.0,46.0 62.0,46.0" class="dim" />')
    svg.append(f'<text x="26.0" y="44.2" class="txt-b" font-size="2.7px">Ø 408,8 (вершины)</text>')
    
    r_root_sc = (df_val / 2.0) * scale
    ang_df = math.radians(225.0)
    p_df_x = cx + r_root_sc * math.cos(ang_df)
    p_df_y = cy - r_root_sc * math.sin(ang_df)
    svg.append(f'<polyline points="{p_df_x:.2f},{p_df_y:.2f} 25.0,154.0 62.0,154.0" class="dim" />')
    svg.append(f'<text x="26.0" y="152.2" class="txt-b" font-size="2.7px">Ø {df_val:.1f}* (впадины)</text>')
    
    ang_b = math.radians(150.0)
    p_b_x = cx + r_bore_sc * math.cos(ang_b)
    p_b_y = cy - r_bore_sc * math.sin(ang_b)
    svg.append(f'<polyline points="{p_b_x:.2f},{p_b_y:.2f} {p_b_x - 10:.2f},{p_b_y - 8:.2f} {p_b_x - 28:.2f},{p_b_y - 8:.2f}" class="dim" />')
    svg.append(f'<text x="{p_b_x - 27:.2f}" y="{p_b_y - 9.5:.2f}" class="txt-b" font-size="2.6px">Ø 75 H7 (+0,030)</text>')
    
    ang_h = math.radians(250.0)
    p_h_x = cx + r_pcd_sc * math.cos(ang_h)
    p_h_y = cy - r_pcd_sc * math.sin(ang_h)
    svg.append(f'<polyline points="{p_h_x:.2f},{p_h_y:.2f} {p_h_x - 8:.2f},{p_h_y + 16:.2f} {p_h_x + 18:.2f},{p_h_y + 16:.2f}" class="dim" />')
    svg.append(f'<text x="{p_h_x - 7:.2f}" y="{p_h_y + 14.5:.2f}" class="txt-b" font-size="2.6px">9 отв. Ø 9,5 на Ø 95</text>')
    
    # CROSS SECTION Б-Б
    sec_x = 141.0
    thk_sc = 10.0 * scale # 2.5 mm
    svg.append(f'<text x="{sec_x + thk_sc/2}" y="20.0" class="txt-b" font-size="3.8px" text-anchor="middle">Б-Б (1:4)</text>')
    svg.append(f'<line x1="{sec_x + thk_sc/2}" y1="23.0" x2="{sec_x + thk_sc/2}" y2="155.0" class="axs" />')
    
    y_top = cy - r_tip_sc
    y_top_bore = cy - r_bore_sc
    y_bot_bore = cy + r_bore_sc
    y_bot = cy + r_tip_sc
    
    # Top and bottom hatched rects
    svg.append(f'<rect x="{sec_x}" y="{y_top}" width="{thk_sc}" height="{y_top_bore - y_top}" fill="url(#hatch-pat)" class="thk" />')
    svg.append(f'<rect x="{sec_x}" y="{y_bot_bore}" width="{thk_sc}" height="{y_bot - y_bot_bore}" fill="url(#hatch-pat)" class="thk" />')
    
    # Chamfer leader on section
    svg.append(f'<polyline points="{sec_x},{y_top+2} {sec_x-8},{y_top-2} {sec_x-18},{y_top-2}" class="dim" />')
    svg.append(f'<text x="{sec_x-17}" y="{y_top-3.5}" class="txt" font-size="2.5px">2,5×15°</text>')
    
    # Thickness dimension 10 mm
    svg.append(draw_arrow_line(sec_x, y_bot + 5, sec_x + thk_sc, y_bot + 5))
    svg.append(f'<line x1="{sec_x}" y1="{y_bot + 1}" x2="{sec_x}" y2="{y_bot + 7}" class="dim" />')
    svg.append(f'<line x1="{sec_x + thk_sc}" y1="{y_bot + 1}" x2="{sec_x + thk_sc}" y2="{y_bot + 7}" class="dim" />')
    svg.append(f'<text x="{sec_x + thk_sc/2}" y="{y_bot + 10.5}" class="txt-b" font-size="2.6px" text-anchor="middle">10</text>')
    
    # DETAIL A (2:1 SCALE)
    det_scale = 2.0
    tx0 = 200.0
    ty0 = 35.0
    h_tooth = 15.20 if is_support else 28.45
    w_tip_sc = (6.97 / 2.0) * det_scale # 6.97 mm
    h_sc = h_tooth * det_scale # 30.4 mm or 56.9 mm
    y_root = ty0 + h_sc
    w_root_half = (w_tip_sc + h_sc * math.tan(math.radians(20.0)))
    
    svg.append(f'<text x="{tx0}" y="20.0" class="txt-b" font-size="3.8px" text-anchor="middle">A (2:1)</text>')
    svg.append(f'<line x1="{tx0}" y1="24.0" x2="{tx0}" y2="{y_root + 8}" class="axs" />')
    
    # Detail tooth trapezoid path
    x_root_l = tx0 - w_root_half
    x_root_r = tx0 + w_root_half
    r_tip_sc_det = 1.6 * det_scale
    r_root_sc_det = 3.0 * det_scale
    
    d_path = f"M {x_root_l - 12} {y_root} L {x_root_l} {y_root} "
    d_path += f"Q {x_root_l + r_root_sc_det*0.5} {y_root} {x_root_l + 1.2} {y_root - 3} "
    d_path += f"L {tx0 - w_tip_sc + 1.2} {ty0 + 3} "
    d_path += f"Q {tx0 - w_tip_sc} {ty0} {tx0 - w_tip_sc + 2.5} {ty0} "
    d_path += f"L {tx0 + w_tip_sc - 2.5} {ty0} "
    d_path += f"Q {tx0 + w_tip_sc} {ty0} {tx0 + w_tip_sc - 1.2} {ty0 + 3} "
    d_path += f"L {x_root_r - 1.2} {y_root - 3} "
    d_path += f"Q {x_root_r - r_root_sc_det*0.5} {y_root} {x_root_r} {y_root} "
    d_path += f"L {x_root_r + 12} {y_root}"
    svg.append(f'<path d="{d_path}" class="thk" fill="none" />')
    
    # Detail dimensions
    svg.append(draw_arrow_line(tx0 - w_tip_sc, ty0 - 3.5, tx0 + w_tip_sc, ty0 - 3.5))
    svg.append(f'<line x1="{tx0 - w_tip_sc}" y1="{ty0 - 5.5}" x2="{tx0 - w_tip_sc}" y2="{ty0 + 1}" class="dim" />')
    svg.append(f'<line x1="{tx0 + w_tip_sc}" y1="{ty0 - 5.5}" x2="{tx0 + w_tip_sc}" y2="{ty0 + 1}" class="dim" />')
    svg.append(f'<text x="{tx0}" y="{ty0 - 5.0}" class="txt-b" font-size="2.6px" text-anchor="middle">6,97</text>')
    
    x_dim_h = tx0 - w_root_half - 6.5
    svg.append(draw_arrow_line(x_dim_h, ty0, x_dim_h, y_root))
    svg.append(f'<line x1="{tx0 - w_tip_sc}" y1="{ty0}" x2="{x_dim_h - 2.5}" y2="{ty0}" class="dim" />')
    svg.append(f'<line x1="{x_root_l}" y1="{y_root}" x2="{x_dim_h - 2.5}" y2="{y_root}" class="dim" />')
    svg.append(f'<text x="{x_dim_h - 2.0}" y="{ty0 + h_sc/2 + 1.0}" class="txt-b" font-size="2.6px" text-anchor="end">{h_tooth:.2f}</text>')
    
    # Angle and radius callouts
    svg.append(f'<text x="{tx0 + w_tip_sc + 2}" y="{ty0 + 8}" class="txt" font-size="2.4px">20°</text>')
    svg.append(f'<text x="{tx0 + w_tip_sc + 1}" y="{ty0 + 4}" class="txt" font-size="2.3px">R1,6</text>')
    svg.append(f'<text x="{x_root_l - 6}" y="{y_root - 2}" class="txt" font-size="2.3px">R3</text>')
    

    
    # PARAMETER TABLE (Upper right)
    tab_x = 235.0
    tab_y = 12.0
    tab_w = 55.0
    svg.append(f'<rect x="{tab_x}" y="{tab_y}" width="{tab_w}" height="57.0" class="thk" fill="#ffffff" />')
    svg.append(f'<line x1="{tab_x}" y1="{tab_y+6}" x2="{tab_x+tab_w}" y2="{tab_y+6}" class="thk" />')
    svg.append(f'<text x="{tab_x+tab_w/2}" y="{tab_y+4.5}" class="txt-b" font-size="2.6px" text-anchor="middle">Параметры венца</text>')
    
    rows = [
        ("Число зубьев", "z", "24"),
        ("Шаг цевки", "p", "50,5 мм"),
        ("Профиль зуба", "—", "Трапеция"),
        ("Делительный Ø", "d", "386,9 мм"),
        ("Диаметр вершин", "da", "408,8 мм"),
        ("Диаметр впадин", "df", f"{df_val:.1f}* мм"),
        ("Высота зуба", "h", f"{h_tooth:.2f} мм"),
        ("Ширина венца", "b", "10 мм"),
        ("Сопряжение", "—", "Муравей"),
    ]
    svg.append(f'<line x1="{tab_x+28}" y1="{tab_y+6}" x2="{tab_x+28}" y2="{tab_y+57}" class="thn" />')
    svg.append(f'<line x1="{tab_x+35}" y1="{tab_y+6}" x2="{tab_x+35}" y2="{tab_y+57}" class="thn" />')
    for idx, r in enumerate(rows):
        ry = tab_y + 6 + (idx+1)*5.65
        if idx < len(rows) - 1:
            svg.append(f'<line x1="{tab_x}" y1="{ry}" x2="{tab_x+tab_w}" y2="{ry}" class="thn" />')
        svg.append(f'<text x="{tab_x+2}" y="{ry-1.8}" class="txt" font-size="2.1px">{r[0]}</text>')
        svg.append(f'<text x="{tab_x+31.5}" y="{ry-1.8}" class="txt" font-size="2.1px" text-anchor="middle">{r[1]}</text>')
        svg.append(f'<text x="{tab_x+tab_w-2}" y="{ry-1.8}" class="txt-b" font-size="2.1px" text-anchor="end">{r[2]}</text>')
        
    # TECHNICAL REQUIREMENTS
    tech_y = 106.0
    svg.append(f'<text x="160.0" y="{tech_y}" class="txt-b" font-size="2.8px">Технические требования:</text>')
    notes = [
        "1. *Размеры для справок.",
        "2. Неуказанные предельные отклонения: H14, h14, ±IT14/2.",
        "3. Фаски на торцах зубьев 2,5×15°.",
        "4. Затупить острые кромки R0,5...1,0 мм.",
        f"5. {'Дно впадины df=378.4 является опорным для скоб гусеницы.' if is_support else 'Дно впадины df=351.9 обеспечивает грязевой зазор снегохода.'}"
    ]
    for idx, n in enumerate(notes):
        svg.append(f'<text x="160.0" y="{tech_y + 4.2 + idx*3.8}" class="txt" font-size="2.2px">{n}</text>')
        
    svg.append('</svg>')
    return "\n".join(svg)


# -------------------------------------------------------------
# DRAWING 3: SIDE SUPPORT CHEEK ROLLER Ø 381.9 mm
# -------------------------------------------------------------
def make_cheek_a4():
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 297.0 210.0" width="297.0mm" height="210.0mm">']
    svg.append(get_defs())
    mat = "Капролон ПА-6 / Фанера ФСФ"
    svg.append(draw_frame_and_stamp("ЩЕКА ОПОРНАЯ", "Ø 381,9 мм (s = 19 мм)", "Опорный каток колеса гусеницы", "ЩО.382.019-01", mat, "1:4"))
    
    scale = 0.25
    cx, cy = 82.0, 100.0
    r_chk_sc = (381.9 / 2.0) * scale # 47.74 mm
    r_bore_sc = (75.0 / 2.0) * scale # 9.375 mm
    r_pcd_sc = (95.0 / 2.0) * scale  # 11.875 mm
    r_hole_sc = (9.5 / 2.0) * scale  # 1.1875 mm
    
    # Outer circle
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_chk_sc:.2f}" class="thk" fill="#ffffff" />')
    
    # Central bore
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_bore_sc:.2f}" class="thk" fill="#ffffff" />')
    
    # PCD circle
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_pcd_sc:.2f}" class="axs" />')
    
    # 9 bolt holes
    for i in range(9):
        ang = math.radians(90.0 - i * 40.0)
        bx = cx + r_pcd_sc * math.cos(ang)
        by = cy - r_pcd_sc * math.sin(ang)
        svg.append(f'<circle cx="{bx:.2f}" cy="{by:.2f}" r="{r_hole_sc:.2f}" class="thk" fill="#ffffff" />')
        svg.append(f'<line x1="{bx-1.6:.2f}" y1="{by:.2f}" x2="{bx+1.6:.2f}" y2="{by:.2f}" class="thn" />')
        svg.append(f'<line x1="{bx:.2f}" y1="{by-1.6:.2f}" x2="{bx:.2f}" y2="{by+1.6:.2f}" class="thn" />')
        
    # Main centerlines
    svg.append(f'<line x1="{cx - 55}" y1="{cy}" x2="{cx + 55}" y2="{cy}" class="axs" />')
    svg.append(f'<line x1="{cx}" y1="{cy - 55}" x2="{cx}" y2="{cy + 55}" class="axs" />')
    
    # Dimensions on front view
    ang_d = math.radians(60.0)
    p_d_x = cx + r_chk_sc * math.cos(ang_d)
    p_d_y = cy - r_chk_sc * math.sin(ang_d)
    svg.append(f'<polyline points="{p_d_x:.2f},{p_d_y:.2f} {p_d_x + 12:.2f},{p_d_y - 12:.2f} {p_d_x + 38:.2f},{p_d_y - 12:.2f}" class="dim" />')
    svg.append(f'<text x="{p_d_x + 13:.2f}" y="{p_d_y - 13.5:.2f}" class="txt-b" font-size="2.7px">Ø 381,9 h12 (-0,3)</text>')
    
    ang_b = math.radians(140.0)
    p_b_x = cx + r_bore_sc * math.cos(ang_b)
    p_b_y = cy - r_bore_sc * math.sin(ang_b)
    svg.append(f'<polyline points="{p_b_x:.2f},{p_b_y:.2f} {p_b_x - 12:.2f},{p_b_y - 8:.2f} {p_b_x - 30:.2f},{p_b_y - 8:.2f}" class="dim" />')
    svg.append(f'<text x="{p_b_x - 29:.2f}" y="{p_b_y - 9.5:.2f}" class="txt-b" font-size="2.6px">Ø 75 H7 (+0,030)</text>')
    
    ang_h = math.radians(240.0)
    p_h_x = cx + r_pcd_sc * math.cos(ang_h)
    p_h_y = cy - r_pcd_sc * math.sin(ang_h)
    svg.append(f'<polyline points="{p_h_x:.2f},{p_h_y:.2f} {p_h_x - 12:.2f},{p_h_y + 14:.2f} {p_h_x - 30:.2f},{p_h_y + 14:.2f}" class="dim" />')
    svg.append(f'<text x="{p_h_x - 29:.2f}" y="{p_h_y + 12.5:.2f}" class="txt-b" font-size="2.6px">9 отв. Ø 9,5 на Ø 95 (40°)</text>')
    
    # CROSS SECTION Б-Б
    sec_x = 162.0
    thk_chk_sc = 19.0 * scale # 4.75 mm
    svg.append(f'<text x="{sec_x + thk_chk_sc/2}" y="20.0" class="txt-b" font-size="3.8px" text-anchor="middle">Б-Б (1:4)</text>')
    svg.append(f'<line x1="{sec_x + thk_chk_sc/2}" y1="23.0" x2="{sec_x + thk_chk_sc/2}" y2="155.0" class="axs" />')
    
    y_top = cy - r_chk_sc
    y_top_bore = cy - r_bore_sc
    y_bot_bore = cy + r_bore_sc
    y_bot = cy + r_chk_sc
    
    svg.append(f'<rect x="{sec_x}" y="{y_top}" width="{thk_chk_sc}" height="{y_top_bore - y_top}" fill="url(#hatch-pat)" class="thk" />')
    svg.append(f'<rect x="{sec_x}" y="{y_bot_bore}" width="{thk_chk_sc}" height="{y_bot - y_bot_bore}" fill="url(#hatch-pat)" class="thk" />')
    
    # Chamfer note 3x30°
    svg.append(f'<polyline points="{sec_x},{y_top+3} {sec_x-6},{y_top-2} {sec_x-18},{y_top-2}" class="dim" />')
    svg.append(f'<text x="{sec_x-17}" y="{y_top-3.5}" class="txt" font-size="2.5px">Фаска 3×30°</text>')
    
    # Thickness dimension 19 mm
    svg.append(draw_arrow_line(sec_x, y_bot + 6, sec_x + thk_chk_sc, y_bot + 6))
    svg.append(f'<line x1="{sec_x}" y1="{y_bot + 1}" x2="{sec_x}" y2="{y_bot + 8}" class="dim" />')
    svg.append(f'<line x1="{sec_x + thk_chk_sc}" y1="{y_bot + 1}" x2="{sec_x + thk_chk_sc}" y2="{y_bot + 8}" class="dim" />')
    svg.append(f'<text x="{sec_x + thk_chk_sc/2}" y="{y_bot + 11.5}" class="txt-b" font-size="2.6px" text-anchor="middle">19</text>')
    
    # TECHNICAL REQUIREMENTS
    tech_y = 96.0
    svg.append(f'<text x="180.0" y="{tech_y}" class="txt-b" font-size="2.8px">Технические требования:</text>')
    notes = [
        "1. *Размеры для справок.",
        "2. Наружный обод Ø 381,9 мм служит опорой для гусеницы «Муравей».",
        "3. На одно опорно-ведущее колесо изготавливается 2 шт. щек.",
        "4. Заходные фаски 3×30° по наружному контуру обязательны",
        "   для предотвращения задира клыков гусеницы при поворотах.",
        "5. Допускается склеивание из двух слоев листового материала",
        "   толщиной по 9,5...10 мм (фанера ФСФ, капролон ПА-6)."
    ]
    for idx, n in enumerate(notes):
        svg.append(f'<text x="180.0" y="{tech_y + 4.5 + idx*4.0}" class="txt" font-size="2.2px">{n}</text>')
        
    svg.append('</svg>')
    return "\n".join(svg)


# -------------------------------------------------------------
# DRAWING 4: ASSEMBLY DRAWING (SANDWICH 48 mm)
# -------------------------------------------------------------
def make_assembly_a4():
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 297.0 210.0" width="297.0mm" height="210.0mm">']
    svg.append(get_defs())
    mat = "Сборочная единица"
    svg.append(draw_frame_and_stamp("КОЛЕСО ОПОРНОЕ", "В СБОРЕ (ПАКЕТ 48 мм)", "Сборочный чертеж колеса", "КОВ.24.048-СБ", mat, "1:4"))
    
    scale = 0.25
    cx, cy = 76.0, 100.0
    r_chk_sc = (381.9 / 2.0) * scale # 47.74 mm
    r_spk_sc = (408.8 / 2.0) * scale # 51.1 mm
    r_bore_sc = (75.0 / 2.0) * scale # 9.375 mm
    r_pcd_sc = (95.0 / 2.0) * scale  # 11.875 mm
    
    # Draw sprocket tooth outline in background
    pts_str = " ".join([f"{cx + pt[0]*scale:.2f},{cy - pt[1]*scale:.2f}" for pt in profile_support])
    svg.append(f'<polygon points="{pts_str}" class="thk" fill="#f8f8f8" />')
    
    # Cheek front circle
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_chk_sc:.2f}" class="thk" fill="#ffffff" stroke-width="0.75" />')
    
    # Bore circle
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_bore_sc:.2f}" class="thk" fill="#ffffff" />')
    
    # PCD circle
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_pcd_sc:.2f}" class="axs" />')
    
    # 9 bolt heads
    r_bhead_sc = (13.0 / 2.0) * scale # ~1.6 mm
    for i in range(9):
        ang = math.radians(90.0 - i * 40.0)
        bx = cx + r_pcd_sc * math.cos(ang)
        by = cy - r_pcd_sc * math.sin(ang)
        svg.append(f'<circle cx="{bx:.2f}" cy="{by:.2f}" r="{r_bhead_sc:.2f}" class="thk" fill="#ffffff" />')
        svg.append(f'<circle cx="{bx:.2f}" cy="{by:.2f}" r="{1.18}" class="thn" fill="none" />')
        svg.append(f'<line x1="{bx-2.2:.2f}" y1="{by:.2f}" x2="{bx+2.2:.2f}" y2="{by:.2f}" class="thn" />')
        svg.append(f'<line x1="{bx:.2f}" y1="{by-2.2:.2f}" x2="{bx:.2f}" y2="{by+2.2:.2f}" class="thn" />')
        
    # Main centerlines
    svg.append(f'<line x1="{cx - 56}" y1="{cy}" x2="{cx + 56}" y2="{cy}" class="axs" />')
    svg.append(f'<line x1="{cx}" y1="{cy - 56}" x2="{cx}" y2="{cy + 56}" class="axs" />')
    
    # Item balloons (Позиции 1, 2, 3)
    # Item 1: Sprocket tip
    p1_x = cx + r_spk_sc * math.cos(math.radians(75.0))
    p1_y = cy - r_spk_sc * math.sin(math.radians(75.0))
    b1_x = cx + 18.0
    b1_y = cy - 58.0
    svg.append(f'<line x1="{p1_x:.2f}" y1="{p1_y:.2f}" x2="{b1_x:.2f}" y2="{b1_y:.2f}" class="dim" />')
    svg.append(f'<circle cx="{p1_x:.2f}" cy="{p1_y:.2f}" r="0.6" fill="#000" />')
    svg.append(f'<circle cx="{b1_x:.2f}" cy="{b1_y:.2f}" r="3.2" fill="#fff" stroke="#000" stroke-width="0.35" />')
    svg.append(f'<text x="{b1_x:.2f}" y="{b1_y + 1.2:.2f}" class="txt-b" font-size="3.2px" text-anchor="middle">1</text>')
    
    # Item 2: Cheek rim
    p2_x = cx + r_chk_sc * math.cos(math.radians(55.0))
    p2_y = cy - r_chk_sc * math.sin(math.radians(55.0))
    b2_x = cx + 42.0
    b2_y = cy - 55.0
    svg.append(f'<line x1="{p2_x:.2f}" y1="{p2_y:.2f}" x2="{b2_x:.2f}" y2="{b2_y:.2f}" class="dim" />')
    svg.append(f'<circle cx="{p2_x:.2f}" cy="{p2_y:.2f}" r="0.6" fill="#000" />')
    svg.append(f'<circle cx="{b2_x:.2f}" cy="{b2_y:.2f}" r="3.2" fill="#fff" stroke="#000" stroke-width="0.35" />')
    svg.append(f'<text x="{b2_x:.2f}" y="{b2_y + 1.2:.2f}" class="txt-b" font-size="3.2px" text-anchor="middle">2</text>')
    
    # Item 3: Bolt
    ang3 = math.radians(90.0 - 5 * 40.0) # -110 deg
    p3_x = cx + r_pcd_sc * math.cos(ang3)
    p3_y = cy - r_pcd_sc * math.sin(ang3)
    b3_x = cx + 38.0
    b3_y = cy + 28.0
    svg.append(f'<line x1="{p3_x:.2f}" y1="{p3_y:.2f}" x2="{b3_x:.2f}" y2="{b3_y:.2f}" class="dim" />')
    svg.append(f'<circle cx="{p3_x:.2f}" cy="{p3_y:.2f}" r="0.6" fill="#000" />')
    svg.append(f'<circle cx="{b3_x:.2f}" cy="{b3_y:.2f}" r="3.2" fill="#fff" stroke="#000" stroke-width="0.35" />')
    svg.append(f'<text x="{b3_x:.2f}" y="{b3_y + 1.2:.2f}" class="txt-b" font-size="3.2px" text-anchor="middle">3</text>')
    
    # CROSS SECTION (SANDWICH)
    sec_x = 152.0
    w_chk = 19.0 * scale # 4.75 mm
    w_spk = 10.0 * scale # 2.5 mm
    tot_w_sc = (19.0 + 10.0 + 19.0) * scale # 12.0 mm
    
    svg.append(f'<line x1="{sec_x + tot_w_sc/2}" y1="23.0" x2="{sec_x + tot_w_sc/2}" y2="155.0" class="axs" />')
    
    # Vertical coordinates:
    y_spk_top = cy - r_spk_sc
    y_chk_top = cy - r_chk_sc
    y_bore_top = cy - r_bore_sc
    y_bore_bot = cy + r_bore_sc
    y_chk_bot = cy + r_chk_sc
    y_spk_bot = cy + r_spk_sc
    
    # Top cheek 1 (left)
    svg.append(f'<rect x="{sec_x}" y="{y_chk_top}" width="{w_chk}" height="{y_bore_top - y_chk_top}" fill="url(#hatch-pat)" class="thk" />')
    # Top center sprocket
    svg.append(f'<rect x="{sec_x + w_chk}" y="{y_spk_top}" width="{w_spk}" height="{y_bore_top - y_spk_top}" fill="#ffffff" class="thk" />')
    # Top cheek 2 (right)
    svg.append(f'<rect x="{sec_x + w_chk + w_spk}" y="{y_chk_top}" width="{w_chk}" height="{y_bore_top - y_chk_top}" fill="url(#hatch-pat)" class="thk" />')
    
    # Bottom cheek 1 (left)
    svg.append(f'<rect x="{sec_x}" y="{y_bore_bot}" width="{w_chk}" height="{y_chk_bot - y_bore_bot}" fill="url(#hatch-pat)" class="thk" />')
    # Bottom center sprocket
    svg.append(f'<rect x="{sec_x + w_chk}" y="{y_bore_bot}" width="{w_spk}" height="{y_spk_bot - y_bore_bot}" fill="#ffffff" class="thk" />')
    # Bottom cheek 2 (right)
    svg.append(f'<rect x="{sec_x + w_chk + w_spk}" y="{y_bore_bot}" width="{w_chk}" height="{y_chk_bot - y_bore_bot}" fill="url(#hatch-pat)" class="thk" />')
    
    # Bolts in cross-section
    y_bolt_top = cy - r_pcd_sc
    y_bolt_bot = cy + r_pcd_sc
    for y_b in [y_bolt_top, y_bolt_bot]:
        # Bolt shank
        svg.append(f'<rect x="{sec_x - 3.5}" y="{y_b - 1.0}" width="{tot_w_sc + 7.0}" height="2.0" fill="#ffffff" stroke="#000" stroke-width="0.3" />')
        # Bolt head
        svg.append(f'<rect x="{sec_x - 4.5}" y="{y_b - 2.5}" width="2.0" height="5.0" fill="#dddddd" stroke="#000" stroke-width="0.35" />')
        # Nut & washer
        svg.append(f'<rect x="{sec_x + tot_w_sc + 0.5}" y="{y_b - 2.5}" width="2.8" height="5.0" fill="#dddddd" stroke="#000" stroke-width="0.35" />')
        svg.append(f'<line x1="{sec_x + tot_w_sc}" y1="{y_b - 2.8}" x2="{sec_x + tot_w_sc}" y2="{y_b + 2.8}" stroke="#000" stroke-width="0.3" />')
        
    # Dimension total width 48* mm
    y_dim = y_spk_bot + 6.0
    svg.append(draw_arrow_line(sec_x, y_dim, sec_x + tot_w_sc, y_dim))
    svg.append(f'<line x1="{sec_x}" y1="{y_dim - 4}" x2="{sec_x}" y2="{y_dim + 3}" class="dim" />')
    svg.append(f'<line x1="{sec_x + tot_w_sc}" y1="{y_dim - 4}" x2="{sec_x + tot_w_sc}" y2="{y_dim + 3}" class="dim" />')
    svg.append(f'<text x="{sec_x + tot_w_sc/2}" y="{y_dim + 4.5}" class="txt-b" font-size="2.7px" text-anchor="middle">48*</text>')
    
    # SPECIFICATION TABLE (Upper right)
    sp_x = 205.0
    sp_y = 12.0
    sp_w = 85.0
    svg.append(f'<rect x="{sp_x}" y="{sp_y}" width="{sp_w}" height="42.0" class="thk" fill="#ffffff" />')
    svg.append(f'<line x1="{sp_x}" y1="{sp_y+6}" x2="{sp_x+sp_w}" y2="{sp_y+6}" class="thk" />')
    svg.append(f'<text x="{sp_x+sp_w/2}" y="{sp_y+4.5}" class="txt-b" font-size="2.6px" text-anchor="middle">Спецификация сборочной единицы</text>')
    
    svg.append(f'<line x1="{sp_x+8}" y1="{sp_y+6}" x2="{sp_x+8}" y2="{sp_y+42}" class="thn" />')
    svg.append(f'<line x1="{sp_x+56}" y1="{sp_y+6}" x2="{sp_x+56}" y2="{sp_y+42}" class="thn" />')
    svg.append(f'<line x1="{sp_x+62}" y1="{sp_y+6}" x2="{sp_x+62}" y2="{sp_y+42}" class="thn" />')
    
    items = [
        ("1", "Звездочка z=24 (10 мм)", "1", "СВМПЭ / Ст.09Г2С"),
        ("2", "Щека опорная Ø382 (19 мм)", "2", "Капролон / Фанера"),
        ("3", "Болт М8×65 ГОСТ 7798-70", "9", "Сталь 40Х"),
        ("4", "Гайка М8 ГОСТ 5915-70", "9", "Сталь 40Х"),
        ("5", "Шайба 8 ГОСТ 11371-78", "18", "Сталь 65Г"),
    ]
    for idx, it in enumerate(items):
        iy = sp_y + 6 + (idx+1)*7.2
        if idx < len(items) - 1:
            svg.append(f'<line x1="{sp_x}" y1="{iy}" x2="{sp_x+sp_w}" y2="{iy}" class="thn" />')
        svg.append(f'<text x="{sp_x+4}" y="{iy-2.4}" class="txt-b" font-size="2.2px" text-anchor="middle">{it[0]}</text>')
        svg.append(f'<text x="{sp_x+10}" y="{iy-2.4}" class="txt" font-size="2.1px">{it[1]}</text>')
        svg.append(f'<text x="{sp_x+59}" y="{iy-2.4}" class="txt-b" font-size="2.2px" text-anchor="middle">{it[2]}</text>')
        svg.append(f'<text x="{sp_x+64}" y="{iy-2.4}" class="txt" font-size="2.0px">{it[3]}</text>')
        
    # TECHNICAL REQUIREMENTS
    tech_y = 96.0
    svg.append(f'<text x="180.0" y="{tech_y}" class="txt-b" font-size="2.8px">Технические требования:</text>')
    notes = [
        "1. *Размеры для справок.",
        "2. Пакет стянуть 9 болтами М8 с моментом затяжки 18...22 Н·м.",
        "3. Резьбовые соединения зафиксировать разъемным фиксатором",
        "   резьбы (Loctite 243) или самоконтрящимися гайками с нейлоном.",
        "4. Радиальное биение наружного диаметра щек относительно",
        "   посадочного отверстия Ø 75 не более 0,5 мм.",
        "5. Общая ширина пакета 48 мм рассчитана под 50-мм коридор",
        "   клыков гусеницы «Муравей» с гарантированным зазором 1 мм на сторону."
    ]
    for idx, n in enumerate(notes):
        svg.append(f'<text x="180.0" y="{tech_y + 4.5 + idx*3.8}" class="txt" font-size="2.2px">{n}</text>')
        
    svg.append('</svg>')
    return "\n".join(svg)


# -------------------------------------------------------------
# GENERATE ALL 4 DRAWINGS (SVG, PDF, PNG)
# -------------------------------------------------------------
print("Generating Drawing 1: Supported Sprocket z=24 (df=378.4)...")
svg1 = make_sprocket_a4(378.4, "ЗВЕЗДОЧКА ОПОРНАЯ", "z = 24 (Шаг 50,5 мм)", "ЗОВ.24.378-01", "Опорное дно впадины df=378,4 мм (h=15,2 мм)", is_support=True)
with open('/home/user/sprocket_z24_support_drawing_A4.svg', 'w') as f:
    f.write(svg1)
cairosvg.svg2pdf(bytestring=svg1.encode('utf-8'), write_to='/home/user/sprocket_z24_support_drawing_A4.pdf')
cairosvg.svg2png(bytestring=svg1.encode('utf-8'), write_to='/home/user/sprocket_z24_support_drawing_A4.png', scale=4.0)

print("Generating Drawing 2: Standard Sprocket z=24 (df=351.9)...")
svg2 = make_sprocket_a4(351.9, "ЗВЕЗДОЧКА ПРИВОДНАЯ", "z = 24 (Шаг 50,5 мм)", "ЗП.24.352-01", "Грязевой зазор снегохода df=351,9 мм (h=28,45 мм)", is_support=False)
with open('/home/user/sprocket_z24_standard_drawing_A4.svg', 'w') as f:
    f.write(svg2)
cairosvg.svg2pdf(bytestring=svg2.encode('utf-8'), write_to='/home/user/sprocket_z24_standard_drawing_A4.pdf')
cairosvg.svg2png(bytestring=svg2.encode('utf-8'), write_to='/home/user/sprocket_z24_standard_drawing_A4.png', scale=4.0)

print("Generating Drawing 3: Side Support Cheek Roller Ø 381.9 mm...")
svg3 = make_cheek_a4()
with open('/home/user/cheek_d382_drawing_A4.svg', 'w') as f:
    f.write(svg3)
with open('/home/user/cheek_roller_drawing_A4.svg', 'w') as f:
    f.write(svg3)
cairosvg.svg2pdf(bytestring=svg3.encode('utf-8'), write_to='/home/user/cheek_d382_drawing_A4.pdf')
cairosvg.svg2png(bytestring=svg3.encode('utf-8'), write_to='/home/user/cheek_d382_drawing_A4.png', scale=4.0)
cairosvg.svg2png(bytestring=svg3.encode('utf-8'), write_to='/home/user/cheek_roller_drawing_A4.png', scale=4.0)

print("Generating Drawing 4: Wheel Assembly (Sandwich 48 mm)...")
svg4 = make_assembly_a4()
with open('/home/user/assembly_wheel_drawing_A4.svg', 'w') as f:
    f.write(svg4)
cairosvg.svg2pdf(bytestring=svg4.encode('utf-8'), write_to='/home/user/assembly_wheel_drawing_A4.pdf')
cairosvg.svg2png(bytestring=svg4.encode('utf-8'), write_to='/home/user/assembly_wheel_drawing_A4.png', scale=4.0)

print("ALL 4 A4 ENGINEERING DRAWINGS SUCCESSFULLY GENERATED!")
