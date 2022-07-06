import tkinter
import tkinter.filedialog as fd
import tkinter.font as TkFont
import os
from pathlib import Path
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "serif"
import numpy as np
from tkinter import ttk
from seaborn import heatmap
import platform
import pandas
from paths import datapath, nanosight_app_path_results as resultspath

from ML_tools.clustering_functions import plot_clustering_results, plot_paired_matrix
from ML_tools.hierarchical_clustering import colors_dendrogram, run_hierarchical_clustering, plot_hierarchical_clustering
from ML_tools.distance_matrix_computation import compute_distance_matrix_distribs, compute_distance_matrix, \
                    compute_test_diff_matrix_distribs, compute_distance_matrix_mixte_wasserstein_euclidean

from nanosight.extract_nanosight_measures import extract_nanosight_experiment_measures
from nanosight.plot_nanosight import plot_nanosight_size_distribution, plot_nanosight_size_densities, plot_nanosight_size_distribution_replicates
from app_tools import get_replicates, create_missing_dir




### Set app parameters

bg_color = "peachpuff"
max_display = 30

ratio_padx = 1 if platform.system() == 'Linux' else 1
ratio_pady = 1 if platform.system() == 'Linux' else 0.5




class App():
        
    def __init__(self, data_dir="", autosampler=False,  
                       dilution_prefix="dil", replicate_prefix="rep",
                       group_replicates=False):

        self.data_dir = data_dir
        self.autosampler=autosampler
        self.dilution_prefix=dilution_prefix
        self.replicate_prefix = replicate_prefix
        self.group_replicates = group_replicates

        self.name_experiments = None
        
        self.name_data_directory = os.path.basename(data_dir)

        self.export_dir = self.name_data_directory
        
        
    
    def run_graphical_interface(self):
        
        self.manual = False
    
        self.root = tkinter.Tk()
        self.root.resizable(width=False, height=False)        

        self.root.grid_rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)
        

        
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        self.root.title("Nanosight data analysis")
        self.root.configure(background=bg_color)

        self.load_data_frame = tkinter.LabelFrame(self.root, text="Load Nanosight data", font = TkFont.Font(weight="bold"))
        self.load_data_frame.configure(background=bg_color)
        
        self.load_data_frame.grid(row = 0, column = 0, pady=20*ratio_pady, padx=20*ratio_padx, sticky="ns")

        self.name_data_directory_tkinter_var = tkinter.StringVar(self.root)
        # self.dirname_nanosight = tkinter.StringVar(self.root)

        self.autosampler_tkinter_var = tkinter.BooleanVar(self.root)
        self.group_replicates_tkinter_var = tkinter.BooleanVar(self.root)
        
        self.replicate_prefix_tkinter_var = tkinter.StringVar(self.root, value="rep")
        
        self.export_dirname = tkinter.StringVar(self.root, value=None)
        self.dilution_prefix_tkinter_var = tkinter.StringVar(self.root, value="dil")

        width_load_data_frame = self.load_data_frame.winfo_width()
        
        
        
        
             
   
        def ask_data_directory():
            title = 'Choose nanosight data directory'
            entry = tkinter.filedialog.askdirectory(title=title, initialdir=datapath)
            
            self.data_dir = entry

            self.name_data_directory = os.path.basename(entry)
            
            self.name_data_directory_tkinter_var.set(self.name_data_directory)
            
            self.export_dir = self.name_data_directory




        num = tkinter.Label(self.load_data_frame, text="1.", bg=bg_color, fg="black")
        num.grid(column=0, row=1)
        num = tkinter.Label(self.load_data_frame, text="2.", bg=bg_color, fg="black")
        num.grid(column=0, row=2)
        num = tkinter.Label(self.load_data_frame, text="3.", bg=bg_color, fg="black")
        num.grid(column=0, row=3)

             
        button_chose_path = tkinter.Button(self.load_data_frame, text = "Choose directory", command = ask_data_directory, bg=bg_color, fg="black")
        button_chose_path.grid(column=1, row=1, pady=40*ratio_pady, padx=10*ratio_padx)
        
        
        chosen_directory = tkinter.Label(self.load_data_frame, textvariable=self.name_data_directory_tkinter_var, background=bg_color, fg="orangered")
        chosen_directory.grid(column=2, row=1, pady=40*ratio_pady, padx=50*ratio_padx)


        autosampler_title = tkinter.Label(self.load_data_frame, text="Autosampler export ?", bg=bg_color, fg="black")
        autosampler_title.grid(column=1, row=2, pady=40*ratio_pady)
        
        check_autosampler = tkinter.Checkbutton(self.load_data_frame, text="Yes", variable=self.autosampler_tkinter_var, bg=bg_color)
        check_autosampler.grid(column=2, row=2, pady=40*ratio_pady)

        dilution_title = tkinter.Label(self.load_data_frame, text="Dilution prefix", bg=bg_color, fg="black")
        dilution_title.grid(column=1, row=3, pady=40*ratio_pady)
        
        dilution_choose = tkinter.Entry(self.load_data_frame, textvariable=self.dilution_prefix_tkinter_var)
        dilution_choose.grid(column=2, row=3, pady=40*ratio_pady)

        replicate_title = tkinter.Label(self.load_data_frame, text="Replicate prefix", bg=bg_color, fg="black")
        replicate_title.grid(column=1, row=4, pady=40*ratio_pady)
        
        replicate_choose = tkinter.Entry(self.load_data_frame, textvariable=self.replicate_prefix_tkinter_var)
        replicate_choose.grid(column=2, row=4, pady=40*ratio_pady)


        button_export_nanosight = tkinter.Button(self.load_data_frame, text = "Load" , command = self.load_nanosight, bg="white", fg="black")
        button_export_nanosight.grid(row=6, columnspan=3, column=0, pady=40*ratio_pady)

        """"""""""""""""""""""""""
        """%%%%%%%%%%%%%%%%%"""
        """"""""""""""""""""""""""


        tkinter.mainloop()
 
        
        
    
    
    def run_manual(self):
        
        self.manual = True
        self.load_nanosight()

        
        
    

    def export_nanosight(self):

                
        if hasattr(self, 'ok_export'):
            self.ok_export.destroy()


        to_save = self.table_concentration_distributions.copy()
        
        to_save = to_save[[col for col in to_save if "Raw" not in col]]
        
        cols = ["Bin centre (nm)"]
                        
        for name in self.name_experiments:
            new_cols = ["Concentration average "+name, "Standard deviation "+name]
            new_cols += ["Concentration (particles / ml) Video "+str(k)+" "+name for k in np.arange(1,6)]
            
            cols += new_cols
            
        for shorted_name in list(self.replicates.keys()):
            
            cols += ["Concentration average "+shorted_name, "Standard deviation "+shorted_name]
            
            
        to_save = to_save[cols]
        
        to_save.columns = [col.replace(" (particles / ml)","") for col in to_save.columns]
        
        to_save.to_csv(Path(resultspath, self.export_dir, "csv", "Results_nanosight_concentration.csv"))
            



        if not self.manual:    
            self.ok_export = tkinter.Label(self.analysis_frame, text = "Ok", bg=bg_color, fg="orangered")
            self.ok_export.grid(row=1, column=1, pady=40*ratio_pady, padx=20*ratio_padx)


    def plot_nanosight_distributions(self):

                
        if hasattr(self, 'ok_plot'):
            self.ok_plot.destroy()

        path_to_save = Path(resultspath, self.export_dir)

        if not os.path.exists(resultspath):
            os.mkdir(Path(resultspath))

        if not os.path.exists(path_to_save):
            os.mkdir(Path(path_to_save))
        
        if not os.path.exists(Path(path_to_save, "distributions_figures")):
            os.mkdir(Path(path_to_save, "distributions_figures"))

        for i, name in enumerate(self.name_experiments):

            plot_nanosight_size_distribution(self.table_concentration_distributions, name, save_path_fig = Path(path_to_save, "distributions_figures", "nanosight_size_concentration_"+name+".png"))
            # plot_nanosight_size_densities(self.table_concentration_distributions, name, save_path_fig = Path(path_to_save, "distributions_figures", "nanosight_size_density_"+name+".png"))
   
        for i, shorted_name in enumerate(list(self.replicates.keys())):
            
            
            cols_video = [col for col in self.table_concentration_distributions if "Video" in col and shorted_name in col and "Raw" not in col]

            self.table_concentration_distributions["Concentration average "+shorted_name] = self.table_concentration_distributions[cols_video].mean(axis=1)
            self.table_concentration_distributions["Standard error "+shorted_name] = self.table_concentration_distributions[cols_video].std(axis=1) / np.sqrt(len(cols_video))

            if np.sum([True if "Raw "+col in self.table_concentration_distributions.columns else False for col in cols_video])==len(cols_video):
                self.table_concentration_distributions["Raw Concentration average "+shorted_name] = self.table_concentration_distributions[["Raw "+col for col in cols_video]].mean(axis=1)
                self.table_concentration_distributions["Raw Standard error "+shorted_name] = self.table_concentration_distributions[["Raw "+col for col in cols_video]].std(axis=1) / np.sqrt(len(cols_video))
            
            plot_nanosight_size_distribution_replicates(self.table_concentration_distributions, shorted_name, replicate_names=self.replicates[shorted_name], save_path_fig = Path(path_to_save, "distributions_figures", shorted_name+".png"))

        if not self.manual:    
            self.ok_plot = tkinter.Label(self.analysis_frame, text = "Ok", bg=bg_color, fg="orangered")
            self.ok_plot.grid(row=2, column=1, pady=40*ratio_pady, padx=20*ratio_padx)
    

    def set_group_replicates(self):
        
        self.group_replicates = self.group_replicates_tkinter_var.get()

    def load_nanosight(self):

        
        create_missing_dir([resultspath, self.export_dir, "csv"])

        
        if not self.manual:

            if hasattr(self, 'list_experiments_frame'):
                self.list_experiments_frame.destroy()
    
            if hasattr(self, 'analysis_frame'):
                self.analysis_frame.destroy()
                
            if hasattr(self, "data_correctly_loaded"):
                self.data_correctly_loaded.destroy()
                
            self.dilution_prefix = self.dilution_prefix_tkinter_var.get()
            self.autosampler = self.autosampler_tkinter_var.get()
            self.replicate_prefix = self.replicate_prefix_tkinter_var.get()
     


        if self.data_dir is not None:
            
            self.name_experiments, self.table_concentration_distributions, self.total_concentrations, self.dilutions, self.reliable_results = extract_nanosight_experiment_measures(Path(datapath, self.data_dir), 
                                                                                                                                            dilution_prefix=self.dilution_prefix, 
                                                                                                                                            autosampler=self.autosampler) 

            self.particles_per_frame = [", ".join(["%.1f"%(self.reliable_results.loc[name]["Video "+str(k)]) for k in range(1,6)]) for name in self.name_experiments]

            self.replicates = get_replicates(self.name_experiments, replicate_prefix = self.replicate_prefix)
            
            self.replicates_exist = np.sum([len(v)>1 for k,v in self.replicates.items()])
            
            if not self.manual :
                self.data_correctly_loaded = tkinter.Label(self.load_data_frame, text = "Data correctly loaded", bg=bg_color, fg="orangered")
                self.data_correctly_loaded.grid(row=7, columnspan=3, column=0, pady=10*ratio_pady)

                
                self.list_experiments_frame = tkinter.LabelFrame(self.root, text="List of samples", font = TkFont.Font(weight="bold"), bg=bg_color)
                self.list_experiments_frame.grid(row=0, column=1, sticky='news', padx=40*ratio_padx, pady=20*ratio_pady)

                frame_canvas = tkinter.Frame(self.list_experiments_frame)
                frame_canvas.grid(row=2, column=0, pady=(5, 0), sticky='nw')
                frame_canvas.grid_rowconfigure(0, weight=1)
                frame_canvas.grid_columnconfigure(0, weight=1)
                # Set grid_propagate to False to allow 5-by-5 buttons resizing later
                frame_canvas.grid_propagate(False)
                
                # Add a canvas in that frame
                canvas = tkinter.Canvas(frame_canvas, bg="yellow")
                canvas.grid(row=0, column=0, sticky="news")
                
                # Link a scrollbar to the canvas
                vsb = tkinter.Scrollbar(frame_canvas, orient="vertical", command=canvas.yview)
                vsb.grid(row=0, column=3, sticky='ns', rowspan=len(self.name_experiments)+1)
                canvas.config(yscrollcommand=vsb.set, bg=bg_color)
                
                # Create a frame to contain the buttons
                frame_buttons = tkinter.Frame(canvas, bg=bg_color)
                canvas.create_window((0, 0), window=frame_buttons, anchor='nw')


                # Set the canvas scrolling region
                canvas.config(scrollregion=canvas.bbox("all"))
                

                max_display = 30

                samples_list = []

                names_title = tkinter.Label(frame_buttons, text = "Name", bg=bg_color, fg="black")
                names_title.grid(row=0, column=0, pady=40*ratio_pady)
                
                dilutions_title = tkinter.Label(frame_buttons, text = "Dilution", bg=bg_color, fg="black")
                dilutions_title.grid(row=0, column=1, pady=40*ratio_pady, padx=30*ratio_padx)

                particles_per_frame_title = tkinter.Label(frame_buttons, text = "Particles per frame", bg=bg_color, fg="black")
                particles_per_frame_title.grid(row=0, column=2, pady=40*ratio_pady, padx=30*ratio_padx)



                
                # for i in range(len(self.name_experiments)):
                #     name = self.name_experiments[i]
                #     dilution = self.dilutions[i]
                #     particles_per_frame = self.particles_per_frame[i]

                #     samples_list.append([name, dilution, particles_per_frame])
  
                #     name_label = tkinter.Label(frame_buttons, text = name, bg=bg_color, fg="black")
                #     name_label.grid(row=1+i, column=0, pady=2*ratio_pady)
                    
                #     dilution_label = tkinter.Label(frame_buttons, text = str(dilution), bg=bg_color, fg="black")
                #     dilution_label.grid(row=1+i, column=1, pady=2*ratio_pady, padx=30*ratio_padx)

                #     particle_per_frame_label = tkinter.Label(frame_buttons, text = particles_per_frame, bg=bg_color, fg="black")
                #     particle_per_frame_label.grid(row=1+i, column=2, pady=2*ratio_pady, padx=30*ratio_padx)
                    

                
                for k in range(len(self.replicates)):
                    
                    short_name = list(self.replicates.keys())[k]
                    exp = self.replicates[short_name]

                    for j in range(len(exp)):
                                                                    
                        name = exp[j]
                        index = self.name_experiments.index(name)
                        dilution = self.dilutions[index]
                        particles_per_frame = self.particles_per_frame[index]
    
                        samples_list.append([name, dilution, particles_per_frame])
      
                        name_label = tkinter.Label(frame_buttons, text = name, bg=bg_color, fg="black")
                        name_label.grid(row=1+index+k, column=0, pady=2*ratio_pady)
                        
                        dilution_label = tkinter.Label(frame_buttons, text = str(dilution), bg=bg_color, fg="black")
                        dilution_label.grid(row=1+index+k, column=1, pady=2*ratio_pady, padx=30*ratio_padx)
    
                        particle_per_frame_label = tkinter.Label(frame_buttons, text = particles_per_frame, bg=bg_color, fg="black")
                        particle_per_frame_label.grid(row=1+index+k, column=2, pady=2*ratio_pady, padx=30*ratio_padx)
                        
                        print(1+index+k)
                        
                        if j == len(exp)-1:
                            
                            space = tkinter.Label(frame_buttons, text="", bg=bg_color)
                            space.grid(row = 2+index+k, column=2, pady=2*ratio_pady, padx=30*ratio_padx)
                            
                            print(2+index+(k))
                            

                    
                        
                                            
                    

                        
                frame_buttons.update_idletasks()

                
                width2 = frame_buttons.winfo_reqwidth() 
                height2 = frame_buttons.winfo_reqheight()
                
                
                ratio = 0.8
                
                frame_canvas.config(width=width2 , height=min(height2, ratio*self.screen_height))
                canvas.config(scrollregion=canvas.bbox("all"))
                
                                
                   
           
                samples_list = pandas.DataFrame(np.array(samples_list), columns= ["name", "dilution", "particles per frame"])
                
                samples_list.to_csv(Path(resultspath, self.export_dir, "csv", "samples_list.csv"))
               
                self.analysis_frame = tkinter.LabelFrame(self.root, text="Analysis", font = TkFont.Font(weight="bold"))
                self.analysis_frame.configure(background=bg_color)
                self.analysis_frame.grid(row = 0, column = 2, sticky="N", padx=20*ratio_padx, pady=20*ratio_pady)
    
                button_export = tkinter.Button(self.analysis_frame, text = "Export excel" , command = self.export_nanosight, bg="white", fg="black")
                button_export.grid(row=1, column=0, pady=40*ratio_pady, padx=20*ratio_padx)
                
                button_launch_analysis = tkinter.Button(self.analysis_frame, text = "Plot distributions" , command = self.plot_nanosight_distributions, bg="white", fg="black")
                button_launch_analysis.grid(row=2, column=0, pady=40*ratio_pady, padx=20*ratio_padx)
                
                
                start = 3
                

                if self.replicates_exist:
                    check_group_replicates = tkinter.Checkbutton(self.analysis_frame, text="Group replicates", variable=self.group_replicates_tkinter_var, command=self.set_group_replicates, bg=bg_color)
                    check_group_replicates.grid(column=0, row=3, pady=40*ratio_pady)
                    start = 4

                button_launch_analysis = tkinter.Button(self.analysis_frame, text = "Clustering normalized distributions" , command = self.run_clustering_normalized_nanosight_size_concentration_distributions_wasserstein, bg="white", fg="black")
                button_launch_analysis.grid(row=start, column=0, pady=40*ratio_pady, padx=20*ratio_padx)
                
                button_launch_analysis = tkinter.Button(self.analysis_frame, text = "Clustering total concentrations" , command = self.run_clustering_total_concentration_nanosight, bg="white", fg="black")
                button_launch_analysis.grid(row=start+1, column=0, pady=40*ratio_pady, padx=20*ratio_padx)
                       
                button_launch_analysis = tkinter.Button(self.analysis_frame, text = "Statistical test between normalized distributions" , command = self.plot_nanosight_kolmogorov_test_matrix, bg="white", fg="black")
                button_launch_analysis.grid(row=start+2, column=0, pady=40*ratio_pady, padx=20*ratio_padx)
                
                
                results = []
                        
                for i, shorted_name in enumerate(list(self.replicates.keys())):
                    
                    cols_video = [col for col in self.table_concentration_distributions if "Video" in col and shorted_name in col and "Raw" not in col]
        
                    self.table_concentration_distributions["Concentration average "+shorted_name] = self.table_concentration_distributions[cols_video].mean(axis=1)
                    self.table_concentration_distributions["Standard deviation "+shorted_name] = self.table_concentration_distributions[cols_video].std(axis=1)# / np.sqrt(len(cols_video))
                    
                    
                    subtable_concentration = self.total_concentrations.loc[[col for col in self.total_concentrations.index if shorted_name in col]]
                    subtable_concentration = subtable_concentration[[col for col in subtable_concentration.columns if "Video" in col]]

                    
                    subtable_concentration_mean = subtable_concentration.mean(axis=1).mean()
                    
                    subtable_concentration_std = subtable_concentration.std(axis=1).std()
                    
                    
                    results.append([subtable_concentration_mean, subtable_concentration_std])
                    
                    
                self.total_concentrations_replicates = pandas.DataFrame(np.array(results), index=list(self.replicates.keys()), columns=["Average Concentration (Particles / ml)", "Standard Deviation" ])

                                                
                


                
    def run_clustering_normalized_nanosight_size_concentration_distributions_wasserstein(self, keys=None):

        
        if not self.manual:
            if hasattr(self, 'ok_normalized_clustering'):
                self.ok_normalized_clustering.destroy()
                

        create_missing_dir([resultspath, self.export_dir, "clustering", "normalized_distributions"])   
                    
        if self.group_replicates is True:
            list_names = list(self.replicates.keys())
            
        else:
            list_names = self.name_experiments
        
        
        cols_concentration = ["Concentration average "+name for name in list_names]

        list_distribs = [self.table_concentration_distributions[col] for col in cols_concentration]
        bin_centers = self.table_concentration_distributions["Bin centre (nm)"].values
        
        fig, ax = plt.subplots(1)

        distance_matrix_dataframe = compute_distance_matrix_distribs(list_distribs, bin_centers, distance="Wasserstein", normalized=True, list_names=list_names, ax=ax)


        results_clustering = run_hierarchical_clustering(distance_matrix_dataframe, 
                                             metric="precomputed",                                                                                 
                                             labelsize=14,
                                             linkage_method="complete",
                                             optimize=True)

        title = "Wasserstein_normalized_size_distribution_nanosight"


        plot_hierarchical_clustering(distance_matrix_dataframe, results_clustering, labelsize=13,
                                 path_to_save_fig = Path(resultspath, self.export_dir, "clustering", "normalized_distributions"), 
                                 title=title+".pdf")

        plot_clustering_results(list_distribs, 
                                bin_centers, 
                                results_clustering["labels"], 
                                list_names=list_names, 
                                normalized=True,
                                path_to_save = Path(resultspath, self.export_dir, "clustering", "normalized_distributions"), title="hierarchical_clustering_"+title)


        if not self.manual:    
            self.ok_normalized_clustering = tkinter.Label(self.analysis_frame, text = "Ok", bg=bg_color, fg="orangered")
            
            if self.replicates_exist:
                start = 4
            else:
                start = 3
            self.ok_normalized_clustering.grid(row=start, column=1, pady=40*ratio_pady, padx=20*ratio_padx)
    




    def _plot_nanosight_test_matrix(self, test):

                
        if hasattr(self, 'ok_stat_tests'):
            self.ok_stat_tests.destroy()

        create_missing_dir([resultspath, self.export_dir, "test_normalized_distributions"])


        if self.group_replicates is True:
            list_names = list(self.replicates.keys())
            
        else:
            list_names = self.name_experiments
        

        cols_concentration = ["Concentration average "+name for name in list_names]
        list_distribs = [self.table_concentration_distributions[col] for col in cols_concentration]
        bin_centers = self.table_concentration_distributions["Bin centre (nm)"].values

        distance_matrix_dataframe = compute_test_diff_matrix_distribs(list_distribs, bin_centers, test=test, normalized=True, list_names=list_names)
                
        plot_paired_matrix(distance_matrix_dataframe, path_to_save_fig=Path(resultspath, self.export_dir, "test_normalized_distributions"), title=test+"_statistical_test_normalized_distribution")

        distance_matrix_dataframe.to_csv(Path(resultspath, self.export_dir, "test_normalized_distributions", test+"_statistical_test_normalized_distribution"))

        if not self.manual:    
            self.ok_stat_tests = tkinter.Label(self.analysis_frame, text = "Ok", bg=bg_color, fg="orangered")
            
            if self.replicates_exist:
                start = 4
            else:
                start = 3
            self.ok_stat_tests.grid(row=start+2, column=1, pady=40*ratio_pady, padx=20*ratio_padx)
    


    def plot_nanosight_kolmogorov_test_matrix(self):

        self._plot_nanosight_test_matrix("Kolmogorov")




    def run_clustering_total_concentration_nanosight(self):


        
        if hasattr(self, 'ok_concentration_clustering'):
            self.ok_concentration_clustering.destroy()
        
        create_missing_dir([resultspath, self.export_dir, "clustering", "total_concentration"])

        if self.group_replicates is True:
            list_names = list(self.replicates.keys())
            
            
            list_concentrations = [self.total_concentrations_replicates["Average Concentration (Particles / ml)"][name] for name in list_names]
            
            
        else:
            list_names = self.name_experiments
        

            list_concentrations = [self.total_concentrations["Average Concentration (Particles / ml)"][name] for name in list_names]

        distance_matrix_dataframe = compute_distance_matrix(list_concentrations, distance="euclidean", list_names=list_names)

        results_clustering = run_hierarchical_clustering(distance_matrix_dataframe, 
                                             metric="precomputed",                                                                                 
                                             labelsize=14,
                                             linkage_method="complete",
                                             optimize=True)


        plot_hierarchical_clustering(distance_matrix_dataframe, results_clustering, labelsize=13,
                                 path_to_save_fig = Path(resultspath, self.export_dir, "clustering", "total_concentration"), 
                                 title="total_concentration_nanosight.pdf")

        fig, ax = plt.subplots(1, figsize=(20,15))

        ordered_list_index = np.array(list_concentrations).argsort()
        
        ordered_colors = [colors_dendrogram[l-1]  if np.sum(results_clustering["labels"]==l)>1 else "black"
                          for l in results_clustering["labels"][ordered_list_index]]
        
        ordered_list_concentrations = np.array(list_concentrations)[ordered_list_index]
        ordered_name_exp = np.array(list_names)[ordered_list_index]
        ax.bar(x=np.arange(len(ordered_list_concentrations)), height=ordered_list_concentrations, color=ordered_colors)#, labels=ordered_name_exp)#, marker=".", s=30)
        ax.set_xticks(np.arange(len(ordered_list_concentrations)))
        ax.set_xticklabels(ordered_name_exp, fontsize=13, rotation=45, rotation_mode="anchor", ha="right")
        fig.tight_layout()
        
        
        
        fig.savefig(Path(resultspath, self.export_dir, "clustering", "total_concentration", "total_concentration_nanosight.pdf"))

        plt.close(fig)

        if not self.manual:    
            self.ok_concentration_clustering = tkinter.Label(self.analysis_frame, text = "Ok", bg=bg_color, fg="orangered")

            if self.replicates_exist:
                start = 4
            else:
                start = 3
            self.ok_concentration_clustering.grid(row=start+1, column=1, pady=40*ratio_pady, padx=20*ratio_padx)
    






    def run_clustering_emd(self):

        create_missing_dir([resultspath, self.export_dir, "clustering"])

        
        cols_concentration = ["Concentration average "+name for name in self.name_experiments]
        list_distribs = [self.table_concentration_distributions[col] for col in cols_concentration]
        bin_centers = self.table_concentration_distributions["Bin centre (nm)"].values
        bin_diffs = np.array([bin_centers[0]*2] + list(bin_centers[1:] - bin_centers[:-1]))
        bins =  [0] + list(bin_centers + bin_diffs/2)
        
        list_area = [np.sum(distrib * bin_diffs) for distrib in list_distribs]
        normalized_distribs = [distrib / list_area[u] for u, distrib in enumerate(list_distribs)]
 
        list_concentrations = self.total_concentrations["Average Concentration (Particles / ml)"].values
           

        
 
        names = self.name_experiments

        


        distance_matrix, index_, labels, silhouette = hierarchical_clustering_distrib_list(list_distribs,
                                                                         bin_centers,
                                                                         names, 
                                                                         distance="emd",
                                                                         labelsize=14,
                                                                         linkage_method="complete",
                                                                         criterion="maxclust",
                                                                         maxclust=int(len(list_distribs)/5),
                                                                         path_to_save_fig = Path(resultspath, self.export_dir, "clustering", "hierarchical_clustering_"+"area.pdf"))
                            #          

        
        plot_clustering_results(list_distribs, 
                                bin_centers, 
                                labels, 
                                list_names=names, 
                                path_to_save = Path(resultspath, self.export_dir, "clustering", "hierarchical_clustering_interpretation_"+"area.pdf"))
        
 


    def run_clustering_combined_distances_nanosight(self):
 

        create_missing_dir([resultspath, self.export_dir, "clustering", "combined_distances"])

        
        cols_concentration = ["Concentration average "+name for name in self.name_experiments]
        list_distribs = [self.table_concentration_distributions[col] for col in cols_concentration]
        bin_centers = self.table_concentration_distributions["Bin centre (nm)"].values

        list_concentrations = [self.total_concentrations["Average Concentration (Particles / ml)"][name] for name in self.name_experiments]

        distance_matrix_dataframe = compute_distance_matrix_mixte_wasserstein_euclidean(list_distribs, bin_centers, list_concentrations, list_names=self.videodrop_name_experiments)

        results_clustering = run_hierarchical_clustering(distance_matrix_dataframe, 
                                             metric="precomputed",                                                                                 
                                             labelsize=14,
                                             linkage_method="complete",
                                             optimize=True)

        title = "combined_distances_size_distribution_nanosight"

        results_clustering = run_hierarchical_clustering(distance_matrix_dataframe, 
                                             metric="precomputed",                                                                                 
                                             labelsize=14,
                                             linkage_method="complete",
                                             optimize=True)

        plot_hierarchical_clustering(distance_matrix_dataframe, results_clustering, labelsize=13,
                                 path_to_save_fig = Path(resultspath, self.export_dir, "clustering"), 
                                 title=title+".pdf")
   
        plot_clustering_results(list_distribs, 
                                bin_centers,
                                normalized=False,
                                labels=results_clustering["labels"], 
                                list_names=self.name_experiments, 
                                path_to_save = Path(resultspath, self.export_dir, "clustering", title+".pdf"))
        


