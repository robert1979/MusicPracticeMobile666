import json
import os
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.list import ThreeLineAvatarIconListItem, IconRightWidget,IconLeftWidget
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from datetime import datetime, timedelta
from kivy.utils import platform
from item_popup import ItemPopup  # Import the ItemPopup class
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp

# Import permissions for Android
if platform == 'android':
    from android.permissions import Permission, request_permissions, check_permission

KV = '''
MDScreen:
    md_bg_color: self.theme_cls.bg_normal

    BoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            title: "Practice Sessions"
            left_action_items: [["menu", lambda x: app.show_settings_menu(x)]]
            right_action_items: [["sort", lambda x: app.on_sort_button(x)]]
            elevation: 10

        ScrollView:
            MDList:
                id: item_list
                padding: [0, 0, 0, dp(10)]  # Bottom padding to avoid the FAB overlapping the last item
                size_hint_y: None
                height: self.minimum_height

    MDFloatingActionButton:
        icon: "plus"
        md_bg_color: app.theme_cls.primary_color
        size_hint: None, None
        size: dp(56), dp(56)
        on_release: app.on_add_button()
        # Use fixed padding for positioning:
        x: root.width - self.width - dp(16)  # 16dp padding from the right
        y: dp(16)  # 16dp padding from the bottom
'''




class MainApp(MDApp):
    dialog = None
    settings_dialog = None
    data_file = None
    sessions = {}  # Runtime dictionary for storing session data

    def build(self):
        self.theme_cls.primary_palette = "Blue"  # Set the primary color palette
        self.theme_cls.theme_style = "Light"  # Set the theme to Light or Dark
        self.data_file = self.get_data_file_path()
        self.menu = None  # Initialize the menu attribute to None

        if platform == 'android':
            self.request_android_permissions()  # Request permissions on Android
        return Builder.load_string(KV)

    def on_start(self):
        """Called after the app is fully initialized and the UI is ready."""
        self.load_data()  # Load the session data when the app starts
        self.populate_ui()  # Populate the UI with data from the runtime dictionary

    def request_android_permissions(self):
        """Request necessary Android permissions."""
        if platform == 'android':
            try:
                request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
            except Exception as e:
                print(f"Error requesting permissions: {e}")

    def get_data_file_path(self):
        """Return the path to save/load data based on platform compatibility."""
        if platform == 'android':
            from android.storage import primary_external_storage_path
            storage_dir = primary_external_storage_path()
            return os.path.join(storage_dir, 'sessions_data.json')
        else:
            return os.path.join(os.path.dirname(__file__), 'sessions_data.json')

    def save_data(self):
        """Save session data to a JSON file from the runtime dictionary."""
        with open(self.data_file, 'w') as f:
            json.dump(self.sessions, f, indent=4)  # Save data, including is_favorite

    def load_data(self):
        """Load session data from the JSON file into the runtime dictionary."""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.sessions = json.load(f)

            for session_name, session_data in self.sessions.items():
                last_practiced = session_data.get('last_practiced')
                practice_count = session_data.get('practice_count', 0)
                is_favorite = session_data.get('is_favorite', False)  # Load the favorite state

                # Convert last_practiced to date
                last_practiced_date = None if last_practiced is None else datetime.strptime(last_practiced,
                                                                                            "%Y-%m-%d").date()

                # Add the session to the UI with the favorite state
                self.add_list_item(session_name, last_practiced_date, practice_count, is_favorite)

    def populate_ui(self):
        """Populate the UI from the session data in the runtime dictionary."""
        self.root.ids.item_list.clear_widgets()  # Clear existing UI items
        for session_name, session_data in self.sessions.items():
            last_practiced = session_data.get('last_practiced')
            practice_count = session_data.get('practice_count', 0)
            is_favorite = session_data.get('is_favorite', False)  # Get the favorite state
            last_practiced_date = None if last_practiced is None else datetime.strptime(last_practiced,
                                                                                        "%Y-%m-%d").date()

            # Pass the is_favorite value to add_list_item
            self.add_list_item(session_name, last_practiced_date, practice_count, is_favorite)

    def add_list_item(self, name, last_practiced=None, practice_count=0, is_favorite=False):
        """Add a new session to the UI and runtime dictionary."""
        # Format the subtitle depending on the last_practiced value
        last_practiced_text = self.format_last_practiced(last_practiced)

        # Create a new ThreeLine list item with Name, Last Practiced, and Practice Count
        list_item = ThreeLineAvatarIconListItem(
            text=name,
            secondary_text=f"Last Practiced: {last_practiced_text}",
            tertiary_text=f"Practice Count: {practice_count}"
        )

        # Make the name text bold
        list_item.ids._lbl_primary.bold = True

        # Create the left star icon for favorite using IconLeftWidget
        favorite_icon = IconLeftWidget(icon="star" if is_favorite else "star-outline")

        # Bind the favorite toggle functionality to the icon
        favorite_icon.bind(on_release=lambda x: self.toggle_favorite(favorite_icon, name))

        # Add the favorite icon to the left side of the list item
        list_item.add_widget(favorite_icon)

        # Create the trailing vertical dots icon (settings)
        trailing_icon = IconRightWidget(icon="dots-vertical")
        trailing_icon.bind(on_release=lambda x: self.show_item_popup(name))

        # Add the trailing icon to the list item
        list_item.add_widget(trailing_icon)

        # Add the list item to the MDList
        self.root.ids.item_list.add_widget(list_item)

        # Ensure the runtime dictionary is updated with the favorite state
        self.sessions[name] = {
            'last_practiced': last_practiced.strftime('%Y-%m-%d') if last_practiced else None,
            'practice_count': practice_count,
            'is_favorite': is_favorite  # Save the favorite status explicitly
        }

        # Save data whenever a new session is added or updated
        self.save_data()

    def toggle_favorite(self, icon, session_name):
        """Toggle the favorite state of the session explicitly."""
        # Check the current state of the session's favorite status
        is_favorite = self.sessions[session_name].get('is_favorite', False)

        # Toggle the favorite state
        if not is_favorite:
            icon.icon = "star"  # Switch to filled star if not favorited
            self.sessions[session_name]['is_favorite'] = True  # Update to favorited
        else:
            icon.icon = "star-outline"  # Switch back to outlined star
            self.sessions[session_name]['is_favorite'] = False  # Update to not favorited

        # Save the updated favorite state after toggle
        self.save_data()

    def show_item_popup(self, session_name):
        """Show the popup using ItemPopup when the settings icon is clicked."""
        session_data = self.sessions.get(session_name, {})
        last_practiced_str = session_data.get('last_practiced')
        last_practiced_date = None if last_practiced_str is None else datetime.strptime(last_practiced_str, "%Y-%m-%d").date()

        # Initialize the ItemPopup with the actual date
        popup = ItemPopup(session_name, last_practiced_date, self.handle_action)
        popup_dialog = popup.create_popup()
        popup_dialog.open()

    def handle_action(self, action, session_name, selected_date=None):
        """Handle actions selected from the popup."""
        if action == "Delete":
            self.delete_session(session_name)
        elif action == "Add Session":
            self.update_session(session_name)
        elif action == "Edit Last Practice Date" and selected_date:
            self.update_last_practiced_date(session_name, selected_date)

    def update_last_practiced_date(self, session_name, selected_date):
        """Update the last practiced date of a session."""
        # Update the runtime dictionary
        if session_name in self.sessions:
            self.sessions[session_name]['last_practiced'] = selected_date.strftime('%Y-%m-%d')

        # Format the selected date properly (e.g., "Today", "X days ago")
        formatted_last_practiced = self.format_last_practiced(selected_date)

        # Update the UI
        for child in self.root.ids.item_list.children:
            if isinstance(child, ThreeLineAvatarIconListItem) and child.text == session_name:
                # Update the last practiced date in the UI with the formatted text
                child.secondary_text = f"Last Practiced: {formatted_last_practiced}"
                break

        # Save the updated data after changes
        self.save_data()

    def update_session(self, session_name):
        """Update the session with today's date and increment the practice count."""
        today = datetime.now().date()

        # Update the runtime dictionary
        if session_name in self.sessions:
            self.sessions[session_name]['last_practiced'] = today.strftime('%Y-%m-%d')
            self.sessions[session_name]['practice_count'] += 1

        # Update the UI
        for child in self.root.ids.item_list.children:
            if isinstance(child, ThreeLineAvatarIconListItem) and child.text == session_name:
                # Update last practiced date to today
                child.secondary_text = "Last Practiced: Today"
                # Increment practice count
                current_count = int(child.tertiary_text.split(": ")[-1])
                child.tertiary_text = f"Practice Count: {current_count + 1}"
                break

        # Save the updated data after changes
        self.save_data()

    def delete_session(self, session_name):
        """Delete a session by its name."""
        # Remove from the runtime dictionary
        if session_name in self.sessions:
            del self.sessions[session_name]

        # Remove from the UI
        for child in self.root.ids.item_list.children[:]:
            if isinstance(child, ThreeLineAvatarIconListItem) and child.text == session_name:
                self.root.ids.item_list.remove_widget(child)
                break

        # Save the updated data after deletion
        self.save_data()

    def format_last_practiced(self, last_practiced):
        """Format the 'Last Practiced' field with proper day/day(s) usage."""
        if not last_practiced:
            return "Never"  # If no date is set

        today = datetime.now().date()
        days_elapsed = (today - last_practiced).days

        if days_elapsed == 0:
            return "Today"  # If last practiced is today
        elif days_elapsed == 1:
            return "1 day ago"  # Singular form for 1 day
        elif days_elapsed > 1:
            return f"{days_elapsed} days ago"  # Plural form for more than 1 day
        else:
            return "Invalid date"  # In case there's an issue with future dates

    def on_add_button(self):
        """Show a dialog to add a new session name."""
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
        """Add a session based on user input from the dialog."""
        name_input = self.dialog.content_cls.text.strip()
        if name_input:
            # Add the new session to the runtime dictionary and UI
            self.add_list_item(name=name_input, last_practiced=None)
        self.dialog.dismiss()

    def show_settings_menu(self, button):
        """Display a dropdown menu for settings with 'About' and 'Reset' options."""
        if not hasattr(self, 'settings_menu'):
            menu_items = [
                {
                    "text": "About",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda: self.on_about()
                },
                {
                    "text": "Reset",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda: self.on_reset()
                },
            ]
            self.settings_menu = MDDropdownMenu(
                caller=button,
                items=menu_items,
                width_mult=4,
            )
        self.settings_menu.open()

    def on_about(self):
        """Show an 'About' dialog."""
        if not self.settings_dialog:
            self.settings_dialog = MDDialog(
                title="About",
                text="This is a Music Practice App.\nVersion 1.0",
                buttons=[MDFlatButton(text="OK", on_release=self.close_dialog)],
            )
        self.settings_menu.dismiss()  # Close the settings dropdown menu
        self.settings_dialog.open()

    def on_reset(self):
        """Reset all session data after confirmation."""

        def confirm_reset(instance, obj):
            self.sessions.clear()  # Clear the runtime dictionary
            self.root.ids.item_list.clear_widgets()  # Clear the UI list
            self.save_data()  # Save the empty state
            reset_dialog.dismiss()  # Close the confirmation dialog

        # Create a confirmation dialog for resetting
        reset_dialog = MDDialog(
            title="Confirm Reset",
            text="Are you sure you want to reset all session data?",
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: reset_dialog.dismiss()),
                MDFlatButton(text="RESET", on_release=confirm_reset),
            ],
        )
        self.settings_menu.dismiss()  # Close the settings dropdown menu
        reset_dialog.open()

    def close_dialog(self, obj):
        """Close the current dialog."""
        if self.settings_dialog:
            self.settings_dialog.dismiss()

    def on_sort_button(self, button):
        """Display a dropdown menu with sorting options."""
        if not hasattr(self, 'sort_menu'):
            menu_items = [
                {
                    "text": "Alphabetical",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda: self.sort_sessions("alphabetical")
                },
                {
                    "text": "Practice Count",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda: self.sort_sessions("practice_count")
                },
                {
                    "text": "Last Practice",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda: self.sort_sessions("last_practice")
                },
                {
                    "text": "Favourites",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda: self.sort_sessions("favourites")
                },
            ]
            self.sort_menu = MDDropdownMenu(
                caller=button,
                items=menu_items,
                width_mult=4,
            )
        self.sort_menu.open()

    def sort_sessions(self, criteria):
        """Sort the sessions based on the selected criteria."""
        if criteria == "alphabetical":
            sorted_sessions = sorted(self.sessions.items(), key=lambda x: x[0].lower())
        elif criteria == "practice_count":
            sorted_sessions = sorted(self.sessions.items(), key=lambda x: x[1]['practice_count'], reverse=True)
        elif criteria == "last_practice":
            sorted_sessions = sorted(self.sessions.items(), key=lambda x: x[1]['last_practiced'] or "", reverse=True)
        elif criteria == "favourites":
            # Sort by is_favorite (True first), and then alphabetically
            sorted_sessions = sorted(self.sessions.items(), key=lambda x: (not x[1]['is_favorite'], x[0].lower()))

        # Clear the current list and re-populate it with the sorted sessions
        self.root.ids.item_list.clear_widgets()
        for session_name, session_data in sorted_sessions:
            last_practiced = session_data.get('last_practiced')
            practice_count = session_data.get('practice_count', 0)
            is_favorite = session_data.get('is_favorite', False)
            last_practiced_date = None if last_practiced is None else datetime.strptime(last_practiced,
                                                                                        "%Y-%m-%d").date()
            self.add_list_item(session_name, last_practiced_date, practice_count, is_favorite)

        self.sort_menu.dismiss()  # Close the sorting menu after sorting


if __name__ == '__main__':
    MainApp().run()
