import sys
from PyQt5.QtWidgets import QHeaderView, QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget, QLabel, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QInputDialog, QLineEdit
from PyQt5.QtGui import QPalette, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import requests

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chemical Equipment Visualizer - Desktop")
        self.resize(1200, 700)  # for better display
        
        # styling
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(245, 246, 250))
        palette.setColor(QPalette.WindowText, QColor(40, 40, 40))
        self.setPalette(palette)

        self.setStyleSheet("""
            QMainWindow { background-color: #f5f6fa; }
            QTabWidget::pane { border: 1px solid #ddd; background: white; }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #357abd; }
            QTableWidget {
                gridline-color: #eee;
                alternate-background-color: #f9f9f9;
                selection-background-color: #4a90e2;
            }
            QLabel { font-size: 11pt; }
        """)
        
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Upload tab
        upload_tab = QWidget()
        self.tabs.addTab(upload_tab, "Upload CSV")
        upload_layout = QVBoxLayout(upload_tab)
        upload_label = QLabel("Select a CSV file to upload:")
        upload_layout.addWidget(upload_label)
        upload_button = QPushButton("Browse and Upload CSV")
        upload_layout.addWidget(upload_button)
        upload_button.clicked.connect(self.upload_csv)
        upload_layout.addStretch()  # Add flexible space
        
        # Summary tab
        summary_tab = QWidget()
        self.tabs.addTab(summary_tab, "Summary")
        summary_layout = QVBoxLayout(summary_tab)
        summary_button = QPushButton("Fetch Summary")
        summary_layout.addWidget(summary_button)
        summary_button.clicked.connect(self.fetch_summary)
        pdf_button = QPushButton("Download PDF Report") 
        summary_layout.addWidget(pdf_button)
        pdf_button.clicked.connect(self.download_pdf)
        self.summary_table = QTableWidget()
        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        summary_layout.addWidget(self.summary_table)
        summary_layout.addStretch()  # Add flexible space
        
        # History tab
        history_tab = QWidget()
        self.tabs.addTab(history_tab, "History")
        history_layout = QVBoxLayout(history_tab)
        history_button = QPushButton("Fetch History")
        history_layout.addWidget(history_button)
        history_button.clicked.connect(self.fetch_history)
        self.history_table = QTableWidget()
        self. history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels(["ID", "Upload Date", "Total Count", "Avg Flowrate", "Avg Pressure", "Avg Temperature", "Type Distribution"])
        self.history_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
        history_layout.addWidget(self.history_table)
        history_layout.addStretch()  # Add flexible space
                
        # Visualizations tab
        visualizations_tab = QWidget()
        self.tabs.addTab(visualizations_tab, "Visualizations")
        self.vis_layout = QVBoxLayout(visualizations_tab)  # Changed to self.vis_layout
        vis_button = QPushButton("Generate Visualizations")
        self.vis_layout.addWidget(vis_button)
        vis_button.clicked.connect(self.generate_visualizations)
        self.charts_layout = QHBoxLayout()
        self.vis_layout.addLayout(self.charts_layout)
        self.pie_canvas = None  # Add this line
        self.bar_canvas = None  # Add this line
        self.vis_layout.addStretch()  # Add flexible space
        
        # API base URL
        self.api_base = "http://localhost:8000/api/"
        
        # Prompt for username and password
        self.username, ok_username = QInputDialog.getText(self, "Authentication", "Enter your username:")
        if not ok_username:
            QMessageBox.critical(self, "Error", "Username is required. App will close.")
            sys.exit(1)  # Exit if canceled
        
        self.password, ok_password = QInputDialog.getText(self, "Authentication", "Enter your password:", QLineEdit.Password)
        if not ok_password:
            QMessageBox.critical(self, "Error", "Password is required. App will close.")
            sys.exit(1)  # Exit if canceled

    def upload_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_path:
            url = self.api_base + "upload/"
            try:
                with open(file_path, 'rb') as f:
                    files = {'file': f}
                    response = requests.post(url, files=files, auth=(self.username, self.password))
                if response.status_code in (200, 201):
                    QMessageBox.information(self, "Success", "CSV uploaded successfully!")
                else:
                    QMessageBox.warning(self, "Error", f"Upload failed. Status: {response.status_code}, Response: {response.text}")
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "Error", f"API connection failed: {str(e)}")

    def fetch_summary(self):
        url = self.api_base + "summary/"
        try:
            response = requests.get(url, auth=(self.username, self.password))
            if response.status_code == 200:
                data = response.json()
                self.summary_table.setRowCount(5)
                self.summary_table.setColumnCount(2)
                self.summary_table.setHorizontalHeaderLabels(["Statistic", "Value"])

                self.summary_table.setItem(0, 0, QTableWidgetItem("Total Count"))
                self.summary_table.setItem(0, 1, QTableWidgetItem(str(data.get('total_count', 0))))

                self.summary_table.setItem(1, 0, QTableWidgetItem("Avg Flowrate"))
                self.summary_table.setItem(1, 1, QTableWidgetItem(f"{data.get('avg_flowrate', 0):.2f}"))

                self.summary_table.setItem(2, 0, QTableWidgetItem("Avg Pressure"))
                self.summary_table.setItem(2, 1, QTableWidgetItem(f"{data.get('avg_pressure', 0):.2f}"))

                self.summary_table.setItem(3, 0, QTableWidgetItem("Avg Temperature"))
                self.summary_table.setItem(3, 1, QTableWidgetItem(f"{data.get('avg_temperature', 0):.1f}"))

                type_dist = data.get('type_distribution', {})
                self.summary_table.setItem(4, 0, QTableWidgetItem("Type Distribution"))
                self.summary_table.setItem(4, 1, QTableWidgetItem(str(type_dist)))
            else:
                QMessageBox.warning(self, "Error", f"Failed to fetch summary. Status: {response.status_code}, Response: {response.text}")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"API connection failed: {str(e)}")

    def fetch_history(self):
        url = self.api_base + "history/"
        try:
            response = requests.get(url, auth=(self.username, self.password))
            if response.status_code == 200:
                data = response.json()  # Assuming list of dicts
                self.history_table.setRowCount(len(data))
                self.history_table.setColumnCount(7)  # +1 for type dist
                self.history_table.setHorizontalHeaderLabels(["ID", "Upload Date", "Total Count", "Avg Flowrate", "Avg Pressure", "Avg Temperature", "Type Distribution"])
                for row, item in enumerate(data):
                    self.history_table.setItem(row, 0, QTableWidgetItem(str(item.get('id', 'N/A'))))
                    self.history_table.setItem(row, 1, QTableWidgetItem(item.get('upload_date', 'N/A')))
                    self.history_table.setItem(row, 2, QTableWidgetItem(str(item.get('total_count', 'N/A'))))
                    self.history_table.setItem(row, 3, QTableWidgetItem(f"{item.get('avg_flowrate', 'N/A'):.2f}"))
                    self.history_table.setItem(row, 4, QTableWidgetItem(f"{item.get('avg_pressure', 'N/A'):.2f}"))
                    self.history_table.setItem(row, 5, QTableWidgetItem(f"{item.get('avg_temperature', 'N/A'):.2f}"))  # Changed to .2f
                    self.history_table.setItem(row, 6, QTableWidgetItem(str(item.get('type_distribution', 'N/A'))))
            else:
                QMessageBox.warning(self, "Error", f"Failed to fetch history. Status: {response.status_code}, Response: {response.text}")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"API connection failed: {str(e)}")


    def generate_visualizations(self):
        url = self.api_base + "summary/"
        try:
            response = requests.get(url, auth=(self.username, self.password))
            if response.status_code == 200:
                data = response.json()
                # Clear existing charts
                if self.pie_canvas:
                    self.pie_canvas.setParent(None)
                if self.bar_canvas:
                    self.bar_canvas.setParent(None)
                
                # Colors to match web
                colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
                
                # Pie chart for type distribution (static)
                type_dist = data.get('type_distribution', {})
                total = sum(type_dist.values())
                if type_dist and total > 0:
                    labels = list(type_dist.keys())
                    values = list(type_dist.values())
                    
                    num_colors = len(labels)
                    pie_colors = [colors[i % len(colors)] for i in range(num_colors)]
                    
                    fig_pie, ax_pie = plt.subplots()
                    fig_pie.set_size_inches(6, 5)

                    ax_pie.pie(
                        values,
                        labels=labels,
                        autopct='%1.1f%%',
                        colors=pie_colors,
                        startangle=90,
                        shadow=False,
                        explode=[0.01] * len(values) if len(values) > 1 else None
                    )
                    ax_pie.set_title("Equipment Type Distribution")
                    ax_pie.axis('equal')

                    self.pie_canvas = FigureCanvas(fig_pie)
                    self.charts_layout.addWidget(self.pie_canvas)

                else:
                    # Fallback when no data or all zeros
                    fig_pie, ax_pie = plt.subplots()
                    fig_pie.set_size_inches(6, 5)
                    ax_pie.text(0.5, 0.5,
                                "No equipment types to display\n(Upload data first)",
                                ha='center', va='center', fontsize=11, color='gray')
                    ax_pie.set_title("Equipment Type Distribution")
                    ax_pie.axis('off')

                    self.pie_canvas = FigureCanvas(fig_pie)
                    self.charts_layout.addWidget(self.pie_canvas)
                
                # Bar chart for averages (static)
                stats_labels = ['Flowrate', 'Pressure', 'Temp']
                stats_values = [
                    float(data.get('avg_flowrate', 0)),
                    float(data.get('avg_pressure', 0)),
                    float(data.get('avg_temperature', 0))
                ]

                max_val = max(stats_values) if stats_values else 1.0
                upper_limit = max(max_val * 1.15, 1.0)

                fig_bar, ax_bar = plt.subplots(figsize=(6, 5))
                ax_bar.bar(stats_labels, stats_values, color='#36A2EB', width=0.6)

                ax_bar.set_title("Average Measurements", fontsize=13, pad=12)
                ax_bar.set_ylabel("Value", fontsize=11)
                ax_bar.set_ylim(0, upper_limit)

                ax_bar.grid(axis='y', linestyle='--', alpha=0.4)

                for i, val in enumerate(stats_values):
                    ax_bar.text(i, val + 0.05 * upper_limit, f"{val:.2f}", ha='center', va='bottom', fontsize=10)

                self.bar_canvas = FigureCanvas(fig_bar)
                self.charts_layout.addWidget(self.bar_canvas)
                
            else:
                QMessageBox.warning(self, "Error", f"Failed to fetch data for visualizations. Status: {response.status_code}, Response: {response.text}")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"API connection failed: {str(e)}")

    def download_pdf(self):
        url = self.api_base + "pdf/"
        try:
            response = requests.get(url, auth=(self.username, self.password), stream=True)
            if response.status_code == 200:
                file_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "report.pdf", "PDF Files (*.pdf)")
                if file_path:
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    QMessageBox.information(self, "Success", "PDF downloaded successfully!")
            else:
                QMessageBox.warning(self, "Error", f"Failed to download PDF. Status: {response.status_code}, Response: {response.text}")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"API connection failed: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())