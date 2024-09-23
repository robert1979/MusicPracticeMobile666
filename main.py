from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.list import OneLineAvatarIconListItem, IconRightWidget
import random
import string

KV = '''
MDScreen:
    md_bg_color: self.theme_cls.bg_normal

    BoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            title: "Sessions"
            left_action_items: [["menu", lambda x: app.on_menu_button()]]
            right_action_items: [["dots-vertical", lambda x: app.on_more_button()]]
            elevation: 10

        ScrollView:
            MDList:
                id: item_list
'''

class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"  # Set the primary color palette
        self.theme_cls.theme_style = "Light"  # Set the theme to Light or Dark
        return Builder.load_string(KV)

    def on_start(self):
        # Populate the list with randomly generated session names
        self.populate_list()

    def populate_list(self):
        for _ in range(15):  # Generate 15 records
            session_name = self.generate_random_session_name()
            self.add_list_item(session_name)

    def generate_random_session_name(self, length=8):
        # Generate a random session name
        return 'Session ' + ''.join(random.choice(string.ascii_uppercase) for _ in range(length))

    def add_list_item(self, session_name):
        # Create a new list item with the session name
        list_item = OneLineAvatarIconListItem(text=session_name)

        # Create the trailing vertical dots icon (settings)
        trailing_icon = IconRightWidget(icon="dots-vertical")
        trailing_icon.bind(on_release=lambda x: self.on_item_settings(session_name))

        # Add the trailing icon to the list item
        list_item.add_widget(trailing_icon)

        # Add the list item to the MDList
        self.root.ids.item_list.add_widget(list_item)

    def on_menu_button(self):
        print("Menu button pressed")

    def on_more_button(self):
        print("More button pressed")

    def on_item_settings(self, session_name):
        print(f"Settings for: {session_name}")


if __name__ == '__main__':
    MainApp().run()
