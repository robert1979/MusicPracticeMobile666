from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.pickers import MDDatePicker

class ItemPopup:

    def __init__(self, session_name, last_practiced_date, callback):
        """Initialize the popup with a session name, last practice date, and a callback function."""
        self.session_name = session_name
        self.last_practiced_date = last_practiced_date
        self.callback = callback
        self.dialog = None

    def create_popup(self):
        """Create the popup with buttons for 'Add Session', 'Edit Last Practice Date', and 'Delete'."""
        if not self.dialog:
            edit_button = MDFlatButton(
                text="EDIT LAST PRACTICE DATE",
                on_release=lambda x: self.show_date_picker()
            )
            # Grey out the button if last_practiced_date is not set
            if self.last_practiced_date is None:
                edit_button.disabled = True

            self.dialog = MDDialog(
                title=f"{self.session_name}",
                type="confirmation",
                buttons=[
                    MDFlatButton(
                        text="ADD SESSION", on_release=lambda x: self.show_add_session_confirmation()
                    ),
                    edit_button,
                    MDFlatButton(
                        text="DELETE", on_release=lambda x: self.on_button_press("Delete")
                    ),
                ],
            )
        return self.dialog

    def show_date_picker(self):
        """Show a date picker to select a new last practice date."""
        print("Date Picker opened")  # Debugging
        date_picker = MDDatePicker()
        date_picker.bind(on_save=self.set_last_practice_date)  # Explicitly bind the callback
        date_picker.open()

    def set_last_practice_date(self, instance, value, date_range):
        """Callback when a date is selected from the date picker."""
        print(f"Date selected: {value}")  # Debugging
        self.callback("Edit Last Practice Date", self.session_name, value)

    def show_add_session_confirmation(self):
        """Show confirmation dialog before adding a session."""
        confirmation_dialog = MDDialog(
            title="Confirm Session Addition",
            text="Are you sure you want to update the session?",
            buttons=[
                MDFlatButton(
                    text="CANCEL", on_release=lambda x: confirmation_dialog.dismiss()
                ),
                MDFlatButton(
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
