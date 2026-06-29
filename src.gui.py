"""
Graphical User Interface Module
Handles all UI components and user interaction
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from .processor import SpreadsheetProcessor


class SpreadsheetApplication:
    """Main application window with all UI components"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Spreadsheet Analysis System")
        self.root.geometry("1400x800")
        
        # Initialize processor
        self.processor = SpreadsheetProcessor()
        self.current_file = None
        
        # Create interface
        self.create_menu()
        self.create_widgets()
        
    def create_menu(self):
        """Create the application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Spreadsheet", command=self.open_file)
        file_menu.add_command(label="Export Data", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Processing Menu
        process_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Process", menu=process_menu)
        process_menu.add_command(label="Clean Data", command=self.clean_data)
        process_menu.add_command(label="Remove Duplicates", command=self.remove_duplicates)
        process_menu.add_command(label="Convert Types", command=self.convert_types)
    
    def create_widgets(self):
        """Create all interface widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel (controls)
        left_frame = ttk.Frame(main_frame, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Right panel (content)
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # ===== LEFT PANEL =====
        self._create_info_panel(left_frame)
        self._create_null_handling_panel(left_frame)
        self._create_filter_panel(left_frame)
        self._create_action_buttons(left_frame)
        self._create_history_panel(left_frame)
        
        # ===== RIGHT PANEL =====
        self._create_notebook(right_frame)
        
    def _create_info_panel(self, parent):
        """Create file information panel"""
        info_frame = ttk.LabelFrame(parent, text="📁 Information", padding=10)
        info_frame.pack(fill=tk.X, pady=5)
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=4, wrap=tk.WORD)
        self.info_text.pack(fill=tk.X)
        self.info_text.insert(tk.END, "No file loaded")
        self.info_text.config(state=tk.DISABLED)
    
    def _create_null_handling_panel(self, parent):
        """Create null handling panel"""
        nulls_frame = ttk.LabelFrame(parent, text="🔧 Handle Null Values", padding=10)
        nulls_frame.pack(fill=tk.X, pady=5)
        
        self.strategy_var = tk.StringVar(value="mean")
        strategies = ['mean', 'median', 'mode', 'zero', 'forward', 'backward']
        for strategy in strategies:
            ttk.Radiobutton(nulls_frame, text=strategy.capitalize(), 
                          variable=self.strategy_var, value=strategy).pack(anchor=tk.W)
        
        ttk.Button(nulls_frame, text="Apply Treatment", 
                  command=self.handle_nulls).pack(fill=tk.X, pady=5)
    
    def _create_filter_panel(self, parent):
        """Create filter panel"""
        filters_frame = ttk.LabelFrame(parent, text="🔍 Filters", padding=10)
        filters_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(filters_frame, text="Column:").pack(anchor=tk.W)
        self.filter_column = ttk.Combobox(filters_frame, state="readonly")
        self.filter_column.pack(fill=tk.X, pady=2)
        
        ttk.Label(filters_frame, text="Operator:").pack(anchor=tk.W)
        self.filter_operator = ttk.Combobox(filters_frame, 
                                           values=['>', '<', '>=', '<=', '==', '!=', 'contains'],
                                           state="readonly")
        self.filter_operator.pack(fill=tk.X, pady=2)
        self.filter_operator.set('==')
        
        ttk.Label(filters_frame, text="Value:").pack(anchor=tk.W)
        self.filter_value = ttk.Entry(filters_frame)
        self.filter_value.pack(fill=tk.X, pady=2)
        
        ttk.Button(filters_frame, text="Apply Filter", 
                  command=self.apply_filter).pack(fill=tk.X, pady=5)
        ttk.Button(filters_frame, text="Clear Filter", 
                  command=self.clear_filter).pack(fill=tk.X)
    
    def _create_action_buttons(self, parent):
        """Create action buttons"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(buttons_frame, text="📊 Metrics", 
                  command=self.show_metrics).pack(fill=tk.X, pady=2)
        ttk.Button(buttons_frame, text="💡 Insights", 
                  command=self.show_insights).pack(fill=tk.X, pady=2)
        ttk.Button(buttons_frame, text="📈 Charts", 
                  command=self.show_charts).pack(fill=tk.X, pady=2)
    
    def _create_history_panel(self, parent):
        """Create history panel"""
        history_frame = ttk.LabelFrame(parent, text="📜 History", padding=10)
        history_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.history_text = scrolledtext.ScrolledText(history_frame, height=8)
        self.history_text.pack(fill=tk.BOTH, expand=True)
    
    def _create_notebook(self, parent):
        """Create notebook with tabs"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Data Tab
        self._create_data_tab()
        
        # Metrics Tab
        self._create_metrics_tab()
        
        # Charts Tab
        self._create_charts_tab()
        
        # Grouping Tab
        self._create_grouping_tab()
    
    def _create_data_tab(self):
        """Create data display tab"""
        data_frame = ttk.Frame(self.notebook)
        self.notebook.add(data_frame, text="📊 Data")
        
        # Tree frame with scrollbars
        tree_frame = ttk.Frame(data_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        v_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        h_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        self.tree = ttk.Treeview(tree_frame, 
                                yscrollcommand=v_scroll.set,
                                xscrollcommand=h_scroll.set)
        
        v_scroll.config(command=self.tree.yview)
        h_scroll.config(command=self.tree.xview)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _create_metrics_tab(self):
        """Create metrics display tab"""
        metrics_frame = ttk.Frame(self.notebook)
        self.notebook.add(metrics_frame, text="📋 Metrics")
        
        self.metrics_text = scrolledtext.ScrolledText(metrics_frame, wrap=tk.WORD)
        self.metrics_text.pack(fill=tk.BOTH, expand=True)
    
    def _create_charts_tab(self):
        """Create charts display tab"""
        charts_frame = ttk.Frame(self.notebook)
        self.notebook.add(charts_frame, text="📈 Charts")
        
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=charts_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Chart controls
        chart_controls = ttk.Frame(charts_frame)
        chart_controls.pack(fill=tk.X, pady=5)
        
        ttk.Label(chart_controls, text="Type:").pack(side=tk.LEFT, padx=5)
        self.chart_type = ttk.Combobox(chart_controls, 
                                      values=['Histogram', 'Boxplot', 'Scatter'],
                                      state="readonly")
        self.chart_type.pack(side=tk.LEFT, padx=5)
        self.chart_type.set('Histogram')
        
        ttk.Label(chart_controls, text="Column:").pack(side=tk.LEFT, padx=5)
        self.chart_column = ttk.Combobox(chart_controls, state="readonly")
        self.chart_column.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(chart_controls, text="Generate Chart", 
                  command=self.generate_chart).pack(side=tk.LEFT, padx=5)
    
    def _create_grouping_tab(self):
        """Create grouping tab"""
        grouping_frame = ttk.Frame(self.notebook)
        self.notebook.add(grouping_frame, text="📊 Grouping")
        
        # Controls
        group_controls = ttk.Frame(grouping_frame)
        group_controls.pack(fill=tk.X, pady=10)
        
        ttk.Label(group_controls, text="Group by:").pack(side=tk.LEFT, padx=5)
        self.group_column = ttk.Combobox(group_controls, state="readonly")
        self.group_column.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(group_controls, text="Aggregate:").pack(side=tk.LEFT, padx=5)
        self.aggregate_column = ttk.Combobox(group_controls, state="readonly")
        self.aggregate_column.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(group_controls, text="Function:").pack(side=tk.LEFT, padx=5)
        self.group_function = ttk.Combobox(group_controls, 
                                          values=['mean', 'sum', 'count', 'min', 'max'],
                                          state="readonly")
        self.group_function.pack(side=tk.LEFT, padx=5)
        self.group_function.set('mean')
        
        ttk.Button(group_controls, text="Apply Grouping", 
                  command=self.apply_grouping).pack(side=tk.LEFT, padx=5)
        
        # Results area
        self.group_result = scrolledtext.ScrolledText(grouping_frame, wrap=tk.WORD)
        self.group_result.pack(fill=tk.BOTH, expand=True)
    
    # ============ ACTION METHODS ============
    
    def open_file(self):
        """Open an Excel/CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select file",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.current_file = file_path
                self.processor.load_data(file_path)
                self.processor.clean_data()
                self.processor.convert_types()
                self.processor.calculate_metrics()
                
                self.update_interface()
                self.update_history()
                
                messagebox.showinfo("Success", f"File loaded successfully!\n{len(self.processor.processed_data)} records")
                
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def handle_nulls(self):
        """Handle null values"""
        if self.processor.processed_data is None:
            messagebox.showwarning("Warning", "No data loaded")
            return
        
        try:
            strategy = self.strategy_var.get()
            self.processor.handle_null_values(strategy)
            self.processor.calculate_metrics()
            self.update_interface()
            self.update_history()
            messagebox.showinfo("Success", f"Null values handled with strategy '{strategy}'")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def apply_filter(self):
        """Apply filter to data"""
        if self.processor.processed_data is None:
            messagebox.showwarning("Warning", "No data loaded")
            return
        
        try:
            column = self.filter_column.get()
            operator = self.filter_operator.get()
            value_str = self.filter_value.get()
            
            if not column or not value_str:
                messagebox.showwarning("Warning", "Fill all filter fields")
                return
            
            # Try to convert value to number
            try:
                value = float(value_str) if '.' in value_str else int(value_str)
            except:
                value = value_str
            
            result = self.processor.filter_data(column, operator, value)
            
            if result is not None:
                self.update_treeview(result)
                messagebox.showinfo("Success", f"Filter applied: {len(result)} records found")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def apply_grouping(self):
        """Apply grouping to data"""
        if self.processor.processed_data is None:
            messagebox.showwarning("Warning", "No data loaded")
            return
        
        try:
            group_col = self.group_column.get()
            agg_col = self.aggregate_column.get()
            function = self.group_function.get()
            
            if not group_col or not agg_col:
                messagebox.showwarning("Warning", "Select columns for grouping")
                return
            
            result = self.processor.group_data(group_col, agg_col, function)
            
            if result is not None:
                self.group_result.delete(1.0, tk.END)
                self.group_result.insert(tk.END, result.to_string())
                
                # Also show in chart
                self.fig.clear()
                ax = self.fig.add_subplot(111)
                ax.bar(result[group_col].astype(str), result[agg_col])
                ax.set_xlabel(group_col)
                ax.set_ylabel(agg_col)
                ax.set_title(f"{function.upper()} of {agg_col} by {group_col}")
                self.fig.autofmt_xdate()
                self.canvas.draw()
                
                self.notebook.select(2)  # Go to charts tab
                
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def generate_chart(self):
        """Generate chart based on selection"""
        if self.processor.processed_data is None:
            messagebox.showwarning("Warning", "No data loaded")
            return
        
        try:
            chart_type = self.chart_type.get()
            column = self.chart_column.get()
            
            if not column:
                messagebox.showwarning("Warning", "Select a column")
                return
            
            df = self.processor.processed_data
            self.fig.clear()
            ax = self.fig.add_subplot(111)
            
            if chart_type == 'Histogram':
                ax.hist(df[column].dropna(), bins=30, edgecolor='black', alpha=0.7)
                ax.set_xlabel(column)
                ax.set_ylabel('Frequency')
                ax.set_title(f'Histogram of {column}')
                
            elif chart_type == 'Boxplot':
                ax.boxplot(df[column].dropna())
                ax.set_ylabel(column)
                ax.set_title(f'Boxplot of {column}')
                ax.set_xticklabels([column])
                
            elif chart_type == 'Scatter':
                if len(self.processor.metrics['numeric_columns']) >= 2:
                    column2 = self.processor.metrics['numeric_columns'][1]
                    ax.scatter(df[column], df[column2], alpha=0.5)
                    ax.set_xlabel(column)
                    ax.set_ylabel(column2)
                    ax.set_title(f'Scatter Plot: {column} vs {column2}')
                else:
                    messagebox.showwarning("Warning", "Need at least 2 numeric columns")
                    return
            
            self.fig.tight_layout()
            self.canvas.draw()
            self.notebook.select(2)  # Go to charts tab
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def show_metrics(self):
        """Show detailed metrics"""
        if not self.processor.metrics:
            messagebox.showwarning("Warning", "No metrics available")
            return
        
        self.metrics_text.delete(1.0, tk.END)
        
        metrics = self.processor.metrics
        
        text = "=" * 60 + "\n"
        text += "DATA METRICS\n"
        text += "=" * 60 + "\n\n"
        
        text += f"Total records: {metrics['total_records']:,}\n"
        text += f"Total columns: {metrics['total_columns']}\n"
        text += f"Duplicates: {metrics['duplicates']}\n"
        text += f"Memory used: {metrics['memory_usage']:.2f} MB\n\n"
        
        text += "Columns:\n"
        for col in metrics['columns']:
            dtype = metrics['data_types'][col]
            nulls = metrics['nulls_per_column'][col]
            pct_nulls = metrics['null_percentage'][col]
            text += f"  - {col}: {dtype} (Nulls: {nulls}, {pct_nulls:.1f}%)\n"
        
        text += "\n" + "=" * 60 + "\n"
        text += "NUMERIC STATISTICS\n"
        text += "=" * 60 + "\n\n"
        
        if metrics['numeric_stats']:
            for col, stats in metrics['numeric_stats'].items():
                text += f"\n{col}:\n"
                for stat, value in stats.items():
                    if isinstance(value, (int, float)):
                        text += f"  {stat}: {value:.2f}\n"
                    else:
                        text += f"  {stat}: {value}\n"
        
        self.metrics_text.insert(tk.END, text)
        self.notebook.select(1)  # Go to metrics tab
    
    def show_insights(self):
        """Show automatic insights"""
        insights = self.processor.generate_insights()
        
        if not insights:
            messagebox.showinfo("Insights", "No interesting insights found")
            return
        
        text = "=" * 60 + "\n"
        text += "AUTOMATIC INSIGHTS\n"
        text += "=" * 60 + "\n\n"
        
        for i, insight in enumerate(insights, 1):
            text += f"{i}. {insight['title']}\n"
            text += f"   {insight['description']}\n\n"
        
        messagebox.showinfo("Insights", text)
    
    def update_interface(self):
        """Update entire interface"""
        if self.processor.processed_data is not None:
            # Update info
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            info = f"File: {self.current_file}\n"
            info += f"Records: {len(self.processor.processed_data):,}\n"
            info += f"Columns: {len(self.processor.processed_data.columns)}\n"
            info += f"Duplicates: {self.processor.metrics.get('duplicates', 0)}"
            self.info_text.insert(tk.END, info)
            self.info_text.config(state=tk.DISABLED)
            
            # Update treeview
            self.update_treeview(self.processor.processed_data)
            
            # Update comboboxes
            self.update_comboboxes()
    
    def update_treeview(self, df):
        """Update treeview with data"""
        # Clear treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Configure columns
        self.tree['columns'] = list(df.columns)
        self.tree['show'] = 'headings'
        
        # Configure headings
        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor='center')
        
        # Insert data (limited to 1000 rows for performance)
        for i, row in df.head(1000).iterrows():
            values = [str(v) if pd.notna(v) else '' for v in row]
            self.tree.insert('', 'end', values=values)
    
    def update_comboboxes(self):
        """Update comboboxes with available columns"""
        if self.processor.processed_data is not None:
            columns = self.processor.processed_data.columns.tolist()
            
            self.filter_column['values'] = columns
            self.chart_column['values'] = columns
            self.group_column['values'] = self.processor.metrics.get('categorical_columns', [])
            self.aggregate_column['values'] = self.processor.metrics.get('numeric_columns', [])
            
            if columns:
                self.filter_column.set(columns[0])
                self.chart_column.set(columns[0])
    
    def update_history(self):
        """Update history display"""
        self.history_text.delete(1.0, tk.END)
        
        if self.processor.history:
            for item in reversed(self.processor.history[-20:]):
                self.history_text.insert(tk.END, f"⏰ {item['timestamp']}\n")
                self.history_text.insert(tk.END, f"📌 {item['action']}: {item['details']}\n")
                self.history_text.insert(tk.END, "-" * 40 + "\n")
    
    def clean_data(self):
        """Clean the data"""
        if self.processor.raw_data is None:
            messagebox.showwarning("Warning", "No data loaded")
            return
        
        try:
            self.processor.clean_data()
            self.processor.calculate_metrics()
            self.update_interface()
            self.update_history()
            messagebox.showinfo("Success", "Data cleaned successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def remove_duplicates(self):
        """Remove duplicates"""
        if self.processor.processed_data is None:
            messagebox.showwarning("Warning", "No data loaded")
            return
        
        try:
            self.processor.remove_duplicates()
            self.processor.calculate_metrics()
            self.update_interface()
            self.update_history()
            messagebox.showinfo("Success", "Duplicates removed successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def convert_types(self):
        """Convert data types"""
        if self.processor.processed_data is None:
            messagebox.showwarning("Warning", "No data loaded")
            return
        
        try:
            self.processor.convert_types()
            self.processor.calculate_metrics()
            self.update_interface()
            self.update_history()
            messagebox.showinfo("Success", "Types converted successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def export_data(self):
        """Export processed data"""
        if self.processor.processed_data is None:
            messagebox.showwarning("Warning", "No data to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save as",
            defaultextension=".xlsx",
            filetypes=[("Excel file", "*.xlsx"), ("CSV file", "*.csv")]
        )
        
        if file_path:
            try:
                format = 'excel' if file_path.endswith('.xlsx') else 'csv'
                self.processor.export_data(file_path, format)
                messagebox.showinfo("Success", "Data exported successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def clear_filter(self):
        """Clear filter and show all data"""
        if self.processor.processed_data is not None:
            self.update_treeview(self.processor.processed_data)
            self.filter_value.delete(0, tk.END)
            messagebox.showinfo("Success", "Filter removed")
    
    def show_charts(self):
        """Show charts tab"""
        self.notebook.select(2)
