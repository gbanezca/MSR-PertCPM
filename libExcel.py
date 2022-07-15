from tkinter import * 
from tkinter import  messagebox
import pandas as pd
from tkinter import filedialog
from collections import namedtuple

class Excel:     

    def abrir_archivo():
        aux = 0
        infiles = ""
        excel = True
        df = ''

        while excel:
            try:
                # open the window to select the file
                messagebox.showinfo(title="Información", message = "Recuerde que el archivo excel debe tener cuatro columnas con identificacion|descripcion|duracion|predecesor")
                
                infiles = filedialog.askopenfilename(multiple=True)

                if (infiles == ""):
                    break

                # validate if it is an excel file
                if(str(infiles[0]).endswith('.xls') or str(infiles[0]).endswith('.xlsx')):
                    archivo = infiles[0]

                    # creating the dataframe
                    data = pd.ExcelFile(archivo)
                    df = data.parse()

                    # the file must have four columns
                    if(df.shape[1] != 4):
                        messagebox.showinfo(title="Advertencia", message = "El archivo no cuenta con las cuatro columnas, porfavor seleccione un archivo nuevo")
                        continue
                    else:
                        for i in range(df.shape[0]):
                            if(isinstance(df["duracion"][i], str)):
                                aux = 1
                                break
                        if(aux == 1):                        
                            messagebox.showinfo(title="Advertencia", message = "Las duraciones deben ser numeros enteros")
                            continue
                        else:
                            break

                else:
                    messagebox.showinfo(title="Advertencia", message = "El archivo debe ser un archivo Excel")        
                    continue
            except ValueError:
                messagebox.showinfo(title="Advertencia", message = "El archivo debe ser un archivo Excel")                 
                continue  
        data = namedtuple("data", ["df", "infiles"])
        return data(
            df,
            infiles,
        )
            
    
    
    

    
  