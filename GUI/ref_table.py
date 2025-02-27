import tkinter as tk
from tkinter import ttk

class SimpleTableApp:
    def __init__(self, root):
        self.root = root
        self.root.title("简单表格展示")

        # 预定义的数据
        self.data = [
            [1.23, 4.56, 7.89, 2.34],
            [5.67, 8.90, 1.23, 4.56],
            [7.89, 2.34, 5.67, 8.90],
            [1.23, 4.56, 7.89, 2.34],
            [5.67, 8.90, 1.23, 4.56]
        ]

        # 创建表格
        self.create_table()

    def create_table(self):
        # 使用 Treeview 组件
        columns = [f"列 {i+1}" for i in range(len(self.data[0]))]
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")

        # 设置表头
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor="center")

        # 插入数据
        for row in self.data:
            self.tree.insert("", "end", values=row)

        # 显示表格
        self.tree.pack(padx=10, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleTableApp(root)
    root.mainloop()