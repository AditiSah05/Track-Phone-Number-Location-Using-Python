import tkinter as tk
from tkinter import ttk, messagebox
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import folium
import webbrowser
import os
from geopy.geocoders import Nominatim

class NumberTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📱 Number Tracker with Location Map")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")
        
        # Store tracking data
        self.latitude = None
        self.longitude = None
        self.map_file = "Location_Map.html"
        
        self.create_widgets()
    
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill="x")
        
        title = tk.Label(header_frame, text="📱 Number Tracker", 
                        font=("Arial", 24, "bold"), fg="white", bg="#2c3e50")
        title.pack(pady=20)
        
        # Input Frame
        input_frame = tk.Frame(self.root, bg="#f0f0f0")
        input_frame.pack(pady=30)
        
        tk.Label(input_frame, text="Enter Phone Number (with country code):", 
                font=("Arial", 12), bg="#f0f0f0").pack()
        
        tk.Label(input_frame, text="Example: +919876543210", 
                font=("Arial", 9, "italic"), fg="#7f8c8d", bg="#f0f0f0").pack()
        
        self.number_entry = tk.Entry(input_frame, font=("Arial", 14), 
                                     width=25, justify="center")
        self.number_entry.pack(pady=10)
        
        # Track Button
        track_btn = tk.Button(input_frame, text="🔍 Track Number", 
                             font=("Arial", 12, "bold"), bg="#3498db", 
                             fg="white", cursor="hand2", padx=20, pady=10,
                             command=self.track_number)
        track_btn.pack(pady=10)
        
        # Results Frame
        self.results_frame = tk.Frame(self.root, bg="white", relief="solid", 
                                      borderwidth=1)
        self.results_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        tk.Label(self.results_frame, text="📊 Tracking Results", 
                font=("Arial", 14, "bold"), bg="white").pack(pady=10)
        
        # Result Labels
        self.result_labels = {}
        fields = ["Country", "Service Provider", "Time Zone", 
                 "Currency", "Symbol", "Latitude", "Longitude"]
        
        for field in fields:
            frame = tk.Frame(self.results_frame, bg="white")
            frame.pack(fill="x", padx=20, pady=5)
            
            tk.Label(frame, text=f"{field}:", font=("Arial", 10, "bold"), 
                    bg="white", width=15, anchor="w").pack(side="left")
            
            label = tk.Label(frame, text="-", font=("Arial", 10), 
                           bg="white", fg="#2c3e50", anchor="w")
            label.pack(side="left", fill="x", expand=True)
            self.result_labels[field] = label
        
        # Map Button
        self.map_btn = tk.Button(self.results_frame, text="🗺️ Show on Map", 
                                font=("Arial", 12, "bold"), bg="#27ae60", 
                                fg="white", cursor="hand2", padx=20, pady=10,
                                command=self.show_map, state="disabled")
        self.map_btn.pack(pady=20)
        
        # Footer
        footer = tk.Label(self.root, text="© 2025 Number Tracker | Educational Purpose Only", 
                         font=("Arial", 8), fg="#7f8c8d", bg="#f0f0f0")
        footer.pack(side="bottom", pady=10)
    
    def track_number(self):
        number = self.number_entry.get().strip()
        
        if not number:
            messagebox.showerror("Error", "Please enter a phone number!")
            return
        
        try:
            # Parse phone number
            parsed_number = phonenumbers.parse(number)
            
            if not phonenumbers.is_valid_number(parsed_number):
                messagebox.showerror("Error", "Invalid phone number!")
                return
            
            # Get country
            country = geocoder.description_for_number(parsed_number, "en")
            
            # Get service provider
            service_provider = carrier.name_for_number(parsed_number, "en")
            if not service_provider:
                service_provider = "Unknown"
            
            # Get timezone
            timezones = timezone.time_zones_for_number(parsed_number)
            tz = timezones[0] if timezones else "Unknown"
            
            # Get country code for currency
            region_code = phonenumbers.region_code_for_number(parsed_number)
            currency_info = self.get_currency_info(region_code)
            
            # Get coordinates
            self.get_coordinates(country)
            
            # Update UI
            self.result_labels["Country"].config(text=country or "Unknown")
            self.result_labels["Service Provider"].config(text=service_provider)
            self.result_labels["Time Zone"].config(text=tz)
            self.result_labels["Currency"].config(text=currency_info["name"])
            self.result_labels["Symbol"].config(text=currency_info["symbol"])
            
            if self.latitude and self.longitude:
                self.result_labels["Latitude"].config(text=f"{self.latitude:.4f}")
                self.result_labels["Longitude"].config(text=f"{self.longitude:.4f}")
                self.map_btn.config(state="normal")
            else:
                self.result_labels["Latitude"].config(text="Not available")
                self.result_labels["Longitude"].config(text="Not available")
                self.map_btn.config(state="disabled")
            
            messagebox.showinfo("Success", "Number tracked successfully!")
            
        except phonenumbers.NumberParseException:
            messagebox.showerror("Error", "Invalid number format! Use format: +[country code][number]")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def get_coordinates(self, location):
        try:
            geolocator = Nominatim(user_agent="number_tracker")
            loc = geolocator.geocode(location)
            
            if loc:
                self.latitude = loc.latitude
                self.longitude = loc.longitude
            else:
                self.latitude = None
                self.longitude = None
        except Exception as e:
            print(f"Geocoding error: {e}")
            self.latitude = None
            self.longitude = None
    
    def get_currency_info(self, country_code):
        # Currency mapping for common countries
        currencies = {
            "US": {"name": "US Dollar", "symbol": "$"},
            "IN": {"name": "Indian Rupee", "symbol": "₹"},
            "GB": {"name": "British Pound", "symbol": "£"},
            "CA": {"name": "Canadian Dollar", "symbol": "C$"},
            "AU": {"name": "Australian Dollar", "symbol": "A$"},
            "JP": {"name": "Japanese Yen", "symbol": "¥"},
            "CN": {"name": "Chinese Yuan", "symbol": "¥"},
            "DE": {"name": "Euro", "symbol": "€"},
            "FR": {"name": "Euro", "symbol": "€"},
            "IT": {"name": "Euro", "symbol": "€"},
            "ES": {"name": "Euro", "symbol": "€"},
            "BR": {"name": "Brazilian Real", "symbol": "R$"},
            "MX": {"name": "Mexican Peso", "symbol": "$"},
            "RU": {"name": "Russian Ruble", "symbol": "₽"},
            "KR": {"name": "South Korean Won", "symbol": "₩"},
            "ZA": {"name": "South African Rand", "symbol": "R"},
            "PK": {"name": "Pakistani Rupee", "symbol": "₨"},
            "BD": {"name": "Bangladeshi Taka", "symbol": "৳"},
            "NP": {"name": "Nepalese Rupee", "symbol": "रू"},
        }
        
        return currencies.get(country_code, {"name": "Unknown", "symbol": "-"})
    
    def show_map(self):
        if not self.latitude or not self.longitude:
            messagebox.showerror("Error", "Location coordinates not available!")
            return
        
        try:
            # Create map
            map_obj = folium.Map(location=[self.latitude, self.longitude], 
                                zoom_start=10)
            
            # Add marker
            folium.Marker(
                [self.latitude, self.longitude],
                popup=f"Tracked Location\nLat: {self.latitude:.4f}\nLon: {self.longitude:.4f}",
                tooltip="Click for details",
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(map_obj)
            
            # Save map
            map_obj.save(self.map_file)
            
            # Open in browser
            webbrowser.open('file://' + os.path.realpath(self.map_file))
            
            messagebox.showinfo("Success", "Map opened in your browser!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate map: {str(e)}")

def main():
    root = tk.Tk()
    app = NumberTrackerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()