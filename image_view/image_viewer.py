from tkinter import *
from tkinter import filedialog
from PIL import ImageTk, Image

root = Tk()
root.title("MANAN PANCHAL")
root.iconphoto(True, ImageTk.PhotoImage(Image.open('D:/git/learning-stuff/image_view/logo.png').resize((32, 32), Image.Resampling.LANCZOS)))

def resize_image(image_path, size=(300, 300)):
    img = Image.open(image_path)
    img = img.resize(size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)

def open_image():
    global label, current_image
    file_path = filedialog.askopenfilename(
        title="Select an image",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.tiff")]
    )
    if file_path:
        img = resize_image(file_path, size=(400, 400))
        images.append(img)
        current_image = len(images) - 1
        update_image()

def update_image():
    label.config(image=images[current_image])

def backward():
    global current_image
    if current_image > 0:
        current_image -= 1
    update_image()

def forward():
    global current_image
    if current_image < len(images) - 1:
        current_image += 1
    update_image()

img = resize_image('logo.png', size=(400, 400))  # Initial image, resized
images = [img]
current_image = 0

label = Label(root, image=images[current_image])
label.grid(row=0, column=0, columnspan=3)

back = Button(root, text="<<", command=backward)
back.grid(row=1, column=0)

forward_button = Button(root, text=">>", command=forward)
forward_button.grid(row=1, column=2)

open_button = Button(root, text="Open Image", command=open_image)
open_button.grid(row=1, column=1)

exit_button = Button(root, text="EXIT", command=root.quit)
exit_button.grid(row=2, column=1)

root.mainloop()
