"""
Programing and algorithms 2 Assignment
Student: Ionut Petrescu
ID: D19124760
Course: DT249
Stage 2

TKinter gui for our API blogging app.

Signup by filling the signup form.
Log in using first_name.last_name@tudublin.ie and the password you selected
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import font as tkFont
import requests
import json
SERVER = 'http://127.0.0.1:8000/'

class RichText(tk.Text):
    """
    Creating custom class to aid in formatting of blog posts
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        default_font = tkFont.nametofont(self.cget("font"))

        em = default_font.measure("m")
        default_size = default_font.cget("size")
        bold_font = tkFont.Font(**default_font.configure())
        italic_font = tkFont.Font(**default_font.configure())
        h1_font = tkFont.Font(**default_font.configure())

        bold_font.configure(weight="bold")
        italic_font.configure(slant="italic")
        h1_font.configure(size=int(default_size*1.5), weight="bold")

        self.tag_configure("bold", font=bold_font)
        self.tag_configure("italic", font=italic_font)
        self.tag_configure("h1", font=h1_font, spacing3=default_size)

        lmargin2 = em + default_font.measure("\u2022 ")
        self.tag_configure("bullet", lmargin1=em, lmargin2=lmargin2)

    def insert_bullet(self, index, text):
        self.insert(index, f"\u2022 {text}", "bullet")

    def from_list(self, lst):
        self.config(state="normal")
        self.delete('1.0', tk.END)
        for item in lst:
            datet = item['created'].split("T")
            date = datet[0]
            time = datet[1][0:8]
            self.insert("end", f"{item['title']}\n", "h1")
            self.insert("end", item["content"]+"\n", "bold")
            self.insert("end", f"{item['category']} (#{item['tag']}) - Posted by {item['author']} "
                               f"on {date} at {time}\n", "italic")
            self.insert("end", '-'*60 + "\n", "bold")
        self.config(state="disabled")
        self.see(tk.END)

class MyGUI(tk.Tk):
    """
    All of the GUI stuff lives here
    """

    def __init__(self, gui_settings):
        """
        All of the GUI 'look' lives here.
        """
        super().__init__()
        self.session = None
        self.token = None

        # Configure basic window options
        for k, v in gui_settings.items():
            setattr(self, k, v)
        self.title(self.title_text)
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(self.resizable_width, self.resizable_height)

        # Make protocol handler to manage interaction between the application and the window handler
        self.protocol("WM_DELETE_WINDOW", self.catch_destroy)

        self.padding = {
            'padx': 5,
            'pady': 5,
            'ipadx': 5,
            'ipady': 5,
        }

        # ============    Menu Bar    ===================
        self.menubar = tk.Menu(self)
        self.menu = tk.Menu(self.menubar, tearoff=False)
        self.menu.add_command(label="Log in", command=self.log_in_page)
        self.menu.add_command(label="Sign up", command=self.sign_up_page)
        self.menu.add_command(label="Sign out", command=self.act_signout, state="disabled")
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=self.catch_destroy)
        self.menu_admin = tk.Menu(self.menubar, tearoff=False)
        self.menu_admin.add_command(label="Create new category", command=self.act_admin_create, state="disabled")
        self.menu_admin.add_command(label="Delete a category", command=self.act_admin_delete, state="disabled")
        self.menu_admin.add_command(label="Modify a category", command=self.act_admin_modify, state="disabled")
        self.menubar.add_cascade(label="Menu", menu=self.menu)
        self.menubar.add_cascade(label="Admin", menu=self.menu_admin)
        self.menubar.add_command(label="About",
                                command=lambda: self.show_info(title="Help text", message=f"{__doc__}"))
        # self.menubar.add_command(label="About",command=self.act_admin_modify)
        self.config(menu=self.menubar)

        # ==========   Main Frame ========================
        self.frame_main = ttk.Frame(
            self,
            width=self.width,
            height=self.height - ((self.padding["pady"] * 2) + (self.padding["ipady"] * 2))
        )
        self.frame_main.grid(row=0, column=0)
        self.lbl_posts = tk.Label(self.frame_main, text="Posts")
        self.lbl_posts.grid(row=0, column=0, **self.padding)
        self.txt_posts = RichText(self.frame_main, height=25, width=70)
        self.txt_posts.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, ipadx=0)
        self.scrollb = ttk.Scrollbar(self.frame_main, command=self.txt_posts.yview)
        self.scrollb.grid(row=1, column=3, sticky='nsew')
        self.txt_posts['yscrollcommand'] = self.scrollb.set
        self.txt_posts.config(state="disabled")
        self.txt_create_post = ScrolledText(self.frame_main, height=6, width=60)
        self.txt_create_post.grid(row=2, rowspan=2, column=0, **self.padding)
        self.btn_post = tk.Button(self.frame_main, text="Post", command=self.act_post, state="disabled")
        self.btn_post.grid(row=3, column=1)
        self.category = tk.StringVar(self)
        self.category.trace('w', self.update_posts)
        self.cmb_category = ttk.Combobox(self.frame_main, state="readonly", textvariable=self.category, width=35)
        self.cmb_category.grid(row=2, column=1, **self.padding)

        # =================== Login Frame   =====================================
        self.frame_login = ttk.Frame(
            self,
            width=self.width,
            height=self.height - ((self.padding["pady"] * 2) + (self.padding["ipady"] * 2))
        )
        self.frame_login.grid(row=0, column=0, padx=300, pady=170)
        self.lbl_login_email = tk.Label(self.frame_login, text="Email")
        self.lbl_login_email.grid(row=0, column=0,  sticky=tk.W)
        self.login_email = tk.StringVar(self)
        self.txt_login_email = tk.Entry(self.frame_login, textvariable=self.login_email, width=35)
        self.txt_login_email.grid(row=0, column=1, sticky=tk.W+tk.E)
        self.txt_login_email.bind("<Return>", (lambda event: self.act_login()))

        self.lbl_login_pwd = tk.Label(self.frame_login, text="Password")
        self.lbl_login_pwd.grid(row=1, column=0, sticky=tk.W)
        self.login_pwd = tk.StringVar(self)
        self.txt_login_pwd = tk.Entry(self.frame_login, show="*", textvariable=self.login_pwd, width=35)
        self.txt_login_pwd.grid(row=1, column=1, sticky=tk.W + tk.E)
        self.txt_login_pwd.bind("<Return>", (lambda event: self.act_login()))

        self.btn_cancel1 = tk.Button(self.frame_login, text="Cancel", command=self.act_cancel)
        self.btn_cancel1.grid(row=2, column=0, pady=50)
        self.btn_login = tk.Button(self.frame_login, text="Log In", command=self.act_login)
        self.btn_login.grid(row=2, column=1)
        self.frame_login.grid_remove()  # Remove login frame from view

        # =================== SignUp Frame   =====================================
        self.frame_signup = ttk.Frame(
            self,
            width=self.width,
            height=self.height - ((self.padding["pady"] * 2) + (self.padding["ipady"] * 2))
        )
        self.frame_signup.grid(row=1, column=0, padx=250, pady=170)
        self.lbl_fname = tk.Label(self.frame_signup, text="First Name")
        self.lbl_fname.grid(row=1, column=0, sticky=tk.E)
        self.signup_fname = tk.StringVar(self)
        self.txt_signup_fname = tk.Entry(self.frame_signup, textvariable=self.signup_fname)
        self.txt_signup_fname.grid(row=1, column=1, sticky=tk.W + tk.E)

        self.lbl_signup_lname = tk.Label(self.frame_signup, text="Last Name")
        self.lbl_signup_lname.grid(row=2, column=0, sticky=tk.E)
        self.signup_lname = tk.StringVar(self)
        self.txt_signup_lname = tk.Entry(self.frame_signup, textvariable=self.signup_lname)
        self.txt_signup_lname.grid(row=2, column=1, sticky=tk.W + tk.E)

        self.lbl_signup_pwd1 = tk.Label(self.frame_signup, text="Password")
        self.lbl_signup_pwd1.grid(row=3, column=0, sticky=tk.E)
        self.signup_pwd1 = tk.StringVar(self)
        self.txt_signup_pwd1 = tk.Entry(self.frame_signup, show="*", textvariable=self.signup_pwd1)
        self.txt_signup_pwd1.grid(row=3, column=1, sticky=tk.W + tk.E)

        self.lbl_signup_pwd2 = tk.Label(self.frame_signup, text="Repeat password")
        self.lbl_signup_pwd2.grid(row=4, column=0, sticky=tk.E)
        self.signup_pwd2 = tk.StringVar(self)
        self.txt_signup_pwd2 = tk.Entry(self.frame_signup, show="*", textvariable=self.signup_pwd2)
        self.txt_signup_pwd2.grid(row=4, column=1, sticky=tk.W + tk.E)
        self.txt_signup_pwd2.bind("<Return>", (lambda event: self.act_signup()))

        self.btn_cancel2 = tk.Button(self.frame_signup, text="Cancel", command=self.act_cancel)
        self.btn_cancel2.grid(row=5, column=0, sticky=tk.E, pady=30)
        self.btn_signup = tk.Button(self.frame_signup, text="Sign Up", command=self.act_signup)
        self.btn_signup.grid(row=5, column=1, sticky=tk.E)

        self.signup_admin = tk.IntVar()
        self.chk_admin = tk.Checkbutton(self.frame_signup, text="Admin", variable=self.signup_admin)
        self.chk_admin.grid(row=6, column=0, sticky=tk.E, pady=30)
        self.frame_signup.grid_remove()

    def populate_categories(self, cmb_box=None):
        """Gets the list of categories and populates the default combo box or any combo box passed as an argument
        It also returns a dict of categories with descriptions as key"""
        items = []
        if cmb_box is None:
            cmb_box = self.cmb_category
            items.append("All categories")

        try:
            response = requests.get(f"{SERVER}categories/")
            for item in response.json()["categories"]:
                items.append(item["name"])
            cmb_box["values"] = items
            cmb_box.current(newindex=0)
            return {item['name']: item for item in response.json()["categories"]}
        except:
            messagebox.showerror("Server offline", f"Server {SERVER} is not responding"
                                                   f"\n Start the server first, then open the gui interface")
            self.disable_login_signup()

    def disable_login_signup(self):
        # In case API is offline, disable login and signup menus
        self.menu.entryconfig("Log in", state="disabled")
        self.menu.entryconfig("Sign up", state="disabled")
        self.menu.entryconfig("Sign out", state="disabled")
        self.menu_admin.entryconfig("Create new category", state="disabled")
        self.menu_admin.entryconfig("Delete a category", state="disabled")
        self.menu_admin.entryconfig("Modify a category", state="disabled")
        self.btn_post.config(state="disabled")

    def set_menus(self):
        # Enables or disables the menus depending if user is logged in or not
        signed_out = self.token is None
        show_admin = not signed_out and self.is_admin()
        self.menu.entryconfig("Log in", state="normal" if signed_out else "disabled")
        self.menu.entryconfig("Sign up", state="normal" if signed_out else "disabled")
        self.menu.entryconfig("Sign out", state="disabled" if signed_out else "normal")
        self.btn_post.configure(state="disabled" if signed_out else "normal")
        self.menu_admin.entryconfig("Create new category",  state="normal" if show_admin else "disabled")
        self.menu_admin.entryconfig("Delete a category", state="normal" if show_admin else "disabled")
        self.menu_admin.entryconfig("Modify a category", state="normal" if show_admin else "disabled")

    def act_cancel(self):
        # Cancel button action
        self.frame_login.grid_remove()
        self.frame_signup.grid_remove()
        self.frame_main.grid()

    def act_signout(self):
        # Action for sign out menu option
        self.session.close()
        self.session = None
        self.token = None
        self.set_menus()
        self.show_info("Signed out", "You are now signed out")

    def act_admin_create(self):
        # Action for admin menu to create new option
        def act_create():
            # Action for pressing create category button
            desc_text = desc.get().strip()
            tag_text = tag.get().replace(" ", "").lower()
            data = {"description": desc_text, "hashtag": tag_text}
            result = requests.post(f"{SERVER}category/create/", data=data, headers=self.token)
            self.clear_entry([txt_desc, txt_tag])
            self.show_info("Message", response=result)

        admin_frame = self.create_admin_window("Create a category")
        lbl_desc = tk.Label(admin_frame, text="Description")
        lbl_desc.grid(row=0, column=0, sticky=tk.E)
        desc = tk.StringVar(self)
        txt_desc = tk.Entry(admin_frame, textvariable=desc)
        txt_desc.grid(row=0, column=1, sticky=tk.W + tk.E)

        lbl_tag = tk.Label(admin_frame, text="Tag")
        lbl_tag.grid(row=1, column=0, sticky=tk.E)
        tag = tk.StringVar(self)
        txt_tag = tk.Entry(admin_frame, textvariable=tag)
        txt_tag.grid(row=1, column=1, sticky=tk.W + tk.E)

        btn_create = tk.Button(admin_frame, text="Create category", command=act_create)
        btn_create.grid(row=2, column=1)

    def act_admin_delete(self):
        # Action for create option in admin menu
        def act_delete():
            # Action for delete button
            data = {"category": cat.get()}
            response = requests.get(f"{SERVER}posts/", params=data)
            nb_of_posts = len(response.json()["posts"])
            message = f"Are you sure you want to delete {cat.get()}?"
            message += f"\nThis will also delete {nb_of_posts} post(s)" if nb_of_posts > 0 else ""
            MsgBox = tk.messagebox.askquestion("Delete category", message, icon='warning')
            if MsgBox == 'yes':
                response = requests.delete(f"{SERVER}category/delete/", headers=self.token, data=data)
                self.show_info(response=response)
                self.populate_categories(cmb)

        admin_frame = self.create_admin_window("Delete a category")
        lbl = tk.Label(admin_frame, text="Choose a category")
        lbl.grid(row=0, column=0, sticky=tk.E)
        cat = tk.StringVar()
        cmb = ttk.Combobox(admin_frame, state="readonly", textvariable=cat, width=35)
        cmb.grid(row=0, column=1, **self.padding)
        btn_delete = tk.Button(admin_frame, text="Delete", command=act_delete)
        btn_delete.grid(row=1, column=1, sticky=tk.E)
        self.populate_categories(cmb)

    def act_admin_modify(self):
        # Action for admin menu to edit a category
        def act_modify():
            # Action for pressing create modify
            desc_text = desc.get().strip()
            tag_text = tag.get().replace(" ", "").lower()
            data = {"category": cat.get(), "new_description": desc_text, "new_hashtag": tag_text}
            result = requests.post(f"{SERVER}category/update/", data=data, headers=self.token)
            self.populate_categories(cmb)
            update_boxes(None, None, None)
            self.show_info("Message", response=result)

        def update_boxes(a, b, c):
            current_cat = self.populate_categories()[cmb.get()]
            desc.set(current_cat["name"])
            tag.set(current_cat["hashtag"])
            created.set(current_cat["created"])
            updated.set(current_cat["updated"])


        admin_frame = self.create_admin_window("Update a category")
        lbl = tk.Label(admin_frame, text="Choose a category")
        lbl.grid(row=0, column=0, sticky=tk.E)
        cat = tk.StringVar()
        tag = tk.StringVar(self)
        desc = tk.StringVar(self)
        created = tk.StringVar(self)
        updated = tk.StringVar(self)

        cat.trace('w', update_boxes)
        cmb = ttk.Combobox(admin_frame, state="readonly", textvariable=cat, width=35)
        self.populate_categories(cmb)
        cmb.grid(row=0, column=1, **self.padding)
        lbl_desc = tk.Label(admin_frame, text="Description")
        lbl_desc.grid(row=1, column=0, sticky=tk.E)
        txt_desc = tk.Entry(admin_frame, textvariable=desc)
        txt_desc.grid(row=1, column=1, sticky=tk.W + tk.E)

        lbl_tag = tk.Label(admin_frame, text="Tag")
        lbl_tag.grid(row=2, column=0, sticky=tk.E)
        txt_tag = tk.Entry(admin_frame, textvariable=tag)
        txt_tag.grid(row=2, column=1, sticky=tk.W + tk.E)

        lbl_created = tk.Label(admin_frame, text="Created on")
        lbl_created.grid(row=3, column=0, sticky=tk.E)
        txt_created = tk.Entry(admin_frame, textvariable=created, state='disabled')
        txt_created.grid(row=3, column=1, sticky=tk.W + tk.E)

        lbl_updated = tk.Label(admin_frame, text="Updated on")
        lbl_updated.grid(row=4, column=0, sticky=tk.E)
        txt_updated = tk.Entry(admin_frame, textvariable=updated, state='disabled')
        txt_updated.grid(row=4, column=1, sticky=tk.W + tk.E)

        btn_create = tk.Button(admin_frame, text="Update", command=act_modify)
        btn_create.grid(row=5, column=1)

    def act_login(self):
        client = requests.session()

        URL = f"{SERVER}api-token-auth/"
        login_data = {'username': self.login_email.get(),
                      'password': self.login_pwd.get()}
        response = client.post(URL, data=login_data)
        if response.status_code == 200:
            self.btn_post.config(state="normal")
            self.session = client

            self.token = {"Authorization": "Token " + json.loads(response.content.decode("utf-8"))['token']}
            self.act_cancel()
            self.set_menus()
        else:
            self.show_info("Unable to login", "Invalid username or password")
        self.clear_entry([self.txt_login_email, self.txt_login_pwd])

    def act_signup(self):
        """
        This is the action performed by the sign up button.
        It does very basic input validation before sending the request to the API.
        Proper validation is done by the API
        """
        fname = self.signup_fname.get().replace(" ", "").lower()
        lname = self.signup_lname.get().replace(" ", "").lower()
        #   Basic input validation
        if fname == "" or lname == "" or not fname.isalpha() or not lname.isalpha():
            self.show_info("Error", "You must enter a valid first and last name")
            return
        if not self.signup_pwd1.get() == self.signup_pwd2.get():
            self.show_info("Error", "Passwords do not match")
            return

        URL = f"{SERVER}register/"
        email = f"{fname}.{lname}@tudublin.ie"
        signup_data = {
            "username": email,
            "email": email,
            "first_name": fname.title(),
            "last_name": lname.title(),
            "password1": self.signup_pwd1.get(),
            "password2": self.signup_pwd2.get(),
            "is_staff": self.signup_admin.get() == 1
        }
        response = requests.post(URL, signup_data)
        if response.status_code == 201:  # User created
            self.act_cancel()
            self.show_info("User created", f"Email: {email}\nPassword: {self.signup_pwd1.get()}")

            # Authenticating the newly created user
            self.login_email.set(email)
            self.login_pwd.set(self.signup_pwd1.get())
            self.act_login()

            # Clearing signup text boxes
            self.clear_entry([self.txt_signup_fname, self.txt_signup_lname, self.txt_signup_pwd1, self.txt_signup_pwd2])
        else:   # Failed to create user
            message = ""
            for k, v in json.loads(response.content.decode("utf-8")).items():
                details = ""
                for item in v:
                    details += item + "\n"
                message += f"*{k}: {details}\n"
            self.show_info("Signup failed", message)

    def act_post(self):
        """
        This is the action performed by the post button.
        It has input validation to make sure that a category was chosen and that the post has a title and content
        """
        if self.category.get() == "All categories":
            self.show_info("Choose a category", "You must first choose a category before you can create a post")
            return
        user_input = self.txt_create_post.get("1.0", tk.END)

        content = user_input.strip()
        if "\n" in content:
            split = content.split("\n", 1)
            output = {"title": split[0],
                    "content": split[1],
                    "category": self.category.get()
            }
            self.clear_textbox(self.txt_create_post)
        else:
            self.show_info("Your post has no content", "The title of the post must be on the first line, and the "
                                                       "content on the lines below")
            return
        result = requests.post(f"{SERVER}create_post/", data=output, headers=self.token)
        self.update_posts(None, None, None)     # Shows the newly created post

    def create_admin_window(self, title):
        # Creates a new window and hides the main one
        self.withdraw()  # Hide the main window
        admin_window = tk.Toplevel(self)

        def act_close_window():
            # This function activates when closing the admin window
            self.deiconify()  # Show the main window again
            admin_window.destroy()  # Destroy the admin window
            self.populate_categories()  # Update the categories in case some changes were made using admin

        admin_window.protocol("WM_DELETE_WINDOW", act_close_window)
        admin_window.geometry("500x300")
        admin_window.title(title)
        frame_admin = ttk.Frame(admin_window)
        frame_admin.grid(padx=50, pady=70)

        return frame_admin

    def update_posts(self, index, value, op):
        # Event for index changed in the category dropbox
        if self.category.get() == "All categories":
            param = {}
        else:
            param = {"category": self.category.get()}
        response = requests.get(f"{SERVER}posts/", params=param)
        self.txt_posts.from_list(response.json()["posts"])

    def is_admin(self):
        if self.session:
            result = self.session.get(f"{SERVER}is_admin/", headers=self.token)
            if result.status_code == 200:
                return True
        return False

    def log_in_page(self):
        # Shows login page
        self.frame_main.grid_remove()
        self.frame_signup.grid_remove()
        self.frame_login.grid()

    def sign_up_page(self):
        # Shows signup page
        self.frame_login.grid_remove()
        self.frame_main.grid_remove()
        self.frame_signup.grid()

    def clear_entry(self, entry_items):
        for item in entry_items:
            item.delete(0, tk.END)

    def clear_textbox(self, itm):
        itm.delete("1.0", tk.END)

    def catch_destroy(self):
        if messagebox.askokcancel("Quit", "Do you really want to quit?"):
            if self.session:
                self.session.close()
            self.destroy()

    def show_info(self, title="Info", message="Nothing to show.", response=None, icon='info'):
        if response is not None:
            message = ""
            for k, v in json.loads(response.content.decode("utf-8")).items():
                title = k
                message += f"{v}\n"
        messagebox.showinfo(title, message)




def main():
    GUI_SETTINGS = {
        "width": 800,
        "height": 600,
        "status_bar_height": 10,
        "resizable_width": False,
        "resizable_height": False,
        "title_text": "My Blogging app",
    }

    app = MyGUI(GUI_SETTINGS)
    app.populate_categories()
    app.mainloop()


if __name__ == "__main__":
    main()
