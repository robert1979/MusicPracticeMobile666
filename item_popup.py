from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.pickers import MDDatePicker

# Define the popup layout using KV string
popup_kv = '''
<CustomButtonBox>:
    orientation: 'vertical'
    padding: dp(10)
    spacing: dp(10)
    size_hint_y: None
    size_hint_x: 0.8  # Center horizontally
    pos_hint: {'center_x': 0.5}
    height: self.minimum_height

    MDRaisedButton:
        id: add_button
        text: "ADD PRACTICE"
        size_hint: None, None
        width: dp(200)
        pos_hint: {'center_x': 0.5}
        on_release: root.on_add_practice()

    MDRaisedButton:
        id: edit_button
        text: "EDIT PRACTICE DATE"
        size_hint: None, None
        width: dp(200)
        pos_hint: {'center_x': 0.5}
        on_release: root.on_edit_practice_date()

    MDRaisedButton:
        id: delete_button
        text: "DELETE"
        size_hint: None, None
        width: dp(200)
        pos_hint: {'center_x': 0.5}
        on_release: root.on_delete_practice()
'''

# Load the KV string to apply it
Builder.load_string(popup_kv)

class CustomButtonBox(BoxLayout):
    def __init__(self, session_name, last_practiced_date, callback, **kwargs):
        """Initialize the popup content with session name, last practice date, and callback."""
        super().__init__(**kwargs)
        self.session_name = session_name
        self.last_practiced_date = last_practiced_date
        self.callback = callback

    def on_add_practice(self):
        """Handle the 'ADD PRACTICE' button press."""
        self.callback('Add Practice', self.session_name)

    def on_edit_practice_date(self):
        """Handle the 'EDIT PRACTICE DATE' button press."""
        if self.last_practiced_date is not None:
            self.show_date_picker()

    def on_delete_practice(self):
        """Handle the 'DELETE' button press."""
        self.callback('Delete Practice', self.session_name)

    def show_date_picker(self):
        """Show a date picker to select a new last practice date."""
        print("Date Picker opened")  # Debugging
        date_picker = MDDatePicker()
        date_picker.bind(on_save=self.set_last_practice_date)  # Explicitly bind the callback
        date_picker.open()

    def set_last_practice_date(self, instance, value, date_range):
        """Callback when a date is selected from the date picker."""
        print(f"Date selected: {value}")  # Debugging
        self.callback("Edit Practice Date", self.session_name, value)

class ItemPopup:

    def __init__(self, session_name, last_practiced_date, callback):
        """Initialize the popup with a session name, last practice date, and a callback function."""
        self.session_name = session_name
        self.last_practiced_date = last_practiced_date
        self.callback = callback
        self.dialog = None

    def create_popup(self):
        """Create the popup with centered buttons using the KV layout."""
        if not self.dialog:
            content_cls = CustomButtonBox(self.session_name, self.last_practiced_date, self.callback)

            self.dialog = MDDialog(
                title=f"{self.session_name}",
                type="custom",
                content_cls=content_cls,  # Load the custom content from the class
                buttons=[],  # No additional buttons are needed
            )

            # Disable the "Edit Practice Date" button if last_practiced_date is None
            if self.last_practiced_date is None:
                content_cls.ids.edit_button.disabled = True

        return self.dialog
