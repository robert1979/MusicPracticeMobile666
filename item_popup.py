from operator import index

from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.pickers import MDDatePicker
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Line

class ItemPopup:

    def __init__(self, session_name, last_practiced_date, callback, session_type, session_colors):
        """Initialize the popup with a session name, last practice date, callback, session type, and colors."""
        self.session_name = session_name
        self.last_practiced_date = last_practiced_date
        self.callback = callback
        self.session_type = session_type
        self.session_colors = session_colors  # Use session_colors passed from main.py
        self.dialog = None
        self.color_buttons = []

    def create_popup(self):
        """Create the popup with icon buttons for 'Add Session', 'Edit Last Practice Date', and 'Delete'."""
        if not self.dialog:
            # Add Session Button with Icon
            add_button = MDIconButton(
                icon="plus",
                size_hint=(1, None),
                height="48dp",
                on_release=lambda x: self.show_add_session_confirmation()
            )

            # Edit Practice Date Button with Icon
            edit_button = MDIconButton(
                icon="pencil",
                size_hint=(1, None),
                height="48dp",
                on_release=lambda x: self.show_date_picker()
            )
            if self.last_practiced_date is None:
                edit_button.disabled = True

            # Delete Button with Icon
            delete_button = MDIconButton(
                icon="delete",
                size_hint=(1, None),
                height="44dp",
                on_release=lambda x: self.on_button_press("Delete")
            )

            # Create a horizontal layout for the additional 4 colored buttons
            color_button_layout = BoxLayout(
                orientation='horizontal',
                size_hint=(1, None),
                height='48dp'
            )

            # Create each button individually and bind on_release event afterward
            for index, color in enumerate(self.session_colors):
                print(color)
                color_button = self.create_color_button(color)  # Create button with specific color
                color_button_layout.add_widget(color_button)
                color_button.bind(on_release=lambda btn, idx=index: self.on_color_button_press(idx))  # Bind event

            # Highlight the current session_type button
            self.highlight_selected_button(self.session_type)

            # Create the layout for the other buttons (Add, Edit, Delete)
            button_layout = BoxLayout(
                orientation='horizontal',
                spacing=10,
                padding=10,
                size_hint=(1, None),
                height='48dp',
                pos_hint={'center_x': 0.5}
            )
            button_layout.add_widget(add_button)
            button_layout.add_widget(edit_button)
            button_layout.add_widget(delete_button)

            # Main layout to combine both action buttons and color buttons
            main_layout = BoxLayout(
                orientation='vertical',
                size_hint=(1, None),
                height='200dp',
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
            )
            main_layout.add_widget(button_layout)
            main_layout.add_widget(color_button_layout)

            # Create the dialog with the custom button layout
            self.dialog = MDDialog(
                title=f"{self.session_name}",
                type="custom",
                content_cls=main_layout,
                size_hint=(0.8, None),
                height='200dp',
                buttons=[],
            )

        return self.dialog

    def create_color_button(self, color):
        """Helper function to create a color button."""
        return MDRaisedButton(
            md_bg_color=get_color_from_hex(color),
            size_hint=(1, 1)
        )

    def highlight_selected_button(self, selected_index):
        """Highlight the selected button corresponding to the session_type."""
        for idx, button in enumerate(self.color_buttons):
            button.elevation = 2  # Reset elevation for all buttons
            if idx == selected_index:
                button.elevation = 12  # Highlight selected button

    def on_color_button_press(self, selected_index):
        """Handle color button press and update the session type."""
        # Highlight the selected button
        print(selected_index)
        self.highlight_selected_button(selected_index)

        # Update the session type and pass it back to the main app
        self.session_type = selected_index
        print(selected_index)
        self.callback("Update Session Type", self.session_name, self.session_type)

    def show_date_picker(self):
        """Show a date picker to select a new last practice date."""
        date_picker = MDDatePicker()
        date_picker.bind(on_save=self.set_last_practice_date)
        date_picker.open()

    def set_last_practice_date(self, instance, value, date_range):
        """Callback when a date is selected from the date picker."""
        self.callback("Edit Last Practice Date", self.session_name, value)

    def show_add_session_confirmation(self):
        """Show confirmation dialog before adding a session."""
        confirmation_dialog = MDDialog(
            title="Confirm Session Addition",
            text="Are you sure you want to update the session?",
            buttons=[
                MDRaisedButton(
                    text="CANCEL", on_release=lambda x: confirmation_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="CONFIRM", on_release=lambda x: self.on_button_press("Add Session", confirmation_dialog)
                ),
            ]
        )
        confirmation_dialog.open()

    def on_button_press(self, action, dialog=None):
        """Handle button press and call the provided callback with the action."""
        if dialog:
            dialog.dismiss()
        if self.dialog:
            self.dialog.dismiss()
        self.callback(action, self.session_name)

