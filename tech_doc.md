This the fundamental language I want to support, nothing less, nothing more.

There are two types of assignments in Pineapple, a statement, and an inquiry.
All statements will present there errors, and halt the runtime.
All inquires will ignore any errors, and attempt to continue runtime.
A inquiry is considered solved if it is provided a fallback, or the errors are caught.
Inquires are meant to handle unknown contexts, and should only every run in a known, stable context.
Unbounded loops (while loops, for loops using runtime variables) will halt at the use of unsolvable inquires within them.

Reserved keywords & symbols
*all keywords must be 5 or less letters*
*any whole word with 6 letters or more is abbreviated*
*this includes primitive types*
*all classes are whole words, always*
```
~ keywords
~ convention: all single words with no separators, never more than 5 characters long

error | stop interpreter, and send error to stdout/stderr
fnc   | create a function with a literal declaration
obj   | create a class with a literal declaration
none  | represents a null/nothing value (declared name, no value)
while | create an unbounded loop
if    | create conditional
for   | create a bounded loop
in    | part of for statement
elif  | append to a conditional
else  | append to a conditional
and   | conditional operator, returns true if both conditionals are true
or    | conditional operators, returns true if at least one of the conditionals is true
not   | used to negate the comparison of conditional, resulting in the opposing state
try   | try something, ignores a runtime error that would normally halt the interpreter
catch | catch the error from a trying something, and do something with it
true  |
false |
_     | reference symbol for "owner" of the declaration, if used in scope of script, the script in-memory as a module is the owner,
        if used in scope of a class, it refers to the instatiation of that class.
[]    | used for the literal declaration of an Array
{}    | used for the literal declaration of a Dictionary



~ inline statements
~ convention: undetermined

| Loop Assignment (raises runtime errors) |
x = for num in numbers if num % 2 is 0

| Conditional Assignment (raises runtime errors) |
x = x if some_thing else none

| Inquiry Assignment (ignores runtime errors) |
x = some_thing() # fallback to none by default
x = some_thing() ? 0 # fallback to 0



~ built-in primitive types (not class, no methods)
~ convention: same as keywords

int
float
char


~ classes, all with helper methods
~ convention: PascalCase

Function
Class
Object
Error
String
Array
Dictionary



~ operators
~ convention: undetermined

+
-
*
/
=
+=
-=
*=
/=
%



~ functions
~ convention: Camel_Case, as they are callable objects (functions)
Out   | print to stdout, which usually goes to the terminal by default
In    | waits for input from stdin, which is usually from the terminal by default



~ importable variables
~ convention: same as keywords and primitive types
_path  | all directories, and files interpreter is aware of
_glbls | all classes, functions, and variables in the global scope





~ duck typing by default, but can explicitly type, and the type will be strict when used

~ some example code

x = [1,2,3]      # array declaration
y = {"a":1}      # dictionary declaration


obj Cat {
	name:String
	
	fnc init(name) _ {
		_.name = name
	}
}

greeting = "hello"

fnc say(msg:String) {
	Out(msg)
}

say(greeting)

fnc add(x:int, y:int) sum:int {
	sum = x + y
} ~ sum is returned at the end of the code block


fnc divide(x:int, y:int) q:int, r:int {
    q = x / y
    r = x % y
} ~ returns q, r

res = divide(10, 3)
Out(res.q, res.r)  # prints 3, 1

q, r = divide(5, 2)
Out(q, r)  # prints 2, 1


try {
	x = some_thing()
} catch e:Error {
	Out(e)
}


x = 5

fnc set_global() {
    _.x = 10  # modifies the global `x`, not a local shadow
    x = 5    # local variable with different value
}


fnc validate(value:int) {
    if value < 0 {
        error { Out("negative values not allowed") }
    }
}


for i in items {
    out(x)
}

for n in 10 {
    out(x)
}

```

For managing packages, and installing them, all packages will be added to a repository as pull requests, and afterward being merged, users can use the built-in package manager to download specific packages, hopefully this is okay with GitHub? We can always change it.


Ideas for additions afterward completion:
 - `with open` implementation of sort, probably using a while loop
 - `function are 'compiled' to actual python code for better reusability`, essentially creating a runtime compiler that can be used. this would probably be a complete rework to make the whole project compile to 'python' code before use, but that may also make implements other than functions slower. maybe we'll implement 'function compilation' of sorts only.
 - LSP for VSCode
 - Stupid little package manager for fun using the github repository idea