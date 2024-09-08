from matplotlib import pyplot as plt
from matplotlib.widgets import Button

def plot_positions_gui(positions):

    fig, (ax_pie,  ax_bar) = plt.subplots(1,2)
    fig.suptitle(f'Fidelity Portfolio Breakdown (${round(sum(positions.values()), 2)})')

    class PlotSort:
        is_alpha   = False
        is_numeric = False

        def __init__(self, positions):
            self.positions_numeric = {k:v for (k,v) in sorted(positions.items(), key=lambda x:x[1])}
            self.positions_alpha   = {k:v for (k,v) in sorted(positions.items(), key=lambda x:x[0], reverse=True)}
            self.total_value       = sum(positions.values())
            self.update_plot(positions)

        def alpha(self, event):
            if self.is_alpha:
                return  
            self.is_alpha   = True
            self.is_numeric = False
            self.update_plot(self.positions_alpha)
        
        def numeric(self, event):
            if self.is_numeric:
                return  
            self.is_alpha   = False
            self.is_numeric = True
            self.update_plot(self.positions_numeric)

        def update_plot(self, positions):
            ax_pie.clear()
            ax_pie.pie(positions.values(), labels=positions.keys())
            ax_bar.clear()
            ax_bar.barh(list(positions.keys()), positions.values())
            ax_bar.set_xlabel('Value USD')
            ax_bar.set_ylabel('Ticker')
            for bar, val in zip(ax_bar.patches, positions.values()):
                width  = bar.get_width()
                height = bar.get_height()
                x, y   = bar.get_xy()
                ax_bar.text(x+width+40,
                        y+height/2,
                        str(round(val/self.total_value*100, 2))+'%',
                        ha='center', 
                        va='center')
            plt.draw()


    callback    = PlotSort(positions)
    ax_aplha    = fig.add_axes([0.05, 0.05, 0.1, 0.075])
    ax_numeric  = fig.add_axes([0.16, 0.05, 0.1, 0.075])
    btn_alpha   = Button(ax_aplha, 'Alphabetical')
    btn_numeric = Button(ax_numeric, 'Numeric')
    btn_alpha.on_clicked(callback.alpha)
    btn_numeric.on_clicked(callback.numeric)

    plt.show()