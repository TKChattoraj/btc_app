# Variables and Objects available throughout the application.
from wallet_database import MyDatabase

app_wallet = MyDatabase('wallet')

temp_factory = None

import tkinter as tk
from tkinter import ttk
btc_amount = None
