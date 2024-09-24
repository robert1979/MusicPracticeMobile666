import os
import json
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.list import ThreeLineAvatarIconListItem, IconRightWidget, IconLeftWidget
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from datetime import datetime, timedelta
from kivy.utils import platform
from kivy.storage.jsonstore import JsonStore  # Import JsonStore
from item_popup import ItemPopup  # Import the ItemPopup class
from kivymd.uix.menu import MDDropdownMenu
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from sort_popup import SortPopup


# Import permissions for Android
if platform == 'android':
    from android.permissions import Permission, request_permissions, check_permission
    from android import mActivity
    from android.storage import app_storage_path

# Define global list of 4 colors
SESSION_COLORS = ['#FFCDD2', '#C8E6C9', '#BBDEFB', '#FFF9C4']  # Red, Green, Blue, Yellow


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
        print("MusApp- Building the application UI...")
        self.theme_cls.primary_palette = "Blue"  # Set the primary color palette
        self.theme_cls.theme_style = "Light"  # Set the theme to Light or Dark

        # Initialize JsonStore without worrying about file paths
        self.store = JsonStore('sessions_data.json')

        self.menu = None  # Initialize the menu attribute to None
        return Builder.load_string(KV)

    def on_start(self):
        """Called after the app is fully initialized and the UI is ready."""
        if platform == 'android':
            self.request_android_permissions()
            if not check_permission(Permission.WRITE_EXTERNAL_STORAGE):
                print("MusApp- Permission not granted after request.")
            else:
                print("MusApp- Permission granted after request.")
        self.load_data()
        self.populate_ui()

    def request_android_permissions(self):
        """Request necessary Android permissions."""
        if platform == 'android':
            try:
                request_permissions([Permission.WRITE_EXTERNAL_STORAGE,
                                     Permission.READ_EXTERNAL_STORAGE])
                print("MusApp- Permissions requested.")
            except Exception as e:
                print(f"MusApp- Permission request failed: {e}")

    def save_data(self):
        """Save session data to JsonStore from the runtime dictionary."""
        serializable_sessions = {}
        for name, session in self.sessions.items():
            try:
                serializable_sessions[name] = {
                    'last_practiced': session.get('last_practiced', None),
                    'practice_count': session.get('practice_count', 0),
                    'is_favorite': session.get('is_favorite', False),
                    'session_type': session.get('session_type', 0)  # Default to 0 if not present
                }
            except Exception as e:
                print(f"MusApp- Error processing session '{name}': {e}")

        try:
            self.store.put('sessions', data=serializable_sessions)
            print("MusApp- Data saved successfully.")
        except Exception as e:
            print(f"MusApp- Error saving data to JsonStore: {e}")

    def load_data(self):
        """Load session data from JsonStore into the runtime dictionary."""
        if self.store.exists('sessions'):
            self.sessions = self.store.get('sessions')['data']
            for session_name, session_data in self.sessions.items():
                last_practiced = session_data.get('last_practiced')
                practice_count = session_data.get('practice_count', 0)
                is_favorite = session_data.get('is_favorite', False)
                session_type = session_data.get('session_type', 0)  # Default to 0 if missing

                # Convert last_practiced to date
                last_practiced_date = None if last_practiced is None else datetime.strptime(last_practiced,
                                                                                            "%Y-%m-%d").date()

                # Add the session to the UI
                self.add_list_item(session_name, last_practiced_date, practice_count, is_favorite, session_type)
            print("MusApp- Data loaded:", self.sessions)
        else:
            print("MusApp- No existing session data found.")

    def populate_ui(self):
        """Populate the UI from the session data in the runtime dictionary."""
        self.root.ids.item_list.clear_widgets()  # Clear existing UI items
        for session_name, session_data in self.sessions.items():
            last_practiced = session_data.get('last_practiced')
            practice_count = session_data.get('practice_count', 0)
            is_favorite = session_data.get('is_favorite', False)  # Get the favorite state
            session_type = session_data.get('session_type', 0)  # Get session type, default to 0 if not found

            last_practiced_date = None if last_practiced is None else datetime.strptime(last_practiced,
                                                                                        "%Y-%m-%d").date()

            # Pass the is_favorite and session_type value to add_list_item
            self.add_list_item(session_name, last_practiced_date, practice_count, is_favorite, session_type)

    def add_list_item(self, name, last_practiced=None, practice_count=0, is_favorite=False, session_type=0):
        """Add a new session to the UI and runtime dictionary."""
        last_practiced_text = self.format_last_practiced(last_practiced)

        # Select background color based on session_type (default to 0 if session_type is out of range)
        background_color = SESSION_COLORS[session_type % len(SESSION_COLORS)]

        # Create a new ThreeLine list item with Name, Last Practiced, and Practice Count
        list_item = ThreeLineAvatarIconListItem(
            text=name,
            secondary_text=f"Last Practiced: {last_practiced_text}",
            tertiary_text=f"Practice Count: {practice_count}, Session Type: {session_type}",
            bg_color=get_color_from_hex(background_color)  # Set background color
        )

        list_item.ids._lbl_primary.bold = True

        # Favorite icon
        favorite_icon = IconLeftWidget(icon="star" if is_favorite else "star-outline")
        favorite_icon.bind(on_release=lambda x: self.toggle_favorite(favorite_icon, name))
        list_item.add_widget(favorite_icon)

        # Trailing vertical dots icon (settings)
        trailing_icon = IconRightWidget(icon="dots-vertical")
        trailing_icon.bind(on_release=lambda x: self.show_item_popup(name))
        list_item.add_widget(trailing_icon)

        # Add the list item to the MDList
        self.root.ids.item_list.add_widget(list_item)

        # Ensure the runtime dictionary is updated with the favorite state and session_type
        self.sessions[name] = {
            'last_practiced': last_practiced.strftime('%Y-%m-%d') if last_practiced else None,
            'practice_count': practice_count,
            'is_favorite': is_favorite,
            'session_type': session_type  # Include session_type in the saved data
        }

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
        last_practiced_date = None if last_practiced_str is None else datetime.strptime(last_practiced_str,
                                                                                        "%Y-%m-%d").date()
        session_type = session_data.get('session_type', 0)  # Get session type, default to 0 if not found

        # Pass SESSION_COLORS to ItemPopup
        popup = ItemPopup(session_name, last_practiced_date, self.handle_action, session_type, SESSION_COLORS)
        popup_dialog = popup.create_popup()
        popup_dialog.open()

    def handle_action(self, action, session_name, value=None):
        """Handle actions selected from the popup."""
        if action == "Delete":
            self.delete_session(session_name)
        elif action == "Add Session":
            self.update_session(session_name)
        elif action == "Edit Last Practice Date" and value:
            self.update_last_practiced_date(session_name, value)
        elif action == "Update Session Type":
            # Update session type
            self.update_session_type(session_name, value)

    def update_session_type(self, session_name, new_session_type):
        """Update the session type of a session."""
        # Update the runtime dictionary
        if session_name in self.sessions:
            self.sessions[session_name]['session_type'] = new_session_type

        # Re-populate the UI to reflect the updated color based on session type
        self.populate_ui()

        # Save the updated data
        self.save_data()

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

        if session_name in self.sessions:
            self.sessions[session_name]['last_practiced'] = today.strftime('%Y-%m-%d')
            self.sessions[session_name]['practice_count'] += 1
            # Leave session_type unchanged during this operation

        self.populate_ui()

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
        """Format the 'Last Practiced' field."""
        if not last_practiced:
            return "Never"  # If no date is set

        today = datetime.now().date()
        days_elapsed = (today - last_practiced).days

        if days_elapsed == 0:
            return "Today"
        elif days_elapsed == 1:
            return "1 day ago"
        else:
            return f"{days_elapsed} days ago"

    def on_add_button(self):
        """Show a dialog to add a new session name."""
        if not self.dialog:
            self.dialog = MDDialog(
                title="Add Session",
                type="custom",
                content_cls=MDTextField(
                    hint_text="Enter Name",
                    required=True,
                    text="",  # Initialize with an empty text field
                ),
                buttons=[
                    MDFlatButton(
                        text="CANCEL", on_release=self.close_dialog  # Correctly assign close_dialog
                    ),
                    MDFlatButton(
                        text="ADD", on_release=self.add_session
                    ),
                ],
            )
        else:
            # Clear the text field each time the dialog is opened
            self.dialog.content_cls.text = ""
        self.dialog.open()

    def close_dialog(self, obj):
        self.dialog.dismiss()

    def add_session(self, obj):
        """Add a session based on user input from the dialog."""
        name_input = self.dialog.content_cls.text.strip()
        if name_input:
            # Add the new session to the runtime dictionary and UI
            self.add_list_item(name=name_input, last_practiced=None)
        self.dialog.dismiss()  # Dismiss after adding the session

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

    def close_dialog(self, obj=None):
        """Close the current dialog."""
        if self.dialog:
            self.dialog.dismiss()  # Ensure the add session dialog is dismissed

    def on_sort_button(self, button):
        """Open the sort popup with sorting options."""
        if not hasattr(self, 'sort_popup'):
            # Create the popup with the sorting options
            self.sort_popup = SortPopup(self.sort_sessions, SESSION_COLORS)

        sort_dialog = self.sort_popup.create_popup()
        sort_dialog.open()

    def sort_sessions_by_color(self, color_index):
        """Sort the sessions based on the selected session_type (color index)."""
        sorted_sessions = sorted(
            self.sessions.items(), key=lambda x: (x[1]['session_type'] == color_index, x[0].lower()), reverse=True
        )

        # Clear the current list and re-populate it with the sorted sessions
        self.root.ids.item_list.clear_widgets()
        for session_name, session_data in sorted_sessions:
            last_practiced = session_data.get('last_practiced')
            practice_count = session_data.get('practice_count', 0)
            is_favorite = session_data.get('is_favorite', False)
            session_type = session_data.get('session_type', 0)
            last_practiced_date = None if last_practiced is None else datetime.strptime(last_practiced,
                                                                                        "%Y-%m-%d").date()
            self.add_list_item(session_name, last_practiced_date, practice_count, is_favorite, session_type)

        self.sort_menu.dismiss()  # Close the sorting menu after sorting

    def sort_sessions(self, criteria):
        """Sort the sessions based on the selected criteria."""
        if "color_" in criteria:
            color_index = int(criteria.split("_")[1])
            sorted_sessions = sorted(
                self.sessions.items(),
                key=lambda x: x[1].get('session_type', 0) == color_index,
                reverse=True
            )
        else:
            if criteria == "alphabetical":
                sorted_sessions = sorted(self.sessions.items(), key=lambda x: x[0].lower())
            elif criteria == "practice_count":
                sorted_sessions = sorted(self.sessions.items(), key=lambda x: x[1]['practice_count'], reverse=True)
            elif criteria == "last_practice":
                sorted_sessions = sorted(self.sessions.items(), key=lambda x: x[1]['last_practiced'] or "",
                                         reverse=True)
            elif criteria == "favourites":
                sorted_sessions = sorted(self.sessions.items(), key=lambda x: (not x[1]['is_favorite'], x[0].lower()))

        # Clear the current list and re-populate it with the sorted sessions
        self.root.ids.item_list.clear_widgets()
        for session_name, session_data in sorted_sessions:
            last_practiced = session_data.get('last_practiced')
            practice_count = session_data.get('practice_count', 0)
            is_favorite = session_data.get('is_favorite', False)
            session_type = session_data.get('session_type', 0)
            last_practiced_date = None if last_practiced is None else datetime.strptime(last_practiced,
                                                                                        "%Y-%m-%d").date()
            self.add_list_item(session_name, last_practiced_date, practice_count, is_favorite, session_type)


if __name__ == '__main__':
    MainApp().run()
