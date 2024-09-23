from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton


class ItemPopup:

    def __init__(self, session_name, callback):
        """Initialize the popup with a session name and a callback function."""
        self.session_name = session_name
        self.callback = callback
        self.dialog = None

    def create_popup(self):
        """Create the popup with buttons for 'Add Session', 'Edit Last Practice Date', and 'Delete'."""
        if not self.dialog:
            self.dialog = MDDialog(
                title=f"Options for {self.session_name}",
                type="confirmation",
                buttons=[
                    MDFlatButton(
                        text="ADD SESSION", on_release=lambda x: self.show_add_session_confirmation()
                    ),
                    MDFlatButton(
                        text="EDIT LAST PRACTICE DATE", on_release=lambda x: self.on_button_press("Edit Last Practice Date")
                    ),
                    MDFlatButton(
                        text="DELETE", on_release=lambda x: self.on_button_press("Delete")
                    ),
                ],
            )
        return self.dialog

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
        self.callback(action, self.session_name)
