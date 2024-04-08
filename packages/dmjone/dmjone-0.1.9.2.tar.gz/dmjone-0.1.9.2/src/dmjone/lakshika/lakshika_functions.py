def calculate_area_of_rectangle():
    Length = int(input("enter length of rectangle: "))
    Breadth = int(input("enter breadth of rectangle: "))
    print("Area of rectangle is:", Length * Breadth)

def calculate_area_of_rectangle_float():
    Length = float(input("enter length of rectangle: "))
    Breadth = float(input("enter breadth of rectangle: "))
    print("Area of rectangle is:", int(Length) * int(Breadth))

def calculate_cube():
    cube = int(input("enter your number"))
    print("cube of given number is:", cube ** 3)

def student_details():
    name = input("enter you name: ")
    roll_num = input("enter your roll no.: ")
    field = input("enter field of interest: ")
    print('Hey, my name is', name, 'and my roll number is', roll_num, 'My field of interest is.', field)
