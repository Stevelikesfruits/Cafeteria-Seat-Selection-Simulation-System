# ui/restaurant_view.py
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem
# 1. 在这里加上 QPainter 的导入
from PySide6.QtGui import QBrush, QColor, QPen, QPainter
from PySide6.QtCore import Qt
from models.restaurant import Restaurant, Table2, Table4


class RestaurantView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # 2. 修改抗锯齿的枚举调用方式
        self.setRenderHint(QPainter.RenderHint.Antialiasing)  # 开启抗锯齿，让圆形和斜线更平滑

        self.table_items = {}

        # 默认颜色 (匹配概念图)
        self.table_color = QColor("#4A70C4")  # 桌子蓝色
        self.empty_seat_color = QColor("#4A70C4")  # 空椅子蓝色
        self.occupied_seat_color = QColor("#FFD700")  # 有人落座变成金色高亮

    def init_restaurant_layout(self, restaurant: Restaurant):
        self.scene.clear()
        self.table_items.clear()

        x_offset, y_offset = 50, 50
        max_x = 600

        for table_id, table in restaurant.tables.items():
            if isinstance(table, Table2):
                width, height = 60, 60
            elif isinstance(table, Table4):
                width, height = 100, 60
            else:
                width, height = 60, 60

            if x_offset + width > max_x:
                x_offset = 50
                y_offset += 120

            # 画桌子
            rect = QGraphicsRectItem(x_offset, y_offset, width, height)
            rect.setBrush(QBrush(self.table_color))
            rect.setPen(QPen(Qt.black))
            self.scene.addItem(rect)
            self.table_items[table_id] = {'rect': rect, 'seats': []}

            # 画椅子
            self._draw_seats(table, x_offset, y_offset, width, height)

            x_offset += width + 60

    def _draw_seats(self, table, x, y, w, h):
        seat_radius = 12
        seat_positions = []
        if isinstance(table, Table2):
            # 概念图中双人桌是上下各一个座位
            seat_positions = [(x + w / 2 - seat_radius, y - seat_radius * 2 - 5),
                              (x + w / 2 - seat_radius, y + h + 5)]
        elif isinstance(table, Table4):
            # 概念图中四人桌是上下各两个座位
            seat_positions = [
                (x + 15, y - seat_radius * 2 - 5), (x + w - 15 - seat_radius * 2, y - seat_radius * 2 - 5),
                (x + 15, y + h + 5), (x + w - 15 - seat_radius * 2, y + h + 5)
            ]

        for px, py in seat_positions:
            seat = QGraphicsEllipseItem(px, py, seat_radius * 2, seat_radius * 2)
            seat.setBrush(QBrush(self.empty_seat_color))
            seat.setPen(QPen(Qt.black))
            self.scene.addItem(seat)
            self.table_items[table.id]['seats'].append(seat)

    def update_view(self, restaurant: Restaurant):
        for table_id, table in restaurant.tables.items():
            ui_seats = self.table_items.get(table_id, {}).get('seats', [])
            for i, student_id in enumerate(table.seats):
                if i < len(ui_seats):
                    if student_id != 0:
                        ui_seats[i].setBrush(QBrush(self.occupied_seat_color))
                    else:
                        ui_seats[i].setBrush(QBrush(self.empty_seat_color))