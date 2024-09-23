from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDIconButton,MDFloatingActionButton
from kivymd.uix.pickers import MDDatePicker
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Line

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
            # Disable the "Edit" button if last_practiced_date is not set
            if self.last_practiced_date is None:
                edit_button.disabled = True

            # Delete Button with Icon
            delete_button = MDIconButton(
                icon="delete",
                size_hint=(1, None),
                height="48dp",
                on_release=lambda x: self.on_button_press("Delete")
            )

            # Create a horizontal layout for the additional 4 colored buttons
            color_button_layout = BoxLayout(
                orientation='horizontal',  # Children laid out horizontally
                spacing=30,
                size_hint=(1, None),  # Disable size hints to allow manual control
                height='48dp'  # Set the desired height
            )

            # Define colors for the buttons (using hex colors)
            colors = ['#FF0000', '#0000FF', '#00FF00', '#FFFF00']  # Red, Blue, Green, Yellow
            for color in colors:
                color_button = MDFloatingActionButton(
                    md_bg_color=get_color_from_hex(color),
                    size_hint=(1, 1),
                    on_release=lambda x, c=color: self.on_color_button_press(c)  # Corrected lambda with default argument
                )
                color_button_layout.add_widget(color_button)



            button_layout = BoxLayout(
                orientation='horizontal',  # Children laid out horizontally
                spacing=10,
                padding=10,
                size_hint=(1, None),  # Disable size hints to allow manual control
                height='48dp',  # Set the desired height
                pos_hint={'center_x': 0.5}  # Center horizontally
            )
            # Add the buttons to the layout
            button_layout.add_widget(add_button)
            button_layout.add_widget(edit_button)
            button_layout.add_widget(delete_button)

            # Main layout to combine both action buttons and color buttons
            main_layout = BoxLayout(
                orientation='vertical',  # Stack widgets vertically
                spacing=10,
                padding='30dp',
                size_hint=(1, None),  # Disable size hints for manual control
                height='200dp',  # Adjust height to fit content
                pos_hint={'center_x': 0.5, 'center_y': 0}  # Center the main layout both horizontally and vertically
            )
            main_layout.add_widget(button_layout)
            main_layout.add_widget(color_button_layout)

            # Create the dialog with the custom button layout
            self.dialog = MDDialog(
                title=f"{self.session_name}",
                type="custom",
                content_cls=main_layout,  # Use the horizontal button layout
                size_hint=(0.75, None),  # Disable size hints for manual control
                height='200dp',  # Adjust height to fit content
                buttons=[],  # No additional buttons needed
            )

            #self.add_debug_border(color_button_layout, color=(0, 1, 0))

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

    def add_debug_border(self, widget, color=(1, 0, 0)):
        """Adds a debug border to a widget to visualize layout placement."""
        # Remove any previous border to avoid stacking
        widget.canvas.before.clear()

        def draw_border(instance, value):
            """Draw the border when the widget's size/pos changes."""
            widget.canvas.before.clear()
            with widget.canvas.before:
                Color(*color, 1)  # Set the color (default red)
                Line(rectangle=(widget.x, widget.y, widget.width, widget.height), width=2)

        # Bind border drawing to size and position changes
        widget.bind(pos=draw_border, size=draw_border)
