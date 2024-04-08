
class Menu:

    def __init__(self, display, menu, modules):
        self._display = display
        self._menu = menu
        self._modules = modules
        self._module_index = 0
        self._module_visible = 0
        self._sub_menu = None
        self._sub_menu_group = None
        self._sub_menu_index = 0
        self._sub_menu_visible = 0
        self.reset_sub_menu()

    def run(self):
        if (self.is_sub_menu_visible()):
            self._sub_menu_visible -= 1
            if (not self.is_sub_menu_visible()):
                self._display.draw_scroll_up_animation(self._modules[self._module_index].get_draw_buffer())
                self.reset_sub_menu()
            return

        self._run_modules()

        self._display.update_brightness()
        self._draw_module()

    def reset_sub_menu(self):
        self._set_sub_menu(self._menu)

    def is_sub_menu_visible(self, seconds=0):
        if (self._sub_menu_visible <= seconds):
            return False
        else:
            return True

    def click(self):
        self._set_sub_menu_visible()

        if ("get_sub_menu" in self._sub_menu[self._sub_menu_index]):
            self._set_sub_menu(self._sub_menu[self._sub_menu_index])
            self._get_buffer_and_draw(self._display.draw_scroll_down_animation)
            self._on_draw()
        elif ("click" in self._sub_menu[self._sub_menu_index]):
            self._sub_menu[self._sub_menu_index]["click"]()
            self._click_animation()
        else:
            self._close_sub_menu()

    def click_left(self, item=None):
        self._set_sub_menu_visible()

        if (self._is_sub_menu(item)):
            return

        if ("click_left" in self._sub_menu[self._sub_menu_index]):
            self._sub_menu[self._sub_menu_index]["click_left"]()
            self._get_buffer_and_draw(self._display.draw)
        else:
            self._sub_menu_index = (self._sub_menu_index - 1) % len(self._sub_menu)
            self._get_buffer_and_draw(self._display.draw_scroll_right_animation)
            self._on_draw()

    def click_right(self, item=None):
        self._set_sub_menu_visible()

        if (self._is_sub_menu(item)):
            return

        if ("click_right" in self._sub_menu[self._sub_menu_index]):
            self._sub_menu[self._sub_menu_index]["click_right"]()
            self._get_buffer_and_draw(self._display.draw)
        else:
            self._sub_menu_index = (self._sub_menu_index + 1) % len(self._sub_menu)
            self._get_buffer_and_draw(self._display.draw_scroll_left_animation)
            self._on_draw()

    def draw_sub_menu_animation(self, anim_dict):
        self._set_sub_menu_visible(anim_dict["length"])
        self._display.draw_animation(anim_dict["buffer"], anim_dict["repeat"], anim_dict["sleep"])

    def draw_sub_menu(self, item):
        self._set_sub_menu_visible()

        if (self._is_sub_menu(item)):
            return

        self._get_buffer_and_draw(self._display.draw)

    def _run_modules(self):
        for module in self._modules:
            module.run()

    def _draw_module(self):
        if (self._modules[self._module_index].is_visible(self._module_visible)):
            self._module_visible = self._module_visible + 1
            self._display.draw(self._modules[self._module_index].get_draw_buffer())
        else:
            self._next_module_index()
            self._display.draw_scroll_left_animation(self._modules[self._module_index].get_draw_buffer())

    def _next_module_index(self):
        self._module_visible = 0
        self._module_index = (self._module_index + 1) % len(self._modules)
        for i in range(self._module_index, len(self._modules)):
            if (self._modules[i].is_visible(self._module_visible)):
                self._module_index = i
                return
        for i in range(self._module_index):
            if (self._modules[i].is_visible(self._module_visible)):
                self._module_index = i
                return

    def _get_buffer_and_draw(self, draw):
        if ("get_buffer" in self._sub_menu[self._sub_menu_index]):
            draw(self._sub_menu[self._sub_menu_index]["get_buffer"]())

    def _on_draw(self):
        if ("on_draw" in self._sub_menu[self._sub_menu_index]):
            self._sub_menu[self._sub_menu_index]["on_draw"]()

    def _click_animation(self):
        if ("click_animation" in self._sub_menu[self._sub_menu_index]):
            self._get_buffer_and_draw(self._display.draw_blink_animation)

    def _close_sub_menu(self):
        if (self._sub_menu_visible > 1):
            self._sub_menu_visible = 1

    def _is_sub_menu(self, item):
        if (item is not None and self._sub_menu_group != item["group"]):
            self._set_sub_menu(item)
            self._get_buffer_and_draw(self._display.draw_scroll_down_animation)
            return True
        return False

    def _set_sub_menu(self, item):
        self._sub_menu = item["get_sub_menu"]()
        self._sub_menu_group = item["group"] if "group" in item else None
        self._sub_menu_index = 0

    def _set_sub_menu_visible(self, seconds=5):
        self._sub_menu_visible = seconds
        self._module_index = 0
        self._module_visible = 0
