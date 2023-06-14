import sys
import time
import psutil
import netifaces
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QColor, QPen
import pyqtgraph as pg
from pyqtgraph import PlotWidget, PlotDataItem


class UsageHistoryPage(QWidget):
    def __init__(self, main_window):
        super(UsageHistoryPage, self).__init__()

        self.data = [0]  # Set initial data to 0
        self.layout = QVBoxLayout()
        self.bar_graph_widget = PlotWidget()
        self.bar_graph_widget.setYRange(0, 100, padding=0)
        self.bar_graph_widget.setBackground('#202124')
        self.bar_graph_widget.setTitle('Average Download Speed', color='white', size='14', bold=True)
        self.bar_graph_widget.setLabel('left', 'Download Speed (Mbps)', color='white', size='12', bold=True)
        self.bar_graph_widget.setLabel('bottom', 'Time (Minutes)', color='white', size='12', bold=True)
        self.bar_graph_widget.showGrid(x=True, y=True, alpha=0.3)
        self.bar_graph_item = PlotDataItem()
        self.bar_graph_widget.addItem(self.bar_graph_item)
        self.layout.addWidget(self.bar_graph_widget)

        # Back button
        back_button_layout = QHBoxLayout()
        self.back_button = QPushButton("Back")
        self.back_button.setStyleSheet("QPushButton { background-color: #000000; color: #FFFFFF; }"
                                       "QPushButton:hover { background-color: #C0C0C0; }")
        self.back_button.clicked.connect(main_window.toggle_page)
        back_button_layout.addWidget(self.back_button, 0, Qt.AlignmentFlag.AlignRight)
        self.layout.addLayout(back_button_layout)

        self.setLayout(self.layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_bar_graph)
        self.timer.start(60000)

    def update_bar_graph(self):
        try:
            download_speed = float(
                psutil.net_io_counters(pernic=True).get('en0', {}).get('bytes_recv', 0) / (1024 * 1024))
            self.data.append(download_speed)
        except KeyError:
            pass

        if len(self.data) > 60:
            self.data.pop(0)

        self.bar_graph_item.setData(y=self.data)


class NetworkThread(QThread):
    update_signal = pyqtSignal(int, int)
    running = True

    def run(self):
        while self.running:
            start_time = time.monotonic()

            # Correction here
            interfaces = psutil.net_io_counters(pernic=True)
            initial_download = interfaces.get('en0', psutil.net_io_counters()).bytes_recv
            initial_upload = interfaces.get('en0', psutil.net_io_counters()).bytes_sent

            time.sleep(1)

            # Correction here
            interfaces = psutil.net_io_counters(pernic=True)
            download_speed = (interfaces.get('en0', psutil.net_io_counters()).bytes_recv - initial_download) * 8
            upload_speed = (interfaces.get('en0', psutil.net_io_counters()).bytes_sent - initial_upload) * 8

            self.update_signal.emit(download_speed, upload_speed)
            end_time = time.monotonic()
            time.sleep(max(0, 1 - (end_time - start_time)))

    def stop(self):
        self.running = False


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Network stats graph
        self.network_stat_graph = PlotWidget()
        self.network_stat_graph.setBackground('#202124')
        self.network_stat_graph.setTitle("Live Network Usage", color='white', size='14pt')
        self.network_stat_graph.setLabel('left', 'Download Speed (Mbps)', color='white', size='12pt')
        self.network_stat_graph.setLabel('bottom', 'Time (s)', color='white', size='12pt')
        self.network_stat_graph.showGrid(x=True, y=True, alpha=0.3)
        self.download_speed_plot_data = self.network_stat_graph.plot([], pen=pg.mkPen(color=(118, 50, 168), width=3))
        self.layout.addWidget(self.network_stat_graph)

        # IPv4 Address
        ipv4_label = QLabel("IPv4 Address:")
        ipv4_label.setFont(QFont("Product Sans", 12))
        self.ipv4_address = QLabel("N/A")
        self.ipv4_address.setFont(QFont("Product Sans", 15, weight=QFont.Bold))
        ipv4_layout = QHBoxLayout()
        ipv4_layout.addWidget(ipv4_label)
        ipv4_layout.addWidget(self.ipv4_address)
        self.layout.addLayout(ipv4_layout)

        # Subnet
        subnet_label = QLabel("Subnet:")
        subnet_label.setFont(QFont("Product Sans", 12))
        self.subnet = QLabel("N/A")
        self.subnet.setFont(QFont("Product Sans", 15, weight=QFont.Bold))
        subnet_layout = QHBoxLayout()
        subnet_layout.addWidget(subnet_label)
        subnet_layout.addWidget(self.subnet)
        self.layout.addLayout(subnet_layout)

        # IPv6 Address
        ipv6_label = QLabel("IPv6 Address:")
        ipv6_label.setFont(QFont("Product Sans", 12))
        self.ipv6_address = QLabel("N/A")
        self.ipv6_address.setFont(QFont("Product Sans", 15, weight=QFont.Bold))
        ipv6_layout = QHBoxLayout()
        ipv6_layout.addWidget(ipv6_label)
        ipv6_layout.addWidget(self.ipv6_address)
        self.layout.addLayout(ipv6_layout)

        # Default Gateway
        default_gateway_label = QLabel("Default Gateway:")
        default_gateway_label.setFont(QFont("Product Sans", 12))
        self.default_gateway = QLabel("N/A")
        self.default_gateway.setFont(QFont("Product Sans", 15, weight=QFont.Bold))
        default_gateway_layout = QHBoxLayout()
        default_gateway_layout.addWidget(default_gateway_label)
        default_gateway_layout.addWidget(self.default_gateway)
        self.layout.addLayout(default_gateway_layout)

        # Buttons layout
        self.buttons_layout = QHBoxLayout()

        # Exit button
        self.exit_button = QPushButton("Exit")
        self.exit_button.setStyleSheet("QPushButton { background-color: #000000; color: #FFFFFF; }"
                                       "QPushButton:hover { background-color: #C0C0C0; }")
        self.exit_button.clicked.connect(self.close)

        # Add buttons to layout
        self.buttons_layout.addWidget(self.exit_button)

        # Add buttons layout to main layout
        self.layout.addLayout(self.buttons_layout)

        # Initialize network thread
        self.network_thread = NetworkThread()
        self.network_thread.update_signal.connect(self.update_graph)
        self.network_thread.start()

        # Initialize download speeds and upload speeds list
        self.download_speeds = []
        self.upload_speeds = []

        # Get network interface information
        self.get_network_interface_info()

        # Window settings
        self.setGeometry(100, 100, 800, 800)
        self.setWindowTitle("JW's Network Monitor")

    def update_graph(self, download_speed, upload_speed):
        # Convert download_speed and upload_speed to Mbps
        download_speed_mbps = download_speed / (1024 * 1024)
        upload_speed_mbps = upload_speed / (1024 * 1024)

        # Append speeds to the lists
        self.download_speeds.append(download_speed_mbps)
        self.upload_speeds.append(upload_speed_mbps)

        # Keep only the last 60 seconds of data
        if len(self.download_speeds) > 60:
            self.download_speeds.pop(0)
            self.upload_speeds.pop(0)

        # Update graph
        self.download_speed_plot_data.setData(self.download_speeds)

    def get_network_interface_info(self):
        try:
            # Retrieve the addresses associated with the network interfaces
            addresses = netifaces.ifaddresses('en0')
            # IPv4 information
            self.ipv4_address.setText(addresses[netifaces.AF_INET][0]['addr'])
            # Subnet mask
            self.subnet.setText(addresses[netifaces.AF_INET][0]['netmask'])
            # IPv6 information
            ipv6_addr = addresses[netifaces.AF_INET6][0]['addr'].split('%')[0]
            self.ipv6_address.setText(ipv6_addr)
            # Default gateway
            gws = netifaces.gateways()
            self.default_gateway.setText(gws['default'][netifaces.AF_INET][0])
        except (KeyError, IndexError):
            pass

    def closeEvent(self, event):
        # Stop the network thread when closing the application
        self.network_thread.stop()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
