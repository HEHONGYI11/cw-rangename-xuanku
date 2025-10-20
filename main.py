#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import random
from loguru import logger

from PyQt5.QtWidgets import QWidget, QLabel, QDialog, QVBoxLayout, QPushButton, QDesktopWidget, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtGui import QFont, QMouseEvent, QPainter, QColor, QPen, QBrush, QPolygonF
import math

from .ClassWidgets.base import PluginBase, SettingsBase


def read_names_from_file(file_path):
    """读取名单文件并返回处理后的名单列表"""
    if not os.path.exists(file_path):
        default_names = ["小明", "李华", "张三", "李四", "王五", "赵六"]
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(default_names))
        return default_names

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            names = f.read().splitlines()
        return [name.strip() for name in names if name.strip()]
    except Exception as e:
        logger.error(f"读取名单文件时出错: {e}")
        return ["小明", "李华", "张三", "李四"]


class Particle:
    """粒子类 - 用于创建科学粒子效果"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.life = 1.0
        self.decay = random.uniform(0.005, 0.015)
        self.size = random.uniform(2, 5)
        # 理科元素颜色：蓝色、绿色、紫色
        colors = [
            QColor(100, 149, 237),  # 蓝色
            QColor(50, 205, 50),    # 绿色
            QColor(138, 43, 226),   # 紫色
            QColor(255, 215, 0),    # 金色
        ]
        self.color = random.choice(colors)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        self.size *= 0.995
        return self.life > 0

    def draw(self, painter):
        if self.life > 0:
            painter.setBrush(QBrush(self.color))
            painter.setPen(Qt.NoPen)
            painter.setOpacity(self.life)
            painter.drawEllipse(int(self.x), int(self.y), int(self.size), int(self.size))


class NameResultDialog(QDialog):
    """显示点名结果的对话框"""
    
    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.name = name
        self.opacity_effect = None
        self.fade_animation = None
        self.particles = []
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_particles)
        self.animation_timer.start(50)  # 20 FPS
        self.init_ui()
        self.move_center()
        self.setup_animation()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("🧬 随机点名 ⚛️")
        self.setFixedSize(800, 500)  # 进一步增大窗口尺寸
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 15px;
            }
        """)
        
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)
        
        # 创建标题标签
        self.title_label = QLabel("🧬 随机点名 ⚛️")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("微软雅黑", 18, QFont.Bold))
        self.title_label.setStyleSheet("""
            QLabel {
                color: white;
                background: transparent;
                padding: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            }
        """)
        
        # 创建名字标签
        self.name_label = QLabel(self.name)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setFont(QFont("黑体", 72, QFont.Bold))  # 适中的字体大小
        self.name_label.setWordWrap(True)  # 允许文字换行
        self.name_label.setStyleSheet("""
            QLabel {
                color: #2E3440;
                background: rgba(255, 255, 255, 0.95);
                border: 3px solid rgba(255, 255, 255, 0.8);
                border-radius: 20px;
                padding: 30px;
                margin: 10px;
                min-height: 150px;
                max-height: 200px;
            }
        """)
        
        # 创建按钮容器
        button_layout = QVBoxLayout()
        button_layout.setSpacing(15)  # 增加按钮之间的间距
        
        # 创建重新点名按钮
        self.reroll_btn = QPushButton("🎲 重新点名")
        self.reroll_btn.setFixedSize(160, 45)
        self.reroll_btn.setFont(QFont("微软雅黑", 13, QFont.Bold))
        self.reroll_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.5);
                border-radius: 22px;
                font-weight: bold;
                margin: 5px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.3);
                border: 2px solid rgba(255, 255, 255, 0.8);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.1);
            }
        """)
        
        # 创建确定按钮
        self.confirm_btn = QPushButton("✅ 确定")
        self.confirm_btn.setFixedSize(160, 45)
        self.confirm_btn.setFont(QFont("微软雅黑", 13, QFont.Bold))
        self.confirm_btn.clicked.connect(self.close)
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.9);
                color: #2E3440;
                border: none;
                border-radius: 22px;
                font-weight: bold;
                margin: 5px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 1.0);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.8);
            }
        """)
        
        # 添加到布局
        layout.addWidget(self.title_label)
        layout.addWidget(self.name_label, 1)  # 给名字标签更多空间权重
        
        button_layout.addWidget(self.reroll_btn, alignment=Qt.AlignCenter)
        button_layout.addWidget(self.confirm_btn, alignment=Qt.AlignCenter)
        layout.addLayout(button_layout)

    def setup_animation(self):
        """设置淡入动画"""
        # 创建透明度效果
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        # 创建淡入动画
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(500)  # 500ms动画时长
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)

    def show(self):
        """重写show方法，添加淡入动画"""
        super().show()
        if self.fade_animation:
            self.fade_animation.start()
        logger.debug("随机点名：开始淡入动画")

    def move_center(self):
        """移动窗口到屏幕中心"""
        screen = QDesktopWidget().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def update_content(self, new_name):
        """更新显示的名字"""
        self.name = new_name
        self.name_label.setText(new_name)
        # 重新播放淡入动画
        if self.fade_animation:
            self.fade_animation.start()

    def set_reroll_callback(self, callback):
        """设置重新点名回调函数"""
        self.reroll_btn.clicked.connect(callback)

    def update_particles(self):
        """更新粒子效果"""
        # 生成新粒子
        if len(self.particles) < 30:
            for _ in range(2):
                x = random.randint(0, self.width())
                y = random.randint(0, self.height())
                self.particles.append(Particle(x, y))
        
        # 更新现有粒子
        self.particles = [p for p in self.particles if p.update()]
        self.update()  # 触发重绘

    def paintEvent(self, event):
        """绘制粒子效果和理科元素"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制粒子
        for particle in self.particles:
            particle.draw(painter)
        
        # 绘制理科元素图案
        self.draw_science_elements(painter)

    def draw_science_elements(self, painter):
        """绘制理科元素图案"""
        painter.setOpacity(0.3)
        
        # 绘制DNA双螺旋结构
        self.draw_dna_helix(painter, 50, 100, 30, 150)
        self.draw_dna_helix(painter, self.width() - 80, 100, 30, 150)
        
        # 绘制原子结构
        self.draw_atom(painter, 100, self.height() - 100, 40)
        self.draw_atom(painter, self.width() - 100, self.height() - 100, 40)
        
        # 绘制分子结构
        self.draw_molecule(painter, self.width() // 2, 80, 25)

    def draw_dna_helix(self, painter, x, y, width, height):
        """绘制DNA双螺旋"""
        painter.setPen(QPen(QColor(100, 149, 237, 100), 2))
        
        points1 = []
        points2 = []
        for i in range(0, height, 5):
            angle = i * 0.2
            x1 = x + width * 0.3 * math.sin(angle)
            x2 = x + width * 0.3 * math.sin(angle + math.pi)
            points1.append(QPoint(int(x1), y + i))
            points2.append(QPoint(int(x2), y + i))
        
        # 绘制螺旋线
        for i in range(len(points1) - 1):
            painter.drawLine(points1[i], points1[i + 1])
            painter.drawLine(points2[i], points2[i + 1])
            
            # 绘制连接线
            if i % 10 == 0:
                painter.drawLine(points1[i], points2[i])

    def draw_atom(self, painter, cx, cy, radius):
        """绘制原子结构"""
        # 原子核
        painter.setBrush(QBrush(QColor(255, 215, 0, 150)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(cx - 5, cy - 5, 10, 10)
        
        # 电子轨道
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(50, 205, 50, 100), 1))
        
        for i in range(3):
            r = radius * (0.5 + i * 0.3)
            painter.drawEllipse(cx - r, cy - r, 2 * r, 2 * r)
            
            # 电子
            angle = self.animation_timer.remainingTime() * 0.01 + i * 2
            ex = cx + r * math.cos(angle)
            ey = cy + r * math.sin(angle)
            painter.setBrush(QBrush(QColor(138, 43, 226, 200)))
            painter.drawEllipse(int(ex - 3), int(ey - 3), 6, 6)

    def draw_molecule(self, painter, cx, cy, size):
        """绘制分子结构"""
        painter.setBrush(QBrush(QColor(100, 149, 237, 150)))
        painter.setPen(QPen(QColor(255, 255, 255, 100), 2))
        
        # 分子节点
        nodes = [
            (cx, cy - size),
            (cx + size, cy),
            (cx, cy + size),
            (cx - size, cy),
            (cx + size * 0.7, cy - size * 0.7),
            (cx - size * 0.7, cy - size * 0.7)
        ]
        
        # 绘制连接线
        connections = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 4), (0, 5)]
        for start, end in connections:
            painter.drawLine(int(nodes[start][0]), int(nodes[start][1]),
                           int(nodes[end][0]), int(nodes[end][1]))
        
        # 绘制节点
        for x, y in nodes:
            painter.drawEllipse(int(x - 4), int(y - 4), 8, 8)


class FloatingWindow(QWidget):
    """悬浮点名窗口"""
    
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.names = []
        self.shuffled_names = []
        self.current_index = 0
        self.drag_pos = QPoint()
        self.mouse_press_pos = QPoint()
        self.result_dialog = None
        
        self.load_names()
        self.init_ui()

    def init_ui(self):
        """初始化界面组件"""
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.9)

        self.label = QLabel("点名", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(30, 144, 255, 0.9);
                font-family: 黑体;
                font-size: 16px;
                font-weight: bold;
                border-radius: 6px;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
        """)
        self.label.setFixedSize(60, 45)
        self.setFixedSize(60, 45)
        self.move_to_corner()

    def load_names(self):
        """加载名单并初始化洗牌队列"""
        file_path = os.path.join(os.path.dirname(__file__), "names.txt")
        self.names = read_names_from_file(file_path)
        self.reset_shuffle()
        logger.info(f"随机点名：加载了 {len(self.names)} 个名字")

    def reset_shuffle(self):
        """执行洗牌算法重置队列"""
        self.shuffled_names = self.names.copy()
        random.shuffle(self.shuffled_names)
        self.current_index = 0

    def move_to_corner(self):
        """移动窗口到屏幕右下角"""
        screen = QDesktopWidget().availableGeometry()
        taskbar_height = 80
        x = screen.width() - self.width() - 10
        y = screen.height() - taskbar_height
        self.move(x, y)

    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            self.mouse_press_pos = event.globalPos()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件"""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            distance = (event.globalPos() - self.mouse_press_pos).manhattanLength()
            logger.debug(f"随机点名：鼠标释放，移动距离={distance}")
            
            if distance <= 15:  # 放宽点击判定
                logger.info("随机点名：检测到点击事件")
                self.show_random_name()
            else:
                logger.debug("随机点名：视为拖拽操作")
            event.accept()

    def show_random_name(self):
        """显示随机点名结果"""
        try:
            name = self.get_next_name()
            logger.info(f"随机点名：抽取到名字={name}")
            
            if self.result_dialog is None:
                self.result_dialog = NameResultDialog(name, self)
                # 连接重新点名按钮的回调
                self.result_dialog.set_reroll_callback(self.reroll_name)
                logger.debug("随机点名：创建新的结果对话框")
            else:
                self.result_dialog.update_content(name)
                logger.debug("随机点名：更新现有对话框内容")
            
            # 确保对话框显示在最前面
            self.result_dialog.show()
            self.result_dialog.raise_()
            self.result_dialog.activateWindow()
            logger.success("随机点名：结果对话框显示成功")
            
        except Exception as e:
            logger.error(f"随机点名：显示结果时出错: {e}")

    def reroll_name(self):
        """重新点名"""
        logger.info("随机点名：用户点击重新点名")
        if self.result_dialog:
            name = self.get_next_name()
            logger.info(f"随机点名：重新抽取到名字={name}")
            self.result_dialog.update_content(name)

    def get_next_name(self):
        """获取下一个不重复的名字"""
        if not self.shuffled_names:
            return "名单为空"

        if self.current_index >= len(self.shuffled_names):
            self.reset_shuffle()
            logger.debug("随机点名：重新洗牌")

        name = self.shuffled_names[self.current_index]
        self.current_index += 1
        return name

    def closeEvent(self, event):
        """窗口关闭事件"""
        self.closed.emit()
        super().closeEvent(event)


class Plugin(PluginBase):
    """随机点名插件主类"""
    
    def __init__(self, cw_contexts, method):
        super().__init__(cw_contexts, method)
        self.floating_window = None
        
        # 注册小组件以触发execute方法
        self.method.register_widget("random-name-widget.ui", "随机点名", 0)
        logger.info("随机点名插件初始化完成")

    def execute(self):
        """启动插件主功能"""
        logger.info("随机点名插件启动")
        try:
            if not self.floating_window:
                self.floating_window = FloatingWindow()
                logger.info("创建随机点名悬浮窗")
            
            self.floating_window.show()
            logger.success("随机点名悬浮窗显示成功")
            
        except Exception as e:
            logger.error(f"随机点名插件启动失败: {e}")


class Settings(SettingsBase):
    """插件设置类"""
    
    def __init__(self, plugin_path, parent=None):
        super().__init__(plugin_path, parent)
        # 这里可以添加设置界面的实现
        pass