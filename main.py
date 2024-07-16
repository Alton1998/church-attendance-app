import datetime
import logging
import os

import bcrypt
from dotenv import load_dotenv
from kivy.properties import ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import (
    MDFloatingActionButton,
    MDRectangleFlatButton,
    MDFlatButton,
)
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, OneLineListItem, ThreeLineListItem, TwoLineListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from pymongo import MongoClient

load_dotenv()
logging.basicConfig(
    format="%(levelname)s - %(asctime)s: %(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
    filename="app.log",
)
ADMIN_MODE = True if os.getenv("ADMIN_MODE") == "TRUE" else False


# church F7hTLbKj2fbjljrz

# mongodb+srv://church:F7hTLbKj2fbjljrz@cluster0.dwo9y43.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0

current_user = None


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
        try:
            client = MongoDBInstance.get_client()
            db = client[os.getenv("MONGODB_NAME")]
            attendance_collection = db["attendance_entries"]
            attendance_entries = attendance_collection.find()
            for attendance in attendance_entries:
                attendance_list.add_widget(
                    AttendanceListItem(
                        text=attendance["attendance_name"],
                        secondary_text=attendance["attendance_description"],
                    )
                )
        except Exception as e:
            error_dialog = Snackbar(text="Internal Error")
            error_dialog.open()
            logging.error(e)

    def on_leave(self, *args):
        attendance_list = self.children[0].children[1].children[0]
        attendance_list.clear_widgets()


class AttendeesScreen(MDScreen):
    def on_pre_enter(self, *args):
        pass


class AttendanceUserSignUpPage(MDScreen):
    def on_pre_enter(self, *args):
        pass


class AttendanceSignInButton(MDRectangleFlatButton):
    screen_manager = ObjectProperty()

    def on_release(self):
        children = self.parent.children
        cred = dict()
        for child in children:
            if not child.text:
                error_dialog = Snackbar(text="Enter all Fields")
                error_dialog.open()
                return
            if isinstance(child, MDTextField):
                cred[child.id] = child.text
        try:
            client = MongoDBInstance.get_client()
            db = client[os.getenv("MONGODB_NAME")]
            app_users_collection = db["app_users"]
            user = app_users_collection.find_one({"username": cred["username"]})
            if not user:
                error_dialog = Snackbar(text="No such user")
                error_dialog.open()
            elif bcrypt.checkpw(cred["password"].encode("utf8"), user["password"]):
                self.screen_manager.current = "attendance_screen"
                global current_user
                current_user = user["name"]
                print(current_user)
            else:
                error_dialog = Snackbar(text="Incorrect Credentials")
                error_dialog.open()
        except Exception as e:
            error_dialog = Snackbar(text="Internal Error")
            error_dialog.open()
            logging.error(e)


class AttendanceSignUpButton(MDRectangleFlatButton):

    def on_release(self):
        children = self.parent.children
        cred = dict()
        for child in children:
            if isinstance(child, MDTextField):
                cred[child.id] = child.text
        if (
            not cred["username"]
            or not cred["name"]
            or not cred["gender"]
            or not cred["password"]
            or not cred["password"] == cred["confirm_password"]
        ):
            error_dialog = Snackbar(
                text="Error!!! Ensure you have entered all fields and the passwords match"
            )
            error_dialog.open()
            return
        try:
            client = MongoDBInstance.get_client()
            db = client[os.getenv("MONGODB_NAME")]
            app_users_collection = db["app_users"]
            user_body = {
                "name": cred["name"],
                "username": cred["username"],
                "gender": cred["gender"],
                "password": bcrypt.hashpw(
                    cred["password"].encode("utf8"), bcrypt.gensalt()
                ),
                "status": "ACTIVE",
            }
            count = app_users_collection.count_documents({"username": cred["username"]})
            if count > 0:
                error_dialog = Snackbar(
                    text="User with the same username already exists"
                )
                error_dialog.open()
                return
            app_users_collection.insert_one(user_body)
            success_dialog = Snackbar(text="Successfully Added User")
            success_dialog.open()
        except Exception as e:
            error_dialog = Snackbar(text="Internal Error")
            error_dialog.open()
            logging.error(e)


class GenderTextField(MDTextField):
    menu = ObjectProperty()

    def on_focus(self, instance_text_field, focus: bool) -> None:
        if self.focus:
            self.menu.open()


class AttendanceSessionEntrySubmitButton(MDFlatButton):
    attendance_name_text_field = ObjectProperty()
    attendance_description_text = ObjectProperty()
    attendance_list = ObjectProperty()

    def on_release(self):
        if not self.attendance_name_text_field.text:
            error_dialog = Snackbar(text="All entries must be entered")
            error_dialog.open()
            return
        attendance_body = {
            "attendance_name": self.attendance_name_text_field.text,
            "attendance_description": self.attendance_description_text.text,
            "created_by": current_user,
            "created_on": datetime.datetime.now(datetime.timezone.utc),
            "attendees": [],
        }
        try:
            client = MongoDBInstance.get_client()
            db = client[os.getenv("MONGODB_NAME")]
            attendance_entries_collection = db["attendance_entries"]
            attendance_entries_collection.insert_one(attendance_body)
            self.attendance_list.add_widget(
                AttendanceListItem(
                    text=attendance_body["attendance_name"],
                    secondary_text=attendance_body["attendance_description"],
                )
            )
        except Exception as e:
            error_dialog = Snackbar(text="Internal Error")
            error_dialog.open()
            logging.error(e)


class AddAttendanceEntryFabButton(MDFloatingActionButton):
    attendance_list = ObjectProperty()

    def on_release(self):
        attendance_dialog_layout = MDBoxLayout(
            orientation="vertical", spacing="12dp", size_hint_y=None, height="120dp"
        )
        attendance_dialog_name = MDTextField(
            id="attendance_session_name",
            hint_text="Attendance Session Name",
            helper_text="Enter the Attendance Session Name",
            helper_text_mode="on_focus",
        )
        attendance_dialog_description = MDTextField(
            id="attendance_description",
            hint_text="Attendance Description",
            helper_text="Enter the Attendance Description",
            helper_text_mode="on_focus",
        )
        attendance_dialog_layout.add_widget(attendance_dialog_name)
        attendance_dialog_layout.add_widget(attendance_dialog_description)
        add_attendance_dialog = MDDialog(
            title="Attendance entry",
            type="custom",
            content_cls=attendance_dialog_layout,
            buttons=[
                AttendanceSessionEntrySubmitButton(
                    text="Submit",
                    attendance_name_text_field=attendance_dialog_name,
                    attendance_list=self.attendance_list,
                    attendance_description_text=attendance_dialog_description,
                )
            ],
        )
        add_attendance_dialog.open()


def build_attendance_screen(screen_manger):
    attendance_screen = AttendanceScreen(name="attendance_screen")
    attendance_layout = MDBoxLayout(orientation="vertical", id="attendance_layout")
    attendance_top_app_bar = MDTopAppBar(title="Attendance Entries")
    attendance_scroll_view = MDScrollView()
    attendance_entries_list = MDList(id="attendance_entries_list")
    attendance_scroll_view.add_widget(attendance_entries_list)
    attendance_layout.add_widget(attendance_top_app_bar)
    attendance_layout.add_widget(attendance_scroll_view)
    attendance_action_button = AddAttendanceEntryFabButton(
        icon="plus",
        pos_hint={"center_x": 0.5},
        attendance_list=attendance_entries_list,
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
        orientation="vertical", padding=[30, 0, 30, 300], spacing=50
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
        AttendanceSignInButton(
            text="Signin", size_hint=(1.0, None), screen_manager=screen_manager
        )
    )
    sign_in_screen_layout.add_widget(sign_in_screen_top_app_bar)
    sign_in_screen.add_widget(sign_in_screen_layout)
    sign_in_screen_layout.add_widget(sign_in_text_layout)

    return sign_in_screen


class AttendanceSignUpBottomNavigationItem(MDBottomNavigationItem):
    screen_manager = ObjectProperty()

    def on_tab_press(self, *args) -> None:
        self.screen_manager.transition.direction = "left"
        self.screen_manager.current = self.name
        super().on_tab_press()


def build_admin_sign_up_page(screen_manager):
    sign_up_screen = MDScreen(name="sign_up_screen")
    sign_up_screen_top_app_bar = MDTopAppBar(title="Admin Church App Signup Users")
    sign_up_screen_layout = MDBoxLayout(
        orientation="vertical", id="sign_in_screen_layout"
    )
    sign_up_text_scroll_view = MDScrollView()
    sign_up_text_layout = MDList(spacing=20)
    sign_up_text_scroll_view.add_widget(sign_up_text_layout)
    sign_up_user_name = MDTextField(
        id="name",
        hint_text="Name",
        helper_text="Users Name",
        helper_text_mode="on_focus",
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
        helper_text="Make the password Strong",
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
    sign_up_gender = GenderTextField(
        id="gender",
        hint_text="Gender",
        helper_text="Enter The Gender",
        helper_text_mode="on_focus",
    )
    menu_items = [
        {
            "text": "Male",
            "viewclass": "GenderListItem",
            "gender_text_box": sign_up_gender,
        },
        {
            "text": "Female",
            "viewclass": "GenderListItem",
            "gender_text_box": sign_up_gender,
        },
    ]
    sign_up_screen_bottom_navigation = MDBottomNavigation(size_hint=(1.0, 0.2))
    sign_up_screen_bottom_navigation.add_widget(
        AttendanceSignUpBottomNavigationItem(
            name="sign_up_screen",
            text="Add Users",
            icon="account-multiple-plus",
            screen_manager=screen_manager,
        )
    )
    sign_up_screen_bottom_navigation.add_widget(
        AttendanceSignUpBottomNavigationItem(
            name="user_list_screen",
            text="Users",
            icon="account-box-multiple",
            screen_manager=screen_manager,
        )
    )
    sign_up_gender_menu = MDDropdownMenu(
        caller=sign_up_gender, items=menu_items, width_mult=4
    )
    sign_up_gender.menu = sign_up_gender_menu
    sign_up_text_layout.add_widget(sign_up_user_name)
    sign_up_text_layout.add_widget(sign_up_user_name_input)
    sign_up_text_layout.add_widget(sign_up_user_password)
    sign_up_text_layout.add_widget(sign_up_confirm_user_password)
    sign_up_text_layout.add_widget(sign_up_gender)
    sign_up_text_layout.add_widget(
        AttendanceSignUpButton(text="Add User", size_hint=(1.0, None))
    )
    sign_up_screen_layout.add_widget(sign_up_screen_top_app_bar)
    sign_up_screen.add_widget(sign_up_screen_layout)
    sign_up_screen_layout.add_widget(sign_up_text_scroll_view)
    sign_up_screen_layout.add_widget(sign_up_screen_bottom_navigation)

    return sign_up_screen


class ChurchAttendanceApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        sm = MDScreenManager()
        sm.add_widget(build_sign_in_screen(sm))
        sm.add_widget(build_attendance_screen(sm))
        return sm


class UsersListItem(ThreeLineListItem):
    pass


class UsersListScreen(MDScreen):
    screen_manager = ObjectProperty()

    def on_pre_enter(self, *args):
        try:
            client = MongoDBInstance.get_client()
            db = client[os.getenv("MONGODB_NAME")]
            app_users_collection = db["app_users"]
            users = app_users_collection.find()
            scroll_view = None
            for child in self.children[0].children:
                if isinstance(child, MDScrollView):
                    scroll_view = child
            users_list = scroll_view.children[0]
            for user in users:
                users_list.add_widget(
                    UsersListItem(
                        text=user["name"],
                        secondary_text=user["username"],
                        tertiary_text=user["status"],
                    )
                )
        except Exception as e:
            error_dialog = Snackbar(text="Internal Error")
            error_dialog.open()
            logging.error(e)

    def on_leave(self, *args):
        scroll_view = None
        for child in self.children[0].children:
            if isinstance(child, MDScrollView):
                scroll_view = child
        users_list = scroll_view.children[0]
        users_list.children = []


class UsersListTopAppBar(MDTopAppBar):
    screen_manager = ObjectProperty()


def back_navigation(obj):
    sm = obj.parent.parent.parent.screen_manager
    sm.transition.direction = "right"
    sm.current = "sign_up_screen"


def build_admin_users_list_page(sm):
    users_list_screen = UsersListScreen(name="user_list_screen", screen_manager=sm)
    users_list_screen_layout = MDBoxLayout(orientation="vertical")
    users_list_screen_top_app_bar = UsersListTopAppBar(
        title="Users List",
        left_action_items=[["arrow-left", back_navigation]],
        screen_manager=sm,
    )
    users_list_screen_layout.add_widget(users_list_screen_top_app_bar)
    users_list_screen_scroll_view = MDScrollView()
    users_list_screen_layout.add_widget(users_list_screen_scroll_view)
    users_list = MDList()
    users_list_screen_scroll_view.add_widget(users_list)
    users_list_screen.add_widget(users_list_screen_layout)
    return users_list_screen


class ChurchAttendanceAdminApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        sm = MDScreenManager()
        sm.add_widget(build_admin_sign_up_page(sm))
        sm.add_widget(build_admin_users_list_page(sm))
        return sm


app = None

if ADMIN_MODE:
    app = ChurchAttendanceAdminApp()
else:
    app = ChurchAttendanceApp()

app.run()
