from collections import defaultdict, UserDict
from datetime import datetime, timedelta
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)  
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if len(value) == 10 and value.isdigit():
            self.__value = value
        else:
            raise ValueError('Invalid phone number')


class Birthday(Field):
    def __init__(self, value):
        try:
            self.date = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(value)
        except ValueError:
            pass


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []


    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))


    def remove_phone(self, phone_number):
        self.phones = [p for p in self.phones if str(p) != phone_number]


    def edit_phone(self, old_phone, new_phone):
        self.delete_phone(old_phone)
        self.add_phone(new_phone)    


    def find_phone(self, phone):
        return phone in [str(p) for p in self.phones]    

    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)


    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        del self.data[name]
        

    def find_next_birthday(self, weekday):
        pass

    def get_upcoming_birthday(self, days=7):
        pass


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "KeyError"
        except ValueError:
            return "ValueError"
        except IndexError:
            return "IndexError"
    return wrapper


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, phone = args
    if name in book:
        book[name] = phone
        return "Contact updated successfully"
    else:
        return f"Contact {name} not found."


@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    if name in book:
        return f"Phone number for {name}: {book[name]}"
    else:
        return f"Contact {name} not found."



@input_error
def show_all(book: AddressBook):
    return "\n".join([f"Name: {name}, Phone: {phone}" for name, phone in book.items()])



@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added for {name}"
    else:
        return f"Contact {name} not found."



@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"Birthday for {name}: {record.birthday}"
    else:
        return f"No birthday found for {name}"



@input_error
def birthdays(args, book):
    today = datetime.now().date()
    end_of_week = today + timedelta(days=7)
    upcoming_birthdays = []
    for record in book.values():
        if record.birthday:
            next_birthday = record.birthday.date.replace(year=today.year)
            if today <= next_birthday <= end_of_week:
                upcoming_birthdays.append((record.name.value, next_birthday))
            elif next_birthday < today:
                next_birthday = record.birthday.date.replace(year=today.year + 1)
                if today <= next_birthday <= end_of_week:
                    upcoming_birthdays.append((record.name.value, next_birthday))
    upcoming_birthdays.sort(key=lambda x: x[1])
    if upcoming_birthdays:
        return "\n".join([f"{name}: {birthday}" for name, birthday in upcoming_birthdays])
    else:
        return "No upcoming birthdays in the next 7 days."



    


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


def save_data(book, filename):
    with open(filename, 'wb') as f:
        pickle.dump(book, f)


def load_data(filename):
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    filename = "address_book.pkl"
    book = load_data(filename)
    print("Welcome to the assistant bot!")

    try:
        while True:
            user_input = input("Enter a command: ")
            command, *args = parse_input(user_input)

            if command in ["close", "exit"]:
                save_data(book, filename)
                print("Address book saved.")
                print("Good bye!")
                break

            elif command == "hello":
                print("How can I help you?")

            elif command == "add":
                print(add_contact(args, book))

            elif command == "change":
                print(change_contact(args, book))

            elif command == "phone":
                print(show_phone(args, book))

            elif command == "all":
                print(show_all(book))

            elif command == "add-birthday":
                print(add_birthday(args, book))

            elif command == "show-birthday":
                print(show_birthday(args, book))

            elif command == "birthdays":
                print(birthdays(args, book))

            else:
                 print("Invalid command.")

    finally:
        save_data(book, filename)             

if __name__ == "__main__":
    main()