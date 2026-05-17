"""
Mô hình phòng học 3D - Tối ưu hoá Framerate với Display List
  - 4 Cửa sổ trượt, 2 Cửa ra vào (cao 4.5m, dời né bục giảng)
  - 4 Quạt trần to & xoay nhanh, xen kẽ hàng đèn, đúng công tắc
  - Sách tủ có lõi giấy trắng, cửa tủ mở mượt mà
  - Lùi dãy bàn 3 ô gạch
  - Phấn + bông lau bảng: nhặt phấn → vẽ lên bảng, nhặt bông → lau sạch
  - Có thùng rác lưới nhựa đỏ ở góc cuối lớp
  - Sửa lỗi tay nắm cửa trong/ngoài
  - XÓA TOÀN BỘ PHÍM TẮT ĐIỀU KHIỂN - CHỈ TƯƠNG TÁC BẰNG CLICK CHUỘT
  - Phiên bản: Lập trình Hướng Đối Tượng (OOP)

Điều khiển chung:
  - W/A/S/D, Space, Ctrl: Di chuyển camera
  - Chuột phải (giữ) + Di chuột: Xoay góc nhìn camera
  - Click chuột trái: Bật/tắt điện, quạt, mở/đóng cửa, tủ sách, nhặt/thả phấn/sách...
"""

import sys
import math
import random
import ctypes
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from datetime import datetime


# ══════════════════════════════════════════════
#  HẰNG SỐ TOÀN CỤC
# ══════════════════════════════════════════════
ROOM_W = 20.0
ROOM_D = 26.0
ROOM_H = 6.0
TILE_S = 1.0
WIN_W, WIN_H = 1200, 750

C_WALL_LIGHT = (0.88, 0.82, 0.70, 1.0)
C_WALL_DARK  = (0.78, 0.72, 0.60, 1.0)
C_TILE_A     = (0.95, 0.93, 0.88, 1.0)
C_TILE_B     = (0.80, 0.76, 0.68, 1.0)
C_TILE_GROUT = (0.55, 0.52, 0.48, 1.0)
C_CEIL       = (1.0,  0.97, 0.78, 1.0)
C_TRIM       = (0.65, 0.55, 0.40, 1.0)
C_GLASS      = (0.60, 0.80, 0.90, 0.35)

DOOR_W  = 2.0
DOOR_H  = 4.4
DOOR_D  = 0.04
LEAF_W  = DOOR_W / 2
FRAME_D = 0.08
FRAME_W = 0.1
C_FRAME     = (0.45, 0.30, 0.15, 1.0)
C_DOOR      = (0.55, 0.38, 0.20, 1.0)
C_DOOR_DARK = (0.40, 0.25, 0.10, 1.0)
C_PANEL     = (0.50, 0.35, 0.18, 1.0)
C_HANDLE    = (0.85, 0.85, 0.90, 1.0)
C_HINGE     = (0.20, 0.20, 0.20, 1.0)

MASTER_SW_X, MASTER_SW_Y, MASTER_SW_Z = 17.05, 2.25, 0.02
LIGHT_SW_X,  LIGHT_SW_Y,  LIGHT_SW_Z  = 17.65, 2.25, 0.02
FAN_SW_X,    FAN_SW_Y,    FAN_SW_Z    = 18.19, 2.25, 0.02

BB_CX,  BB_CY,  BB_CZ   = 10.0, 3.0, 0.0     
BB_W,   BB_H            = 10.0, 2.2            
BB_TEX_W, BB_TEX_H      = 1024, 512            

TRAY_CX, TRAY_Y, TRAY_CZ = BB_CX, BB_CY - BB_H/2 - 0.10, 0.12
CHALK_X,  CHALK_Z  = TRAY_CX - 2.0, TRAY_CZ
ERASER_X, ERASER_Z = TRAY_CX + 2.0, TRAY_CZ


# ══════════════════════════════════════════════
#  LỚP TIỆN ÍCH VẼ (Renderer)
# ══════════════════════════════════════════════
class Renderer:
    @staticmethod
    def set_color(rgba):
        if len(rgba) == 3: glColor3f(*rgba)
        else: glColor4f(*rgba)

    @staticmethod
    def draw_box(x, y, z, w, h, d):
        x1, x2 = x - w/2, x + w/2
        y1, y2 = y - h/2, y + h/2
        z1, z2 = z - d/2, z + d/2
        glBegin(GL_QUADS)
        glNormal3f(0,  0,  1);  glVertex3f(x1,y1,z2); glVertex3f(x2,y1,z2); glVertex3f(x2,y2,z2); glVertex3f(x1,y2,z2)
        glNormal3f(0,  0, -1);  glVertex3f(x2,y1,z1); glVertex3f(x1,y1,z1); glVertex3f(x1,y2,z1); glVertex3f(x2,y2,z1)
        glNormal3f(-1, 0,  0);  glVertex3f(x1,y1,z1); glVertex3f(x1,y1,z2); glVertex3f(x1,y2,z2); glVertex3f(x1,y2,z1)
        glNormal3f(1,  0,  0);  glVertex3f(x2,y1,z2); glVertex3f(x2,y1,z1); glVertex3f(x2,y2,z1); glVertex3f(x2,y2,z2)
        glNormal3f(0,  1,  0);  glVertex3f(x1,y2,z2); glVertex3f(x2,y2,z2); glVertex3f(x2,y2,z1); glVertex3f(x1,y2,z1)
        glNormal3f(0, -1,  0);  glVertex3f(x1,y1,z1); glVertex3f(x2,y1,z1); glVertex3f(x2,y1,z2); glVertex3f(x1,y1,z2)
        glEnd()

    @staticmethod
    def draw_box_coords(x1, x2, y1, y2, z1, z2, color):
        Renderer.set_color(color)
        glBegin(GL_QUADS)
        glNormal3f(-1,0,0); glVertex3f(x1,y1,z1); glVertex3f(x1,y1,z2); glVertex3f(x1,y2,z2); glVertex3f(x1,y2,z1)
        glNormal3f(1, 0,0); glVertex3f(x2,y1,z1); glVertex3f(x2,y1,z2); glVertex3f(x2,y2,z2); glVertex3f(x2,y2,z1)
        glNormal3f(0,0,-1); glVertex3f(x1,y2,z1); glVertex3f(x2,y2,z1); glVertex3f(x2,y2,z2); glVertex3f(x1,y2,z2)
        glNormal3f(0,0, 1); glVertex3f(x1,y1,z1); glVertex3f(x2,y1,z1); glVertex3f(x2,y1,z2); glVertex3f(x1,y1,z2)
        glNormal3f(0,-1,0); glVertex3f(x1,y1,z1); glVertex3f(x2,y1,z1); glVertex3f(x2,y2,z1); glVertex3f(x1,y2,z1)
        glNormal3f(0, 1,0); glVertex3f(x1,y1,z2); glVertex3f(x2,y1,z2); glVertex3f(x2,y2,z2); glVertex3f(x1,y2,z2)
        glEnd()

    @staticmethod
    def draw_box_corner(x, y, z, w, h, d, color, dark_color=None):
        if dark_color is None:
            dark_color = (color[0]*0.7, color[1]*0.7, color[2]*0.7, 1.0)
        x0, x1 = x, x + w
        y0, y1 = y, y + h
        z0, z1 = z - d/2, z + d/2
        glBegin(GL_QUADS)
        glColor4f(*color);      glNormal3f(0,  0,  1);  glVertex3f(x0,y0,z1); glVertex3f(x1,y0,z1); glVertex3f(x1,y1,z1); glVertex3f(x0,y1,z1)
        glColor4f(*dark_color); glNormal3f(0,  0, -1);  glVertex3f(x1,y0,z0); glVertex3f(x0,y0,z0); glVertex3f(x0,y1,z0); glVertex3f(x1,y1,z0)
        glColor4f(*color);      glNormal3f(0,  1,  0);  glVertex3f(x0,y1,z0); glVertex3f(x1,y1,z0); glVertex3f(x1,y1,z1); glVertex3f(x0,y1,z1)
        glColor4f(*dark_color); glNormal3f(0, -1,  0);  glVertex3f(x0,y0,z1); glVertex3f(x1,y0,z1); glVertex3f(x1,y0,z0); glVertex3f(x0,y0,z0)
        glColor4f(color[0]*0.9,      color[1]*0.9,      color[2]*0.9,      1.0); glNormal3f(1,0,0);  glVertex3f(x1,y0,z1); glVertex3f(x1,y0,z0); glVertex3f(x1,y1,z0); glVertex3f(x1,y1,z1)
        glColor4f(dark_color[0]*0.9, dark_color[1]*0.9, dark_color[2]*0.9, 1.0); glNormal3f(-1,0,0); glVertex3f(x0,y0,z0); glVertex3f(x0,y0,z1); glVertex3f(x0,y1,z1); glVertex3f(x0,y1,z0)
        glEnd()

    @staticmethod
    def draw_cylinder(x, y, z, radius, height, axis='z', segments=16, color=(1,1,1,1)):
        glColor4f(*color)
        glPushMatrix()
        glTranslatef(x, y, z)
        if   axis == 'y': glRotatef(-90, 1, 0, 0)
        elif axis == 'x': glRotatef(90, 0, 1, 0)
        quad = gluNewQuadric()
        gluCylinder(quad, radius, radius, height, segments, 1)
        gluDisk(quad, 0, radius, segments, 1)
        glTranslatef(0, 0, height)
        gluDisk(quad, 0, radius, segments, 1)
        gluDeleteQuadric(quad)
        glPopMatrix()


# ══════════════════════════════════════════════
#  BẢNG ĐEN — DYNAMIC TEXTURE
# ══════════════════════════════════════════════
class Blackboard:
    BG_COLOR   = (20,  30,  20,  255)
    CHALK_COLOR = (240, 240, 230, 255)

    def __init__(self):
        self.tex_id  = None
        self.surface = pygame.Surface((BB_TEX_W, BB_TEX_H), pygame.SRCALPHA)
        self.surface.fill(self.BG_COLOR)
        self.dirty   = True
        self.chalk_color = self.CHALK_COLOR

    def init_texture(self):
        self.tex_id = int(glGenTextures(1))
        glBindTexture(GL_TEXTURE_2D, self.tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        self._upload_full()

    def _upload_full(self):
        data = pygame.image.tostring(self.surface, "RGBA", False)
        glBindTexture(GL_TEXTURE_2D, self.tex_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, BB_TEX_W, BB_TEX_H, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)

    def _upload_dirty(self):
        data = pygame.image.tostring(self.surface, "RGBA", False)
        glBindTexture(GL_TEXTURE_2D, self.tex_id)
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, BB_TEX_W, BB_TEX_H, GL_RGBA, GL_UNSIGNED_BYTE, data)
        self.dirty = False

    def world_to_pixel(self, hit_x, hit_y):
        u = (hit_x - (BB_CX - BB_W/2)) / BB_W
        v = (hit_y - (BB_CY - BB_H/2)) / BB_H
        if not (0.0 <= u <= 1.0 and 0.0 <= v <= 1.0): return None
        px = int(u * (BB_TEX_W - 1))
        py = int((1.0 - v) * (BB_TEX_H - 1))
        return px, py

    def draw_chalk(self, hit_x, hit_y, radius=2):
        pt = self.world_to_pixel(hit_x, hit_y)
        if pt is None: return False
        px, py = pt
        pygame.draw.circle(self.surface, self.chalk_color, (px, py), radius)
        for _ in range(2):
            nx = px + random.randint(-radius, radius)
            ny = py + random.randint(-radius, radius)
            alpha = random.randint(80, 180)
            c = (*self.chalk_color[:3], alpha)
            pygame.draw.circle(self.surface, c, (nx, ny), max(1, radius//3))
        self.dirty = True
        return True

    def erase(self, hit_x, hit_y, radius=22):
        pt = self.world_to_pixel(hit_x, hit_y)
        if pt is None: return False
        pygame.draw.circle(self.surface, self.BG_COLOR, pt, radius)
        self.dirty = True
        return True

    def sync_texture(self):
        if self.dirty and self.tex_id is not None:
            self._upload_dirty()

    def draw(self, chalk_tool=None):
        R = Renderer
        R.set_color((0.6, 0.6, 0.65, 1.0))
        R.draw_box(BB_CX, BB_CY, 0.04, BB_W + 0.4, BB_H + 0.3, 0.08)
        R.set_color((0.35, 0.22, 0.10, 1.0))
        R.draw_box(BB_CX, TRAY_Y, TRAY_CZ, BB_W + 0.4, 0.08, 0.18)
        
        if chalk_tool is None or not chalk_tool.has_chalk:
            R.set_color((0.95, 0.95, 0.90, 1.0))
            R.draw_box(CHALK_X, TRAY_Y + 0.06, CHALK_Z, 0.28, 0.06, 0.10)
            R.draw_cylinder(CHALK_X - 0.06, TRAY_Y + 0.06, CHALK_Z,
                            0.018, 0.32, 'x', 8, (0.98, 0.98, 0.98, 1.0))

        if chalk_tool is None or not chalk_tool.has_eraser:
            R.set_color((0.75, 0.60, 0.45, 1.0))
            R.draw_box(ERASER_X, TRAY_Y + 0.06, ERASER_Z, 0.32, 0.07, 0.14)
            R.set_color((0.92, 0.90, 0.88, 1.0))   
            R.draw_box(ERASER_X, TRAY_Y + 0.095, ERASER_Z, 0.30, 0.02, 0.12)

        if self.tex_id is not None:
            glEnable(GL_TEXTURE_2D); glBindTexture(GL_TEXTURE_2D, self.tex_id)
            glDisable(GL_LIGHTING); glColor4f(1.0, 1.0, 1.0, 1.0)
            x0 = BB_CX - BB_W / 2; x1 = BB_CX + BB_W / 2
            y0 = BB_CY - BB_H / 2; y1 = BB_CY + BB_H / 2
            z_face = 0.092   
            glBegin(GL_QUADS)
            glNormal3f(0, 0, 1)
            glTexCoord2f(0, 1); glVertex3f(x0, y0, z_face)
            glTexCoord2f(1, 1); glVertex3f(x1, y0, z_face)
            glTexCoord2f(1, 0); glVertex3f(x1, y1, z_face)
            glTexCoord2f(0, 0); glVertex3f(x0, y1, z_face)
            glEnd()
            glDisable(GL_TEXTURE_2D); glEnable(GL_LIGHTING)
        else:
            R.set_color((0.08, 0.12, 0.08, 1.0))
            R.draw_box(BB_CX, BB_CY, 0.092, BB_W, BB_H, 0.01)


# ══════════════════════════════════════════════
#  PHẤN & BÔNG LAU (vật cầm trên tay)
# ══════════════════════════════════════════════
class ChalkTool:
    NONE   = 0
    CHALK  = 1
    ERASER = 2

    def __init__(self): self.held = self.NONE
    def pick_chalk(self): self.held = self.CHALK
    def pick_eraser(self): self.held = self.ERASER
    def drop(self): self.held = self.NONE
    @property
    def has_chalk(self): return self.held == self.CHALK
    @property
    def has_eraser(self): return self.held == self.ERASER
    @property
    def holding_something(self): return self.held != self.NONE

    def draw_in_hand(self):
        if not self.holding_something: return
        R = Renderer
        glDisable(GL_DEPTH_TEST) 
        glDisable(GL_LIGHTING)   
        glPushMatrix(); glLoadIdentity() 
        glTranslatef(0.15, -0.15, -0.4) 
        glRotatef(-30, 0, 0, 1); glRotatef(30, 1, 0, 0)  
        
        if self.has_chalk:
            R.draw_cylinder(0, -0.04, 0, 0.01, 0.14, 'y', 8, (0.98, 0.98, 0.98, 1.0))
        elif self.has_eraser:
            glRotatef(45, 0, 1, 0) 
            R.set_color((0.75, 0.60, 0.45, 1.0)); R.draw_box(0, 0, 0, 0.12, 0.03, 0.06)
            R.set_color((0.92, 0.90, 0.88, 1.0)); R.draw_box(0, 0.02, 0, 0.11, 0.01, 0.05)
            
        glPopMatrix(); glEnable(GL_LIGHTING); glEnable(GL_DEPTH_TEST)


# ══════════════════════════════════════════════
#  CAMERA
# ══════════════════════════════════════════════
class Camera:
    def __init__(self):
        self.x, self.y, self.z = ROOM_W / 2, 2.5, ROOM_D - 5.0
        self.yaw, self.pitch = 0.0, -5.0
        self.speed, self.sens = 14.0, 0.25

    def apply(self):
        glLoadIdentity()
        glRotatef(self.pitch, 1, 0, 0)
        glRotatef(self.yaw,   0, 1, 0)
        glTranslatef(-self.x, -self.y, -self.z)

    def move(self, keys, dt):
        sp = (self.speed * 2.5 if keys[K_LSHIFT] else self.speed) * dt
        yr = math.radians(self.yaw)
        fwd_x,   fwd_z   =  math.sin(yr), -math.cos(yr)
        right_x, right_z =  math.cos(yr),  math.sin(yr)
        if keys[K_w]:     self.x += fwd_x   * sp; self.z += fwd_z   * sp
        if keys[K_s]:     self.x -= fwd_x   * sp; self.z -= fwd_z   * sp
        if keys[K_a]:     self.x -= right_x * sp; self.z -= right_z * sp
        if keys[K_d]:     self.x += right_x * sp; self.z += right_z * sp
        if keys[K_SPACE]: self.y += sp
        if keys[K_LCTRL]: self.y -= sp

    def rotate(self, dx, dy):
        self.yaw   += dx * self.sens
        self.pitch += dy * self.sens
        self.pitch  = max(-89.0, min(89.0, self.pitch))


# ══════════════════════════════════════════════
#  QUẠT TRẦN, CỬA RA VÀO, CỬA SỔ, TỦ SÁCH
# ══════════════════════════════════════════════
class Fan:
    def __init__(self, x, z):
        self.x, self.z = x, z
        self.angle, self.on = 0.0, False

    def update(self, power_on):
        if self.on and power_on: self.angle = (self.angle + 25) % 360

    def draw(self):
        R = Renderer
        C_BODY, C_MOTOR, C_DARK, C_POLE = (0.88, 0.88, 0.85), (0.75, 0.75, 0.73), (0.55, 0.55, 0.53), (0.70, 0.70, 0.68)
        pole_h, motor_r, motor_h, cap_h = 0.28, 0.13, 0.18, 0.07
        blade_y = ROOM_H - pole_h - motor_h - 0.01

        glPushMatrix(); glTranslatef(self.x, 0, self.z)
        R.draw_cylinder(0, ROOM_H - pole_h, 0, 0.018, pole_h, 'y', 10, (*C_POLE, 1.0))
        R.draw_cylinder(0, ROOM_H - 0.04,   0, 0.06,  0.04,   'y', 16, (*C_BODY, 1.0))
        R.draw_cylinder(0, ROOM_H - pole_h - motor_h, 0, motor_r, motor_h, 'y', 24, (*C_MOTOR, 1.0))
        for rib in [0.04, 0.09, 0.14]: R.draw_cylinder(0, ROOM_H - pole_h - motor_h + rib, 0, motor_r + 0.008, 0.015, 'y', 24, (*C_DARK, 1.0))
        R.draw_cylinder(0, blade_y - cap_h, 0, motor_r * 0.75, cap_h, 'y', 20, (*C_BODY, 1.0))
        hub_r = 0.045
        glPushMatrix(); glTranslatef(0, blade_y, 0); glRotatef(self.angle, 0, 1, 0)
        for i in range(3):
            glPushMatrix(); glRotatef(i * 120, 0, 1, 0); glTranslatef(hub_r, 0, 0); self._draw_blade(); glPopMatrix()
        R.draw_cylinder(0, -0.01, 0, hub_r, 0.022, 'y', 16, (*C_DARK, 1.0))
        glPopMatrix(); glPopMatrix()

    @staticmethod
    def _draw_blade(length=1.5):
        C_BLADE, C_BLADE_BOT = (0.91, 0.91, 0.88, 1.0), (0.80, 0.80, 0.78, 1.0)
        root_w, tip_w, thick = 0.10, 0.26, 0.012
        x0, x1 = 0.0, length
        yr0, yr1, yt0, yt1 = -root_w, root_w, -tip_w, tip_w
        zt, zb   =  thick/2, -thick/2
        glBegin(GL_QUADS)
        glColor4f(*C_BLADE);     glNormal3f(0, 1, 0);  glVertex3f(x0,zt,yr0); glVertex3f(x0,zt,yr1); glVertex3f(x1,zt,yt1); glVertex3f(x1,zt,yt0)
        glColor4f(*C_BLADE_BOT); glNormal3f(0,-1, 0);  glVertex3f(x0,zb,yr0); glVertex3f(x1,zb,yt0); glVertex3f(x1,zb,yt1); glVertex3f(x0,zb,yr1)
        glColor4f(*C_BLADE);     glNormal3f(0, 0, 1);  glVertex3f(x0,zb,yr1); glVertex3f(x1,zb,yt1); glVertex3f(x1,zt,yt1); glVertex3f(x0,zt,yr1)
        glColor4f(*C_BLADE_BOT); glNormal3f(0, 0,-1);  glVertex3f(x0,zt,yr0); glVertex3f(x1,zt,yt0); glVertex3f(x1,zb,yt0); glVertex3f(x0,zb,yr0)
        glColor4f(*C_BLADE);     glNormal3f(1, 0, 0);  glVertex3f(x1,zb,yt0); glVertex3f(x1,zt,yt0); glVertex3f(x1,zt,yt1); glVertex3f(x1,zb,yt1)
        glEnd()

class Door:
    def __init__(self, door_id, cz):
        self.door_id, self.cz = door_id, cz
        self.l_ang, self.l_tgt, self.l_open = 0.0, 0.0, False
        self.r_ang, self.r_tgt, self.r_open = 0.0, 0.0, False

    def update(self, dt):
        for side in ('l', 'r'):
            ang = getattr(self, f'{side}_ang')
            tgt = getattr(self, f'{side}_tgt')
            diff = tgt - ang
            if abs(diff) > 0.1: ang += min(120.0 * dt, abs(diff)) * (1 if diff > 0 else -1)
            else: ang = tgt
            setattr(self, f'{side}_ang', ang)

    def toggle_left(self): self.l_open = not self.l_open; self.l_tgt = 105.0 if self.l_open else 0.0
    def toggle_right(self): self.r_open = not self.r_open; self.r_tgt = 105.0 if self.r_open else 0.0
    def toggle_both(self): self.toggle_left(); self.toggle_right()

    def draw(self):
        R = Renderer
        glPushMatrix(); glTranslatef(ROOM_W, 0.0, self.cz); glRotatef(-90, 0, 1, 0)
        R.draw_box_corner(-DOOR_W/2 - FRAME_W, 0, 0, FRAME_W, DOOR_H + FRAME_W, FRAME_D, C_FRAME)
        R.draw_box_corner( DOOR_W/2, 0, 0, FRAME_W, DOOR_H + FRAME_W, FRAME_D, C_FRAME)
        R.draw_box_corner(-DOOR_W/2, DOOR_H, 0, DOOR_W, FRAME_W, FRAME_D, C_FRAME)
        glPushMatrix(); glTranslatef(-DOOR_W/2, 0, 0); glRotatef(self.l_ang, 0, 1, 0); self._draw_leaf(is_left=True); glPopMatrix()
        glPushMatrix(); glTranslatef(DOOR_W/2, 0, 0);  glRotatef(-self.r_ang, 0, 1, 0); self._draw_leaf(is_left=False); glPopMatrix()
        glPopMatrix()

    def draw_glass(self):
        """Pass trong suốt — gọi SAU khi đã vẽ hết vật đặc."""
        glPushMatrix(); glTranslatef(ROOM_W, 0.0, self.cz); glRotatef(-90, 0, 1, 0)
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA); glDepthMask(GL_FALSE)
        glass_h = DOOR_H - 1.27
        glPushMatrix(); glTranslatef(-DOOR_W/2, 0, 0); glRotatef(self.l_ang, 0, 1, 0)
        Renderer.draw_box_corner(0.12, 1.15, -0.005, LEAF_W-0.24, glass_h, 0.01, C_GLASS, C_GLASS)
        glPopMatrix()
        glPushMatrix(); glTranslatef(DOOR_W/2, 0, 0); glRotatef(-self.r_ang, 0, 1, 0)
        Renderer.draw_box_corner(-LEAF_W+0.12, 1.15, -0.005, LEAF_W-0.24, glass_h, 0.01, C_GLASS, C_GLASS)
        glPopMatrix()
        glDepthMask(GL_TRUE); glDisable(GL_BLEND)
        glPopMatrix()

    @staticmethod
    def _draw_leaf(is_left=True):
        R, offset_x = Renderer, 0 if is_left else -LEAF_W
        R.draw_box_corner(offset_x, 0, -DOOR_D/2, 0.12, DOOR_H, DOOR_D, C_DOOR, C_DOOR_DARK)
        R.draw_box_corner(offset_x+LEAF_W-0.12, 0, -DOOR_D/2, 0.12, DOOR_H, DOOR_D, C_DOOR, C_DOOR_DARK)
        R.draw_box_corner(offset_x+0.12, 0, -DOOR_D/2, LEAF_W-0.24, 0.20, DOOR_D, C_DOOR, C_DOOR_DARK)
        R.draw_box_corner(offset_x+0.12, 1.0, -DOOR_D/2, LEAF_W-0.24, 0.15, DOOR_D, C_DOOR, C_DOOR_DARK)
        R.draw_box_corner(offset_x+0.12, DOOR_H-0.12, -DOOR_D/2, LEAF_W-0.24, 0.12, DOOR_D, C_DOOR, C_DOOR_DARK)
        
        glass_h = DOOR_H - 1.27
        R.draw_box_corner(offset_x+LEAF_W/2-0.02, 1.15, -DOOR_D/2, 0.04, glass_h, DOOR_D, C_DOOR, C_DOOR_DARK)
        for i in range(1, int(glass_h / 0.5) + 1):
            R.draw_box_corner(offset_x+0.12, 1.15 + i * (glass_h / (int(glass_h / 0.5) + 1)), -DOOR_D/2, LEAF_W-0.24, 0.04, DOOR_D, C_DOOR, C_DOOR_DARK)
        for i in range(13):
            glPushMatrix(); glTranslatef(offset_x+0.12, 0.22 + i * 0.06, 0); glRotatef(-35, 1, 0, 0)
            R.draw_box_corner(0, 0, -DOOR_D*0.3, LEAF_W-0.24, 0.065, 0.015, C_PANEL, C_DOOR_DARK); glPopMatrix()
        
        # SỬA LỖI TAY NẮM CỬA BỊ NGƯỢC
        hx = offset_x + LEAF_W - 0.1 if is_left else offset_x + 0.1
        R.draw_cylinder(hx, 2.1, DOOR_D/2, 0.015, 0.04, 'z', 8, C_HANDLE)
        R.draw_cylinder(hx, 1.9, DOOR_D/2, 0.015, 0.04, 'z', 8, C_HANDLE)
        R.draw_cylinder(hx, 1.88, DOOR_D/2 + 0.04, 0.015, 0.24, 'y', 8, C_HANDLE)
        R.draw_cylinder(hx, 2.1, -DOOR_D/2 - 0.04, 0.015, 0.04, 'z', 8, C_HANDLE)
        R.draw_cylinder(hx, 1.9, -DOOR_D/2 - 0.04, 0.015, 0.04, 'z', 8, C_HANDLE)
        R.draw_cylinder(hx, 1.88, -DOOR_D/2 - 0.04, 0.015, 0.24, 'y', 8, C_HANDLE)

        for hy_h in [DOOR_H*0.15, DOOR_H*0.5, DOOR_H*0.85]: 
            R.draw_box_corner(-0.015 if is_left else 0.015, hy_h-0.05, -0.03, 0.03, 0.1, 0.06, C_HINGE)

class SlidingWindow:
    def __init__(self, key, x_center, z_start, z_end, y_bot, y_top):
        self.key, self.x_center, self.z_start, self.z_end, self.y_bot, self.y_top = key, x_center, z_start, z_end, y_bot, y_top
        self.open, self.anim = False, 0.0

    def update(self): self.anim += ((1.9 if self.open else 0.0) - self.anim) * 0.2
    def toggle(self): self.open = not self.open

    def draw(self):
        R, x, w_z, h_y = Renderer, self.x_center, self.z_end - self.z_start, self.y_top - self.y_bot
        mid_y, mid_z = self.y_bot + h_y / 2, self.z_start + w_z / 2
        R.set_color((0.4, 0.4, 0.4, 1.0))
        R.draw_box(x, self.y_bot+0.05, mid_z, 0.2, 0.1, w_z); R.draw_box(x, self.y_top-0.05, mid_z, 0.2, 0.1, w_z)
        R.draw_box(x, mid_y, self.z_start+0.05, 0.2, h_y, 0.1); R.draw_box(x, mid_y, self.z_end-0.05, 0.2, h_y, 0.1)
        x_off = 0.03 if x == 0 else -0.03
        self._draw_pane(x - x_off, mid_y, self.z_start + w_z / 4, h_y - 0.1, w_z / 2)
        self._draw_pane(x + x_off, mid_y, (self.z_end - w_z / 4) - self.anim, h_y - 0.1, w_z / 2)

    @staticmethod
    def _draw_pane(x, y, z, h, w):
        R = Renderer; R.set_color((0.8, 0.8, 0.8, 1.0))
        R.draw_box(x, y+h/2-0.05, z, 0.06, 0.1, w); R.draw_box(x, y-h/2+0.05, z, 0.06, 0.1, w)
        R.draw_box(x, y, z-w/2+0.05, 0.06, h, 0.1); R.draw_box(x, y, z+w/2-0.05, 0.06, h, 0.1)
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA); glDepthMask(GL_FALSE)
        R.set_color(C_GLASS); R.draw_box(x, y, z, 0.02, h-0.1, w-0.1)
        glDepthMask(GL_TRUE); glDisable(GL_BLEND)


class Book:
    _id_counter = 1
    def __init__(self, bc_id, x, y, z, w, h, d, color):
        self.id = Book._id_counter; Book._id_counter += 1
        self.bc_id, self.x, self.y, self.z, self.w, self.h, self.d, self.color = bc_id, x, y, z, w, h, d, color
        self.is_taken = False

class Bookcase:
    def __init__(self, bc_id, x_start):
        self.bc_id, self.x_start, self.z, self.is_open, self.anim, self.books = bc_id, x_start, 25.8, False, 0.0, []

    def toggle(self): self.is_open = not self.is_open

    def update(self, dt):
        target = 120.0 if self.is_open else 0.0; diff = target - self.anim
        if abs(diff) > 0.1: self.anim += min(150.0 * dt, abs(diff)) * (1 if diff > 0 else -1)
        else: self.anim = target

    def generate_books(self):
        self.books.clear()
        for sh in [0.4, 1.0, 1.6, 2.2, 2.8, 3.4, 4.0]:
            curr_x, max_x = self.x_start + 0.05, self.x_start + 4.0 - 0.05
            while curr_x < max_x:
                bw = random.uniform(0.04, 0.08)
                if curr_x + bw > max_x: break
                bh, bd = random.uniform(0.30, 0.45), random.uniform(0.25, 0.38)
                self.books.append(Book(self.bc_id, curr_x + bw / 2, sh, self.z - 0.02 - bd / 2, bw, bh, bd, (random.uniform(0.2,0.8), random.uniform(0.2,0.8), random.uniform(0.2,0.8), 1.0)))
                curr_x += bw + random.uniform(0.005, 0.02)

    def draw_structure(self):
        R, bx, bz, w_bc, h_bc, d_bc = Renderer, self.x_start, self.z, 4.0, 4.5, 0.8
        wood_dark, wood_light, wood_shelf = (0.35, 0.20, 0.10, 1.0), (0.50, 0.30, 0.15, 1.0), (0.45, 0.25, 0.12, 1.0)
        R.draw_box_coords(bx, bx+w_bc, 0, h_bc, bz-0.04, bz, wood_dark)
        R.draw_box_coords(bx, bx+0.04, 0, h_bc, bz-d_bc, bz, wood_light); R.draw_box_coords(bx+w_bc-0.04, bx+w_bc, 0, h_bc, bz-d_bc, bz, wood_light)
        R.draw_box_coords(bx, bx+w_bc, h_bc-0.05, h_bc, bz-d_bc, bz, wood_light); R.draw_box_coords(bx, bx+w_bc, 0, 0.05, bz-d_bc, bz, wood_light)
        for sh in [0.4, 1.0, 1.6, 2.2, 2.8, 3.4, 4.0]: R.draw_box_coords(bx+0.04, bx+w_bc-0.04, sh, sh+0.04, bz-d_bc+0.02, bz, wood_shelf)
        for sign, ox in [(1, bx), (-1, bx+w_bc)]:
            glPushMatrix(); glTranslatef(ox, 0, bz-d_bc); glRotatef(sign * self.anim, 0, 1, 0)
            if sign == -1: glScalef(-1, 1, 1)
            R.draw_box_coords(0, 0.1, 0, h_bc, -0.04, 0, wood_light); R.draw_box_coords(w_bc/2-0.1, w_bc/2, 0, h_bc, -0.04, 0, wood_light)
            R.draw_box_coords(0.1, w_bc/2-0.1, 0, 0.1, -0.04, 0, wood_light); R.draw_box_coords(0.1, w_bc/2-0.1, h_bc-0.1, h_bc, -0.04, 0, wood_light)
            glEnable(GL_BLEND); glDepthMask(GL_FALSE); R.set_color((0.6, 0.8, 0.9, 0.4))
            glBegin(GL_QUADS); glNormal3f(0, 0, -1); glVertex3f(0.1, 0.1, -0.02); glVertex3f(w_bc/2-0.1, 0.1, -0.02); glVertex3f(w_bc/2-0.1, h_bc-0.1, -0.02); glVertex3f(0.1, h_bc-0.1, -0.02); glEnd()
            glDepthMask(GL_TRUE); R.draw_box_coords(w_bc/2-0.05-0.03, w_bc/2-0.05+0.03, h_bc/2-0.25, h_bc/2+0.25, -0.04-0.03, -0.04, (0.7,0.7,0.75,1.0))
            glPopMatrix()


# ══════════════════════════════════════════════
#  HỆ THỐNG ĐIỆN / ĐÈN / CÔNG TẮC
# ══════════════════════════════════════════════
class ElectricalSystem:
    def __init__(self):
        self.power_on = False
        self.sw_light = {1: False, 2: False, 3: False}
        self.l_switch_positions = [(LIGHT_SW_X, LIGHT_SW_Y + 0.14, LIGHT_SW_Z + 0.01), (LIGHT_SW_X, LIGHT_SW_Y, LIGHT_SW_Z + 0.01), (LIGHT_SW_X, LIGHT_SW_Y - 0.14, LIGHT_SW_Z + 0.01)]
        self.fan_switch_positions = [(FAN_SW_X - 0.115, FAN_SW_Y + 0.105, FAN_SW_Z + 0.01), (FAN_SW_X + 0.115, FAN_SW_Y + 0.105, FAN_SW_Z + 0.01), (FAN_SW_X - 0.115, FAN_SW_Y - 0.105, FAN_SW_Z + 0.01), (FAN_SW_X + 0.115, FAN_SW_Y - 0.105, FAN_SW_Z + 0.01)]

    def toggle_power(self): self.power_on = not self.power_on
    def toggle_light(self, group): self.sw_light[group] = not self.sw_light[group]
    def active_light_groups(self): return sum(self.sw_light.values()) if self.power_on else 0

    def update_gl_lighting(self):
        brightness = 0.20 + self.active_light_groups() * 0.26
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [brightness]*3 + [1.0])
        glClearColor(0.82*brightness, 0.88*brightness, 0.96*brightness, 1.0)

    def draw_master_switch(self):
        R, bx, by, bz = Renderer, MASTER_SW_X, MASTER_SW_Y, MASTER_SW_Z
        glColor3f(0.22, 0.24, 0.27); R.draw_box(bx, by, bz+0.018, 0.32, 0.44, 0.036)
        glColor3f(0.38, 0.41, 0.46); R.draw_box(bx, by, bz+0.032, 0.30, 0.42, 0.024)
        glColor3f(0.50, 0.53, 0.58); R.draw_box(bx, by, bz+0.042, 0.28, 0.40, 0.010)
        glColor3f(0.68, 0.70, 0.74); R.draw_box(bx, by+0.202, bz+0.042, 0.28, 0.006, 0.010)
        glColor3f(0.30, 0.32, 0.36); R.draw_box(bx, by-0.202, bz+0.042, 0.28, 0.006, 0.010)
        glColor3f(0.60, 0.62, 0.66); R.draw_box(bx+0.143, by, bz+0.042, 0.006, 0.40, 0.010)
        glColor3f(0.34, 0.36, 0.40); R.draw_box(bx-0.143, by, bz+0.042, 0.006, 0.40, 0.010)
        glColor3f(0.72, 0.73, 0.75); R.draw_box(bx, by, bz+0.046, 0.26, 0.016, 0.008)
        glColor3f(0.52, 0.53, 0.55); R.draw_box(bx, by, bz+0.050, 0.26, 0.007, 0.004)
        glColor3f(0.12, 0.12, 0.14); R.draw_box(bx, by, bz+0.055, 0.115, 0.230, 0.022)
        glColor3f(0.17, 0.17, 0.19); R.draw_box(bx, by+0.100, bz+0.054, 0.112, 0.038, 0.020)
        glColor3f(0.17, 0.17, 0.19); R.draw_box(bx, by-0.100, bz+0.054, 0.112, 0.038, 0.020)
        glColor3f(0.94, 0.94, 0.94); R.draw_box(bx, by-0.018, bz+0.068, 0.078, 0.080, 0.003)
        glColor3f(0.08, 0.08, 0.10); R.draw_box(bx, by+0.038, bz+0.064, 0.076, 0.072, 0.014)
        if self.power_on:
            glColor3f(0.92, 0.28, 0.10); R.draw_box(bx, by+0.060, bz+0.076, 0.064, 0.036, 0.016)
            glColor3f(0.08, 0.90, 0.28); R.draw_box(bx, by+0.095, bz+0.070, 0.024, 0.014, 0.004)
        else:
            glColor3f(0.40, 0.40, 0.42); R.draw_box(bx, by+0.018, bz+0.076, 0.064, 0.036, 0.016)
            glColor3f(0.92, 0.06, 0.06); R.draw_box(bx, by+0.095, bz+0.070, 0.024, 0.014, 0.004)
        for dy_vit in [+0.124, -0.124]: glColor3f(0.70, 0.52, 0.16); R.draw_box(bx, by+dy_vit, bz+0.060, 0.040, 0.018, 0.018)

    def draw_light_switch_panel(self):
        R, bx, by, bz = Renderer, LIGHT_SW_X, LIGHT_SW_Y, LIGHT_SW_Z
        glColor3f(0.28, 0.28, 0.28); R.draw_box(bx, by, bz+0.006, 0.25, 0.45, 0.012)
        glColor3f(0.52, 0.52, 0.52); R.draw_box(bx, by, bz+0.011, 0.23, 0.43, 0.012)
        glColor3f(0.97, 0.97, 0.96); R.draw_box(bx, by, bz+0.016, 0.21, 0.41, 0.006)
        for i, (cx, cy, cz) in enumerate(self.l_switch_positions):
            is_on = self.sw_light[i + 1]
            glColor3f(0.62, 0.62, 0.62); R.draw_box(cx, cy, cz+0.008, 0.17, 0.10, 0.009)
            glColor3f(*(0.98,0.98,0.97) if is_on else (0.91,0.91,0.90)); R.draw_box(cx, cy, cz+0.013, 0.15, 0.09, 0.008)
            if is_on: glColor3f(0.10, 0.95, 0.35)
            else: glColor3f(0.95, 0.08, 0.08)
            R.draw_box(cx + 0.055, cy, cz+0.018, 0.016, 0.032, 0.004)

    def draw_fan_switch_panel(self, fans):
        R, bx, by, bz = Renderer, FAN_SW_X, FAN_SW_Y, FAN_SW_Z
        glColor3f(0.28, 0.28, 0.28); R.draw_box(bx, by, bz+0.006, 0.50, 0.45, 0.012)
        glColor3f(0.52, 0.52, 0.52); R.draw_box(bx, by, bz+0.011, 0.48, 0.43, 0.012)
        glColor3f(0.97, 0.97, 0.96); R.draw_box(bx, by, bz+0.016, 0.46, 0.41, 0.006)
        glColor3f(0.70, 0.70, 0.70); R.draw_box(bx, by, bz+0.018, 0.012, 0.39, 0.004)
        for i, (cx, cy, cz) in enumerate(self.fan_switch_positions):
            is_on = fans[i].on
            glColor3f(0.62, 0.62, 0.62); R.draw_box(cx, cy, cz+0.008, 0.108, 0.118, 0.009)
            glColor3f(*(0.98,0.98,0.97) if is_on else (0.91,0.91,0.90)); R.draw_box(cx, cy, cz+0.013, 0.102, 0.112, 0.008)
            if is_on: glColor3f(0.10, 0.95, 0.35)
            else: glColor3f(0.95, 0.08, 0.08)
            R.draw_box(cx, cy+0.028, cz+0.019, 0.026, 0.012, 0.004)

    def draw_lights_3D(self):
        R = Renderer; glDisable(GL_LIGHTING)
        for group_num, px in {1: 5.0, 2: 10.0, 3: 15.0}.items():
            is_lit = self.power_on and self.sw_light[group_num]
            for pz in [4.0, 8.0, 12.0, 16.0, 20.0, 24.0]:
                R.set_color((0.4, 0.4, 0.4, 1.0)); R.draw_box(px, ROOM_H-0.05, pz, 1.4, 0.1, 2.6)
                R.set_color((1.0,1.0,1.0,1.0) if is_lit else (0.2,0.2,0.2,1.0)); R.draw_box(px, ROOM_H-0.12, pz, 1.2, 0.04, 2.4)
        glEnable(GL_LIGHTING)


# ══════════════════════════════════════════════
#  RAYCASTING (tiện ích tương tác 3D bằng chuột)
# ══════════════════════════════════════════════
class Raycaster:
    @staticmethod
    def get_ray(mx, my):
        try:
            modelview  = glGetDoublev(GL_MODELVIEW_MATRIX)
            projection = glGetDoublev(GL_PROJECTION_MATRIX)
            viewport   = glGetIntegerv(GL_VIEWPORT)
        except Exception: return None, None
        winX = float(mx); winY = float(viewport[3] - my)
        try:
            p_near = gluUnProject(winX, winY, 0.0, modelview, projection, viewport)
            p_far  = gluUnProject(winX, winY, 1.0, modelview, projection, viewport)
        except ValueError: return None, None
        raw = (p_far[0]-p_near[0], p_far[1]-p_near[1], p_far[2]-p_near[2])
        length = math.sqrt(sum(v*v for v in raw))
        return p_near, tuple(v/length for v in raw) if length > 0 else raw

    @staticmethod
    def hits_box(ray_o, ray_d, box_c, box_s):
        half = [s/2 for s in box_s]; t_min, t_max = -float('inf'), float('inf')
        for i in range(3):
            if abs(ray_d[i]) < 0.0001:
                if ray_o[i] < box_c[i]-half[i] or ray_o[i] > box_c[i]+half[i]: return False
            else:
                t1 = (box_c[i]-half[i]-ray_o[i])/ray_d[i]
                t2 = (box_c[i]+half[i]-ray_o[i])/ray_d[i]
                if t1 > t2: t1, t2 = t2, t1
                t_min = max(t_min, t1); t_max = min(t_max, t2)
                if t_min > t_max: return False
        return t_max >= 0

    @staticmethod
    def intersect_aabb(nx,ny,nz,dx,dy,dz,min_x,max_x,min_y,max_y,min_z,max_z):
        tmin, tmax = -999999, 999999
        for (n, d_val, m_min, m_max) in [(nx,dx,min_x,max_x),(ny,dy,min_y,max_y),(nz,dz,min_z,max_z)]:
            if abs(d_val) < 1e-6:
                if n < m_min or n > m_max: return None
            else:
                t1, t2 = (m_min-n)/d_val, (m_max-n)/d_val
                if t1 > t2: t1, t2 = t2, t1
                tmin = max(tmin, t1); tmax = min(tmax, t2)
                if tmin > tmax: return None
        return tmin if tmax >= 0 and tmin >= 0 else (0 if tmax >= 0 else None)

    @staticmethod
    def intersect_plane(p_near, p_far, axis, val):
        d = p_far[axis] - p_near[axis]
        if d == 0: return -1, None
        t = (val - p_near[axis]) / d
        if t < 0: return -1, None
        return t, [p_near[0]+t*(p_far[0]-p_near[0]), p_near[1]+t*(p_far[1]-p_near[1]), p_near[2]+t*(p_far[2]-p_near[2])]

    @staticmethod
    def _transform_door_local(ray_o, ray_d, cz): return (ray_o[2]-cz, ray_o[1], -(ray_o[0]-ROOM_W)), (ray_d[2], ray_d[1], -ray_d[0])

    @staticmethod
    def _hits_rotated_leaf(local_o, local_d, hinge_x, angle, is_left):
        ox, oy, oz = local_o[0]-hinge_x, local_o[1], local_o[2]
        rad = math.radians(-angle); c, s = math.cos(rad), math.sin(rad)
        lox, loy, loz = ox*c+oz*s, oy, -ox*s+oz*c
        ldx, ldy, ldz = local_d[0]*c+local_d[2]*s, local_d[1], -local_d[0]*s+local_d[2]*c
        return Raycaster.hits_box((lox,loy,loz),(ldx,ldy,ldz),((LEAF_W/2) if is_left else (-LEAF_W/2),DOOR_H/2,0),(LEAF_W,DOOR_H,0.2))

    def check_interact(self, mx, my, elec, fans, doors, windows, bookcases, held_book, chalk_tool, blackboard):
        p_near, ray_d = self.get_ray(mx, my)
        if p_near is None: return held_book

        ray_o = p_near; nx2,ny2,nz2 = p_near; dx2,dy2,dz2 = ray_d
        p_far_pt = (p_near[0]+ray_d[0]*200, p_near[1]+ray_d[1]*200, p_near[2]+ray_d[2]*200)

        if self.hits_box(ray_o, ray_d, (CHALK_X,  TRAY_Y + 0.06, CHALK_Z), (0.35, 0.12, 0.18)):
            chalk_tool.drop() if chalk_tool.has_chalk else chalk_tool.pick_chalk(); return held_book

        if self.hits_box(ray_o, ray_d, (ERASER_X, TRAY_Y + 0.06, ERASER_Z), (0.38, 0.12, 0.20)):
            chalk_tool.drop() if chalk_tool.has_eraser else chalk_tool.pick_eraser(); return held_book

        if self.hits_box(ray_o, ray_d, (MASTER_SW_X, MASTER_SW_Y, MASTER_SW_Z), (0.30, 0.40, 0.10)):
            elec.toggle_power(); return held_book

        for i, pos in enumerate(elec.l_switch_positions):
            if self.hits_box(ray_o, ray_d, pos, (0.15, 0.1, 0.05)): elec.toggle_light(i+1); return held_book

        for i, pos in enumerate(elec.fan_switch_positions):
            if self.hits_box(ray_o, ray_d, pos, (0.10, 0.12, 0.10)): fans[i].on = not fans[i].on; return held_book

        t_fsw, hit_fsw = self.intersect_plane(p_near, p_far_pt, 2, FAN_SW_Z+0.02)
        if t_fsw > 0 and hit_fsw:
            hx, hy, _ = hit_fsw
            if (FAN_SW_X-0.25)<=hx<=(FAN_SW_X+0.25) and (FAN_SW_Y-0.225)<=hy<=(FAN_SW_Y+0.225):
                if   hx < FAN_SW_X and hy >= FAN_SW_Y: fans[0].on = not fans[0].on
                elif hx >= FAN_SW_X and hy >= FAN_SW_Y: fans[1].on = not fans[1].on
                elif hx < FAN_SW_X and hy < FAN_SW_Y:  fans[2].on = not fans[2].on
                else: fans[3].on = not fans[3].on

        for door in doors:
            lo, ld = self._transform_door_local(ray_o, ray_d, door.cz)
            if self._hits_rotated_leaf(lo, ld, -DOOR_W/2, door.l_ang, True) or self.hits_box(lo, ld, (-DOOR_W/2-FRAME_W/2, DOOR_H/2, 0), (FRAME_W, DOOR_H, FRAME_D)): door.toggle_left()
            if self._hits_rotated_leaf(lo, ld,  DOOR_W/2, -door.r_ang, False) or self.hits_box(lo, ld, ( DOOR_W/2+FRAME_W/2, DOOR_H/2, 0), (FRAME_W, DOOR_H, FRAME_D)): door.toggle_right()
            if self.hits_box(lo, ld, (0, DOOR_H+FRAME_W/2, 0), (DOOR_W, FRAME_W, FRAME_D)): door.toggle_both()

        for plane_x, t_val, hit_val in [(0.0, *self.intersect_plane(p_near, p_far_pt, 0, 0.0)), (ROOM_W, *self.intersect_plane(p_near, p_far_pt, 0, ROOM_W))]:
            if t_val > 0 and hit_val:
                if 1.5 <= hit_val[1] <= 4.5:
                    for win in windows:
                        if win.x_center == plane_x and win.z_start <= hit_val[2] <= win.z_end: win.toggle()

        all_books, best_t, hit_type, hit_id = [b for bc in bookcases for b in bc.books], 999999, None, None

        for bc in bookcases:
            bx, bz, d_bc = bc.x_start, bc.z, 0.8
            if bc.is_open:
                for bounds in [(bx, bx+4.0, 0, 4.5, bz-0.1, bz), (bx-2, bx+0.5, 0, 4.5, bz-d_bc-1.8, bz-d_bc), (bx+3.5, bx+6, 0, 4.5, bz-d_bc-1.8, bz-d_bc)]:
                    t = self.intersect_aabb(nx2,ny2,nz2,dx2,dy2,dz2,*bounds)
                    if t is not None and t < best_t: best_t=t; hit_type="bookcase"; hit_id=bc.bc_id
            else:
                t = self.intersect_aabb(nx2,ny2,nz2,dx2,dy2,dz2, bx,bx+4.0,0,4.5,bz-d_bc-0.1,bz-d_bc+0.1)
                if t is not None and t < best_t: best_t=t; hit_type="bookcase"; hit_id=bc.bc_id

        for b in all_books:
            if not b.is_taken and [bc for bc in bookcases if bc.bc_id==b.bc_id and bc.is_open]:
                t = self.intersect_aabb(nx2,ny2,nz2,dx2,dy2,dz2, b.x-b.w/2, b.x+b.w/2, b.y, b.y+b.h, b.z-b.d/2, b.z+b.d/2)
                if t is not None and t < best_t: best_t=t; hit_type="book"; hit_id=b.id

        if hit_type == "book" and held_book is None:
            for b in all_books:
                if b.id == hit_id: b.is_taken = True
            return hit_id
        elif hit_type == "bookcase":
            if held_book is not None:
                for b in all_books:
                    if b.id == held_book: b.is_taken = False
                return None
            else:
                for bc in bookcases:
                    if bc.bc_id == hit_id: bc.toggle()
        return held_book

    def try_draw_on_board(self, mx, my, chalk_tool, blackboard):
        if not chalk_tool.holding_something: return False
        p_near, ray_d = self.get_ray(mx, my)
        if p_near is None: return False
        t, hit = self.intersect_plane(p_near, (p_near[0]+ray_d[0]*200, p_near[1]+ray_d[1]*200, p_near[2]+ray_d[2]*200), 2, 0.09)
        if t is None or t <= 0 or hit is None: return False
        if chalk_tool.has_chalk: return blackboard.draw_chalk(hit[0], hit[1])
        elif chalk_tool.has_eraser: return blackboard.erase(hit[0], hit[1])
        return False


# ══════════════════════════════════════════════
#  VẼ MÔI TRƯỜNG TĨNH (Sử dụng Display List)
# ══════════════════════════════════════════════
class RoomRenderer:
    @staticmethod
    def draw_trash_can(elec_system=None):
        """
        Thùng rác nhựa đỏ - Đã được làm tròn đều (Cylindrical) và rỗng bên trong (nhìn xuyên qua lưới).
        """
        import math
        cx, cz  = 1.5, 25.0
        base_y  = 0.01

        # Kích thước thùng tròn thon
        R_top = 0.35   # Bán kính miệng
        R_bot = 0.25   # Bán kính đáy
        H     = 0.85   # Chiều cao
        T     = 0.015  # Độ dày thành nhựa

        SLICES = 24    # Số mặt cắt để tạo độ tròn
        NH     = 7     # Số thanh ngang (vành)

        # Bảng màu đỏ
        RED_BRIGHT = (0.95, 0.12, 0.09)
        RED_MID    = (0.82, 0.09, 0.07)
        RED_DARK   = (0.65, 0.06, 0.05)
        RED_BOT    = (0.42, 0.03, 0.03)

        def get_r(f): return R_bot + (R_top - R_bot) * f

        # Tính toán các đỉnh (vertices) trên vòng tròn trước
        angles = [i * 2 * math.pi / SLICES for i in range(SLICES)]
        cos_a = [math.cos(a) for a in angles]
        sin_a = [math.sin(a) for a in angles]

        # ════════════════════════════════════════════════════════════════
        # 1. ĐÁY THÙNG
        # ════════════════════════════════════════════════════════════════
        glColor3f(*RED_BOT)
        glNormal3f(0, 1, 0)
        glBegin(GL_POLYGON)
        for i in range(SLICES):
            glVertex3f(cx + R_bot * cos_a[i], base_y, cz + R_bot * sin_a[i])
        glEnd()

        # (Đã xóa phần vẽ MẶT TRONG ĐẶC để thùng rỗng và nhìn xuyên qua được)

        # ════════════════════════════════════════════════════════════════
        # 2. LƯỚI THANH DỌC (Vỏ ngoài)
        # ════════════════════════════════════════════════════════════════
        glColor3f(*RED_BRIGHT)
        bar_w = 0.05 # Độ rộng góc của thanh dọc (radian)
        F0, F1 = 0.08, 0.92
        
        # Bật GL_LIGHT_MODEL_TWO_SIDE để mặt trong của lưới vẫn bắt sáng khi nhìn xuyên qua
        glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)
        
        glBegin(GL_QUADS)
        for i in range(SLICES):
            ac = angles[i]
            al, ar = ac - bar_w/2, ac + bar_w/2
            rb, rt = get_r(F0), get_r(F1)
            yb, yt = base_y + H*F0, base_y + H*F1
            
            glNormal3f(math.cos(ac), 0.1, math.sin(ac))
            glVertex3f(cx + rb * math.cos(ar), yb, cz + rb * math.sin(ar))
            glVertex3f(cx + rb * math.cos(al), yb, cz + rb * math.sin(al))
            glVertex3f(cx + rt * math.cos(al), yt, cz + rt * math.sin(al))
            glVertex3f(cx + rt * math.cos(ar), yt, cz + rt * math.sin(ar))
        glEnd()

        # ════════════════════════════════════════════════════════════════
        # 3. LƯỚI THANH NGANG (Vỏ ngoài)
        # ════════════════════════════════════════════════════════════════
        glColor3f(*RED_MID)
        BH = 0.015 # Bề cao thanh ngang
        for hi in range(NH):
            fc = F0 + hi / (NH - 1) * (F1 - F0)
            fb, ft = fc - BH/2, fc + BH/2
            rb, rt = get_r(fb), get_r(ft)
            yb, yt = base_y + H*fb, base_y + H*ft

            glBegin(GL_QUAD_STRIP)
            for i in range(SLICES + 1):
                idx = i % SLICES
                glNormal3f(cos_a[idx], 0.1, sin_a[idx])
                glVertex3f(cx + rb * cos_a[idx], yb, cz + rb * sin_a[idx])
                glVertex3f(cx + rt * cos_a[idx], yt, cz + rt * sin_a[idx])
            glEnd()
            
        glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_FALSE) # Trả lại trạng thái cũ

        # ════════════════════════════════════════════════════════════════
        # 4. DẢI CHÂN & ĐỈNH ĐẶC
        # ════════════════════════════════════════════════════════════════
        glColor3f(*RED_DARK)
        glBegin(GL_QUAD_STRIP)
        for i in range(SLICES + 1):
            idx = i % SLICES
            glNormal3f(cos_a[idx], 0.1, sin_a[idx])
            glVertex3f(cx + R_bot * cos_a[idx], base_y, cz + R_bot * sin_a[idx])
            glVertex3f(cx + get_r(F0) * cos_a[idx], base_y + H*F0, cz + get_r(F0) * sin_a[idx])
        glEnd()
        
        glBegin(GL_QUAD_STRIP)
        for i in range(SLICES + 1):
            idx = i % SLICES
            glNormal3f(cos_a[idx], 0.1, sin_a[idx])
            glVertex3f(cx + get_r(F1) * cos_a[idx], base_y + H*F1, cz + get_r(F1) * sin_a[idx])
            glVertex3f(cx + R_top * cos_a[idx], base_y + H, cz + R_top * sin_a[idx])
        glEnd()

        # ════════════════════════════════════════════════════════════════
        # 5. VÀNH MIỆNG DÀY (Torus-like)
        # ════════════════════════════════════════════════════════════════
        glColor3f(*RED_BRIGHT)
        RH = 0.04  # Chiều cao vành
        RO = 0.02  # Độ nhô ra ngoài
        y_top = base_y + H
        y_rim = y_top + RH
        r_out = R_top + RO
        r_in_top = R_top - T
        
        # Mặt dưới vành
        glBegin(GL_QUAD_STRIP)
        for i in range(SLICES + 1):
            idx = i % SLICES
            glNormal3f(0, -1, 0)
            glVertex3f(cx + R_top * cos_a[idx], y_top, cz + R_top * sin_a[idx])
            glVertex3f(cx + r_out * cos_a[idx], y_top, cz + r_out * sin_a[idx])
        glEnd()
        
        # Mặt ngoài vành
        glBegin(GL_QUAD_STRIP)
        for i in range(SLICES + 1):
            idx = i % SLICES
            glNormal3f(cos_a[idx], 0, sin_a[idx])
            glVertex3f(cx + r_out * cos_a[idx], y_top, cz + r_out * sin_a[idx])
            glVertex3f(cx + r_out * cos_a[idx], y_rim, cz + r_out * sin_a[idx])
        glEnd()
        
        # Mặt trên vành
        glBegin(GL_QUAD_STRIP)
        for i in range(SLICES + 1):
            idx = i % SLICES
            glNormal3f(0, 1, 0)
            glVertex3f(cx + r_out * cos_a[idx], y_rim, cz + r_out * sin_a[idx])
            glVertex3f(cx + r_in_top * cos_a[idx], y_rim, cz + r_in_top * sin_a[idx])
        glEnd()

        # Mặt trong vành (thêm vào để khép kín độ dày của khối vành)
        glColor3f(*RED_DARK)
        glBegin(GL_QUAD_STRIP)
        for i in range(SLICES + 1):
            idx = i % SLICES
            glNormal3f(-cos_a[idx], 0, -sin_a[idx])
            glVertex3f(cx + r_in_top * cos_a[idx], y_rim, cz + r_in_top * sin_a[idx])
            glVertex3f(cx + R_top * cos_a[idx], y_top, cz + R_top * sin_a[idx])
        glEnd()


    @staticmethod
    def draw_floor():
        R = Renderer
        cols_x = int(ROOM_W / TILE_S); cols_z = int(ROOM_D / TILE_S); grout = 0.02
        tile_a = TILE_S - grout
        glNormal3f(0,1,0); glEnable(GL_POLYGON_OFFSET_FILL); glPolygonOffset(1.0,1.0)
        R.set_color(C_TILE_GROUT)
        glBegin(GL_QUADS); glVertex3f(0,0,0); glVertex3f(ROOM_W,0,0); glVertex3f(ROOM_W,0,ROOM_D); glVertex3f(0,0,ROOM_D); glEnd()
        glDisable(GL_POLYGON_OFFSET_FILL)
        for iz in range(cols_z):
            for ix in range(cols_x):
                x0, z0 = ix*TILE_S + grout/2, iz*TILE_S + grout/2
                x1, z1 = x0 + tile_a, z0 + tile_a
                R.set_color(C_TILE_A if (ix+iz)%2==0 else C_TILE_B)
                glBegin(GL_QUADS); glVertex3f(x0,0.001,z0); glVertex3f(x1,0.001,z0); glVertex3f(x1,0.001,z1); glVertex3f(x0,0.001,z1); glEnd()

    @staticmethod
    def draw_ceiling():
        R = Renderer
        R.set_color(C_CEIL); glNormal3f(0,-1,0)
        glBegin(GL_QUADS); glVertex3f(0,ROOM_H,0); glVertex3f(ROOM_W,ROOM_H,0); glVertex3f(ROOM_W,ROOM_H,ROOM_D); glVertex3f(0,ROOM_H,ROOM_D); glEnd()

    @staticmethod
    def draw_walls():
        R = Renderer
        tw = 0.12; wl, wd = C_WALL_LIGHT, C_WALL_DARK
        R.set_color(wl); glNormal3f(0,0,1); glBegin(GL_QUADS); glVertex3f(0,0,0); glVertex3f(ROOM_W,0,0); glVertex3f(ROOM_W,ROOM_H,0); glVertex3f(0,ROOM_H,0); glEnd()
        R.set_color(wl); glNormal3f(0,0,-1); glBegin(GL_QUADS); glVertex3f(ROOM_W,0,ROOM_D); glVertex3f(0,0,ROOM_D); glVertex3f(0,ROOM_H,ROOM_D); glVertex3f(ROOM_W,ROOM_H,ROOM_D); glEnd()
        R.set_color(wd); glNormal3f(1,0,0); glBegin(GL_QUADS); glVertex3f(0,0,ROOM_D); glVertex3f(0,0,0); glVertex3f(0,1.5,0); glVertex3f(0,1.5,ROOM_D); glVertex3f(0,4.5,ROOM_D); glVertex3f(0,4.5,0); glVertex3f(0,ROOM_H,0); glVertex3f(0,ROOM_H,ROOM_D); glVertex3f(0,1.5,5.0); glVertex3f(0,1.5,0); glVertex3f(0,4.5,0); glVertex3f(0,4.5,5.0); glVertex3f(0,1.5,12.0); glVertex3f(0,1.5,9.0); glVertex3f(0,4.5,9.0); glVertex3f(0,4.5,12.0); glVertex3f(0,1.5,ROOM_D); glVertex3f(0,1.5,16.0); glVertex3f(0,4.5,16.0); glVertex3f(0,4.5,ROOM_D); glEnd()
        R.set_color(wd); glNormal3f(-1,0,0); glBegin(GL_QUADS)
        def wr(y1,y2,z1,z2): glVertex3f(ROOM_W,y1,z1); glVertex3f(ROOM_W,y1,z2); glVertex3f(ROOM_W,y2,z2); glVertex3f(ROOM_W,y2,z1)
        wr(4.5,ROOM_H,0,ROOM_D); wr(0,1.5,0,5); wr(0,1.5,7,23); wr(0,1.5,25,ROOM_D); wr(1.5,4.5,0,5); wr(1.5,4.5,7,10); wr(1.5,4.5,14,17); wr(1.5,4.5,21,23); wr(1.5,4.5,25,ROOM_D); glEnd()
        R.set_color(C_TRIM); glNormal3f(0,1,1); glBegin(GL_QUADS); glVertex3f(0,0,0.001); glVertex3f(ROOM_W,0,0.001); glVertex3f(ROOM_W,tw,0.001); glVertex3f(0,tw,0.001); glVertex3f(0,0,ROOM_D-0.001); glVertex3f(ROOM_W,0,ROOM_D-0.001); glVertex3f(ROOM_W,tw,ROOM_D-0.001); glVertex3f(0,tw,ROOM_D-0.001); glVertex3f(0.001,0,0); glVertex3f(0.001,0,ROOM_D); glVertex3f(0.001,tw,ROOM_D); glVertex3f(0.001,tw,0); glVertex3f(ROOM_W-0.001,0,ROOM_D); glVertex3f(ROOM_W-0.001,0,0); glVertex3f(ROOM_W-0.001,tw,0); glVertex3f(ROOM_W-0.001,tw,ROOM_D); glEnd()

    @staticmethod
    def draw_podium():
        R = Renderer
        glColor3f(0.72,0.72,0.72); R.draw_box(0,0.25,-8.5,20.0,0.5,3.0)
        glColor3f(0.55,0.55,0.55); R.draw_box(0,0.25,-6.9,20.2,0.5,0.2)

    @staticmethod
    def draw_chair(x, z):
        R = Renderer
        wood, metal = (0.55,0.35,0.15), (0.12,0.12,0.12)
        glColor3f(*metal); R.draw_box(x-0.35,0.4,z-0.35,0.05,0.8,0.05); R.draw_box(x+0.35,0.4,z-0.35,0.05,0.8,0.05); R.draw_box(x-0.35,0.4,z+0.35,0.05,0.8,0.05); R.draw_box(x+0.35,0.4,z+0.35,0.05,0.8,0.05)
        glColor3f(*wood); R.draw_box(x,0.85,z,0.9,0.08,0.9)
        glColor3f(*metal); R.draw_box(x-0.32,1.35,z+0.35,0.05,1,0.05); R.draw_box(x+0.32,1.35,z+0.35,0.05,1,0.05)
        glColor3f(*wood); R.draw_box(x,1.45,z+0.28,0.82,0.7,0.06)

    @staticmethod
    def draw_desk(x, z):
        R = Renderer
        wood, metal = (0.58,0.38,0.18), (0.10,0.10,0.10)
        glColor3f(*wood); R.draw_box(x,1.15,z,2.2,0.12,1)
        glColor3f(*metal); R.draw_box(x-1,0.6,z-0.4,0.07,1.2,0.07); R.draw_box(x+1,0.6,z-0.4,0.07,1.2,0.07); R.draw_box(x-1,0.6,z+0.4,0.07,1.2,0.07); R.draw_box(x+1,0.6,z+0.4,0.07,1.2,0.07)

    @staticmethod
    def draw_students():
        columns = [-6.3, -2.1, 2.1, 6.3]
        for colX in columns:
            for r in range(5):
                z = 10.0 - r * 3.0
                RoomRenderer.draw_desk(colX, z); RoomRenderer.draw_chair(colX-0.6, z+1.6); RoomRenderer.draw_chair(colX+0.6, z+1.6)

    @staticmethod
    def draw_teacher_table():
        R = Renderer
        glColor3f(0.45, 0.28, 0.12)
        base_y, extra_h, z_shift = 0.5, 0.1, 0.5
        R.draw_box(-6.0, 1.15+base_y+extra_h, -8.5+z_shift, 3.5, 0.15, 1.5)
        leg_h = 1.2 + extra_h; leg_y = base_y + leg_h/2
        for lx, lz in [(-7.6,-9.1),(-4.4,-9.1),(-7.6,-7.9),(-4.4,-7.9)]: R.draw_box(lx, leg_y, lz+z_shift, 0.1, leg_h, 0.1)
        glPushMatrix(); glTranslatef(-6.0, base_y, -9.5+z_shift); glRotatef(180, 0, 1, 0); RoomRenderer.draw_chair(0, 0); glPopMatrix()

    @staticmethod
    def draw_clock():
        now = datetime.now()
        second, minute, hour = now.second, now.minute, now.hour % 12
        R = Renderer
        glPushMatrix(); glTranslatef(3.0, 4.2, 0.0)
        radius, depth = 0.7, 0.1
        qobj = gluNewQuadric(); gluQuadricNormals(qobj, GLU_SMOOTH)
        R.set_color((0.15,0.15,0.15,1.0)); gluCylinder(qobj, radius, radius, depth, 40, 1)
        glPushMatrix(); glRotatef(180,1,0,0); gluDisk(qobj,0,radius,40,1); glPopMatrix()
        glPushMatrix(); glTranslatef(0,0,depth); R.set_color((1.0,1.0,1.0,1.0)); gluDisk(qobj,0,radius,40,1)
        R.set_color((0.0,0.0,0.0,1.0)); R.draw_box(0,0,0.02,0.1,0.1,0.04)
        for i in range(12):
            ang = math.radians(i*30); px, py = math.sin(ang)*0.55, math.cos(ang)*0.55
            glPushMatrix(); glTranslatef(px,py,0.01); glRotatef(-i*30,0,0,1); R.draw_box(0,0,0,0.04,0.15,0.02); glPopMatrix()
        glPushMatrix(); glRotatef(-(hour*30+minute/2),0,0,1); glTranslatef(0,0.15,0.03); R.draw_box(0,0,0,0.06,0.3,0.02); glPopMatrix()
        glPushMatrix(); glRotatef(-(minute*6),0,0,1); glTranslatef(0,0.22,0.05);          R.draw_box(0,0,0,0.04,0.45,0.02); glPopMatrix()
        R.set_color((1.0,0.0,0.0,1.0))
        glPushMatrix(); glRotatef(-(second*6),0,0,1); glTranslatef(0,0.27,0.07); R.draw_box(0,0,0,0.02,0.55,0.02); glPopMatrix()
        glPopMatrix(); glPopMatrix()
        gluDeleteQuadric(qobj)

    @staticmethod
    def draw_portrait(tex_id):
        R = Renderer
        cx, cy = 16.5, 4.2
        R.set_color((0.85,0.65,0.10,1.0)); R.draw_box(cx,cy,0.04,1.5,1.8,0.08)
        lx, rx = cx-0.65, cx+0.65; by, ty = cy-0.8, cy+0.8; z_front = 0.082
        if tex_id is not None:
            glEnable(GL_TEXTURE_2D); glBindTexture(GL_TEXTURE_2D, tex_id)
            R.set_color((1.0,1.0,1.0,1.0))
            glBegin(GL_QUADS); glNormal3f(0,0,1)
            glTexCoord2f(1.0,1.0); glVertex3f(rx,by,z_front)
            glTexCoord2f(0.0,1.0); glVertex3f(lx,by,z_front)
            glTexCoord2f(0.0,0.0); glVertex3f(lx,ty,z_front)
            glTexCoord2f(1.0,0.0); glVertex3f(rx,ty,z_front)
            glEnd(); glDisable(GL_TEXTURE_2D)
        else:
            R.set_color((0.90,0.92,0.95,1.0))
            glBegin(GL_QUADS); glNormal3f(0,0,1)
            glVertex3f(rx,by,z_front); glVertex3f(lx,by,z_front); glVertex3f(lx,ty,z_front); glVertex3f(rx,ty,z_front); glEnd()


# ══════════════════════════════════════════════
#  HUD (sách cầm trên tay)
# ══════════════════════════════════════════════
class HUD:
    @staticmethod
    def draw(held_book_id, all_books):
        if held_book_id is None: return
        R = Renderer
        glDisable(GL_DEPTH_TEST); glDisable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); gluOrtho2D(0, WIN_W, 0, WIN_H)
        glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
        b = next((x for x in all_books if x.id == held_book_id), None)
        if b:
            bw, bh = 460, 300
            cx = WIN_W - bw/2 - 40; cy = bh/2 + 40
            R.set_color(b.color)
            glBegin(GL_QUADS); glVertex2f(cx-bw/2-10,cy-bh/2-10); glVertex2f(cx+bw/2+10,cy-bh/2-10); glVertex2f(cx+bw/2+10,cy+bh/2+10); glVertex2f(cx-bw/2-10,cy+bh/2+10); glEnd()
            R.set_color((0.95,0.95,0.92,1.0))
            glBegin(GL_QUADS); glVertex2f(cx-bw/2,cy-bh/2); glVertex2f(cx-5,cy-bh/2); glVertex2f(cx-5,cy+bh/2); glVertex2f(cx-bw/2,cy+bh/2); glEnd()
            glBegin(GL_QUADS); glVertex2f(cx+5,cy-bh/2);    glVertex2f(cx+bw/2,cy-bh/2); glVertex2f(cx+bw/2,cy+bh/2); glVertex2f(cx+5,cy+bh/2); glEnd()
        glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix()
        glMatrixMode(GL_MODELVIEW); glEnable(GL_LIGHTING); glEnable(GL_DEPTH_TEST)


# ══════════════════════════════════════════════
#  ỨNG DỤNG CHÍNH
# ══════════════════════════════════════════════
class ClassroomApp:
    def __init__(self):
        self.camera  = Camera()
        self.elec    = ElectricalSystem()
        self.raycaster = Raycaster()
        self.hud     = HUD()

        self.chalk_tool = ChalkTool()
        self.blackboard = Blackboard()
        self.left_mouse_down = False

        self.fans = [Fan(7.5, 10.0), Fan(12.5, 10.0), Fan(7.5, 18.0), Fan(12.5, 18.0)]
        self.doors = [Door(1, 6.0), Door(2, 24.0)]
        self.windows = [
            SlidingWindow("L1", 0.0, 5.0, 9.0, 1.5, 4.5),
            SlidingWindow("L2", 0.0, 12.0, 16.0, 1.5, 4.5),
            SlidingWindow("R1", ROOM_W, 10.0, 14.0, 1.5, 4.5),
            SlidingWindow("R2", ROOM_W, 17.0, 21.0, 1.5, 4.5),
        ]
        self.bookcases = [Bookcase(1, 3.0), Bookcase(2, 13.0)]
        for bc in self.bookcases: bc.generate_books()

        self.held_book_id = None
        self.mouse_down   = False
        self.last_mouse   = (0, 0)
        self.dl_static    = None
        self.dl_books     = None
        self.photo_tex    = None

    def setup_gl(self):
        glMatrixMode(GL_PROJECTION); glLoadIdentity()
        gluPerspective(60, WIN_W/WIN_H, 0.05, 200.0)
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST); glEnable(GL_NORMALIZE)
        glEnable(GL_BLEND);      glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_DITHER)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_FASTEST)
        glHint(GL_POLYGON_SMOOTH_HINT, GL_FASTEST)
        glEnable(GL_LIGHTING); glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glShadeModel(GL_SMOOTH)

    def load_texture(self, path):
        try: surface = pygame.image.load(path)
        except pygame.error: return None
        surface   = pygame.transform.flip(surface, False, True)
        img_data  = pygame.image.tostring(surface, "RGBA", True)
        w, h      = surface.get_width(), surface.get_height()
        tex_id    = glGenTextures(1); glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        return tex_id

    def build_static_list(self):
        self.dl_static = glGenLists(1)
        glNewList(self.dl_static, GL_COMPILE)
        RoomRenderer.draw_floor()
        RoomRenderer.draw_ceiling()
        RoomRenderer.draw_walls()
        
        # KHÔNG gọi draw_trash_can ở đây vì nó cần elec_system để đồng bộ độ sáng
        # Thùng rác sẽ được vẽ động mỗi frame trong draw()
        
        glPushMatrix(); glTranslatef(ROOM_W/2, 0, 10.0)
        RoomRenderer.draw_students()
        RoomRenderer.draw_podium()
        RoomRenderer.draw_teacher_table()
        glPopMatrix()
        glEndList()

    def compile_books_list(self):
        if self.dl_books is None: self.dl_books = glGenLists(1)
        R = Renderer; glNewList(self.dl_books, GL_COMPILE)
        all_books = [b for bc in self.bookcases for b in bc.books]
        for b in all_books:
            if not b.is_taken:
                R.set_color((0.92, 0.92, 0.92, 1.0)); R.draw_box(b.x, b.y+b.h/2, b.z+0.002, b.w-0.008, b.h-0.01, b.d-0.004)
                R.set_color(b.color); R.draw_box(b.x, b.y+b.h/2, b.z-b.d/2+0.002, b.w, b.h, 0.004)
                R.draw_box(b.x-b.w/2+0.002, b.y+b.h/2, b.z, 0.004, b.h, b.d); R.draw_box(b.x+b.w/2-0.002, b.y+b.h/2, b.z, 0.004, b.h, b.d)
        glEndList()

    def handle_event(self, event):
        if event.type == QUIT: pygame.quit(); sys.exit()
        
        # Chỉ giữ lại phím ESC để thoát, các phím tắt đồ vật khác đã bị loại bỏ
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE: pygame.quit(); sys.exit()

        if event.type == MOUSEBUTTONDOWN:
            if event.button == 3: self.mouse_down = True; self.last_mouse = pygame.mouse.get_pos()
            elif event.button == 1:
                self.left_mouse_down = True
                mx, my = pygame.mouse.get_pos()
                if self.held_book_id is not None:
                    bw, bh = 460, 300
                    cx = WIN_W - bw/2 - 40; cy = bh/2 + 40
                    my_gl = WIN_H - my
                    if (cx-bw/2-10 <= mx <= cx+bw/2+10) and (cy-bh/2-10 <= my_gl <= cy+bh/2+10):
                        all_books = [b for bc in self.bookcases for b in bc.books]
                        for b in all_books:
                            if b.id == self.held_book_id: b.is_taken = False
                        self.held_book_id = None; self.compile_books_list(); return
                
                new_held = self.raycaster.check_interact(mx, my, self.elec, self.fans, self.doors, self.windows, self.bookcases, self.held_book_id, self.chalk_tool, self.blackboard)
                if new_held != self.held_book_id: self.held_book_id = new_held; self.compile_books_list()

        if event.type == MOUSEBUTTONUP:
            if event.button == 3: self.mouse_down = False
            if event.button == 1: self.left_mouse_down = False

        if event.type == MOUSEMOTION and self.mouse_down:
            mx, my = pygame.mouse.get_pos()
            self.camera.rotate(mx - self.last_mouse[0], my - self.last_mouse[1])
            self.last_mouse = (mx, my)

    def update(self, dt):
        for fan in self.fans: fan.update(self.elec.power_on)
        for door in self.doors: door.update(dt)
        for win in self.windows: win.update()
        for bc in self.bookcases: bc.update(dt)
            
        if getattr(self, 'left_mouse_down', False):
            mx, my = pygame.mouse.get_pos()
            self.raycaster.try_draw_on_board(mx, my, self.chalk_tool, self.blackboard)
            
        self.blackboard.sync_texture()

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.camera.apply()
        self.elec.update_gl_lighting()

        glCallList(self.dl_static)
        RoomRenderer.draw_trash_can(self.elec)
        self.blackboard.draw()
        self.blackboard.draw(self.chalk_tool)

        # --- Vẽ tất cả vật đặc (opaque) trước ---
        for door in self.doors: door.draw()
        for fan in self.fans: fan.draw()
        for bc in self.bookcases: bc.draw_structure()
        if self.dl_books is not None: glCallList(self.dl_books)

        RoomRenderer.draw_portrait(self.photo_tex)
        RoomRenderer.draw_clock()
        self.elec.draw_master_switch()
        self.elec.draw_light_switch_panel()
        self.elec.draw_fan_switch_panel(self.fans)
        self.elec.draw_lights_3D()

        # --- Vẽ kính trong suốt cuối cùng (transparent pass) ---
        # Quy tắc OpenGL: transparent objects phải vẽ SAU tất cả opaque objects
        # để depth buffer đã có đầy đủ thông tin, kính mới blend đúng lên trên
        for door in self.doors: door.draw_glass()
        for win in self.windows: win.draw()

        all_books = [b for bc in self.bookcases for b in bc.books]
        self.hud.draw(self.held_book_id, all_books)
        self.chalk_tool.draw_in_hand()

    def run(self):
        pygame.init()
        pygame.display.gl_set_attribute(pygame.GL_SWAP_CONTROL, 1)
        pygame.display.set_mode((WIN_W, WIN_H), DOUBLEBUF | OPENGL | RESIZABLE | HWSURFACE)
        pygame.display.set_caption("Lớp Học 3D - OOP Edition")

        self.setup_gl()
        self.blackboard.init_texture()
        self.build_static_list()
        self.compile_books_list()
        self.photo_tex = self.load_texture("anh_Bac_Ho.jpg")

        clock = pygame.time.Clock(); dt = 1 / 60.0

        while True:
            for event in pygame.event.get(): self.handle_event(event)
            self.camera.move(pygame.key.get_pressed(), dt)
            self.update(dt)
            self.draw()
            pygame.display.flip()
            fps = clock.get_fps()
            pygame.display.set_caption(f"FPS: {fps:.1f}")
            dt = clock.tick_busy_loop(144) / 1000

# ══════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════
if __name__ == "__main__":
    app = ClassroomApp()
    app.run()