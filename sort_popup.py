from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.utils import get_color_from_hex
from kivymd.uix.button import MDRaisedButton, MDFloatingActionButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivy.metrics import dp

class SortPopup:

    def __init__(self, sort_callback, session_colors):
        """Initialize the sort popup with a callback and available session colors."""
        self.sort_callback = sort_callback
        self.session_colors = session_colors
        self.dialog = None

    def create_popup(self):
        """Create a popup with sorting options."""
        if not self.dialog:
            # Create sorting buttons for standard options
            alphabetical_button = MDRaisedButton(
                text="Alphabetical",
                size_hint=(1, None),
                height="48dp",
                on_release=lambda x: self.on_sort("alphabetical")
            )
            practice_count_button = MDRaisedButton(
                text="Practice Count",
                size_hint=(1, None),
                height="48dp",
                on_release=lambda x: self.on_sort("practice_count")
            )
            last_practice_button = MDRaisedButton(
                text="Last Practice",
                size_hint=(1, None),
                height="48dp",
                on_release=lambda x: self.on_sort("last_practice")
            )
            favorites_button = MDRaisedButton(
                text="Favorites",
                size_hint=(1, None),
                height="48dp",
                on_release=lambda x: self.on_sort("favourites")
            )

            # Create color buttons for session_type sorting
            color_button_layout = GridLayout(
                cols=2,
                size_hint=(1, None),
                height="96dp",
                padding=[10, 10, 10, 10],
                spacing=10
            )

            for index, color in enumerate(self.session_colors):
                color_button = MDFloatingActionButton(
                    md_bg_color=get_color_from_hex(color),
                    size_hint=(1, 1),

                    on_release=lambda btn, idx=index: self.on_sort_color(idx)  # Pass index explicitly
                )
                color_button_layout.add_widget(color_button)

            # Create the main layout for the popup
            main_layout = BoxLayout(
                orientation='vertical',
                size_hint=(None, None),

                padding=10,
                spacing=10,
                width='240dp',
                height='300dp'
            )
            main_layout.add_widget(alphabetical_button)
            main_layout.add_widget(practice_count_button)
            main_layout.add_widget(last_practice_button)
            main_layout.add_widget(favorites_button)
            main_layout.add_widget(color_button_layout)

            # Create the popup dialog
            self.dialog = MDDialog(
                title="Sort Sessions",
                type="custom",
                content_cls=main_layout,
                size_hint=(None, None),
                width='300dp',
                height='500dp'
            )

        return self.dialog

    def on_sort(self, criteria):
        """Handle sort by standard criteria."""
        self.sort_callback(criteria)
        self.dialog.dismiss()

    def on_sort_color(self, color_index):
        """Handle sort by session_type (color)."""
        self.sort_callback(f"color_{color_index}")
        self.dialog.dismiss()
