from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
import mysql.connector


# Clickable image for detail view
class ClickableImage(ButtonBehavior, Image):
    pass


# Login/Signup Screen
class LoginSignupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mode = 'login'
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=10)

        self.title_label = Label(text='Login', font_size=24)
        self.layout.add_widget(self.title_label)

        self.name_input = TextInput(hint_text='Name', multiline=False)
        self.email_input = TextInput(hint_text='Email', multiline=False)

        self.username_input = TextInput(hint_text='Username', multiline=False)
        self.layout.add_widget(self.username_input)

        self.password_input = TextInput(hint_text='Password', password=True, multiline=False)
        self.layout.add_widget(self.password_input)

        self.message_label = Label(text='', color=(1, 0, 0, 1))
        self.layout.add_widget(self.message_label)

        self.submit_button = Button(text='Login')
        self.submit_button.bind(on_press=self.submit_action)
        self.layout.add_widget(self.submit_button)

        self.toggle_button = Button(text="Don't have an account? Sign Up")
        self.toggle_button.bind(on_press=self.toggle_mode)
        self.layout.add_widget(self.toggle_button)

        self.add_widget(self.layout)

    def toggle_mode(self, instance):
        self.layout.clear_widgets()
        self.layout.add_widget(self.title_label)

        if self.mode == 'login':
            self.mode = 'signup'
            self.title_label.text = 'Sign Up'
            self.submit_button.text = 'Create Account'
            self.toggle_button.text = 'Already have an account? Login'
            self.layout.add_widget(self.name_input)
            self.layout.add_widget(self.email_input)
        else:
            self.mode = 'login'
            self.title_label.text = 'Login'
            self.submit_button.text = 'Login'
            self.toggle_button.text = "Don't have an account? Sign Up"

        self.layout.add_widget(self.username_input)
        self.layout.add_widget(self.password_input)
        self.layout.add_widget(self.message_label)
        self.layout.add_widget(self.submit_button)
        self.layout.add_widget(self.toggle_button)

    def submit_action(self, instance):
        if self.mode == 'login':
            username = self.username_input.text
            password = self.password_input.text
            if username and password:
                try:
                    conn = mysql.connector.connect(
                        host="localhost",
                        user="root",
                        password="",
                        database="digital_lost_found_system"
                    )
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
                    result = cursor.fetchone()
                    if result:
                        self.message_label.text = f"Welcome back, {username}!"
                        self.manager.current = 'home'
                    else:
                        self.message_label.text = "Invalid login credentials."
                    conn.close()
                except Exception as e:
                    self.message_label.text = f"Database error: {str(e)}"
            else:
                self.message_label.text = "Enter valid username and password."
        else:
            name = self.name_input.text
            email = self.email_input.text
            username = self.username_input.text
            password = self.password_input.text
            if name and email and username and password:
                try:
                    conn = mysql.connector.connect(
                        host="localhost",
                        user="root",
                        password="",
                        database="digital_lost_found_system"
                    )
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO users (name, email, username, password) VALUES (%s, %s, %s, %s)",
                                   (name, email, username, password))
                    conn.commit()
                    conn.close()

                    self.message_label.text = "Account created successfully!"
                    self.name_input.text = ''
                    self.email_input.text = ''
                    self.username_input.text = ''
                    self.password_input.text = ''
                    self.toggle_mode(None)
                except Exception as e:
                    self.message_label.text = f"Database error: {str(e)}"
            else:
                self.message_label.text = "Please fill all signup fields."


# Home Screen
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)

        layout.add_widget(Label(text='Found and Lost Items', font_size=26))
        layout.add_widget(Label(text='What are you looking for?', font_size=18))

        lost_button = Button(text='Lost Items')
        lost_button.bind(on_press=self.go_to_lost)
        layout.add_widget(lost_button)

        found_button = Button(text='Found Items')
        found_button.bind(on_press=self.go_to_found)
        layout.add_widget(found_button)

        back_button = Button(text='Back to Login')
        back_button.bind(on_press=self.go_to_login)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def go_to_lost(self, instance):
        self.manager.get_screen('lost_list').refresh_items()
        self.manager.current = 'lost_list'

    def go_to_found(self, instance):
        self.manager.get_screen('found_list').refresh_items()
        self.manager.current = 'found_list'

    def go_to_login(self, instance):
        self.manager.current = 'login'


# Lost Items List Screen
class LostItemsListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=10)
        self.items_box = BoxLayout(orientation='vertical', spacing=5)
        self.layout.add_widget(Label(text='Lost Items List', font_size=24))
        self.layout.add_widget(self.items_box)

        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        add_btn = Button(text='Add New')
        add_btn.bind(on_press=self.go_to_add)
        back_btn = Button(text='Back to Home')
        back_btn.bind(on_press=self.go_home)
        btn_layout.add_widget(add_btn)
        btn_layout.add_widget(back_btn)
        self.layout.add_widget(btn_layout)

        self.add_widget(self.layout)

    def refresh_items(self):
        self.items_box.clear_widgets()
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="digital_lost_found_system"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT id, item_name, description, photo, contact FROM lost_items")
            for item_id, name, desc, photo_path, contact in cursor.fetchall():
                item_layout = BoxLayout(size_hint_y=None, height=80, spacing=10)

                try:
                    img = ClickableImage(source=photo_path, size_hint_x=0.3)
                except Exception:
                    img = Label(text='No Image', size_hint_x=0.3)

                img.bind(on_press=lambda instance, id=item_id: self.open_item_detail(id))

                item_label = Label(text=f"{name} - {desc}", size_hint_x=0.5)
                edit_btn = Button(text='Edit', size_hint_x=0.1)
                delete_btn = Button(text='Delete', size_hint_x=0.1)
                edit_btn.bind(on_press=lambda x, id=item_id: self.edit_item(id))
                delete_btn.bind(on_press=lambda x, id=item_id: self.delete_item(id))

                item_layout.add_widget(img)
                item_layout.add_widget(item_label)
                item_layout.add_widget(edit_btn)
                item_layout.add_widget(delete_btn)

                self.items_box.add_widget(item_layout)
            conn.close()
        except Exception as e:
            self.items_box.add_widget(Label(text=f"Error: {str(e)}"))

    def open_item_detail(self, item_id):
        detail_screen = self.manager.get_screen('lost_detail')
        detail_screen.load_item(item_id)
        self.manager.current = 'lost_detail'

    def delete_item(self, item_id):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="digital_lost_found_system"
            )
            cursor = conn.cursor()
            cursor.execute("DELETE FROM lost_items WHERE id = %s", (item_id,))
            conn.commit()
            conn.close()
            self.refresh_items()
        except Exception as e:
            print(f"Error deleting: {e}")

    def edit_item(self, item_id):
        edit_screen = self.manager.get_screen('edit_lost')
        edit_screen.load_item(item_id)
        self.manager.current = 'edit_lost'

    def go_home(self, instance):
        self.manager.current = 'home'

    def go_to_add(self, instance):
        self.manager.current = 'lost'


# Lost Item Form Screen
class LostItemScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=10)
        self.layout.add_widget(Label(text='Report Lost Item', font_size=24))

        self.item_name = TextInput(hint_text='Item Name', multiline=False)
        self.description = TextInput(hint_text='Description', multiline=False)
        self.date = TextInput(hint_text='Date Lost (YYYY-MM-DD)', multiline=False)
        self.contact = TextInput(hint_text='Contact Info', multiline=False)
        self.add_photo = TextInput(hint_text='Photo Path (e.g. images/lost1.jpg)', multiline=False)

        self.submit_btn = Button(text='Submit Lost Item')
        self.submit_btn.bind(on_press=self.submit_item)

        self.result_label = Label(text='')

        self.back_btn = Button(text='Back to Lost Items List')
        self.back_btn.bind(on_press=self.back_to_lost_list)

        self.layout.add_widget(self.item_name)
        self.layout.add_widget(self.description)
        self.layout.add_widget(self.date)
        self.layout.add_widget(self.contact)
        self.layout.add_widget(self.add_photo)
        self.layout.add_widget(self.submit_btn)
        self.layout.add_widget(self.result_label)
        self.layout.add_widget(self.back_btn)

        self.add_widget(self.layout)

    def submit_item(self, instance):
        if self.item_name.text and self.description.text and self.date.text and self.contact.text and self.add_photo.text:
            try:
                conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="digital_lost_found_system"
                )
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO lost_items (item_name, description, date_lost, contact, photo)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    self.item_name.text,
                    self.description.text,
                    self.date.text,
                    self.contact.text,
                    self.add_photo.text
                ))
                conn.commit()
                conn.close()

                self.item_name.text = ''
                self.description.text = ''
                self.date.text = ''
                self.contact.text = ''
                self.add_photo.text = ''

                self.manager.get_screen('lost_list').refresh_items()
                self.manager.current = 'lost_list'
            except Exception as e:
                self.result_label.text = f"Error: {str(e)}"
        else:
            self.result_label.text = "Please fill all fields."

    def back_to_lost_list(self, instance):
        self.manager.current = 'lost_list'


# Edit Lost Item Screen
class EditLostItemScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.item_id = None
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=10)
        self.layout.add_widget(Label(text='Edit Lost Item', font_size=24))

        self.item_name = TextInput(hint_text='Item Name', multiline=False)
        self.description = TextInput(hint_text='Description', multiline=False)
        self.date = TextInput(hint_text='Date Lost (YYYY-MM-DD)', multiline=False)
        self.contact = TextInput(hint_text='Contact Info', multiline=False)
        self.add_photo = TextInput(hint_text='Photo Path (e.g. images/lost1.jpg)', multiline=False)

        self.save_btn = Button(text='Save Changes')
        self.save_btn.bind(on_press=self.save_changes)

        self.result_label = Label(text='')

        self.back_btn = Button(text='Back to Lost Items List')
        self.back_btn.bind(on_press=self.back_to_lost_list)

        self.layout.add_widget(self.item_name)
        self.layout.add_widget(self.description)
        self.layout.add_widget(self.date)
        self.layout.add_widget(self.contact)
        self.layout.add_widget(self.add_photo)
        self.layout.add_widget(self.save_btn)
        self.layout.add_widget(self.result_label)
        self.layout.add_widget(self.back_btn)

        self.add_widget(self.layout)

    def load_item(self, item_id):
        self.item_id = item_id
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="digital_lost_found_system"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT item_name, description, date_lost, contact, photo FROM lost_items WHERE id=%s", (item_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                self.item_name.text = row[0]
                self.description.text = row[1]
                self.date.text = row[2]
                self.contact.text = row[3]
                self.add_photo.text = row[4]
                self.result_label.text = ''
            else:
                self.result_label.text = 'Item not found.'
        except Exception as e:
            self.result_label.text = f"Error loading item: {str(e)}"

    def save_changes(self, instance):
        if not self.item_id:
            self.result_label.text = "No item loaded."
            return

        if self.item_name.text and self.description.text and self.date.text and self.contact.text and self.add_photo.text:
            try:
                conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="digital_lost_found_system"
                )
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE lost_items SET item_name=%s, description=%s, date_lost=%s, contact=%s, photo=%s
                    WHERE id=%s
                """, (
                    self.item_name.text,
                    self.description.text,
                    self.date.text,
                    self.contact.text,
                    self.add_photo.text,
                    self.item_id
                ))
                conn.commit()
                conn.close()

                self.result_label.text = "Item updated successfully!"
                self.manager.get_screen('lost_list').refresh_items()
                self.manager.current = 'lost_list'
            except Exception as e:
                self.result_label.text = f"Error updating item: {str(e)}"
        else:
            self.result_label.text = "Please fill all fields."

    def back_to_lost_list(self, instance):
        self.manager.current = 'lost_list'


# Lost Item Detail Screen
class LostItemDetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=10)

        self.image = Image(size_hint=(1, 0.5))
        self.name_label = Label(font_size=24)
        self.contact_label = Label(font_size=18)
        self.description_label = Label(font_size=16)
        self.date_label = Label(font_size=16)
        self.back_btn = Button(text='Back to Lost Items List')
        self.back_btn.bind(on_press=self.go_back)

        self.layout.add_widget(self.image)
        self.layout.add_widget(self.name_label)
        self.layout.add_widget(self.contact_label)
        self.layout.add_widget(self.description_label)
        self.layout.add_widget(self.date_label)
        self.layout.add_widget(self.back_btn)

        self.add_widget(self.layout)

    def load_item(self, item_id):
        try:
            conn = mysql.connector.connect(
                host="localhost", user="root", password="", database="digital_lost_found_system"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT item_name, contact, description, date_lost, photo FROM lost_items WHERE id=%s", (item_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                self.image.source = row[4]
                self.name_label.text = f"Name: {row[0]}"
                self.contact_label.text = f"Contact: {row[1]}"
                self.description_label.text = f"Description: {row[2]}"
                self.date_label.text = f"Date Lost: {row[3]}"
            else:
                self.name_label.text = "Item not found."
        except Exception as e:
            self.name_label.text = f"Error loading details: {str(e)}"

    def go_back(self, instance):
        self.manager.current = 'lost_list'


# Found Items List Screen
class FoundItemsListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=10)
        self.items_box = BoxLayout(orientation='vertical', spacing=5)
        self.layout.add_widget(Label(text='Found Items List', font_size=24))
        self.layout.add_widget(self.items_box)

        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        add_btn = Button(text='Add New')
        add_btn.bind(on_press=self.go_to_add)
        back_btn = Button(text='Back to Home')
        back_btn.bind(on_press=self.go_home)
        btn_layout.add_widget(add_btn)
        btn_layout.add_widget(back_btn)
        self.layout.add_widget(btn_layout)

        self.add_widget(self.layout)

    def refresh_items(self):
        self.items_box.clear_widgets()
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="digital_lost_found_system"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT id, item_name, description, photo, contact FROM found_items")
            for item_id, name, desc, photo_path, contact in cursor.fetchall():
                item_layout = BoxLayout(size_hint_y=None, height=80, spacing=10)

                try:
                    img = ClickableImage(source=photo_path, size_hint_x=0.3)
                except Exception:
                    img = Label(text='No Image', size_hint_x=0.3)

                img.bind(on_press=lambda instance, id=item_id: self.open_item_detail(id))

                item_label = Label(text=f"{name} - {desc}", size_hint_x=0.5)
                edit_btn = Button(text='Edit', size_hint_x=0.1)
                delete_btn = Button(text='Delete', size_hint_x=0.1)
                edit_btn.bind(on_press=lambda x, id=item_id: self.edit_item(id))
                delete_btn.bind(on_press=lambda x, id=item_id: self.delete_item(id))

                item_layout.add_widget(img)
                item_layout.add_widget(item_label)
                item_layout.add_widget(edit_btn)
                item_layout.add_widget(delete_btn)

                self.items_box.add_widget(item_layout)
            conn.close()
        except Exception as e:
            self.items_box.add_widget(Label(text=f"Error: {str(e)}"))

    def open_item_detail(self, item_id):
        detail_screen = self.manager.get_screen('found_detail')
        detail_screen.load_item(item_id)
        self.manager.current = 'found_detail'

    def delete_item(self, item_id):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="digital_lost_found_system"
            )
            cursor = conn.cursor()
            cursor.execute("DELETE FROM found_items WHERE id = %s", (item_id,))
            conn.commit()
            conn.close()
            self.refresh_items()
        except Exception as e:
            print(f"Error deleting: {e}")

    def edit_item(self, item_id):
        edit_screen = self.manager.get_screen('edit_found')
        edit_screen.load_item(item_id)
        self.manager.current = 'edit_found'

    def go_home(self, instance):
        self.manager.current = 'home'

    def go_to_add(self, instance):
        self.manager.current = 'found'


# Found Item Form Screen
class FoundItemScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=10)
        self.layout.add_widget(Label(text='Report Found Item', font_size=24))

        self.item_name = TextInput(hint_text='Item Name', multiline=False)
        self.description = TextInput(hint_text='Description', multiline=False)
        self.date = TextInput(hint_text='Date Found (YYYY-MM-DD)', multiline=False)
        self.contact = TextInput(hint_text='Contact Info', multiline=False)
        self.add_photo = TextInput(hint_text='Photo Path (e.g. images/found1.jpg)', multiline=False)

        self.submit_btn = Button(text='Submit Found Item')
        self.submit_btn.bind(on_press=self.submit_item)

        self.result_label = Label(text='')

        self.back_btn = Button(text='Back to Found Items List')
        self.back_btn.bind(on_press=self.back_to_found_list)

        self.layout.add_widget(self.item_name)
        self.layout.add_widget(self.description)
        self.layout.add_widget(self.date)
        self.layout.add_widget(self.contact)
        self.layout.add_widget(self.add_photo)
        self.layout.add_widget(self.submit_btn)
        self.layout.add_widget(self.result_label)
        self.layout.add_widget(self.back_btn)

        self.add_widget(self.layout)

    def submit_item(self, instance):
        if self.item_name.text and self.description.text and self.date.text and self.contact.text and self.add_photo.text:
            try:
                conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="digital_lost_found_system"
                )
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO found_items (item_name, description, date_found, contact, photo)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    self.item_name.text,
                    self.description.text,
                    self.date.text,
                    self.contact.text,
                    self.add_photo.text
                ))
                conn.commit()
                conn.close()

                self.item_name.text = ''
                self.description.text = ''
                self.date.text = ''
                self.contact.text = ''
                self.add_photo.text = ''

                self.manager.get_screen('found_list').refresh_items()
                self.manager.current = 'found_list'
            except Exception as e:
                self.result_label.text = f"Error: {str(e)}"
        else:
            self.result_label.text = "Please fill all fields."

    def back_to_found_list(self, instance):
        self.manager.current = 'found_list'


# Edit Found Item Screen
class EditFoundItemScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.item_id = None
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=10)
        self.layout.add_widget(Label(text='Edit Found Item', font_size=24))

        self.item_name = TextInput(hint_text='Item Name', multiline=False)
        self.description = TextInput(hint_text='Description', multiline=False)
        self.date = TextInput(hint_text='Date Found (YYYY-MM-DD)', multiline=False)
        self.contact = TextInput(hint_text='Contact Info', multiline=False)
        self.add_photo = TextInput(hint_text='Photo Path (e.g. images/found1.jpg)', multiline=False)

        self.save_btn = Button(text='Save Changes')
        self.save_btn.bind(on_press=self.save_changes)

        self.result_label = Label(text='')

        self.back_btn = Button(text='Back to Found Items List')
        self.back_btn.bind(on_press=self.back_to_found_list)

        self.layout.add_widget(self.item_name)
        self.layout.add_widget(self.description)
        self.layout.add_widget(self.date)
        self.layout.add_widget(self.contact)
        self.layout.add_widget(self.add_photo)
        self.layout.add_widget(self.save_btn)
        self.layout.add_widget(self.result_label)
        self.layout.add_widget(self.back_btn)

        self.add_widget(self.layout)

    def load_item(self, item_id):
        self.item_id = item_id
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="digital_lost_found_system"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT item_name, description, date_found, contact, photo FROM found_items WHERE id=%s", (item_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                self.item_name.text = row[0]
                self.description.text = row[1]
                self.date.text = row[2]
                self.contact.text = row[3]
                self.add_photo.text = row[4]
                self.result_label.text = ''
            else:
                self.result_label.text = 'Item not found.'
        except Exception as e:
            self.result_label.text = f"Error loading item: {str(e)}"

    def save_changes(self, instance):
        if not self.item_id:
            self.result_label.text = "No item loaded."
            return

        if self.item_name.text and self.description.text and self.date.text and self.contact.text and self.add_photo.text:
            try:
                conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="digital_lost_found_system"
                )
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE found_items SET item_name=%s, description=%s, date_found=%s, contact=%s, photo=%s
                    WHERE id=%s
                """, (
                    self.item_name.text,
                    self.description.text,
                    self.date.text,
                    self.contact.text,
                    self.add_photo.text,
                    self.item_id
                ))
                conn.commit()
                conn.close()

                self.result_label.text = "Item updated successfully!"
                self.manager.get_screen('found_list').refresh_items()
                self.manager.current = 'found_list'
            except Exception as e:
                self.result_label.text = f"Error updating item: {str(e)}"
        else:
            self.result_label.text = "Please fill all fields."

    def back_to_found_list(self, instance):
        self.manager.current = 'found_list'


# Found Item Detail Screen
class FoundItemDetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=10)

        self.image = Image(size_hint=(1, 0.5))
        self.name_label = Label(font_size=24)
        self.contact_label = Label(font_size=18)
        self.description_label = Label(font_size=16)
        self.date_label = Label(font_size=16)
        self.back_btn = Button(text='Back to Found Items List')
        self.back_btn.bind(on_press=self.go_back)

        self.layout.add_widget(self.image)
        self.layout.add_widget(self.name_label)
        self.layout.add_widget(self.contact_label)
        self.layout.add_widget(self.description_label)
        self.layout.add_widget(self.date_label)
        self.layout.add_widget(self.back_btn)

        self.add_widget(self.layout)

    def load_item(self, item_id):
        try:
            conn = mysql.connector.connect(
                host="localhost", user="root", password="", database="digital_lost_found_system"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT item_name, contact, description, date_found, photo FROM found_items WHERE id=%s", (item_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                self.image.source = row[4]
                self.name_label.text = f"Name: {row[0]}"
                self.contact_label.text = f"Contact: {row[1]}"
                self.description_label.text = f"Description: {row[2]}"
                self.date_label.text = f"Date Found: {row[3]}"
            else:
                self.name_label.text = "Item not found."
        except Exception as e:
            self.name_label.text = f"Error loading details: {str(e)}"

    def go_back(self, instance):
        self.manager.current = 'found_list'


# Main app
class LostFoundApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginSignupScreen(name='login'))
        sm.add_widget(HomeScreen(name='home'))

        sm.add_widget(LostItemsListScreen(name='lost_list'))
        sm.add_widget(LostItemScreen(name='lost'))
        sm.add_widget(EditLostItemScreen(name='edit_lost'))
        sm.add_widget(LostItemDetailScreen(name='lost_detail'))

        sm.add_widget(FoundItemsListScreen(name='found_list'))
        sm.add_widget(FoundItemScreen(name='found'))
        sm.add_widget(EditFoundItemScreen(name='edit_found'))
        sm.add_widget(FoundItemDetailScreen(name='found_detail'))

        return sm


if __name__ == '__main__':
    LostFoundApp().run()