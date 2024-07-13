import os

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, TwoLineListItem, OneLineListItem
from kivymd.uix.button import MDFloatingActionButton
from dotenv import load_dotenv
from kivy.properties import ObjectProperty
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRectangleFlatButton
from pymongo import MongoClient
from kivymd.uix.menu import MDDropdownMenu
import bcrypt
from kivymd.uix.bottomnavigation import MDBottomNavigation,MDBottomNavigationItem

load_dotenv()
ADMIN_MODE = True if os.getenv("ADMIN_MODE") == "TRUE" else False


# church F7hTLbKj2fbjljrz

# mongodb+srv://church:F7hTLbKj2fbjljrz@cluster0.dwo9y43.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0


class MongoDBInstance:
    _client: MongoClient = None

    @classmethod
    def get_client(cls):
        if not cls._client:
            cls._client = MongoClient(os.getenv("MONGODB_ATLAS_CLUSTER_URI"))
        return cls._client


class AttendanceListItem(TwoLineListItem):
    screen_manager = ObjectProperty()

    def on_press(self):
        pass


class GenderListItem(OneLineListItem):
    gender_text_box = ObjectProperty()

    def on_release(self):
        self.gender_text_box.text = self.text


class AttendanceScreen(MDScreen):
    screen_manager = ObjectProperty()

    def on_pre_enter(self, *args):
        attendance_list = self.children[0].children[1].children[0]
        print(attendance_list)
        for i in range(100):
            attendance_list.add_widget(
                AttendanceListItem(
                    text="First Text " + str(i), secondary_text="Second Text " + str(i)
                )
            )


class AttendeesScreen(MDScreen):
    def on_pre_enter(self, *args):
        pass


class AttendanceUserSignUpPage(MDScreen):
    def on_pre_enter(self, *args):
        pass


class AttendanceSignInButton(MDRectangleFlatButton):

    def on_release(self):
        children = self.parent.children
        cred = dict()
        for child in children:
            if isinstance(child, MDTextField):
                cred[child.id] = child.text
        print(cred)


class AttendanceSignUpButton(MDRectangleFlatButton):

    def on_release(self):
        children = self.parent.children
        cred = dict()
        for child in children:
            if isinstance(child, MDTextField):
                cred[child.id] = child.text
        client = MongoDBInstance.get_client()
        db = client[os.getenv("MONGODB_NAME")]
        app_users_collection = db["app_users"]
        user_body = {
            "username": cred["username"],
            "gender": cred["gender"],
            "password": bcrypt.hashpw(cred["password"].encode("utf8"), bcrypt.gensalt())
        }
        app_users_collection.insert_one(user_body)



class GenderTextField(MDTextField):
    menu = ObjectProperty()

    def on_focus(self, instance_text_field, focus: bool) -> None:
        if self.focus:
            self.menu.open()


def build_attendance_screen(screen_manger):
    attendance_screen = AttendanceScreen()
    attendance_layout = MDBoxLayout(orientation="vertical", id="attendance_layout")
    attendance_top_app_bar = MDTopAppBar(title="Attendance Entries")
    attendance_scroll_view = MDScrollView()
    attendance_entries_list = MDList(id="attendance_entries_list")
    attendance_scroll_view.add_widget(attendance_entries_list)
    attendance_layout.add_widget(attendance_top_app_bar)
    attendance_layout.add_widget(attendance_scroll_view)
    attendance_action_button = MDFloatingActionButton(
        icon="plus", pos_hint={"center_x": 0.5}
    )
    attendance_layout.add_widget(attendance_action_button)
    attendance_screen.add_widget(attendance_layout)
    return attendance_screen


def build_sign_in_screen(screen_manager):
    sign_in_screen = MDScreen()
    sign_in_screen_top_app_bar = MDTopAppBar(title="Church App Signin")
    sign_in_screen_layout = MDBoxLayout(
        orientation="vertical", id="sign_in_screen_layout"
    )
    sign_in_text_layout = MDBoxLayout(
        orientation="vertical",
    )
    sign_in_user_name_input = MDTextField(
        id="username",
        hint_text="Username",
        helper_text="Your Username is your email essentially",
        helper_text_mode="on_focus",
    )
    sign_in_user_password = MDTextField(
        id="password",
        hint_text="Password",
        helper_text="If you don't have the password contact IT",
        helper_text_mode="on_focus",
        password=True,
    )
    sign_in_text_layout.add_widget(sign_in_user_name_input)
    sign_in_text_layout.add_widget(sign_in_user_password)
    sign_in_text_layout.add_widget(
        AttendanceSignInButton(text="Signin", size_hint=(1.0, None))
    )
    sign_in_screen_layout.add_widget(sign_in_screen_top_app_bar)
    sign_in_screen.add_widget(sign_in_screen_layout)
    sign_in_screen_layout.add_widget(sign_in_text_layout)

    return sign_in_screen

class AttendanceSignUpBottomNavigationItem(MDBottomNavigationItem):
    screen_manager = ObjectProperty()
    def on_tab_press(self, *args) -> None:
        self.screen_manager.current = self.name
        super().on_tab_press()


def build_admin_sign_up_page(screen_manager):
    sign_up_screen = MDScreen(name="sign_up_screen")
    sign_up_screen_top_app_bar = MDTopAppBar(title="Admin Church App Signup Users")
    sign_up_screen_layout = MDBoxLayout(
        orientation="vertical", id="sign_in_screen_layout"
    )
    sign_up_text_layout = MDBoxLayout(
        orientation="vertical", spacing=50, padding=[0, 0, 0, 100],
    )
    sign_up_user_name_input = MDTextField(
        id="username",
        hint_text="Username",
        helper_text="Your Username is your email essentially",
        helper_text_mode="on_focus",
    )
    sign_up_user_password = MDTextField(
        id="password",
        hint_text="Password",
        helper_text="Make the password",
        helper_text_mode="on_focus",
        password=True,
    )
    sign_up_confirm_user_password = MDTextField(
        id="confirm_password",
        hint_text="Confirm Password",
        helper_text="Enter " "Your " "Password Again",
        helper_text_mode="on_focus",
        password=True,
    )
    sign_up_gender = GenderTextField(id="gender", hint_text="Gender", helper_text="Enter The Gender",
                                     helper_text_mode="on_focus")
    menu_items = [{"text": "Male", "viewclass": "GenderListItem", "gender_text_box": sign_up_gender},
                  {"text": "Female", "viewclass": "GenderListItem", "gender_text_box": sign_up_gender}]
    sign_up_screen_bottom_navigation = MDBottomNavigation()
    sign_up_screen_bottom_navigation.add_widget(AttendanceSignUpBottomNavigationItem(name="sign_up_screen",text="Add Users",icon="account-multiple-plus",screen_manager=screen_manager))
    sign_up_screen_bottom_navigation.add_widget(AttendanceSignUpBottomNavigationItem(name="user_list_screen",text="Users",icon="account-box-multiple",screen_manager=screen_manager))
    sign_up_gender_menu = MDDropdownMenu(caller=sign_up_gender, items=menu_items, width_mult=4)
    sign_up_gender.menu = sign_up_gender_menu
    sign_up_text_layout.add_widget(sign_up_user_name_input)
    sign_up_text_layout.add_widget(sign_up_user_password)
    sign_up_text_layout.add_widget(sign_up_confirm_user_password)
    sign_up_text_layout.add_widget(sign_up_gender)
    sign_up_text_layout.add_widget(
        AttendanceSignUpButton(text="Add User", size_hint=(1.0, None))
    )
    sign_up_screen_layout.add_widget(sign_up_screen_top_app_bar)
    sign_up_screen.add_widget(sign_up_screen_bottom_navigation)
    sign_up_screen.add_widget(sign_up_screen_layout)
    sign_up_screen_layout.add_widget(sign_up_text_layout)

    return sign_up_screen


class ChurchAttendanceApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        sm = MDScreenManager()
        sm.add_widget(build_sign_in_screen(sm))
        sm.add_widget(build_attendance_screen(sm))
        return sm


class ChurchAttendanceAdminApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        sm = MDScreenManager()
        sm.add_widget(build_admin_sign_up_page(sm))
        sm.add_widget(MDScreen(name="user_list_screen"))
        return sm


app = None

if ADMIN_MODE:
    app = ChurchAttendanceAdminApp()
else:
    app = ChurchAttendanceApp()

app.run()
