# liteexpr

A light, expression language.


## Overview

liteexpr is a general-purpose expression language for running simple
calculations.  It may be called from a host language, such as Python, to run
calculations inside a sandboxed environment.  The host language may pass
variables and functions to the evaluation environment to enrich its
capabilities.


## Example

```
# The host may alternatively pass students into the evaluation environment
students = [ "Alice", "Bob", "Charlie" ];

FOR(i = 0, i < LEN(students), i++,
    note = "";

    IF(students[i] == "Alice",
        note = " (she's my favorite)"
    );

    PRINT("Student #" + (i+1) + "'s name is " + students[i] + note)
);

# Return the number of students (last expression always returns its value)
LEN(students)
```

Like many expression languages, liteexpr uses functions for flow control, which
is the reason the syntax of `FOR` and `IF` resemble functions in the above
example.


## Supported Host Languages

* [C++](cpp)
* [Python](python)


## Data Types

* int - 64-bit signed integer
* double - 64-bit floating point number
* string
* function
* array
* object - for storing key-value pair data

An integer literal may be a decimal integer or a hexadecimal integer.
A decimal integer may not start with a 0.
A hexadecimal integer starts with the chracter sequence `0x`.

A double literal must start with one or more valid decimal digits, followed by a period, followed by one or more valid decimal digits.
The exponent format common in some languages that include the chracter literal `e` is not s upported.

A string literal begins and ends with the double quote character (`"`).
Any double quote chracter or backslash character must be prefixed (escaped) by the backslash character.
Other commonly used escape characters are supported, including the tab, (`\t`), the carriage return (`\r`), and the newline (`\n`).
An 8-bit unicode character may be embedded using its 2-digit hexadecimal code prefixed by `\x`,
a 16-bit unicode character may be embedded using its 4-digit hexadecimal code prefixed by `\u`,
and a 32-bit unicode character may be embedded using its 8-digit hexadecimal code prefixed by `\U`.

An array may contain elements of mixed type; for example, one array may contain one element that is an integer, and another that is a string.
An array may contain elements of any type, including arrays and objects.
An array literal is encapsulated in brackets (`[ ... ]`), with its elements separated by commas.
An array index must be contiguous.
The index of the first element in the array is 0.

An object stores key-value pairs.
An object literal is encapsulated in braces (`{ ... }`), with its elements separated by commas,
with each element's key-value pair separated by the colon (`:`).
The key must be a valid identifier.
The value may be of any data type, including arrays and objects.


## Variables

The name of a variable must be a valid identifier.
A valid identifier consists of one or more alphanumeric character and/or the underscore, except it may not start with a digit.

Variable names are case-sensitive.
By default, built-in variables are in all-caps;
it is recommended custom variable names include at least one lower case letter to avoid compatibility with future built-in variables.

A variable is not typed or declared.
The variable is instantiated the first time it is assigned a value.

If the variable contains an array,
its element may be accessed by the variable name followed by the array index in brackets (`[...]`).

If the variable contains an object,
the object's element may be accessed by the object's name followed by the period (`.`) and the key.


## Operations

Following are valid identifiers, in the order of highest to lowest precedence:

| Operator                                                                                              | Associativity[^1]         | Description                                                     |
| ----------------------------------------------------------------------------------------------------- | ------------------------- | --------------------------------------------------------------- |
| `( ... )`                                                                                             |                           | Grouping                                                        |
| `.`                                                                                                   |                           | Object member accessor                                          |
| `[ ... ]`                                                                                             |                           | Array element accessor                                          |
| `( ... )`                                                                                             |                           | Function call                                                   |
| `++` `--`                                                                                             |                           | Postfix increment, decrement                                    |
| `++` `--`                                                                                             |                           | Prefix increment, decrement                                     |
| `!`<br>`~`<br>`+` `-`                                                                                 |                           | Logical not<br>Bitwise not<br>Positive, negative                |
| `**`                                                                                                  | right-to-left             | Power                                                           |
| `*` `/` `%`                                                                                           |                           | Multiply, divide, modulus                                       |
| `+` `-`                                                                                               |                           | Add, subtract                                                   |
| `<<`<br>`>>`<br>`>>>`                                                                                 |                           | Left shift<br>Right shift sign-extended<br>Right shift unsigned |
| `<` `>` `<=` `>=`                                                                                     |                           | Inequality                                                      |
| `==` `!=`                                                                                             |                           | Equal to, not equal to                                          |
| `&`                                                                                                   |                           | Bitwise and                                                     |
| `^`                                                                                                   |                           | Bitwise xor                                                     |
| `\|`                                                                                                  |                           | Bitwise or                                                      |
| `&&`                                                                                                  |                           | Logical and                                                     |
| `\|\|`                                                                                                |                           | Logical or                                                      |
| `=`<br>`**=`<br>`*=` `/=` `%=`<br>`+=` `-=`<br>`<<=` `>>=` `>>>=`<br>`&=` `^=` `\|=`<br>`&&=` `\|\|=` | right-to-left             | Assignment                                                      |
| `? ... :`                                                                                             | right-to-left             | Ternary conditional                                             |
| `;`                                                                                                   |                           | Expression separator / terminator                               |

[^1]: Associativity is left-to-right unless noted otherwise.


## Built-In Functions

Following are functions built into liteexpr, arguments they accept, and their return values.

* `CEIL(int or double) -> int`
* `EVAL(string) -> any`
* `FLOOR(int or double) -> int`
* `FOR(expr1, expr2, expr3, expr4) -> any`[^2]
* `FOREACH(variable, iterable, expr) -> any`[^2]
* `FUNCTION(string, expr) -> function`[^2]
* `IF(expr1, then1, [expr2, then2, [expr3, then3, ...]], [else]) -> any`[^2]
* `LEN(string or array or object) -> int`
* `PRINT(any, [any, [any, ...]]) -> int`
* `ROUND(int or double) -> int`
* `SQRT(int or double) -> double`
* `WHILE(expr1, expr2) -> any`[^2]

[^2]: These functions' arguments are delay-evaluated.
Typically, arguments to a function are evaluated before the function is called in order to pass the results of the evaluation to the function.
However, flow-control functions such as `IF`, `FOR`, `FOREACH`, and `WHILE` need to be able to control when to evaluate its arguments;
in order to support this behavior, its arguments are passed to these functions, and the functions themselves choose when to evaluate the arguments.
Custom functions created with the `FUNCTION()` call always evaluate its arguments immediately;
it is not possible to create a custom function with delay-evaluated arguments.

The `FUNCTION()` function may be used to create a custom function within the expression;
it returns a function object which may be assigned to a variable to be called in a later part of the expression.

`FUNCTION()` takes two arguments:
The first argument is a character sequence (a string) that describes the number of arguments the custom function can accept;
the number of `?` characters in the string describes the [minimum] number of arguments expected by the function.
If the string ends with a `*`, the function can accept any number of additional arguments.

The second argument to `FUNCTION()` is the custom function's body.
The arguments passed to the function may be accessed through the automatic array variable `ARG`.

The custom function body has its own scope.
Assigning to a variable within the function scope instantiates a new variable within the function scope.
A variable instantiated outside of the function scope may only be read directly;
To write to variables instantiated outside of the function scope, use the following automatic variables:

* `GLOBAL` - An object that can be used to access global variables.
* `UPSCOPE` - An object that can be used to access variables one scope level above the function scope.


## License

[Apache 2.0](LICENSE)

