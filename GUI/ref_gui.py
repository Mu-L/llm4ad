import tkinter as tk
from tkinter import ttk, messagebox


class AlgorithmConfigGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("算法配置工具")

        # 初始化算法数据
        self.available_algorithms = {
            "随机森林": {"n_estimators": 100, "max_depth": 5},
            "支持向量机": {"C": 1.0, "kernel": "rbf"},
            "神经网络": {"hidden_layers": 3, "learning_rate": 0.01},
            "梯度提升树": {"n_estimators": 50, "learning_rate": 0.1}
        }

        self.selected_algorithms = {}  # 存储已选算法及其参数

        # 创建界面组件
        self.create_widgets()

    def create_widgets(self):
        # 主容器布局
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky="nsew")

        # 算法选择区域
        selection_frame = ttk.LabelFrame(main_frame, text="算法选择", padding=10)
        selection_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # 可用算法列表
        self.algorithm_listbox = tk.Listbox(
            selection_frame,
            selectmode=tk.SINGLE,
            height=8,
            width=25
        )
        for algo in self.available_algorithms:
            self.algorithm_listbox.insert(tk.END, algo)
        self.algorithm_listbox.grid(row=0, column=0, padx=5, pady=5)

        # 操作按钮
        button_frame = ttk.Frame(selection_frame)
        button_frame.grid(row=0, column=1, padx=5, pady=5)

        self.add_button = ttk.Button(
            button_frame,
            text="添加 >>",
            command=self.add_algorithm
        )
        self.add_button.pack(pady=5)

        self.remove_button = ttk.Button(
            button_frame,
            text="<< 删除",
            command=self.remove_algorithm
        )
        self.remove_button.pack(pady=5)

        # 已选算法列表
        self.selected_listbox = tk.Listbox(
            selection_frame,
            selectmode=tk.SINGLE,
            height=8,
            width=25
        )
        self.selected_listbox.grid(row=0, column=2, padx=5, pady=5)
        self.selected_listbox.bind("<<ListboxSelect>>", self.show_parameters)

        # 参数配置区域
        self.param_frame = ttk.LabelFrame(main_frame, text="参数配置", padding=10)
        self.param_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # 配置网格权重
        main_frame.columnconfigure(0, weight=1)
        selection_frame.columnconfigure(0, weight=1)
        selection_frame.columnconfigure(2, weight=1)

    def add_algorithm(self):
        selected = self.algorithm_listbox.curselection()
        if not selected:
            return

        algo_name = self.algorithm_listbox.get(selected[0])
        if algo_name not in self.selected_algorithms:
            # 复制默认参数
            self.selected_algorithms[algo_name] = self.available_algorithms[algo_name].copy()
            self.selected_listbox.insert(tk.END, algo_name)
            self.create_parameter_controls(algo_name)

    def remove_algorithm(self):
        selected = self.selected_listbox.curselection()
        if not selected:
            return

        algo_name = self.selected_listbox.get(selected[0])
        del self.selected_algorithms[algo_name]
        self.selected_listbox.delete(selected[0])
        self.clear_parameters()

    def create_parameter_controls(self, algo_name):
        # 为每个算法创建独立的参数控件容器
        param_container = ttk.Frame(self.param_frame)
        param_container.grid(row=0, column=0, sticky="nsew")
        param_container.grid_remove()  # 初始隐藏

        # 存储参数控件引用
        param_controls = {}
        params = self.selected_algorithms[algo_name]

        for i, (param, value) in enumerate(params.items()):
            ttk.Label(param_container, text=f"{param}:").grid(row=i, column=0, sticky="e")

            if isinstance(value, (int, float)):
                entry = ttk.Entry(param_container)
                entry.insert(0, str(value))
                entry.grid(row=i, column=1, padx=5, pady=2)
                param_controls[param] = entry
            else:
                # 可以根据需要添加其他控件类型（如Combobox）
                pass

        # 保存参数控件引用
        self.selected_algorithms[algo_name]["_controls"] = {
            "container": param_container,
            "widgets": param_controls
        }

    def show_parameters(self, event):
        self.clear_parameters()
        selected = self.selected_listbox.curselection()
        if not selected:
            return

        algo_name = self.selected_listbox.get(selected[0])
        if "_controls" in self.selected_algorithms[algo_name]:
            controls = self.selected_algorithms[algo_name]["_controls"]
            controls["container"].grid()

    def clear_parameters(self):
        for child in self.param_frame.winfo_children():
            child.grid_remove()


if __name__ == "__main__":
    root = tk.Tk()
    app = AlgorithmConfigGUI(root)
    root.mainloop()