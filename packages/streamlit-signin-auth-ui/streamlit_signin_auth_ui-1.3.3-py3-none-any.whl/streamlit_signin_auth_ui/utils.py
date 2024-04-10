import re
import secrets
from argon2 import PasswordHasher
import requests
import smtplib
import streamlit as st
import gspread
import pandas as pd
import warnings
from oauth2client.service_account import ServiceAccountCredentials

warnings.filterwarnings("ignore")


@st.cache_resource(show_spinner=False)
def worksheet(_credentials):

    scope = ["https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive"]
    Worksheet = ServiceAccountCredentials.from_json_keyfile_dict(_credentials, scope)
    client = gspread.authorize(Worksheet)
    sheet = client.open("mydb").sheet1
    return sheet


ph = PasswordHasher()

def check_usr_pass(credentials,username: str, password: str) -> bool:
    """
  Authenticates the username and password.
  """
    sheet = worksheet(credentials)
    users = pd.DataFrame(sheet.get_values(), columns=sheet.get_values()[0]).drop(index=0)
    users_name = users["username"]
    for name in users_name:
        if name == username:
            try:
                for pass_word in users[users['username'] == username]['password']:
                    if ph.verify(pass_word, password):
                        return True
            except:
                pass
    return False


def load_lottieurl(url: str) -> str:
    """
    Fetches the lottie animation using the URL.
    """
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        pass

def check_valid_email(email_sign_up: str) -> bool:
    """
    Checks if the user entered a valid email while creating the account.
    """
    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

    if re.fullmatch(regex, email_sign_up):
        return True
    return False


def check_unique_email(credentials,email_sign_up: str) -> bool:
  """
  Checks if the email already exists (since email needs to be unique).
  """
  sheet = worksheet (credentials)
  users = pd.DataFrame(sheet.get_values(), columns=sheet.get_values()[0]).drop(index=0)
  emails = users["email"]

  if email_sign_up in list(emails):
    return False
  return True


def non_empty_str_check(username_sign_up: str) -> bool:
    """
    Checks for non-empty strings.
    """
    empty_count = 0
    for i in username_sign_up:
        if i == ' ':
            empty_count = empty_count + 1
            if empty_count == len(username_sign_up):
                return False

    if not username_sign_up:
        return False
    return True


def check_unique_usr(credentials,username_sign_up: str):
    """
    Checks if the username already exists (since username needs to be unique),
    also checks for non - empty username.
    """
    sheet = worksheet(credentials)
    if sheet.find(username_sign_up):
        return False

    non_empty_check = non_empty_str_check(username_sign_up)

    if non_empty_check == False:
        return None
    return True


def register_new_usr(credentials,email_sign_up: str, username_sign_up: str, password_sign_up: str) -> None:
    """
    Saves the information of the new user in the database (worksheet).
    """
    sheet = worksheet(credentials)
    new_usr_data = [username_sign_up,email_sign_up,ph.hash(password_sign_up)]
    sheet.append_row(new_usr_data)


def check_username_exists(credentials,user_name: str) -> bool:
    """
    Checks if the username exists in the database (worksheet).
    """
    sheet = worksheet(credentials)
    users = list(pd.DataFrame(sheet.get_values(), columns=sheet.get_values()[0]).drop(index=0))
    if user_name in users:
        return True
    return False


def check_email_exists(credentials,email_forgot_passwd: str):
    """
    Checks if the email entered is present in the database.
    """
    sheet = worksheet(credentials)
    if sheet.find(email_forgot_passwd):
        return True, sheet.find(email_forgot_passwd).value
    return False, None

def generate_random_passwd() -> str:
    """
    Generates a random password to be sent in email.
    """
    password_length = 10
    return secrets.token_urlsafe(password_length)


def send_pass_in_mail( smtp_username:str, smtp_password:str,username_forgot_passwd: str, email_forgot_passwd: str, company_name: str,
                         random_password: str) -> None:
    """ Send a temporary password in the email using SMTP """
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    #'uwbg fjbl brwg gdwv'

    to_email = email_forgot_passwd
    mail = f"Salut! {username_forgot_passwd}, \n \n Votre mot de passe temporaire est: {random_password} \n \n"
    info = "S'il vous plait renouvelez votre mot de passe le plus vite pour des raisons de protection."
    body = f'Email from : Moudakira.ma  \n {mail}.'
    subject = f"{company_name}: Un nouveau mot de passe"
    message = f'Subject: {subject}\n\n{body}\n\n{info}'

    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        smtp.sendmail(smtp_username, to_email, message)



def change_passwd(credentials,email_: str, random_password: str) -> None:
  """
  Replaces the old password with the newly generated password.
  """
  sheet = worksheet(credentials)
  if sheet.find(email_):
      email_row = sheet.find(email_).row
      email_col = sheet.find(email_).col
      sheet.update_cell(row=email_row,col=email_col+1,value=ph.hash(random_password))

def check_current_passwd(credentials,email_reset_passwd: str, current_passwd: str) -> bool:
  """
  Authenticates the password entered against the username when
  resetting the password.
  """
  sheet = worksheet(credentials)
  email = sheet.find(email_reset_passwd)
  if email:
      users = pd.DataFrame(sheet.get_values(), columns=sheet.get_values()[0]).drop(index=0)
      password = list(users[users["email"]==email.value]["password"])[0]
      try:
        if ph.verify(password, current_passwd):
          return True
      except:
        pass
  return False
