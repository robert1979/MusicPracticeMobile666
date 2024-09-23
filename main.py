from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.list import TwoLineAvatarIconListItem, IconRightWidget
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from datetime import datetime, timedelta

KV = '''
MDScreen:
    md_bg_color: self.theme_cls.bg_normal

    BoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            title: "Sessions"
            left_action_items: [["menu", lambda x: app.on_menu_button()]]
            right_action_items: [["plus", lambda x: app.on_add_button()]]
            elevation: 10

        ScrollView:
            MDList:
                id: item_list
'''


class MainApp(MDApp):
    dialog = None

    def build(self):
        self.theme_cls.primary_palette = "Blue"  # Set the primary color palette
        self.theme_cls.theme_style = "Light"  # Set the theme to Light or Dark
        return Builder.load_string(KV)

    def add_list_item(self, name, last_practiced=None):
        # Format the subtitle depending on the last_practiced value
        subtitle = self.format_last_practiced(last_practiced)

        # Create a new TwoLine list item with Name as header and Last Practiced as subtitle
        list_item = TwoLineAvatarIconListItem(text=name, secondary_text=subtitle)

        # Create the trailing vertical dots icon (settings)
        trailing_icon = IconRightWidget(icon="dots-vertical")
        trailing_icon.bind(on_release=lambda x: self.on_item_settings(name))

        # Add the trailing icon to the list item
        list_item.add_widget(trailing_icon)

        # Add the list item to the MDList
        self.root.ids.item_list.add_widget(list_item)

    def format_last_practiced(self, last_practiced):
        """Format the 'Last Practiced' field."""
        if not last_practiced:
            return "Last Practiced: Never"

        today = datetime.now().date()
        days_elapsed = (today - last_practiced).days

        if days_elapsed == 0:
            return "Last Practiced: Today"
        elif days_elapsed > 0:
            return f"Last Practiced: {days_elapsed} days ago"
        else:
            return "Last Practiced: Invalid date"

    def on_menu_button(self):
        print("Menu button pressed")

    def on_item_settings(self, name):
        print(f"Settings for: {name}")

    def on_add_button(self):
        # Show a dialog to add a new name
        if not self.dialog:
            self.dialog = MDDialog(
                title="Add Session",
                type="custom",
                content_cls=MDTextField(
                    hint_text="Enter Name",
                    required=True
                ),
                buttons=[
                    MDFlatButton(
                        text="CANCEL", on_release=self.close_dialog
                    ),
                    MDFlatButton(
                        text="ADD", on_release=self.add_session
                    ),
                ],
            )
        self.dialog.open()

    def close_dialog(self, obj):
        self.dialog.dismiss()

    def add_session(self, obj):
        # Get the input from the dialog
        name_input = self.dialog.content_cls.text.strip()
        if name_input:
            # Add the new session with name, and last practiced as "Unset"
            self.add_list_item(name=name_input, last_practiced=None)
        self.dialog.dismiss()


if __name__ == '__main__':
    MainApp().run()
