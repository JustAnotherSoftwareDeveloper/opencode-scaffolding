# Values, Defaults, Objects, And Iteration

This page answers three connected questions about everyday TypeScript values: whether `0`, `false`, and `""` count as absent, whether a copy isolates nested state, and how iterating an array's values differs from iterating an object's keys. Each answer is language behavior with an observable result, and each sits beside a local choice that the result does not settle.

Keep two kinds of claim apart. The falsy set, the `||` and `??` results, destructuring-default conditions, spread copy depth, and iteration targets are runtime semantics with consequences a caller can see. A preference for `??` everywhere, for `value == null`, for destructuring, for copying instead of mutating, for `Map`, or for a functional iteration method is a convention whose rationale is the input contract, consistency, or readability; only the contract or codebase that states it is bound by it. Everything here stays inside TypeScript source. Node.js and Bun mechanics appear only where they explain how TypeScript source executes, and none of it decides a project's style. The examples illustrate a decision shape; they are not mandated house style.

## Treat Falsy And Absent As Different Questions

MDN lists nine falsy values: `null`, `undefined`, `false`, `NaN`, `0`, `-0`, `0n`, `""`, and `document.all` ([MDN Falsy](https://developer.mozilla.org/en-US/docs/Glossary/Falsy)). `document.all` is a legacy browser object and the only falsy object; it belongs to the language's complete list even though Node.js and Bun code does not normally handle it. The other eight are ordinary values in a TypeScript program.

`||` returns its right operand for any falsy left operand, while `??` returns its right operand only when the left operand is `null` or `undefined` ([MDN Logical OR](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Logical_OR), [MDN Nullish coalescing operator](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Nullish_coalescing)). The values that `||` therefore discards but `??` keeps are `0`, `-0`, `0n`, `NaN`, `false`, `""`, and, in a browser, `document.all`.

Which behavior is correct is decided by the input contract. If `0` is a valid timeout, `false` a valid flag, or `""` a valid label, then the fallback must not replace it. If every falsy value means "use the default", `||` states that contract directly. The operator is not chosen by habit, and TypeScript's type layer does not choose it either: the checker records which values the type admits, not which of them the application treats as absent.

```ts
interface TimeoutOptions {
  timeoutMs: number | undefined;
}

function timeoutFor(options: TimeoutOptions): number {
  return options.timeoutMs ?? 5000; // 0 stays 0
}

function legacyTimeoutFor(options: TimeoutOptions): number {
  return options.timeoutMs || 5000; // 0 becomes 5000
}

console.log(timeoutFor({ timeoutMs: 0 })); // 0
console.log(legacyTimeoutFor({ timeoutMs: 0 })); // 5000
```

`value == null` is one documented idiom for testing both `null` and `undefined`, not a rule. MDN's equality reference documents that a loose comparison involving `null` or `undefined` is true only when the other operand is also `null` or `undefined`, so `value == null` matches both and `0 == null` is false ([MDN Equality](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Equality)). Google's TypeScript style guide presents the same check as the practice of its own codebase ([Google TypeScript style guide](https://google.github.io/styleguide/tsguide.html)); that is a scoped convention, not a language requirement. An explicit input contract can call for `!== undefined`, a `== null` test, or a separate presence flag; choose the test that matches which values the input can carry.

### Keep An Empty String Visible When It Is A Value

A truthiness test and a presence test answer different questions, and the empty string makes the difference observable:

```ts
function labelFor(name: string | undefined): string {
  if (name) {
    return name; // "" takes the fallback below
  }
  return "unnamed";
}

function labelForPresent(name: string | undefined): string {
  if (name !== undefined) {
    return name; // "" is kept
  }
  return "unnamed";
}

console.log(labelFor("")); // "unnamed"
console.log(labelForPresent("")); // ""
```

The first condition asks whether the string is truthy, so a valid empty label becomes the fallback. The second asks whether the value is present. Which one is correct depends on whether `""` is a legitimate name in the input contract; neither test is universally right.

## Apply Destructuring Defaults Only To Absent Or Undefined Values

A destructuring default applies when the property is not present or has the value `undefined`; it does not apply when the property is `null` ([MDN Destructuring assignment](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring)). In `const { timeoutMs = 5000 } = options`, an absent property and `{ timeoutMs: undefined }` both produce `5000`, while `{ timeoutMs: null }` produces `null`.

Two consequences follow. First, the default is not a validation layer: a supplied `null`, or any other supplied value, reaches the binding unchanged, so a default that would coerce or check the input does not run for that case. To guarantee a usable value, the contract must exclude `null`, or the code must check the binding afterwards. Second, TypeScript keeps the supplied `null` in the binding's type, so a property typed `number | null | undefined` yields a binding typed `number | null` after the default; arithmetic on it is a compile-time error until the `null` case is handled.

The same condition explains why a destructuring default is not interchangeable with `??`. A default applies only when the value is absent or `undefined`; `??` applies to `null` and `undefined`. If the input can be `null`, the two forms answer different questions.

## Read Object Spread As A One-Level Copy

Object spread enumerates the source's own properties and creates a shallow copy: non-enumerable properties are not copied and the prototype is not copied, a repeated key takes the rightmost value while keeping its original position, and nested object or array values remain shared by reference ([MDN Spread syntax](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Spread_syntax), [MDN Shallow copy](https://developer.mozilla.org/en-US/docs/Glossary/Shallow_copy), [ECMAScript `CopyDataProperties`](https://tc39.es/ecma262/multipage/abstract-operations.html#sec-copydataproperties)).

```ts
const defaults = { headers: { accept: "application/json" }, retries: 2 };
const options = { headers: { accept: "text/plain" } };

const settings = { ...defaults, ...options };
settings.headers.accept = "application/xml";

console.log(settings.retries); // 2
console.log(options.headers.accept); // "application/xml": the nested object is shared
console.log(defaults.headers.accept); // "application/json": replaced, not mutated
```

The rightmost spread wins at the key level. `options.headers` replaces `defaults.headers` as a value, so the default `accept` header is not merged in; the default `retries` survives because no later source sets it. The copy is one level deep, so `settings.headers` and `options.headers` are the same object: mutating one is visible through the other. `defaults.headers` is a different object and keeps its value.

A copy that must isolate nested state therefore needs a nested copy at the level that is mutated, not a deeper guarantee from spread. Spreading `headers` separately, as in `{ ...defaults, ...options, headers: { ...defaults.headers, ...options.headers } }`, copies that one level; a structure with further nested objects still shares them until each level is copied or the objects are treated as immutable by contract.

## Choose Between Iterable Values And Enumerable Keys

`for...of` over an array iterates the values that the iterable defines, while `for...in` iterates enumerable string keys ([MDN `for...of`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/for...of), [MDN `for...in`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/for...in)). The key set includes inherited enumerable prototype properties and non-index properties on an array, skips symbol keys, and skips empty slots in a sparse array. `for...of` uses the array iterator, so a hole reaches the loop body as `undefined` rather than being skipped.

```ts
const labels: Record<string, string> = { alpha: "first", beta: "second" };

for (const [key, value] of Object.entries(labels)) {
  console.log(key, value); // own enumerable string keys
}

for (const key in labels) {
  console.log(key, labels[key]); // would also include inherited enumerable keys
}
```

For a plain object literal, both loops usually print the same keys because the members inherited from `Object.prototype` are non-enumerable and are not visited. The distinction becomes observable as soon as an enumerable property is added to the prototype, or an array carries a non-index property: `for...in` visits those, and `for...of` does not. Built-in prototype methods such as `Array.prototype.indexOf` are non-enumerable, so inheritance alone does not imply visitation.

Use `Object.entries`, `Object.keys`, or `Object.hasOwn` when the unit is an object's own data, and `for...of` over an array or another iterable when the unit is a value. `for...in` states the question "which enumerable string keys does this object expose, including inherited ones", and code that wants only own data must filter for it.

## Read Conventions As Conventions

The sections above state language behavior. The choices below are conventions, and each keeps its rationale.

- **`??` or `||`.** When only `null` and `undefined` mean absent, `??` or an explicit null check states the contract; when any falsy value means "use the default", `||` states it. Using one operator throughout a codebase is a consistency choice, but it does not override an input contract that admits `0`, `false`, or `""`.
- **`value == null` or an explicit test.** The loose check is compact and covers both absence values; an explicit `value === undefined` or `value === null` states which one the code expects. Neither is more correct without the contract.
- **Destructuring.** Naming the fields a function reads can make the inputs visible; a single property read can be clearer when only one field is used. The choice is a reader and consistency convention except where a default changes the result.
- **Mutating in place or copying.** When no other reference observes an object, an in-place update is a local convention. When a shared reference exists, the choice changes what other code sees, and the copy depth decides which state is isolated.
- **Object or `Map`.** The two accept different key types and expose different entry APIs, so representation is a contract question. No universal preference for `Map` follows from the language.
- **Functional iteration or a loop.** `map` produces a result array; `for...of` runs statements. Use the form that matches whether the result is used. Where both fit, consistency and readability decide.

None of these conventions changes the falsy set, the spread copy depth, or what an iteration statement visits. This page imposes no universal preference for `== null`, destructuring, in-place mutation, `Map`, or functional iteration; each has a semantic effect only in the conditions stated above, and where a preference has no semantic effect, its rationale is consistency or readability. A project or publisher that states the preference is the authority for its own code.

## What Fails, And Where

- `count || 42` yields `42` when `count` is `0`, while `count ?? 42` yields `0`.
- Mutating a nested value through a spread copy also changes the source object that supplied the reference, because the nested object was copied by reference.
- `for...in` visits inherited enumerable properties and non-index array properties; own-data filters such as `Object.hasOwn` or `Object.entries` do not include them.
- A property set to `null` is not replaced by a destructuring default, so later code observes `null` even though a default was written.
- `if (name)` treats `""` as absent and takes the fallback branch, while a presence check such as `name !== undefined` keeps the empty string.
- A spread copy of a class instance does not carry the class prototype, so methods and accessors defined on that prototype are not available through the copy.

## Limits And Ownership

- MDN's complete falsy list includes `false`, `-0`, and `document.all`; the TypeScript Handbook's truthiness-narrowing list names `0`, `NaN`, `""`, `0n`, `null`, and `undefined` and does not enumerate the other three ([TypeScript Handbook: Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#truthiness-narrowing)). Treat that shortening as a narrowing discussion, not as the complete falsy set.
- `strictNullChecks`, enabled by `strict`, decides whether `null` and `undefined` are separate from other types in the checker ([TSConfig `strictNullChecks`](https://www.typescriptlang.org/tsconfig/strictNullChecks.html)); the input contract decides whether one, both, or neither is a possible absence value. An optional property still admits `undefined` under strict checking.
- The spread, copy, and iteration semantics above come from MDN and the cited specification clause and are recorded here for TypeScript source. The pages are rolling, so re-cite the current text when a statement is used for a concrete compiler or runtime target.
- All examples here are non-normative illustrations and were not compiled or executed for this page. They show a decision shape, not a required house style.
- This page provides style guidance only. An application-level default or configuration contract is a production-behavior concern owned by `node-project-writer -> reference/change-design-and-validation.md`; the package owner is engaged only for packaged-artifact and consumer-facing validation, not for exported settings by default (`node-package-distribution -> reference/artifact-and-consumer-boundaries.md`).
- Callback argument lists, receivers, and state belong to [Functions, Callbacks, Receivers, And State](functions-callbacks-receivers-and-state.md). Type-level guarantees, `readonly` shallowness, and runtime-value validation belong to [Types, Validation, And Generics](types-validation-and-generics.md).
- The method for weighing these sources, and the routing across the style pages, stays with the hub, [Contextual Source-Style Guidance](source-style-guidance.md).
