# Blind answer review

Fill labels.csv yourself before inspecting judge verdicts. No judge scores are included.

Correctness: 1 fully correct, 0.5 partial/incomplete, 0 incorrect or unjustified refusal.
Faithfulness: 1 every factual claim supported by retrieved text, 0 any unsupported claim.
Plausible outside knowledge or invented examples still count as unsupported.
A simple refusal contains no unsupported factual claims, but may be incorrect.

Compare the generated answer with the reference for correctness and with the retrieved
context for faithfulness. If a reference itself is flawed, record that in notes and
resolve the benchmark issue before interpreting judge agreement. Do not fabricate labels.

## q001 (direct)

Question: Which declaration is needed to read a cookie instead of a query parameter?

Reference: Use Cookie; without it the parameter is interpreted as a query parameter.

Generated answer: You must declare the parameter with `Cookie` (e.g., `my_cookie: str = Cookie(...)`) so that FastAPI treats it as a cookie rather than a query parameter. [ cookie-params.md::0 ]

Retrieved context:

### cookie-params.md::0

# Cookie Parameters { #cookie-parameters }

You can define Cookie parameters the same way you define `Query` and `Path` parameters.

## Import `Cookie` { #import-cookie }

First import `Cookie`:

## Declare `Cookie` parameters { #declare-cookie-parameters }

Then declare the cookie parameters using the same structure as with `Path` and `Query`.

You can define the default value as well as all the extra validation or annotation parameters:

/// note | Technical Details

`Cookie` is a "sister" class of `Path` and `Query`. It also inherits from

### cookie-params.md::1

tails

`Cookie` is a "sister" class of `Path` and `Query`. It also inherits from the same common `Param` class.

But remember that when you import `Query`, `Path`, `Cookie` and others from `fastapi`, those are actually functions that return special classes.

///

/// note

To declare cookies, you need to use `Cookie`, because otherwise the parameters would be interpreted as query parameters.

///

/// note

Have in mind that, as **browsers handle cookies** in special ways and behind the scenes, they **don't** easily allow **JavaScript** to

### header-params.md::0

# Header Parameters { #header-parameters }

You can define Header parameters the same way you define `Query`, `Path` and `Cookie` parameters.

## Import `Header` { #import-header }

First import `Header`:

## Declare `Header` parameters { #declare-header-parameters }

Then declare the header parameters using the same structure as with `Path`, `Query` and `Cookie`.

You can define the default value as well as all the extra validation or annotation parameters:

/// note | Technical Details

`Header` is a "sister" class of `Path`, `Query` and

### header-params.md::1

// note | Technical Details

`Header` is a "sister" class of `Path`, `Query` and `Cookie`. It also inherits from the same common `Param` class.

But remember that when you import `Query`, `Path`, `Header`, and others from `fastapi`, those are actually functions that return special classes.

///

/// note

To declare headers, you need to use `Header`, because otherwise the parameters would be interpreted as query parameters.

///

## Automatic conversion { #automatic-conversion }

`Header` has a little extra functionality on top of what `Path`,

### query-params.md::0

# Query Parameters { #query-parameters }

When you declare other function parameters that are not part of the path parameters, they are automatically interpreted as "query" parameters.

The query is the set of key-value pairs that go after the `?` in a URL, separated by `&` characters.

For example, in the URL:

```
http://127.0.0.1:8000/items/?skip=0&limit=10
```

...the query parameters are:

* `skip`: with a value of `0`
* `limit`: with a value of `10`

As they are part of the URL, they are "naturally" strings.

But when you declare them

## q006 (multi_part)

Question: How do I disable header underscore conversion, and what compatibility issue should I consider?

Reference: Set convert_underscores to False on Header. Some HTTP proxies and servers disallow headers containing underscores.

Generated answer: To stop FastAPI from turning underscores (`_`) in a header name into hyphens (`-`), set the `convert_underscores` argument of `Header` to `False`. However, be aware that many HTTP proxies and servers do not allow headers that contain underscores, so disabling the conversion may cause those proxies or servers to reject the request. [header-params.md::3][header-params.md::4]

Retrieved context:

### header-params.md::3

u can declare them with standard Python style (also known as "snake_case").

So, you can use `user_agent` as you normally would in Python code, instead of needing to capitalize the first letters as `User_Agent` or something similar.

If for some reason you need to disable automatic conversion of underscores to hyphens, set the parameter `convert_underscores` of `Header` to `False`:

/// warning

Before setting `convert_underscores` to `False`, bear in mind that some HTTP proxies and servers disallow the usage of headers with underscores.

///

### header-params.md::4

e HTTP proxies and servers disallow the usage of headers with underscores.

///

## Duplicate headers { #duplicate-headers }

It is possible to receive duplicate headers. That means, the same header with multiple values.

You can define those cases using a list in the type declaration.

You will receive all the values from the duplicate header as a Python `list`.

For example, to declare a header of `X-Token` that can appear more than once, you can write:

If you communicate with that *path operation* sending two HTTP headers like:

```

### header-params.md::2

c-conversion }

`Header` has a little extra functionality on top of what `Path`, `Query` and `Cookie` provide.

Most of the standard headers are separated by a "hyphen" character, also known as the "minus symbol" (`-`).

But a variable like `user-agent` is invalid in Python.

So, by default, `Header` will convert the parameter names characters from underscore (`_`) to hyphen (`-`) to extract and document the headers.

Also, HTTP headers are case-insensitive, so, you can declare them with standard Python style (also known as "snake_case").

So,

### header-params.md::1

// note | Technical Details

`Header` is a "sister" class of `Path`, `Query` and `Cookie`. It also inherits from the same common `Param` class.

But remember that when you import `Query`, `Path`, `Header`, and others from `fastapi`, those are actually functions that return special classes.

///

/// note

To declare headers, you need to use `Header`, because otherwise the parameters would be interpreted as query parameters.

///

## Automatic conversion { #automatic-conversion }

`Header` has a little extra functionality on top of what `Path`,

### header-params.md::0

# Header Parameters { #header-parameters }

You can define Header parameters the same way you define `Query`, `Path` and `Cookie` parameters.

## Import `Header` { #import-header }

First import `Header`:

## Declare `Header` parameters { #declare-header-parameters }

Then declare the header parameters using the same structure as with `Path`, `Query` and `Cookie`.

You can define the default value as well as all the extra validation or annotation parameters:

/// note | Technical Details

`Header` is a "sister" class of `Path`, `Query` and

## q008 (paraphrase)

Question: Can the detail of an HTTPException contain structured data rather than just text?

Reference: Yes. It accepts JSON-convertible values, including dictionaries and lists.

Generated answer: Yes. FastAPI’s `HTTPException` allows the `detail` field to be any JSON‑able value (e.g., a dict, list, etc.), not only a plain string [handling-errors.md::16][handling-errors.md::5].

Retrieved context:

### handling-errors.md::16

pts any JSON-able data for the `detail` field, while Starlette's `HTTPException` only accepts strings for it.

So, you can keep raising **FastAPI**'s `HTTPException` as normally in your code.

But when you register an exception handler, you should register it for Starlette's `HTTPException`.

This way, if any part of Starlette's internal code, or a Starlette extension or plug-in, raises a Starlette `HTTPException`, your handler will be able to catch and handle it.

In this example, to be able to have both `HTTPException`s in the same code,

### handling-errors.md::5

found" error), and a JSON response of:

```JSON
{
  "detail": "Item not found"
}
```

/// tip

When raising an `HTTPException`, you can pass any value that can be converted to JSON as the parameter `detail`, not only `str`.

You could pass a `dict`, a `list`, etc.

They are handled automatically by **FastAPI** and converted to JSON.

///

## Add custom headers { #add-custom-headers }

There are some situations where it's useful to be able to add custom headers to the HTTP error. For example, for some types of security.

You probably won't need

### handling-errors.md::15

"value is not a valid integer",
      "type": "type_error.integer"
    }
  ],
  "body": {
    "title": "towel",
    "size": "XL"
  }
}
```

#### FastAPI's `HTTPException` vs Starlette's `HTTPException` { #fastapis-httpexception-vs-starlettes-httpexception }

**FastAPI** has its own `HTTPException`.

And **FastAPI**'s `HTTPException` error class inherits from Starlette's `HTTPException` error class.

The only difference is that **FastAPI**'s `HTTPException` accepts any JSON-able data for the `detail` field, while Starlette's `HTTPException`

### handling-errors.md::1

cases, you would normally return an **HTTP status code** in the range of **400** (from 400 to 499).

This is similar to the 200 HTTP status codes (from 200 to 299). Those "200" status codes mean that somehow there was a "success" in the request.

The status codes in the 400 range mean that there was an error from the client.

Remember all those **"404 Not Found"** errors (and jokes)?

## Use `HTTPException` { #use-httpexception }

To return HTTP responses with errors to the client you use `HTTPException`.

### Import `HTTPException` {

### handling-errors.md::2

with errors to the client you use `HTTPException`.

### Import `HTTPException` { #import-httpexception }

### Raise an `HTTPException` in your code { #raise-an-httpexception-in-your-code }

`HTTPException` is a normal Python exception with additional data relevant for APIs.

Because it's a Python exception, you don't `return` it, you `raise` it.

This also means that if you are inside a utility function that you are calling inside of your *path operation function*, and you raise the `HTTPException` from inside of that utility function, it

## q005 (similar_page)

Question: How do I explicitly read a header versus a cookie, rather than treating either as a query parameter?

Reference: Use Header for headers and Cookie for cookies; without those declarations they are interpreted as query parameters.

Generated answer: To read a request header you must declare the parameter with `Header`; otherwise FastAPI would treat it as a query parameter.
To read a cookie you must declare the parameter with `Cookie`; otherwise it would also be interpreted as a query parameter.
Both `Header` and `Cookie` are “sister” classes of `Path` and `Query` that return special classes when imported from FastAPI.

Sources: [header-params.md::0], [cookie-params.md::0]

Retrieved context:

### header-params.md::0

# Header Parameters { #header-parameters }

You can define Header parameters the same way you define `Query`, `Path` and `Cookie` parameters.

## Import `Header` { #import-header }

First import `Header`:

## Declare `Header` parameters { #declare-header-parameters }

Then declare the header parameters using the same structure as with `Path`, `Query` and `Cookie`.

You can define the default value as well as all the extra validation or annotation parameters:

/// note | Technical Details

`Header` is a "sister" class of `Path`, `Query` and

### header-params.md::2

c-conversion }

`Header` has a little extra functionality on top of what `Path`, `Query` and `Cookie` provide.

Most of the standard headers are separated by a "hyphen" character, also known as the "minus symbol" (`-`).

But a variable like `user-agent` is invalid in Python.

So, by default, `Header` will convert the parameter names characters from underscore (`_`) to hyphen (`-`) to extract and document the headers.

Also, HTTP headers are case-insensitive, so, you can declare them with standard Python style (also known as "snake_case").

So,

### header-params.md::1

// note | Technical Details

`Header` is a "sister" class of `Path`, `Query` and `Cookie`. It also inherits from the same common `Param` class.

But remember that when you import `Query`, `Path`, `Header`, and others from `fastapi`, those are actually functions that return special classes.

///

/// note

To declare headers, you need to use `Header`, because otherwise the parameters would be interpreted as query parameters.

///

## Automatic conversion { #automatic-conversion }

`Header` has a little extra functionality on top of what `Path`,

### cookie-params.md::0

# Cookie Parameters { #cookie-parameters }

You can define Cookie parameters the same way you define `Query` and `Path` parameters.

## Import `Cookie` { #import-cookie }

First import `Cookie`:

## Declare `Cookie` parameters { #declare-cookie-parameters }

Then declare the cookie parameters using the same structure as with `Path` and `Query`.

You can define the default value as well as all the extra validation or annotation parameters:

/// note | Technical Details

`Cookie` is a "sister" class of `Path` and `Query`. It also inherits from

### cookie-params.md::1

tails

`Cookie` is a "sister" class of `Path` and `Query`. It also inherits from the same common `Param` class.

But remember that when you import `Query`, `Path`, `Cookie` and others from `fastapi`, those are actually functions that return special classes.

///

/// note

To declare cookies, you need to use `Cookie`, because otherwise the parameters would be interpreted as query parameters.

///

/// note

Have in mind that, as **browsers handle cookies** in special ways and behind the scenes, they **don't** easily allow **JavaScript** to

## q002 (direct)

Question: How does Header handle underscores in parameter names by default?

Reference: Header converts underscores to hyphens when extracting and documenting headers.

Generated answer: By default, `Header` automatically converts underscores (`_`) in parameter names to hyphens (`-`) when extracting and documenting HTTP headers. This allows you to use standard Python snake_case names (e.g., `user_agent`) while the actual header sent is `User-Agent`. The conversion can be disabled by setting `convert_underscores=False`, but some proxies/servers may then reject such headers. [header-params.md::2][header-params.md::0]

Retrieved context:

### header-params.md::3

u can declare them with standard Python style (also known as "snake_case").

So, you can use `user_agent` as you normally would in Python code, instead of needing to capitalize the first letters as `User_Agent` or something similar.

If for some reason you need to disable automatic conversion of underscores to hyphens, set the parameter `convert_underscores` of `Header` to `False`:

/// warning

Before setting `convert_underscores` to `False`, bear in mind that some HTTP proxies and servers disallow the usage of headers with underscores.

///

### header-params.md::4

e HTTP proxies and servers disallow the usage of headers with underscores.

///

## Duplicate headers { #duplicate-headers }

It is possible to receive duplicate headers. That means, the same header with multiple values.

You can define those cases using a list in the type declaration.

You will receive all the values from the duplicate header as a Python `list`.

For example, to declare a header of `X-Token` that can appear more than once, you can write:

If you communicate with that *path operation* sending two HTTP headers like:

```

### header-params.md::2

c-conversion }

`Header` has a little extra functionality on top of what `Path`, `Query` and `Cookie` provide.

Most of the standard headers are separated by a "hyphen" character, also known as the "minus symbol" (`-`).

But a variable like `user-agent` is invalid in Python.

So, by default, `Header` will convert the parameter names characters from underscore (`_`) to hyphen (`-`) to extract and document the headers.

Also, HTTP headers are case-insensitive, so, you can declare them with standard Python style (also known as "snake_case").

So,

### header-params.md::0

# Header Parameters { #header-parameters }

You can define Header parameters the same way you define `Query`, `Path` and `Cookie` parameters.

## Import `Header` { #import-header }

First import `Header`:

## Declare `Header` parameters { #declare-header-parameters }

Then declare the header parameters using the same structure as with `Path`, `Query` and `Cookie`.

You can define the default value as well as all the extra validation or annotation parameters:

/// note | Technical Details

`Header` is a "sister" class of `Path`, `Query` and

### query-params.md::0

# Query Parameters { #query-parameters }

When you declare other function parameters that are not part of the path parameters, they are automatically interpreted as "query" parameters.

The query is the set of key-value pairs that go after the `?` in a URL, separated by `&` characters.

For example, in the URL:

```
http://127.0.0.1:8000/items/?skip=0&limit=10
```

...the query parameters are:

* `skip`: with a value of `0`
* `limit`: with a value of `10`

As they are part of the URL, they are "naturally" strings.

But when you declare them

## q007 (multi_part)

Question: How can duplicate header values be declared, and what Python type receives their values?

Reference: Use a list in the type declaration; the duplicate values are received as a Python list.

Generated answer: Duplicate header values are declared by specifying the header’s type as a list in the parameter declaration, which tells the framework to collect all occurrences of that header. When a request contains the same header multiple times, the framework returns all of its values as a Python `list` [header-params.md::4].

Retrieved context:

### header-params.md::4

e HTTP proxies and servers disallow the usage of headers with underscores.

///

## Duplicate headers { #duplicate-headers }

It is possible to receive duplicate headers. That means, the same header with multiple values.

You can define those cases using a list in the type declaration.

You will receive all the values from the duplicate header as a Python `list`.

For example, to declare a header of `X-Token` that can appear more than once, you can write:

If you communicate with that *path operation* sending two HTTP headers like:

```

### header-params.md::2

c-conversion }

`Header` has a little extra functionality on top of what `Path`, `Query` and `Cookie` provide.

Most of the standard headers are separated by a "hyphen" character, also known as the "minus symbol" (`-`).

But a variable like `user-agent` is invalid in Python.

So, by default, `Header` will convert the parameter names characters from underscore (`_`) to hyphen (`-`) to extract and document the headers.

Also, HTTP headers are case-insensitive, so, you can declare them with standard Python style (also known as "snake_case").

So,

### header-params.md::0

# Header Parameters { #header-parameters }

You can define Header parameters the same way you define `Query`, `Path` and `Cookie` parameters.

## Import `Header` { #import-header }

First import `Header`:

## Declare `Header` parameters { #declare-header-parameters }

Then declare the header parameters using the same structure as with `Path`, `Query` and `Cookie`.

You can define the default value as well as all the extra validation or annotation parameters:

/// note | Technical Details

`Header` is a "sister" class of `Path`, `Query` and

### header-params.md::3

u can declare them with standard Python style (also known as "snake_case").

So, you can use `user_agent` as you normally would in Python code, instead of needing to capitalize the first letters as `User_Agent` or something similar.

If for some reason you need to disable automatic conversion of underscores to hyphens, set the parameter `convert_underscores` of `Header` to `False`:

/// warning

Before setting `convert_underscores` to `False`, bear in mind that some HTTP proxies and servers disallow the usage of headers with underscores.

///

### query-params-str-validations.md::31

estion.

...we do all this in a **single simple line**. 🤯 Don't you love Python? 🐍

## Recap { #recap }

You can declare additional validations and metadata for your parameters.

Generic validations and metadata:

* `alias`
* `title`
* `description`
* `deprecated`

Validations specific for strings:

* `min_length`
* `max_length`
* `pattern`

Custom validations using `AfterValidator`.

In these examples you saw how to declare validations for `str` values.

See the next chapters to learn how to declare validations for other types, like numbers.

## q009 (paraphrase)

Question: How can a query argument be made mandatory without assigning it a default?

Reference: Declare it without a default value.

Generated answer: A query argument becomes mandatory simply by **omitting any default value** when you declare it. If you write the parameter without “= …” (e.g., `q: str`), FastAPI treats it as required, forcing the client to supply a value. Providing a default— even `None`—makes the parameter optional, so leaving the default out is the way to make it required. [query-params.md::6]

Retrieved context:

### query-params.md::6

:

## Required query parameters { #required-query-parameters }

When you declare a default value for non-path parameters (for now, we have only seen query parameters), then it is not required.

If you don't want to add a specific value but just make it optional, set the default as `None`.

But when you want to make a query parameter required, you can just not declare any default value:

Here the query parameter `needy` is a required query parameter of type `str`.

If you open in your browser a URL like:

```

### path-params-numeric-validations.md::2

ter is always required as it has to be part of the path. Even if you declared it with `None` or set a default value, it would not affect anything, it would still be always required.

///

## Order the parameters as you need { #order-the-parameters-as-you-need }

/// tip

This is probably not as important or necessary if you use `Annotated`.

///

Let's say that you want to declare the query parameter `q` as a required `str`.

And you don't need to declare anything else for that parameter, so you don't really need to use `Query`.

But you still

### query-params-str-validations.md::16

e, use default values other than `None`.

Let's say that you want to declare the `q` query parameter to have a `min_length` of `3`, and to have a default value of `"fixedquery"`:

/// note

Having a default value of any type, including `None`, makes the parameter optional (not required).

///

## Required parameters { #required-parameters }

When we don't need to declare more validations or metadata, we can make the `q` query parameter required just by not declaring a default value, like:

```Python
q: str
```

instead of:

```Python
q: str |

### query-params-str-validations.md::18

required. This would force clients to send a value, even if the value is `None`.

To do that, you can declare that `None` is a valid type but simply do not declare a default value:

## Query parameter list / multiple values { #query-parameter-list-multiple-values }

When you define a query parameter explicitly with `Query` you can also declare it to receive a list of values, or said in another way, to receive multiple values.

For example, to declare a query parameter `q` that can appear multiple times in the URL, you can write:

Then, with a

### query-params-str-validations.md::17

ng a default value, like:

```Python
q: str
```

instead of:

```Python
q: str | None = None
```

But we are now declaring it with `Query`, for example like:

```Python
q: Annotated[str | None, Query(min_length=3)] = None
```

So, when you need to declare a value as required while using `Query`, you can simply not declare a default value:

### Required, can be `None` { #required-can-be-none }

You can declare that a parameter can accept `None`, but that it's still required. This would force clients to send a value, even if the value is `None`.

## q003 (direct)

Question: Should HTTPException be returned or raised?

Reference: It must be raised because it is a Python exception.

Generated answer: `HTTPException` should be **raised**, not returned; because it is a normal Python exception, you raise it to terminate the request and send the error response. [handling-errors.md::2]

Retrieved context:

### handling-errors.md::1

cases, you would normally return an **HTTP status code** in the range of **400** (from 400 to 499).

This is similar to the 200 HTTP status codes (from 200 to 299). Those "200" status codes mean that somehow there was a "success" in the request.

The status codes in the 400 range mean that there was an error from the client.

Remember all those **"404 Not Found"** errors (and jokes)?

## Use `HTTPException` { #use-httpexception }

To return HTTP responses with errors to the client you use `HTTPException`.

### Import `HTTPException` {

### handling-errors.md::2

with errors to the client you use `HTTPException`.

### Import `HTTPException` { #import-httpexception }

### Raise an `HTTPException` in your code { #raise-an-httpexception-in-your-code }

`HTTPException` is a normal Python exception with additional data relevant for APIs.

Because it's a Python exception, you don't `return` it, you `raise` it.

This also means that if you are inside a utility function that you are calling inside of your *path operation function*, and you raise the `HTTPException` from inside of that utility function, it

### handling-errors.md::3

ion*, and you raise the `HTTPException` from inside of that utility function, it won't run the rest of the code in the *path operation function*, it will terminate that request right away and send the HTTP error from the `HTTPException` to the client.

The benefit of raising an exception over returning a value will be more evident in the section about Dependencies and Security.

In this example, when the client requests an item by an ID that doesn't exist, raise an exception with a status code of `404`:

### The resulting response {

### handling-errors.md::6

he HTTP error. For example, for some types of security.

You probably won't need to use it directly in your code.

But in case you needed it for an advanced scenario, you can add custom headers:

## Install custom exception handlers { #install-custom-exception-handlers }

You can add custom exception handlers with [the same exception utilities from Starlette](https://starlette.dev/exceptions/).

Let's say you have a custom exception `UnicornException` that you (or a library you use) might `raise`.

And you want to handle this exception

### handling-errors.md::16

pts any JSON-able data for the `detail` field, while Starlette's `HTTPException` only accepts strings for it.

So, you can keep raising **FastAPI**'s `HTTPException` as normally in your code.

But when you register an exception handler, you should register it for Starlette's `HTTPException`.

This way, if any part of Starlette's internal code, or a Starlette extension or plug-in, raises a Starlette `HTTPException`, your handler will be able to catch and handle it.

In this example, to be able to have both `HTTPException`s in the same code,

## q004 (direct)

Question: Where do query parameters appear in a URL and how are they separated?

Reference: They follow the question mark and are separated by ampersands.

Generated answer: Query parameters appear after the `?` in a URL, and each key‑value pair is separated from the next by an `&` character.【query-params.md::0】

Retrieved context:

### query-params.md::0

# Query Parameters { #query-parameters }

When you declare other function parameters that are not part of the path parameters, they are automatically interpreted as "query" parameters.

The query is the set of key-value pairs that go after the `?` in a URL, separated by `&` characters.

For example, in the URL:

```
http://127.0.0.1:8000/items/?skip=0&limit=10
```

...the query parameters are:

* `skip`: with a value of `0`
* `limit`: with a value of `10`

As they are part of the URL, they are "naturally" strings.

But when you declare them

### query-params-str-validations.md::18

required. This would force clients to send a value, even if the value is `None`.

To do that, you can declare that `None` is a valid type but simply do not declare a default value:

## Query parameter list / multiple values { #query-parameter-list-multiple-values }

When you define a query parameter explicitly with `Query` you can also declare it to receive a list of values, or said in another way, to receive multiple values.

For example, to declare a query parameter `q` that can appear multiple times in the URL, you can write:

Then, with a

### query-params.md::1

ey are part of the URL, they are "naturally" strings.

But when you declare them with Python types (in the example above, as `int`), they are converted to that type and validated against it.

All the same processes that apply to path parameters also apply to query parameters:

* Editor support (obviously)
* Data <dfn title="converting the string that comes from an HTTP request into Python data">"parsing"</dfn>
* Data validation
* Automatic documentation

## Defaults { #defaults }

As query parameters are not a fixed part of a path, they can be

### query-params.md::4

` is not, so, it's a query parameter.

///

## Query parameter type conversion { #query-parameter-type-conversion }

You can also declare `bool` types, and they will be converted:

In this case, if you go to:

```
http://127.0.0.1:8000/items/foo?short=1
```

or

```
http://127.0.0.1:8000/items/foo?short=True
```

or

```
http://127.0.0.1:8000/items/foo?short=true
```

or

```
http://127.0.0.1:8000/items/foo?short=on
```

or

```
http://127.0.0.1:8000/items/foo?short=yes
```

or any other case variation (uppercase, first letter in uppercase,

### query-params.md::2

s { #defaults }

As query parameters are not a fixed part of a path, they can be optional and can have default values.

In the example above they have default values of `skip=0` and `limit=10`.

So, going to the URL:

```
http://127.0.0.1:8000/items/
```

would be the same as going to:

```
http://127.0.0.1:8000/items/?skip=0&limit=10
```

But if you go to, for example:

```
http://127.0.0.1:8000/items/?skip=20
```

The parameter values in your function will be:

* `skip=20`: because you set it in the URL
* `limit=10`: because that was the

## q011 (direct)

Question: What class should a request-body data model inherit from?

Reference: It should inherit from Pydantic BaseModel.

Generated answer: I cannot find this in the provided documentation.

Retrieved context:

### body.md::0

# Request Body { #request-body }

When you need to send data from a client (let's say, a browser) to your API, you send it as a **request body**.

A **request** body is data sent by the client to your API. A **response** body is the data your API sends to the client.

Your API almost always has to send a **response** body. But clients don't necessarily need to send **request bodies** all the time, sometimes they only request a path, maybe with some query parameters, but don't send a body.

To declare a **request** body, you use

### body.md::1

query parameters, but don't send a body.

To declare a **request** body, you use [Pydantic](https://pydantic.dev/docs/) models with all their power and benefits.

/// note

To send data, you should use one of: `POST` (the most common), `PUT`, `DELETE` or `PATCH`.

Sending a body with a `GET` request has an undefined behavior in the specifications, nevertheless, it is supported by FastAPI, only for very complex/extreme use cases.

As it is discouraged, the interactive docs with Swagger UI won't show the documentation for the body when using

### response-model.md::13

se will only include the fields declared in the response model.

In the previous example, because the classes were different, we had to use the `response_model` parameter. But that also means that we don't get the support from the editor and tools checking the function return type.

But in most of the cases where we need to do something like this, we want the model just to **filter/remove** some of the data as in this example.

And in those cases, we can use classes and inheritance to take advantage of function **type annotations** to get

### body.md::10

he attributes of the model object directly:

## Request body + path parameters { #request-body-path-parameters }

You can declare path parameters and request body at the same time.

**FastAPI** will recognize that the function parameters that match path parameters should be **taken from the path**, and that function parameters that are declared to be Pydantic models should be **taken from the request body**.

## Request body + path + query parameters { #request-body-path-query-parameters }

You can also declare **body**, **path** and **query**

### handling-errors.md::15

"value is not a valid integer",
      "type": "type_error.integer"
    }
  ],
  "body": {
    "title": "towel",
    "size": "XL"
  }
}
```

#### FastAPI's `HTTPException` vs Starlette's `HTTPException` { #fastapis-httpexception-vs-starlettes-httpexception }

**FastAPI** has its own `HTTPException`.

And **FastAPI**'s `HTTPException` error class inherits from Starlette's `HTTPException` error class.

The only difference is that **FastAPI**'s `HTTPException` accepts any JSON-able data for the `detail` field, while Starlette's `HTTPException`

## q012 (direct)

Question: When both response_model and a return type annotation are declared, which does FastAPI use?

Reference: FastAPI gives response_model priority.

Generated answer: FastAPI gives priority to the `response_model`; when both a return‑type annotation and a `response_model` are provided, FastAPI uses the `response_model` for documentation, validation, and response handling. [response-model.md::20]

Retrieved context:

### response-model.md::19

).

This simple case is handled automatically by FastAPI because the return type annotation is the class (or a subclass of) `Response`.

And tools will also be happy because both `RedirectResponse` and `JSONResponse` are subclasses of `Response`, so the type annotation is correct.

### Annotate a Response Subclass { #annotate-a-response-subclass }

You can also use a subclass of `Response` in the type annotation:

This will also work because `RedirectResponse` is a subclass of `Response`, and FastAPI will automatically handle this simple case.

### response-model.md::6

mypy, etc, you can declare the function return type as `Any`.

That way you tell the editor that you are intentionally returning anything. But FastAPI will still do the data documentation, validation, filtering, etc. with the `response_model`.

///

### `response_model` Priority { #response-model-priority }

If you declare both a return type and a `response_model`, the `response_model` will take priority and be used by FastAPI.

This way you can add correct type annotations to your functions even when you are returning a type different than

### response-model.md::20

subclass of `Response`, and FastAPI will automatically handle this simple case.

### Invalid Return Type Annotations { #invalid-return-type-annotations }

But when you return some other arbitrary object that is not a valid Pydantic type (e.g. a database object) and you annotate it like that in the function, FastAPI will try to create a Pydantic response model from that type annotation, and will fail.

The same would happen if you had something like a <dfn title='A union between multiple types means "any of these types".'>union</dfn> between

### response-model.md::22

ght not want to have the default data validation, documentation, filtering, etc. that is performed by FastAPI.

But you might want to still keep the return type annotation in the function to get the support from tools like editors and type checkers (e.g. mypy).

In this case, you can disable the response model generation by setting `response_model=None`:

This will make FastAPI skip the response model generation and that way you can have any return type annotations you need without it affecting your FastAPI application. 🤓

## Response Model

### response-model.md::5

function*, like all the parameters and body.

///

`response_model` receives the same type you would declare for a Pydantic model field, so, it can be a Pydantic model, but it can also be, e.g. a `list` of Pydantic models, like `List[Item]`.

FastAPI will use this `response_model` to do all the data documentation, validation, etc. and also to **convert and filter the output data** to its type declaration.

/// tip

If you have strict type checks in your editor, mypy, etc, you can declare the function return type as `Any`.

That way you tell

## q013 (direct)

Question: Should a dependency function be called when it is passed to Depends?

Reference: No. Pass the function itself without calling it.

Generated answer: No. You should pass the function itself to `Depends` without calling it (no parentheses); FastAPI will invoke the dependency function when handling a request【dependencies__index.md::6】.

Retrieved context:

### dependencies__index.md::6

only give `Depends` a single parameter.

This parameter must be something like a function.

You **don't call it** directly (don't add the parenthesis at the end), you just pass it as a parameter to `Depends()`.

And that function takes parameters in the same way that *path operation functions* do.

/// tip

You'll see what other "things", apart from functions, can be used as dependencies in the next chapter.

///

Whenever a new request arrives, **FastAPI** will take care of:

* Calling your dependency ("dependable") function with the correct

### dependencies__index.md::14

his case, **FastAPI**).

With the Dependency Injection system, you can also tell **FastAPI** that your *path operation function* also "depends" on something else that should be executed before your *path operation function*, and **FastAPI** will take care of executing it and "injecting" the results.

Other common terms for this same idea of "dependency injection" are:

* resources
* providers
* services
* injectables
* components

## **FastAPI** plug-ins { #fastapi-plug-ins }

Integrations and "plug-ins" can be built using the **Dependency

### dependencies__index.md::5

sions) to at least 0.95.1 before using `Annotated`.

///

### Import `Depends` { #import-depends }

### Declare the dependency, in the "dependant" { #declare-the-dependency-in-the-dependant }

The same way you use `Body`, `Query`, etc. with your *path operation function* parameters, use `Depends` with a new parameter:

Although you use `Depends` in the parameters of your function the same way you use `Body`, `Query`, etc, `Depends` works a bit differently.

You only give `Depends` a single parameter.

This parameter must be something like a

### dependencies__index.md::11

c` or not to `async` { #to-async-or-not-to-async }

As dependencies will also be called by **FastAPI** (the same as your *path operation functions*), the same rules apply while defining your functions.

You can use `async def` or normal `def`.

And you can declare dependencies with `async def` inside of normal `def` *path operation functions*, or `def` dependencies inside of `async def` *path operation functions*, etc.

It doesn't matter. **FastAPI** will know what to do.

/// note

If you don't know, check the [Async: *"In a

### dependencies__index.md::0

# Dependencies { #dependencies }

**FastAPI** has a very powerful but intuitive **<dfn title="also known as components, resources, providers, services, injectables">Dependency Injection</dfn>** system.

It is designed to be very simple to use, and to make it very easy for any developer to integrate other components with **FastAPI**.

## What is "Dependency Injection" { #what-is-dependency-injection }

**"Dependency Injection"** means, in programming, that there is a way for your code (in this case, your *path operation functions*) to declare

## q014 (direct)

Question: What status code does OAuth2PasswordBearer return when the Authorization header has no Bearer token?

Reference: It returns HTTP 401 Unauthorized.

Generated answer: OAuth2PasswordBearer returns a **401 UNAUTHORIZED** status code when the request lacks an `Authorization` header with a Bearer token. [security__first-steps.md::16]

Retrieved context:

### security__first-steps.md::8

res that token temporarily somewhere.
* The user clicks in the frontend to go to another section of the frontend web app.
* The frontend needs to fetch some more data from the API.
    * But it needs authentication for that specific endpoint.
    * So, to authenticate with our API, it sends a header `Authorization` with a value of `Bearer ` plus the token.
    * If the token contains `foobar`, the content of the `Authorization` header would be: `Bearer foobar`.

## **FastAPI**'s `OAuth2PasswordBearer` { #fastapis-oauth2passwordbearer }

### security__first-steps.md::16

o and look in the request for that `Authorization` header, check if the value is `Bearer ` plus some token, and will return the token as a `str`.

If it doesn't see an `Authorization` header, or the value doesn't have a `Bearer ` token, it will respond with a 401 status code error (`UNAUTHORIZED`) directly.

You don't even have to check if the token exists to return an error. You can be sure that if your function is executed, it will have a `str` in that token.

You can try it already in the interactive docs:

<img

### security__first-steps.md::15

an use the class `OAuth2PasswordBearer` (declared in a dependency) to define the security scheme in OpenAPI because it inherits from `fastapi.security.oauth2.OAuth2`, which in turn inherits from `fastapi.security.base.SecurityBase`.

All the security utilities that integrate with OpenAPI (and the automatic API docs) inherit from `SecurityBase`, that's how **FastAPI** can know how to integrate them in OpenAPI.

///

## What it does { #what-it-does }

It will go and look in the request for that `Authorization` header, check if the value is

### security__first-steps.md::9

r`.

## **FastAPI**'s `OAuth2PasswordBearer` { #fastapis-oauth2passwordbearer }

**FastAPI** provides several tools, at different levels of abstraction, to implement these security features.

In this example we are going to use **OAuth2**, with the **Password** flow, using a **Bearer** token. We do that using the `OAuth2PasswordBearer` class.

/// note

A "bearer" token is not the only option.

But it's the best one for our use case.

And it might be the best for most use cases, unless you are an OAuth2 expert and know exactly why there's

### security__first-steps.md::10

for most use cases, unless you are an OAuth2 expert and know exactly why there's another option that better suits your needs.

In that case, **FastAPI** also provides you with the tools to build it.

///

When we create an instance of the `OAuth2PasswordBearer` class we pass in the `tokenUrl` parameter. This parameter contains the URL that the client (the frontend running in the user's browser) will use to send the `username` and `password` in order to get a token.

/// tip

Here `tokenUrl="token"` refers to a relative URL `token` that we

## q015 (direct)

Question: Can a path parameter become optional by setting its default to None?

Reference: No. Path parameters are always required, even when a default or None is declared.

Generated answer: No. A path parameter is always required; setting a default value such as `None` does not make it optional【path-params-numeric-validations.md::2】.

Retrieved context:

### query-params.md::6

:

## Required query parameters { #required-query-parameters }

When you declare a default value for non-path parameters (for now, we have only seen query parameters), then it is not required.

If you don't want to add a specific value but just make it optional, set the default as `None`.

But when you want to make a query parameter required, you can just not declare any default value:

Here the query parameter `needy` is a required query parameter of type `str`.

If you open in your browser a URL like:

```

### path-params-numeric-validations.md::2

ter is always required as it has to be part of the path. Even if you declared it with `None` or set a default value, it would not affect anything, it would still be always required.

///

## Order the parameters as you need { #order-the-parameters-as-you-need }

/// tip

This is probably not as important or necessary if you use `Annotated`.

///

Let's say that you want to declare the query parameter `q` as a required `str`.

And you don't need to declare anything else for that parameter, so you don't really need to use `Query`.

But you still

### query-params-str-validations.md::18

required. This would force clients to send a value, even if the value is `None`.

To do that, you can declare that `None` is a valid type but simply do not declare a default value:

## Query parameter list / multiple values { #query-parameter-list-multiple-values }

When you define a query parameter explicitly with `Query` you can also declare it to receive a list of values, or said in another way, to receive multiple values.

For example, to declare a query parameter `q` that can appear multiple times in the URL, you can write:

Then, with a

### dependencies__index.md::3

all the same parameters that a *path operation function* can take:

That's it.

**2 lines**.

And it has the same shape and structure that all your *path operation functions* have.

You can think of it as a *path operation function* without the "decorator" (without the `@app.get("/some-path")`).

And it can return anything you want.

In this case, this dependency expects:

* An optional query parameter `q` that is a `str`.
* An optional query parameter `skip` that is an `int`, and by default is `0`.
* An optional query parameter `limit` that

### query-params-str-validations.md::16

e, use default values other than `None`.

Let's say that you want to declare the `q` query parameter to have a `min_length` of `3`, and to have a default value of `"fixedquery"`:

/// note

Having a default value of any type, including `None`, makes the parameter optional (not required).

///

## Required parameters { #required-parameters }

When we don't need to declare more validations or metadata, we can make the `q` query parameter required just by not declaring a default value, like:

```Python
q: str
```

instead of:

```Python
q: str |
