#import libaries
import sqlite3

from tkinter import *
from tkinter import messagebox

#from threading import Thread

from TkTreectrl import *

import time

connSQL=sqlite3.connect('database_PoS.db')
curs=connSQL.cursor()

output_txt = 'today_transaction.txt' 

#create root window
root = Tk()

#modify root window
root.title("P.P. Parts (Rimkok)")
toplevel = root.winfo_toplevel()
toplevel.wm_state('zoomed')

##for Windows platform##
txtfield = Frame(root, width=1000, height=600, bd=1)
txtfield.pack(side='top', fill='both', padx=5, pady=5)

itxtfield = Frame(txtfield, bd=2, relief=RIDGE)
itxtfield.pack(fill=X)
Label(itxtfield, text = "Insert Barcode: ", font=(16)).pack(side=LEFT, padx=5)

e = Entry(itxtfield, bg='white', font=(20), width=20)
e.pack(side=LEFT, padx=5)
e.focus_set()

Label(itxtfield, text = "Press Enter to add a product", font=(16)).pack(side=LEFT, padx=5)


#create listbox (MultiListbox)
m = ScrolledMultiListbox(root, relief='groove', bd=2, width=150, height=300)
m.pack(side='top', fill='both', expand=1, padx=2, pady=2)
m.listbox.config(columns=('Barcode', 'Product name', 'Price'), expandcolumns=(0,1,2), selectmode='extended', font=(16), headerfont=(16))

#configure listbox
colors = ('white', '#ffdddd', 'white', '#ddeeff')
m.listbox.column_configure(m.listbox.column(0), itembackground=colors)
m.listbox.column_configure(m.listbox.column(1), itembackground=colors)
m.listbox.column_configure(m.listbox.column(2), itembackground=colors)


#create frame for total
totalFrame = Frame(root, width=1000, height=5, bd=1)
totalFrame.pack(side='top', fill='both', padx=5, pady=5)

totalInside = Frame(totalFrame, bd=2, relief=RIDGE)
totalInside.pack(fill=X)
Label(totalInside, text="Total", font=(50), bg='violet', width=20, height=5).grid(row=0, column=0, padx=5, pady=5)

#set a label for updating total value
v = StringVar()
Label(totalInside, textvariable=v, font=(50), bg='yellow',width=40, height=5).grid(row=0, column=1, columnspan =2, padx=5, pady=5)
v.set("0")

#set a label to inform after press Ctrl+s
Label(totalInside, text = "Received", font=(50), width=20, height=5).grid(row=0, column=3, padx=5, pady=5)

calc_frame = Frame(totalInside, width=5, height=5)
c = Entry(calc_frame, bg='white', font=(50))    
c.pack(fill=X)
c.config(state=DISABLED)
calc_frame.grid(row=0, column=4, padx=5, pady=5)

Label(totalInside, text = "Insert recieved amount >> press Enter", font=(50), height=5).grid(row=0, column=5, padx=5, pady=5)

Label(totalInside, text = "Change", font=(50), width=20, height=5).grid(row=1, column=3, rowspan=2, padx=5, pady=5)
u = StringVar()
Label(totalInside, textvariable=u, font=(50), width=25, height=5, bg='white', fg='red').grid(row=1, column=4, rowspan=2, padx=5, pady=5)
u.set("")

dateNtime = Frame(totalInside, width=5, height=5)
d = StringVar()
Label(dateNtime, textvariable=d, font=(50), width=25, height=2, bg='black', fg='white').pack()
d.set("")
t = StringVar()
Label(dateNtime, textvariable=t, font=(50), width=25, height=2, bg='black', fg='white').pack()
t.set("")
dateNtime.grid(row=1, column=5)

#set global variables
priceB4addition = 0 #initial value for summation calculation
end = False
init_ready4newTrans = True
initNodata = True
print_date = ""
print_time = ""


#definitions
def DATE(): 
    return time.strftime("%d/%m/%Y")

def TIME():    
    return time.strftime("%H:%M:%S")   

def retrieve_pName(code):
    curs.execute("SELECT Pname FROM productDetail WHERE Bcode=(?)",(code,))
    for row in curs:
        return row

def retrieve_pPrice(code):
    curs.execute("SELECT Pprice FROM productDetail WHERE Bcode=(?)",(code,))
    for row in curs:
        return row

def set_iniprice():
    global priceB4addition
    priceB4addition = 0
    return priceB4addition

def sum_calculate(price):
    global priceB4addition
    priceB4addition = priceB4addition + price
    print("total for now: ",priceB4addition)
    return priceB4addition

def press_Enter(event):
    global end
    global init_ready4newTrans
    global initNodata
    global priceB4addition
    if(end == False):
        if(init_ready4newTrans == True):
            init_ready4newTrans = False
        getBarcode =e.get()
        nameProduct = retrieve_pName(getBarcode)
        priceProduct = retrieve_pPrice(getBarcode)
        if(nameProduct == None or priceProduct == None):
            print("No data")
            messagebox.showwarning(
                "Warning",
                "No product barcode in database"
                )
            e.delete(0, END)
            e.focus_set()
            if(initNodata == True):
                checkout_transButt.config(state=DISABLED)
                cancel_transButt.config(state=DISABLED)
        else:
            if(initNodata == True):
                head_trans()
                initNodata = False
                checkout_transButt.config(state=NORMAL)
                cancel_transButt.config(state=NORMAL)
            priceEdit = str(priceProduct).replace("(","")
            priceEdit2 = priceEdit.replace(")","")
            priceStr = priceEdit2.replace(",","")
            nameEdit = str(nameProduct).replace("(","")
            nameEdit2 = nameEdit.replace(",","")
            nameEdit3 = nameEdit2.replace("'","")
            nameStr = nameEdit3.replace(")","")
            status_on_screen(getBarcode, nameStr, priceStr)
            write_file(getBarcode, nameStr, priceStr)
            #Thread(target = status_on_screen(getBarcode, nameStr, priceStr)).start()
            #Thread(target = status_on_led(nameStr[:8] + ": " + priceStr[:4], "Total: " + priceB4addition)).start()
            #Thread(target = write_file(getBarcode, nameStr, priceStr)).start()
            #status_on_led(nameStr[:10] + ": " + priceStr[:4], "Total= " + str(priceB4addition))
    else:
        pay = c.get()
        try:
            pay_int = int(pay)
            if(int(pay) < int(priceB4addition)):
                messagebox.showwarning(
                    "Invalid integer",
                    "...Insert again"
                    )
                c.delete(0, END)
                c.focus_set()
            else:
                init_ready4newTrans = True
                c.config(state=DISABLED)
                change = str(int(pay)-int(priceB4addition))
                u.set(change)
                #status_on_led("Change :", change)
                new_transButt.config(state=NORMAL)
                file = open(output_txt, 'a+')
                file.write("\n\nRecieved : " + pay)
                file.write("\n>> Change : " + change)
                file.write("\n")
                file.close()
        except ValueError:
            messagebox.showwarning(
                    "Invalid input",
                    "...Insert again in numbers"
                    )
            c.delete(0, END)
            c.focus_set()

def write_file(barcode, name, price):
    file = open(output_txt, 'a+')
    file.write("\n")
    file.write(str(barcode) + " | " + name + " | " + price)
    file.close()

def status_on_screen(barcodeP, nameP, priceP):
    priceInt = int(priceP)
    print("current product price: "+ priceP)
    v.set(str(sum_calculate(priceInt)))        
    m.listbox.insert(END, barcodeP, nameP, priceP)
    e.delete(0, END)
    e.focus_set()

def head_trans():
    global print_date
    global print_time
    print_date = DATE()
    print_time = TIME()
    d.set(print_date)
    t.set(print_time)
    date_time = print_date + " - " + print_time
    print(date_time)
    file = open(output_txt, 'a+')
    file.write("\n____________________ New Transaction ____________________\n")
    file.write(date_time)
    file.write("\n\n   Product Code   |   Product Name   |   Price\n")
    file.close()

def state_init():
    global end
    global priceB4addition
    global init_ready4newTrans
    global initNodata
    global print_date
    global print_time
    end = False
    priceB4addition = 0
    init_ready4newTrans = True
    initNodata = True
    v.set("0")
    u.set("")
    d.set("")
    t.set("")
    print_date = ""
    print_time = ""
    e.config(state=NORMAL)
    e.focus_set()
    m.listbox.delete(0,END)
    c.config(state=NORMAL)
    c.delete(0, END)
    c.config(state=DISABLED)
    new_transButt.config(state=DISABLED)
    cancel_transButt.config(state=DISABLED)
    set_iniprice()
    checkout_transButt.config(state=DISABLED)
    #welcome_on_led("P.P.Parts", "(Rimkok)")

def temp_end_trans():
    e.config(state=DISABLED)
    quitORnot = messagebox.askquestion("Continue", "Check out?", icon='warning')
    if quitORnot == 'yes':
        end_trans()
        checkout_transButt.config(state=DISABLED)
    else:
        continue_trans()
    print("temp_end_trans")
    
def continue_trans():
    e.config(state=NORMAL)
    print("continue_trans")
    u.set("")
    return

def end_trans():
    cancel_transButt.config(state=DISABLED)
    global end    
    global priceB4addition
    end = True
    total_2pay = str(priceB4addition)

    c.config(state=NORMAL)
    c.focus_set()
    
    file = open(output_txt, 'a+')
    file.write("\n\n>> Total : " + total_2pay)
    file.close()
    
    print("end_trans")

def cancel_trans():
    global end
    end = False
    quitORnot = messagebox.askquestion("Continue", "Start new transaction?\n...Current transaction will be removed", icon='warning')
    if quitORnot == 'yes':
        file = open(output_txt, 'a+')
        file.write("\n=============== The transaction is canceled ===============\n")
        file.close()
        state_init()
    else:
        continue_trans()

def b4exit():
    global print_date
    global print_time
    print_date = DATE()
    print_time = TIME()
    date_time = print_date + " - " + print_time
    if(init_ready4newTrans == True):
        quitORnot = messagebox.askquestion("Continue", "Exit program?", icon='warning')
        if quitORnot == 'yes':
            print("/////// Program is terminated //////////")
            file = open(output_txt, 'a+')
            file.write("\n///////////////////////// Program is terminated (" + date_time + ") /////////////////////////\n")
            file.close()
            root.destroy()
            root.quit()
        else:
            continue_trans()
    else:
        quitORnot = messagebox.askquestion("Continue", "Exit program?\n...Current transaction will be removed", icon='warning')
        if quitORnot == 'yes':
            print("/////// Program is terminated //////////")
            file = open(output_txt, 'a+')
            file.write("\n=============== The transaction is canceled ===============\n")
            file.write("\n///////////////////////// Program is terminated (" + date_time + ") /////////////////////////\n")
            file.close()
            root.destroy()
            root.quit()
        else:
            continue_trans()


#add buttons

exitButt = Button(itxtfield, text = "Exit program", font=(40), width=30, bg='#ffdddd', command=b4exit)
exitButt.pack(side=RIGHT, padx=5)

cancel_transButt = Button(totalInside, text = "Cancel", font=(40), width=20, bg='#ddeeff', command=cancel_trans)
cancel_transButt.grid(row=1, column=0, padx=5, pady=5)
new_transButt = Button(totalInside, text = "New transaction", font=(40), width=20, bg='#ddeeff', command=state_init)
new_transButt.grid(row=1, column=1, padx=5, pady=5)
checkout_transButt = Button(totalInside, text = "Checkout", font=(40), width=20, bg='#ddeeff', command=temp_end_trans)
checkout_transButt.grid(row=1, column=2, padx=5, pady=5)
    

#bind keys with root
root.bind("<Return>", press_Enter)
root.protocol("WM_DELETE_WINDOW", b4exit)

#initiate state
state_init()

#loop
root.mainloop()

