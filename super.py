# Imports
import sys
import argparse
import datetime
import csv
import os.path
import collections
from fpdf import FPDF

# Do not change these lines.
__winc_id__ = 'a2bc36ea784242e4989deb157d527ba0'
__human_name__ = 'superpy'

# Your code below this line.
APP_DESCRIPTION = """ PROGRAM DESCRIPTION"""

HELP_COMMAND = """Possible commands are: setdate, printdate, adjustdate, buy, sell, report_inventory, report_inventory_pdf, report_revenue, revenue_from, report_profit, profit_from, gets_expired"""
HELP_VALUE = """Defines the value to be used by the main command.
Example: python3 {0} setdate --value 2021-04-26
Example: python3 {0} adjustdate --value 2
Example: python3 {0} gets_expired --value 3""".format(sys.argv[0])
HELP_PRODNAME = """Defines the productname of the item bought or sold.
Example: python3 {0} buy --prodname orange""".format(sys.argv[0])
HELP_PRICE = """Defines the price of the item bought or sold.
Example: python3 {0} buy --price 0.8""".format(sys.argv[0])
HELP_EXPDATE = """Defines the expiry date of the item bought.
Example: python3 {0} buy --expdate 2021-06-14""".format(sys.argv[0])
HELP_NOW = """Defines current date, can be used with report_inventory and report_inventory_pdf.
Example: python3 {0} report_inventory --now
Example: python3 {0} report_inventory_pdf --now""".format(sys.argv[0])
HELP_YESTERDAY = """ Defines current date -1, can be used with report_inventory, report_inventory_pdf, report_revenue, report_profit.
Example: python3 {0} report_revenue --yesterday""".format(sys.argv[0])
HELP_TODAY = """Defines current date, can be used with report_revenue and report_profit.
Example: python3 {0} report_revenue --today""".format(sys.argv[0])
HELP_DATE = """Defines starting date for revenue_from and profit_from (end date is the date the program is set to)
Example: python3 {0} revenue_from --date 2021-04-01
Example: python3 {0} profit_from --date 2021-04-01""".format(sys.argv[0])


class Kassa():
    def __init__(self):
        if not os.path.exists("sold.csv"):
            open('sold.csv', 'w') #create file 'sold.csv' if it doesn't already exist
        if not os.path.exists("bought.csv"):
            open('bought.csv', 'w') #create file 'bought.csv' if it doesn't already exist
            
            
    def set_date(self, time_now):
        with open('datevalue.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([time_now]) #with this function you can set the date to a fixed date. It is called with the command 'setdate'.
            
        
    def print_date(self):
        with open('datevalue.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                return row[0]  #function returns the current date the program is set to. It is called with the command 'printdate'.
            
                
    def adjust_date(self, adjust_value):
        adjust_value =  int(adjust_value)
        saved_date = self.print_date()
        new_date = datetime.datetime.strptime(saved_date, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(days=adjust_value)
        self.set_date(new_date) #with this function you can adjust the date compared from the current date. It is called with the command 'adjustdate'.
        print('OK')
        
    
    def buy_item(self, prodname, price, expdate):
        number_of_lines = 0
        with open('bought.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                number_of_lines += 1 # reads the bought.csv. This is necessary to determine the next item_id.
            
        with open('bought.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            item_id = number_of_lines
            writer.writerow([item_id, self.print_date(), prodname, price, expdate]) #adds the buy to the 'bought.csv' file
            
    
    def sell_item(self, prodname, price):
        number_of_lines = 0
        with open('sold.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                number_of_lines += 1 # reads the sold.csv and counts the number of lines. This is necessary to determine the next id in the file.
                
        with open('bought.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            list_ids = []
            for row in reader:
                if prodname in row:
                    if datetime.datetime.strptime(self.print_date(), '%Y-%m-%d %H:%M:%S') < datetime.datetime.strptime((row[4]), '%Y-%m-%d %H:%M:%S'):
                        list_ids.append(row[0])  #creates a list with possible item ids of the specific productname that can be sold and are not expired.
        
        list_of_sold_ids = []
        with open('sold.csv', 'r', newline= '') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                list_of_sold_ids.append(row[1])  #creates a list of already sold item_ids
                
        for item_id in list_ids:
            if item_id not in list_of_sold_ids:     
                with open('sold.csv', 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([number_of_lines, item_id, self.print_date(), prodname, price])  #sells the first item_id item that is not already sold and adds a row to the 'sold.csv' file 
                    return 0   # to stop running of the code if an item is sold
                
        print("NO PRODUCT CAN BE SOLD") # message that will be printed if there is no unexpired product in stock.
        return 1
    
    
    def report_inventory(self, option): # this function returns the inventory in the 
        results, date = self.report_inventory_aux(option)
        
        print('+---------------------------------------------------------+')
        print('+ REPORT FOR THE DATE: {}                         |'.format(str(date)[:10]))
        print('+--------------+------------+-----------+-----------------+')
        print('| Product Name | Buy date   | Buy Price | Expiration Date |')
        print('+==============+============+===========+=================+')

        for row in results:
            name_to_print = row[0][:10] #to not print over 10 characters which will disturb the layout of the table             
            print('|', name_to_print+" "*(12-len(name_to_print)), '|', row[1][0:10], '|', row[2]+ " "*(9-len(row[2])), '|', row[3][0:10]+" "*5, '|') #lay-out fixings

        print('+==============+============+===========+=================+')
        
        
    def report_inventory_aux(self, option): #function to get the data from the inventory reported in the terminal
        actual_data = []
        
        with open('datevalue.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if option == "now":
                    date = datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') #gets current date from the datevalue.csv file
                if option == "yesterday":
                    date = datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') + datetime.timedelta(days=-1) #gets yesterdays date based on the current date from the datevalue.csv file
                    
        list_sold_ids = []
        with open('sold.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if date <= datetime.datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S'): 
                    list_sold_ids.append(row[1]) # creates a list of ids that have been sold on and before the set date ('now' or 'yesterday')
                    
        with open('bought.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                list_bought_ids = []
                if datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S') <= date: #products should be bought on or before the set date
                    if date < datetime.datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S'): #inventory can only contain non-expired items
                        list_bought_ids.append(row[0])
                        for item_id in list_bought_ids:
                            if item_id not in list_sold_ids: #items cannot be sold already
                                name_to_print = row[2][:10]
                                actual_data.append([name_to_print, row[1], row[3], row[4]])
        return (actual_data, date)
    
        
    def report_inventory_pdf(self, option): #function to get the data from the inventory reported in a PDF file
        results, date = self.report_inventory_aux(option) #getting the results and date calling the function report_inventory_aux
        
        pdf = FPDF() #calls PDF creator
        pdf.add_page()
        pdf.set_font("Arial", size = 20)
        pdf.cell(200, 10, txt = "SHO SUPERMARKET", ln = 1, align = 'C')
        pdf.set_font("Arial", size = 11)
        pdf.image('supermarket_cat_logo.jpeg', x = 70, y = None, w = 0, h = 50, type = '', link = '') #creates the supermarket logo (image)
        pdf.cell(200, 10, txt = "INVENTORY REPORT "+str(date)[:10], ln = 2, align = 'C')
        pdf.cell(200, 10, txt = "Amersfoort City Centre", ln = 2, align = 'C')
        
        pdf.cell(w = 45, h = 7, txt = 'Product Name', border = 1, ln = 0, align = 'L', fill = False, link = '')
        pdf.cell(w = 45, h = 7, txt = 'Buy Date', border = 1, ln = 0, align = 'L', fill = False, link = '')
        pdf.cell(w = 45, h = 7, txt = 'Buy Price (Euros)', border = 1, ln = 0, align = 'L', fill = False, link = '')
        pdf.cell(w = 45, h = 7, txt = 'Expiration Date', border = 1, ln = 1, align = 'L', fill = False, link = '')
        
        for row in results:
            pdf.cell(w = 45, h = 7, txt = str(row[0]), border = 1, ln = 0, align = 'L', fill = False, link = '')
            pdf.cell(w = 45, h = 7, txt = str(row[1][:10]), border = 1, ln = 0, align = 'L', fill = False, link = '')
            pdf.cell(w = 45, h = 7, txt = str(row[2]), border = 1, ln = 0, align = 'L', fill = False, link = '')
            pdf.cell(w = 45, h = 7, txt = str(row[3][:10]), border = 1, ln = 1, align = 'L', fill = False, link = '')
    
        pdf.output("supermarket_inventory_report.pdf")
        
    
    def report_revenue(self, option): #function to get revenue for 'today' or 'yesterday' 
        with open('datevalue.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if option == "today":
                    revenue_date = datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
                if option == "yesterday":
                    revenue_date = datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') + datetime.timedelta(days=-1)

                revenue = []
                with open('sold.csv', 'r', newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    for row in reader:
                        if revenue_date == datetime.datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S'):
                            revenue.append(float(row[4]))
                    print('{}\'s revenue is:'.format(option), round(sum(revenue), 2))
                    
    
    def revenue_from(self, date): #function to get revenue over a period of time, start date should be entered in command line, current date will be the end date the program is currently set to.
        current_date = self.print_date()
        revenue_period = []
        with open('sold.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if datetime.datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S') < datetime.datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S'): #selling date should be before current date
                    if datetime.datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S') >= datetime.datetime.strptime(date, '%Y-%m-%d'): #selling date should be equal or bigger than the entered start date
                        revenue_period.append(float(row[4]))
            print('revenue from {} is:'.format(date), round(sum(revenue_period), 2))
            
    
    def report_profit(self, option): #function to get profit for 'today' or 'yesterday' 
        with open('datevalue.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if option == "today":
                    profit_date = datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
                if option == "yesterday":
                    profit_date = datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') + datetime.timedelta(days=-1)

        revenue = []
        with open('sold.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if profit_date == datetime.datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S'):
                    revenue.append(float(row[4]))
            total_revenue = round(sum(revenue), 2) # I know it might have been better to reuse the report_revenue function here but due to a lack of time I did not manage to do that.
                
        expenses = []
        with open('bought.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if profit_date == datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S'):
                    expenses.append(float(row[3]))
            total_expenses = round(sum(expenses), 2)
                    
        profit = round((total_revenue - total_expenses), 2)
        print('{}\'s profit is'.format(option), profit)     
    
    
    def profit_from(self, date): #function to get profit over a period of time, start date should be entered in command line, current date will be the end date the program is currently set to.
        current_date = self.print_date()
        revenue_period = []
        with open('sold.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if datetime.datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S') < datetime.datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S'): #selling date should be before current date
                    if datetime.datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S') >= datetime.datetime.strptime(date, '%Y-%m-%d'): #selling date should be equal or bigger than the entered start date
                        revenue_period.append(float(row[4]))
            total_revenue_period = round(sum(revenue_period), 2) # I know it might have been better to reuse the revenue_from function here but due to a lack of time I did not manage to do that.
        
        expenses_period = []
        with open('bought.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S') < datetime.datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S'): #buying date should be before the current date
                    if datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S') >= datetime.datetime.strptime(date, '%Y-%m-%d'): #buying date should be equal or bigger than the entered start date
                        expenses_period.append(float(row[3]))
            total_expenses_period = round(sum(expenses_period), 2)
        
        profit_period = round((total_revenue_period - total_expenses_period), 2) 
        print('profit from {} is:'.format(date), profit_period)
        
        
    def to_get_expired(self, number_of_days): #function that lists the items from inventory which will be expired within now and x days
        results, date = self.report_inventory_aux("now")
        print(results)
        number_of_days =  int(number_of_days)
        current_date = self.print_date()
        new_date = datetime.datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(days=number_of_days) #add the amount of days by the given value of 'number_of_days'
        
        
        with open('to_get_expired.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for row in results:
                if datetime.datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S') >= datetime.datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S'): #expiration date should be equal or bigger than current date
                    if datetime.datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S') <= new_date: #expiration date should be smaller of equal to the 'date + x days' 
                        writer.writerow([row[0], row[1], row[2], row[3]])                      
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=APP_DESCRIPTION)
    parser.add_argument('command', type=str, help=HELP_COMMAND)
    parser.add_argument('--value', type=str, default=None, help=HELP_VALUE)
    parser.add_argument('--prodname', type=str, default=None, help=HELP_PRODNAME)
    parser.add_argument('--price', type=str, default=None, help=HELP_PRICE)
    parser.add_argument('--expdate', type=str, default=None, help=HELP_EXPDATE)
    parser.add_argument('--now', action='store_true', help=HELP_NOW) #to not expect another value after 'now'
    parser.add_argument('--yesterday', action='store_true', help=HELP_YESTERDAY) #to not expect another value after 'yesterday'
    parser.add_argument('--today', action='store_true', help=HELP_TODAY) #to not expect another value after 'today'
    parser.add_argument('--date', type=str, default=None, help=HELP_DATE)
    args = parser.parse_args()
    
    kassa = Kassa()
    
    if args.command == "setdate":
        time_now = datetime.datetime.strptime(args.value, '%Y-%m-%d')
        kassa.set_date(time_now)
    elif args.command == "printdate":
        print(kassa.print_date())
    elif args.command == "adjustdate":
        kassa.adjust_date(args.value)
    elif args.command == "buy":
        print(args.prodname, args.price, args.expdate)
        expirydate = datetime.datetime.strptime(args.expdate, '%Y-%m-%d')
        kassa.buy_item(args.prodname, args.price, expirydate)
    elif args.command == "sell":
        kassa.sell_item(args.prodname, args.price)
    elif args.command == "report_inventory":
        if args.now:
            kassa.report_inventory("now")
        elif args.yesterday:
            kassa.report_inventory("yesterday")
    elif args.command == "report_inventory_pdf":
        if args.now:
            kassa.report_inventory_pdf("now")
        elif args.yesterday:
            kassa.report_inventory_pdf("yesterday")
    elif args.command == "report_revenue":
        if args.today:
            kassa.report_revenue("today")
        elif args.yesterday:
            kassa.report_revenue("yesterday")
    elif args.command == "revenue_from":
        kassa.revenue_from(args.date)
    elif args.command == "report_profit":
        if args.today:
            kassa.report_profit("today")
        elif args.yesterday:
            kassa.report_profit("yesterday")
    elif args.command == "profit_from":
        kassa.profit_from(args.date)
    elif args.command == "gets_expired":
        kassa.to_get_expired(args.value)                   
    else:
        print("No valid command")
    