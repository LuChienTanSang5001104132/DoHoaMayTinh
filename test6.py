"""
Mô hình phòng học 3D - Tối ưu hoá Framerate với Display List
  - 4 Cửa sổ trượt, 2 Cửa ra vào (cao 4.5m, dời né bục giảng)
  - 4 Quạt trần to & xoay nhanh, xen kẽ hàng đèn, đúng công tắc
  - Sách tủ có lõi giấy trắng, cửa tủ mở mượt mà
  - Lùi dãy bàn 3 ô gạch
"""

import sys
import math
import random
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from datetime import datetime

# ──────────────────────────────────────────────
# Kích thước phòng
# ──────────────────────────────────────────────
ROOM_W  = 20.0
ROOM_D  = 26.0
ROOM_H  = 6.0
TILE_S  = 1.0

WIN_W, WIN_H = 1200, 750

# ──────────────────────────────────────────────
# Màu sắc chung
# ──────────────────────────────────────────────
C_WALL_LIGHT  = (0.88, 0.82, 0.70, 1.0)
C_WALL_DARK   = (0.78, 0.72, 0.60, 1.0)
C_TILE_A      = (0.95, 0.93, 0.88, 1.0)
C_TILE_B      = (0.80, 0.76, 0.68, 1.0)
C_TILE_GROUT  = (0.55, 0.52, 0.48, 1.0)
C_CEIL        = (1.0, 0.97, 0.78, 1.0)
C_TRIM        = (0.65, 0.55, 0.40, 1.0)

# ──────────────────────────────────────────────
# Cửa ra vào
# ──────────────────────────────────────────────
DOOR_W   = 2.0
DOOR_H   = 4.4
DOOR_D   = 0.04
LEAF_W   = DOOR_W / 2
FRAME_D  = 0.08
FRAME_W  = 0.1

C_FRAME      = (0.45, 0.30, 0.15, 1.0)
C_DOOR       = (0.55, 0.38, 0.20, 1.0)
C_DOOR_DARK  = (0.40, 0.25, 0.10, 1.0)
C_PANEL      = (0.50, 0.35, 0.18, 1.0)
C_GLASS      = (0.60, 0.80, 0.90, 0.35)
C_HANDLE     = (0.85, 0.85, 0.90, 1.0)
C_HINGE      = (0.20, 0.20, 0.20, 1.0)

door_states = {
    1: {"cz": 6.0,  "l_ang": 0.0, "l_tgt": 0.0, "l_open": False, "r_ang": 0.0, "r_tgt": 0.0, "r_open": False},
    2: {"cz": 24.0, "l_ang": 0.0, "l_tgt": 0.0, "l_open": False, "r_ang": 0.0, "r_tgt": 0.0, "r_open": False}
}

# ──────────────────────────────────────────────
# Config quạt trần
# ──────────────────────────────────────────────
fan_angle = [0] * 4
fan_on    = [False] * 4
fan_pos = [
    (7.5,  10.0),   # 0: Trái trên
    (12.5, 10.0),   # 1: Phải trên
    (7.5,  18.0),   # 2: Trái dưới
    (12.5, 18.0)    # 3: Phải dưới
]

# ──────────────────────────────────────────────
# Config công tắc quạt — đặt kế bên công tắc đèn
# Khung quạt: 0.50 rộng x 0.45 cao — chứa 4 nút 2x2
# Khung đèn:  0.25 rộng x 0.45 cao — 3 nút dọc
# Cùng Y = 2.25, nằm ngang hàng
# ──────────────────────────────────────────────
FAN_SW_X  = 18.19   # tâm khung quạt (0.25 gap + 0.25 bán kính sau LIGHT_SW_X=17.65)
FAN_SW_Y  = 2.25
FAN_SW_Z  = 0.02
switch_size = (0.10, 0.12, 0.10)
_sx, _sy = 0.115, 0.105
switch_positions = [
    (FAN_SW_X - _sx, FAN_SW_Y + _sy, FAN_SW_Z + 0.01), # 0: Trai tren
    (FAN_SW_X + _sx, FAN_SW_Y + _sy, FAN_SW_Z + 0.01), # 1: Phai tren
    (FAN_SW_X - _sx, FAN_SW_Y - _sy, FAN_SW_Z + 0.01), # 2: Trai duoi
    (FAN_SW_X + _sx, FAN_SW_Y - _sy, FAN_SW_Z + 0.01), # 3: Phai duoi
]

# ──────────────────────────────────────────────
# Camera
# ──────────────────────────────────────────────
cam = {
    "x": ROOM_W / 2, "y": 2.5, "z": ROOM_D - 5.0,
    "yaw": 0.0, "pitch": -5.0,
    "speed": 14.0, "sens": 0.25,
}
mouse_down = False
last_mouse = (0, 0)

# ──────────────────────────────────────────────
# Trạng thái đèn, cửa sổ & tủ sách
# ──────────────────────────────────────────────
sw_states = {1: False, 2: False, 3: False, 4: False}
win_open = {"L1": False, "L2": False, "R1": False, "R2": False}
win_anim = {"L1": 0.0,   "L2": 0.0,  "R1": 0.0,  "R2": 0.0}

bookcase_states = {1: False, 2: False}
bc_anim = {1: 0.0, 2: 0.0} # Animation mượt cho cửa tủ sách
books = []
held_book_id = None
dl_static = None  # Biến chứa Display List môi trường tĩnh
# ──────────────────────────────────────────────
# Trạng thái điện, đèn, cửa sổ & tủ sách
# ──────────────────────────────────────────────
global_power_on = False # APTOMAT TỔNG CỦA PHÒNG
sw_states = {1: False, 2: False, 3: False} # Chỉ còn 3 công tắc cho 3 hàng đèn

win_open = {"L1": False, "L2": False, "R1": False, "R2": False}
win_anim = {"L1": 0.0,   "L2": 0.0,  "R1": 0.0,  "R2": 0.0}
bookcase_states = {1: False, 2: False}
bc_anim = {1: 0.0, 2: 0.0} 
books = []
held_book_id = None
dl_static = None  

# Toạ độ các bộ công tắc trên tường
# Ba bộ xếp ngang hàng, cùng Y = 2.25:
#   Aptomat tổng  X=17.05  (rộng 0.30)
#   Công tắc đèn  X=17.65  (rộng 0.25)  gap=0.05 với aptomat
#   Công tắc quạt X=18.19  (rộng 0.50)  gap=0.04 với đèn
MASTER_SW_X, MASTER_SW_Y, MASTER_SW_Z = 17.05, 2.25, 0.02
LIGHT_SW_X,  LIGHT_SW_Y,  LIGHT_SW_Z  = 17.65, 2.25, 0.02
l_switch_positions = [
    (LIGHT_SW_X, LIGHT_SW_Y + 0.14, LIGHT_SW_Z + 0.01),
    (LIGHT_SW_X, LIGHT_SW_Y,        LIGHT_SW_Z + 0.01),
    (LIGHT_SW_X, LIGHT_SW_Y - 0.14, LIGHT_SW_Z + 0.01)
]


def init_books():
    global books
    books = []
    book_id = 1
    for bc_id, x_start in [(1, 3.0), (2, 13.0)]:
        for sh in [0.4, 1.0, 1.6, 2.2, 2.8, 3.4, 4.0]:
            curr_x = x_start + 0.05
            max_x  = x_start + 4.0 - 0.05
            while curr_x < max_x:
                b_thickness = random.uniform(0.04, 0.08)
                if curr_x + b_thickness > max_x: break
                b_height = random.uniform(0.3, 0.45)
                b_depth  = random.uniform(0.25, 0.38)
                b_z = 25.8 - 0.02 - b_depth / 2
                c_r = random.uniform(0.2, 0.8)
                c_g = random.uniform(0.2, 0.8)
                c_b = random.uniform(0.2, 0.8)
                books.append({
                    "id": book_id, "bc_id": bc_id, "x": curr_x + b_thickness / 2, "y": sh, "z": b_z,
                    "w": b_thickness, "h": b_height, "d": b_depth, "color": (c_r, c_g, c_b, 1.0), "is_taken": False
                })
                curr_x += b_thickness + random.uniform(0.005, 0.02)
                book_id += 1
    compile_books_list()
# ═══════════════════════════════════════════════
#  HÀM VẼ CƠ BẢN
# ═══════════════════════════════════════════════
def set_color(rgba):
    if len(rgba) == 3: glColor3f(*rgba)
    else: glColor4f(*rgba)

def drawBox(x, y, z, w, h, d):
    x1, x2 = x - w/2, x + w/2; y1, y2 = y - h/2, y + h/2; z1, z2 = z - d/2, z + d/2
    glBegin(GL_QUADS)
    glNormal3f(0,0,1);  glVertex3f(x1,y1,z2); glVertex3f(x2,y1,z2); glVertex3f(x2,y2,z2); glVertex3f(x1,y2,z2)
    glNormal3f(0,0,-1); glVertex3f(x2,y1,z1); glVertex3f(x1,y1,z1); glVertex3f(x1,y2,z1); glVertex3f(x2,y2,z1)
    glNormal3f(-1,0,0); glVertex3f(x1,y1,z1); glVertex3f(x1,y1,z2); glVertex3f(x1,y2,z2); glVertex3f(x1,y2,z1)
    glNormal3f(1,0,0);  glVertex3f(x2,y1,z2); glVertex3f(x2,y1,z1); glVertex3f(x2,y2,z1); glVertex3f(x2,y2,z2)
    glNormal3f(0,1,0);  glVertex3f(x1,y2,z2); glVertex3f(x2,y2,z2); glVertex3f(x2,y2,z1); glVertex3f(x1,y2,z1)
    glNormal3f(0,-1,0); glVertex3f(x1,y1,z1); glVertex3f(x2,y1,z1); glVertex3f(x2,y1,z2); glVertex3f(x1,y1,z2)
    glEnd()

def draw_box_coords(x1, x2, y1, y2, z1, z2, color):
    set_color(color); glBegin(GL_QUADS)
    glNormal3f(-1,0,0); glVertex3f(x1,y1,z1); glVertex3f(x1,y1,z2); glVertex3f(x1,y2,z2); glVertex3f(x1,y2,z1)
    glNormal3f(1,0,0);  glVertex3f(x2,y1,z1); glVertex3f(x2,y1,z2); glVertex3f(x2,y2,z2); glVertex3f(x2,y2,z1)
    glNormal3f(0,-1,0); glVertex3f(x1,y1,z1); glVertex3f(x2,y1,z1); glVertex3f(x2,y2,z1); glVertex3f(x1,y2,z1)
    glNormal3f(0,1,0);  glVertex3f(x1,y1,z2); glVertex3f(x2,y1,z2); glVertex3f(x2,y2,z2); glVertex3f(x1,y2,z2)
    glNormal3f(0,0,-1); glVertex3f(x1,y2,z1); glVertex3f(x2,y2,z1); glVertex3f(x2,y2,z2); glVertex3f(x1,y2,z2)
    glNormal3f(0,0,1);  glVertex3f(x1,y1,z1); glVertex3f(x2,y1,z1); glVertex3f(x2,y1,z2); glVertex3f(x1,y1,z2)
    glEnd()

def draw_box_corner(x, y, z, w, h, d, color, dark_color=None):
    if dark_color is None: dark_color = (color[0]*0.7, color[1]*0.7, color[2]*0.7, 1.0)
    x0, x1, y0, y1, z0, z1 = x, x+w, y, y+h, z-d/2, z+d/2
    glBegin(GL_QUADS)
    glColor4f(*color);      glNormal3f(0,0,1);  glVertex3f(x0,y0,z1); glVertex3f(x1,y0,z1); glVertex3f(x1,y1,z1); glVertex3f(x0,y1,z1)
    glColor4f(*dark_color); glNormal3f(0,0,-1); glVertex3f(x1,y0,z0); glVertex3f(x0,y0,z0); glVertex3f(x0,y1,z0); glVertex3f(x1,y1,z0)
    glColor4f(*color);      glNormal3f(0,1,0);  glVertex3f(x0,y1,z0); glVertex3f(x1,y1,z0); glVertex3f(x1,y1,z1); glVertex3f(x0,y1,z1)
    glColor4f(*dark_color); glNormal3f(0,-1,0); glVertex3f(x0,y0,z1); glVertex3f(x1,y0,z1); glVertex3f(x1,y0,z0); glVertex3f(x0,y0,z0)
    glColor4f(color[0]*0.9, color[1]*0.9, color[2]*0.9, 1.0);              glNormal3f(1,0,0);  glVertex3f(x1,y0,z1); glVertex3f(x1,y0,z0); glVertex3f(x1,y1,z0); glVertex3f(x1,y1,z1)
    glColor4f(dark_color[0]*0.9, dark_color[1]*0.9, dark_color[2]*0.9,1.0);glNormal3f(-1,0,0); glVertex3f(x0,y0,z0); glVertex3f(x0,y0,z1); glVertex3f(x0,y1,z1); glVertex3f(x0,y1,z0)
    glEnd()

def draw_cylinder(x, y, z, radius, height, axis='z', segments=16, color=(1,1,1,1)):
    glColor4f(*color); glPushMatrix(); glTranslatef(x, y, z)
    if axis == 'y':   glRotatef(-90, 1, 0, 0)
    elif axis == 'x': glRotatef(90, 0, 1, 0)
    quad = gluNewQuadric(); gluCylinder(quad, radius, radius, height, segments, 1)
    gluDisk(quad, 0, radius, segments, 1); glTranslatef(0, 0, height); gluDisk(quad, 0, radius, segments, 1)
    gluDeleteQuadric(quad); glPopMatrix()

# ═══════════════════════════════════════════════
#  QUẠT TRẦN LỚP HỌC
# ═══════════════════════════════════════════════
def draw_fan_blade(length=1.5): # Tăng độ dài cánh quạt
    C_BLADE, C_BLADE_BOT = (0.91, 0.91, 0.88, 1.0), (0.80, 0.80, 0.78, 1.0)
    root_w, tip_w, thick = 0.10, 0.26, 0.012
    x0, x1 = 0.0, length; yr0, yr1 = -root_w, root_w; yt0, yt1 = -tip_w, tip_w; zt, zb = thick/2, -thick/2
    glBegin(GL_QUADS)
    glColor4f(*C_BLADE);     glNormal3f(0,1,0);  glVertex3f(x0,zt,yr0); glVertex3f(x0,zt,yr1); glVertex3f(x1,zt,yt1); glVertex3f(x1,zt,yt0)
    glColor4f(*C_BLADE_BOT); glNormal3f(0,-1,0); glVertex3f(x0,zb,yr0); glVertex3f(x1,zb,yt0); glVertex3f(x1,zb,yt1); glVertex3f(x0,zb,yr1)
    glColor4f(*C_BLADE);     glNormal3f(0,0,1);  glVertex3f(x0,zb,yr1); glVertex3f(x1,zb,yt1); glVertex3f(x1,zt,yt1); glVertex3f(x0,zt,yr1)
    glColor4f(*C_BLADE_BOT); glNormal3f(0,0,-1); glVertex3f(x0,zt,yr0); glVertex3f(x1,zt,yt0); glVertex3f(x1,zb,yt0); glVertex3f(x0,zb,yr0)
    glColor4f(*C_BLADE);     glNormal3f(1,0,0);  glVertex3f(x1,zb,yt0); glVertex3f(x1,zt,yt0); glVertex3f(x1,zt,yt1); glVertex3f(x1,zb,yt1)
    glEnd()

def draw_fan(x, z, angle):
    C_BODY, C_MOTOR, C_DARK, C_POLE = (0.88, 0.88, 0.85), (0.75, 0.75, 0.73), (0.55, 0.55, 0.53), (0.70, 0.70, 0.68)
    pole_h, motor_r, motor_h, cap_h = 0.28, 0.13, 0.18, 0.07
    blade_y = ROOM_H - pole_h - motor_h - 0.01

    glPushMatrix(); glTranslatef(x, 0, z)
    draw_cylinder(0, ROOM_H - pole_h, 0, 0.018, pole_h, 'y', 10, (*C_POLE, 1.0))
    draw_cylinder(0, ROOM_H - 0.04,   0, 0.06,  0.04,   'y', 16, (*C_BODY, 1.0))
    draw_cylinder(0, ROOM_H - pole_h - motor_h, 0, motor_r, motor_h, 'y', 24, (*C_MOTOR, 1.0))
    for rib in [0.04, 0.09, 0.14]:
        draw_cylinder(0, ROOM_H - pole_h - motor_h + rib, 0, motor_r + 0.008, 0.015, 'y', 24, (*C_DARK, 1.0))
    draw_cylinder(0, blade_y - cap_h, 0, motor_r * 0.75, cap_h, 'y', 20, (*C_BODY, 1.0))
    
    hub_r = 0.045
    glPushMatrix(); glTranslatef(0, blade_y, 0); glRotatef(angle, 0, 1, 0)
    for i in range(3):
        glPushMatrix(); glRotatef(i * 120, 0, 1, 0); glTranslatef(hub_r, 0, 0); draw_fan_blade(1.5); glPopMatrix()
    draw_cylinder(0, -0.01, 0, hub_r, 0.022, 'y', 16, (*C_DARK, 1.0))
    glPopMatrix(); glPopMatrix()

# ═══════════════════════════════════════════════
#  CÔNG TẮC
# ═══════════════════════════════════════════════
def draw_cube_center_sz(x, y, z, w, h, d, color):
    glColor3f(*color[:3]); drawBox(x, y, z, w, h, d)

def draw_button(cx, cy, cz, is_on):
    draw_cube_center_sz(cx, cy, cz + 0.008, 0.108, 0.118, 0.009, (0.62,0.62,0.62))
    draw_cube_center_sz(cx, cy, cz + 0.013, 0.102, 0.112, 0.008, (0.98,0.98,0.97) if is_on else (0.91,0.91,0.90))
    draw_cube_center_sz(cx, cy + 0.028, cz + 0.018, 0.034, 0.018, 0.004, (0.40,0.40,0.40))
    if is_on: draw_cube_center_sz(cx, cy + 0.028, cz + 0.019, 0.026, 0.012, 0.004, (0.10,0.95,0.35))
    else:     draw_cube_center_sz(cx, cy + 0.028, cz + 0.019, 0.026, 0.012, 0.004, (0.95,0.08,0.08))

def draw_fan_switch_box():
    bx, by, bz = FAN_SW_X, FAN_SW_Y, FAN_SW_Z
    # Khung ngoài rộng 0.50 x cao 0.45 — đủ chứa 4 nút 2x2
    glColor3f(0.28, 0.28, 0.28); drawBox(bx, by, bz + 0.006, 0.50, 0.45, 0.012)
    glColor3f(0.52, 0.52, 0.52); drawBox(bx, by, bz + 0.011, 0.48, 0.43, 0.012)
    glColor3f(0.97, 0.97, 0.96); drawBox(bx, by, bz + 0.016, 0.46, 0.41, 0.006)
    # Thanh ngăn dọc giữa 2 cột
    glColor3f(0.70, 0.70, 0.70); drawBox(bx, by, bz + 0.018, 0.012, 0.39, 0.004)
    for i in range(4): draw_button(*switch_positions[i], fan_on[i])

# ═══════════════════════════════════════════════
#  CỬA RA VÀO 2 CÁNH 
# ═══════════════════════════════════════════════
def draw_door_leaf(is_left=True):
    offset_x = 0 if is_left else -LEAF_W
    draw_box_corner(offset_x,            0,            -DOOR_D/2, 0.12,       DOOR_H,      DOOR_D, C_DOOR, C_DOOR_DARK)
    draw_box_corner(offset_x+LEAF_W-0.12,0,            -DOOR_D/2, 0.12,       DOOR_H,      DOOR_D, C_DOOR, C_DOOR_DARK)
    draw_box_corner(offset_x+0.12,       0,            -DOOR_D/2, LEAF_W-0.24, 0.20,       DOOR_D, C_DOOR, C_DOOR_DARK)
    draw_box_corner(offset_x+0.12,       1.0,          -DOOR_D/2, LEAF_W-0.24, 0.15,       DOOR_D, C_DOOR, C_DOOR_DARK)
    draw_box_corner(offset_x+0.12,       DOOR_H-0.12,  -DOOR_D/2, LEAF_W-0.24, 0.12,       DOOR_D, C_DOOR, C_DOOR_DARK)
    
    glass_h = DOOR_H - 1.27
    draw_box_corner(offset_x+LEAF_W/2-0.02, 1.15, -DOOR_D/2, 0.04, glass_h, DOOR_D, C_DOOR, C_DOOR_DARK)
    num_hm = int(glass_h / 0.5)
    for i in range(1, num_hm + 1):
        my = 1.15 + i * (glass_h / (num_hm + 1))
        draw_box_corner(offset_x+0.12, my, -DOOR_D/2, LEAF_W-0.24, 0.04, DOOR_D, C_DOOR, C_DOOR_DARK)

    for i in range(13):
        ly = 0.22 + i * 0.06
        glPushMatrix(); glTranslatef(offset_x+0.12, ly, 0); glRotatef(-35, 1, 0, 0)
        draw_box_corner(0, 0, -DOOR_D*0.3, LEAF_W-0.24, 0.065, 0.015, C_PANEL, C_DOOR_DARK); glPopMatrix()
        
    hx = offset_x + LEAF_W - 0.1 if is_left else offset_x + 0.1
    hy = 2
    for side_z in [DOOR_D/2, -DOOR_D/2 - 0.04]:
        draw_cylinder(hx, hy+0.1,  side_z, 0.015, 0.04, 'z', 8, C_HANDLE)
        draw_cylinder(hx, hy-0.1,  side_z, 0.015, 0.04, 'z', 8, C_HANDLE)
        draw_cylinder(hx, hy-0.12, side_z, 0.015, 0.24, 'y', 8, C_HANDLE)
        
    hinge_x = -0.015 if is_left else 0.015
    for hy_h in [DOOR_H*0.15, DOOR_H*0.5, DOOR_H*0.85]:
        draw_box_corner(hinge_x, hy_h-0.05, -0.03, 0.03, 0.1, 0.06, C_HINGE)
        
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA); glDepthMask(GL_FALSE)
    draw_box_corner(offset_x+0.12, 1.15, -0.005, LEAF_W-0.24, glass_h, 0.01, C_GLASS, C_GLASS)
    glDepthMask(GL_TRUE); glDisable(GL_BLEND)

def draw_the_door(cz, l_ang, r_ang):
    glPushMatrix()
    glTranslatef(ROOM_W, 0.0, cz)
    glRotatef(-90, 0, 1, 0)
    
    draw_box_corner(-DOOR_W/2-FRAME_W, 0, 0, FRAME_W, DOOR_H+FRAME_W, FRAME_D, C_FRAME)
    draw_box_corner( DOOR_W/2,         0, 0, FRAME_W, DOOR_H+FRAME_W, FRAME_D, C_FRAME)
    draw_box_corner(-DOOR_W/2,         DOOR_H, 0, DOOR_W,  FRAME_W,        FRAME_D, C_FRAME)
    
    glPushMatrix(); glTranslatef(-DOOR_W/2, 0, 0); glRotatef(l_ang, 0, 1, 0)
    draw_door_leaf(is_left=True); glPopMatrix()
    
    glPushMatrix(); glTranslatef(DOOR_W/2, 0, 0); glRotatef(-r_ang, 0, 1, 0)
    draw_door_leaf(is_left=False); glPopMatrix()
    glPopMatrix()

# ═══════════════════════════════════════════════
#  RAYCASTING
# ═══════════════════════════════════════════════
def transform_ray_to_door_local(ray_o, ray_d, cz):
    ox, oy, oz = ray_o[0] - ROOM_W, ray_o[1], ray_o[2] - cz
    lox, loy, loz = oz, oy, -ox
    ldx, ldy, ldz = ray_d[2], ray_d[1], -ray_d[0]
    return (lox, loy, loz), (ldx, ldy, ldz)

def ray_hits_box(ray_o, ray_d, box_c, box_s):
    half = [s/2 for s in box_s]; t_min, t_max = -float('inf'), float('inf')
    for i in range(3):
        if abs(ray_d[i]) < 0.0001:
            if ray_o[i] < box_c[i]-half[i] or ray_o[i] > box_c[i]+half[i]: return False
        else:
            t1 = (box_c[i]-half[i]-ray_o[i])/ray_d[i]; t2 = (box_c[i]+half[i]-ray_o[i])/ray_d[i]
            if t1 > t2: t1, t2 = t2, t1
            t_min = max(t_min, t1); t_max = min(t_max, t2)
            if t_min > t_max: return False
    return t_max >= 0

def ray_hits_rotated_leaf_local(local_o, local_d, hinge_x, angle, is_left):
    ox = local_o[0] - hinge_x; oy = local_o[1]; oz = local_o[2]
    rad = math.radians(-angle); cos_t, sin_t = math.cos(rad), math.sin(rad)
    lox = ox*cos_t+oz*sin_t; loy = oy; loz = -ox*sin_t+oz*cos_t
    ldx = local_d[0]*cos_t+local_d[2]*sin_t; ldy = local_d[1]; ldz = -local_d[0]*sin_t+local_d[2]*cos_t
    center_x = (LEAF_W/2) if is_left else (-LEAF_W/2)
    return ray_hits_box((lox,loy,loz),(ldx,ldy,ldz),(center_x,DOOR_H/2,0.0),(LEAF_W,DOOR_H,0.2))

def intersect_plane(p_near, p_far, axis, val):
    d = p_far[axis] - p_near[axis]
    if d == 0: return -1, None
    t = (val - p_near[axis]) / d
    if t < 0: return -1, None
    hit = [p_near[0]+t*(p_far[0]-p_near[0]), p_near[1]+t*(p_far[1]-p_near[1]), p_near[2]+t*(p_far[2]-p_near[2])]
    return t, hit

def intersect_aabb(nx,ny,nz,dx,dy,dz,min_x,max_x,min_y,max_y,min_z,max_z):
    tmin, tmax = -999999, 999999
    for (n,d_val,m_min,m_max) in [(nx,dx,min_x,max_x),(ny,dy,min_y,max_y),(nz,dz,min_z,max_z)]:
        if abs(d_val) < 1e-6:
            if n < m_min or n > m_max: return None
        else:
            t1 = (m_min-n)/d_val; t2 = (m_max-n)/d_val
            if t1>t2: t1,t2=t2,t1
            tmin=max(tmin,t1); tmax=min(tmax,t2)
            if tmin>tmax: return None
    if tmax<0: return None
    return tmin if tmin>=0 else 0

def check_interact(mx, my):
    global held_book_id, fan_on, global_power_on
    try:
        modelview  = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport   = glGetIntegerv(GL_VIEWPORT)
    except Exception: return

    winX = float(mx); winY = float(viewport[3] - my)
    try:
        p_near = gluUnProject(winX, winY, 0.0, modelview, projection, viewport)
        p_far  = gluUnProject(winX, winY, 1.0, modelview, projection, viewport)
    except ValueError: return

    ray_o = p_near
    ray_d_raw = (p_far[0]-p_near[0], p_far[1]-p_near[1], p_far[2]-p_near[2])
    length = math.sqrt(sum(v*v for v in ray_d_raw))
    ray_d = tuple(v/length for v in ray_d_raw) if length > 0 else ray_d_raw

    
    # ── Cửa ra vào ──
    for d_id, d in door_states.items():
        cz = d["cz"]
        local_o, local_d = transform_ray_to_door_local(ray_o, ray_d, cz)

        hit_lf = ray_hits_box(local_o, local_d, (-DOOR_W/2-FRAME_W/2, DOOR_H/2, 0), (FRAME_W, DOOR_H, FRAME_D))
        hit_rf = ray_hits_box(local_o, local_d, (DOOR_W/2+FRAME_W/2, DOOR_H/2, 0), (FRAME_W, DOOR_H, FRAME_D))
        hit_tf = ray_hits_box(local_o, local_d, (0, DOOR_H+FRAME_W/2, 0), (DOOR_W, FRAME_W, FRAME_D))

        hit_left_leaf = ray_hits_rotated_leaf_local(local_o, local_d, -DOOR_W/2, d["l_ang"], True)
        hit_right_leaf = ray_hits_rotated_leaf_local(local_o, local_d, DOOR_W/2, -d["r_ang"], False)

        if hit_left_leaf or hit_lf:
            d["l_open"] = not d["l_open"]; d["l_tgt"] = 105.0 if d["l_open"] else 0.0
        if hit_right_leaf or hit_rf:
            d["r_open"] = not d["r_open"]; d["r_tgt"] = 105.0 if d["r_open"] else 0.0
        if hit_tf:
            d["l_open"] = not d["l_open"]; d["l_tgt"] = 105.0 if d["l_open"] else 0.0
            d["r_open"] = not d["r_open"]; d["r_tgt"] = 105.0 if d["r_open"] else 0.0

    # ── Aptomat Tổng ──
    if ray_hits_box(ray_o, ray_d, (MASTER_SW_X, MASTER_SW_Y, MASTER_SW_Z), (0.30, 0.40, 0.10)):
        global_power_on = not global_power_on
        return

    # ── Công tắc đèn ──
    for i in range(3):
        if ray_hits_box(ray_o, ray_d, l_switch_positions[i], (0.15, 0.1, 0.05)):
            sw_states[i+1] = not sw_states[i+1]
            return

    # ── Công tắc quạt ──
    for i in range(4):
        if ray_hits_box(ray_o, ray_d, switch_positions[i], switch_size):
            fan_on[i] = not fan_on[i]; return
        
    # Map công tắc quạt đúng chuẩn (khung rộng 0.50 x 0.45)
    t_fsw, hit_fsw = intersect_plane(p_near, p_far, 2, FAN_SW_Z + 0.02)
    if t_fsw > 0 and hit_fsw:
        hx, hy, hz = hit_fsw
        if (FAN_SW_X - 0.25) <= hx <= (FAN_SW_X + 0.25) and (FAN_SW_Y - 0.225) <= hy <= (FAN_SW_Y + 0.225):
            if   hx <  FAN_SW_X and hy >= FAN_SW_Y: fan_on[0] = not fan_on[0] # Trái Trên
            elif hx >= FAN_SW_X and hy >= FAN_SW_Y: fan_on[1] = not fan_on[1] # Phải Trên
            elif hx <  FAN_SW_X and hy <  FAN_SW_Y: fan_on[2] = not fan_on[2] # Trái Dưới
            else:                                   fan_on[3] = not fan_on[3] # Phải Dưới

    # ── Cửa sổ ──
    t_wl, hit_wl = intersect_plane(p_near, p_far, 0, 0.0)
    if t_wl > 0 and hit_wl:
        hx, hy, hz = hit_wl
        if 1.5 <= hy <= 4.5:
            if   5.0  <= hz <= 9.0:  win_open["L1"] = not win_open["L1"]
            elif 12.0 <= hz <= 16.0: win_open["L2"] = not win_open["L2"]

    t_wr, hit_wr = intersect_plane(p_near, p_far, 0, ROOM_W)
    if t_wr > 0 and hit_wr:
        hx, hy, hz = hit_wr
        if 1.5 <= hy <= 4.5:
            if   10.0 <= hz <= 14.0: win_open["R1"] = not win_open["R1"]
            elif 17.0 <= hz <= 21.0: win_open["R2"] = not win_open["R2"]

    # ── Tủ sách ──
    nx2, ny2, nz2 = p_near; dx2, dy2, dz2 = ray_d
    best_t, hit_type, hit_id = 999999, None, None
    for bc_id, x_start in [(1, 3.0), (2, 13.0)]:
        is_open = bookcase_states[bc_id]; base_z = 25.8; d_bc = 0.8
        if is_open:
            t1 = intersect_aabb(nx2,ny2,nz2,dx2,dy2,dz2, x_start,x_start+4.0, 0,4.5, base_z-0.1,base_z)
            if t1 is not None and t1<best_t: best_t=t1; hit_type="bookcase"; hit_id=bc_id
            t2 = intersect_aabb(nx2,ny2,nz2,dx2,dy2,dz2, x_start-2,x_start+0.5, 0,4.5, base_z-d_bc-1.8,base_z-d_bc)
            if t2 is not None and t2<best_t: best_t=t2; hit_type="bookcase"; hit_id=bc_id
            t3 = intersect_aabb(nx2,ny2,nz2,dx2,dy2,dz2, x_start+3.5,x_start+6, 0,4.5, base_z-d_bc-1.8,base_z-d_bc)
            if t3 is not None and t3<best_t: best_t=t3; hit_type="bookcase"; hit_id=bc_id
        else:
            t = intersect_aabb(nx2,ny2,nz2,dx2,dy2,dz2, x_start,x_start+4.0, 0,4.5, base_z-d_bc-0.1,base_z-d_bc+0.1)
            if t is not None and t<best_t: best_t=t; hit_type="bookcase"; hit_id=bc_id

    for b in books:
        if not b["is_taken"] and bookcase_states[b["bc_id"]]:
            t = intersect_aabb(nx2,ny2,nz2,dx2,dy2,dz2, b["x"]-b["w"]/2,b["x"]+b["w"]/2, b["y"],b["y"]+b["h"], b["z"]-b["d"]/2,b["z"]+b["d"]/2)
            if t is not None and t<best_t: best_t=t; hit_type="book"; hit_id=b["id"]

    if hit_type == "book":
        if held_book_id is None:
            held_book_id = hit_id
            for b in books:
                if b["id"] == hit_id: b["is_taken"] = True
            compile_books_list() # <--- Dựng lại khối sách vì đã rút 1 cuốn ra

    elif hit_type == "bookcase":
        if held_book_id is not None:
            for b in books:
                if b["id"] == held_book_id: b["is_taken"] = False
            held_book_id = None
            compile_books_list() # <--- Dựng lại khối sách vì đã cất 1 cuốn vào
        else:
            bookcase_states[hit_id] = not bookcase_states[hit_id]

# ═══════════════════════════════════════════════
#  VẼ MÔI TRƯỜNG & VẬT DỤNG KHÁC
# ═══════════════════════════════════════════════
def draw_glass_door_x(door_w, h, th, fs):
    wood_light, glass_c = (0.50, 0.30, 0.15, 1.0), (0.6, 0.8, 0.9, 0.4)
    draw_box_coords(0, fs, 0, h, -th, 0, wood_light); draw_box_coords(door_w-fs, door_w, 0, h, -th, 0, wood_light)
    draw_box_coords(fs, door_w-fs, 0, fs, -th, 0, wood_light); draw_box_coords(fs, door_w-fs, h-fs, h, -th, 0, wood_light)
    glEnable(GL_BLEND); glDepthMask(GL_FALSE); set_color(glass_c)
    glBegin(GL_QUADS); glNormal3f(0,0,-1)
    glVertex3f(fs,fs,-th/2); glVertex3f(door_w-fs,fs,-th/2)
    glVertex3f(door_w-fs,h-fs,-th/2); glVertex3f(fs,h-fs,-th/2)
    glEnd(); glDepthMask(GL_TRUE)
    handle_x = door_w - fs/2
    draw_box_coords(handle_x-0.03,handle_x+0.03, h/2-0.25,h/2+0.25, -th-0.03,-th, (0.7,0.7,0.75,1.0))

def draw_bookcases():
    bookcases = [{"id": 1, "x": 3.0, "z": 25.8, "is_open": bookcase_states[1]}, {"id": 2, "x": 13.0, "z": 25.8, "is_open": bookcase_states[2]}]
    w_bc=4.0; h_bc=4.5; d_bc=0.8
    wood_dark, wood_light, wood_shelf = (0.35, 0.20, 0.10, 1.0), (0.50, 0.30, 0.15, 1.0), (0.45, 0.25, 0.12, 1.0)
    
    for bc in bookcases:
        bx = bc["x"]; bz = bc["z"]
        # Vẽ khung tủ
        draw_box_coords(bx, bx+w_bc, 0, h_bc, bz-0.04, bz, wood_dark)
        draw_box_coords(bx, bx+0.04, 0, h_bc, bz-d_bc, bz, wood_light); draw_box_coords(bx+w_bc-0.04, bx+w_bc, 0, h_bc, bz-d_bc, bz, wood_light)
        draw_box_coords(bx, bx+w_bc, h_bc-0.05, h_bc, bz-d_bc, bz, wood_light); draw_box_coords(bx, bx+w_bc, 0, 0.05, bz-d_bc, bz, wood_light)
        # Vẽ các ngăn kệ
        for sh in [0.4, 1.0, 1.6, 2.2, 2.8, 3.4, 4.0]: 
            draw_box_coords(bx+0.04, bx+w_bc-0.04, sh, sh+0.04, bz-d_bc+0.02, bz, wood_shelf)
        
        # ĐÃ XOÁ VÒNG LẶP FOR B IN BOOKS Ở ĐÂY

        # Vẽ cửa kính
        dw = w_bc/2; angle = bc_anim[bc["id"]]
        glPushMatrix(); glTranslatef(bx, 0, bz-d_bc); glRotatef(angle, 0,1,0); draw_glass_door_x(dw, h_bc, 0.04, 0.1); glPopMatrix()
        glPushMatrix(); glTranslatef(bx+w_bc, 0, bz-d_bc); glRotatef(-angle, 0,1,0); glScalef(-1,1,1); draw_glass_door_x(dw, h_bc, 0.04, 0.1); glPopMatrix()
        
    # NẰM NGOÀI VÒNG LẶP FOR BC, GỌI DANH SÁCH SÁCH CHỈ 1 LẦN BẰNG DISPLAY LIST LÀ ĐỦ:
    if dl_books is not None:
        glCallList(dl_books)
def draw_hud():
    if held_book_id is None: return
    glDisable(GL_DEPTH_TEST); glDisable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); gluOrtho2D(0, WIN_W, 0, WIN_H)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    b = next((x for x in books if x["id"] == held_book_id), None)
    if b:
        book_w, book_h = 460, 300
        cx = WIN_W - book_w/2 - 40; cy = book_h/2 + 40
        set_color(b["color"])
        glBegin(GL_QUADS)
        glVertex2f(cx-book_w/2-10,cy-book_h/2-10); glVertex2f(cx+book_w/2+10,cy-book_h/2-10)
        glVertex2f(cx+book_w/2+10,cy+book_h/2+10); glVertex2f(cx-book_w/2-10,cy+book_h/2+10)
        glEnd()
        set_color((0.95,0.95,0.92,1.0))
        glBegin(GL_QUADS); glVertex2f(cx-book_w/2,cy-book_h/2); glVertex2f(cx-5,cy-book_h/2); glVertex2f(cx-5,cy+book_h/2); glVertex2f(cx-book_w/2,cy+book_h/2); glEnd()
        glBegin(GL_QUADS); glVertex2f(cx+5,cy-book_h/2); glVertex2f(cx+book_w/2,cy-book_h/2); glVertex2f(cx+book_w/2,cy+book_h/2); glVertex2f(cx+5,cy+book_h/2); glEnd()
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW); glEnable(GL_LIGHTING); glEnable(GL_DEPTH_TEST)
def draw_pane(x, y, z, h, w):
    # Khung viền cửa sổ
    set_color((0.8, 0.8, 0.8, 1.0))
    drawBox(x, y+h/2-0.05, z, 0.06, 0.1, w); drawBox(x, y-h/2+0.05, z, 0.06, 0.1, w)
    drawBox(x, y, z-w/2+0.05, 0.06, h, 0.1); drawBox(x, y, z+w/2-0.05, 0.06, h, 0.1)

    # Kính cửa sổ (Đồng bộ logic với cửa ra vào)
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA); glDepthMask(GL_FALSE)
    set_color(C_GLASS)
    drawBox(x, y, z, 0.02, h-0.1, w-0.1)
    glDepthMask(GL_TRUE); glDisable(GL_BLEND)

def draw_sliding_window(x_center, z_start, z_end, y_bottom, y_top, slide_offset):
    w_z, h_y = z_end - z_start, y_top - y_bottom
    mid_y, mid_z = y_bottom + h_y/2, z_start + w_z/2
    set_color((0.4, 0.4, 0.4, 1.0))
    drawBox(x_center, y_bottom+0.05, mid_z, 0.2, 0.1, w_z); drawBox(x_center, y_top-0.05, mid_z, 0.2, 0.1, w_z)
    drawBox(x_center, mid_y, z_start+0.05, 0.2, h_y, 0.1); drawBox(x_center, mid_y, z_end-0.05, 0.2, h_y, 0.1)
    p1_z, p2_z = z_start + w_z/4, (z_end - w_z/4) - slide_offset
    x_offset = 0.03 if x_center == 0 else -0.03
    draw_pane(x_center-x_offset, mid_y, p1_z, h_y-0.1, w_z/2)
    draw_pane(x_center+x_offset, mid_y, p2_z, h_y-0.1, w_z/2)

def draw_windows():
    draw_sliding_window(0.0, 5.0, 9.0, 1.5, 4.5, win_anim["L1"])
    draw_sliding_window(0.0, 12.0, 16.0, 1.5, 4.5, win_anim["L2"])
    draw_sliding_window(ROOM_W, 10.0, 14.0, 1.5, 4.5, win_anim["R1"])
    draw_sliding_window(ROOM_W, 17.0, 21.0, 1.5, 4.5, win_anim["R2"])

def draw_light_switches():
    bx, by, bz = LIGHT_SW_X, LIGHT_SW_Y, LIGHT_SW_Z
    # Khung ngoài — cùng kích thước với bộ công tắc quạt (0.25 x 0.45)
    glColor3f(0.28, 0.28, 0.28); drawBox(bx, by, bz + 0.006, 0.25, 0.45, 0.012)
    glColor3f(0.52, 0.52, 0.52); drawBox(bx, by, bz + 0.011, 0.23, 0.43, 0.012)
    glColor3f(0.97, 0.97, 0.96); drawBox(bx, by, bz + 0.016, 0.21, 0.41, 0.006)

    # 3 Nút bấm có đèn báo — bố cục dọc, cách đều nhau
    for i in range(3):
        cx, cy, cz = l_switch_positions[i]
        is_on = sw_states[i+1]

        # Nút nhấn (ngang x dọc: 0.17 x 0.10 — cùng tỉ lệ với nút quạt)
        draw_cube_center_sz(cx, cy, cz + 0.008, 0.17, 0.10, 0.009, (0.62, 0.62, 0.62))
        draw_cube_center_sz(cx, cy, cz + 0.013, 0.15, 0.09, 0.008,
                            (0.98, 0.98, 0.97) if is_on else (0.91, 0.91, 0.90))

        # Đèn LED báo trạng thái (bên phải nút)
        led_x = cx + 0.055
        if is_on: draw_cube_center_sz(led_x, cy, cz + 0.018, 0.016, 0.032, 0.004, (0.10, 0.95, 0.35))
        else:     draw_cube_center_sz(led_x, cy, cz + 0.018, 0.016, 0.032, 0.004, (0.95, 0.08, 0.08))

def draw_master_switch():
    bx, by, bz = MASTER_SW_X, MASTER_SW_Y, MASTER_SW_Z

    # === Hộp nhựa ngoài (viền xám đậm) ===
    glColor3f(0.25, 0.25, 0.25)
    drawBox(bx, by, bz + 0.010, 0.30, 0.40, 0.05)

    # === Mặt nhựa trong (xám sáng) ===
    glColor3f(0.80, 0.80, 0.80)
    drawBox(bx, by, bz + 0.036, 0.26, 0.36, 0.014)

    # === Đường rãnh trang trí hai bên ===
    glColor3f(0.55, 0.55, 0.55)
    drawBox(bx - 0.10, by, bz + 0.042, 0.03, 0.32, 0.006)
    drawBox(bx + 0.10, by, bz + 0.042, 0.03, 0.32, 0.006)

    # === Cần gạt Aptomat (to, nổi bật) ===
    if global_power_on:
        # BẬT: cần gạt lên trên, màu đỏ tươi
        glColor3f(0.85, 0.15, 0.10)
        glPushMatrix()
        glTranslatef(bx, by + 0.07, bz + 0.044)
        glRotatef(-18, 1, 0, 0)
        drawBox(0, 0, 0, 0.10, 0.17, 0.05)
        glPopMatrix()
        # Đèn LED xanh báo có điện
        glColor3f(0.05, 0.95, 0.25)
        drawBox(bx, by - 0.13, bz + 0.046, 0.06, 0.04, 0.008)
    else:
        # TẮT: cần gạt xuống dưới, màu đen
        glColor3f(0.12, 0.12, 0.12)
        glPushMatrix()
        glTranslatef(bx, by - 0.07, bz + 0.044)
        glRotatef(18, 1, 0, 0)
        drawBox(0, 0, 0, 0.10, 0.17, 0.05)
        glPopMatrix()
        # Đèn LED đỏ báo mất điện
        glColor3f(0.95, 0.10, 0.05)
        drawBox(bx, by - 0.13, bz + 0.046, 0.06, 0.04, 0.008)

    # === Nhãn chữ "MAIN" dạng khối nhỏ phía trên ===
    glColor3f(0.20, 0.20, 0.20)
    drawBox(bx - 0.035, by + 0.16, bz + 0.042, 0.014, 0.014, 0.005)
    drawBox(bx + 0.000, by + 0.16, bz + 0.042, 0.014, 0.014, 0.005)
    drawBox(bx + 0.035, by + 0.16, bz + 0.042, 0.014, 0.014, 0.005)

def draw_blackboard():
    set_color((0.6, 0.6, 0.65, 1.0)); drawBox(10.0, 3.0, 0.04, 10.4, 2.5, 0.08)
    set_color((0.08,0.12,0.08,1.0));  drawBox(10.0, 3.0, 0.045, 10.0, 2.2, 0.09)

def draw_portrait(tex_id):
    cx, cy = 16.5, 4.2
    set_color((0.85, 0.65, 0.10, 1.0)); drawBox(cx, cy, 0.04, 1.5, 1.8, 0.08)
    lx,rx = cx-0.65, cx+0.65; by,ty = cy-0.8, cy+0.8; z_front = 0.082
    if tex_id is not None:
        glEnable(GL_TEXTURE_2D); glBindTexture(GL_TEXTURE_2D, tex_id)
        set_color((1.0,1.0,1.0,1.0)) 
        # Đã bỏ glDisable(GL_LIGHTING) -> tranh sẽ tối khi tắt đèn
        glBegin(GL_QUADS); glNormal3f(0,0,1)
        glTexCoord2f(1.0,1.0); glVertex3f(rx,by,z_front); glTexCoord2f(0.0,1.0); glVertex3f(lx,by,z_front)
        glTexCoord2f(0.0,0.0); glVertex3f(lx,ty,z_front); glTexCoord2f(1.0,0.0); glVertex3f(rx,ty,z_front)
        glEnd(); glDisable(GL_TEXTURE_2D)
    else:
        set_color((0.90,0.92,0.95,1.0)); glBegin(GL_QUADS); glNormal3f(0,0,1)
        glVertex3f(rx,by,z_front); glVertex3f(lx,by,z_front); glVertex3f(lx,ty,z_front); glVertex3f(rx,ty,z_front); glEnd()

def draw_clock3D():
    now = datetime.now()
    second, minute, hour = now.second, now.minute, now.hour%12
    glPushMatrix(); glTranslatef(3.0, 4.2, 0.0)
    radius, depth = 0.7, 0.1
    qobj = gluNewQuadric(); gluQuadricNormals(qobj, GLU_SMOOTH)
    set_color((0.15,0.15,0.15,1.0)); gluCylinder(qobj, radius, radius, depth, 40, 1)
    glPushMatrix(); glRotatef(180,1,0,0); gluDisk(qobj,0,radius,40,1); glPopMatrix()
    glPushMatrix(); glTranslatef(0,0,depth); set_color((1.0,1.0,1.0,1.0)); gluDisk(qobj,0,radius,40,1)
    set_color((0.0,0.0,0.0,1.0)); drawBox(0,0,0.02,0.1,0.1,0.04)
    for i in range(12):
        ang = math.radians(i*30); px,py = math.sin(ang)*0.55, math.cos(ang)*0.55
        glPushMatrix(); glTranslatef(px,py,0.01); glRotatef(-i*30,0,0,1); drawBox(0,0,0,0.04,0.15,0.02); glPopMatrix()
    glPushMatrix(); glRotatef(-(hour*30+minute/2),0,0,1); glTranslatef(0,0.15,0.03); drawBox(0,0,0,0.06,0.3,0.02); glPopMatrix()
    glPushMatrix(); glRotatef(-(minute*6),0,0,1); glTranslatef(0,0.22,0.05); drawBox(0,0,0,0.04,0.45,0.02); glPopMatrix()
    set_color((1.0,0.0,0.0,1.0))
    glPushMatrix(); glRotatef(-(second*6),0,0,1); glTranslatef(0,0.27,0.07); drawBox(0,0,0,0.02,0.55,0.02); glPopMatrix()
    glPopMatrix(); glPopMatrix(); gluDeleteQuadric(qobj)

def draw_lights_3D():
    x_pos = {1: 5.0, 2: 10.0, 3: 15.0}
    z_pos = [4.0, 8.0, 12.0, 16.0, 20.0, 24.0]
    glDisable(GL_LIGHTING)
    for group_num, px in x_pos.items():
        is_lit = global_power_on and sw_states[group_num]
        for pz in z_pos:
            set_color((0.4,0.4,0.4,1.0)); drawBox(px, ROOM_H-0.05, pz, 1.4, 0.1, 2.6)
            if is_lit: set_color((1.0,1.0,1.0,1.0))
            else:      set_color((0.2,0.2,0.2,1.0))
            drawBox(px, ROOM_H-0.12, pz, 1.2, 0.04, 2.4)
    glEnable(GL_LIGHTING)

def drawChair(x, z):
    wood, metal = (0.55, 0.35, 0.15), (0.12, 0.12, 0.12)
    glColor3f(*metal)
    drawBox(x-0.35,0.4,z-0.35,0.05,0.8,0.05); drawBox(x+0.35,0.4,z-0.35,0.05,0.8,0.05)
    drawBox(x-0.35,0.4,z+0.35,0.05,0.8,0.05); drawBox(x+0.35,0.4,z+0.35,0.05,0.8,0.05)
    glColor3f(*wood); drawBox(x,0.85,z,0.9,0.08,0.9)
    glColor3f(*metal)
    drawBox(x-0.32,1.35,z+0.35,0.05,1,0.05); drawBox(x+0.32,1.35,z+0.35,0.05,1,0.05)
    glColor3f(*wood); drawBox(x,1.45,z+0.28,0.82,0.7,0.06)

def drawDesk(x, z):
    wood, metal = (0.58, 0.38, 0.18), (0.10, 0.10, 0.10)
    glColor3f(*wood); drawBox(x,1.15,z,2.2,0.12,1)
    glColor3f(*metal)
    drawBox(x-1,0.6,z-0.4,0.07,1.2,0.07); drawBox(x+1,0.6,z-0.4,0.07,1.2,0.07)
    drawBox(x-1,0.6,z+0.4,0.07,1.2,0.07); drawBox(x+1,0.6,z+0.4,0.07,1.2,0.07)

def drawStudents():
    columns = [-6.3, -2.1, 2.1, 6.3]
    startZ = 10.0 # Lùi dãy bàn xuống 3 ô
    for colX in columns:
        for r in range(5):
            z = startZ - r*3.0
            drawDesk(colX, z); drawChair(colX-0.6, z+1.6); drawChair(colX+0.6, z+1.6)

def drawPodium():
    glColor3f(0.72,0.72,0.72); drawBox(0,0.25,-8.5,20.0,0.5,3.0)
    glColor3f(0.55,0.55,0.55); drawBox(0,0.25,-6.9,20.2,0.5,0.2)

def drawTeacherTable():
    glColor3f(0.45, 0.28, 0.12)
    
    base_y = 0.5     # Cao độ của bục giảng (không đổi)
    extra_h = 0.1    # Tăng thêm chiều cao cho mặt bàn giáo viên
    z_shift = 0.5    # Kéo cụm bàn ghế tiến lên phía trước 0.5m cho đỡ sát tường
    
    # Vẽ mặt bàn (Đã nâng cao)
    drawBox(-6.0, 1.15 + base_y + extra_h, -8.5 + z_shift, 3.5, 0.15, 1.5)
    
    # Tính toán chiều dài 4 chân bàn
    leg_h = 1.2 + extra_h
    leg_y = base_y + leg_h / 2
    
    # Vẽ 4 chân bàn (Đã dời vị trí và kéo dài)
    drawBox(-7.6, leg_y, -9.1 + z_shift, 0.1, leg_h, 0.1)
    drawBox(-4.4, leg_y, -9.1 + z_shift, 0.1, leg_h, 0.1)
    drawBox(-7.6, leg_y, -7.9 + z_shift, 0.1, leg_h, 0.1)
    drawBox(-4.4, leg_y, -7.9 + z_shift, 0.1, leg_h, 0.1)
    
    # Ghế giáo viên (Đứng trên bục giảng base_y và tiến lên theo z_shift)
    glPushMatrix()
    glTranslatef(-6.0, base_y, -9.5 + z_shift)
    glRotatef(180, 0, 1, 0)
    drawChair(0, 0)
    glPopMatrix()

def draw_floor():
    cols_x, cols_z, grout = int(ROOM_W/TILE_S), int(ROOM_D/TILE_S), 0.02
    tile_a = TILE_S - grout
    glNormal3f(0,1,0); glEnable(GL_POLYGON_OFFSET_FILL); glPolygonOffset(1.0,1.0)
    set_color(C_TILE_GROUT)
    glBegin(GL_QUADS); glVertex3f(0,0,0); glVertex3f(ROOM_W,0,0); glVertex3f(ROOM_W,0,ROOM_D); glVertex3f(0,0,ROOM_D); glEnd()
    glDisable(GL_POLYGON_OFFSET_FILL)
    for iz in range(cols_z):
        for ix in range(cols_x):
            x0,z0 = ix*TILE_S+grout/2, iz*TILE_S+grout/2
            x1,z1 = x0+tile_a, z0+tile_a
            set_color(C_TILE_A if (ix+iz)%2==0 else C_TILE_B)
            glBegin(GL_QUADS); glVertex3f(x0,0.001,z0); glVertex3f(x1,0.001,z0); glVertex3f(x1,0.001,z1); glVertex3f(x0,0.001,z1); glEnd()

def draw_ceiling():
    set_color(C_CEIL); glNormal3f(0,-1,0)
    glBegin(GL_QUADS); glVertex3f(0,ROOM_H,0); glVertex3f(ROOM_W,ROOM_H,0); glVertex3f(ROOM_W,ROOM_H,ROOM_D); glVertex3f(0,ROOM_H,ROOM_D); glEnd()

def draw_walls():
    tw = 0.12; wl, wd = C_WALL_LIGHT, C_WALL_DARK

    set_color(wl); glNormal3f(0,0,1)
    glBegin(GL_QUADS)
    glVertex3f(0,0,0); glVertex3f(ROOM_W,0,0); glVertex3f(ROOM_W,ROOM_H,0); glVertex3f(0,ROOM_H,0)
    glEnd()

    set_color(wl); glNormal3f(0,0,-1)
    glBegin(GL_QUADS)
    glVertex3f(ROOM_W,0,ROOM_D); glVertex3f(0,0,ROOM_D); glVertex3f(0,ROOM_H,ROOM_D); glVertex3f(ROOM_W,ROOM_H,ROOM_D)
    glEnd()

    set_color(wd); glNormal3f(1,0,0)
    glBegin(GL_QUADS)
    glVertex3f(0,0,ROOM_D); glVertex3f(0,0,0); glVertex3f(0,1.5,0); glVertex3f(0,1.5,ROOM_D)
    glVertex3f(0,4.5,ROOM_D); glVertex3f(0,4.5,0); glVertex3f(0,ROOM_H,0); glVertex3f(0,ROOM_H,ROOM_D)
    glVertex3f(0,1.5,5.0); glVertex3f(0,1.5,0); glVertex3f(0,4.5,0); glVertex3f(0,4.5,5.0)
    glVertex3f(0,1.5,12.0); glVertex3f(0,1.5,9.0); glVertex3f(0,4.5,9.0); glVertex3f(0,4.5,12.0)
    glVertex3f(0,1.5,ROOM_D); glVertex3f(0,1.5,16.0); glVertex3f(0,4.5,16.0); glVertex3f(0,4.5,ROOM_D)
    glEnd()

    set_color(wd); glNormal3f(-1,0,0)
    glBegin(GL_QUADS)
    def wall_rect(y1, y2, z1, z2):
        glVertex3f(ROOM_W, y1, z1); glVertex3f(ROOM_W, y1, z2)
        glVertex3f(ROOM_W, y2, z2); glVertex3f(ROOM_W, y2, z1)

    wall_rect(4.5, ROOM_H, 0, ROOM_D)
    wall_rect(0, 1.5, 0, 5)
    wall_rect(0, 1.5, 7, 23)
    wall_rect(0, 1.5, 25, ROOM_D)
    wall_rect(1.5, 4.5, 0, 5)
    wall_rect(1.5, 4.5, 7, 10)
    wall_rect(1.5, 4.5, 14, 17)
    wall_rect(1.5, 4.5, 21, 23)
    wall_rect(1.5, 4.5, 25, ROOM_D)
    glEnd()

    set_color(C_TRIM); glNormal3f(0,1,1)
    glBegin(GL_QUADS)
    glVertex3f(0,0,0.001); glVertex3f(ROOM_W,0,0.001); glVertex3f(ROOM_W,tw,0.001); glVertex3f(0,tw,0.001)
    glVertex3f(0,0,ROOM_D-0.001); glVertex3f(ROOM_W,0,ROOM_D-0.001); glVertex3f(ROOM_W,tw,ROOM_D-0.001); glVertex3f(0,tw,ROOM_D-0.001)
    glVertex3f(0.001,0,0); glVertex3f(0.001,0,ROOM_D); glVertex3f(0.001,tw,ROOM_D); glVertex3f(0.001,tw,0)
    glVertex3f(ROOM_W-0.001,0,ROOM_D); glVertex3f(ROOM_W-0.001,0,0); glVertex3f(ROOM_W-0.001,tw,0); glVertex3f(ROOM_W-0.001,tw,ROOM_D)
    glEnd()


# ═══════════════════════════════════════════════
#  TỐI ƯU HOÁ FPS BẰNG DISPLAY LIST
# ═══════════════════════════════════════════════
def build_display_lists():
    global dl_static
    dl_static = glGenLists(1)
    glNewList(dl_static, GL_COMPILE)
    draw_floor()
    draw_ceiling()
    draw_walls()
    draw_blackboard()
    glPushMatrix()
    glTranslatef(ROOM_W/2, 0, 10.0)
    drawStudents()
    drawPodium()
    drawTeacherTable()
    glPopMatrix()
    glEndList()
dl_books = None

def compile_books_list():
    global dl_books
    if dl_books is None:
        dl_books = glGenLists(1)
    
    glNewList(dl_books, GL_COMPILE)
    for b in books:
        if not b["is_taken"]:
            bxb=b["x"]; byb=b["y"]; bzb=b["z"]; bwb=b["w"]; bhb=b["h"]; bdb=b["d"]
            
            # Giấy trắng (lõi trong)
            set_color((0.92, 0.92, 0.92, 1.0))
            drawBox(bxb, byb + bhb/2, bzb + 0.002, bwb - 0.008, bhb - 0.01, bdb - 0.004)
            
            # Bìa màu
            set_color(b["color"])
            drawBox(bxb, byb + bhb/2, bzb - bdb/2 + 0.002, bwb, bhb, 0.004)       # Gáy sách
            drawBox(bxb - bwb/2 + 0.002, byb + bhb/2, bzb, 0.004, bhb, bdb) # Bìa trái
            drawBox(bxb + bwb/2 - 0.002, byb + bhb/2, bzb, 0.004, bhb, bdb) # Bìa phải
    glEndList()

def load_texture(image_path):
    try: surface = pygame.image.load(image_path)
    except pygame.error: return None
    surface = pygame.transform.flip(surface, False, True)
    image_data = pygame.image.tostring(surface, "RGBA", True)
    width, height = surface.get_width(), surface.get_height()
    tex_id = glGenTextures(1); glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR); glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
    return tex_id

def setup_lighting():
    glEnable(GL_LIGHTING); glEnable(GL_COLOR_MATERIAL); glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE); glShadeModel(GL_SMOOTH)

def update_lighting():
    # Sửa dòng này:
    active_groups = sum([sw_states[1],sw_states[2],sw_states[3]]) if global_power_on else 0
    brightness = 0.20 + (active_groups * 0.26)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [brightness,brightness,brightness,1.0])
    glClearColor(0.82*brightness, 0.88*brightness, 0.96*brightness, 1.0)

def apply_camera():
    glLoadIdentity(); glRotatef(cam["pitch"], 1, 0, 0); glRotatef(cam["yaw"], 0, 1, 0); glTranslatef(-cam["x"], -cam["y"], -cam["z"])

def move_camera(keys, dt):
    # Nhân tốc độ với dt
    sp = (cam["speed"] * 2.5 if keys[K_LSHIFT] else cam["speed"]) * dt
    yr = math.radians(cam["yaw"])
    fwd_x, fwd_z   =  math.sin(yr), -math.cos(yr)
    right_x, right_z = math.cos(yr),  math.sin(yr)
    
    if keys[K_w]: cam["x"] += fwd_x * sp;   cam["z"] += fwd_z * sp
    if keys[K_s]: cam["x"] -= fwd_x * sp;   cam["z"] -= fwd_z * sp
    if keys[K_a]: cam["x"] -= right_x * sp; cam["z"] -= right_z * sp
    if keys[K_d]: cam["x"] += right_x * sp; cam["z"] += right_z * sp
    if keys[K_SPACE]: cam["y"] += sp
    if keys[K_LCTRL]: cam["y"] -= sp

def main():
    global mouse_down, last_mouse, held_book_id, global_power_on
    pygame.init()
    mx, my = pygame.mouse.get_rel()
    pygame.display.gl_set_attribute(pygame.GL_SWAP_CONTROL, 1)

    pygame.display.set_mode(
        (WIN_W, WIN_H),
        DOUBLEBUF | OPENGL | RESIZABLE | HWSURFACE
)
    pygame.display.set_caption("Lớp Học 3D - Tối ưu FPS & Sách")

    glMatrixMode(GL_PROJECTION); glLoadIdentity(); gluPerspective(60, WIN_W/WIN_H, 0.05, 200.0); glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST); glEnable(GL_NORMALIZE); glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDisable(GL_DITHER)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_FASTEST)
    glHint(GL_POLYGON_SMOOTH_HINT, GL_FASTEST)
    setup_lighting()
    init_books()
    build_display_lists() # Khởi tạo danh sách các chi tiết tĩnh (giúp tăng vọt FPS)
    
    my_photo_tex = load_texture("anh_Bac_Ho.jpg")
    clock = pygame.time.Clock(); dt = 1/60.0

    while True:
        # Cập nhật Animation cửa sổ
        for key in win_open.keys():
            target = 1.9 if win_open[key] else 0.0
            win_anim[key] += (target - win_anim[key]) * 0.2

        # Cập nhật Animation tủ kính (mượt y hệt cửa phòng)
        for bc_id in [1, 2]:
            target = 120.0 if bookcase_states[bc_id] else 0.0
            diff = target - bc_anim[bc_id]
            if abs(diff) > 0.1: bc_anim[bc_id] += min(150.0*dt, abs(diff)) * (1 if diff>0 else -1)
            else: bc_anim[bc_id] = target

        # Cập nhật Animation cửa chính
        for d in door_states.values():
            diff_l = d["l_tgt"] - d["l_ang"]
            if abs(diff_l) > 0.1: d["l_ang"] += min(120.0*dt, abs(diff_l)) * (1 if diff_l>0 else -1)
            else: d["l_ang"] = d["l_tgt"]
            diff_r = d["r_tgt"] - d["r_ang"]
            if abs(diff_r) > 0.1: d["r_ang"] += min(120.0*dt, abs(diff_r)) * (1 if diff_r>0 else -1)
            else: d["r_ang"] = d["r_tgt"]

        # Cập nhật Animation Quạt xoay
        for i in range(4):
            # Thêm điều kiện global_power_on
            if fan_on[i] and global_power_on: 
                fan_angle[i] = (fan_angle[i] + 25) % 360 # Quay tít hơn
        for event in pygame.event.get():
            if event.type == QUIT: pygame.quit(); sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE: pygame.quit(); sys.exit()
                if event.key == K_1: sw_states[1] = not sw_states[1]
                if event.key == K_2: sw_states[2] = not sw_states[2]
                if event.key == K_3: sw_states[3] = not sw_states[3]
                if event.key == K_4: sw_states[4] = not sw_states[4]
                if event.key == K_q: fan_on[0] = not fan_on[0]
                if event.key == K_e: fan_on[1] = not fan_on[1]
                if event.key == K_r: fan_on[2] = not fan_on[2]
                if event.key == K_f: fan_on[3] = not fan_on[3]
                if event.key in (K_5, K_KP5): bookcase_states[1] = not bookcase_states[1]
                if event.key in (K_6, K_KP6): bookcase_states[2] = not bookcase_states[2]

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 3: mouse_down = True; last_mouse = pygame.mouse.get_pos()
                elif event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    if held_book_id is not None:
                        book_w, book_h = 460, 300
                        cx_hud = WIN_W - book_w/2 - 40; cy_hud = book_h/2 + 40
                        my_gl = WIN_H - my
                        if (cx_hud-book_w/2-10<=mx<=cx_hud+book_w/2+10) and (cy_hud-book_h/2-10<=my_gl<=cy_hud+book_h/2+10):
                            for b in books:
                                if b["id"] == held_book_id: b["is_taken"] = False
                            held_book_id = None
                            compile_books_list()
                        continue
                    check_interact(mx, my)

            if event.type == MOUSEBUTTONUP:
                if event.button == 3: mouse_down = False

            if event.type == MOUSEMOTION and mouse_down:
                mx, my = pygame.mouse.get_pos()
                cam["yaw"] += (mx - last_mouse[0]) * cam["sens"]
                cam["pitch"] += (my - last_mouse[1]) * cam["sens"]
                cam["pitch"] = max(-89, min(89, cam["pitch"]))
                last_mouse = (mx, my)

        move_camera(pygame.key.get_pressed(),dt)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        apply_camera(); update_lighting()

        # Render Môi trường Tĩnh qua Display List
        glCallList(dl_static)

        # Render các Vật thể Động
        draw_windows()
        draw_portrait(my_photo_tex)
        draw_master_switch()    # <---- GỌI Ở ĐÂY
        draw_light_switches()   # <---- GỌI Ở ĐÂY
        draw_fan_switch_box()
        draw_clock3D()
        draw_lights_3D()
        draw_bookcases()

        for d in door_states.values(): draw_the_door(d["cz"], d["l_ang"], d["r_ang"])
        for i in range(4): draw_fan(fan_pos[i][0], fan_pos[i][1], fan_angle[i])
        draw_windows()
        draw_hud()

        pygame.display.flip()
        fps = clock.get_fps()
        pygame.display.set_caption(f"FPS: {fps:.1f}")
        dt = clock.tick_busy_loop(144) / 1000

if __name__ == "__main__":
    main()