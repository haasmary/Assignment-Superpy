# Imports
import argparse
import datetime
import csv
import os.path
from fpdf import FPDF

# Do not change these lines.
__winc_id__ = 'a2bc36ea784242e4989deb157d527ba0'
__human_name__ = 'superpy'

# Your code below this line.

class Kassa:
    def __init__(self):
        if not os.path.exists("sold.csv"):
            open('sold.csv', 'w') #create file 'sold.csv' if it doesn't already exist
        if not os.path.exists("bought.csv"):
            open('bought.csv', 'w') #create file 'bought.csv' if it doesn't already exist

    def set_date(self, args):
        time_now = datetime.datetime.strptime(args.time_now, '%Y-%m-%d')
        with open('datevalue.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([time_now]) #with this function you can set the date to a fixed date. It is called with the command 'setdate'.
        self.print_date()

    def get_date(self):
        with open('datevalue.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                return row[0]  #function returns the current date the program is set to. It is called with the command 'printdate'.

    def print_date(self, args=None):
        print("Current date is set to: {}".format(self.get_date()))

    def adjust_date(self, args):
        adjust_value = int(args.days_differential)
        saved_date = self.get_date()
        new_date = datetime.datetime.strptime(saved_date, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(days=adjust_value)
        with open('datevalue.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([new_date]) #with this function you can set the date to a fixed date. It is called with the command 'setdate'.
        self.print_date()

    def buy_item(self, args):
        number_of_lines = 0
        with open('bought.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                number_of_lines += 1 # reads the bought.csv. This is necessary to determine the next item_id.
            
        with open('bought.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            item_id = number_of_lines
            writer.writerow([item_id, self.get_date(), args.prodname, args.price, args.expdate]) #adds the buy to the 'bought.csv' file

    def sell_item(self, args):
        number_of_lines = 0
        with open('sold.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                number_of_lines += 1 # reads the sold.csv and counts the number of lines. This is necessary to determine the next id in the file.
                
        with open('bought.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            list_ids = []
            for row in reader:
                if args.prodname in row:
                    if datetime.datetime.strptime(self.get_date(), '%Y-%m-%d %H:%M:%S') < datetime.datetime.strptime((row[4]), '%Y-%m-%d'):
                        list_ids.append(row[0])  #creates a list with possible item ids of the specific productname that can be sold and are not expired.
        
        list_of_sold_ids = []
        with open('sold.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                list_of_sold_ids.append(row[1])  #creates a list of already sold item_ids
                
        for item_id in list_ids:
            if item_id not in list_of_sold_ids:     
                with open('sold.csv', 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([number_of_lines, item_id, self.get_date(), args.prodname, args.price])  #sells the first item_id item that is not already sold and adds a row to the 'sold.csv' file
                    return 0   # to stop running of the code if an item is sold
                
        print("NO PRODUCT CAN BE SOLD") # message that will be printed if there is no unexpired product in stock.
        return 1

    def report_inventory(self, args):
        """returns the inventory of the supermarket on a specific date

        Keyword arguments:
        self: used to represent the instance of the class
        args.option: 'now' or 'yesterday', determines the date for which the inventory is made
        
        output: list of items printed in the terminal includes information: Product name, Buy date, Buy price, Expiration date"""
        option = args.option
        results, date = self.report_inventory_aux(option)
        
        print('+---------------------------------------------------------+')
        print('| REPORT FOR THE DATE: {}                         |'.format(str(date)[:10]))
        print('+--------------+------------+-----------+-----------------+')
        print('| Product Name | Buy date   | Buy Price | Expiration Date |')
        print('+==============+============+===========+=================+')

        for row in results:
            name_to_print = row[0][:10] #to not print over 10 characters which will disturb the layout of the table             
            print('|', name_to_print+" "*(12-len(name_to_print)), '|', row[1][0:10], '|', row[2]+ " "*(9-len(row[2])), '|', row[3][0:10]+" "*5, '|') #lay-out fixings

        print('+==============+============+===========+=================+')

    def report_inventory_aux(self, option):
        """gets the data for the inventory

        Keyword arguments:
        self: used to represent the instance of the class
        option: 'now' or 'yesterday', determines the date for which the inventory is made
        
        output: the inventory date and inventory items (actual_data): Product name, Buy date, Buy price, Expiration date"""
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
                    if date < datetime.datetime.strptime(row[4], '%Y-%m-%d'): #inventory can only contain non-expired items
                        list_bought_ids.append(row[0])
                        for item_id in list_bought_ids:
                            if item_id not in list_sold_ids: #items cannot be sold already
                                name_to_print = row[2][:10]
                                actual_data.append([name_to_print, row[1], row[3], row[4]])
        return (actual_data, date)

    def report_inventory_pdf(self, args):
        """gets the data from the inventory reported in a PDF file

        Keyword arguments:
        self: used to represent the instance of the class
        args.option: 'now' or 'yesterday', determines the date for which the inventory is made
        
        output: the inventory date and inventory items (actual_data): Product name, Buy date, Buy price, Expiration date IN PDF including supermarket logo"""
        option = args.option
        results, date = self.report_inventory_aux(option) #getting the results and date calling the function report_inventory_aux
        
        pdf = FPDF() #calls PDF creator
        pdf.add_page()
        pdf.set_font("Arial", size = 20)
        pdf.cell(200, 10, txt = "SHO SUPERMARKET", ln = 1, align = 'C')
        pdf.set_font("Arial", size = 11)
        try:
            pdf.image('supermarket_cat_logo.jpeg', x = 70, y = None, w = 0, h = 50, type = '', link = '') #creates the supermarket logo (image)
        except RuntimeError:
            print("Not necessary to create the pdf, but you should have the image of our supercat in the supermarket so that it can be included in the report!!")

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
        print("Report saved at your current folder: supermarket_inventory_report.pdf")

    def report_revenue(self, args):
        """gets revenue for 'today' or 'yesterday'

        Keyword arguments:
        self: used to represent the instance of the class
        option: 'today' or 'yesterday', determines the date for which the revenue is calculated
        
        output: today's or yesterday's revenue printed in terminal"""
        option = args.option
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

    def revenue_from(self, args):
        """get revenue over a period of time

        Keyword arguments:
        self: used to represent the instance of the class
        date: start date from which the revenue is calculated. End date will be the date the program is currently set to.
        
        output: revenue over a period of time printed in terminal"""
        date = args.date
        current_date = self.get_date()
        revenue_period = []
        with open('sold.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if datetime.datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S') < datetime.datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S'): #selling date should be before current date
                    if datetime.datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S') >= datetime.datetime.strptime(date, '%Y-%m-%d'): #selling date should be equal or bigger than the entered start date
                        revenue_period.append(float(row[4]))
            print('revenue from {} is:'.format(date), round(sum(revenue_period), 2))

    def report_profit(self, args):
        """gets profit for 'today' or 'yesterday'

        Keyword arguments:
        self: used to represent the instance of the class
        option: 'today' or 'yesterday', determines the date for which the profit is calculated
        
        output: today's or yesterday's profit printed in terminal"""
        option = args.option
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

    def profit_from(self, args):
        """get profit over a period of time

        Keyword arguments:
        self: used to represent the instance of the class
        date: start date from which the profit is calculated. End date will be the date the program is currently set to.
        
        output: profit over a period of time printed in terminal"""
        date = args.date
        current_date = self.get_date()
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

    def to_get_expired(self, args):
        """lists the items from inventory which will be expired within now and x days

        Keyword arguments:
        self: used to represent the instance of the class
        number_of_days: number of days in which user wants to see expired item list, counted from current date (date the program is set to)
        
        output: csv file with the items of the inventory that will expire within now and x days"""
        number_of_days = args.number_of_days
        results, date = self.report_inventory_aux("now")
        
        number_of_days =  int(number_of_days)
        current_date = self.get_date()
        new_date = datetime.datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(days=number_of_days) #add the amount of days by the given value of 'number_of_days'

        with open('to_get_expired.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for row in results:
                if datetime.datetime.strptime(row[3], '%Y-%m-%d') >= datetime.datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S'): #expiration date should be equal or bigger than current date
                    if datetime.datetime.strptime(row[3], '%Y-%m-%d') <= new_date: #expiration date should be smaller of equal to the 'date + x days'
                        writer.writerow([row[0], row[1], row[2], row[3]])
                        print("Currently unsold inventory item '{}' will expire on the date {}.".format(row[0], row[3]))
        

if __name__ == "__main__":
    kassa = Kassa()

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="Superpy commands", help="To learn more about a specific command, you can type <python3 {} [command] -h>".format(__file__))

    # Parser for set_date function
    parser_setdate = subparsers.add_parser('setdate', description="Manually specify the current date in YYYY-MM-DD format.")
    parser_setdate.add_argument('time_now', help="Example: <python3 {} setdate 2021-06-14>".format(__file__))
    parser_setdate.set_defaults(func=kassa.set_date)

    # Parser for adjust_date function
    parser_adjustdate = subparsers.add_parser('adjustdate', description="Change the currently set date by <days_differential> number of days.")
    parser_adjustdate.add_argument('days_differential', help="Example: <python3 {} adjustdate -3>".format(__file__))
    parser_adjustdate.set_defaults(func=kassa.adjust_date)

    # Parser for print_date function
    parser_printdate = subparsers.add_parser('printdate', description="Prints the currently set date.")
    parser_printdate.set_defaults(func=kassa.print_date)

    # Parser for buy_item function
    parser_buyitem = subparsers.add_parser('buyitem', description="Buys an item to be placed in the current stock. Example: <python3 {} buyitem orange 0.55 2021-07-01>".format(__file__))
    parser_buyitem.add_argument('prodname', help="Name of the item.")
    parser_buyitem.add_argument('price', help="Price paid to buy the item (decimal number).")
    parser_buyitem.add_argument('expdate', help="Expiry date of the item (YYYY-MM-DD).")
    parser_buyitem.set_defaults(func=kassa.buy_item)

    # Parser for sell_item function
    parser_sellitem = subparsers.add_parser('sellitem', description="Sells an item from the current stock. If item does not exist, will print an error message. Example: <python3 {} sellitem orange 0.75>".format(__file__))
    parser_sellitem.add_argument('prodname', help="Name of the item.")
    parser_sellitem.add_argument('price', help="Price the item is being sold for (decimal number).")
    parser_sellitem.set_defaults(func=kassa.sell_item)

    # Parser for report_inventory function
    parser_reportinventory = subparsers.add_parser('reportinventory', description="Displays the current inventory (unsold items). Example: <python3 {} reportinventory now".format(__file__))
    parser_reportinventory.add_argument('option', help="Report the inventory for 'now' or 'yesterday'")
    parser_reportinventory.set_defaults(func=kassa.report_inventory)

    # Parser for report_inventory_pdf function
    parser_reportinventorypdf = subparsers.add_parser('reportinventorypdf', description="Generates a pdf file with the current inventory (unsold items). Example: <python3 {} reportinventorypdf now".format(__file__))
    parser_reportinventorypdf.add_argument('option', help="Report the inventory for 'now' or 'yesterday'")
    parser_reportinventorypdf.set_defaults(func=kassa.report_inventory_pdf)

    # Parser for report_revenue function
    parser_reportrevenue = subparsers.add_parser('reportrevenue', description="Displays the current revenue (items sold). Example: <python3 {} reportrevenue today".format(__file__))
    parser_reportrevenue.add_argument('option', help="Report the revenue for 'today' or 'yesterday'")
    parser_reportrevenue.set_defaults(func=kassa.report_revenue)

    # Parser for revenue_from function
    parser_reportrevenuefrom = subparsers.add_parser('reportrevenuefrom', description="Displays the revenue (items sold) from <date> until the currently set date. Example: <python3 {} reportrevenuefrom 2021-01-01".format(__file__))
    parser_reportrevenuefrom.add_argument('date', help="Initial date in YYYY-MM-DD format")
    parser_reportrevenuefrom.set_defaults(func=kassa.revenue_from)

    # Parser for report_profit function
    parser_reportrevenue = subparsers.add_parser('reportprofit', description="Displays the current profit (items sold - items bought). Example: <python3 {} reportprofit today".format(__file__))
    parser_reportrevenue.add_argument('option', help="Report the profit for 'today' or 'yesterday'")
    parser_reportrevenue.set_defaults(func=kassa.report_profit)

    # Parser for profit_from function
    parser_reportrevenuefrom = subparsers.add_parser('reportprofitfrom', description="Displays the profit (items sold - items bought) from <date> until the currently set date. Example: <python3 {} reportrevenuefrom 2021-01-01".format(__file__))
    parser_reportrevenuefrom.add_argument('date', help="Initial date in YYYY-MM-DD format")
    parser_reportrevenuefrom.set_defaults(func=kassa.profit_from)

    # Parser for to_get_expired function
    parser_expiredcheck = subparsers.add_parser('expirycheck', description="Returns a list of items that will expire in <number_of_days> days. Example: <python3 {} expirycheck 5".format(__file__))
    parser_expiredcheck.add_argument('number_of_days', help="Integer to specify the number of days to look into the future")
    parser_expiredcheck.set_defaults(func=kassa.to_get_expired)
    
    args = parser.parse_args()
    args.func(args)

