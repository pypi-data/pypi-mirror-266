apiKey = "advcalc-oisdf8asdiufj9iuejisdfuj48ieujkassdfh834iuer84ue6479ureidjfhjiherjfug8ireuufh"
def advcalc(equation):
    print(eval(equation))
    
def add(num1, num2):
    sum = float(num1) + float(num2)
    print(sum)

def sub(num1, num2):
    sum = float(num1) - float(num2)
    print(sum)
    
def div(num1, num2):
    sum = float(num1) / float(num2)
    print(sum)
    
def mul(num1, num2):
    sum = float(num1) * float(num2)
    print(sum)

def sqrt(num):
    sum = float(num ** 0.5)
    print(sum)

def square(num):
    sum = float(num * num)
    print(sum)
    
def round_without_decimal_place(num):
    sum = float(round(num))
    print(sum)

def round_with_decimal_place(num,decimal):
    sum = float(round(num,decimal))
    print(sum)

def cube(num):
    sum = float(num**3)
    print(sum)
    
def cbrt(num):
    sum = float(num) ** (1. / 3)
    print(sum)

def pow(num1, num2):
    sum = float(num1) ** float(num2)
    print(sum)

def getAPIKey():
    print("Your API Key is:\n")
    print(f'{apiKey}')
    
def getCode(ApiKey):
    if str(ApiKey) == str(apiKey):
        print("""
def advcalc(equation):
    print(eval(equation))
    
def add(num1, num2):
    sum = float(num1) + float(num2)
    print(sum)

def sub(num1, num2):
    sum = float(num1) - float(num2)
    print(sum)
    
def div(num1, num2):
    sum = float(num1) / float(num2)
    print(sum)
    
def mul(num1, num2):
    sum = float(num1) * float(num2)
    print(sum)

def sqrt(num):
    sum = float(num ** 0.5)
    print(sum)

def square(num):
    sum = float(num * num)
    print(sum)
    
def round_without_decimal_place(num):
    sum = float(round(num))
    print(sum)

def round_with_decimal_place(num,decimal):
    sum = float(round(num,decimal))
    print(sum)

def cube(num):
    sum = float(num**3)
    print(sum)
    
def cbrt(num):
    sum = float(num) ** (1. / 3)
    print(sum)

def pow(num1, num2):
    sum = float(num1) ** float(num2)
    print(sum)""")
        
    else:
        print("Error: API Key does not exist.")