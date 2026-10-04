import math
import numpy as np
import cairosvg
from pypdf import PdfWriter, PdfReader
import io

from build_all_a4 import get_svg_defs, draw_calibration_ruler

W_A4 = 210.0
H_A4 = 297.0

# Load full profile points for df = 378.4 mm
profile_df378 = np.load('/home/user/profile_df378.npy')

z = 24
p = 50.5
Rp = p / (2 * math.sin(math.pi / z)) # 193.45 mm
Ra = 408.8 / 2.0                    # 204.40 mm
Rf_sup = 378.4 / 2.0                # 189.20 mm

# 9 bolt holes
bolt_holes = []
for i in range(9):
    ang = i * (2 * math.pi / 9)
    bolt_holes.append((47.5 * math.cos(ang), 47.5 * math.sin(ang)))

tooth_labels = []
for i in range(z):
    ang = math.pi / 2.0 - i * (2 * math.pi / z)
    tx = (Ra + 10.0) * math.cos(ang)
    ty = (Ra + 10.0) * math.sin(ang)
    num = (i % z) + 1
    tooth_labels.append((tx, ty, num))

# -------------------------------------------------------------
# 1. SECTOR TEMPLATE A4 FOR SUPPORTED SPROCKET (60° / 4 TEETH, 1:1)
# -------------------------------------------------------------
def make_sector_support_svg():
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W_A4} {H_A4}" width="{W_A4}mm" height="{H_A4}mm">')
    svg.append(get_svg_defs())
    svg.append(f'<rect x="0" y="0" width="{W_A4}" height="{H_A4}" fill="#ffffff" />')
    svg.append(f'<rect x="6" y="6" width="{W_A4-12}" height="{H_A4-12}" fill="none" stroke="#ccc" stroke-width="0.3" stroke-dasharray="2, 2" />')
    
    # Header
    svg.append(f'<text x="{W_A4/2}" y="13" class="txt-head" text-anchor="middle" font-size="4.2px">ШАБЛОН-СЕКТОР ЗВЕЗДЫ С ОПОРНЫМ ДНОМ df=378.4 мм — 1:1</text>')
    svg.append(f'<text x="{W_A4/2}" y="18" class="txt-main" text-anchor="middle" fill="#0066cc">Скоба гусеницы «Муравей» садится прямо на дно впадины (6 поворотов на 60° вокруг центра Ø75)</text>')
    svg.append(f'<line x1="10" y1="21" x2="{W_A4-10}" y2="21" stroke="#aaa" stroke-width="0.4" />')
    
    x_c = W_A4 / 2.0 # 105 mm
    y_c = 240.0      # center origin
    
    ang_l = math.radians(120.0)
    ang_r = math.radians(60.0)
    ray_l_end = (x_c + Ra * math.cos(ang_l), y_c - Ra * math.sin(ang_l))
    ray_r_end = (x_c + Ra * math.cos(ang_r), y_c - Ra * math.sin(ang_r))
    
    def make_arc(r, a_start_deg=130.0, a_end_deg=50.0, css_class="thin-line", extra_attr=""):
        rad_s = math.radians(a_start_deg)
        rad_e = math.radians(a_end_deg)
        x1 = x_c + r * math.cos(rad_s)
        y1 = y_c - r * math.sin(rad_s)
        x2 = x_c + r * math.cos(rad_e)
        y2 = y_c - r * math.sin(rad_e)
        return f'<path d="M {x1:.2f} {y1:.2f} A {r:.2f} {r:.2f} 0 0 1 {x2:.2f} {y2:.2f}" class="{css_class}" {extra_attr} />'

    svg.append(make_arc(Rp, 130.0, 50.0, "red-pitch"))
    svg.append(make_arc(Rf_sup, 130.0, 50.0, "dashed-grey"))
    svg.append(make_arc(47.5, 135.0, 45.0, "blue-axis"))
    svg.append(make_arc(37.5, 140.0, 40.0, "thin-line", 'stroke-width="0.5" fill="none"'))
    
    r_hub = 37.5
    h_s_x = x_c + r_hub * math.cos(ang_l)
    h_s_y = y_c - r_hub * math.sin(ang_l)
    h_e_x = x_c + r_hub * math.cos(ang_r)
    h_e_y = y_c - r_hub * math.sin(ang_r)
    svg.append(f'<path d="M {x_c} {y_c} L {h_s_x:.2f} {h_s_y:.2f} A {r_hub} {r_hub} 0 0 1 {h_e_x:.2f} {h_e_y:.2f} Z" fill="#f0f7ff" stroke="#0066cc" stroke-width="0.4" stroke-dasharray="2, 1" />')
    
    for bx, by in bolt_holes:
        ang = math.atan2(by, bx)
        if math.radians(45.0) <= ang <= math.radians(135.0):
            pg_bx = x_c + bx
            pg_by = y_c - by
            svg.append(f'<circle cx="{pg_bx:.3f}" cy="{pg_by:.3f}" r="4.75" class="thin-line" stroke-width="0.5" fill="#fff" />')
            svg.append(f'<circle cx="{pg_bx:.3f}" cy="{pg_by:.3f}" r="0.4" fill="#000" />')
            
    # Center cross
    svg.append(f'<line x1="{x_c-12}" y1="{y_c}" x2="{x_c+12}" y2="{y_c}" class="cut-line" stroke-width="0.5" />')
    svg.append(f'<line x1="{x_c}" y1="{y_c-12}" x2="{x_c}" y2="{y_c+12}" class="cut-line" stroke-width="0.5" />')
    svg.append(f'<circle cx="{x_c}" cy="{y_c}" r="1.3" fill="#d00" />')
    svg.append(f'<text x="{x_c}" y="{y_c + 6}" font-size="2.4px" text-anchor="middle" font-weight="bold">ЦЕНТР ЗВЕЗДЫ (0,0)</text>')
    
    # Sector rays
    svg.append(f'<line x1="{x_c}" y1="{y_c}" x2="{ray_l_end[0]:.2f}" y2="{ray_l_end[1]:.2f}" class="dashed-seam" stroke-width="0.6" />')
    svg.append(f'<line x1="{x_c}" y1="{y_c}" x2="{ray_r_end[0]:.2f}" y2="{ray_r_end[1]:.2f}" class="dashed-seam" stroke-width="0.6" />')
    svg.append(f'<text x="{ray_l_end[0] - 2:.2f}" y="{ray_l_end[1] + 6:.2f}" class="txt-seam">ЛУЧ 60° (ЛИНИЯ ПОВОРОТА)</text>')
    svg.append(f'<text x="{ray_r_end[0] + 2:.2f}" y="{ray_r_end[1] + 6:.2f}" class="txt-seam" text-anchor="end">ЛУЧ 60°</text>')
    
    # Filter points for angle [53°, 127°]
    sec_points = []
    for pt in profile_df378:
        ang = math.atan2(pt[1], pt[0])
        ang_deg = math.degrees(ang)
        if 53.0 <= ang_deg <= 127.0:
            sec_points.append((ang_deg, pt[0], pt[1]))
            
    sec_points.sort(key=lambda item: -item[0])
    pts_d = [(x_c + pt[1], y_c - pt[2]) for pt in sec_points]
    if len(pts_d) > 0:
        path_str = "M " + " L ".join([f"{p[0]:.2f} {p[1]:.2f}" for p in pts_d])
        svg.append(f'<path d="{path_str}" class="cut-line" stroke-width="0.8" />')
        
    for tx, ty, num in tooth_labels:
        ang = math.degrees(math.atan2(ty, tx))
        if 56.0 <= ang <= 124.0:
            pg_tx = x_c + tx
            pg_ty = y_c - ty
            svg.append(f'<circle cx="{pg_tx:.2f}" cy="{pg_ty:.2f}" r="3.2" fill="#fff" stroke="#d00" stroke-width="0.3" />')
            svg.append(f'<text x="{pg_tx:.2f}" y="{pg_ty + 1.2:.2f}" class="txt-num" text-anchor="middle">{num}</text>')
            
    # Instructions Box
    inst_y = H_A4 - 42.0
    svg.append(f'<rect x="12" y="{inst_y}" width="186" height="23" fill="#f4f8fb" stroke="#0066cc" stroke-width="0.4" rx="2" />')
    svg.append(f'<text x="16" y="{inst_y + 5.0}" class="txt-main" font-weight="bold" fill="#0066cc">ОСОБЕННОСТЬ ЗВЕЗДЫ С ОПОРНЫМ ДНОМ (df = 378.4 мм):</text>')
    svg.append(f'<text x="16" y="{inst_y + 9.2}" font-size="2.4px" fill="#222">• Высота зуба составляет 15.2 мм (вершина выступает сквозь окно гусеницы на 7.0 мм).</text>')
    svg.append(f'<text x="16" y="{inst_y + 13.2}" font-size="2.4px" fill="#222">• Скоба гусеницы ложится прямо на дно впадины без зазора — колесо несет вес техники.</text>')
    svg.append(f'<text x="16" y="{inst_y + 17.2}" font-size="2.4px" fill="#222">• Разметка: закрепить центр (0,0), обвести 4 зуба, повернуть на 60°, повторить 6 раз (всего 24 зуба).</text>')
    svg.append(f'<text x="16" y="{inst_y + 21.0}" font-size="2.4px" fill="#222">• Материал: листовой СВМПЭ / капролон / фанера / сталь толщиной 10 мм.</text>')
    
    # Calibration ruler
    svg.append(draw_calibration_ruler(x=12, y=H_A4 - 15, length_mm=100))
    svg.append(f'<text x="{W_A4 - 12}" y="{H_A4 - 9}" class="txt-scale" text-anchor="end" font-weight="bold">Масштаб 1:1 (100%)</text>')
    
    svg.append('</svg>')
    return "\n".join(svg)

# -------------------------------------------------------------
# 2. SECTOR TEMPLATE A4 FOR CHEEK ROLLER Ø381.9 mm (60°, 1:1)
# -------------------------------------------------------------
def make_cheek_sector_svg():
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W_A4} {H_A4}" width="{W_A4}mm" height="{H_A4}mm">')
    svg.append(get_svg_defs())
    svg.append(f'<rect x="0" y="0" width="{W_A4}" height="{H_A4}" fill="#ffffff" />')
    svg.append(f'<rect x="6" y="6" width="{W_A4-12}" height="{H_A4-12}" fill="none" stroke="#ccc" stroke-width="0.3" stroke-dasharray="2, 2" />')
    
    # Header
    svg.append(f'<text x="{W_A4/2}" y="13" class="txt-head" text-anchor="middle" font-size="4.2px">ШАБЛОН-СЕКТОР БОКОВОЙ ОПОРНОЙ ЩЕКИ Ø 381.9 мм — 1:1</text>')
    svg.append(f'<text x="{W_A4/2}" y="18" class="txt-main" text-anchor="middle" fill="#008800">Опорный каток под резиновую дорожку гусеницы «Муравей» (2 шт. на 1 колесо, толщина 19 мм)</text>')
    svg.append(f'<line x1="10" y1="21" x2="{W_A4-10}" y2="21" stroke="#aaa" stroke-width="0.4" />')
    
    x_c = W_A4 / 2.0 # 105 mm
    y_c = 240.0      # center origin
    R_cheek = 381.9 / 2.0 # 190.95 mm
    
    ang_l = math.radians(120.0)
    ang_r = math.radians(60.0)
    ray_l_end = (x_c + R_cheek * math.cos(ang_l), y_c - R_cheek * math.sin(ang_l))
    ray_r_end = (x_c + R_cheek * math.cos(ang_r), y_c - R_cheek * math.sin(ang_r))
    
    # Outer cylindrical arc of cheek
    x_arc_s = x_c + R_cheek * math.cos(math.radians(125.0))
    y_arc_s = y_c - R_cheek * math.sin(math.radians(125.0))
    x_arc_e = x_c + R_cheek * math.cos(math.radians(55.0))
    y_arc_e = y_c - R_cheek * math.sin(math.radians(55.0))
    svg.append(f'<path d="M {x_arc_s:.2f} {y_arc_s:.2f} A {R_cheek} {R_cheek} 0 0 1 {x_arc_e:.2f} {y_arc_e:.2f}" class="cut-line" stroke-width="1.0" stroke="#008800" />')
    
    # Center bore & PCD
    svg.append(f'<circle cx="{x_c}" cy="{y_c}" r="47.5" class="blue-axis" />')
    svg.append(f'<circle cx="{x_c}" cy="{y_c}" r="37.5" class="thin-line" stroke-width="0.5" fill="#f0fff0" />')
    
    for bx, by in bolt_holes:
        ang = math.atan2(by, bx)
        if math.radians(45.0) <= ang <= math.radians(135.0):
            pg_bx = x_c + bx
            pg_by = y_c - by
            svg.append(f'<circle cx="{pg_bx:.3f}" cy="{pg_by:.3f}" r="4.75" class="thin-line" stroke-width="0.5" fill="#fff" />')
            svg.append(f'<circle cx="{pg_bx:.3f}" cy="{pg_by:.3f}" r="0.4" fill="#000" />')
            
    # Center cross
    svg.append(f'<line x1="{x_c-12}" y1="{y_c}" x2="{x_c+12}" y2="{y_c}" class="cut-line" stroke-width="0.5" />')
    svg.append(f'<line x1="{x_c}" y1="{y_c-12}" x2="{x_c}" y2="{y_c+12}" class="cut-line" stroke-width="0.5" />')
    svg.append(f'<circle cx="{x_c}" cy="{y_c}" r="1.3" fill="#008800" />')
    svg.append(f'<text x="{x_c}" y="{y_c + 6}" font-size="2.4px" text-anchor="middle" font-weight="bold">ЦЕНТР ЩЕКИ (0,0)</text>')
    
    # Sector rays
    svg.append(f'<line x1="{x_c}" y1="{y_c}" x2="{ray_l_end[0]:.2f}" y2="{ray_l_end[1]:.2f}" class="dashed-seam" stroke-width="0.6" stroke="#008800" />')
    svg.append(f'<line x1="{x_c}" y1="{y_c}" x2="{ray_r_end[0]:.2f}" y2="{ray_r_end[1]:.2f}" class="dashed-seam" stroke-width="0.6" stroke="#008800" />')
    svg.append(f'<text x="{ray_l_end[0] - 2:.2f}" y="{ray_l_end[1] + 6:.2f}" class="txt-seam" fill="#008800">ЛУЧ 60° (ЛИНИЯ РАЗМЕТКИ)</text>')
    svg.append(f'<text x="{ray_r_end[0] + 2:.2f}" y="{ray_r_end[1] + 6:.2f}" class="txt-seam" fill="#008800" text-anchor="end">ЛУЧ 60°</text>')
    
    # Callout on outer rim
    svg.append(f'<text x="{x_c}" y="{y_c - R_cheek - 4}" font-size="3.2px" text-anchor="middle" font-weight="bold" fill="#008800">НАРУЖНЫЙ ОПОРНЫЙ ОБОД Ø 381.9 мм (ПОД ПОЛОТНО ГУСЕНИЦЫ)</text>')
    
    # Instructions Box
    inst_y = H_A4 - 42.0
    svg.append(f'<rect x="12" y="{inst_y}" width="186" height="23" fill="#f4faf4" stroke="#008800" stroke-width="0.4" rx="2" />')
    svg.append(f'<text x="16" y="{inst_y + 5.0}" class="txt-main" font-weight="bold" fill="#008800">КАК ИЗГОТОВИТЬ ОПОРНУЮ ЩЕКУ ПО ДАННОМУ ШАБЛОНУ:</text>')
    svg.append(f'<text x="16" y="{inst_y + 9.2}" font-size="2.4px" fill="#222">• Требуется 2 щеки на одно колесо. Толщина каждой щеки 18...19 мм (или склеить из двух слоев по 9.5-10 мм).</text>')
    svg.append(f'<text x="16" y="{inst_y + 13.2}" font-size="2.4px" fill="#222">• Разметка: закрепить центр (0,0) в заготовке, очертить дугу 60°, повернуть 6 раз -> замкнутый круг Ø381.9 мм.</text>')
    svg.append(f'<text x="16" y="{inst_y + 17.2}" font-size="2.4px" fill="#222">• Просверлить центр Ø 75 мм и 9 отверстий Ø 9.5 мм на Ø 95 мм (совпадают со звездой).</text>')
    svg.append(f'<text x="16" y="{inst_y + 21.0}" font-size="2.4px" fill="#222">• По наружной кромке снять фаску 3×30° для легкого центрирования между клыками гусеницы.</text>')
    
    # Calibration ruler
    svg.append(draw_calibration_ruler(x=12, y=H_A4 - 15, length_mm=100))
    svg.append(f'<text x="{W_A4 - 12}" y="{H_A4 - 9}" class="txt-scale" text-anchor="end" font-weight="bold">Масштаб 1:1 (100%)</text>')
    
    svg.append('</svg>')
    return "\n".join(svg)

# Save Sector SVGs, PDFs, PNGs
sec_sup_svg = make_sector_support_svg()
with open('/home/user/sprocket_z24_support_sector_1to1.svg', 'w') as f:
    f.write(sec_sup_svg)
cairosvg.svg2pdf(bytestring=sec_sup_svg.encode('utf-8'), write_to='/home/user/sprocket_z24_support_sector_1to1.pdf')
cairosvg.svg2png(bytestring=sec_sup_svg.encode('utf-8'), write_to='/home/user/sprocket_z24_support_sector_1to1.png', dpi=200)

sec_chk_svg = make_cheek_sector_svg()
with open('/home/user/cheek_roller_d382_sector_1to1.svg', 'w') as f:
    f.write(sec_chk_svg)
cairosvg.svg2pdf(bytestring=sec_chk_svg.encode('utf-8'), write_to='/home/user/cheek_roller_d382_sector_1to1.pdf')
cairosvg.svg2png(bytestring=sec_chk_svg.encode('utf-8'), write_to='/home/user/cheek_roller_d382_sector_1to1.png', dpi=200)

print("Saved sector templates for both options")
