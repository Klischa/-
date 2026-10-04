import math
import numpy as np
import cairosvg
from pypdf import PdfWriter, PdfReader
import io

from build_all_a4 import (
    full_profile, bolt_holes, tooth_labels,
    Ra, Rf, Rp, z,
    get_svg_defs, draw_calibration_ruler
)

W_A4 = 210.0
H_A4 = 297.0

# -------------------------------------------------------------
# PAGE 1: COVER & ASSEMBLY MAP (Лист-инструкция и схема раскладки)
# -------------------------------------------------------------
def make_cover_svg():
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W_A4} {H_A4}" width="{W_A4}mm" height="{H_A4}mm">')
    svg.append(get_svg_defs())
    svg.append(f'<rect x="0" y="0" width="{W_A4}" height="{H_A4}" fill="#ffffff" />')
    
    # Border
    svg.append(f'<rect x="8" y="8" width="{W_A4-16}" height="{H_A4-16}" fill="none" stroke="#000" stroke-width="0.7" />')
    svg.append(f'<rect x="10" y="10" width="{W_A4-20}" height="{H_A4-20}" fill="none" stroke="#aaa" stroke-width="0.3" />')
    
    # Header
    svg.append(f'<text x="{W_A4/2}" y="22" class="txt-head" text-anchor="middle" font-size="5.2px">ШАБЛОН ЗВЕЗДОЧКИ z=24 (ШАГ 50,5 мм) ДЛЯ ПЕЧАТИ 1:1</text>')
    svg.append(f'<text x="{W_A4/2}" y="28" class="txt-main" text-anchor="middle" font-weight="bold" fill="#0066cc">Гусеница «Муравей» / Зацепление через окна / Трапецеидальный зуб</text>')
    svg.append(f'<line x1="15" y1="31" x2="{W_A4-15}" y2="31" stroke="#000" stroke-width="0.5" />')
    
    # Assembly Map Visual (Схема раскладки 6 листов А4)
    map_x = 20.0
    map_y = 38.0
    map_w = 170.0
    map_h = 110.0
    
    svg.append(f'<rect x="{map_x}" y="{map_y}" width="{map_w}" height="{map_h}" fill="#fcfcfc" stroke="#555" stroke-width="0.4" />')
    svg.append(f'<text x="{map_x + map_w/2}" y="{map_y - 2.5}" class="txt-main" text-anchor="middle" font-weight="bold">СХЕМА РАСКЛАДКИ 6 ЛИСТОВ ФОРМАТА А4 (СЕТКА 3 × 2):</text>')
    
    # 6 sheet rectangles inside map:
    # 3 cols, 2 rows
    cell_w = (map_w - 20) / 3.0 # 50 mm
    cell_h = (map_h - 16) / 2.0 # 47 mm
    
    sheet_labels = [
        ("ЛИСТ 1", "Верхний Левый", "Зубья 21...24, 1"),
        ("ЛИСТ 2", "Верхний Центр", "Зубья 24, 1...4, Ступица"),
        ("ЛИСТ 3", "Верхний Правый", "Зубья 3...8"),
        ("ЛИСТ 4", "Нижний Левый", "Зубья 15...20"),
        ("ЛИСТ 5", "Нижний Центр", "Зубья 11...16, Ступица"),
        ("ЛИСТ 6", "Нижний Правый", "Зубья 8...13")
    ]
    
    # Draw mini sprocket circle inside the map
    cx_map = map_x + map_w / 2.0
    cy_map = map_y + map_h / 2.0
    r_map = 42.0 # scaled sprocket ~84 mm dia
    svg.append(f'<circle cx="{cx_map}" cy="{cy_map}" r="{r_map}" fill="#fff" stroke="#000" stroke-width="0.6" />')
    svg.append(f'<circle cx="{cx_map}" cy="{cy_map}" r="{r_map * (Rf/Ra)}" fill="none" stroke="#777" stroke-dasharray="2, 2" />')
    svg.append(f'<circle cx="{cx_map}" cy="{cy_map}" r="{r_map * (Rp/Ra)}" fill="none" stroke="#d00" stroke-dasharray="3, 1" />')
    svg.append(f'<circle cx="{cx_map}" cy="{cy_map}" r="{r_map * (37.5/Ra)}" fill="#f0f0f0" stroke="#000" stroke-width="0.4" />')
    svg.append(f'<circle cx="{cx_map}" cy="{cy_map}" r="{r_map * (47.5/Ra)}" fill="none" stroke="#0066cc" stroke-dasharray="2, 1" />')
    
    # Grid lines showing sheet seams
    x_s1 = map_x + 10 + cell_w
    x_s2 = map_x + 10 + 2*cell_w
    y_sm = map_y + 8 + cell_h
    
    for r in range(2):
        for c in range(3):
            lx = map_x + 10 + c * cell_w
            ly = map_y + 8 + r * cell_h
            idx = r * 3 + c
            name, pos, teeth = sheet_labels[idx]
            
            svg.append(f'<rect x="{lx}" y="{ly}" width="{cell_w}" height="{cell_h}" fill="none" stroke="#ff6600" stroke-width="0.5" stroke-dasharray="3, 2" />')
            svg.append(f'<rect x="{lx+2}" y="{ly+2}" width="16" height="6" fill="#ff6600" rx="1" />')
            svg.append(f'<text x="{lx+10}" y="{ly+6.2}" fill="#fff" font-size="2.8px" font-weight="bold" text-anchor="middle">{name}</text>')
            svg.append(f'<text x="{lx + cell_w/2}" y="{ly + cell_h - 6}" font-size="2.4px" text-anchor="middle" fill="#333">{pos}</text>')
            svg.append(f'<text x="{lx + cell_w/2}" y="{ly + cell_h - 2.5}" font-size="2.1px" text-anchor="middle" fill="#777">{teeth}</text>')
            
    # Key dimensions callout box
    dim_box_y = 155.0
    svg.append(f'<rect x="15" y="{dim_box_y}" width="180" height="26" fill="#f4f8fb" stroke="#0066cc" stroke-width="0.4" rx="2" />')
    svg.append(f'<text x="20" y="{dim_box_y + 6}" class="txt-main" font-weight="bold" fill="#0066cc">КОНТРОЛЬНЫЕ ГЕОМЕТРИЧЕСКИЕ РАЗМЕРЫ (МАСШТАБ 1:1):</text>')
    
    col_dims = [
        ("Наружный диаметр (по вершинам зубьев):", "Ø 408,8 мм"),
        ("Диаметр впадин (дно между зубьями):", "Ø 351,9 мм"),
        ("Делительный диаметр зацепления:", "Ø 386,9 мм"),
        ("Посадочное отверстие под вал:", "Ø 75,0 мм"),
        ("Крепежные отверстия (9 шт.):", "Ø 9,5 мм на Ø 95 мм"),
        ("Ширина вершины / основания зуба:", "6,97 мм / 21,0 мм")
    ]
    for i, (k, v) in enumerate(col_dims):
        cx_d = 20 if i < 3 else 110
        cy_d = dim_box_y + 11.5 + (i % 3) * 4.6
        svg.append(f'<text x="{cx_d}" y="{cy_d}" font-size="2.6px" fill="#333">• {k}</text>')
        svg.append(f'<text x="{cx_d + 72}" y="{cy_d}" font-size="2.6px" font-weight="bold" fill="#000">{v}</text>')
        
    # Instructions Box
    inst_y = 186.0
    svg.append(f'<rect x="15" y="{inst_y}" width="180" height="74" fill="#ffffff" stroke="#333" stroke-width="0.4" rx="2" />')
    svg.append(f'<text x="20" y="{inst_y + 7}" class="txt-head" font-size="3.6px">ПОШАГОВАЯ ИНСТРУКЦИЯ ПО ПЕЧАТИ И СКЛЕЙКЕ:</text>')
    
    steps = [
        ("1. НАСТРОЙКА ПРИНТЕРА:", "В программе просмотра PDF (Acrobat Reader, браузер) в окне печати выберите параметр «Реальный размер» (Actual size) или масштаб ровно «100%». НЕ ВЫБИРАЙТЕ «Подогнать под страницу» (Fit to page)!"),
        ("2. ПРОВЕРКА МАСШТАБА:", "Внизу каждого из 6 листов напечатана контрольная шкала 100 мм. После печати приложите линейку или штангенциркуль к шкале: расстояние от 0 до 100 должно составлять ровно 100,0 мм."),
        ("3. ОБРЕЗКА ПОЛЕЙ:", "На каждом листе оранжевым пунктиром нанесена «Линия склейки». Отрежьте бумагу канцелярским ножом по линейке строго по этой пунктирной линии со стороны наложения."),
        ("4. СОВМЕЩЕНИЕ ЛИСТОВ:", "Наложите листы срезанным краем на соседний лист так, чтобы совпали кресты совмещения ⨁, контуры зубьев и красная делительная окружность. Проверьте совпадение на просвет (на окне или световом столе)."),
        ("5. ФИКСАЦИЯ:", "Скрепите совмещенные листы малярным скотчем или клеящим карандашом с тыльной стороны."),
        ("6. ПЕРЕНОС НА МАТЕРИАЛ:", "Наклейте полученный шаблон на заготовку (СВМПЭ PE-1000, капролон или фанеру/металл) клеем-спреем или зафиксируйте по центру Ø75 мм. Вырезайте по сплошной черной линии.")
    ]
    
    for i, (title, desc) in enumerate(steps):
        sy = inst_y + 14.0 + i * 9.8
        svg.append(f'<text x="20" y="{sy}" font-size="2.7px" font-weight="bold" fill="#d00">{title}</text>')
        # Wrap desc if needed
        svg.append(f'<text x="20" y="{sy + 3.8}" font-size="2.4px" fill="#222">{desc[:115]}</text>')
        if len(desc) > 115:
            svg.append(f'<text x="20" y="{sy + 6.8}" font-size="2.4px" fill="#222">{desc[115:]}</text>')
            
    # Master calibration ruler on cover page
    svg.append(draw_calibration_ruler(x=20, y=H_A4 - 23, length_mm=100))
    svg.append(f'<text x="{W_A4 - 20}" y="{H_A4 - 18}" font-size="2.6px" text-anchor="end" font-weight="bold">Лист 1 из 7 (Общая инструкция)</text>')
    svg.append(f'<text x="{W_A4 - 20}" y="{H_A4 - 13}" font-size="2.3px" text-anchor="end" fill="#666">Далее следуют Листы 1..6 шаблона 1:1</text>')
    
    svg.append('</svg>')
    return "\n".join(svg)

# -------------------------------------------------------------
# SINGLE SHEET A4 QUADRANT TEMPLATE (6 teeth at 1:1 on 1 page)
# -------------------------------------------------------------
def make_quadrant_svg():
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W_A4} {H_A4}" width="{W_A4}mm" height="{H_A4}mm">')
    svg.append(get_svg_defs())
    svg.append(f'<rect x="0" y="0" width="{W_A4}" height="{H_A4}" fill="#ffffff" />')
    
    # Border
    svg.append(f'<rect x="5" y="5" width="{W_A4-10}" height="{H_A4-10}" fill="none" stroke="#ccc" stroke-width="0.3" stroke-dasharray="2, 2" />')
    
    # Header
    svg.append(f'<text x="{W_A4/2}" y="14" class="txt-head" text-anchor="middle" font-size="4.2px">ШАБЛОН-СЕКТОР НА 1 ЛИСТЕ А4 (90° / 6 ЗУБЬЕВ) — МАСШТАБ 1:1</text>')
    svg.append(f'<text x="{W_A4/2}" y="19" class="txt-main" text-anchor="middle" fill="#0066cc">Позволяет разметить всю звездочку 24 зуба без склейки (4 поворота на 90° вокруг центра Ø75)</text>')
    svg.append(f'<line x1="10" y1="22" x2="{W_A4-10}" y2="22" stroke="#aaa" stroke-width="0.4" />')
    
    # Position origin (0,0) near bottom-left:
    # Radius = 204.4 mm.
    # On A4 (210 x 297 mm):
    # Origin at (x_orig = 25 mm, y_orig = 240 mm):
    # Quadrant 1 goes X from 0 to +204.4 -> x_page from 25 to 229.4 (exceeds 210 mm by 19.4 mm!).
    # BUT if we rotate the sector by 45 degrees so the diagonal is vertical:
    # At 45 degrees, the angle spans from 0 to 90 deg, rotated so centerline is at 90 deg:
    # Max width across sector = 2 * Ra * sin(45 deg) = 2 * 204.4 * 0.7071 = 289 mm? Still 289 mm!
    # WAIT! What if origin is placed at (x_orig = 15 mm, y_orig = 250 mm) and we orient the sector along the diagonal of the A4 page?!
    # Diagonal of A4 is 364 mm!
    # Vector along diagonal: (cos 54.7 deg, sin 54.7 deg) ~ (0.577, 0.816).
    # From origin at bottom-left (15, 275) to top-right:
    # A 6-tooth sector covers angle 90 degrees (15 deg * 6 = 90 deg)!
    # Let the sector centerline be directed towards top-right (angle 54.7 degrees)!
    # Then the sector spans from angle 54.7 - 45 = 9.7 degrees to 54.7 + 45 = 99.7 degrees!
    # At radius 204.4 mm:
    # For angle 9.7 deg: X = 204.4 * cos(9.7) = 201 mm, Y = 204.4 * sin(9.7) = 34 mm.
    # 15 + 201 = 216 mm -> slightly over 210 mm!
    # BUT WHAT IF WE TAKE A 5-TOOTH OR 4-TOOTH SECTOR (60 degrees)?
    # A 60-degree sector (4 teeth, 60 deg) has width = 2 * 204.4 * sin(30 deg) = 204.4 mm!
    # And a 3-tooth sector (45 degrees) has width = 2 * 204.4 * sin(22.5 deg) = 156 mm!
    # 156 mm fits in 210 mm with 54 mm to spare!
    # If you take a 45-degree sector (3 teeth) or 60-degree sector (4 teeth):
    # 4-tooth sector (60°): exactly 1/6th of the sprocket (24 / 4 = 6 times)!
    # Let's check a 60-degree sector (4 teeth, 1/6th of sprocket):
    # Height = Ra = 204.4 mm.
    # Width at rim = 2 * Ra * sin(30°) = 2 * 204.4 * 0.5 = 204.4 mm.
    # Width at pitch circle = 2 * 193.45 * 0.5 = 193.45 mm!
    # Fits on A4 portrait (width 210 mm, height 297 mm)!
    # A 60° template has 4 teeth: rotate 6 times around center to make 24 teeth!
    # That fits cleanly on a single sheet of A4 with zero overhang!
    
    # Let's generate this 60° (4 teeth) + center bore 1:1 master template on A4:
    x_c = W_A4 / 2.0 # 105 mm
    y_c = 245.0 # origin (0,0)
    
    # Centerline is vertical upwards (angle 90 deg)
    # Sector spans from 60 deg to 120 deg (span 60 deg, 4 teeth!)
    # At y_c = 245, apex at y_page = 245 - 204.4 = 40.6 mm (plenty of margin from 22 mm header!)
    # Left edge: X = 105 - 204.4 * sin(30) = 105 - 102.2 = 2.8 mm (or angle 25 deg = 86 mm -> X = 19 mm!)
    # Let's draw 4 teeth (indices 0, 1, 2, 3 or centered around vertical: teeth 24, 1, 2, 3):
    
    # Tooth points for the 4 teeth centered around top:
    # Tooth 0 (index 0) centered at 90 deg.
    # Tooth 1 at 75 deg.
    # Tooth -1 at 105 deg.
    # Tooth 2 at 60 deg, Tooth -2 at 120 deg.
    # Total 5 teeth or 4 teeth!
    # Let's draw the arc from angle -35 deg to +35 deg around vertical:
    
    # Cut line for sector:
    # 1. Radial ray from center to left tooth root (angle -30 deg from vertical):
    rad_l = math.radians(90.0 + 30.0) # 120 deg
    rad_r = math.radians(90.0 - 30.0) # 60 deg
    
    p_cen = np.array([x_c, y_c])
    p_ray_l = np.array([x_c + Ra * math.cos(rad_l), y_c - Ra * math.sin(rad_l)])
    p_ray_r = np.array([x_c + Ra * math.cos(rad_r), y_c - Ra * math.sin(rad_r)])
    
    # Full teeth profile points within angle [60 deg, 120 deg]:
    sec_pts = []
    for pt in full_profile:
        ang = math.atan2(pt[1], pt[0]) # angle in radians
        # check if in range [pi/3 - 0.05, 2*pi/3 + 0.05]:
        if math.pi/3 - 0.05 <= ang <= 2*math.pi/3 + 0.05:
            sec_pts.append((x_c + pt[0], y_c - pt[1]))
            
    # Sort or connect sector
    svg.append(f'<circle cx="{x_c}" cy="{y_c}" r="{Rp}" class="red-pitch" />')
    svg.append(f'<circle cx="{x_c}" cy="{y_c}" r="{Rf}" class="dashed-grey" />')
    svg.append(f'<circle cx="{x_c}" cy="{y_c}" r="60.0" class="thin-line" stroke="#888" stroke-dasharray="2, 2" />')
    svg.append(f'<circle cx="{x_c}" cy="{y_c}" r="37.5" class="thin-line" stroke-width="0.5" fill="#fdfdfd" />')
    svg.append(f'<circle cx="{x_c}" cy="{y_c}" r="47.5" class="blue-axis" />')
    
    # Bolt holes in sector
    for bx, by in bolt_holes:
        ang = math.atan2(by, bx)
        if math.pi/4 <= ang <= 3*math.pi/4:
            pg_bx = x_c + bx
            pg_by = y_c - by
            svg.append(f'<circle cx="{pg_bx:.3f}" cy="{pg_by:.3f}" r="4.75" class="thin-line" stroke-width="0.5" fill="#fff" />')
            svg.append(f'<circle cx="{pg_bx:.3f}" cy="{pg_by:.3f}" r="0.4" fill="#000" />')
            
    # Center cross
    svg.append(f'<line x1="{x_c-15}" y1="{y_c}" x2="{x_c+15}" y2="{y_c}" class="cut-line" stroke-width="0.5" />')
    svg.append(f'<line x1="{x_c}" y1="{y_c-15}" x2="{x_c}" y2="{y_c+15}" class="cut-line" stroke-width="0.5" />')
    svg.append(f'<circle cx="{x_c}" cy="{y_c}" r="1.5" fill="#d00" />')
    svg.append(f'<text x="{x_c}" y="{y_c + 7}" font-size="2.8px" text-anchor="middle" font-weight="bold">ЦЕНТР ЗВЕЗДЫ (0,0)</text>')
    
    # Sector cut rays (60 deg sector)
    svg.append(f'<line x1="{x_c}" y1="{y_c}" x2="{p_ray_l[0]}" y2="{p_ray_l[1]}" class="dashed-seam" stroke-width="0.5" />')
    svg.append(f'<line x1="{x_c}" y1="{y_c}" x2="{p_ray_r[0]}" y2="{p_ray_r[1]}" class="dashed-seam" stroke-width="0.5" />')
    svg.append(f'<text x="{p_ray_l[0] - 2}" y="{p_ray_l[1] + 5}" class="txt-seam">ЛУЧ 60° (ЛИНИЯ ПОВОРОТА)</text>')
    svg.append(f'<text x="{p_ray_r[0] + 2}" y="{p_ray_r[1] + 5}" class="txt-seam" text-anchor="end">ЛУЧ 60°</text>')
    
    # Draw teeth profile in this sector
    pts_d = []
    for i, pt in enumerate(full_profile):
        ang = math.atan2(pt[1], pt[0])
        if math.radians(52.0) <= ang <= math.radians(128.0):
            px = x_c + pt[0]
            py = y_c - pt[1]
            pts_d.append((px, py))
            
    # Draw polyline of teeth
    if len(pts_d) > 0:
        path_str = "M " + " L ".join([f"{p[0]:.2f} {p[1]:.2f}" for p in pts_d])
        svg.append(f'<path d="{path_str}" class="cut-line" stroke-width="0.8" />')
        
    # Tooth numbers in this sector
    for tx, ty, num in tooth_labels:
        ang = math.atan2(ty, tx)
        if math.radians(55.0) <= ang <= math.radians(125.0):
            pg_tx = x_c + tx
            pg_ty = y_c - ty
            svg.append(f'<circle cx="{pg_tx:.2f}" cy="{pg_ty:.2f}" r="3.2" fill="#fff" stroke="#d00" stroke-width="0.3" />')
            svg.append(f'<text x="{pg_tx:.2f}" y="{pg_ty + 1.2:.2f}" class="txt-num" text-anchor="middle">{num}</text>')
            
    # Instructions on quadrant page
    svg.append(f'<rect x="15" y="{H_A4 - 48}" width="180" height="23" fill="#f4f8fb" stroke="#0066cc" stroke-width="0.4" rx="2" />')
    svg.append(f'<text x="20" y="{H_A4 - 42}" class="txt-main" font-weight="bold" fill="#0066cc">КАК ПОЛЬЗОВАТЬСЯ ШАБЛОНОМ-СЕКТОРОМ БЕЗ СКЛЕЙКИ:</text>')
    svg.append(f'<text x="20" y="{H_A4 - 37}" font-size="2.4px" fill="#222">1. Вырежьте данный сектор (4 зуба, угол 60°) и проколите центр (0,0) шилом/гвоздиком.</text>')
    svg.append(f'<text x="20" y="{H_A4 - 33}" font-size="2.4px" fill="#222">2. Закрепите центр на заготовке и обведите 4 зуба карандашом или чертилкой.</text>')
    svg.append(f'<text x="20" y="{H_A4 - 29}" font-size="2.4px" fill="#222">3. Поверните сектор вокруг центра на 60° (совместив луч с крайней линией) и обведите следующие 4 зуба.</text>')
    svg.append(f'<text x="20" y="{H_A4 - 25}" font-size="2.4px" fill="#222">4. Повторите 6 раз (6 × 4 = 24 зуба) — получите полный точный контур звезды без необходимости склеивать листы!</text>')
    
    # Calibration ruler
    svg.append(draw_calibration_ruler(x=15, y=H_A4 - 18, length_mm=100))
    svg.append(f'<text x="{W_A4 - 15}" y="{H_A4 - 10}" class="txt-scale" text-anchor="end" font-weight="bold">Масштаб 1:1 (100%)</text>')
    
    svg.append('</svg>')
    return "\n".join(svg)

# Write Cover SVG and PDF
cover_svg = make_cover_svg()
with open('/home/user/page_cover.svg', 'w', encoding='utf-8') as f:
    f.write(cover_svg)
cover_pdf_bytes = cairosvg.svg2pdf(bytestring=cover_svg.encode('utf-8'))
print("Cover page generated")

# Write Quadrant SVG and PDF and PNG
quad_svg = make_quadrant_svg()
with open('/home/user/sprocket_muravey_z24_quadrant_1to1.svg', 'w', encoding='utf-8') as f:
    f.write(quad_svg)
cairosvg.svg2pdf(bytestring=quad_svg.encode('utf-8'), write_to='/home/user/sprocket_muravey_z24_quadrant_1to1.pdf')
cairosvg.svg2png(bytestring=quad_svg.encode('utf-8'), write_to='/home/user/sprocket_muravey_z24_quadrant_1to1.png', dpi=200)
print("Quadrant template generated")

# Now combine Cover + 6 Tiles into multi-page PDF: sprocket_muravey_z24_1to1_tiled.pdf
writer = PdfWriter()

# Page 1: Cover
cover_reader = PdfReader(io.BytesIO(cover_pdf_bytes))
writer.add_page(cover_reader.pages[0])

# Pages 2 to 7: 6 tiles
for r_idx in range(2):
    for c_idx in range(3):
        tile_path = f'/home/user/tile_{r_idx}_{c_idx}.svg'
        with open(tile_path, 'r', encoding='utf-8') as f:
            t_svg = f.read()
        t_pdf_bytes = cairosvg.svg2pdf(bytestring=t_svg.encode('utf-8'))
        t_reader = PdfReader(io.BytesIO(t_pdf_bytes))
        writer.add_page(t_reader.pages[0])

out_pdf_path = '/home/user/sprocket_muravey_z24_1to1_tiled.pdf'
with open(out_pdf_path, 'wb') as f:
    writer.write(f)

print(f"Master multi-page PDF generated: {out_pdf_path} (Total {len(writer.pages)} pages)")

# Also render Page 1 (Cover) to PNG for preview
cairosvg.svg2png(bytestring=cover_svg.encode('utf-8'), write_to='/home/user/sprocket_muravey_z24_cover.png', dpi=200)
print("Cover PNG generated")

