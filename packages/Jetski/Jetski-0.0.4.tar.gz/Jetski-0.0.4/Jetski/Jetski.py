import datetime
import json
import prettytable 

class JetskiRental:
    def __init__(self,stock=0):
        self.stock = stock

    def displaystock(self):
        return self.stock

    def rentJetskiOnHourlyBasis(self, n):
        if n <= 0:
            print("Number of jetskis should be positive!")
            return None
        elif n > self.stock:
            print(f"Sorry! We have currently {self.stock} jetskis available to rent.")
            return None
        else:
            now = datetime.datetime.now()
            self.stock -= n
            return now

    def rentJetskiOnHalfDailyBasis(self, n):
        if n <= 0:
            print("Number of jetskis should be positive!")
            return None
        elif n > self.stock:
            print(f"Sorry! We have currently {self.stock} jetskis available to rent.")
            return None
        else:
            now = datetime.datetime.now()
            self.stock -= n
            return now

    def rentJetskiOnDailyBasis(self, n):
        if n <= 0:
            print("Number of jetskis should be positive!")
            return None
        elif n > self.stock:
            print(f"Sorry! We have currently {self.stock} jetskis available to rent.")
            return None
        else:
            now = datetime.datetime.now()            
            self.stock -= n
            return now


    def returnJetski(self, request):
        rentalTime, rentalBasis, numOfJetskis = request
        bill = 0

        if rentalTime and rentalBasis and numOfJetskis:
            self.stock += numOfJetskis
            now = datetime.datetime.now()
            rentalPeriod = now - rentalTime

            if rentalBasis == 1:
                bill = (rentalPeriod.seconds / 3600) * 55 * numOfJetskis

            elif rentalBasis == 2:
                bill = (rentalPeriod.seconds / (3600*4)) * 110 * numOfJetskis

            elif rentalBasis == 3:
                bill = (rentalPeriod.seconds / (3600*8)) * 165 * numOfJetskis

            # family discount calculation
            if (3 <= numOfJetskis <= 5):
                bill = bill * 0.8
            return bill
        else:
            print("Are you sure you rented a jetski with us?")
            return None
    
    # Save   
    def save_file(self, n=0, data={"Stock": 0, "Customers": {}}, filename="Jetski\JetskiInformation.json"):
        data["Stock"] = n
        with open(filename, "w") as file:
            json.dump(data, file)
            
    # Load
    def load_file(self, filename="Jetski\JetskiInformation.json"):
        try:
            with open(filename, "r") as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            return "We don't have that file..."


class Customer:
    def __init__(self):
        self.jetskis = 0
        self.rentalBasis = 0
        self.rentalTime = 0
        self.bill = 0

    def requestJetski(self):
        jetskis = input("How many jetskis would you like to rent? ")

        try:
            jetskis = int(jetskis)
        except ValueError:
            print("That's not a positive integer!")
            return -1

        if jetskis < 1:
            print("Invalid input. Number of jetskis should be greater than zero!")
            return -1
        else:
            self.jetskis = jetskis
        return self.jetskis

    def returnJetski(self):
        if self.rentalBasis and self.rentalTime and self.jetskis:
            return self.rentalTime, self.rentalBasis, self.jetskis
        else:
            return 0,0,0

def main():
    shop = JetskiRental()
    if shop.load_file()=="We don't have that file...":
        n = int(input("Enter the number of your shop's jetskis: "))
        shop.save_file(n)
        mydata = shop.load_file()
    else:
        mydata = shop.load_file()
        n = mydata['Stock']
        
    if n>0:
        while True:
            print("========= Menu =========")
            print("1: Display informations")
            print("2: To rent jetskis")
            print("3: To return jetskis")
            print("4: Exit and Save")
            choice = input("Enter your choice (1-4): ")
            
            if choice == '1':
                customer = Customer()
                myTable = prettytable.PrettyTable(["Customer", "Type", "Amount", "Start", "End", "Period(hrs)"])
                if mydata['Customers']=={}:
                    myTable.add_row(["-","-","-","-","-","-"])
                else:
                    for key,value in mydata['Customers'].items():
                        list_time  = value[2]
                        customer.rentalTime = datetime.datetime(*list_time)
                        myTable.add_row([key, 
                                        value[1], 
                                        value[0],
                                        customer.rentalTime,
                                        "-",
                                        "-",
                                        ])
                print(myTable)
                print(f"Stocks: {mydata['Stock']}")
                
            elif choice == '2':
                customer = Customer()
                name = input("Enter your name: ")
                jetskis = customer.requestJetski()
                if mydata["Stock"]>=jetskis and jetskis>=1:
                    mydata["Stock"] -= jetskis
                    rentalBasis = int(input("Choose the rentalBasis: 1(1 hr), 2(4 hrs), 3(8 hrs): "))
                    rentalTime = datetime.datetime.now()
                    date_list = list(rentalTime.timetuple())
                    del date_list[5:]
                    mydata['Customers'][name] = [jetskis, rentalBasis, date_list]
                    
                    # Table
                    myTable = prettytable.PrettyTable(["Customer", "Type", "Amount", "Start", "End", "Period(hrs)", "Discount($)", "Price($)"])
                    list_time  = mydata["Customers"][name][2]
                    customer.rentalTime = datetime.datetime(*list_time)
                    myTable.add_row([name, 
                                    mydata["Customers"][name][1], 
                                    mydata["Customers"][name][0],
                                    customer.rentalTime,
                                    "-","-","-","-"
                                    ])
                    print(myTable)
                    
                    shop.save_file(n=mydata["Stock"], data=mydata)
                
            elif choice == '3':
                customer = Customer()
                name = input("Enter your name: ")
                customer.jetskis = mydata["Customers"][name][0]
                customer.rentalBasis = mydata["Customers"][name][1]
                list_time  = mydata["Customers"][name][2]
                customer.rentalTime = datetime.datetime(*list_time)
                request = customer.returnJetski()
                bill = shop.returnJetski(request)
                
                if 3 <= mydata["Customers"][name][0] <= 5:
                    discount = bill/0.8 - bill
                else:
                    discount = 0
                
                End = datetime.datetime.now()
                Endlist = list(End.timetuple())
                del Endlist[5:]
                EndrentalTime = datetime.datetime(*Endlist)

                periodTime = datetime.datetime.now()-customer.rentalTime
                periodhour = (periodTime.seconds / 3600)
                myTable = prettytable.PrettyTable(["Customer", "Type", "Amount", "Start", "End", "Period(hrs)", "Discount($)", "Price($)"]) 
                myTable.add_row([name, 
                                mydata["Customers"][name][1], 
                                mydata["Customers"][name][0],
                                customer.rentalTime,
                                EndrentalTime,
                                f"{periodhour:.2f}",
                                f"{discount:.2f}",
                                f"{bill:.2f}"
                                ])
                print(myTable)
                
                mydata["Stock"] += mydata["Customers"][name][0]
                del mydata["Customers"][name]
                shop.save_file(n=mydata["Stock"], data=mydata)
                
            elif choice == '4':
                print("Exiting the program.")
                break
            else:
                print("Invalid choice! Please try again.")
    else:
        print("Invalid number!")
    
#Test   
if __name__ == '__main__':
    main()