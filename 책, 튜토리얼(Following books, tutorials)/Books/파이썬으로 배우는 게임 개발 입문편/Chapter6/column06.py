import tkinter

root = tkinter.Tk()

root.title("캔버스에 도형 그리기")
root.geometry("500x400")

cvs = tkinter.Canvas(root, width=500, height=400, bg="white")

cvs.pack()

cvs.create_text(250, 25, text="문자열", fill="green", font=("Times New Roman", 24))

cvs.create_line(30, 30, 70, 80, fill="navy", width=5)
cvs.create_line(120, 20, 80, 50, 200, 80, 140, 120, fill="blue", smooth=True)

cvs.create_rectangle(40, 140, 160, 200, fill="lime")
cvs.create_rectangle(60, 240, 120, 360, fill="pink", outline="red", width=5)

cvs.create_oval(250 - 40, 100 - 40, 250 + 40, 100 + 40, fill="silver", outline="purple")
cvs.create_oval(250 - 80, 200 - 40, 250 + 80, 200 + 40, fill="cyan", width=0)

cvs.create_polygon(250, 250, 150, 350, 350, 350, fill="magenta", width=0)

cvs.create_arc(400 - 50, 100 - 50, 400 + 50, 100 + 50, fill="yellow", start=30, extent=300)
cvs.create_arc(400 - 50, 250 - 50, 400 + 50, 250 + 50, fill="gold", start=0, extent=120, style=tkinter.CHORD)
cvs.create_arc(400 - 50, 350 - 50, 400 + 50, 350 + 50, outline="orange", start=0, extent=120, style=tkinter.ARC)

cvs.mainloop()
