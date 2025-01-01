import tkinter as tk
from tkinter import messagebox

def login():
    username = entry_username.get()
    password = entry_password.get()
    
    # Here, you can add your authentication logic
    # For simplicity, let's just check if username and password are not empty
    if username and password:
        messagebox.showinfo("Login", "Login successful!")
    else:
        messagebox.showerror("Login", "Invalid username or password")

# Create main window
root = tk.Tk()
root.title("Login Page")

# Set window size and position
window_width = 400
window_height = 300
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_coordinate = (screen_width/2) - (window_width/2)
y_coordinate = (screen_height/2) - (window_height/2)
root.geometry("%dx%d+%d+%d" % (window_width, window_height, x_coordinate, y_coordinate))

# Load background image
bg_image = tk.PhotoImage(file="bg.png")
bg_label = tk.Label(root, image=bg_image)
bg_label.place(relwidth=1, relheight=1)

# Create username label and entry
label_username = tk.Label(root, text="Username:", font=("Arial", 12), bg="pink")
label_username.place(relx=0.2, rely=0.3)
entry_username = tk.Entry(root, font=("Arial", 12))
entry_username.place(relx=0.4, rely=0.3)

# Create password label and entry
label_password = tk.Label(root, text="Password:", font=("Arial", 12), bg="light pink")
label_password.place(relx=0.2, rely=0.4)
entry_password = tk.Entry(root, show="*", font=("Arial", 12))
entry_password.place(relx=0.4, rely=0.4)

# Create login button
button_login = tk.Button(root, text="Login", font=("Arial", 12), command=login)
button_login.place(relx=0.4, rely=0.5)

root.mainloop()
