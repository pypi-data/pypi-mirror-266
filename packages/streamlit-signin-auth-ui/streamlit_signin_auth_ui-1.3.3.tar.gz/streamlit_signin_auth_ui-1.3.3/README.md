# Login page with Streamlit (Lables of widgets are in Frensh language)

# Update of https://github.com/GitSamad88



#Version 2024-3-29 : this version is an update of streamlit-login-auth-ui-23

- streamlit 3.31.1
- trimmed requirements.txt
- removed name from user
- attempt to fix cache deprecated in imported module streamlit-cookies-manager==0.2.0 latest Version!
- store user's authentifications in a Google Sheets file as a database.
- connect with the user using STMP Gmail.


HOW TO INSTALL ALL LIBRARIES:?
python3.10 -m venv venv
source venv/bin/activate
python3.10 -m pip install -r requirements.txt

# Streamlit Login/ Sign Up Library   [![Downloads](https://static.pepy.tech/personalized-badge/streamlit-signin-auth-ui?period=month&units=international_system&left_color=grey&right_color=blue&left_text=downloads)](https://pepy.tech/project/streamlit-signin-auth-ui)

The streamlit_signin_auth_ui library is meant for streamlit application developers.
It lets you connect your streamlit application to a pre-built and secure Login/ Sign-Up page and store user's data in Google Sheets.

You can customize specific parts of the page without any hassle!

The library grants users an option to reset their password, users can click on ```Forgot Password?``` after which an Email is triggered containing a temporary, randomly generated password.

The library also sets encrypted cookies to remember and automatically authenticate the users without password. \
The users can logout using the ```Sortir``` button.


## Authors
- [@GitSamad88](https://github.com/GitSamad88)

## PyPi
https://pypi.org/project/streamlit_signin_auth_ui/

## The UI:
<img width="920" alt="connect" src="https://github.com/GitSamad88/streamlit-signin-ui/assets/110288424/bede11d3-e1f2-4021-991f-cf1be77eac50">


```python
pip install streamlit_signin_auth_ui
```

## How to implement the library?

To import the library, just paste this at the starting of the code:
```python
from streamlit_signin_auth_ui.widgets import __login__
```

All you need to do is create an object for the ```__login__``` class and pass the following parameters:

1. self
2. credentials : The credentials to connect with Google Sheets API.
    you have to enable Google Sheets API and create credentials, visit : [Google Cloud Console](https://console.cloud.google.com/)
4. smtp_username : username to login to your SMTP Gmail account
5. smtp_password : password to login to your SMTP Gmail account
6. company_name : This is the name of the person/ organization which will send the password reset email.
7. width : Width of the animation on the login page.
8. height : Height of the animation on the login page.
9. logout_button_name : The logout button name.
10. hide_menu_bool : Pass True if the streamlit menu should be hidden.
11. hide_footer_bool : Pass True if the 'made with streamlit' footer should be hidden.
12. lottie_url : The lottie animation you would like to use on the login page. Explore animations
        
#### Mandatory Arguments:
* ```company_name```
* ```width```
* ```height```

#### Non Mandatory Arguments:
* ```logout_button_name```     [default = 'Sortir']
* ```hide_menu_bool```         [default = False]
* ```hide_footer_bool```       [default = False]
* ```lottie_url```             [default = https://assets8.lottiefiles.com/packages/lf20_ktwnwv5m.json]

After doing that, just call the ```build_login_ui()``` function using the object you just created and store the return value in a variable.

# Example:
```python
import streamlit as st
from streamlit_signin_auth_ui.widgets import __login__

__login__obj = __login__(credentials=credentials_of_your_google_sheet_API, # must be .json or Python dictionnary.
                    smtp_username = 'your_email@gmail.com',
                    smtp_password = 'your password', # 16 caracters
                    company_name = "your_company_name", # mandatory
                    width = 400, height = 500,
                    logout_button_name = 'Sortir', hide_menu_bool = False,
                    hide_footer_bool = False,
                    lottie_url = 'https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json')



LOGGED_IN = __login__obj.build_login_ui()

if LOGGED_IN == True:
    st.success("Bienvenue!")
```

That's it! The library handles the rest. \
Just make sure you call/ build your application indented under ```if st.session_state['LOGGED_IN'] == True:```, this guarantees that your application runs only after the user is securely logged in. 

## Explanation

### Login page
The login page, authenticates the user.

<img width="920" alt="connect" src="https://github.com/GitSamad88/streamlit-signin-ui/assets/110288424/c8bf1342-4003-4c5f-92d6-0001dd20a8fb">

### Create Account page
Stores the user info in a secure way in the ```google-sheet``` file. as a database \

<img width="925" alt="creat-account" src="https://github.com/GitSamad88/streamlit-signin-ui/assets/110288424/0581fd1f-6fb1-4e62-ab54-4735ecee7dd7">


### Forgot Password page
After user authentication (email), triggers an email to the user containing a random password. \

<img width="919" alt="get-password" src="https://github.com/GitSamad88/streamlit-signin-ui/assets/110288424/a6abe750-f5d6-479d-ae29-c338f90455fb">


### Reset Password page
After user authentication (email and the password shared over email), resets the password and updates the same \
in the ```google-sheet``` file. \

<img width="919" alt="edit-password" src="https://github.com/GitSamad88/streamlit-signin-ui/assets/110288424/740d843d-c5c3-4c23-844e-5a14db926103">


### Logout button
Generated in the sidebar only if the user is logged in, allows users to logout. \

<img width="919" alt="loggin" src="https://github.com/GitSamad88/streamlit-signin-ui/assets/110288424/034ff583-0e81-437a-a5ae-33ca7e6f521f">

__Cookies are automatically created and destroyed depending on the user authentication status.__

## Version
v1.3.3

## License
[MIT](https://github.com/GitSamad88/streamlit_signin_ui/blob/main/LICENSE)