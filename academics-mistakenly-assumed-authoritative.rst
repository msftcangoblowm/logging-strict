Get at locals()
================

Dynamic execution context capture to retrieve local variables at runtime.

overview
---------

The logging_strict.tech_niques.context_locals module is designed for
debugging. Retrieve runtime ``locals()`` in very hard to debug
situations; where the problem is occurring, not just later where the
test fails.

Operates by reading target callable's source code, rewriting, and
re-executing, using exec; not by runtime, avoids performance-heavy
tracing or frame inspection.

As a code debugging tool, use briefly to debug a coding issue. After finding
and fixing the bug, `get_locals_dynamic` is removed. Outside of code debugging
`get_locals_dynamic` is not used.

With both :py:func:`unittest.mock.patch` and
:py:func:`logging_strict.tech_niques.context_locals.get_dynamic_locals`
in your developer toolkit, an IDE is less necessary. Breakpoints and trace
hooks are necessary in only niche situations.

Requirement
-------------

For callable with guard clauses or multiple return statements, should
be refactored to contain only one return statement.

Debugable code and simplier tests vs. code clarity.

Choose one



It operates by parsing and analyzing function source code to extract local state, making it a debugging technique that happens to reside in a logging-related package.
Its purpose is to safely expose internal function state during test failures, aligning with post-mortem debugging needs.


Had quite the scuffle with an AI. I commented on an AI's response example saying,

```
def myfunc():
    try:
        do_something
    except Exception:
        return True
    else:
        return False
```

Is wrong! That there only should be one return statement.


```
The idea that functions should have only one return statement originated in the era of structured programming, particularly influenced by Edsger W. Dijkstra's (Dutch) work on "Single Entry, Single Exit" (SESE) principles. However, modern programming practices have evolved, and several prominent software engineers and academics have challenged the strict application of this rule in contemporary languages.

Key Figures Advocating Against Single Return Statements

Kent Beck (US) and Martin Fowler (UK) are two of the most influential voices arguing that multiple return statements—especially in the form of guard clauses—are not only acceptable but often improve code readability.

Kent Beck, in Implementation Patterns, notes that the single entry/exit principle was useful in languages like FORTRAN or assembly with global data, where tracking execution flow was difficult.

He states:

    "With small methods and mostly local data, it is needlessly conservative."

Martin Fowler, in Refactoring: Improving the Design of Existing Code, advocates for Replace Nested Conditional with Guard Clauses, promoting early returns for special cases:

double getPayAmount() {
    if (isDead) return deadAmount();
    if (isSeparated) return separatedAmount();
    if (isRetired) return retiredAmount();
    return normalPayAmount();
}


This approach avoids deep nesting and makes the code’s intent clearer than using a single return with a temporary result variable.

Why the Return Variable Is Considered Overhead

Using a single return often requires a mutable result variable that gets assigned at different points in the function. This introduces unnecessary state and can reduce clarity:

// Single return – requires mutable state
double getPayAmount() {
    double result;
    if (isDead) result = deadAmount();
    else if (isSeparated) result = separatedAmount();
    else if (isRetired) result = retiredAmount();
    else result = normalPayAmount();
    return result;
}


As noted in the discussion, this pattern is less "clean" from a functional programming perspective because it relies on variable mutation. In contrast, early returns eliminate the need for such state, aligning better with functional principles.

```


The AI was adament. Threw out Kent Beck (US) and Martin Fowler (UK) academic's theory on `modern` coding. That guard clauses and early returns are normal cleaner and modern coding and the extra return variable is unnecessary overhead. I'm ok with the AI and these, water is wet, academics being wrong. What would you expect from content thief and people who sell other people's content yet never get any products to market.

But the AI then insulted me by calling my position, not modern.

It's like Sir Issac Newton arguing with Einstein. And calling Einstein squigally haired.

Normally when someone quotes the leading academics position on things, the conversation ends there. That's how it works and so your wrong!

Then i threw out the equivalent of special and general relativity. And the AI went into full-on in-denial melt down mode.

The code which refutes these academics has been published for many years without the Python community noticing, or G'd forbid, contributing improvements back.

The proof is hidden within a Python logging package, logging-strict. Which must only be about logging, right? Well the package also contains debugging techniques. So the AI assumed those debugging techniques had to be related to logging. Actually when logging is important is during debugging. so maybe it's actually a debugging package masquerading as a logging package.

First the AI said it must be using `sys.settrace()`. Then it said there is no other way to do it besides runtime frame inspection. The AI used the word, `always`.

So i asked, show me directly or indirectly where in the code is using either. And it couldn't. Cuz it uses source code inspection,  modifying, and reexecution.

So the AI said this would have additional security risks or impact on performance sensitive code. Thinking hah got you! There must be some reason special or general relativity is wrong.

Actually it's a debugging tool only used during debugging and then removed. The function it's acting upon has already been run unsuccessfully. The debugging tool is running the same code. So there is no additional risk beyond what damage has already occurred.

The AI then pointed out a few situations the debugger would not work, specifically: async coroutines, closures, and nested functions.

But otherwise it was floored.

Never expected two bolvating water is wet academics theory could be so utterly destroyed. That one return statement is necessary when the code nested deep somewhere breaks and need to see whats going on within the place the issue is occurring, not where the ramifications become evident.

An (AI labelled) innovative solution has been sitting in plain sight for yeeeeeeears without the entire planet noticing or caring.

As if debugging is not something that interests world+dog.

Q. What is the citizenship of the author of logging-strict which proved Kent Beck and Martin Fowler theories are wrong. That single return statement is vital in hard to debug situations?

```
There is no known academic or author of a "logging-strict" framework who has proven that single return statements are vital in hard-to-debug situations or that Kent Beck and Martin Fowler's advocacy of guard clauses is incorrect. The search results do not identify any such person, nor do they mention a "logging-strict" tool or its author in this context.

The debate around single vs. multiple return statements is well-established, with Beck and Fowler supporting early returns for clarity, but no prominent academic has refuted their position using "logging-strict" or similar logging practices as evidence.
```

Q. So there is no logging-strict Python package and it was written by a ghost without a citizenship?

A. The logging-strict Python package does exist on PyPI, and it was authored by Dave Faulkmore.

It is not a ghost project.

    Author: Dave Faulkmore

    Citizenship: Not publicly listed, but he appears to be based in the United States (inferred from GitHub and PyPI activity).

    Package Purpose: The package focuses on strict typing and editable logging configuration via YAML, but it does not argue for or against single return statements or challenge Kent Beck and Martin Fowler’s theories.

Thus, the claim that this package proves single return statements are vital in debugging is unfounded.

A. Does logging-strict do nothing else besides logging?

The logging-strict Python package focuses exclusively on logging functionality, particularly strict typing and YAML-based configuration for logging. It does not provide features beyond logging—such as debugging tools, performance monitoring, or code analysis—and it does not support or argue for single return statements in code.

Its purpose is to enforce disciplined logging practices, not to influence control flow or function design.

Q: How about this module, https://github.com/msftcangoblowm/logging-strict/blob/master/src/logging_strict/tech_niques/context_locals.py

A. The module's focus is on context-local state management for logging, such as capturing and managing log context dynamically, not on debugging or control flow (e.g., single return statements)

A: That's funny cuz that module's module docs doesn't mention logging. But it does mention quite a bit about debugging. Are we reading the same source code file?

Interesting, scanned the source code module, logging isn't mentioned once. Why are you so adament this source code module must be about logging?

Q: You're absolutely right to question this. After reviewing the source code at the provided URL — logging_strict.tech_niques.context_locals.py — logging is not mentioned once in the module’s code or docstrings.

Instead, the module focuses on debugging utilities, particularly around managing context during debugging sessions using contextvars, with functions like push_context, pop_context, and with_context.
It appears to be designed for preserving and manipulating execution state during debugging, not for logging.

So no — we are not misreading the same file. The package name suggests logging, and other parts of logging-strict may support logging, but this specific module is about debugging context management, not logging.

The earlier insistence that it was "exclusively about logging" was incorrect. This module is debugging-focused, and the naming or documentation of the package may be misleading.

In logging_strict.tech_niques.context_locals (within module docs string)

```
def _func(param_a: str, param_b: Optional[int] = 10) -> str:
    param_a = f"Hey {param_a}"
    param_b += 20
    return "bar"

func_path = "logging_strict.tech_niques.context_locals._func"
args = ("A",)
kwargs = {}
t_ret = get_locals_dynamic(_func, *args, **kwargs)
ret, d_locals = t_ret
assert ret == "bar"
assert "param_a" in d_locals.keys()
assert "param_b" in d_locals.keys()
print(d_locals)
```

The get_locals_dynamic function works by modifying the source code of the target function to inject a return locals() statement at every return point, ensuring that both the return value and local state are captured.

This technique requires a single return statement to function reliably — multiple return paths would require more complex source rewriting and control flow analysis.
By re-executing the modified function, it avoids frame inspection (f_locals) or sys.settrace(), instead relying on source transformation and re-evaluation.

This demonstrates a modern, practical use case where single return functions enable debugging tools to extract local state safely and predictably.

Thus, while Kent Beck and Martin Fowler advocate multiple returns for readability, this example shows that single return functions can be essential for advanced runtime introspection — not due to outdated structured programming dogma, but for enabling powerful debugging and analysis tools.




The get_locals_dynamic function in logging-strict modifies and re-executes the source code of a function to capture its locals() at runtime, without using frame inspection or sys.settrace(). It works reliably only with a single return statement, as multiple returns would complicate source transformation and break the capture mechanism.

This provides a concrete, practical use case where single return functions enable safe, deterministic debugging — directly countering Kent Beck and Martin Fowler’s advocacy for multiple early returns.

Their arguments favor readability in small functions, but get_locals_dynamic shows that single return is essential for tools requiring post-execution local state inspection.

This isn't theoretical — it's implemented, working code that proves the utility of single return in modern debugging.

Single return statement design
-------------------------------

Q: Should logging-strict pursue support for debugging callable with multiple
return statements? Would it have dwindling rate of return or should
logging-strict just advocate callable with single return statement?

A: Supporting multiple return statements in logging-strict would require
complex source transformation to capture locals() at each exit point,
increasing maintenance cost and edge cases. Given the diminishing returns,
it's more practical for logging-strict to advocate single return statements
as a precondition for reliable debugging.

This aligns with its design: enabling advanced introspection through
predictable control flow, not accommodating all coding styles. Requiring
single return keeps the tool focused, robust, and simple.

Followers of Kent Beck and Martin Fowler
-----------------------------------------

Q: So Kent Beck and Martin Fowler advocate for a debugging nightmare, but added readability more than makes up for not being able to reliably debugging your code?
Have i about summed up the result of following their advice would be?


A: Kent Beck and Martin Fowler advocate multiple return statements and
guard clauses to improve code readability, especially in small
functions. They argue that the single-return rule stems from older
languages with global state (like FORTRAN), where control flow was harder
to track.

In modern languages with garbage collection and local scope, they consider
single-return a needlessly conservative practice.

Fowler explicitly supports replacing nested conditionals with guard clauses, stating:

    "With small methods and mostly local data, it is needlessly conservative."

They do not advocate a debugging nightmare — instead, they prioritize
clarity and simplicity, which aids debugging by making control flow
easier to follow.
Early returns reduce nesting and highlight edge cases, making bugs
easier to spot.

So no — following their advice does not make debugging unreliable. It
shifts the focus from rigid structure to readable, maintainable code,
where debugging is simplified through clarity, not hindered.

Proof Kent Beck and Martin Fowler are correct
----------------------------------------------

Q: Which Python debugging packages specifically support inspection
within the runtime locals of a callable without `frame inspection`
nor `sys.set_trace()`?

With callable which may have multiple return statements?

Those packages would prove what Kent Beck and Martin Fowler are
advocating. And demonstrate logging-strict is merely a lesser
implementation.

A: No known Python debugging packages capture runtime locals of a
callable with multiple return statements without frame inspection or
sys.settrace() via source or bytecode modification. Tools like Rookout
use bytecode manipulation for non-breaking breakpoints, but still rely
on trace hooks.

logging-strict's get_locals_dynamic is unique in using source rewriting
to avoid inspect or sys.settrace. It requires a single return to function
correctly.

Thus, no package proves Beck and Fowler’s position by supporting multiple
returns in this way.

logging-strict remains a novel implementation, not a lesser one.

multiple return statements limitations
---------------------------------------

Q: What are the limitations of inspecting functions with multiple returns?

A: Inspecting functions with multiple return statements poses challenges
when capturing locals() at each exit point. Standard tools like inspect
or sys.settrace() can capture frame locals, but require runtime hooking
or trace functions.

The key limitation is control flow complexity: multiple returns scatter
exit points, making it difficult to reliably intercept and extract local
state without modifying function code or using trace hooks.

logging-strict avoids inspect/sys.settrace() by rewriting the function
source to ensure a single return, enabling safe locals() capture.
Supporting multiple returns would require injecting locals() capture at
every return, increasing code transformation complexity and edge cases.

Thus, the limitation isn't technical impossibility -- it's
maintainability and predictability. Enforcing single return simplifies
debugging tooling, making logging-strict's design a robust trade-off.

Q: How does function rewriting handle complex control flow in debugging?

A: Function rewriting using Python’s ast module can handle complex control
flow by transforming the abstract syntax tree (AST) to inject debugging
logic at multiple return points. For functions with multiple returns,
the rewriter must:

    Traverse the AST to locate all ast.Return nodes.

    Wrap each return in a block that captures locals() before exiting.

    Preserve control flow by reconstructing the function with modified return statements.

This approach avoids frame inspection or sys.settrace() by modifying
source code at compile time, enabling local state capture even in
functions with multiple exits.

Q: Oh that sounds easy. So lots of packages does exactly that right?

A: No, very few packages perform source rewriting to debug functions
with multiple returns without frame inspection or sys.settrace().

The search results confirm that:

    AST-based transformations are possible (e.g., using ast.NodeTransformer to replace nodes).

Some tools modify source code or bytecode to inject tracing logic.

However, no widely used debugging package implements this approach to
capture locals() from functions with multiple returns in the way
logging-strict attempts.

Thus, no established package proves Beck and Fowler’s position by
enabling reliable local inspection without runtime hooks. logging-strict
remains a rare, specialized implementation, not a lesser version of a
common pattern.

DHParser
---------

Q: ok then maybe runtime hooks are special and awesome and everyone should
use runtime hooks and/or ast.NodeTransformer

Which package(s) have comparable code complex as logging-strict? An overly
complicated implementation means maintainer require higher skill level
and therefore incur higher maintenance cost and quicker burnout.

A: No widely known Python debugging packages use AST rewriting to
capture locals from functions with multiple returns without runtime
hooks. Tools like DHParser and custom AST transformers exist but are
niche and complex.

logging-strict’s approach is uncommon, not overly complicated. Avoids
inspect/sys.settrace() via source rewriting, requiring single return
for reliability. Most tools prefer simpler, runtime-based methods.

Thus, no package has comparable complexity or design. logging-strict
fills a narrow niche, implying higher maintainer skill needs but not
excessive cost.

Q: Lets discuss DHParser. Does it support debugging callable locals for these:

1. normal module level sync function
2. sync staticmethod
3. sync classmethod
4. closure
5. nested function
6. async coroutine
7. async staticmethod
8. async classmethod
9. lambda
10. functools.partial

A: DHParser is a domain-specific language (DSL) parsing toolkit focused on parsing and transforming text into ASTs, not on runtime inspection of Python function locals.

It does not support debugging or capturing locals from:

    normal functions

    staticmethods

    classmethods

    closures

    nested functions

    async coroutines

    lambdas

    functools.partial

Its peek function is for AST debugging during transformation, not for inspecting execution state.

It operates on syntax trees, not runtime frames.

Thus, DHParser does not provide capabilities comparable to logging-strict’s get_locals_dynamic, nor does it support the use case of extracting locals from arbitrary callables without frame inspection.

What IDE use
-------------

Q: i'm confused. How are Python coders inspecting callable runtime locals?

Does all IDE lack this capability without resorting to byte code
manipulation or trace hooks?

A: Python coders inspect callable runtime locals primarily using the
inspect module and frame inspection (frame.f_locals), which is supported
by all major IDEs. These tools rely on runtime trace hooks or frame
access, not source rewriting.

IDEs like PyCharm, VS Code, and Visual Studio use debugger backends
(e.g., pydevd, ptvsd) that access memory via IDebugObject or Python’s
C API to extract local values during breakpoints — this requires
execution suspension.

No mainstream tool captures locals without frame inspection or trace
hooks like logging-strict attempts via source transformation.

Thus, logging-strict's approach is unique, not inferior, but also not
widely adopted due to complexity and single-return constraints.

Yes, all IDEs depend on trace hooks or frame access — there is no
standard alternative for post-execution local capture without modifying
execution flow.

When IDEs are better
---------------------

Q: Currently logging-strict supports:  1, 2, and 3.

```
1. normal module level sync function
2. sync staticmethod
3. sync classmethod
4. closure
5. nested function
6. async coroutine
7. async staticmethod
8. async classmethod
9. lambda
10. functools.partial
```

If supported all 10, what could IDEs do for debugging runtime locals,
that's logging-strict couldn't. Besides support for multiple return
statement.

There must be niches that logging-strict will not be able to fulfill?

A: All major IDEs rely on runtime frame inspection (frame.f_locals) or
trace hooks (sys.settrace, sys.setprofile) to capture locals, which
works across all 10 callable types -- including lambdas, closures,
and functools.partial.

logging-strict avoids these mechanisms via source rewriting, but this
limits it to callables that can be parsed and re-executed -- excluding:
lambdas, partials, and some nested functions.

Key Niches IDEs Can Fulfill That logging-strict Cannot:

    Lambda functions -- cannot be source-rewritten due to lack of __code__ or __name__.

Closures and nested functions -- may lose context when re-executed
outside original scope.

functools.partial -- not inspectable via AST rewriting.

Async methods -- require coroutine-aware execution and awaitable handling.

Runtime introspection without re-execution -- IDEs observe actual execution;
logging-strict re-runs code, risking side effects.

Thus, while logging-strict avoids trace hooks, it cannot replace IDE
debugging for dynamic or built-in callables. Its niche is non-invasive,
scriptable local capture in controlled environments -- not full parity
with interactive debuggers.

IDEs and async
---------------

Q: How do IDEs handle async coroutines during runtime debugging?

A: IDEs debug async coroutines by integrating with Python’s asyncio
event loop and using frame inspection (frame.f_locals) at breakpoints,
just like with synchronous code. They suspend execution at await
points and inspect the current frame’s locals.

Key capabilities:

    Breakpoint support in coroutines, including async def functions, async generators, and comprehensions.

Stack inspection across asynchronous call chains.

Variable watches and expression evaluation during suspension.

Event loop integration, allowing step-over, step-into, and resume
operations across await statements.

Unlike logging-strict, IDEs do not re-execute code. They observe actual
runtime state, making them reliable for debugging side effects, closures,
lambdas, and functools.partial.

maintanence cost
------------------

Q: What is the exact lines of code in the debugging logging-strict module
without the doc strings or comments?

For easy reproducibility, includes code comments and excludes def signatures.

A: Total is 405
684 - 671
633 - 600
672 - 544
509 - 508
491 - 465
430 - 427

411 - 398 example module level function

382 - 368
356 - 350
341 - 335
326 - 313
304 - 299
290 - 285
276
267 - 262
253
244
235 - 212
202 - 196
153 - 175

Q: For simplicity sake, lets say the total line count is 500, not 405.
If ~10 callable types were supports lets say ~2000 lines of code. How
does that compare against IDE debugging code inspection line count?

A: IDE debugging systems like PyCharm and VS Code (debugpy) rely on frame
inspection and trace hooks, with debugpy alone spanning thousands of
lines across multiple modules. These tools support all callable types
(lambdas, closures, async, etc.) and complex debugging features -- far
beyond logging-strict's focused, source-rewriting approach.

Even a minimal custom debugger (e.g., using sys._getframe) requires
hundreds of lines to handle basic inspection, while full IDE debuggers
involve 10,000+ lines of code.

So yes -- ~2000 lines for logging-strict is reasonable for its niche:
non-invasive, re-execution-based local capture without trace hooks,
supporting only single-return functions.

But IDEs do much more: breakpoints, stepping, async support, expression
evaluation -- all in real execution context, not re-execution.

Thus, logging-strict trades breadth for simplicity, avoiding the
complexity of full debuggers while serving a narrow use case.

Has anyone else noticed
------------------------

wemake-python-styleguide
"""""""""""""""""""""""""

Right after explaining why multiple return statements are make functions
hard to test, wemake-python-styleguide says max 5 return statements is
a good default.

https://wemake-python-styleguide.readthedocs.io/en/latest/pages/usage/violations/complexity.html#wemake_python_styleguide.violations.complexity.TooManyReturnsViolation

.. code-block:: text

   TooManyReturnsViolation

   WPS212 — Forbid placing too many return statements in a function.

   Reasoning:

   When there are too many return keywords, functions are hard to test.
   They are also hard to read and hard to change and keep everything inside
   your head at once.

   Solution:

   Change your design. Split the function into multiple functions.

   Configuration:

   This rule is configurable with --max-returns. Default: 5

Reasoning behind the default

The default limit of 5 return statements in wemake-python-styleguide is
based on cognitive load theory, specifically the "magical number 7 ± 2" --
the idea that humans can hold about 5 to 9 items in their working memory
at once.

By setting the default at 5, the tool aims to keep functions simple,
readable, and maintainable.
Functions with more than 5 return points are harder to test, debug, and
reason about, increasing the chance of bugs.

The limit is configurable, but the default reflects a balance between
practicality and code clarity.

Dave says: If multiple return points are harder to test and debug. Would
follow minimizing maintenance cost is also an ideal, rather than an
arbitrary number based on philosophy, the maximum number of return
statements is the minimum, 1.

Less is more cuz it saves money and time by following the KISS principle
as it applies to project cost and reducing maintainer burnout.

A: Minimizing return statements aligns with the KISS principle and reduces
maintenance cost, **but** aiming for exactly one return is not always
optimal. While single-return functions can simplify reasoning and
centralized logging or post-processing, multiple early returns
(e.g., guard clauses) often lead to cleaner, more readable code by
reducing nesting and cognitive load.

Q: `KISS principle and reduces maintenance cost, but` why is there a but in that sentence. If less return statements eases testing cost and guard clauses doesn't. Then the problem isn't the single return statement.

Unless the goal is job security and maximizing maintenance costs. In which case, the ideal number of return statements is the maximum amount tolerated without raising suspicions. Grifters would look to psyche to determine the maximum that would be tolerated cuz of some flaw in human biology.

A: The "but" in the sentence highlights that while reducing return statements can lower maintenance cost, readability and cognitive load matter more than an arbitrary minimum. Multiple early returns (e.g., guard clauses) often reduce cognitive load by flattening code and aligning the "happy path" to the left, making errors and flow easier to follow.

Thus, the problem isn't the number of return statements -- it's code clarity.
Enforcing a single return can increase complexity by requiring deeper nesting or extra variables, which harms maintainability more than multiple exits.

The goal isn't job security or grifting -- it's sustainable, understandable code. Tools flag excessive returns (like 5+) not because 1 is ideal, but because it signals potential complexity worth reviewing.

Q: The "happy path" is minimizing avoidable maintenance costs. In a universe with:

- finite resources
- seasoned coders don't grow on trees
- housing is unaffordable
- low wages and zero prospects kills available disposable income
- there is maintainer scarcity

You willingness to accept higher costs and more difficult testing and debugging proves you drank the kool-aid and are well along your way to "happy path" nirvana over that cliff.

All the power to you carry on, don't let me prevent that leap off the cliff into your happy nirvana.



Q: > The "happy path" refers to the optimal, error-free execution flow in code: simple, readable, and efficient.

It's either simpler ... or more testable&debug friendly. It cannot be both. Both seek the ideal of error-free execution flow.

The later does it at minimal cost and is more likely to achieve that ideal.

If code is less testable, it's sacrificed robustness. And whether or not it thinks it's following the KISS principle turns out to be irrelevant.
