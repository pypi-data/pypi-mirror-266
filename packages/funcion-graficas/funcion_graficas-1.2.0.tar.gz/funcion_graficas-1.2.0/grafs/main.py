import matplotlib.pyplot as plt
from matplotlib.ticker import (AutoMinorLocator)

def graficar(x,y,titulo="",nombre_eje_x="",nombre_eje_y="",nombre_archivo="Grafica"):
    fig,ax = plt.subplots(dpi=1200)
    ax.plot(x,y)
    if titulo != "":
        ax.set_title(titulo,fontsize=16)
        ax.set_xlabel(nombre_eje_x,fontsize=14)
        ax.set_ylabel(nombre_eje_y,fontsize=14)
    ax.grid(True,'major',linewidth=1.5)
    ax.grid(True,'minor',linewidth=0.5)
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.tick_params(which='major', width=2)
    ax.tick_params(which='minor', width=1.2)
    ax.tick_params(which='major', length=9)
    ax.tick_params(which='minor', length=4)
    plt.xlim([x[0],x[-1]])
    archivo = nombre_archivo + ".png"
    plt.savefig(archivo)
    
def graficas_multiples(titulo,nombre_eje_x,nombre_eje_y,nombre_archivo,x_1,y_1,nombre_1,x_2,y_2,nombre_2,x_3=0,y_3=0,nombre_3="",x_4=0,y_4=0,nombre_4="",x_5=0,y_5=0,nombre_5=""):
    fig,ax = plt.subplots(dpi=1200)
    ax.plot(x_1,y_1,label=nombre_1)
    ax.plot(x_2,y_2,label=nombre_2)
    if x_3 != 0 and y_3 != 0:
        ax.plot(x_3,y_3,label=nombre_3)
        if x_4 != 0 and y_4 != 0:
            ax.plot(x_4,y_4,label=nombre_4)
            if x_5 != 0 and y_5 != 0:
                ax.plot(x_5,y_5,label=nombre_5)
    ax.set_title(titulo,fontsize=16)
    ax.set_xlabel(nombre_eje_x,fontsize=14)
    ax.set_ylabel(nombre_eje_y,fontsize=14)
    ax.grid(True,'major',linewidth=1.5)
    ax.grid(True,'minor',linewidth=0.5)
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.tick_params(which='major', width=2)
    ax.tick_params(which='minor', width=1.2)
    ax.tick_params(which='major', length=9)
    ax.tick_params(which='minor', length=4)
    if x_3 == 0 or y_3 == 0:
        plt.xlim([min([x_1[0],x_2[0]]),max([x_1[-1],x_2[-1]])])
    elif x_4 == 0 or y_4 == 0:
        plt.xlim([min([x_1[0],x_2[0],x_3[0]]),max([x_1[-1],x_2[-1],x_3[-1]])])
    elif x_5 == 0 or y_5 == 0:
        plt.xlim([min([x_1[0],x_2[0],x_3[0],x_4[0]]),max([x_1[-1],x_2[-1],x_3[-1],x_4[-1]])])
    else:
        plt.xlim([min([x_1[0],x_2[0],x_3[0],x_4[0],x_5[0]]),max([x_1[-1],x_2[-1],x_3[-1],x_4[-1],x_5[-1]])])

    plt.legend()
    archivo = nombre_archivo + ".png"
    plt.savefig(archivo)