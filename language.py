import configparser
import os

class Language:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        self.config.read(self.config_path, encoding='utf-8')
        self.current_language = self.config.get('Settings', 'language', fallback='en')

    def get_text(self, key):
        """获取指定键的文本"""
        try:
            return self.config.get(self.current_language, key)
        except:
            return key

    def set_language(self, lang):
        """设置语言"""
        if lang in ['en', 'zh']:
            self.current_language = lang
            self.config.set('Settings', 'language', lang)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.config.write(f)

# 创建一个全局实例
i18n = Language()

# i18n = {
#     'en': {
#         'file': 'File',
#         'open_folder': 'Open Folder',
#         'language_menu': 'Language',
#         'english': 'English',
#         'chinese': 'Chinese',
#         'clear': 'Clear',
#         'save': 'Save',
#         'save_all': 'Save All',
#         'save_all_button': 'Save All Captions',
#         'save_selected_only': 'Save Selected Images Only',
#         'refresh_caption': 'Refresh Caption',
#         'tags_in_folder': 'Tags in Folder',
#         'original_caption': 'Original Caption',
#         'modified_caption': 'Modified Caption',
#         'replace_label': 'Find:',
#         'with_label': 'Replace with:',
#         'replace_button': 'Find and Replace',
#         'add_prefix_label': 'Add Prefix:',
#         'add_prefix_button': 'Add Prefix',
#         'add_suffix_label': 'Add Suffix:',
#         'add_suffix_button': 'Add Suffix',
#         'delete_label': 'Delete Tag:',
#         'delete_button': 'Delete Tag',
#         'no_images_selected': 'No images selected',
#         'no_folder_selected': 'No folder selected',
#         'no_images_found': 'No images found in the selected folder',
#         'error_loading_files': 'Error loading files',
#         'error_loading_image': 'Error loading image',
#         'error_saving_caption': 'Error saving caption',
#         'error_saving_captions': 'Error saving captions',
#         'success_saving_caption': 'Caption saved successfully',
#         'success_saving_captions': 'Captions saved successfully',
#         'confirm_save_all': 'Are you sure you want to save all captions?',
#         'confirm_save_selected': 'Are you sure you want to save selected captions?',
#         'confirm_clear': 'Are you sure you want to clear all selected images?',
#         'confirm_delete': 'Are you sure you want to delete this tag?',
#         'confirm_replace': 'Are you sure you want to replace all occurrences?',
#         'confirm_add_prefix': 'Are you sure you want to add this prefix to all tags?',
#         'confirm_add_suffix': 'Are you sure you want to add this suffix to all tags?',
#         'confirm_delete_tag': 'Are you sure you want to delete this tag?',
#         'confirm_delete_all_tags': 'Are you sure you want to delete all tags?',
#         'confirm_delete_selected_tags': 'Are you sure you want to delete selected tags?',
#         'confirm_delete_all_captions': 'Are you sure you want to delete all captions?',
#         'confirm_delete_selected_captions': 'Are you sure you want to delete selected captions?',
#         'confirm_delete_all_images': 'Are you sure you want to delete all images?',
#         'confirm_delete_selected_images': 'Are you sure you want to delete selected images?',
#         'confirm_delete_all': 'Are you sure you want to delete all?',
#         'confirm_delete_selected': 'Are you sure you want to delete selected?',
#         'confirm_delete_all_and_captions': 'Are you sure you want to delete all images and their captions?',
#         'confirm_delete_selected_and_captions': 'Are you sure you want to delete selected images and their captions?',
#         'confirm_delete_all_and_tags': 'Are you sure you want to delete all images and their tags?',
#         'confirm_delete_selected_and_tags': 'Are you sure you want to delete selected images and their tags?',
#         'confirm_delete_all_and_all': 'Are you sure you want to delete all images, captions and tags?',
#         'confirm_delete_selected_and_all': 'Are you sure you want to delete selected images, captions and tags?',
#         'confirm_delete_all_and_all_and_all': 'Are you sure you want to delete all images, captions, tags and all?',
#         'confirm_delete_selected_and_all_and_all': 'Are you sure you want to delete selected images, captions, tags and all?',
#     },
#     'zh': {
#         'file': '文件',
#         'open_folder': '打开文件夹',
#         'language_menu': '语言',
#         'english': '英文',
#         'chinese': '中文',
#         'clear': '清除',
#         'save': '保存',
#         'save_all': '保存全部',
#         'save_all_button': '保存所有标签',
#         'save_selected_only': '仅保存选中的图片',
#         'refresh_caption': '刷新标签',
#         'tags_in_folder': '文件夹中的标签',
#         'original_caption': '原始标签',
#         'modified_caption': '修改后的标签',
#         'replace_label': '查找:',
#         'with_label': '替换为:',
#         'replace_button': '查找并替换',
#         'add_prefix_label': '添加前缀:',
#         'add_prefix_button': '添加前缀',
#         'add_suffix_label': '添加后缀:',
#         'add_suffix_button': '添加后缀',
#         'delete_label': '删除标签:',
#         'delete_button': '删除标签',
#         'no_images_selected': '未选择图片',
#         'no_folder_selected': '未选择文件夹',
#         'no_images_found': '在选定的文件夹中未找到图片',
#         'error_loading_files': '加载文件时出错',
#         'error_loading_image': '加载图片时出错',
#         'error_saving_caption': '保存标签时出错',
#         'error_saving_captions': '保存标签时出错',
#         'success_saving_caption': '标签保存成功',
#         'success_saving_captions': '标签保存成功',
#         'confirm_save_all': '确定要保存所有标签吗？',
#         'confirm_save_selected': '确定要保存选中的标签吗？',
#         'confirm_clear': '确定要清除所有选中的图片吗？',
#         'confirm_delete': '确定要删除此标签吗？',
#         'confirm_replace': '确定要替换所有匹配项吗？',
#         'confirm_add_prefix': '确定要为此标签添加此前缀吗？',
#         'confirm_add_suffix': '确定要为此标签添加此后缀吗？',
#         'confirm_delete_tag': '确定要删除此标签吗？',
#         'confirm_delete_all_tags': '确定要删除所有标签吗？',
#         'confirm_delete_selected_tags': '确定要删除选中的标签吗？',
#         'confirm_delete_all_captions': '确定要删除所有标签吗？',
#         'confirm_delete_selected_captions': '确定要删除选中的标签吗？',
#         'confirm_delete_all_images': '确定要删除所有图片吗？',
#         'confirm_delete_selected_images': '确定要删除选中的图片吗？',
#         'confirm_delete_all': '确定要删除所有吗？',
#         'confirm_delete_selected': '确定要删除选中的吗？',
#         'confirm_delete_all_and_captions': '确定要删除所有图片及其标签吗？',
#         'confirm_delete_selected_and_captions': '确定要删除选中的图片及其标签吗？',
#         'confirm_delete_all_and_tags': '确定要删除所有图片及其标签吗？',
#         'confirm_delete_selected_and_tags': '确定要删除选中的图片及其标签吗？',
#         'confirm_delete_all_and_all': '确定要删除所有图片、标签和所有吗？',
#         'confirm_delete_selected_and_all': '确定要删除选中的图片、标签和所有吗？',
#         'confirm_delete_all_and_all_and_all': '确定要删除所有图片、标签、所有和所有吗？',
#         'confirm_delete_selected_and_all_and_all': '确定要删除选中的图片、标签、所有和所有吗？',
#     }
# }

