from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.list import ThreeLineAvatarIconListItem, IconRightWidget
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
                padding: [0, 40, 0, 0]  # Adds 20dp padding between the toolbar and the list
'''


class MainApp(MDApp):
    dialog = None
    settings_dialog = None

    def build(self):
        self.theme_cls.primary_palette = "Blue"  # Set the primary color palette
        self.theme_cls.theme_style = "Light"  # Set the theme to Light or Dark
        return Builder.load_string(KV)

    def add_list_item(self, name, last_practiced=None, practice_count=0):
        # Format the subtitle depending on the last_practiced value
        last_practiced_text = self.format_last_practiced(last_practiced)

        # Create a new ThreeLine list item with Name, Last Practiced, and Practice Count
        list_item = ThreeLineAvatarIconListItem(
            text=name,
            secondary_text=f"Last Practiced: {last_practiced_text}",
            tertiary_text=f"Practice Count: {practice_count}"
        )

        # Create the trailing vertical dots icon (settings)
        trailing_icon = IconRightWidget(icon="dots-vertical")
        trailing_icon.bind(on_release=lambda x: self.show_item_settings_popup(name))

        # Add the trailing icon to the list item
        list_item.add_widget(trailing_icon)

        # Add the list item to the MDList
        self.root.ids.item_list.add_widget(list_item)

    def show_item_settings_popup(self, name):
        """Show a popup with 'Add Session', 'Edit Last Practice Date', and 'Delete'."""
        if not self.settings_dialog:
            self.settings_dialog = MDDialog(
                title=f"Options for {name}",
                type="confirmation",
                buttons=[
                    MDFlatButton(
                        text="ADD SESSION", on_release=lambda x: self.handle_action("Add Session", name)
                    ),
                    MDFlatButton(
                        text="EDIT LAST PRACTICE DATE", on_release=lambda x: self.handle_action("Edit Last Practice Date", name)
                    ),
                    MDFlatButton(
                        text="DELETE", on_release=lambda x: self.handle_action("Delete", name)
                    ),
                ]
            )
        self.settings_dialog.open()

    def handle_action(self, action, name):
        """Handle actions selected from the popup."""
        print(f"{action} selected for session: {name}")
        self.settings_dialog.dismiss()

    def format_last_practiced(self, last_practiced):
        """Format the 'Last Practiced' field."""
        if not last_practiced:
            return "Never"

        today = datetime.now().date()
        days_elapsed = (today - last_practiced).days

        if days_elapsed == 0:
            return "Today"
        elif days_elapsed > 0:
            return f"{days_elapsed} days ago"
        else:
            return "Invalid date"

    def on_menu_button(self):
        print("Menu button pressed")

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
