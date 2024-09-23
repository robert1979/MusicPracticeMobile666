from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.pickers import MDDatePicker
from kivy.uix.boxlayout import BoxLayout

class ItemPopup:

    def __init__(self, session_name, last_practiced_date, callback):
        """Initialize the popup with a session name, last practice date, and a callback function."""
        self.session_name = session_name
        self.last_practiced_date = last_practiced_date
        self.callback = callback
        self.dialog = None

    def create_popup(self):
        """Create the popup with icon buttons for 'Add Session', 'Edit Last Practice Date', and 'Delete'."""
        if not self.dialog:
            # Create a horizontal layout for the buttons
            button_layout = BoxLayout(orientation='horizontal', spacing=10, padding=10, size_hint_y=None, height='48dp')

            # Add Session Button with Icon
            add_button = MDIconButton(
                icon="plus",
                size_hint=(None, None),
                size=("48dp", "48dp"),
                on_release=lambda x: self.show_add_session_confirmation()
            )

            # Edit Practice Date Button with Icon
            edit_button = MDIconButton(
                icon="pencil",
                size_hint=(None, None),
                size=("48dp", "48dp"),
                on_release=lambda x: self.show_date_picker()
            )
            # Disable the "Edit" button if last_practiced_date is not set
            if self.last_practiced_date is None:
                edit_button.disabled = True

            # Delete Button with Icon
            delete_button = MDIconButton(
                icon="delete",
                size_hint=(None, None),
                size=("48dp", "48dp"),
                on_release=lambda x: self.on_button_press("Delete")
            )

            # Add the buttons to the layout
            button_layout.add_widget(add_button)
            button_layout.add_widget(edit_button)
            button_layout.add_widget(delete_button)

            # Create the dialog with the custom button layout
            self.dialog = MDDialog(
                title=f"{self.session_name}",
                type="custom",
                content_cls=button_layout,  # Use the horizontal button layout
                buttons=[],  # No additional buttons needed
            )

        return self.dialog

    def show_date_picker(self):
        """Show a date picker to select a new last practice date."""
        date_picker = MDDatePicker()
        date_picker.bind(on_save=self.set_last_practice_date)  # Explicitly bind the callback
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
        # Call the callback function with the session name and the action
        self.callback(action, self.session_name)
