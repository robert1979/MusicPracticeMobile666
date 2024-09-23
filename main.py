import json
import os
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.list import ThreeLineAvatarIconListItem, IconRightWidget
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from datetime import datetime, timedelta
from kivy.utils import platform
from item_popup import ItemPopup  # Import the ItemPopup class

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
                padding: [0, 40, 0, 0]  # Adds 40dp padding between the toolbar and the list
'''


class MainApp(MDApp):
    dialog = None
    settings_dialog = None
    data_file = None

    def build(self):
        self.theme_cls.primary_palette = "Blue"  # Set the primary color palette
        self.theme_cls.theme_style = "Light"  # Set the theme to Light or Dark
        self.data_file = self.get_data_file_path()
        return Builder.load_string(KV)

    def on_start(self):
        """Called after the app is fully initialized and the UI is ready."""
        self.load_data()  # Load the session data when the app starts

    def get_data_file_path(self):
        """Return the path to save/load data based on platform compatibility."""
        if platform == 'android':
            return os.path.join(self.user_data_dir, 'sessions_data.json')
        else:
            return os.path.join(os.path.dirname(__file__), 'sessions_data.json')

    def save_data(self, data):
        """Save session data to a JSON file."""
        with open(self.data_file, 'w') as f:
            json.dump(data, f)

    def load_data(self):
        """Load session data from the JSON file and populate the list."""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                sessions = json.load(f)
                for session in sessions:
                    self.add_list_item(
                        name=session['name'],
                        last_practiced=datetime.strptime(session['last_practiced'], "%Y-%m-%d") if session['last_practiced'] else None,
                        practice_count=session['practice_count']
                    )

    def get_sessions_as_dict(self):
        """Get the current sessions as a list of dictionaries."""
        sessions = []
        for child in self.root.ids.item_list.children:
            if isinstance(child, ThreeLineAvatarIconListItem):
                name = child.text
                last_practiced_text = child.secondary_text.split(": ")[-1]
                practice_count = int(child.tertiary_text.split(": ")[-1])
                last_practiced = None if last_practiced_text == 'Never' else last_practiced_text
                sessions.append({
                    'name': name,
                    'last_practiced': last_practiced,
                    'practice_count': practice_count
                })
        return sessions

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
        trailing_icon.bind(on_release=lambda x: self.show_item_popup(name))

        # Add the trailing icon to the list item
        list_item.add_widget(trailing_icon)

        # Add the list item to the MDList
        self.root.ids.item_list.add_widget(list_item)

        # Save data whenever a new session is added
        self.save_data(self.get_sessions_as_dict())

    def show_item_popup(self, session_name):
        """Show the popup using ItemPopup when the settings icon is clicked."""
        popup = ItemPopup(session_name, self.handle_action)
        popup_dialog = popup.create_popup()
        popup_dialog.open()

    def handle_action(self, action, session_name):
        """Handle actions selected from the popup."""
        if action == "Delete":
            self.delete_session(session_name)
        elif action == "Add Session":
            self.update_session(session_name)
        else:
            print(f"{action} selected for session: {session_name}")

    def update_session(self, session_name):
        """Update the session with today's date and increment the practice count."""
        today = datetime.now().date()

        # Find the session by name and update it
        for child in self.root.ids.item_list.children:
            if isinstance(child, ThreeLineAvatarIconListItem) and child.text == session_name:
                # Update last practiced date to today
                child.secondary_text = f"Last Practiced: Today"

                # Increment practice count
                current_count = int(child.tertiary_text.split(": ")[-1])
                child.tertiary_text = f"Practice Count: {current_count + 1}"

                break

        # Save the updated data after changes
        self.save_data(self.get_sessions_as_dict())

    def delete_session(self, session_name):
        """Delete a session by its name."""
        # Find the session by name and remove it from the list
        for child in self.root.ids.item_list.children[:]:
            if isinstance(child, ThreeLineAvatarIconListItem) and child.text == session_name:
                self.root.ids.item_list.remove_widget(child)
                break
        # Save the updated data after deletion
        self.save_data(self.get_sessions_as_dict())

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
