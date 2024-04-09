"""A customtkinter gui that utilises various sorting algorithms to visualise
how an array is sorted
"""

from time import time
from tkinter import END, Canvas, BOTH, messagebox
from typing import Callable, Any, List
from os import path
from random import randint
from pathlib import Path

from PIL import Image
from customtkinter import (
    set_widget_scaling, set_appearance_mode, set_default_color_theme,
    CTkFont, CTkLabel, CTkOptionMenu, CTkButton, CTkEntry, CTk, 
    CTkToplevel, set_widget_scaling, CTkImage, CTkFrame
)

MINIMUM_ARRAY_VALUE = 1
MAXIMUM_ARRAY_VALUE = 1000
MINIMUM_ARRAY_SAMPLES = 1
MAXIMUM_ARRAY_SAMPLES = 600
AVAILABLE_SORTING_FUNCTIONS = ["bubble_sort", "insertion_sort", "selection_sort"]
ASSETS_PATH = Path(__file__).resolve().parents[0] / "assets"

# Append sorting times and function names from wrapper
current_sort = {"name": "", "runtime": 0}

def _sorting_time(func: Callable) -> None:
    def wrapper(*args, 
                **kwargs
                ) -> Any:
        global current_sort
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        time_taken = end_time - start_time
        if result == "pause":
            current_sort["name"] = func.__name__
            current_sort["runtime"] += time_taken
        else:
            if current_sort["runtime"] == 0:
                current_sort = {"name": func.__name__, "runtime": time_taken}
            else:
                current_sort["runtime"] += time_taken
            messagebox.showinfo(title="Sort complete!", 
                                message=f"{current_sort['name']} took "
                                        f"{round(current_sort['runtime'], 3)}s")
            current_sort["runtime"] = 0
        return result 
    return wrapper


class Home(CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Sorting Algorithm Visualisation")
        self.protocol("WM_DELETE_WINDOW", self._handle_exit)
        self.geometry("500x500")
        self.minsize(500, 500)
        set_widget_scaling(0.9)
        set_default_color_theme(path.join(ASSETS_PATH, "themes", "TrojanBlue.json"))
        
        self._default_font = CTkFont(family="Courier New")
        self._screen_width = self.winfo_screenwidth()
        self._screen_height = self.winfo_screenheight()
        
        self._make_content()
        self._place_content()
    
    def _handle_exit(self) -> None:
        try:
            self.array_visualiser.sorter.pause_sort = True
        except: ...
        self.destroy()
        
    def _make_content(self) -> None:
        self.title_label = CTkLabel(self, text="Sorting Algorithm Visualisation",
                                    font=CTkFont(family="Courier New", size=25, 
                                                 weight="bold"))
        self.sorting_image = CTkLabel(self, text="", 
            image=CTkImage(Image.open(path.join(ASSETS_PATH, "sorting_vis.png")), size=(300,150)))
        self.bluemoji_1 = CTkLabel(self, text="", image=CTkImage(Image.open(path.join(ASSETS_PATH, "gasp.png")), size=(100, 100)))
        self.bluemoji_2 = CTkLabel(self, text="", image=CTkImage(Image.open(path.join(ASSETS_PATH, "thumbs_up.png")), size=(100, 100)))
        
        
        self.choose_algorithm = CTkOptionMenu(self, 
                values=AVAILABLE_SORTING_FUNCTIONS, font=self._default_font)
        self.choose_algorithm_label = CTkLabel(self, text="Sorting algorithm",
                                                    font=self._default_font)
        
        self.lower_sample_bound_entry = CTkEntry(self, font=self._default_font,
                        placeholder_text=f"< upper, >= {MINIMUM_ARRAY_VALUE}")
        self.upper_sample_bound_entry = CTkEntry(self, font=self._default_font,
                        placeholder_text=f"> lower, <= {MAXIMUM_ARRAY_VALUE}")
        self.lower_sample_bound_label = CTkLabel(self, text="Lower sample bound", 
                                                        font=self._default_font)
        self.upper_sample_bound_label = CTkLabel(self, text="Upper sample bound", 
                                                 font=self._default_font)
        self.sample_count_entry = CTkEntry(self, font=self._default_font,
            placeholder_text=(f">= {MINIMUM_ARRAY_SAMPLES}, <= "
                              f"{MAXIMUM_ARRAY_SAMPLES}"))
        self.sample_count_entry_label = CTkLabel(self, text="Sample count",
                                                 font=self._default_font)
        self.random_entry_fill_button = CTkButton(self, text="Randomly fill inputs", 
                    font=self._default_font, command=self._random_entry_filler)
        self.clear_entries_button = CTkButton(self, text="Clear inputs", 
                        font=self._default_font, command=self._clear_entries)
        self.fill_max_values_button = CTkButton(self, font=self._default_font,
            text="Fill in max array values", command=self._fill_max_values)
        
        self.open_sorter_button = CTkButton(self, text="Load array", 
                                            font=self._default_font, 
                                            command=self._init_array_visualiser)
        
    def _place_content(self) -> None:
        self.title_label.place(relx=0.5, rely=0.415, anchor="c")
        self.sorting_image.place(relx=0.5, rely=0.1925, anchor="c")
        self.bluemoji_1.place(relx=0.115, rely=0.1925, anchor="c")
        self.bluemoji_2.place(relx=0.885, rely=0.1925, anchor="c")
        self.choose_algorithm.place(relx=0.3, rely=0.6, anchor="c")
        self.choose_algorithm_label.place(relx=0.3, rely=0.55, anchor="c")
        self.lower_sample_bound_entry.place(relx=0.7, rely=0.6, anchor="c")
        self.upper_sample_bound_entry.place(relx=0.7, rely=0.725, anchor="c")
        self.lower_sample_bound_label.place(relx=0.7, rely=0.55, anchor="c")
        self.upper_sample_bound_label.place(relx=0.7, rely=0.675, anchor="c")
        self.sample_count_entry.place(relx=0.3, rely=0.725, anchor="c")
        self.sample_count_entry_label.place(relx=0.3, rely=0.675, anchor="c")
        self.open_sorter_button.place(relx=0.7, rely=0.925, anchor="c")
        self.random_entry_fill_button.place(relx=0.3, rely=0.825, anchor="c")
        self.clear_entries_button.place(relx=0.7, rely=0.825, anchor="c")
        self.fill_max_values_button.place(relx=0.3, rely=0.925, anchor="c")

    def _verify_entries(self) -> bool:
        try:
            self.lower_input = int(self.lower_sample_bound_entry.get())
            self.upper_input = int(self.upper_sample_bound_entry.get())
            self.sample_count_input = int(self.sample_count_entry.get())
        except:
            messagebox.showerror(message="Entries have non-integer inputs! "
                                         "Press Enter to continue.")
            return False

        if (self.lower_input < MINIMUM_ARRAY_VALUE 
                or self.upper_input > MAXIMUM_ARRAY_VALUE
                or self.lower_input >= self.upper_input 
                or self.sample_count_input > MAXIMUM_ARRAY_SAMPLES
                or self.sample_count_input < MINIMUM_ARRAY_SAMPLES):
            messagebox.showerror(
                message="Entries must contain integers within the required "
                        "bounds! Press Enter to continue.")
            return False
        else:
            return True
            
    def _init_array_visualiser(self) -> None:
        if self._verify_entries():
            self.array_visualiser = ArrayVisualiser(
                             self, self.lower_input, self.upper_input, 
                            self.sample_count_input, self.choose_algorithm.get())
            return

    def _clear_entries(self) -> None:
        self.lower_sample_bound_entry.delete(0, END)
        self.upper_sample_bound_entry.delete(0, END)
        self.sample_count_entry.delete(0, END)
        self.lower_sample_bound_entry.focus()
        self.upper_sample_bound_entry.focus()
        self.sample_count_entry.focus()
        self.focus()

    def _random_entry_filler(self) -> None:
        self._clear_entries()
        self.lower_sample_bound_entry.insert(0, 
            f"{randint(MINIMUM_ARRAY_VALUE, int(MAXIMUM_ARRAY_VALUE / 2))}")
        self.upper_sample_bound_entry.insert(0,
            f"{randint(int(self.lower_sample_bound_entry.get()) + 1, MAXIMUM_ARRAY_VALUE)}")
        self.sample_count_entry.insert(0, 
            f"{randint(MINIMUM_ARRAY_SAMPLES, MAXIMUM_ARRAY_SAMPLES)}")

    def _fill_max_values(self) -> None:
        self._clear_entries()
        self.lower_sample_bound_entry.insert(0, 1)
        self.upper_sample_bound_entry.insert(0, MAXIMUM_ARRAY_VALUE)
        self.sample_count_entry.insert(0, MAXIMUM_ARRAY_SAMPLES)


class ArrayVisualiser(CTkToplevel):
    def __init__(self, 
                 master: Home, 
                 lowerbound: int, 
                 upperbound: int, 
                 samplecount: int, 
                 algorithm: str
                 ) -> None:
        super().__init__(master)
        
        self.attributes("-fullscreen", True)
        self.title(algorithm)
        self.protocol("WM_DELETE_WINDOW", self._handle_exit)
        self.geometry(f"{self.master._screen_width}x{self.master._screen_height}")
        set_widget_scaling(0.9)
        
        self.master = master
        self._lower_bound = lowerbound
        self._upper_bound = upperbound
        self._sample_count = samplecount
        self._algorithm = algorithm
        
        self.sorter = SortingAlgorithms(self) 
        self.currently_sorting = False
        
        self._make_content()
        self._place_content()
        self._display_array()
    
    def _handle_exit(self) -> None:
        self.toggle_sort_button.invoke()
        self.destroy()
    
    def _make_content(self) -> None:
        self.frame = CTkFrame(self)
        self.initialise_sort_button = CTkButton(self.frame, text="Initialise sort", 
            command=lambda: self._initialise_sort(self.arr), state="disabled",
                                            font=self.master._default_font)
        self.gen_new_arr_button = CTkButton(self.frame, text="Make a new array", 
                    font=self.master._default_font, command=self._display_array)
        self.toggle_sort_button = CTkButton(self.frame, text="Stop sorting", 
            font=self.master._default_font, state="disabled", 
            command=self._toggle_sort)
        self.exit_button = CTkButton(self.frame, text="Exit", 
            font=self.master._default_font, command=self._handle_exit, 
            fg_color="#ED3B4D", hover_color="#590911")
        
        self.canvas = Canvas(self.frame, width=self.master._screen_width - 60,
            height=self.master._screen_height * 0.9 - 60, background="#2d4485")
    
    def _place_content(self):
        self.frame.pack(fill=BOTH, expand=True)
        self.initialise_sort_button.place(relx=0.35, rely=0.93725, relheight=0.05, 
                                           relwidth=0.09, anchor="c")
        self.gen_new_arr_button.place(relx=0.45, rely=0.93725, relheight=0.05, 
                                      relwidth=0.09, anchor="c")
        self.toggle_sort_button.place(relx=0.55, rely=0.93725, relheight=0.05, 
                                      relwidth=0.09, anchor="c")
        self.exit_button.place(relx=0.65, rely=0.93725, relheight=0.05, 
                               relwidth=0.09, anchor="c")
        self.canvas.pack(padx=30, pady=(30, 78))

    def _display_array(self) -> None:
        self.currently_sorting = False
        self.toggle_sort_button.configure(state="disabled", text="Stop sorting")
        self.initialise_sort_button.configure(state="normal")
        
        self.arr = [randint(self._lower_bound, self._upper_bound) \
                    for _ in range(self._sample_count)]
        self._arr_length = len(self.arr)
        self._min_val = min(self.arr)
        self._max_val = max(self.arr)
        self._range = self._max_val - self._min_val
        
        self.render_array(self.arr)

    def _initialise_sort(self, 
                         arr: List[int]
                         ) -> None:
        self.currently_sorting = True
        self.sorter.pause_sort = False
        self.toggle_sort_button.configure(state="normal")
        self.initialise_sort_button.configure(state="disabled")
        self.gen_new_arr_button.configure(state="disabled")
        
        if self._algorithm == "bubble_sort":
            self.sorter.bubble_sort(arr)
        elif self._algorithm == "selection_sort":
            self.sorter.selection_sort(arr)
        elif self._algorithm == "insertion_sort":
            self.sorter.insertion_sort(arr)

    def _toggle_sort(self) -> None:
        if self.currently_sorting:
            self.sorter.pause_sort = True
            self.currently_sorting = False
            self.toggle_sort_button.configure(text="Start Sorting", 
                                              state="normal")
            self.gen_new_arr_button.configure(state="normal")
        else:
            self.sorter.pause_sort = False
            self.currently_sorting = True 
            self.toggle_sort_button.configure(text="Stop Sorting", 
                state="normal")
            self.gen_new_arr_button.configure(state="disabled")
            self._initialise_sort(self.sorter._paused_array)

    def render_array(self, 
                     arr: List[int], 
                     sorting_indices: List[int] = [], 
                     complete: bool = False
                     ) -> None:        
        self.canvas.delete("columns")
        canvas_width = self.canvas.winfo_reqwidth() - 10
        canvas_height = self.canvas.winfo_reqheight() - 21
        bar_width = canvas_width / self._arr_length

        for i, item in enumerate(arr):
            x1 = i * bar_width + 3
            y1 = canvas_height * (1 - (item - self._min_val) / self._range)
            x2 = x1 + bar_width
            y2 = canvas_height
            if not complete:    
                fill = "#eb3f3f" if i in sorting_indices else "#aebac2"
                outline = "#eb6e6e" if i in sorting_indices else "#c7cdd1"
            else:
                fill = "#28b842"
                outline = "#229937"
            
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, 
                                         outline=outline, tags="columns")
            
        if complete:
            self.currently_sorting = False
            self.toggle_sort_button.configure(state="disabled")
            self.gen_new_arr_button.configure(state="normal")
        
        self.update()
        

class SortingAlgorithms(object):
    def __init__(self, 
                 master: ArrayVisualiser
                 ) -> None:
        self.master = master
        self.pause_sort = False
        self._paused_array = []
        
    @_sorting_time
    def bubble_sort(self,
                    arr: List[int]
                    ) -> None:
        """Iterate through an array, where each iteration excludes another 
        item from the end. With each iteration, arr[j] and arr[j + 1] are 
        compared. If arr[j] is greater than arr[j + 1], they switch. Say arr[j] 
        is the greatest value in the array, then with each iteration it will 
        switch with the value to its right, effectively "bubbling" to the end 
        of the array.
        """
        length = len(arr)
        for i in range(length):
            for j in range(length - i - 1):
                if arr[j] > arr[j + 1]: 
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    if self.pause_sort:
                        self._paused_array = arr.copy()
                        return "pause"
                    self.master.render_array(arr, [j, j + 1])
                    
        self.master.render_array(arr, complete=True)
    
    @_sorting_time
    def selection_sort(self, 
                       arr: List[int]
                       ) -> None: 
        """Iterate through an array, with each new iteration excluding another 
        item from the start of the list. Each iteration finds the smallest 
        item in the array and switches it with the next item of the outer loop.
        """
        length = len(arr)
        for i in range(length):
            min_index = i 
            for j in range(i, length):
                if arr[j] < arr[min_index]: 
                    min_index = j
            if min_index != i: 
                arr[i], arr[min_index] = arr[min_index], arr[i]
                if self.pause_sort:
                        self._paused_array = arr.copy()
                        return "pause"
                self.master.render_array(arr, [i, min_index])
                
        self.master.render_array(arr, complete=True)

    @_sorting_time
    def insertion_sort(self, 
                       arr: List[int]
                       ) -> None:
        """Similar to bubble sort but in reverse. The insertion sort algorithm
        selects an item in an array and shifts it to the left (descending)
        until the value to its left is smaller than it. This process builds
        the sorted array from the left to the right.
        """
        length = len(arr)
        for i in range(1, length): 
            j = i
            while j > 0 and arr[j - 1] > arr[j]: 
                arr[j], arr[j - 1] = arr[j - 1], arr[j]
                if self.pause_sort:
                        self._paused_array = arr.copy()
                        return "pause"
                self.master.render_array(arr, [j, j - 1])
                j -= 1 
                
        self.master.render_array(arr, complete=True)
    
 
def start():
    # entry point for package
    app = Home()
    app.mainloop()

if __name__ == "__main__":
    app = Home()
    app.mainloop()