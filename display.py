import tkinter as tk
from tkinter import ttk
from mqtt import shared_data, start_subscriber
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import datetime
import json
import os

# Constants
ROOMS = ["Room 1", "Room 2", "Room 3", "Room 4"]
THEME_COLORS = {
    'background': '#f5f6fa',
    'card': '#ffffff',
    'primary': '#3498db',
    'success': '#2ecc71',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'text': '#2c3e50',
    'border': '#dcdde1'
}
FONT_PRIMARY = ('Segoe UI', 10)
FONT_SECONDARY = ('Segoe UI', 8)
FONT_TITLE = ('Segoe UI', 12, 'bold')

# Start MQTT subscriber
start_subscriber()

class SmartBuildingDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Building Dashboard")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        self.root.configure(bg=THEME_COLORS['background'])
        
        # Initialize icons dictionary first
        self.icons = {}
        self.load_icons()
        
        # Configure styles
        self.configure_styles()
        
        # Create main containers
        self.create_header()
        self.create_main_content()
        self.create_footer()
        
        # Initialize data history
        self.history = {room: {'temp': [], 'humidity': [], 'timestamps': []} for room in ROOMS}
        self.max_history_points = 30
        
        # Start data updates
        self.update_data()
        
        # Make window responsive
        self.make_responsive()
        
        # Initialize data logging
        self.log_file = "sensor_data.log"
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump([], f)
    
    def configure_styles(self):
        """Configure ttk styles for the application"""
        style = ttk.Style()
        
        # Frame styles
        style.configure('TFrame', background=THEME_COLORS['background'])
        style.configure('Card.TFrame', 
                      background=THEME_COLORS['card'],
                      borderwidth=1,
                      relief='solid',
                      bordercolor=THEME_COLORS['border'])
        
        # Label styles
        style.configure('Title.TLabel',
                      font=FONT_TITLE,
                      background=THEME_COLORS['background'],
                      foreground=THEME_COLORS['text'])
        
        style.configure('Value.TLabel',
                      font=('Segoe UI', 14, 'bold'),
                      background=THEME_COLORS['card'],
                      foreground=THEME_COLORS['primary'])
        
        style.configure('Unit.TLabel',
                      font=FONT_SECONDARY,
                      background=THEME_COLORS['card'],
                      foreground=THEME_COLORS['text'])
        
        style.configure('Status.TLabel',
                      font=FONT_SECONDARY,
                      background=THEME_COLORS['card'],
                      foreground=THEME_COLORS['success'])
        
        # Button styles
        style.configure('TButton',
                      font=FONT_PRIMARY,
                      padding=6)
        
        style.map('TButton',
                 foreground=[('pressed', THEME_COLORS['text']),
                            ('active', THEME_COLORS['text'])],
                 background=[('pressed', '!disabled', THEME_COLORS['border']),
                            ('active', THEME_COLORS['border'])])
    
    def create_header(self):
        """Create the header section"""
        header_frame = ttk.Frame(self.root, style='Card.TFrame')
        header_frame.pack(fill=tk.X, padx=10, pady=10, ipady=10)
        
        # Title
        ttk.Label(header_frame, 
                 text="SMART BUILDING MONITORING SYSTEM", 
                 style='Title.TLabel').pack(side=tk.LEFT, padx=10)
        
        # Status indicators
        status_frame = ttk.Frame(header_frame)
        status_frame.pack(side=tk.RIGHT, padx=10)
        
        self.connection_status = ttk.Label(status_frame, 
                                         text="● Connected", 
                                         style='Status.TLabel')
        self.connection_status.pack(side=tk.LEFT, padx=5)
        
        self.last_update = ttk.Label(status_frame, 
                                   text=f"Last update: --", 
                                   style='Status.TLabel')
        self.last_update.pack(side=tk.LEFT, padx=5)
    
    def create_main_content(self):
        """Create the main content area with room cards"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Create a grid of room cards
        self.room_cards = {}
        for i, room in enumerate(ROOMS):
            card = self.create_room_card(main_frame, room)
            card.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="nsew")
            self.room_cards[room] = card
            
            # Configure grid weights for responsiveness
            main_frame.grid_rowconfigure(i//2, weight=1)
            main_frame.grid_columnconfigure(i%2, weight=1)
    
    def create_room_card(self, parent, room_name):
        """Create a card for a single room"""
        card = ttk.Frame(parent, style='Card.TFrame', padding=10)
        
        # Room title
        ttk.Label(card, 
                 text=room_name.upper(), 
                 style='Title.TLabel',
                 background=THEME_COLORS['card']).pack(fill=tk.X, pady=(0, 10))
        
        # Sensor data frame
        data_frame = ttk.Frame(card)
        data_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side - sensor values
        sensor_frame = ttk.Frame(data_frame)
        sensor_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Create sensor value displays
        self.create_sensor_display(sensor_frame, room_name, "temp", "°C", "temp_icon.png")
        self.create_sensor_display(sensor_frame, room_name, "humidity", "%", "humidity_icon.png")
        self.create_sensor_display(sensor_frame, room_name, "pressure", "hPa", "pressure_icon.png")
        self.create_sensor_display(sensor_frame, room_name, "airquality", "", "air_icon.png")
        
        # Right side - graphs
        graph_frame = ttk.Frame(data_frame)
        graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Temperature graph
        fig_temp = plt.Figure(figsize=(4, 2), dpi=80, facecolor=THEME_COLORS['card'])
        ax_temp = fig_temp.add_subplot(111)
        ax_temp.set_facecolor(THEME_COLORS['card'])
        self.configure_plot_style(ax_temp, "Temperature (°C)")
        canvas_temp = FigureCanvasTkAgg(fig_temp, graph_frame)
        canvas_temp.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Humidity graph
        fig_hum = plt.Figure(figsize=(4, 2), dpi=80, facecolor=THEME_COLORS['card'])
        ax_hum = fig_hum.add_subplot(111)
        ax_hum.set_facecolor(THEME_COLORS['card'])
        self.configure_plot_style(ax_hum, "Humidity (%)")
        canvas_hum = FigureCanvasTkAgg(fig_hum, graph_frame)
        canvas_hum.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Store references to update later
        card.ax_temp = ax_temp
        card.ax_hum = ax_hum
        card.canvas_temp = canvas_temp
        card.canvas_hum = canvas_hum
        
        return card
    
    def create_sensor_display(self, parent, room_name, sensor, unit, icon_name):
        """Create a single sensor display row"""
        frame = ttk.Frame(parent, style='Card.TFrame', padding=5)
        frame.pack(fill=tk.X, pady=2)
        
        # Icon
        icon = self.icons.get(icon_name, None)
        if icon:
            ttk.Label(frame, image=icon, background=THEME_COLORS['card']).pack(side=tk.LEFT, padx=5)
        
        # Sensor name
        ttk.Label(frame, 
                 text=sensor.capitalize() + ":", 
                 font=FONT_PRIMARY,
                 background=THEME_COLORS['card']).pack(side=tk.LEFT, padx=5)
        
        # Value display
        value_label = ttk.Label(frame, 
                               text="--", 
                               style='Value.TLabel',
                               background=THEME_COLORS['card'])
        value_label.pack(side=tk.LEFT)
        
        # Unit
        if unit:
            ttk.Label(frame, 
                     text=unit, 
                     style='Unit.TLabel',
                     background=THEME_COLORS['card']).pack(side=tk.LEFT, padx=2)
        
        # Status indicator for air quality
        if sensor == "airquality":
            status_label = ttk.Label(frame, 
                                    text="", 
                                    style='Status.TLabel',
                                    background=THEME_COLORS['card'])
            status_label.pack(side=tk.LEFT, padx=10)
            setattr(self, f"{room_name}_{sensor}_status", status_label)
        
        # Store reference to update later
        setattr(self, f"{room_name}_{sensor}_label", value_label)
    
    def create_footer(self):
        """Create the footer section"""
        footer_frame = ttk.Frame(self.root, style='Card.TFrame')
        footer_frame.pack(fill=tk.X, padx=10, pady=(0, 10), ipady=5)
        
        ttk.Label(footer_frame, 
                 text="© 2023 Smart Building Monitoring System | Version 1.0", 
                 font=FONT_SECONDARY,
                 background=THEME_COLORS['card']).pack(side=tk.LEFT, padx=10)
        
        # Refresh button
        refresh_btn = ttk.Button(footer_frame, 
                               text="Manual Refresh", 
                               command=self.update_data)
        refresh_btn.pack(side=tk.RIGHT, padx=10)
    
    def load_icons(self):
        """Load all required icons"""
        icon_names = ["temp_icon.png", "humidity_icon.png", "pressure_icon.png", "air_icon.png"]
        
        for icon_name in icon_names:
            try:
                img = Image.open(icon_name)
                img = img.resize((24, 24), Image.LANCZOS)
                self.icons[icon_name] = ImageTk.PhotoImage(img)
            except:
                # Create a blank placeholder if icon not found
                self.icons[icon_name] = ImageTk.PhotoImage(Image.new('RGBA', (24, 24), (255, 255, 255, 0)))
    
    def configure_plot_style(self, ax, title):
        """Configure consistent style for all plots"""
        ax.set_title(title, fontsize=10, pad=5)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.tick_params(axis='both', which='major', labelsize=8)
        ax.set_facecolor(THEME_COLORS['card'])
    
    def update_data(self):
        """Update all data displays"""
        try:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            self.last_update.config(text=f"Last update: {current_time}")
            
            for room in ROOMS:
                room_data = shared_data.get(room, {})
                
                # Update sensor values
                for sensor in ["temp", "humidity", "pressure", "airquality"]:
                    value = room_data.get(sensor, "--")
                    label = getattr(self, f"{room}_{sensor}_label")
                    label.config(text=value)
                    
                    # Color coding for air quality
                    if sensor == "airquality":
                        status_label = getattr(self, f"{room}_{sensor}_status")
                        if value.lower() == "good":
                            status_label.config(text="Good", foreground=THEME_COLORS['success'])
                        elif value.lower() == "moderate":
                            status_label.config(text="Moderate", foreground=THEME_COLORS['warning'])
                        else:
                            status_label.config(text="Poor", foreground=THEME_COLORS['danger'])
                
                # Update graphs if we have numeric data
                try:
                    temp = float(room_data.get("temp", 0))
                    hum = float(room_data.get("humidity", 0))
                    
                    # Add to history
                    self.history[room]['temp'].append(temp)
                    self.history[room]['humidity'].append(hum)
                    self.history[room]['timestamps'].append(current_time)
                    
                    # Trim history
                    if len(self.history[room]['temp']) > self.max_history_points:
                        self.history[room]['temp'].pop(0)
                        self.history[room]['humidity'].pop(0)
                        self.history[room]['timestamps'].pop(0)
                    
                    # Update graphs
                    card = self.room_cards[room]
                    self.update_graph(card.ax_temp, 
                                   self.history[room]['temp'], 
                                   "Temperature (°C)", 
                                   THEME_COLORS['primary'])
                    self.update_graph(card.ax_hum, 
                                   self.history[room]['humidity'], 
                                   "Humidity (%)", 
                                   THEME_COLORS['primary'])
                    
                    card.canvas_temp.draw()
                    card.canvas_hum.draw()
                    
                    # Log data
                    self.log_data(room, room_data)
                    
                except (ValueError, TypeError):
                    pass
            
            self.connection_status.config(text="● Connected", foreground=THEME_COLORS['success'])
        except Exception as e:
            print(f"Update error: {e}")
            self.connection_status.config(text="● Connection Error", foreground=THEME_COLORS['danger'])
        
        # Schedule next update
        self.root.after(2000, self.update_data)
    
    def update_graph(self, ax, data, title, color):
        """Update a single graph"""
        ax.clear()
        ax.plot(data, color=color, marker='o', markersize=3, linewidth=1.5)
        ax.set_title(title, fontsize=10, pad=5)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.tick_params(axis='both', which='major', labelsize=8)
        ax.set_facecolor(THEME_COLORS['card'])
    
    def log_data(self, room, data):
        """Log sensor data to file"""
        log_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'room': room,
            'data': data
        }
        
        try:
            with open(self.log_file, 'r+') as f:
                logs = json.load(f)
                logs.append(log_entry)
                f.seek(0)
                json.dump(logs, f, indent=2)
        except:
            pass
    
    def make_responsive(self):
        """Configure responsive behavior"""
        for i in range(2):
            self.root.grid_columnconfigure(i, weight=1)
            self.root.grid_rowconfigure(i, weight=1)
        
        self.root.bind('<Configure>', self.on_window_resize)
    
    def on_window_resize(self, event):
        """Handle window resize events"""
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartBuildingDashboard(root)
    root.mainloop()