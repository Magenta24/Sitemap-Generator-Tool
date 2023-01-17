from flask import Flask
app = Flask(__name__)

# @app.route("/")
# def spierdalaj():
# 	return 'xdxd'

def sayHello(name):
	print('hello ' + name)

def greet_bob(greeter):
	greeter("Bob")

def the_decorator(func):
	def wrapper(*args):
		print('hello ziomo')
		func(args[0])
		print('bye ziomo')

	return wrapper


# equals to xd = the_decorator(say_my_name)
@the_decorator
def say_my_name(name):
	print('siema mordo ' + name)

def fine(*args):
	print(args)
	return type(args)

def fine1(**kwargs):
	return type(kwargs)

def fine2(*args, **kwargs):
	print(args)
	print(kwargs)


say_my_name('seba')
help(Flask)