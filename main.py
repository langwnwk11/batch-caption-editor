import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from PIL import Image, ImageTk
import os
from collections import Counter
from language import i18n

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.folder_path = ""
        self.image_files = []
        self.caption_files = {}
        self.image_tk = {}
        self.selected_image_path = None
        self.selected_images = set()
        self.create_widgets()
        self.update_language()

    def create_widgets(self):
        # ... (菜单栏和上部、下左、下右框架的代码与之前版本相同，此处省略以保持简洁)
        # 菜单栏
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=i18n.get_text('file'), menu=file_menu)
        file_menu.add_command(label=i18n.get_text('open_folder'), command=self.open_folder)
        
        lang_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label=i18n.get_text('language_menu'), menu=lang_menu)
        lang_menu.add_command(label=i18n.get_text('english'), command=lambda: self.switch_language('en'))
        lang_menu.add_command(label=i18n.get_text('chinese'), command=lambda: self.switch_language('zh'))

        # 主框架
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建可调节的窗格
        self.paned_window = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # --- 上部：横向图片预览 ---
        up_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(up_frame, weight=1)

        # 添加上部标签框架
        up_header = ttk.Frame(up_frame)
        up_header.pack(fill=tk.X, pady=5)
        
        # 添加总图片数标签
        self.total_images_label = ttk.Label(up_header, text="Total Images: 0")
        self.total_images_label.pack(side=tk.LEFT, padx=5)

        up_canvas = tk.Canvas(up_frame)
        h_scroll = ttk.Scrollbar(up_frame, orient=tk.HORIZONTAL, command=up_canvas.xview)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        up_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        up_canvas.configure(xscrollcommand=h_scroll.set)
        
        self.up_scrollable_frame = ttk.Frame(up_canvas)
        up_canvas.create_window((0, 0), window=self.up_scrollable_frame, anchor="nw")
        self.up_scrollable_frame.bind("<Configure>", lambda e: up_canvas.configure(scrollregion=up_canvas.bbox("all")))

        # --- 下部主框架 ---
        down_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(down_frame, weight=3)

        # 创建水平方向的PanedWindow用于左右布局
        down_paned = ttk.PanedWindow(down_frame, orient=tk.HORIZONTAL)
        down_paned.pack(fill=tk.BOTH, expand=True)

        # --- 下部左侧：纵向图片列表 ---
        left_f = ttk.Frame(down_paned)
        down_paned.add(left_f, weight=1)

        left_header = ttk.Frame(left_f)
        left_header.pack(fill=tk.X, pady=5)
        # 初始化时显示0
        self.img_count_label = ttk.Label(left_header, text="Selected Images: 0")
        self.img_count_label.pack(side=tk.LEFT)
        self.clear_button = ttk.Button(left_header, text=i18n.get_text('clear'), command=self.clear_left_frame, width=6)
        self.clear_button.pack(side=tk.RIGHT)
        
        left_canvas = tk.Canvas(left_f)
        v_scroll = ttk.Scrollbar(left_f, orient=tk.VERTICAL, command=left_canvas.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        left_canvas.configure(yscrollcommand=v_scroll.set)
        
        self.left_scrollable_frame = ttk.Frame(left_canvas)
        left_canvas.create_window((0, 0), window=self.left_scrollable_frame, anchor="nw")
        self.left_scrollable_frame.bind("<Configure>", lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all")))

        # --- 下部中间：编辑区域 ---
        middle_f = ttk.Frame(down_paned)
        down_paned.add(middle_f, weight=2)

        # mu - 原始Caption
        mu = ttk.Frame(middle_f)
        mu.pack(fill=tk.BOTH, expand=True)
        self.mu_label = ttk.Label(mu, text=i18n.get_text('original_caption'))
        self.mu_label.pack(anchor='w')
        self.original_caption_text = tk.Text(mu, height=5, state='disabled', wrap=tk.WORD, relief=tk.SOLID, borderwidth=1)
        self.original_caption_text.pack(fill=tk.BOTH, expand=True)

        # mm - 修改后Caption
        mm = ttk.Frame(middle_f)
        mm.pack(fill=tk.BOTH, expand=True, pady=10)
        self.mm_label = ttk.Label(mm, text=i18n.get_text('modified_caption'))
        self.mm_label.pack(anchor='w')
        self.modified_caption_text = tk.Text(mm, height=5, wrap=tk.WORD, relief=tk.SOLID, borderwidth=1)
        self.modified_caption_text.pack(fill=tk.BOTH, expand=True)
        
        # 创建按钮和图片名称的容器
        button_frame = ttk.Frame(mm)
        button_frame.pack(pady=(5,0))
        
        self.save_button = ttk.Button(button_frame, text=i18n.get_text('save'), command=self.save_caption)
        self.save_button.pack(side=tk.LEFT)
        
        # 添加图片名称标签
        self.current_image_label = ttk.Label(button_frame, text="")
        self.current_image_label.pack(side=tk.LEFT, padx=(10,0))

        # --- md - 操作区域 ---
        md = ttk.Frame(middle_f)
        md.pack(fill=tk.X, expand=False, pady=10)
        md.columnconfigure(1, weight=1) # 让输入框可以伸缩

        # 行 0: 查找并替换
        self.replace_label = ttk.Label(md, text=i18n.get_text('replace_label'))
        self.replace_label.grid(row=0, column=0, sticky='w', padx=5, pady=2)
        
        self.replace_find_entry = ttk.Entry(md)
        self.replace_find_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=2)

        self.with_label = ttk.Label(md, text=i18n.get_text('with_label'))
        self.with_label.grid(row=0, column=2, sticky='w', padx=5, pady=2)

        self.replace_with_entry = ttk.Entry(md)
        self.replace_with_entry.grid(row=0, column=3, sticky='ew', padx=5, pady=2)
        md.columnconfigure(3, weight=1) # 让第二个输入框也可以伸缩

        self.replace_button = ttk.Button(md, text=i18n.get_text('replace_button'), command=self.find_and_replace)
        self.replace_button.grid(row=0, column=4, sticky='e', padx=5, pady=2)

        # 定义其他操作 (从行 1 开始)
        other_ops = [
            ('add_prefix_label', 'prefix_entry', 'add_prefix_button', self.add_prefix),
            ('add_suffix_label', 'suffix_entry', 'add_suffix_button', self.add_suffix),
            ('delete_label', 'delete_entry', 'delete_button', self.delete_tag)
        ]
        
        for i, (label_key, entry_name, btn_key, cmd) in enumerate(other_ops, start=1):
            label = ttk.Label(md, text=i18n.get_text(label_key))
            label.grid(row=i, column=0, sticky='w', padx=5, pady=2)
            
            entry = ttk.Entry(md)
            entry.grid(row=i, column=1, columnspan=3, sticky='ew', padx=5, pady=2)
            setattr(self, entry_name, entry)

            button = ttk.Button(md, text=i18n.get_text(btn_key), command=cmd)
            button.grid(row=i, column=4, sticky='e', padx=5, pady=2)

        # 添加保存选项行
        save_frame = ttk.Frame(md)
        save_frame.grid(row=len(other_ops) + 1, column=0, columnspan=5, sticky='ew', pady=5)
        
        # 添加复选框
        self.save_selected_only = tk.BooleanVar(value=True)  # 默认选中
        self.save_selected_checkbox = ttk.Checkbutton(
            save_frame, 
            text=i18n.get_text('save_selected_only'),
            variable=self.save_selected_only
        )
        self.save_selected_checkbox.pack(side=tk.LEFT, padx=5)
        
        # 添加保存按钮
        self.save_all_button = ttk.Button(
            save_frame,
            text=i18n.get_text('save_all_button'),
            command=self.save_all_captions
        )
        self.save_all_button.pack(side=tk.RIGHT, padx=5)

        # 添加重新加载按钮
        self.reload_caption_button = ttk.Button(
            save_frame,
            text=i18n.get_text('reload_caption_button'),
            command=self.refresh_caption
        )
        self.reload_caption_button.pack(side=tk.RIGHT, padx=5)

        # --- 下部右侧：标签统计 ---
        right_f = ttk.Frame(down_paned)
        down_paned.add(right_f, weight=1)
        
        self.right_f_label = ttk.Label(right_f, text=i18n.get_text('tags_in_folder'), anchor="center")
        self.right_f_label.pack(fill=tk.X, pady=5)
        self.tag_list_text = tk.Text(right_f, wrap=tk.WORD, state='disabled', height=1, spacing1=3)
        self.tag_list_text.pack(fill=tk.BOTH, expand=True)

    def update_language(self):
        """更新所有GUI组件的文本"""
        self.title(i18n.get_text('title'))
        self.menu_bar.entryconfig(1, label=i18n.get_text('file'))
        file_menu = self.menu_bar.winfo_children()[0]
        file_menu.entryconfig(i18n.get_text('open_folder'), label=i18n.get_text('open_folder'))
        file_menu.entryconfig(i18n.get_text('language_menu'), label=i18n.get_text('language_menu'))
        lang_menu = file_menu.winfo_children()[0]
        lang_menu.entryconfig(i18n.get_text('english'), label=i18n.get_text('english'))
        lang_menu.entryconfig(i18n.get_text('chinese'), label=i18n.get_text('chinese'))
        
        self.clear_button.config(text=i18n.get_text('clear'))
        self.mu_label.config(text=i18n.get_text('original_caption'))
        self.mm_label.config(text=i18n.get_text('modified_caption'))
        self.save_button.config(text=i18n.get_text('save'))
        
        # 更新操作区 (md) 的文本
        self.replace_label.config(text=i18n.get_text('replace_label'))
        self.with_label.config(text=i18n.get_text('with_label'))
        self.replace_button.config(text=i18n.get_text('replace_button'))
        
        # 获取其他操作的标签和按钮并更新
        md = self.replace_label.master
        md.grid_slaves(row=1, column=0)[0].config(text=i18n.get_text('add_prefix_label'))
        md.grid_slaves(row=1, column=4)[0].config(text=i18n.get_text('add_prefix_button'))
        md.grid_slaves(row=2, column=0)[0].config(text=i18n.get_text('add_suffix_label'))
        md.grid_slaves(row=2, column=4)[0].config(text=i18n.get_text('add_suffix_button'))
        md.grid_slaves(row=3, column=0)[0].config(text=i18n.get_text('delete_label'))
        md.grid_slaves(row=3, column=4)[0].config(text=i18n.get_text('delete_button'))
        
        self.right_f_label.config(text=i18n.get_text('tags_in_folder'))
        
        # 更新保存选项的文本
        self.save_selected_checkbox.config(text=i18n.get_text('save_selected_only'))
        self.save_all_button.config(text=i18n.get_text('save_all_button'))
        self.reload_caption_button.config(text=i18n.get_text('reload_caption_button'))
    
    def switch_language(self, lang):
        i18n.set_language(lang)
        self.update_language()

    # --- 后续方法 (open_folder, load_files, 等) 保持不变, 除了 find_and_replace ---
    def open_folder(self):
        path = filedialog.askdirectory()
        print(f"Selected path: {path}")  # 调试信息
        if not path:
            return
        if not os.path.exists(path):
            messagebox.showerror("Error", "Selected folder does not exist.")
            return
        if not os.access(path, os.R_OK):
            messagebox.showerror("Error", "No permission to access the selected folder.")
            return
        
        # 先清空所有状态
        self.clear_all()
        
        # 设置新的文件夹路径
        self.folder_path = path
        print(f"Set folder_path to: {self.folder_path}")  # 调试信息
        
        # 加载文件
        self.load_files()

    def load_files(self):
        print(f"Loading files from: {self.folder_path}")  # 调试信息
        if not self.folder_path:
            messagebox.showerror("Error", "No folder selected.")
            return
        
        try:
            # 确保 selected_images 是空的
            self.selected_images.clear()
            # 确保计数显示为0
            self.update_image_count()
            
            img_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
            all_files = os.listdir(self.folder_path)
            self.image_files = sorted([f for f in all_files if f.lower().endswith(img_extensions)])

            if not self.image_files:
                messagebox.showinfo("Info", "No images found in the selected folder.")
                return

            for img_file in self.image_files:
                base_name, _ = os.path.splitext(img_file)
                caption_file = base_name + '.txt'
                caption_path = os.path.join(self.folder_path, caption_file)
                if os.path.exists(caption_path):
                    self.caption_files[os.path.join(self.folder_path, img_file)] = caption_path
                else:
                    # 如果不存在，创建一个空的
                    with open(caption_path, 'w', encoding='utf-8') as f:
                        pass
                    self.caption_files[os.path.join(self.folder_path, img_file)] = caption_path

            # 显示图片
            self.display_images()
            # 更新标签列表
            self.update_tag_list()
            # 更新总图片数
            self.total_images_label.config(text=f"Total Images: {len(self.image_files)}")
            # 确保左侧计数为0
            self.update_image_count()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading files: {str(e)}")
            print(f"Error details: {e}")  # 调试信息

    def display_images(self):
        # 清除所有现有的图片显示
        for widget in self.up_scrollable_frame.winfo_children():
            widget.destroy()
        for widget in self.left_scrollable_frame.winfo_children():
            widget.destroy()
        
        # 确保 selected_images 是空的
        self.selected_images.clear()
        # 确保计数显示为0
        self.update_image_count()

        # 只在上方显示图片预览
        for img_path_str in self.image_files:
            full_path = os.path.join(self.folder_path, img_path_str)
            try:
                img = Image.open(full_path)
                
                # 只创建上方预览图
                img_up = img.copy()
                img_up.thumbnail((150, 150))
                tk_img_up = ImageTk.PhotoImage(img_up)

                # 保存引用（只保存上方预览图）
                self.image_tk[full_path] = (tk_img_up, None)

                # 创建上方图片容器
                up_container = ttk.Frame(self.up_scrollable_frame)
                up_container.pack(side=tk.LEFT, padx=5, pady=5)

                # 添加图片名称标签
                name_label = ttk.Label(up_container, text=img_path_str)
                name_label.pack(side=tk.TOP, pady=(0, 2))

                # 创建按钮并绑定双击事件
                up_btn = tk.Button(up_container, image=tk_img_up, 
                                 command=lambda p=full_path: self.select_image(p), 
                                 borderwidth=0)
                up_btn.pack(side=tk.TOP)
                
                # 绑定双击事件
                up_btn.bind('<Double-Button-1>', lambda e, p=full_path: self.add_to_left_canvas(p))

            except Exception as e:
                print(f"Error loading image {full_path}: {e}")

    def select_image(self, img_path):
        self.selected_image_path = img_path
        caption_path = self.caption_files.get(img_path)
        original_content = ""
        modified_content = ""
        
        # 更新图片名称标签
        if img_path:
            image_name = os.path.basename(img_path)
            self.current_image_label.config(text=f"Current: {image_name}")
        
        # 读取原始内容
        if caption_path and os.path.exists(caption_path):
            try:
                with open(caption_path, 'r', encoding='utf-8') as f:
                    original_content = f.read().strip()
            except Exception as e:
                print(f"Error reading caption file: {e}")
                original_content = ""
        
        # 检查是否有修改后的内容
        if hasattr(self, 'modified_captions') and caption_path in self.modified_captions:
            modified_content = self.modified_captions[caption_path]
        else:
            modified_content = original_content

        # 显示原始内容
        self.original_caption_text.config(state='normal')
        self.original_caption_text.delete('1.0', tk.END)
        self.original_caption_text.insert('1.0', original_content)
        self.original_caption_text.config(state='disabled')
        
        # 显示修改后的内容
        self.modified_caption_text.delete('1.0', tk.END)
        self.modified_caption_text.insert('1.0', modified_content)

    def dealAndFormat(self, caption_content):
        """处理并格式化caption内容
        1. 按逗号分割
        2. 去除重复tag（保留第一次出现的）
        3. 每个tag后添加空格
        """
        if not caption_content:
            return ""
            
        # 按逗号分割并去除空白字符
        tags = [tag.strip() for tag in caption_content.split(',') if tag.strip()]
        
        # 使用OrderedDict保持顺序并去重
        from collections import OrderedDict
        unique_tags = list(OrderedDict.fromkeys(tags))
        
        # 用逗号+空格连接所有tag
        return ", ".join(unique_tags)

    def save_caption(self):
        print("save_caption")
        if not self.selected_image_path:
            messagebox.showwarning("Warning", "No image selected.")
            return
        
        caption_path = self.caption_files.get(self.selected_image_path)
        if not caption_path:
            messagebox.showerror("Error", "Cannot find caption file for the selected image.")
            return
            
        new_content = self.modified_caption_text.get('1.0', tk.END).strip()
        # 处理并格式化caption内容
        print(new_content)
        formatted_content = self.dealAndFormat(new_content)
        
        try:
            with open(caption_path, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            
            # 更新原始显示区并刷新标签列表
            self.original_caption_text.config(state='normal')
            self.original_caption_text.delete('1.0', tk.END)
            self.original_caption_text.insert('1.0', formatted_content)
            self.original_caption_text.config(state='disabled')
            
            # 更新修改后的显示区
            self.modified_caption_text.delete('1.0', tk.END)
            self.modified_caption_text.insert('1.0', formatted_content)
            
            self.update_tag_list()
            messagebox.showinfo("Success", "Caption saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save caption: {str(e)}")

    def update_tag_list(self):
        all_tags = []
        for caption_path in self.caption_files.values():
            if os.path.exists(caption_path):
                with open(caption_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        tags = [tag.strip() for tag in content.split(',')]
                        all_tags.extend(tags)
        
        tag_counts = Counter(all_tags)
        
        self.tag_list_text.config(state='normal')
        self.tag_list_text.delete('1.0', tk.END)
        sorted_tags = sorted(tag_counts.items(), key=lambda item: item[1], reverse=True)
        for tag, count in sorted_tags:
            self.tag_list_text.insert(tk.END, f"{tag}({count})\n")
        self.tag_list_text.config(state='disabled')
        
        # 绑定双击事件
        self.tag_list_text.bind('<Double-Button-1>', self.on_tag_double_click)

    def on_tag_double_click(self, event):
        """处理标签双击事件，显示包含该标签的所有图片"""
        # 获取点击位置的行号
        index = self.tag_list_text.index(f"@{event.x},{event.y}")
        line = index.split('.')[0]
        
        # 获取该行的文本
        line_text = self.tag_list_text.get(f"{line}.0", f"{line}.end")
        if not line_text:
            return
            
        # 提取标签名（去掉计数部分）
        tag = line_text.split('(')[0].strip()
        if not tag:
            return
            
        # 清空左侧显示区
        self.clear_left_frame()
        
        # 查找包含该标签的所有图片
        for img_path, caption_path in self.caption_files.items():
            if os.path.exists(caption_path):
                try:
                    with open(caption_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            # 检查标签是否存在（不区分大小写）
                            tags = [t.strip().lower() for t in content.split(',')]
                            if tag.lower() in tags:
                                # 添加到左侧显示区
                                self.add_to_left_canvas(img_path)
                except Exception as e:
                    print(f"Error reading caption file: {e}")
        
        # 显示操作结果
        count = len(self.selected_images)
        if count > 0:
            messagebox.showinfo("Info", f"Found {count} images with tag '{tag}'")
        else:
            messagebox.showinfo("Info", f"No images found with tag '{tag}'")

    def clear_all(self):
        # 清空所有数据
        self.folder_path = ""
        self.image_files.clear()
        self.caption_files.clear()
        self.image_tk.clear()
        self.selected_image_path = None
        self.selected_images.clear()
        
        # 清除所有显示
        for widget in self.up_scrollable_frame.winfo_children(): 
            widget.destroy()
        for widget in self.left_scrollable_frame.winfo_children(): 
            widget.destroy()
        
        # 重置所有文本
        self.original_caption_text.config(state='normal')
        self.original_caption_text.delete('1.0', tk.END)
        self.original_caption_text.config(state='disabled')
        self.modified_caption_text.delete('1.0', tk.END)
        self.tag_list_text.config(state='normal')
        self.tag_list_text.delete('1.0', tk.END)
        self.tag_list_text.config(state='disabled')
        
        # 清除图片名称标签
        self.current_image_label.config(text="")
        
        # 重置计数
        self.total_images_label.config(text="Total Images: 0")
        self.update_image_count()

    def clear_left_frame(self):
        """只清除左侧画布的图片和更新计数"""
        # 清空已选择的图片集合
        self.selected_images.clear()
        
        # 清除左侧画布的所有图片
        for widget in self.left_scrollable_frame.winfo_children():
            widget.destroy()
        
        # 更新图片计数为0
        self.update_image_count()

    # --- 操作函数 ---
    def get_current_tags(self):
        return [tag.strip() for tag in self.modified_caption_text.get('1.0', tk.END).strip().split(',') if tag.strip()]

    def set_current_tags(self, tags):
        self.modified_caption_text.delete('1.0', tk.END)
        self.modified_caption_text.insert('1.0', ", ".join(tags))

    def find_and_replace(self):
        """根据选择模式进行查找替换"""
        find_val = self.replace_find_entry.get().strip()
        replace_val = self.replace_with_entry.get().strip()
        if not find_val: 
            messagebox.showwarning("Warning", "The 'Find' field cannot be empty.")
            return
        
        # 获取要处理的图片列表
        if self.save_selected_only.get():
            # 只处理左侧画布中的图片
            if not self.selected_images:
                messagebox.showwarning("Warning", i18n.get_text('no_images_selected'))
                return
            images_to_process = self.selected_images
        else:
            # 处理所有图片
            images_to_process = [os.path.join(self.folder_path, img) for img in self.image_files]
        
        # 存储修改后的内容
        self.modified_captions = {}  # 用于存储修改后的内容
        
        # 处理每个图片的caption
        for img_path in images_to_process:
            caption_path = self.caption_files.get(img_path)
            if caption_path and os.path.exists(caption_path):
                try:
                    with open(caption_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            # 进行查找替换
                            new_content = content.replace(find_val, replace_val)
                            if new_content != content:  # 只有在内容有变化时才存储
                                self.modified_captions[caption_path] = new_content
                except Exception as e:
                    print(f"Error reading caption for {img_path}: {e}")
        
        # 更新当前显示的caption
        if self.selected_image_path:
            caption_path = self.caption_files.get(self.selected_image_path)
            if caption_path in self.modified_captions:
                self.modified_caption_text.delete('1.0', tk.END)
                self.modified_caption_text.insert('1.0', self.modified_captions[caption_path])
        
        # 显示处理结果
        modified_count = len(self.modified_captions)
        if modified_count > 0:
            if self.save_selected_only.get():
                messagebox.showinfo("Info", f"Found and replaced in {modified_count} selected captions. Click 'Save All Captions' to save changes.")
            else:
                messagebox.showinfo("Info", f"Found and replaced in {modified_count} captions. Click 'Save All Captions' to save changes.")
        else:
            messagebox.showinfo("Info", "No matches found.")

    def add_prefix(self):
        """添加前缀到选中的图片或所有图片的标注"""
        prefix = self.prefix_entry.get().strip()
        if not prefix:
            messagebox.showwarning("Warning", "Please enter a prefix")
            return

        # 初始化modified_captions字典（如果不存在）
        if not hasattr(self, 'modified_captions'):
            self.modified_captions = {}

        if self.save_selected_only.get():
            # 从左侧画布中获取选中的图片
            if not self.selected_images:
                messagebox.showwarning("Warning", i18n.get_text('no_images_selected'))
                return
            
            # 更新选中图片的标注
            for img_path in self.selected_images:
                caption_path = self.caption_files.get(img_path)
                if caption_path and os.path.exists(caption_path):
                    try:
                        # 读取当前内容
                        with open(caption_path, 'r', encoding='utf-8') as f:
                            current_caption = f.read().strip()
                        
                        # 添加前缀，用逗号分隔
                        new_caption = f"{prefix}, {current_caption}" if current_caption else prefix
                        
                        # 存储修改后的内容
                        self.modified_captions[caption_path] = new_caption
                        
                        # 如果当前选中的图片在更新列表中，更新显示
                        if img_path == self.selected_image_path:
                            self.modified_caption_text.delete('1.0', tk.END)
                            self.modified_caption_text.insert('1.0', new_caption)
                            
                    except Exception as e:
                        print(f"Error reading caption file: {e}")
            
            messagebox.showinfo("Info", f"Added prefix to {len(self.selected_images)} selected captions. Click 'Save All Captions' to save changes.")
            
        else:
            # 更新所有图片的标注
            modified_count = 0
            for img_path, caption_path in self.caption_files.items():
                if os.path.exists(caption_path):
                    try:
                        # 读取当前内容
                        with open(caption_path, 'r', encoding='utf-8') as f:
                            current_caption = f.read().strip()
                        
                        # 添加前缀，用逗号分隔
                        new_caption = f"{prefix}, {current_caption}" if current_caption else prefix
                        
                        # 存储修改后的内容
                        self.modified_captions[caption_path] = new_caption
                        modified_count += 1
                        
                        # 如果当前选中的图片在更新列表中，更新显示
                        if img_path == self.selected_image_path:
                            self.modified_caption_text.delete('1.0', tk.END)
                            self.modified_caption_text.insert('1.0', new_caption)
                            
                    except Exception as e:
                        print(f"Error reading caption file: {e}")
            
            messagebox.showinfo("Info", f"Added prefix to {modified_count} captions. Click 'Save All Captions' to save changes.")

    def add_suffix(self):
        """添加后缀到选中的图片或所有图片的标注"""
        suffix = self.suffix_entry.get().strip()
        if not suffix:
            messagebox.showwarning("Warning", "Please enter a suffix")
            return

        # 初始化modified_captions字典（如果不存在）
        if not hasattr(self, 'modified_captions'):
            self.modified_captions = {}

        if self.save_selected_only.get():
            # 从左侧画布中获取选中的图片
            if not self.selected_images:
                messagebox.showwarning("Warning", i18n.get_text('no_images_selected'))
                return
            
            # 更新选中图片的标注
            for img_path in self.selected_images:
                caption_path = self.caption_files.get(img_path)
                if caption_path and os.path.exists(caption_path):
                    try:
                        # 读取当前内容
                        with open(caption_path, 'r', encoding='utf-8') as f:
                            current_caption = f.read().strip()
                        
                        # 添加后缀，用逗号分隔
                        new_caption = f"{current_caption}, {suffix}" if current_caption else suffix
                        
                        # 存储修改后的内容
                        self.modified_captions[caption_path] = new_caption
                        
                        # 如果当前选中的图片在更新列表中，更新显示
                        if img_path == self.selected_image_path:
                            self.modified_caption_text.delete('1.0', tk.END)
                            self.modified_caption_text.insert('1.0', new_caption)
                            
                    except Exception as e:
                        print(f"Error reading caption file: {e}")
            
            messagebox.showinfo("Info", f"Added suffix to {len(self.selected_images)} selected captions. Click 'Save All Captions' to save changes.")
            
        else:
            # 更新所有图片的标注
            modified_count = 0
            for img_path, caption_path in self.caption_files.items():
                if os.path.exists(caption_path):
                    try:
                        # 读取当前内容
                        with open(caption_path, 'r', encoding='utf-8') as f:
                            current_caption = f.read().strip()
                        
                        # 添加后缀，用逗号分隔
                        new_caption = f"{current_caption}, {suffix}" if current_caption else suffix
                        
                        # 存储修改后的内容
                        self.modified_captions[caption_path] = new_caption
                        modified_count += 1
                        
                        # 如果当前选中的图片在更新列表中，更新显示
                        if img_path == self.selected_image_path:
                            self.modified_caption_text.delete('1.0', tk.END)
                            self.modified_caption_text.insert('1.0', new_caption)
                            
                    except Exception as e:
                        print(f"Error reading caption file: {e}")
            
            messagebox.showinfo("Info", f"Added suffix to {modified_count} captions. Click 'Save All Captions' to save changes.")

    def delete_tag(self):
        """删除指定的tag
        1. 如果选中了save_selected_only，只处理左侧选中的图片
        2. 否则处理所有图片
        3. 删除匹配的tag（不区分大小写）
        4. 更新显示
        """
        delete_val = self.delete_entry.get().strip()
        if not delete_val:
            messagebox.showwarning("Warning", "Please enter a tag to delete")
            return

        # 初始化modified_captions字典（如果不存在）
        if not hasattr(self, 'modified_captions'):
            self.modified_captions = {}

        if self.save_selected_only.get():
            # 从左侧画布中获取选中的图片
            if not self.selected_images:
                messagebox.showwarning("Warning", i18n.get_text('no_images_selected'))
                return
            
            # 更新选中图片的标注
            modified_count = 0
            for img_path in self.selected_images:
                caption_path = self.caption_files.get(img_path)
                if caption_path and os.path.exists(caption_path):
                    try:
                        # 读取当前内容
                        with open(caption_path, 'r', encoding='utf-8') as f:
                            current_caption = f.read().strip()
                        
                        if current_caption:
                            # 分割并删除匹配的tag
                            tags = [tag.strip() for tag in current_caption.split(',') if tag.strip()]
                            original_count = len(tags)
                            tags = [tag for tag in tags if tag.lower() != delete_val.lower()]
                            
                            if len(tags) < original_count:
                                # 有tag被删除，更新内容
                                new_caption = ", ".join(tags)
                                self.modified_captions[caption_path] = new_caption
                                modified_count += 1
                                
                                # 如果当前选中的图片在更新列表中，更新显示
                                if img_path == self.selected_image_path:
                                    self.modified_caption_text.delete('1.0', tk.END)
                                    self.modified_caption_text.insert('1.0', new_caption)
                                    
                    except Exception as e:
                        print(f"Error reading caption file: {e}")
            
            if modified_count > 0:
                messagebox.showinfo("Info", f"Deleted tag '{delete_val}' from {modified_count} selected captions. Click 'Save All Captions' to save changes.")
            else:
                messagebox.showinfo("Info", f"Tag '{delete_val}' not found in selected captions.")
            
        else:
            # 更新所有图片的标注
            modified_count = 0
            for img_path, caption_path in self.caption_files.items():
                if os.path.exists(caption_path):
                    try:
                        # 读取当前内容
                        with open(caption_path, 'r', encoding='utf-8') as f:
                            current_caption = f.read().strip()
                        
                        if current_caption:
                            # 分割并删除匹配的tag
                            tags = [tag.strip() for tag in current_caption.split(',') if tag.strip()]
                            original_count = len(tags)
                            tags = [tag for tag in tags if tag.lower() != delete_val.lower()]
                            
                            if len(tags) < original_count:
                                # 有tag被删除，更新内容
                                new_caption = ", ".join(tags)
                                self.modified_captions[caption_path] = new_caption
                                modified_count += 1
                                
                                # 如果当前选中的图片在更新列表中，更新显示
                                if img_path == self.selected_image_path:
                                    self.modified_caption_text.delete('1.0', tk.END)
                                    self.modified_caption_text.insert('1.0', new_caption)
                                    
                    except Exception as e:
                        print(f"Error reading caption file: {e}")
            
            if modified_count > 0:
                messagebox.showinfo("Info", f"Deleted tag '{delete_val}' from {modified_count} captions. Click 'Save All Captions' to save changes.")
            else:
                messagebox.showinfo("Info", f"Tag '{delete_val}' not found in any captions.")

    def update_image_count(self):
        """更新左侧画布的图片数量显示"""
        count = len(self.selected_images)
        self.img_count_label.config(text=f"Selected Images: {count}")

    def add_to_left_canvas(self, img_path):
        """处理双击事件，将图片添加到左侧画布"""
        if img_path in self.selected_images:
            # 如果图片已经在左侧，则移除它
            self.selected_images.remove(img_path)
            # 移除左侧对应的图片按钮
            for widget in self.left_scrollable_frame.winfo_children():
                if hasattr(widget, 'image_path') and widget.image_path == img_path:
                    widget.destroy()
                    break
        else:
            # 如果图片不在左侧，则添加它
            self.selected_images.add(img_path)
            try:
                img = Image.open(img_path)
                img_left = img.copy()
                img_left.thumbnail((150, 150))
                tk_img_left = ImageTk.PhotoImage(img_left)

                # 创建左侧图片容器
                left_container = ttk.Frame(self.left_scrollable_frame)
                left_container.pack(side=tk.TOP, padx=5, pady=5)
                left_container.image_path = img_path  # 存储图片路径到容器

                # 创建按钮
                left_btn = tk.Button(left_container, image=tk_img_left, 
                                   command=lambda p=img_path: self.select_image(p),
                                   borderwidth=0)
                left_btn.pack(side=tk.TOP)
                left_btn.image = tk_img_left  # 保持引用

                # 添加图片名称标签
                name_label = ttk.Label(left_container, text=os.path.basename(img_path))
                name_label.pack(side=tk.TOP, pady=(2, 0))

                # 绑定双击事件到容器
                left_container.bind('<Double-Button-1>', lambda e, p=img_path: self.remove_from_left_canvas(p))
                # 同时绑定到按钮和标签，确保整个区域都能响应双击
                left_btn.bind('<Double-Button-1>', lambda e, p=img_path: self.remove_from_left_canvas(p))
                name_label.bind('<Double-Button-1>', lambda e, p=img_path: self.remove_from_left_canvas(p))

                # 绑定鼠标滚轮事件到左侧画布
                self.left_scrollable_frame.bind_all('<MouseWheel>', self._on_mousewheel)
                # 当鼠标进入左侧画布时启用滚动
                self.left_scrollable_frame.bind('<Enter>', self._bound_to_mousewheel)
                # 当鼠标离开左侧画布时禁用滚动
                self.left_scrollable_frame.bind('<Leave>', self._unbound_to_mousewheel)

            except Exception as e:
                print(f"Error loading image {img_path}: {e}")

        # 更新图片计数
        self.update_image_count()

    def _on_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        # 获取画布的父级（Canvas）
        canvas = self.left_scrollable_frame.master
        # 根据滚轮方向滚动
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bound_to_mousewheel(self, event):
        """绑定鼠标滚轮事件"""
        self.left_scrollable_frame.bind_all('<MouseWheel>', self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        """解绑鼠标滚轮事件"""
        self.left_scrollable_frame.unbind_all('<MouseWheel>')

    def remove_from_left_canvas(self, img_path):
        """处理左侧图片的双击删除事件"""
        if img_path in self.selected_images:
            # 从已选择集合中移除
            self.selected_images.remove(img_path)
            # 移除左侧对应的图片按钮
            for widget in self.left_scrollable_frame.winfo_children():
                if hasattr(widget, 'image_path') and widget.image_path == img_path:
                    widget.destroy()
                    break
            # 更新图片计数
            self.update_image_count()

    def save_all_captions(self):
        """保存所有修改的caption"""
        if not hasattr(self, 'modified_captions') or not self.modified_captions:
            messagebox.showinfo("Info", "No changes to save.")
            return
        
        saved_count = 0
        for caption_path, content in self.modified_captions.items():
            try:
                # 使用dealAndFormat处理内容
                formatted_content = self.dealAndFormat(content)
                with open(caption_path, 'w', encoding='utf-8') as f:
                    f.write(formatted_content)
                saved_count += 1
            except Exception as e:
                print(f"Error saving caption {caption_path}: {e}")
        
        # 清空修改记录
        self.modified_captions = {}
        
        # 更新显示
        if self.selected_image_path:
            caption_path = self.caption_files.get(self.selected_image_path)
            if caption_path and os.path.exists(caption_path):
                with open(caption_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.original_caption_text.config(state='normal')
                    self.original_caption_text.delete('1.0', tk.END)
                    self.original_caption_text.insert('1.0', content)
                    self.original_caption_text.config(state='disabled')
                    self.modified_caption_text.delete('1.0', tk.END)
                    self.modified_caption_text.insert('1.0', content)
        
        messagebox.showinfo("Success", i18n.get_text('save_success').format(count=saved_count))

    def refresh_caption(self):
        """刷新当前图片的标签"""
        if not self.selected_image_path:
            messagebox.showwarning("Warning", i18n.get_text('no_images_selected'))
            return
            
        # 重新加载当前图片的标签
        caption_path = os.path.splitext(self.selected_image_path)[0] + '.txt'
        if os.path.exists(caption_path):
            with open(caption_path, 'r', encoding='utf-8') as f:
                caption = f.read().strip()
                self.original_caption_text.delete('1.0', tk.END)
                self.original_caption_text.insert('1.0', caption)
                # 更新标签列表
                self.update_tag_list()
                # 更新标签计数
                self.update_image_count()


if __name__ == "__main__":
    app = App()
    app.title(i18n.get_text('title'))
    app.geometry("1200x800")
    app.mainloop()