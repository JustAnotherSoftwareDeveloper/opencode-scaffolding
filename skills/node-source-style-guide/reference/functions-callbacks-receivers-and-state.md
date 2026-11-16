# Functions, Callbacks, Receivers, And State

Three questions connect the choices on this page: can this callback be passed directly, does a detached method keep its receiver, and should a value be a field or a constructor-local. Each mixes a language guarantee with a local convention, so keep the two kinds of claim apart. Callback argument lists, call-site `this`, field initialization, and `#` privacy are language behavior with observable consequences. A preference for function declarations, arrow callbacks, explicit visibility modifiers, or concise bodies is a convention whose rationale is reader comprehension, consistency, tooling, or churn, and only the publisher that states it is bound by it.

Everything here stays inside TypeScript source. Node.js and Bun runtime mechanics appear only where they explain how TypeScript source executes, and none of it decides a project's style. The examples illustrate a decision shape; they are not mandated house style.

## Pass A Callback Only When Its Argument List Fits

`Array.prototype.map` invokes its callback once per assigned index with three arguments: the element, the index, and the array. A callback that declares fewer parameters still receives all three, because a caller's argument list is not filtered by the callee's declared parameter list. MDN documents that shape and shows the consequence directly ([MDN `Array.prototype.map()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/map)).

```ts
["1", "2", "3"].map(parseInt); // [1, NaN, NaN]
["1", "2", "3"].map((s) => parseInt(s, 10)); // [1, 2, 3]
```

`parseInt` reads its second argument as the radix, so the array index becomes a radix. Index `0` asks for inference, and radixes `1` and `2` are invalid, so the second and third results are `NaN`.

A forwarding wrapper fixes the argument list the target receives. `(s) => parseInt(s, 10)` passes the element and an explicit radix and never passes the index or the array, which changes behavior compared with passing `parseInt` directly. The wrapper also chooses the result: the callback's return value, not the source element, becomes the corresponding element of the new array.

A passing type check does not settle this. TypeScript accepts a callback that declares fewer parameters than the caller supplies, so both calls above can type-check while producing different arrays; the checker compares declared function types, not the argument list a library passes at run time ([TypeScript Handbook: More on Functions](https://www.typescriptlang.org/docs/handbook/2/functions.html)). Read the API's documented callback signature before passing a function whose parameter meanings differ.

Decide with the called API's contract:

- Pass the target directly only when its parameter list means what the caller supplies in each position.
- Use a forwarding wrapper when the target needs a fixed argument list, a default, or a different meaning for one position.
- Do not generalize `map`'s three-argument shape. MDN documents it for `Array.prototype.map`; other APIs document their own callback signatures, and this page states no general callback rule.

## Read The Receiver From The Call Site, Not The Definition

`this` is determined by how a function is invoked, not where it is defined: a method call supplies the object as the receiver, and a standalone call supplies none. MDN documents the call-site rule and states that class bodies are strict, so a detached class method sees `this` as `undefined` and throws when it reads instance state ([MDN `this`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/this), [MDN Classes](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes)).

```ts
class Controller {
  #started = false;

  start(): void {
    this.#started = true;
  }
}

const controller = new Controller();
const run = controller.start;
run(); // TypeError: no receiver to read #started from
controller.start(); // receiver is controller
```

The detached reference is the same function object; what changes is the receiver at the call site. `bind` fixes a receiver and returns a new bound function, and `call` and `apply` set it for one invocation. A static method called as `Class.method()` has `this` set to the class, while a detached static call is `undefined` for the same strict-mode reason.

An arrow function has no `this` of its own. It inherits `this` from the scope where it is defined, and `call`, `apply`, and `bind` cannot change it ([MDN `this`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/this)). That makes an arrow the alternative when a callback should keep its defining scope's receiver:

```ts
class Ticker {
  #count = 0;

  start(register: (tick: () => void) => void): void {
    register(() => {
      this.#count += 1;
    });
  }
}
```

The inner arrow reads `this.#count` on the instance that called `start`, whatever receiver the callback API would otherwise supply.

When a detached callback needs a receiver that no call site will supply, put that receiver in the parameter list. That is a different contract from `this`, and the caller can see it:

```ts
const formatAll = (formatter: Formatter, values: string[]): string[] =>
  values.map((value) => formatter.format(value));
```

A `this` parameter is a declaration-level constraint. It states which receiver a typed call must supply: a call whose receiver is incompatible is the compiler error TS2684, "The 'this' context of type 'void' is not assignable to method's 'this' of type 'Formatter'". The constraint lives in the type layer, and the declaration supplies no receiver at run time.

### The Detached-Method Diagnosis Depends On The Layer

The runtime behavior is one of three answers to "why did no tool stop this", and the three must not be merged.

- **Runtime.** The receiver is lost because `this` follows the call site, and the strict class body makes it `undefined`. That happens whether or not any tool reports it.
- **Compiler.** TypeScript has no general diagnostic for referencing a method and calling it without its receiver. In the inspected compiler, a compiler error appears only under narrower conditions: TS2684 when the declaration has an explicit `this` parameter and the call supplies an incompatible receiver, TS2683 under `noImplicitThis` when `this` has an implied `any` type, and argument checking for `call`, `bind`, and `apply` under `strictBindCallApply`. Two maintainer threads label the general case a Design Limitation rather than a defect ([TypeScript issue #35451](https://github.com/microsoft/TypeScript/issues/35451), [TypeScript issue #46027](https://github.com/microsoft/TypeScript/issues/46027)). `noImplicitThis` defaults to `true` when `strict` is enabled and was released in 2.0; `strictBindCallApply` defaults to `true` when `strict` is enabled and was released in 3.2 ([TSConfig Reference](https://www.typescriptlang.org/tsconfig/)).
- **Typed lint.** The common compile-time signal for a class method referenced unbound is the typescript-eslint rule `@typescript-eslint/unbound-method`. The rule reports a class method referenced in an unbound manner and requires type information to run; extending the `recommended-type-checked` shared configuration, or configuring the rule directly, is documented to enable it ([`unbound-method`](https://typescript-eslint.io/rules/unbound-method/)). Its enabling condition is type-aware linting configuration — `parserOptions.projectService` (the recommended option) or `project`, which the type-checked shared configurations supply — not the compiler's `strict` flag ([Linting with Type Information](https://typescript-eslint.io/getting-started/typed-linting/)).

The rule's exemptions belong to the rule, not to the language: a method annotated `this: void` and an arrow-function class property are treated as safely bound, and the rule's only option is `ignoreStatic`, default `false`. A `this: void` annotation is also a statement that the method does not read its receiver.

Read each result for what it shows:

- A clean `tsc` run reports that the compiler's enabled checks found nothing; it does not show the detached reference is safe.
- An `unbound-method` finding comes from a type-aware lint configuration, not from the compiler; its absence shows only what the effective configuration checked.
- If a project wants this detection, that is a lint-configuration decision. Enablement, preset membership, and the effective target set belong to `node-quality-workflow -> reference/quality-scope-and-mutation.md`.

This page therefore does not say TypeScript rejects a detached method. In general it does not; only the narrow compiler conditions above produce an error, and the general signal depends on a typed-lint rule that a project must configure.

## Choose Where Instance State Lives

An instance value can be assigned in the constructor or declared as a class field. Field initializers are evaluated during instance creation — at the start of the constructor for a base class, or immediately before `super()` returns for a derived class — and class elements are evaluated in declaration order. Static field initializers are evaluated with `this` set to the class itself ([MDN Classes](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes)).

```ts
class Report {
  #rows: string[];

  constructor(raw: string) {
    const rows = raw.split("\n"); // constructor-local
    this.#rows = rows; // retained: the accessor reads it later
  }

  get count(): number {
    return this.#rows.length;
  }
}
```

A value that nothing reads after construction can stay a constructor-local; a value that a method or accessor reads later needs to be stored on the instance. Both forms keep instance state, and the choice is about which state the object should keep, not about spelling.

Accessors follow the same state rule: `get` and `set` elements are installed on the prototype for instances and on the class for statics, so an accessor that computes from instance state reads it through `this` and inherits the call-site rule above.

Initialization order becomes observable across a hierarchy:

```ts
interface Animal {
  animalStuff: unknown;
}

interface Dog extends Animal {
  dogStuff: unknown;
}

class AnimalHouse {
  resident: Animal;

  constructor(animal: Animal) {
    this.resident = animal;
  }
}

class DogHouse extends AnimalHouse {
  // `declare` marks a type-only redeclaration of the parent field.
  declare resident: Dog;

  constructor(dog: Dog) {
    super(dog);
  }
}
```

Base fields initialize, then the base constructor runs, then derived fields initialize, then the derived constructor runs. A derived constructor that reads an inherited field before its own field initializers run therefore sees the base value. Without `declare`, a derived redeclaration of a parent field is a field definition that runs after `super()` returns and overwrites the parent's value with `undefined` when `target` is ES2022 or later or `useDefineForClassFields` is `true`; below that target, or with the option `false`, the declaration is type-only and emits nothing ([TypeScript Handbook: Classes](https://www.typescriptlang.org/docs/handbook/2/classes.html)).

Parameter properties are TypeScript syntax that declares and initializes a field from a constructor parameter:

```ts
class RetryPolicy {
  constructor(
    readonly attempts: number,
    private readonly delayMs: number,
  ) {}

  nextDelay(attempt: number): number {
    return this.delayMs * attempt;
  }
}
```

The modifiers create class fields of the same names and values, and the emitted runtime form is the constructor assignment. The construct generates runtime code, so it is not interchangeable with an annotation that erases; [Types, Validation, And Generics](types-validation-and-generics.md) owns which TypeScript syntax can run without a transform.

## Separate Visibility From Privacy

`public`, `private`, `protected`, and `readonly` are TypeScript compile-time constructs. They change what the checker accepts; they do not create runtime access control. TypeScript documents that ECMAScript `#` private fields, by contrast, "remain private after compilation" and do not provide the escape hatches that TypeScript `private` leaves open, such as bracket notation ([TypeScript Handbook: Classes](https://www.typescriptlang.org/docs/handbook/2/classes.html)).

```ts
class Account {
  private token = "t-1";
  #secret = "s-1";
}

const account = new Account();
account["token"]; // documented escape hatch: the property exists at run time
account.#secret; // SyntaxError: the field is not declared in an enclosing class
```

The `private` member is an ordinary property that the checker guards; a caller who bypasses the checker can still read it, and property enumeration and spread see it. A `#` name cannot be referenced outside the class at all: the reference above is a syntax error, not a different way to read the field, and `delete` on a private element is also a syntax error ([MDN Private elements](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes/Private_elements)).

`readonly` is also compile-time: it rejects assignment in checked code and does not freeze the value or deep-copy it, so a `readonly` property that holds an object still exposes that object's mutable state. [Types, Validation, And Generics](types-validation-and-generics.md) owns `readonly`'s shallowness and the rest of the type-level guarantees.

Emit adds one target-sensitive detail: TypeScript documents that it lowers `#` fields to `WeakMap`-based storage when compiling to ES2021 or less ([TypeScript Handbook: Classes](https://www.typescriptlang.org/docs/handbook/2/classes.html)). That lowering is an emit detail of the same privacy model, not a second visibility tier.

The choice between `private` and `#` is therefore not cosmetic: `private` keeps a checker guard plus a reachable property, while `#` adds enforcement that the runtime performs. Choose by the guarantee the class must make, and state that guarantee rather than the keyword preference.

## Read Conventions As Conventions

The sections above state language behavior. The choices below are conventions, and each keeps its rationale.

- **Function declaration or arrow for a named function.** Both produce a function value. For a helper that does not read `this`, the choice is a reader and navigation convention; when it does read a receiver, whether it has its own `this` is behavior. Google's TypeScript style guide states its own preferences for named functions and arrow usage for code in its environment ([Google TypeScript style guide](https://google.github.io/styleguide/tsguide.html)); that guide says its constraints may not apply outside its context, so it is attributed evidence, not a default.
- **Arrow or `function` for a callback.** When the callback must keep its defining scope's receiver, the arrow is the form with that behavior, and the typed-lint rule treats arrow class properties as bound. When no `this` is involved, the choice is consistency with neighboring code or brevity.
- **Explicit visibility modifiers.** Marking implementation members `private` changes what the checker rejects, so it has a compile-time and API-intent effect, but no runtime effect on the member itself. Its rationale is that the reader and future callers see the intended surface; it is not an access-control guarantee.
- **Concise or block callback body.** A concise arrow body returns its expression; a block body returns `undefined` without a `return`. Where the caller uses the return value, as in `map`, `filter`, or `reduce`, that difference is behavior, so the body shape follows the contract. Where the return value is unused, a block body's rationale is that the reader sees no value is produced. Google's guide contrasts a value-returning callback with a side-effect-only callback as its own example ([Google TypeScript style guide](https://google.github.io/styleguide/tsguide.html)).
- **Google's additional function and class conventions.** The same guide states preferences about parameter defaults, function length, event-handler identity, constructor-only state, field declarations, `readonly` use, accessors, and static `this` ([Google TypeScript style guide](https://google.github.io/styleguide/tsguide.html)). They document the practices of one codebase; adopting any of them is a project decision.

None of these conventions overrides a callback contract. A wrapper that fixes the argument list, a receiver the callback must keep, or a class element that must be private at run time is a behavior decision, and it takes precedence over a spelling preference.

## What Fails, And Where

- `["1", "2", "3"].map(parseInt)` produces `[1, NaN, NaN]` because the index becomes the radix; the type check can pass because a callback position accepts a function with fewer parameters.
- A detached class method call throws when the method reads `this`, because the class body is strict and the call site supplies no receiver.
- The compiler reports nothing for a plain detached method in the inspected versions; TS2684 appears only for a `this`-annotated declaration called with an incompatible receiver.
- `@typescript-eslint/unbound-method` reports the unbound reference only when type-aware linting is configured; a warning-free compiler run is not evidence that the rule ran.
- Referencing a `#` name outside the class is a syntax error; the TypeScript `private` member at the same position is readable at run time through the documented escape hatch.
- With `target` ES2022 or later or `useDefineForClassFields: true`, a derived redeclaration of a parent field without `declare` overwrites the value the parent constructor set with `undefined`.
- A `readonly` property rejects assignment in checked code but does not prevent mutation of the object it references.

## Limits And Ownership

- The three-argument `map` shape and the call-dependent `this` rule are recorded from the MDN reference pages cited above. The normative specification clause for `Array.prototype.map` was not inspected, so the arity statement rests on MDN.
- The "no general compiler diagnostic" statement describes the inspected compiler versions and the two maintainer issues labeled Design Limitation; it is not a claim about every past or future release. TS2684, TS2683, and `strictBindCallApply` constrain a typed call site and are not a general detached-reference check.
- The `unbound-method` rule page documents an available rule; it does not show that a project enables it or which shared configurations include it. Read the effective configuration and the invocation. Rule documentation establishes a rule, not adoption.
- Class field timing depends on `target` and `useDefineForClassFields`; `#` lowering is documented for ES2021 or less. Check the project's compiler target before reasoning about initialization or emit.
- All examples here are non-normative illustrations and were not compiled or executed for this page. They show a decision shape, not a required house style.
- This page provides style guidance only. A change to callback behavior, a method's receiver contract, or class state goes to the production owner (`node-project-writer -> reference/change-design-and-validation.md`) with the contract it affects; callback and receiver tests go to `node-project-test-writer -> reference/test-design-and-measurement.md`.
- Lint and formatter configuration, including enablement of `@typescript-eslint/unbound-method`, belongs to `node-quality-workflow -> reference/quality-scope-and-mutation.md`.
- Runtime, module, and emitted-JavaScript mechanics belong to `node-project-reference -> reference/runtime-and-project-structure.md`; the public source and API surface belongs to `node-project-reference -> reference/source-and-api-conventions.md`.
- Type-level guarantees, `readonly` shallowness, and which TypeScript syntax can run without a transform are owned by [Types, Validation, And Generics](types-validation-and-generics.md). Value and absence semantics belong to [Values, Defaults, Objects, And Iteration](values-defaults-objects-and-iteration.md), and failure observation across async boundaries belongs to [Async And Error Boundaries](async-and-error-boundaries.md).
- The method for weighing these sources, and the routing across the style pages, stays with the hub, [Contextual Source-Style Guidance](source-style-guidance.md).
