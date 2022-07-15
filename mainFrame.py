from tkinter import CENTER, END, Label,Button, Entry, Frame, Radiobutton, Scrollbar
from tkinter import ttk
from tkinter.ttk import Combobox
from tkinter import *
from tkinter.constants import DISABLED, NORMAL
from tkinter import  messagebox
from libExcel import Excel
from libCaminoCritico import CaminoCritico


class MainFrame(Frame):
    archivoExcel = ""  #Variable que mantiene en menoria el archivo excel seleccionado
    dataFrame = ""  #Variable que mantiene el dataframe de pandas que se genero a partir de archivoExcel
    auxInput = []   #Vector auxziliar que mantiene el input de los usuarios cuando insertan las tareas manualmente
    rutaCritica = '' #Lista que recibe los resultados del algoritmo de CPM 
                    #(forwardPass, backwardPass y la ruta critica en si)
    def __init__(self, master=None):
        super().__init__(master, width=800, height= 660)
        self.master = master        
        self.pack()
        claseExcel = Excel 
        claseCPM = CaminoCritico
        self.create_widgets(claseExcel,claseCPM)  


    def recolectarInput(self,input1,input2,input3,input4,tabla, opciones):
        #Se recogen los input de cada textbot (tkinter Entry)        
        ident = input1.get()
        if ident in opciones:
            messagebox.showinfo(title="Advertencia", message="Ese identificador ya existe")
        else:
            opciones.append(ident)
            desc = input2.get()
            duracion = input3.get()
            predec = input4.get()
            if duracion.isdigit():            
                #Si no tiene predecesor se le coloca * Para que no haya error con el algoritmo implementado
                if predec == '':
                    predec = float("*")
                    self.auxInput.append(ident+'-'+desc+'-'+duracion+'-'+'.')
                else:
                    self.auxInput.append(ident+'-'+desc+'-'+duracion+'-'+predec)
                #Se inserta en la tabla de la interfaz de estado inicial
                tabla.insert("",END,text=ident, values=(predec,desc,duracion))
                self.lista_auxiliar = opciones
            else:
                messagebox.showinfo(title="Advertencia", message="La duracion debe ser numerica")
        

    #Se llama a una funcion en libExcel que permite la carga de un archivo en disco
    #y se inserta lo del archivo en la tabla de la interfaz de estado inicial
    #Necesita que se le pase la clase de libExcel y la tabla a modificar
    def cargarArchivo(self, excel,tabla1):
        #LLamamos a la funcion en libExcel para que abra y procese el archivo
        self.dataFrame, self.archivoExcel = excel.abrir_archivo()
        #Si no se escogio archivo alguno se le avisa al usuario 
        if(self.archivoExcel == ""):
            messagebox.showinfo(title="Advertencia", message = "No seleccionaste ningun archivo") 
        else:
        #Si se escogio un archivo se agrega a la tabla de la interfaz
            for x in range(0,self.dataFrame['identificacion'].size):
                tabla1.insert("",END,text=self.dataFrame['identificacion'][x]
                    ,values=(self.dataFrame['predecessors'][x],self.dataFrame['descripcion'][x]
                        ,self.dataFrame['duracion'][x]))

    #Funcion que de acuerdo a como se hayan ingresado los datos rellena las tablas de forwardpass
    # y backward pass
    #Necesita que se le pase la clase de libCaminoCritico y las tablas a modificar
    def llenarTablas(self,llenadoTabla,tabla1,tabla2):
        try:
            #Variable auxiliar
            informacion = ''
            #Verificaciones basicas dependiendo de como se hayan ingresado los datos
            if (self.archivoExcel == "" and len(self.auxInput)==0):
                messagebox.showinfo(title="Advertencia", message = "No hay datos ingresados")
            #La clase libCaminoCritico tiene metodos diferentes para procesar la informacion recibirda
            #(si se ingreso por excel o manual)
            elif self.archivoExcel == "":
                informacion = llenadoTabla.procesarInput(CaminoCritico,self.auxInput) 
            elif len(self.auxInput)==0:
                informacion = llenadoTabla.procesarArchivo(CaminoCritico,self.dataFrame)

            #Luego de recibida la info de los metodos de libCaminoCritico se inserta en las respectivas
            #tablas de la interfaz
            if informacion != '':
                self.rutaCritica = informacion
                Fp = informacion.forwardPass
                bP = informacion.backwardPass
                indices = Fp.index
                #Insercion en tabla de forwardPass
                for x in range(0,Fp['earlyFinish'].size):
                    tabla1.insert("",END,text=indices[x],values=(Fp['earlyFinish'][x],Fp['earlyStart'][x]))
                indices = bP.index
                #Insercion en tabla de backwardPass
                for x in range(0,bP['lateStart'].size):
                    tabla2.insert("",END,text=indices[x],values=(bP['lateStart'][x],bP['lateFinish'][x],bP['slack'][x]))
        except:
            messagebox.showinfo(title="Advertencia", message = "Hubo un error al calcular la ruta crítica. \n Por favor cierre el programa, revise los datos agregados e inténtelo nuevamente. \n Puede ser algun error de tipeo o su grafo tiene ciclos.")

    #Funcion que rellena los textbox que indican ruta critica y si hay holgura
    #Necesita que se le pasen todos los textbox a modificar
    def llenarTextbox(self,resp1,resp2,resp3,resp4,resp5):        
            #Modificando el textbox de si existe RC
            if resp1 != "":
                resp1.insert(0,"Si hay ruta critica")
            else:
                resp1.insert(0,"No hay ruta critica")
            #Modificando el textbox que indica cual es la RC
            resp2.insert(0,self.rutaCritica.criticalPath)
            #Modificando el textbox que pregunta si hay holgura
            auxBp = self.rutaCritica.backwardPass
            hasSlack = False
            for x in range(0,auxBp['slack'].size):
                if auxBp['slack'][x] > 0:
                    hasSlack = True
                    break
            if hasSlack == False:
                resp3.insert(0,"No posee holgura")
            else:
                resp3.insert(0,"Si posee holgura")
                #Modificando el textbox que indica 
                #la cantidad de eventos qe tienen holgura
                indicesHolgura = []
                cantidadholgura = []
                for x in range(0,auxBp['slack'].size):
                    if auxBp['slack'][x] > 0:
                        indicesHolgura.append(auxBp.index[x])
                        cantidadholgura.append(auxBp['slack'][x])
                resp4.insert(0,len(indicesHolgura))
                #Modificando el textbox que indica los eventos que tienen 
                #holgura con su respectiva holgura
                resp5Text = ''
                for x in range(0,len(indicesHolgura)):
                    resp5Text = resp5Text + str(indicesHolgura[x]) +' -> '+ str(cantidadholgura[x]) + ' \n'
                resp5.insert(0,resp5Text)        
        
    def create_widgets(self,excel,llenadoTabla):
 
        # labels
        Label(self,text="CARGA DE DATOS").place(x=20,y=10)
        Label(self,text="_____________________________________________________________________________________________________").place(x=20,y=30)
        Label(self,text="Identificador").place(x=20,y=50)
        Label(self,text="Descripción").place(x=140,y=50)
        Label(self,text="Duración").place(x=430,y=50)
        Label(self,text="Predecesor").place(x=20,y=110)
        Label(self,text="_____________________________________________________________________________________________________").place(x=20,y=130)
        Label(self,text="TABLA DE INICIO").place(x=230,y=155)
        Label(self,text="FORWARD PASS").place(x=230,y=320)
        Label(self,text="BACKWARD PASS").place(x=230,y=485)
        Label(self,text="ESTADÍSTICAS").place(x=650,y=155)
        Label(self,text="¿Posee ruta crítica?").place(x=590,y=195)
        Label(self,text="Ruta crítica:").place(x=590,y=255)
        Label(self,text="¿Posee holgura?").place(x=590,y=315)
        Label(self,text="Contador eventos con holgura").place(x=590,y=375)
        Label(self,text="Eventos y su holgura:").place(x=590,y=435)


        # textbox
        #input1
        txt_id = Entry(self, bg="white", state= DISABLED)
        txt_id.place(x=20, y=70, width=100, height=20)

        #input2
        txt_des = Entry(self, bg="white", state= DISABLED)
        txt_des.place(x=140, y=70, width=270, height=20)

        #input3
        txt_du = Entry(self, bg="white", state= DISABLED)
        txt_du.place(x=430, y=70, width=100, height=20)

        #respuesta1
        txt_existeRC = Entry(self, bg="white")
        txt_existeRC.place(x=590, y=225, width=190, height=20)
        
        #respuesta2
        txt_RC = Entry(self, bg="white")
        txt_RC.place(x=590, y=285, width=190, height=20)
        
        #respuesta3
        txt_holgura = Entry(self, bg="white")
        txt_holgura.place(x=590, y=345, width=190, height=20)
       
        #respuesta4
        txt_contador = Entry(self, bg="white")
        txt_contador.place(x=590, y=405, width=190, height=20)

        #respuesta5
        txt_listaHolgura = Entry(self, bg="white")
        txt_listaHolgura.place(x=590, y=465, width=190, height=100)

        #input4
        txt_pre = Entry(self, bg="white", state=DISABLED)
        txt_pre.place(x=260, y=110, width=150, height=20)


        

        
        # radiobuttons        
        
               
        opcion = IntVar()
        rbt_manual = Radiobutton(self, text= "Manual", value=1, variable=opcion, command=lambda: actualiza(opcion.get()))
        rbt_manual.place(x=140,y=10)
        rbt_archivo = Radiobutton(self, text= "Archivo", value=2, variable=opcion, command=lambda: actualiza(opcion.get()))
        rbt_archivo.place(x=260,y=10)     
       


        # combo_box

        self.opciones=[]
        self.lista_auxiliar =["Ninguno"]
        cmb_pre = Combobox(self, values=self.lista_auxiliar, state= DISABLED)        
        cmb_pre.place(x=140,y=110, width=100)

        def string_pre(pre, new, textbox):    
            if pre != "":
                    if pre.find(new) == -1:                        
                        pre = pre + ','+ new
                        txt_pre.config(text= pre)  
                    else:
                        messagebox.showinfo(title="Advertencia", message="No puede repetir predecesores")
            else:
                if new == "Ninguno":
                    new = "." 
                pre = new 
            textbox.delete(0, "end")
            textbox.insert(0, pre)           
        
        cmb_pre.bind("<<ComboboxSelected>>", lambda _ : [string_pre(txt_pre.get(), cmb_pre.get(), txt_pre)])

        # tabla datos iniciales

        tv = ttk.Treeview(self, columns=("col1","col2", "col3"))
        tv.column("#0",width=30)
        tv.column("col1",width=30, anchor=CENTER)
        tv.column("col2",width=150, anchor=CENTER)
        tv.column("col3",width=50, anchor=CENTER)

        tv.heading("#0", text="Identificador", anchor=CENTER)
        tv.heading("col1", text="Predecesor", anchor=CENTER)
        tv.heading("col2", text="Descripción", anchor=CENTER)
        tv.heading("col3", text="Duración", anchor=CENTER)

        #tv.insert("",END,text="Azucar", values=("28","lala", "12"))
        #tv.insert("",END,text="Refresco", values=("16","lala", "2"))
        #tv.insert("",END,text="AQceite", values=("34","lala", "3"))
        tv.place(x=20, y=180, width=510, height=130)

        # frame para scrollbar de tabla inicial

        p_aux =Frame(self)
        p_aux.place(x=530,y=180, width=20, height=130)

        # scrollbar de tabla inicial

        scroll_syn = Scrollbar(p_aux)
        scroll_syn.pack(side='right', fill='y')
        scroll_syn.config(command = tv.yview )

        # tabla forward

        tv1 = ttk.Treeview(self, columns=("col1","col2"))
        tv1.column("#0",width=30)
        tv1.column("col1",width=30, anchor=CENTER)
        tv1.column("col2",width=150, anchor=CENTER)

        tv1.heading("#0", text="Identificador", anchor=CENTER)
        tv1.heading("col1", text="EarlyFinish", anchor=CENTER)
        tv1.heading("col2", text="EarlyStart", anchor=CENTER)

        #tv1.insert("",END,text="A", values=("28","2"))
        #tv1.insert("",END,text="B", values=("16","3"))
        #tv1.insert("",END,text="C", values=("34","1"))
        tv1.place(x=20, y= 345, width=510, height=130)
        
        # tabla backward

        tv2 = ttk.Treeview(self, columns=("col1","col2", "col3"))
        tv2.column("#0",width=30)
        tv2.column("col1",width=30, anchor=CENTER)
        tv2.column("col2",width=150, anchor=CENTER)
        tv2.column("col3",width=50, anchor=CENTER)

        tv2.heading("#0", text="Identificador", anchor=CENTER)
        tv2.heading("col1", text="LateStart", anchor=CENTER)
        tv2.heading("col2", text="LateFinish", anchor=CENTER)
        tv2.heading("col3", text="Slack", anchor=CENTER)

        #tv2.insert("",END,text="A", values=("28","2", "0"))
        #tv2.insert("",END,text="B", values=("16","3", "0"))
        #tv2.insert("",END,text="C", values=("34","1", "0"))
        tv2.place(x=20, y=510, width=510, height=130)

        # frame para scrollbar syn de tablas for y back

        p_aux2 =Frame(self)
        p_aux2.place(x=530,y=345, width=20, height=295)

        # funcion syncro-scroll

        def  multiple_yview(*args):
            tv1.yview(*args)
            tv2.yview(*args)

        # scrollbar syn de tablas for y back 

        scroll_syn = Scrollbar(p_aux2)
        scroll_syn.pack(side='right', fill='y')
        scroll_syn.config(command = multiple_yview )

        

        def borrar():
            txt_pre.delete(0, "end")
            txt_id.delete(0, "end")
            txt_du.delete(0, "end")
            txt_des.delete(0, "end")


        # buttons

        self.btnA=Button(self,text="Agregar"
            ,command=lambda: [self.recolectarInput(txt_id,txt_des,txt_du,txt_pre,tv, self.opciones), cmb_pre.config(values= self.opciones), borrar()], state = DISABLED)
        self.btnA.place(x=430,y=110, width=100)

        self.btnRC=Button(self,text="Pert CMP / Ruta Crítica"
            ,command=lambda: [self.llenarTablas(llenadoTabla,tv1,tv2)
                ,self.llenarTextbox(txt_existeRC,txt_RC,txt_holgura,txt_contador,txt_listaHolgura), self.btnRC.config(state =DISABLED)])
        self.btnRC.place(x=590,y=110, width=190)

        self.btnExcel=Button(self,text="Archivo Excel",command=lambda: self.cargarArchivo(excel,tv) and rbt_manual.config(state=DISABLED), state = DISABLED)
        self.btnExcel.place(x=430,y=10, width=100) 

      

        def actualiza(opcion):	

            if opcion == 1:
                self.btnExcel.configure(state= DISABLED)  
                self.btnA.configure(state= NORMAL)   
                txt_id.configure(state= NORMAL)
                txt_du.configure(state= NORMAL)
                cmb_pre.configure(state= 'readonly')
                txt_des.configure(state= NORMAL)

                txt_pre.configure(state= NORMAL)
               
                    
            
            else:
                self.btnExcel.configure(state= NORMAL)  
                self.btnA.configure(state= DISABLED)                
                txt_id.configure(state= DISABLED)
                txt_du.configure(state= DISABLED)
                txt_des.configure(state= DISABLED)
                cmb_pre.configure(state= DISABLED)
                txt_pre.configure(state= DISABLED)
               
               


            
     
