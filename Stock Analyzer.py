import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import csv
from pathlib import Path



class StockOptionAnalyzer:
    def __init__(self):
        self.data = pd.DataFrame(columns=['date', 'price'])
        self.analysis_results = None
    
    def add_data_point(self, date_str, price):
        """Add a new data point to the analyzer."""
        try:
            date = pd.to_datetime(date_str).strftime('%Y/%m/%d')
            price = float(price)
            
            new_data = pd.DataFrame({'date': [date], 'price': [price]})
            self.data = pd.concat([self.data, new_data], ignore_index=True)
            self.data = self.data.sort_values('date').reset_index(drop=True)
            
            return True
        except Exception as e:
            print(f"Error adding data point: {e}")
            return False
    
    def calculate_metrics(self):
        """Calculate all metrics for the data points."""
        if len(self.data) < 1:
            return None
        
        # Convert dates to datetime
        self.data['date'] = pd.to_datetime(self.data['date'])
        
        # Calculate days since first entry
        first_date = self.data['date'].min()
        self.data['day'] = (self.data['date'] - first_date).dt.days
        
        # Calculate returns
        initial_price = self.data['price'].iloc[0]
        self.data['total_return'] = ((self.data['price'] - initial_price) / initial_price) * 100
        
        # Calculate dollar value per day
        self.data['dollar_value_per_day'] = self.data.apply(
            lambda row: (row['total_return'] * initial_price / 100) / max(1, row['day'])
            if row['day'] > 0 else 0, axis=1
        )
        
        return self.data
    
    def find_max_return_per_day(self):
        """Find the point with maximum return per day."""
        if len(self.data) < 2:
            return None
        
        self.calculate_metrics()
        max_return_idx = self.data['dollar_value_per_day'].idxmax()
        max_return_point = self.data.iloc[max_return_idx]
        
        return {
            'date': max_return_point['date'].strftime('%Y/%m/%d'),
            'day': int(max_return_point['day']),
            'price': max_return_point['price'],
            'total_return': max_return_point['total_return'],
            'dollar_value_per_day': max_return_point['dollar_value_per_day']
        }
    
    def plot_data(self):
        """Create plots of the price and returns data."""
        if len(self.data) < 2:
            print("Not enough data points to create a plot")
            return
        
        self.calculate_metrics()
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Plot option price
        ax1.plot(self.data['day'], self.data['price'], 'b-', label='Option Price')
        ax1.set_xlabel('Days')
        ax1.set_ylabel('Price ($)')
        ax1.set_title('Option Price Over Time')
        ax1.grid(True)
        ax1.legend()
        
        # Plot dollar value per day
        ax2.plot(self.data['day'], self.data['dollar_value_per_day'], 'g-', label='$/Day')
        ax2.set_xlabel('Days')
        ax2.set_ylabel('$/Day')
        ax2.set_title('Return per Day Over Time')
        ax2.grid(True)
        ax2.legend()
        
        plt.tight_layout()
        plt.show()
    
    def export_to_csv(self, filename):
        """Export data to a CSV file."""
        if len(self.data) < 1:
            print("No data to export")
            return False
        
        try:
            self.calculate_metrics()
            self.data.to_csv(filename, index=False)
            print(f"Data exported to {filename}")
            return True
        except Exception as e:
            print(f"Error exporting data: {e}")
            return False
    
    def import_from_csv(self, filename):
        """Import data from a CSV file."""
        try:
            imported_data = pd.read_csv(filename)
            required_columns = ['date', 'price']
            
            if not all(col in imported_data.columns for col in required_columns):
                print("CSV file must contain 'date' and 'price' columns")
                return False
            
            self.data = imported_data[required_columns]
            self.calculate_metrics()
            print(f"Successfully imported {len(self.data)} data points")
            return True
        except Exception as e:
            print(f"Error importing data: {e}")
            return False

def main():
    analyzer = StockOptionAnalyzer()
    
    while True:
        print("\nStock Option Analyzer")
        print("1. Add data point")
        print("2. View all data points")
        print("3. Calculate max return per day")
        print("4. Plot data")
        print("5. Export to CSV")
        print("6. Import from CSV")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ")
        
        if choice == '1':
            date = input("Enter date (YYYY-MM-DD): ")
            price = input("Enter price: ")
            if analyzer.add_data_point(date, price):
                print("Data point added successfully")
        
        elif choice == '2':
            if len(analyzer.data) > 0:
                print("\nCurrent Data Points:")
                print(analyzer.calculate_metrics().to_string())
            else:
                print("No data points available")
        
        elif choice == '3':
            max_return = analyzer.find_max_return_per_day()
            if max_return:
                print("\nMaximum Return Per Day:")
                print(f"Date: {max_return['date']}")
                print(f"Day: {max_return['day']}")
                print(f"Price: ${max_return['price']:.2f}")
                print(f"Total Return: {max_return['total_return']:.2f}%")
                print(f"$/Day: ${max_return['dollar_value_per_day']:.4f}")
            else:
                print("Not enough data points to calculate maximum return")
        
        elif choice == '4':
            analyzer.plot_data()
        
        elif choice == '5':
            filename = input("Enter filename to export (e.g., data.csv): ")
            analyzer.export_to_csv(filename)
        
        elif choice == '6':
            filename = input("Enter filename to import: ")
            analyzer.import_from_csv(filename)
        
        elif choice == '7':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
