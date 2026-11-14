# Blind answer review

Fill labels.csv yourself before inspecting judge verdicts. No judge scores are included.

Correctness: 1 fully correct, 0.5 partial/incomplete, 0 incorrect or unjustified refusal.
Faithfulness: 1 every factual claim supported by retrieved text, 0 any unsupported claim.
For unanswerable questions leave correctness/faithfulness blank and set abstention:
1 for correctly declining to invent an answer, 0 for supplying an invented answer.
Plausible outside knowledge or invented examples still count as unsupported.
A simple refusal contains no unsupported factual claims, but may be incorrect.

Compare the generated answer with the reference for correctness and with the retrieved
context for faithfulness. If a reference itself is flawed, record that in notes and
resolve the benchmark issue before interpreting judge agreement. Do not fabricate labels.

## q016 (direct)

Question: Why must /users/me be declared before /users/{user_id}?

Reference: Routes are evaluated in order; otherwise the variable route can match me as user_id.

Generated answer: Because FastAPI evaluates path operations in the order they are declared, the more specific static path `/users/me` must appear first so it matches before the generic `/users/{user_id}`. If the generic path is declared first, it would also match `/users/me` and treat “me” as a `user_id` value, preventing the intended handler from running. This ordering ensures the correct route is selected.【path-params.md::s6】

Retrieved context:

### path-params.md::s6

Several of these are explored in the next chapters of the tutorial.

## Order matters { #order-matters }

When creating *path operations*, you can find situations where you have a fixed path.

Like `/users/me`, let's say that it's to get data about the current user.

And then you can also have a path `/users/{user_id}` to get data about a specific user by some user ID.

Because *path operations* are evaluated in order, you need to make sure that the path for `/users/me` is declared before the one for `/users/{user_id}`:

Otherwise, the path for `/users/{user_id}` would match also for `/users/me`, "thinking" that it's receiving a parameter `user_id` with a value of `"me"`.

Similarly, you cannot redefine a path operation:

The first one will always be used since the path matches first.

## Predefined values { #predefined-values }

### response-model.md::s11

### Type Annotations and Tooling { #type-annotations-and-tooling }

First let's see how editors, mypy and other tools would see this.

`BaseUser` has the base fields. Then `UserIn` inherits from `BaseUser` and adds the `password` field, so, it will include all the fields from both models.

We annotate the function return type as `BaseUser`, but we are actually returning a `UserIn` instance.

The editor, mypy, and other tools won't complain about this because, in typing terms, `UserIn` is a subclass of `BaseUser`, which means it's a *valid* type when what is expected is anything that is a `BaseUser`.

### security__first-steps.md::s8

///

When we create an instance of the `OAuth2PasswordBearer` class we pass in the `tokenUrl` parameter. This parameter contains the URL that the client (the frontend running in the user's browser) will use to send the `username` and `password` in order to get a token.

/// tip

Here `tokenUrl="token"` refers to a relative URL `token` that we haven't created yet. As it's a relative URL, it's equivalent to `./token`.

Because we are using a relative URL, if your API was located at `https://example.com/`, then it would refer to `https://example.com/token`. But if your API was located at `https://example.com/api/v1/`, then it would refer to `https://example.com/api/v1/token`.

Using a relative URL is important to make sure your application keeps working even in an advanced use case like [Behind a Proxy](../../advanced/behind-a-proxy.md).

### first-steps.md::s14

...the path would be:

```
/items/foo
```

/// note

A "path" is also commonly called an "endpoint" or a "route".

///

While building an API, the "path" is the main way to separate "concerns" and "resources".

#### Operation { #operation }

"Operation" here refers to one of the HTTP "methods".

One of:

* `POST`
* `GET`
* `PUT`
* `DELETE`

### path-params-numeric-validations.md::s1

///

## Declare metadata { #declare-metadata }

You can declare all the same parameters as for `Query`.

For example, to declare a `title` metadata value for the path parameter `item_id` you can type:

/// note

A path parameter is always required as it has to be part of the path. Even if you declared it with `None` or set a default value, it would not affect anything, it would still be always required.

## q031 (multi_part)

Question: Can normal def and async def dependencies be mixed with either type of path-operation function?

Reference: Yes. Dependencies may use normal def or async def, and can be mixed with either kind of path-operation function.

Generated answer: Yes. FastAPI lets you use `async def` or normal `def` dependencies with both async and regular path‑operation functions; you can declare async dependencies inside normal functions and vice‑versa, and FastAPI will handle it correctly【dependencies__index.md::s10】.

Retrieved context:

### dependencies__index.md::s10

As dependencies will also be called by **FastAPI** (the same as your *path operation functions*), the same rules apply while defining your functions.

You can use `async def` or normal `def`.

And you can declare dependencies with `async def` inside of normal `def` *path operation functions*, or `def` dependencies inside of `async def` *path operation functions*, etc.

It doesn't matter. **FastAPI** will know what to do.

/// note

### dependencies__index.md::s5

///

### Import `Depends` { #import-depends }

### Declare the dependency, in the "dependant" { #declare-the-dependency-in-the-dependant }

The same way you use `Body`, `Query`, etc. with your *path operation function* parameters, use `Depends` with a new parameter:

Although you use `Depends` in the parameters of your function the same way you use `Body`, `Query`, etc, `Depends` works a bit differently.

You only give `Depends` a single parameter.

This parameter must be something like a function.

You **don't call it** directly (don't add the parenthesis at the end), you just pass it as a parameter to `Depends()`.

And that function takes parameters in the same way that *path operation functions* do.

### dependencies__index.md::s2

But this way we can focus on how the **Dependency Injection** system works.

### Create a dependency, or "dependable" { #create-a-dependency-or-dependable }

Let's first focus on the dependency.

It is just a function that can take all the same parameters that a *path operation function* can take:

That's it.

**2 lines**.

And it has the same shape and structure that all your *path operation functions* have.

You can think of it as a *path operation function* without the "decorator" (without the `@app.get("/some-path")`).

And it can return anything you want.

### dependencies__index.md::s6

/// tip

You'll see what other "things", apart from functions, can be used as dependencies in the next chapter.

///

Whenever a new request arrives, **FastAPI** will take care of:

* Calling your dependency ("dependable") function with the correct parameters.
* Get the result from your function.
* Assign that result to the parameter in your *path operation function*.

### first-steps.md::s18

///

### Step 4: define the **path operation function** { #step-4-define-the-path-operation-function }

This is our "**path operation function**":

* **path**: is `/`.
* **operation**: is `get`.
* **function**: is the function below the "decorator" (below `@app.get("/")`).

This is a Python function.

It will be called by **FastAPI** whenever it receives a request to the URL "`/`" using a `GET` operation.

In this case, it is an `async` function.

## q037 (paraphrase)

Question: My Python argument name cannot contain a dash, but the URL must use item-query. What feature maps those names?

Reference: Declare an alias for the query parameter; the alias is used to find its value.

Generated answer: You can use an **alias** for the query parameter: declare the Python‑compatible name (e.g., `item_query`) and set `alias="item-query"` so that FastAPI reads the value from the URL key `item-query` while the function argument keeps a valid Python identifier. [query-params-str-validations.md::s19]

Retrieved context:

### query-params-str-validations.md::s19

///

You can add a `title`:

And a `description`:

## Alias parameters { #alias-parameters }

Imagine that you want the parameter to be `item-query`.

Like in:

```
http://127.0.0.1:8000/items/?item-query=foobaritems
```

But `item-query` is not a valid Python variable name.

The closest would be `item_query`.

But you still need it to be exactly `item-query`...

Then you can declare an `alias`, and that alias is what will be used to find the parameter value:

## Deprecating parameters { #deprecating-parameters }

Now let's say you don't like this parameter anymore.

You have to leave it there a while because there are clients using it, but you want the docs to clearly show it as <dfn title="obsolete, recommended not to use it">deprecated</dfn>.

Then pass the parameter `deprecated=True` to `Query`:

The docs will show it like this:

### query-params.md::s1

As they are part of the URL, they are "naturally" strings.

But when you declare them with Python types (in the example above, as `int`), they are converted to that type and validated against it.

All the same processes that apply to path parameters also apply to query parameters:

* Editor support (obviously)
* Data <dfn title="converting the string that comes from an HTTP request into Python data">"parsing"</dfn>
* Data validation
* Automatic documentation

## Defaults { #defaults }

As query parameters are not a fixed part of a path, they can be optional and can have default values.

In the example above they have default values of `skip=0` and `limit=10`.

So, going to the URL:

```
http://127.0.0.1:8000/items/
```

### path-params.md::s0

# Path Parameters { #path-parameters }

You can declare path "parameters" or "variables" with the same syntax used by Python format strings:

The value of the path parameter `item_id` will be passed to your function as the argument `item_id`.

So, if you run this example and go to [http://127.0.0.1:8000/items/foo](http://127.0.0.1:8000/items/foo), you will see a response of:

```JSON
{"item_id":"foo"}
```

## Path parameters with types { #path-parameters-with-types }

You can declare the type of a path parameter in the function, using standard Python type annotations:

In this case, `item_id` is declared to be an `int`.

### query-params-str-validations.md::s15

To do that, you can declare that `None` is a valid type but simply do not declare a default value:

## Query parameter list / multiple values { #query-parameter-list-multiple-values }

When you define a query parameter explicitly with `Query` you can also declare it to receive a list of values, or said in another way, to receive multiple values.

For example, to declare a query parameter `q` that can appear multiple times in the URL, you can write:

Then, with a URL like:

```
http://localhost:8000/items/?q=foo&q=bar
```

you would receive the multiple `q` *query parameters'* values (`foo` and `bar`) in a Python `list` inside your *path operation function*, in the *function parameter* `q`.

So, the response to that URL would be:

```JSON
{
  "q": [
    "foo",
    "bar"
  ]
}
```

### path-params-numeric-validations.md::s4

///

Here's a **small trick** that can be handy, but you won't need it often.

If you want to:

* declare the `q` query parameter without a `Query` nor any default value
* declare the path parameter `item_id` using `Path`
* have them in a different order
* not use `Annotated`

...Python has a little special syntax for that.

Pass `*`, as the first parameter of the function.

Python won't do anything with that `*`, but it will know that all the following parameters should be called as keyword arguments (key-value pairs), also known as <abbr title="From: K-ey W-ord Arg-uments"><code>kwargs</code></abbr>. Even if they don't have a default value.

### Better with `Annotated` { #better-with-annotated }

Keep in mind that if you use `Annotated`, as you are not using function parameter default values, you won't have this problem, and you probably won't need to use `*`.

## q022 (similar_page)

Question: Which helpers add validation metadata to query parameters and path parameters respectively?

Reference: Use Query for query parameters and Path for path parameters.

Generated answer: The `Query` helper adds validation metadata to query parameters, while the `Path` helper does the same for path parameters【path-params-numeric-validations.md::s7】【query-params.md::s1】

Retrieved context:

### path-params-numeric-validations.md::s1

///

## Declare metadata { #declare-metadata }

You can declare all the same parameters as for `Query`.

For example, to declare a `title` metadata value for the path parameter `item_id` you can type:

/// note

A path parameter is always required as it has to be part of the path. Even if you declared it with `None` or set a default value, it would not affect anything, it would still be always required.

### path-params-numeric-validations.md::s7

## Recap { #recap }

With `Query`, `Path` (and others you haven't seen yet) you can declare metadata and string validations in the same ways as with [Query Parameters and String Validations](query-params-str-validations.md).

And you can also declare numeric validations:

* `gt`: `g`reater `t`han
* `ge`: `g`reater than or `e`qual
* `lt`: `l`ess `t`han
* `le`: `l`ess than or `e`qual

/// note

### query-params-str-validations.md::s0

# Query Parameters and String Validations { #query-parameters-and-string-validations }

**FastAPI** allows you to declare additional information and validation for your parameters.

Let's take this application as example:

The query parameter `q` is of type `str | None`, that means that it's of type `str` but could also be `None`, and indeed, the default value is `None`, so FastAPI will know it's not required.

### body.md::s8

* If the parameter is also declared in the **path**, it will be used as a path parameter.
* If the parameter is of a **singular type** (like `int`, `float`, `str`, `bool`, etc) it will be interpreted as a **query** parameter.
* If the parameter is declared to be of the type of a **Pydantic model**, it will be interpreted as a request **body**.

### query-params.md::s1

As they are part of the URL, they are "naturally" strings.

But when you declare them with Python types (in the example above, as `int`), they are converted to that type and validated against it.

All the same processes that apply to path parameters also apply to query parameters:

* Editor support (obviously)
* Data <dfn title="converting the string that comes from an HTTP request into Python data">"parsing"</dfn>
* Data validation
* Automatic documentation

## Defaults { #defaults }

As query parameters are not a fixed part of a path, they can be optional and can have default values.

In the example above they have default values of `skip=0` and `limit=10`.

So, going to the URL:

```
http://127.0.0.1:8000/items/
```

## q047 (unanswerable)

Question: What Alembic commands create and apply a PostgreSQL database migration for this application?

Reference: I cannot find this in the provided documentation.

Generated answer: I cannot find this in the provided documentation.

Retrieved context:

### dependencies__index.md::s17

## Integrated with **OpenAPI** { #integrated-with-openapi_1 }

All these dependencies, while declaring their requirements, also add parameters, validations, etc. to your *path operations*.

**FastAPI** will take care of adding it all to the OpenAPI schema, so that it is shown in the interactive documentation systems.

### dependencies__index.md::s13

Integrations and "plug-ins" can be built using the **Dependency Injection** system. But in fact, there is actually **no need to create "plug-ins"**, as by using dependencies it's possible to declare an infinite number of integrations and interactions that become available to your *path operation functions*.

And dependencies can be created in a very simple and intuitive way that allows you to just import the Python packages you need, and integrate them with your API functions in a couple of lines of code, *literally*.

You will see examples of this in the next chapters, about relational and NoSQL databases, security, etc.

### dependencies__index.md::s1

## What is "Dependency Injection" { #what-is-dependency-injection }

**"Dependency Injection"** means, in programming, that there is a way for your code (in this case, your *path operation functions*) to declare things that it requires to work and use: "dependencies".

And then, that system (in this case **FastAPI**) will take care of doing whatever is needed to provide your code with those needed dependencies ("inject" the dependencies).

This is very useful when you need to:

* Have shared logic (the same code logic again and again).
* Share database connections.
* Enforce security, authentication, role requirements, etc.
* And many other things...

All these, while minimizing code repetition.

## First Steps { #first-steps }

Let's see a very simple example. It will be so simple that it is not very useful, for now.

### dependencies__index.md::s14

## **FastAPI** compatibility { #fastapi-compatibility }

The simplicity of the dependency injection system makes **FastAPI** compatible with:

* all the relational databases
* NoSQL databases
* external packages
* external APIs
* authentication and authorization systems
* API usage monitoring systems
* response data injection systems
* etc.

### first-steps.md::s11

Additionally, other tools might not be able to find it, for example the [VS Code Extension](../editor-support.md) or [FastAPI Cloud](https://fastapicloud.com), so it is recommended to use the `entrypoint` in `pyproject.toml`.

### Deploy your app (optional) { #deploy-your-app-optional }

You can optionally deploy your FastAPI app to [FastAPI Cloud](https://fastapicloud.com) with a single command. 🚀

## q017 (direct)

Question: Which query declaration option hides a parameter from OpenAPI documentation?

Reference: Set Query include_in_schema to False.

Generated answer: Set the `include_in_schema` argument of the `Query` declaration to `False` to hide that query parameter from the generated OpenAPI documentation. [query-params-str-validations.md::s20]

Retrieved context:

### query-params-str-validations.md::s18

///

## Declare more metadata { #declare-more-metadata }

You can add more information about the parameter.

That information will be included in the generated OpenAPI and used by the documentation user interfaces and external tools.

/// note

Keep in mind that different tools might have different levels of OpenAPI support.

Some of them might not show all the extra information declared yet, although in most of the cases, the missing feature is already planned for development.

### query-params-str-validations.md::s20

<img src="/img/tutorial/query-params-str-validations/image01.png">

## Exclude parameters from OpenAPI { #exclude-parameters-from-openapi }

To exclude a query parameter from the generated OpenAPI schema (and thus, from the automatic documentation systems), set the parameter `include_in_schema` of `Query` to `False`:

### query-params-str-validations.md::s5

Here we are using `Query()` because this is a **query parameter**. Later we will see others like `Path()`, `Body()`, `Header()`, and `Cookie()`, that also accept the same arguments as `Query()`.

///

FastAPI will now:

* **Validate** the data making sure that the max length is 50 characters
* Show a **clear error** for the client when the data is not valid
* **Document** the parameter in the OpenAPI schema *path operation* (so it will show up in the **automatic docs UI**)

### query-params-str-validations.md::s0

# Query Parameters and String Validations { #query-parameters-and-string-validations }

**FastAPI** allows you to declare additional information and validation for your parameters.

Let's take this application as example:

The query parameter `q` is of type `str | None`, that means that it's of type `str` but could also be `None`, and indeed, the default value is `None`, so FastAPI will know it's not required.

### query-params.md::s0

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

## q032 (multi_part)

Question: What happens if HTTPException is raised inside a utility called by a path operation, and does the remaining path-operation code execute?

Reference: The request terminates immediately, the HTTP error is sent to the client, and the remaining path-operation code does not execute.

Generated answer: When an `HTTPException` is raised inside a utility function that a path‑operation function calls, the exception aborts the request immediately; the rest of the code in the path‑operation function is **not** executed, and FastAPI sends the HTTP error response to the client. [handling-errors.md::s1]

Retrieved context:

### handling-errors.md::s1

To return HTTP responses with errors to the client you use `HTTPException`.

### Import `HTTPException` { #import-httpexception }

### Raise an `HTTPException` in your code { #raise-an-httpexception-in-your-code }

`HTTPException` is a normal Python exception with additional data relevant for APIs.

Because it's a Python exception, you don't `return` it, you `raise` it.

This also means that if you are inside a utility function that you are calling inside of your *path operation function*, and you raise the `HTTPException` from inside of that utility function, it won't run the rest of the code in the *path operation function*, it will terminate that request right away and send the HTTP error from the `HTTPException` to the client.

The benefit of raising an exception over returning a value will be more evident in the section about Dependencies and Security.

### handling-errors.md::s12

So, you can keep raising **FastAPI**'s `HTTPException` as normally in your code.

But when you register an exception handler, you should register it for Starlette's `HTTPException`.

This way, if any part of Starlette's internal code, or a Starlette extension or plug-in, raises a Starlette `HTTPException`, your handler will be able to catch and handle it.

In this example, to be able to have both `HTTPException`s in the same code, Starlette's exceptions is renamed to `StarletteHTTPException`:

```Python
from starlette.exceptions import HTTPException as StarletteHTTPException
```

### Reuse **FastAPI**'s exception handlers { #reuse-fastapis-exception-handlers }

If you want to use the exception along with the same default exception handlers from  **FastAPI**, you can import and reuse the default exception handlers from `fastapi.exception_handlers`:

### first-steps.md::s14

...the path would be:

```
/items/foo
```

/// note

A "path" is also commonly called an "endpoint" or a "route".

///

While building an API, the "path" is the main way to separate "concerns" and "resources".

#### Operation { #operation }

"Operation" here refers to one of the HTTP "methods".

One of:

* `POST`
* `GET`
* `PUT`
* `DELETE`

### first-steps.md::s18

///

### Step 4: define the **path operation function** { #step-4-define-the-path-operation-function }

This is our "**path operation function**":

* **path**: is `/`.
* **operation**: is `get`.
* **function**: is the function below the "decorator" (below `@app.get("/")`).

This is a Python function.

It will be called by **FastAPI** whenever it receives a request to the URL "`/`" using a `GET` operation.

In this case, it is an `async` function.

### handling-errors.md::s3

/// tip

When raising an `HTTPException`, you can pass any value that can be converted to JSON as the parameter `detail`, not only `str`.

You could pass a `dict`, a `list`, etc.

They are handled automatically by **FastAPI** and converted to JSON.

///

## Add custom headers { #add-custom-headers }

There are some situations where it's useful to be able to add custom headers to the HTTP error. For example, for some types of security.

You probably won't need to use it directly in your code.

But in case you needed it for an advanced scenario, you can add custom headers:

## Install custom exception handlers { #install-custom-exception-handlers }

You can add custom exception handlers with [the same exception utilities from Starlette](https://starlette.dev/exceptions/).

Let's say you have a custom exception `UnicornException` that you (or a library you use) might `raise`.

## q038 (paraphrase)

Question: I want older clients to keep using a query argument while the docs mark it obsolete. What should I set?

Reference: Set deprecated=True on Query.

Generated answer: Set the parameter’s `deprecated` argument to `True` when you declare it with `Query`. This marks the query argument as obsolete in the generated documentation while still accepting it from older clients. [query-params-str-validations.md::s14]

Retrieved context:

### query-params-str-validations.md::s19

///

You can add a `title`:

And a `description`:

## Alias parameters { #alias-parameters }

Imagine that you want the parameter to be `item-query`.

Like in:

```
http://127.0.0.1:8000/items/?item-query=foobaritems
```

But `item-query` is not a valid Python variable name.

The closest would be `item_query`.

But you still need it to be exactly `item-query`...

Then you can declare an `alias`, and that alias is what will be used to find the parameter value:

## Deprecating parameters { #deprecating-parameters }

Now let's say you don't like this parameter anymore.

You have to leave it there a while because there are clients using it, but you want the docs to clearly show it as <dfn title="obsolete, recommended not to use it">deprecated</dfn>.

Then pass the parameter `deprecated=True` to `Query`:

The docs will show it like this:

### query-params-str-validations.md::s14

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
q: str | None = None
```

But we are now declaring it with `Query`, for example like:

```Python
q: Annotated[str | None, Query(min_length=3)] = None
```

So, when you need to declare a value as required while using `Query`, you can simply not declare a default value:

### Required, can be `None` { #required-can-be-none }

You can declare that a parameter can accept `None`, but that it's still required. This would force clients to send a value, even if the value is `None`.

### query-params.md::s0

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

### path-params-numeric-validations.md::s8

`Query`, `Path`, and other classes you will see later are subclasses of a common `Param` class.

All of them share the same parameters for additional validation and metadata you have seen.

///

/// note | Technical Details

When you import `Query`, `Path` and others from `fastapi`, they are actually functions.

That when called, return instances of classes of the same name.

So, you import `Query`, which is a function. And when you call it, it returns an instance of a class also named `Query`.

These functions are there (instead of just using the classes directly) so that your editor doesn't mark errors about their types.

That way you can use your normal editor and coding tools without having to add custom configurations to disregard those errors.

///

### query-params-str-validations.md::s5

Here we are using `Query()` because this is a **query parameter**. Later we will see others like `Path()`, `Body()`, `Header()`, and `Cookie()`, that also accept the same arguments as `Query()`.

///

FastAPI will now:

* **Validate** the data making sure that the max length is 50 characters
* Show a **clear error** for the client when the data is not valid
* **Document** the parameter in the OpenAPI schema *path operation* (so it will show up in the **automatic docs UI**)

## q023 (similar_page)

Question: Does a Pydantic model parameter represent a query parameter or a request body?

Reference: A parameter typed as a Pydantic model is interpreted as the request body.

Generated answer: A parameter whose type is a Pydantic model is interpreted as a request **body** parameter, not a query parameter. [body.md::s8]

Retrieved context:

### body.md::s8

* If the parameter is also declared in the **path**, it will be used as a path parameter.
* If the parameter is of a **singular type** (like `int`, `float`, `str`, `bool`, etc) it will be interpreted as a **query** parameter.
* If the parameter is declared to be of the type of a **Pydantic model**, it will be interpreted as a request **body**.

### body.md::s7

## Use the model { #use-the-model }

Inside of the function, you can access all the attributes of the model object directly:

## Request body + path parameters { #request-body-path-parameters }

You can declare path parameters and request body at the same time.

**FastAPI** will recognize that the function parameters that match path parameters should be **taken from the path**, and that function parameters that are declared to be Pydantic models should be **taken from the request body**.

## Request body + path + query parameters { #request-body-path-query-parameters }

You can also declare **body**, **path** and **query** parameters, all at the same time.

**FastAPI** will recognize each of them and take the data from the correct place.

The function parameters will be recognized as follows:

### body.md::s0

# Request Body { #request-body }

When you need to send data from a client (let's say, a browser) to your API, you send it as a **request body**.

A **request** body is data sent by the client to your API. A **response** body is the data your API sends to the client.

Your API almost always has to send a **response** body. But clients don't necessarily need to send **request bodies** all the time, sometimes they only request a path, maybe with some query parameters, but don't send a body.

To declare a **request** body, you use [Pydantic](https://pydantic.dev/docs/) models with all their power and benefits.

/// note

To send data, you should use one of: `POST` (the most common), `PUT`, `DELETE` or `PATCH`.

Sending a body with a `GET` request has an undefined behavior in the specifications, nevertheless, it is supported by FastAPI, only for very complex/extreme use cases.

### query-params.md::s1

As they are part of the URL, they are "naturally" strings.

But when you declare them with Python types (in the example above, as `int`), they are converted to that type and validated against it.

All the same processes that apply to path parameters also apply to query parameters:

* Editor support (obviously)
* Data <dfn title="converting the string that comes from an HTTP request into Python data">"parsing"</dfn>
* Data validation
* Automatic documentation

## Defaults { #defaults }

As query parameters are not a fixed part of a path, they can be optional and can have default values.

In the example above they have default values of `skip=0` and `limit=10`.

So, going to the URL:

```
http://127.0.0.1:8000/items/
```

### response-model.md::s3

Notice that `response_model` is a parameter of the "decorator" method (`get`, `post`, etc). Not of your *path operation function*, like all the parameters and body.

///

`response_model` receives the same type you would declare for a Pydantic model field, so, it can be a Pydantic model, but it can also be, e.g. a `list` of Pydantic models, like `List[Item]`.

FastAPI will use this `response_model` to do all the data documentation, validation, etc. and also to **convert and filter the output data** to its type declaration.

## q048 (unanswerable)

Question: How should a Redis connection be configured to cache API responses with a time-to-live?

Reference: I cannot find this in the provided documentation.

Generated answer: I cannot find this in the provided documentation.

Retrieved context:

### security__first-steps.md::s6

Normally, a token is set to expire after some time.
        * So, the user will have to log in again at some point later.
        * And if the token is stolen, the risk is less. It is not like a permanent key that will work forever (in most of the cases).
* The frontend stores that token temporarily somewhere.
* The user clicks in the frontend to go to another section of the frontend web app.
* The frontend needs to fetch some more data from the API.
    * But it needs authentication for that specific endpoint.
    * So, to authenticate with our API, it sends a header `Authorization` with a value of `Bearer ` plus the token.
    * If the token contains `foobar`, the content of the `Authorization` header would be: `Bearer foobar`.

## **FastAPI**'s `OAuth2PasswordBearer` { #fastapis-oauth2passwordbearer }

### body.md::s0

# Request Body { #request-body }

When you need to send data from a client (let's say, a browser) to your API, you send it as a **request body**.

A **request** body is data sent by the client to your API. A **response** body is the data your API sends to the client.

Your API almost always has to send a **response** body. But clients don't necessarily need to send **request bodies** all the time, sometimes they only request a path, maybe with some query parameters, but don't send a body.

To declare a **request** body, you use [Pydantic](https://pydantic.dev/docs/) models with all their power and benefits.

/// note

To send data, you should use one of: `POST` (the most common), `PUT`, `DELETE` or `PATCH`.

Sending a body with a `GET` request has an undefined behavior in the specifications, nevertheless, it is supported by FastAPI, only for very complex/extreme use cases.

### first-steps.md::s15

...and the more exotic ones:

* `OPTIONS`
* `HEAD`
* `PATCH`
* `TRACE`

In the HTTP protocol, you can communicate to each path using one (or more) of these "methods".

---

When building APIs, you normally use these specific HTTP methods to perform a specific action.

Normally you use:

* `POST`: to create data.
* `GET`: to read data.
* `PUT`: to update data.
* `DELETE`: to delete data.

So, in OpenAPI, each of the HTTP methods is called an "operation".

We are going to call them "**operations**" too.

#### Define a *path operation decorator* { #define-a-path-operation-decorator }

The `@app.get("/")` tells **FastAPI** that the function right below is in charge of handling requests that go to:

* the path `/`
* using a <dfn title="an HTTP GET method"><code>get</code> operation</dfn>

### dependencies__index.md::s11

If you don't know, check the [Async: *"In a hurry?"*](../../async.md#in-a-hurry) section about `async` and `await` in the docs.

///

## Integrated with OpenAPI { #integrated-with-openapi }

All the request declarations, validations and requirements of your dependencies (and sub-dependencies) will be integrated in the same OpenAPI schema.

So, the interactive docs will have all the information from these dependencies too:

<img src="/img/tutorial/dependencies/image01.png">

## Simple usage { #simple-usage }

If you look at it, *path operation functions* are declared to be used whenever a *path* and *operation* matches, and then **FastAPI** takes care of calling the function with the correct parameters, extracting the data from the request.

### handling-errors.md::s5

/// note | Technical Details

You could also use `from starlette.requests import Request` and `from starlette.responses import JSONResponse`.

**FastAPI** provides the same `starlette.responses` as `fastapi.responses` just as a convenience for you, the developer. But most of the available responses come directly from Starlette. The same with `Request`.
