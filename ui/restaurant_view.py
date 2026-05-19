# ui/restaurant_view.py
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem
# 在这里加上 QPainter 的导入
from PySide6.QtGui import QBrush, QColor, QPen, QPainter
from PySide6.QtCore import Qt
from models.restaurant import Restaurant, Table2, Table4

# 设置餐厅界面
class RestaurantView(QGraphicsView):
    def __init__(self):
        super().__init__()
        # 在self的画框上面设置scene画布
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # 修改抗锯齿的枚举调用方式
        # 开启抗锯齿，让圆形和斜线更平滑
        self.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 设置字典用来记录桌子和椅子的序号
        self.table_items = {}

        # 默认颜色
        self.table_color = QColor("#4A70C4")  # 桌子蓝色
        self.empty_seat_color = QColor("#4A70C4")  # 空椅子蓝色
        self.occupied_seat_color = QColor("#FFD700")  # 有人落座变成金色高亮

    def init_restaurant_layout(self, restaurant: Restaurant):
        self.scene.clear()
        self.table_items.clear()

        # 设置第一张桌子的起点
        x_offset, y_offset = 50, 50
        # 横向最大绘制宽度，超过则换行
        max_x = 600

        # 从restaurant类里的tables字典取id，桌子类型
        for table_id, table in restaurant.tables.items():
            # 判断table是不是Table2双人桌
            if isinstance(table, Table2):
                width, height = 60, 60
            elif isinstance(table, Table4):
                width, height = 100, 60
            else:
                width, height = 60, 60

            # 换行逻辑：横向超过max_x则重置x，y向下偏移
            if x_offset + width > max_x:
                x_offset = 50
                y_offset += 120

            # 画桌子
            # 从指定坐标绘制相应长宽的矩形
            rect = QGraphicsRectItem(x_offset, y_offset, width, height)
            # 填充桌子颜色
            rect.setBrush(QBrush(self.table_color))
            # 桌子边框黑色
            rect.setPen(QPen(Qt.black))
            # 添加到场景
            self.scene.addItem(rect)
            # 记录桌子的ID
            self.table_items[table_id] = {'rect': rect, 'seats': []}

            # 画椅子
            # table参数传递双人还是四人桌子
            self._draw_seats(table, x_offset, y_offset, width, height)

            x_offset += width + 60

    def _draw_seats(self, table, x, y, w, h):
        # 椅子半径
        seat_radius = 12
        # 座位坐标列表
        seat_positions = []
        if isinstance(table, Table2):
            # 双人桌上下各一个座位
            seat_positions = [(x + w / 2 - seat_radius, y - seat_radius * 2 - 5),
                              (x + w / 2 - seat_radius, y + h + 5)]
        elif isinstance(table, Table4):
            # 四人桌是上下各两个座位
            seat_positions = [
                (x + 15, y - seat_radius * 2 - 5), (x + w - 15 - seat_radius * 2, y - seat_radius * 2 - 5),
                (x + 15, y + h + 5), (x + w - 15 - seat_radius * 2, y + h + 5)
            ]

        for px, py in seat_positions:
            # 创建椭圆（椅子）：参数为左上角坐标 + 宽高（直径=半径*2）
            seat = QGraphicsEllipseItem(px, py, seat_radius * 2, seat_radius * 2)
            # 填充空座位颜色
            seat.setBrush(QBrush(self.empty_seat_color))
            # 椅子边框黑色
            seat.setPen(QPen(Qt.black))
            # 添加到场景
            self.scene.addItem(seat)
            # 记录椅子ID
            # 每个table创建时相当于一个结构体，记录着自己的id
            self.table_items[table.id]['seats'].append(seat)

    # 更新视图函数
    def update_view(self, restaurant: Restaurant):
        # 从restaurant类里的tables字典取id，桌子类型
        for table_id, table in restaurant.tables.items():
            # self.table_items.get(table_id, {})从之前记录的字典里找索引table_id，找到返回对应的value，没找到返回空{}
            # .get('seats', [])从返回的字典里找seats对应的列表
            ui_seats = self.table_items.get(table_id, {}).get('seats', [])
            # 遍历餐桌的座位数据（student_id：0=空，非0=有人）
            for i, student_id in enumerate(table.seats):
                # 避免索引越界
                if i < len(ui_seats):
                    if student_id != 0:
                        # 有人：设置为金色
                        ui_seats[i].setBrush(QBrush(self.occupied_seat_color))
                    else:
                        # 空座位：恢复蓝色
                        ui_seats[i].setBrush(QBrush(self.empty_seat_color))