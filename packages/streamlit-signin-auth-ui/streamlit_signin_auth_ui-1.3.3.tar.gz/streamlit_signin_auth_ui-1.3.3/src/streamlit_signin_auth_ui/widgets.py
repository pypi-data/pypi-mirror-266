import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
from streamlit_cookies_manager import EncryptedCookieManager
from .utils import check_usr_pass
from .utils import load_lottieurl
from .utils import check_valid_email
from .utils import check_unique_email
from .utils import check_unique_usr
from .utils import register_new_usr
from .utils import check_email_exists
from .utils import generate_random_passwd
from .utils import send_pass_in_mail
from .utils import change_passwd
from .utils import check_current_passwd


class __login__:
    """
    Builds the UI for the Login/ Sign Up page.
    """

    def __init__(self, credentials : dict,smtp_username:str, smtp_password:str, company_name: str, width, height, logout_button_name: str = 'Quitter',
                 hide_menu_bool: bool = False, hide_footer_bool: bool = False,
                 lottie_url: str = "https://assets8.lottiefiles.com/packages/lf20_ktwnwv5m.json"):
        """
        Arguments:
        -----------
        1. self
        2. credentials : The credentials to connect with Google Sheet API
        3. smtp_username : username to login to your SMTP Gmail account
        4. smtp_password : password to login to your SMTP Gmail account
        5. company_name : This is the name of the person/ organization which will send the password reset email.
        6. width : Width of the animation on the login page.
        7. height : Height of the animation on the login page.
        8. logout_button_name : The logout button name.
        9. hide_menu_bool : Pass True if the streamlit menu should be hidden.
        10. hide_footer_bool : Pass True if the 'made with streamlit' footer should be hidden.
        11. lottie_url : The lottie animation you would like to use on the login page. Explore animations at - https://lottiefiles.com/featured
        """
        self.credentials = credentials
        self.company_name = company_name
        self.width = width
        self.height = height
        self.logout_button_name = logout_button_name
        self.hide_menu_bool = hide_menu_bool
        self.hide_footer_bool = hide_footer_bool
        self.lottie_url = lottie_url
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.cookies = EncryptedCookieManager(
            prefix="streamlit_login_ui_yummy_cookies",
            password='9d68d6f2-4258-45c9-96eb-2d6bc74ddbb5-d8f49cab-edbb-404a-94d0-b25b1d4a564b')

        if not self.cookies.ready():
            st.stop()

    def get_username(self):
        if st.session_state['LOGOUT_BUTTON_HIT'] == False:
            fetched_cookies = self.cookies
            if '__streamlit_login_signup_ui_username__' in fetched_cookies.keys():
                username = fetched_cookies['__streamlit_login_signup_ui_username__']
                return username

    def login_widget(self) -> None:
        """
        Creates the login widget, checks and sets cookies, authenticates the users.
        """

        # Checks if cookie exists.
        if st.session_state['LOGGED_IN'] == False:
            if st.session_state['LOGOUT_BUTTON_HIT'] == False:
                fetched_cookies = self.cookies
                if '__streamlit_login_signup_ui_username__' in fetched_cookies.keys():
                    if fetched_cookies[
                        '__streamlit_login_signup_ui_username__'] != '1c9a923f-fb21-4a91-b3f3-5f18e3f01182':
                        st.session_state['LOGGED_IN'] = True

        if st.session_state['LOGGED_IN'] == False:
            st.session_state['LOGOUT_BUTTON_HIT'] = False

            del_login = st.empty()
            with del_login.form("Login Form"):
                username = st.text_input("Nom d'utilisateur", placeholder="Votre nom d'utilisateur unique")
                password = st.text_input("Mot de passe", placeholder='Votre mot de passe', type='password')

                st.markdown("###")
                login_submit_button = st.form_submit_button(label='Enregistrer')

                if login_submit_button == True:
                    authenticate_user_check = check_usr_pass(self.credentials,username, password)

                    if authenticate_user_check == False:
                        st.error("Le mot de passe ou le nom d'utilisateur sont invalides!")

                    else:
                        st.session_state['LOGGED_IN'] = True
                        self.cookies['__streamlit_login_signup_ui_username__'] = username
                        self.cookies['username'] = username
                        st.markdown(f"### Welcome {username}!")
                        self.cookies.save()
                        del_login.empty()
                        st.rerun()

    def animation(self) -> None:
        """
        Renders the lottie animation.
        """
        lottie_json = load_lottieurl(self.lottie_url)
        st_lottie(lottie_json, width=self.width, height=self.height)

    def sign_up_widget(self) -> None:
        """
        Creates the sign-up widget and stores the user info in a secure way in the database.
        """
        form = st.form(key="form001")
        # name_sign_up = st.text_input("Name *", placeholder = 'Please enter your name')
        # valid_name_check = check_valid_name(name_sign_up)

        username_sign_up = form.text_input("Nom d'utilisateur *", placeholder="votre nom d'utilisateur unique",key="username111")
        email_sign_up = form.text_input("Email *", placeholder='entrez votre email',key="email111")



        password_sign_up = form.text_input("Mot de passe *", placeholder='Créez un mot de passe fort',
                                           type='password',key="password123")


        #form.markdown("###")

        if form.form_submit_button(label='Enregister'):
            # if valid_name_check == False:
            #     st.error("Please enter a valid name!")
            unique_username_check = check_unique_usr(self.credentials,username_sign_up)
            valid_email_check = check_valid_email(email_sign_up)
            unique_email_check = check_unique_email(self.credentials,email_sign_up)

            if valid_email_check == False:
                form.error("S'il vous plait entrez un email valide!")

            elif unique_email_check == False:
                form.error("Email déjà existe!")

            elif unique_username_check == False:
                form.error(f"Désolé, nom d'utilisateur {username_sign_up} déjà existe!")

            elif unique_username_check == None:
                form.error("S'il vous plait entrez un nom d'utilisateur unique!")

            if valid_email_check == True:
                if unique_email_check == True:
                    if unique_username_check == True:
                        register_new_usr(self.credentials,email_sign_up, username_sign_up, password_sign_up)
                        form.success("Vous vous avez enregistré avec succès !")

    def forgot_password(self) -> None:
        """
        Creates the forgot password widget and after user authentication (email), triggers an email to the user
        containing a random password.
        """
        with st.form(key="form0002"):
            email_forgot_passwd = st.text_input("Email", placeholder='entrez votre email')
            email_exists_check, username_forgot_passwd = check_email_exists(self.credentials,email_forgot_passwd)

            st.markdown("###")
            forgot_passwd_submit_button = st.form_submit_button(label='Recuperez votre mot de passe')

            if forgot_passwd_submit_button:
                if email_exists_check == False:
                    st.error("On ne peut pas identifier votre email!")

                if email_exists_check == True:
                    random_password = generate_random_passwd()
                    send_pass_in_mail(self.smtp_username,self.smtp_password,username_forgot_passwd, email_forgot_passwd,
                                         self.company_name, random_password)
                    change_passwd(self.credentials,email_forgot_passwd, random_password)
                    st.success("Un mot de passe a ètait envoyer avec succés à votre email!")

    def reset_password(self) -> None:
        """
        Creates the reset password widget and after user authentication (email and the password shared over that email),
        resets the password and updates the same in the Google sheet file (database).
        """
        with st.form(key="form0003"):
            email_reset_passwd = st.text_input("Email",value='example@gmail.com', placeholder='Entrez votre email')
            email_exists_check, username_reset_passwd = check_email_exists(self.credentials,email_reset_passwd)

            current_passwd = st.text_input("Mot de passe temporaire",
                                           placeholder='Svp entrez le mot de passe que vous avez reçu par email!')
            current_passwd_check = check_current_passwd(self.credentials,email_reset_passwd, current_passwd)

            new_passwd = st.text_input("Nouveau mot de passe", placeholder='Svp entrez un mot de passe nouveau et fort!',
                                       type='password')

            new_passwd_1 = st.text_input("Rentrez un nouveau mot de passe", placeholder='Svp rentrez le nouveau mot de passe!',
                                         type='password')

            st.markdown("###")
            reset_passwd_submit_button = st.form_submit_button(label='Recuperation de mot de passe')

            if reset_passwd_submit_button:
                if email_exists_check == False:
                    st.error("Cette email n'éxiste pas!")

                elif current_passwd_check == False:
                    st.error("Mot de passe temporaire incorrect!")

                elif new_passwd != new_passwd_1:
                    st.error("Mots de passe incompatible!")

                if email_exists_check == True:
                    if current_passwd_check == True:
                        change_passwd(self.credentials,email_reset_passwd, new_passwd)
                        st.success("Vous avez renouvelé votre mot de passe avec succés!")

    def logout_widget(self) -> None:
        """
        Creates the logout widget in the sidebar only if the user is logged in.
        """
        if st.session_state['LOGGED_IN'] == True:
            del_logout = st.sidebar.empty()
            del_logout.markdown("#")
            logout_click_check = del_logout.button(self.logout_button_name)

            if logout_click_check == True:
                st.session_state['LOGOUT_BUTTON_HIT'] = True
                st.session_state['LOGGED_IN'] = False
                self.cookies['__streamlit_login_signup_ui_username__'] = '1c9a923f-fb21-4a91-b3f3-5f18e3f01182'
                del_logout.empty()
                st.rerun()
                #st.cache_resource.clear()

    def nav_sidebar(self):
        """
        Creates the side navigaton bar
        """
        main_page_sidebar = st.sidebar.empty()
        with main_page_sidebar:
            selected_option = option_menu(
                menu_title='Navigation',
                menu_icon='list-columns-reverse',
                icons=['box-arrow-in-right', 'person-plus', 'x-circle', 'arrow-counterclockwise'],
                options=['Se connecté', 'Créer un compte', 'Mot de passe oublier?', 'Réinitialiser le mot de passe'],
                styles={
                    "container": {"padding": "5px"},
                    "nav-link": {"font-size": "14px", "text-align": "left", "margin": "0px"}})
        return main_page_sidebar, selected_option

    def hide_menu(self) -> None:
        """
        Hides the streamlit menu situated in the top right.
        """
        st.markdown(""" <style>
        #MainMenu {visibility: hidden;}
        </style> """, unsafe_allow_html=True)

    def hide_footer(self) -> None:
        """
        Hides the 'made with streamlit' footer.
        """
        st.markdown(""" <style>
        footer {visibility: hidden;}
        </style> """, unsafe_allow_html=True)

    def build_login_ui(self):
        """
        Brings everything together, calls important functions.
        """
        if 'LOGGED_IN' not in st.session_state:
            st.session_state['LOGGED_IN'] = False

        if 'LOGOUT_BUTTON_HIT' not in st.session_state:
            st.session_state['LOGOUT_BUTTON_HIT'] = False


        main_page_sidebar, selected_option = self.nav_sidebar()

        if selected_option == 'Se connecté':
            c1, c2 = st.columns([7, 3])
            with c1:
                self.login_widget()
            with c2:
                if st.session_state['LOGGED_IN'] == False:
                    self.animation()

        if selected_option == 'Créer un compte':
            self.sign_up_widget()

        if selected_option == 'Mot de passe oublier?':
            self.forgot_password()

        if selected_option == 'Réinitialiser le mot de passe':
            self.reset_password()

        self.logout_widget()

        if st.session_state['LOGGED_IN'] == True:
            main_page_sidebar.empty()

        if self.hide_menu_bool == True:
            self.hide_menu()

        if self.hide_footer_bool == True:
            self.hide_footer()

        return st.session_state['LOGGED_IN']

