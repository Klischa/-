import math
import numpy as np
import cairosvg
from pypdf import PdfWriter, PdfReader
import io
import os

# Sprocket geometry
Ra = 204.4
Rf = 351.9 / 2.0 # 175.95
Rp = 386.9 / 2.0 # 193.45
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

val = (d_line + r_root) / (Rf + r_root)
theta_plus_alpha = math.asin(val)
theta_c = theta_plus_alpha - alpha

C_root_r = (Rf + r_root) * np.array([math.sin(theta_c), math.cos(theta_c)])
C_root_l = np.array([-C_root_r[0], C_root_r[1]])

pt_root_flank_tan_r = C_root_r - r_root * n_flank_r
pt_root_flank_tan_l = np.array([-pt_root_flank_tan_r[0], pt_root_flank_tan_r[1]])

pt_root_circle_tan_r = Rf * np.array([math.sin(theta_c), math.cos(theta_c)])
pt_root_circle_tan_l = np.array([-pt_root_circle_tan_r[0], pt_root_circle_tan_r[1]])

pts_tooth = []
for a in np.linspace(-half_gamma, -theta_c, 8):
    pts_tooth.append([Rf * math.sin(a), Rf * math.cos(a)])
ang_r_start = math.atan2(pt_root_circle_tan_l[1] - C_root_l[1], pt_root_circle_tan_l[0] - C_root_l[0])
ang_r_end = math.atan2(pt_root_flank_tan_l[1] - C_root_l[1], pt_root_flank_tan_l[0] - C_root_l[0])
for a in np.linspace(ang_r_start, ang_r_end, 8):
    pts_tooth.append([C_root_l[0] + r_root * math.cos(a), C_root_l[1] + r_root * math.sin(a)])
for t in np.linspace(0, 1, 8):
    pts_tooth.append((1-t)*pt_root_flank_tan_l + t*pt_flank_tan_l)
c_tip_l = np.array([-x_c_tip, y_c_tip])
ang_t_start = math.atan2(pt_flank_tan_l[1] - c_tip_l[1], pt_flank_tan_l[0] - c_tip_l[0])
ang_t_end = math.atan2(pt_top_tan_l[1] - c_tip_l[1], pt_top_tan_l[0] - c_tip_l[0])
for a in np.linspace(ang_t_start, ang_t_end, 8):
    pts_tooth.append([c_tip_l[0] + r_tip * math.cos(a), c_tip_l[1] + r_tip * math.sin(a)])
for t in np.linspace(0, 1, 6):
    pts_tooth.append((1-t)*pt_top_tan_l + t*pt_top_tan_r)
c_tip_r = np.array([x_c_tip, y_c_tip])
ang_t2_start = math.atan2(pt_top_tan_r[1] - c_tip_r[1], pt_top_tan_r[0] - c_tip_r[0])
ang_t2_end = math.atan2(pt_flank_tan_r[1] - c_tip_r[1], pt_flank_tan_r[0] - c_tip_r[0])
for a in np.linspace(ang_t2_start, ang_t2_end, 8):
    pts_tooth.append([c_tip_r[0] + r_tip * math.cos(a), c_tip_r[1] + r_tip * math.sin(a)])
for t in np.linspace(0, 1, 8):
    pts_tooth.append((1-t)*pt_flank_tan_r + t*pt_root_flank_tan_r)
ang_r2_start = math.atan2(pt_root_flank_tan_r[1] - C_root_r[1], pt_root_flank_tan_r[0] - C_root_r[0])
ang_r2_end = math.atan2(pt_root_circle_tan_r[1] - C_root_r[1], pt_root_circle_tan_r[0] - C_root_r[0])
for a in np.linspace(ang_r2_start, ang_r2_end, 8):
    pts_tooth.append([C_root_r[0] + r_root * math.cos(a), C_root_r[1] + r_root * math.sin(a)])
for a in np.linspace(theta_c, half_gamma, 8):
    pts_tooth.append([Rf * math.sin(a), Rf * math.cos(a)])

full_profile = []
for k in range(z):
    rot = k * gamma_rad
    cos_k = math.cos(rot)
    sin_k = math.sin(rot)
    for p_t in pts_tooth:
        rx = p_t[0] * cos_k + p_t[1] * sin_k
        ry = -p_t[0] * sin_k + p_t[1] * cos_k
        full_profile.append([rx, ry])
full_profile = np.array(full_profile)

r_bolt = 47.5
bolt_holes = []
for i in range(9):
    ang = math.radians(90.0 - i * 40.0)
    bx = r_bolt * math.cos(ang)
    by = r_bolt * math.sin(ang)
    bolt_holes.append((bx, by))

tooth_labels = []
for k in range(z):
    ang = math.radians(90.0 - k * 15.0)
    tx = (Ra + 8.5) * math.cos(ang)
    ty = (Ra + 8.5) * math.sin(ang)
    tooth_labels.append((tx, ty, k + 1))

# Common SVG defs for A4 sheets
def get_svg_defs():
    return '''<defs>
      <style>
        .cut-line { stroke: #000; stroke-width: 0.8; fill: none; stroke-linecap: round; stroke-linejoin: round; }
        .thin-line { stroke: #000; stroke-width: 0.3; fill: none; }
        .red-pitch { stroke: #d00; stroke-width: 0.35; stroke-dasharray: 8, 2, 2, 2; fill: none; }
        .blue-axis { stroke: #0066cc; stroke-width: 0.3; stroke-dasharray: 10, 2, 2, 2; fill: none; }
        .dashed-seam { stroke: #ff6600; stroke-width: 0.4; stroke-dasharray: 4, 3; fill: none; }
        .dashed-grey { stroke: #777; stroke-width: 0.25; stroke-dasharray: 3, 2; fill: none; }
        .crosshair { stroke: #ff6600; stroke-width: 0.4; fill: none; }
        text { font-family: 'DejaVu Sans', Arial, sans-serif; font-style: normal; }
        .txt-head { font-size: 4.5px; font-weight: bold; fill: #000; }
        .txt-main { font-size: 3.2px; fill: #000; }
        .txt-num { font-size: 3.8px; font-weight: bold; fill: #d00; }
        .txt-seam { font-size: 2.6px; fill: #ff6600; font-weight: bold; }
        .txt-scale { font-size: 2.5px; fill: #000; }
      </style>
    </defs>'''

def draw_calibration_ruler(x, y, length_mm=100):
    lines = []
    lines.append(f'<rect x="{x}" y="{y}" width="{length_mm}" height="5" fill="#fcfcfc" stroke="#000" stroke-width="0.3" />')
    for m in range(length_mm + 1):
        if m % 10 == 0:
            h_tick = 5.0
            lines.append(f'<line x1="{x+m}" y1="{y}" x2="{x+m}" y2="{y+h_tick}" class="thin-line" stroke-width="0.35" />')
            if m > 0:
                lines.append(f'<text x="{x+m}" y="{y-1.5}" class="txt-scale" text-anchor="middle">{m}</text>')
        elif m % 5 == 0:
            h_tick = 3.2
            lines.append(f'<line x1="{x+m}" y1="{y}" x2="{x+m}" y2="{y+h_tick}" class="thin-line" />')
        else:
            h_tick = 1.8
            lines.append(f'<line x1="{x+m}" y1="{y}" x2="{x+m}" y2="{y+h_tick}" class="thin-line" stroke-width="0.2" />')
    lines.append(f'<text x="{x}" y="{y-1.5}" class="txt-scale" text-anchor="middle">0 мм</text>')
    lines.append(f'<text x="{x + length_mm/2}" y="{y + 9}" class="txt-scale" text-anchor="middle" font-weight="bold">КОНТРОЛЬНАЯ ШКАЛА 100 мм (ПРОВЕРКА МАСШТАБА 1:1)</text>')
    return "\n".join(lines)

def draw_registration_mark(cx, cy):
    # Crosshair with concentric circle
    return f'''
    <circle cx="{cx}" cy="{cy}" r="3.5" class="crosshair" />
    <line x1="{cx-5}" y1="{cy}" x2="{cx+5}" y2="{cy}" class="crosshair" />
    <line x1="{cx}" y1="{cy-5}" x2="{cx}" y2="{cy+5}" class="crosshair" />
    '''

print("Helper functions ready")
