# Types, Validation, And Generics

Does this assertion validate its input? Does `readonly` protect nested runtime state? Does this generic preserve an input-output relationship? Which TypeScript syntax can Node run without a transform?

All four questions are about the same limit: what the compiler can prove at a call site, and where that proof stops. A type-level statement describes the program the checker analyzed under its selected options. A runtime value is whatever the executing runtime received. This page keeps the two apart, states language and type behavior separately from convention choices, and routes validation design, compiler configuration, and loader behavior to their owners.

Everything here is TypeScript source, together with the emitted-JavaScript and module mechanics that explain how that source executes, resolves, or reaches a consumer. JavaScript-only work is out of scope: this page does not cover `allowJs`, `checkJs`, JavaScript diagnostics, or JSDoc typing of `.js` files. TypeScript documentation comments on exported declarations stay within this workspace's scope and are covered on the imports page. The examples illustrate a decision shape; they are not required house style.

## Read An Annotation Differently From An Assertion

A type annotation states the type a declaration is expected to have, and the checker enforces it where values flow into that declaration ([TypeScript Handbook: Everyday Types](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html)). Where a value has an initializer, the checker infers the type from it, so an annotation adds no check the initializer did not already provide; most variable annotations are therefore unnecessary. A parameter annotation is what makes a caller's argument checked at the call site, and the checker counts arguments even when no parameter is annotated.

An explicit return type is an annotation like any other: the returned value is checked against the declared type rather than against an inferred one, so the declaration states the contract the body must satisfy. Google's TypeScript style guide recommends an explicit return type for a public contract ([Google TypeScript style guide](https://google.github.io/styleguide/tsguide.html)). That recommendation is the guide's own convention for the code it governs, not a language requirement, and the check it produces exists whether or not a project adopts the convention.

All of this syntax is erased. No annotation survives into the JavaScript that runs, so the expectation it records is a statement about the analyzed program only.

A type assertion is the inverse operation. `as T`, the angle-bracket `<T>expr` form, and the postfix `!` operator tell the compiler to accept a type it did not derive. The Handbook states that assertions "are removed by the compiler and won't affect the runtime behavior", that "there is no runtime checking associated with a type assertion", and that no exception or `null` is produced if the assertion is wrong. The one check that remains is plausibility: an assertion must convert between sufficiently overlapping versions of a type, and the documented escape is to assert through `unknown` or `any`.

The difference is visible when a fresh object literal meets an annotation and then meets an assertion:

```ts
type Config = { name: string; retries: number };

const annotated: Config = { name: "svc", retries: 3, timoutMs: 5_000 };
// rejected: the object literal is checked against Config, so the misspelled key fails

const asserted = { name: "svc", retries: 3, timoutMs: 5_000 } as Config;
// accepted: the key stays misspelled in the object, and the type now claims otherwise

asserted.timeoutMs; // rejected: the declared type has no such property
```

A fresh object literal is checked for excess properties against its annotation ([TypeScript Handbook: Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html)). The assertion suppresses that complaint because the shapes overlap at `name` and `retries`, but it changes only what the compiler believes. The value that reaches the caller still carries `timoutMs`, and no runtime check inspected it.

## Declare Intent With Literal And Readonly Types

`as const` "acts like `const` but for the type system": it fixes property types to their literal types instead of widening them to `string` or `number` ([TypeScript Handbook: Everyday Types](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html)). It is a type-level operation with no runtime counterpart, and it does not freeze anything. A `const` assertion on an array literal infers a `readonly` tuple from TypeScript 3.4 ([TypeScript 3.4 release notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-4.html)).

`readonly` is the same kind of statement about a value the program still holds. TypeScript states that a property marked `readonly` "can't be written to during type-checking" while the modifier "won't change any behavior at runtime", and that it "doesn't necessarily imply that a value is totally immutable … It just means the property itself can't be re-written to" ([TypeScript Handbook: Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html)). The restriction is per property and shallow: state reached through a `readonly` property stays writable.

```ts
type Settings = {
  readonly timeoutMs: number;
  readonly retry: { attempts: number };
};

const settings: Settings = { timeoutMs: 5_000, retry: { attempts: 3 } };

settings.timeoutMs = 1_000;  // TS2540: assignment to a read-only property
settings.retry.attempts = 5; // accepted: the property is read-only, not what it references
```

The first write fails at compile time; the second is accepted, and at run time both objects are ordinary mutable objects. The object-types page shows the same asymmetry with an update through the nested reference that the checker allows, alongside a rejected assignment to the reference itself.

Compare an object whose protection is arranged at run time, for example one passed through `Object.freeze`. That call acts on the object the program holds, and how deep its protection reaches and what a rejected write does are properties of that operation, which its own documentation must state. The `readonly` annotation is erased before the program runs, so it is not evidence that any freeze happened, and a freeze does not extend the annotation's check to nested state. If the requirement is runtime immutability, choose a runtime mechanism and read its contract.

## Choose Between Any And Unknown By What The Source Can Prove

`any` removes the checker from the path. Property access, calls, and assignment in either direction are permitted, and the Handbook states that "using `any` disables all further type checking" ([TypeScript Handbook: Everyday Types](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html)). When no type can be inferred, the compiler falls back to `any`; `noImplicitAny` turns that fallback into an error. It defaults to `true` when `strict` is enabled and `false` otherwise and was released in 1.0, and `strict` itself defaults to `true` in the configuration reference and from TypeScript 6.0 ([TSConfig Reference](https://www.typescriptlang.org/tsconfig/), [TypeScript 6.0 release notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-6-0.html)).

`unknown` is the type-safe counterpart, introduced in TypeScript 3.0. Anything is assignable to it, but it is assignable only to itself and `any` without an assertion or a narrowing check, and no operation is permitted on it before the source asserts or narrows ([TypeScript 3.0 release notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-0.html)).

```ts
function sizeOfAny(value: any): number {
  return value.length; // accepted: the checker stops here
}

function sizeOfUnknown(value: unknown): number {
  return value.length; // TS18046: 'value' is of type 'unknown'
}
```

The difference matters wherever the value's shape is not the source's own: `any` lets the code proceed without evidence, while `unknown` requires the source to produce evidence, either a guard or an explicit assertion. The assertion branch establishes nothing at run time, which is why the guard is the useful form.

## Preserve The Relationship With Generics

A type parameter captures the type the caller supplies so the same type can be used again in the return type; the generics page describes a function as able to "traffic that type information in one side of the function and out the other", and notes that an `any`-based identity signature loses the information about what the type was when the function returns ([TypeScript Handbook: Generics](https://www.typescriptlang.org/docs/handbook/2/generics.html)).

Two constraints govern what the body may assume. Inside the body the compiler treats a type parameter as if it could be any and all types, so a member access such as `.length` is rejected on an unconstrained parameter; a constraint written with `extends` names the capability the body is allowed to use. A generic class is generic only over its instance side, so static members cannot refer to the class type parameter.

```ts
function first<T>(items: readonly T[]): T | undefined {
  return items[0];
}

function firstAny(items: readonly any[]): any {
  return items[0];
}

const names: readonly string[] = ["a", "b"];

const name = first(names);    // string | undefined: the element type survives
const lost = firstAny(names); // any: the element type is gone
```

The `readonly` parameter modifier keeps the function from mutating the array through the parameter; the return type keeps the element relationship. Because generics are erased like all other type syntax, this is a checking guarantee about call sites, not a runtime conversion.

Preservation is not a promise that the compiler always infers the intended argument: the page notes that explicit type arguments may be needed when inference fails, which is a call-site decision rather than a change to the relationship.

## Narrow A Union And Exhaust It

A union whose members share a property with literal types is a discriminated union, and checking that property removes the other members from the current branch ([TypeScript Handbook: Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)). The impossible remainder is `never`, which is what makes an exhaustiveness check possible: a value the compiler has narrowed to `never` can be handed only to a function that accepts nothing.

```ts
type Result<T> = { ok: true; value: T } | { ok: false; error: Error };

function unwrap<T>(result: Result<T>): T {
  if (result.ok) return result.value;
  throw result.error;
}

function assertNever(value: never): never {
  throw new Error(`unhandled case: ${JSON.stringify(value)}`);
}
```

In `unwrap`, `ok` is the discriminant. The true branch has a `value`, and the remaining branch has an `error`; reading `value` without the check would be rejected because the union still contains the failure member.

```ts
type Shape = { kind: "circle"; radius: number } | { kind: "square"; side: number };

function area(shape: Shape): number {
  switch (shape.kind) {
    case "circle":
      return Math.PI * shape.radius ** 2;
    case "square":
      return shape.side ** 2;
    default:
      return assertNever(shape); // a new variant makes this line a compile error
  }
}
```

Narrowing is a union mechanism, and it is not the same as intersection reduction, which has two distinct documented outcomes. An incompatible non-discriminant property makes that property `never` while the intersection stays object-like: the object-types page's `Staff = Person & Person2` example yields `(property) name: never`. A disjoint literal discriminant collapses the entire intersection to `never`, from TypeScript 3.9: the release notes describe `Circle & Square` reducing to `never`, after which a property access reports that the property does not exist on type `never` ([TypeScript 3.9 release notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-9.html)). A blanket claim that incompatible intersections become `never` would be wrong about the first case.

## Validate The Value, Not Just The Type

The documentation places checking before execution consistently: assertions generate no check, type-only imports and exports are elided, and both runtimes discussed below execute TypeScript without checking it. What the checker establishes is a statement about the program it analyzed. What exists at run time is whatever JavaScript the runtime executes. A guard written in source is the only mechanism in these pages that inspects an actual value.

```ts
type Config = { name: string; retries: number };

function parseConfig(text: string): unknown {
  return JSON.parse(text);
}

function isConfig(value: unknown): value is Config {
  if (typeof value !== "object" || value === null) return false;
  if (!("name" in value) || !("retries" in value)) return false;

  const { name, retries } = value as { name: unknown; retries: unknown };
  return typeof name === "string" && typeof retries === "number";
}

const unchecked = JSON.parse(text) as Config; // compiles; validates nothing

const candidate = parseConfig(text); // unknown: no property may be read yet
if (!isConfig(candidate)) throw new Error("invalid config");
candidate.retries; // Config after the guard
```

The `as Config` above and `unchecked` here are the same mistake in two spellings: the assertion states a belief the checker accepts and the value keeps whatever shape it arrived with. The guard is an ordinary runtime expression, and `typeof`, `in`, and `===` are documented narrowing forms the checker follows. Inside `isConfig`, the assertion is confined to the keys the guard has just verified, which is why it adds no new claim about the value.

Value and absence semantics — which values count as absent, and when `??` differs from `||` — belong to [Values, Defaults, Objects, And Iteration](values-defaults-objects-and-iteration.md). Narrowing a caught failure typed `unknown` belongs to [Async And Error Boundaries](async-and-error-boundaries.md).

## Execute Only Erasable Syntax Without A Transform

`import type` and `export type` are guaranteed to be erased, so a declaration-side name can have no runtime binding at all ([TypeScript 3.8 release notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-8.html)). The import and export forms, and the emit options that govern unmarked imports, belong to [Imports, Names, And Comments](imports-names-and-comments.md). What this page answers is which syntax a runtime can execute and which needs a transform.

Node.js v26 documents native execution as type stripping: a file whose TypeScript syntax is all erasable is run after the runtime "replace[s] TypeScript syntax with whitespace", and "no type checking is performed" ([Node.js Modules: TypeScript](https://nodejs.org/docs/latest-v26.x/api/typescript.html)). The same page states that Node ignores `tsconfig.json`, so settings such as `paths` never apply, that syntax requiring code generation is not supported, that TypeScript under `node_modules` is refused, and that `--no-strip-types` disables the behavior. Module kind is decided per file: `.ts` follows the package `type` rule, `.mts` is always ESM, `.cts` is always CommonJS, and the runtime does not convert between them. Type imports must carry the `type` keyword, because "Without the `type` keyword, Node.js will treat the import as a value import, which will result in a runtime error."

The constructs that need a transform are the ones that generate JavaScript. The Handbook's enums page shows `enum Enum { A }` compiled to `var Enum; (function (Enum) { Enum[Enum["A"] = 0] = "A"; })(Enum || (Enum = {}));`, an object with forward and reverse mappings ([TypeScript Handbook: Enums](https://www.typescriptlang.org/docs/handbook/enums.html)). An enum is therefore not erasable, and the same is true of a namespace containing runtime code, a parameter property, and the non-ECMAScript `import =` and `export =` aliases.

`erasableSyntaxOnly` turns that list into a compile error: it "will cause TypeScript to error on most TypeScript-specific constructs that have runtime behavior", and the option page and the release notes both name enums, namespaces with runtime code, parameter properties, and `import =`/`export =` ([TSConfig `erasableSyntaxOnly`](https://www.typescriptlang.org/tsconfig/erasableSyntaxOnly.html), [TypeScript 5.8 release notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-8.html)). It was introduced in 5.8 and is opt-in; the page also recommends pairing it with `verbatimModuleSyntax`, which from 5.0 makes emit syntactic rather than usage-driven ([TSConfig `verbatimModuleSyntax`](https://www.typescriptlang.org/tsconfig/verbatimModuleSyntax.html)).

Bun splits the work differently. It transpiles every file before running it, runs TypeScript "without checking their types", and provides checking as a separate interface through `--check` and `bun check`, which check before running and exit non-zero on error ([Bun runtime](https://bun.com/docs/runtime); [Bun type checking](https://bun.com/docs/runtime/check)). Bun's suggested `compilerOptions` include `verbatimModuleSyntax: true` and `noEmit: true` ([Bun TypeScript](https://bun.com/docs/runtime/typescript)).

Two consequences follow, and both are load-time facts rather than type errors:

- A `.tsx` file run on Node's native path is refused as an unsupported file, not rejected for a type mistake, because that path does not accept the extension.
- A type-only import written without the `type` keyword can pass a green check, because default emit elides an unmarked import the compiler sees used only in type positions; at run time Node does not elide it, treats it as a value import of a name with no binding, and the module fails to load.

## Derive Types With The Advanced Type Tools

The checker offers constructs that describe shapes it cannot enumerate. Five topics are stated in full, each with its mechanism and release bound: index signatures, mapped types, conditional types, tuples, and wrapper types. Two adjacent mechanisms appear where they belong — `keyof` and indexed access beside index signatures, and intersection reduction beside narrowing — because the first four topics cannot be used precisely without them. Each topic is type-level unless the runtime object behind the name is the subject, as it is for wrapper types.

### Index Signatures Describe Keys You Do Not Know

An index signature `{ [key: KeyType]: ValueType }` describes the value type for properties whose names are not known ahead of time. The current page allows `string`, `number`, `symbol`, template string patterns, and unions of those as key types ([TypeScript Handbook: Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html)). Three documented constraints follow from that model:

- A numeric indexer's value type must be a subtype of the string indexer's, because a numeric key is coerced to a string; the failure is `TS2413`.
- Every declared property must be assignable to the index type, unless the index type is a union that includes it; the failure is `TS2411`.
- A `readonly` index signature permits reads only; a write is `TS2542`.

```ts
type Scores = {
  [name: string]: number;
  best: number; // must be assignable to the index type
};

const scores: Scores = { best: 3 };
const best = scores["algebra"]; // number — or number | undefined under noUncheckedIndexedAccess
```

`keyof` on that type yields the key union, which for a string index signature is `string | number`; an indexed access such as `Scores["best"]` reads a property type, and a missing property is `TS2339` ([TypeScript Handbook: Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html)).

The read type changes under `noUncheckedIndexedAccess`, introduced in TypeScript 4.1, which adds `undefined` to an undeclared index read so that every such access is "considered potentially undefined" ([TypeScript 4.1 release notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-1.html), [TSConfig `noUncheckedIndexedAccess`](https://www.typescriptlang.org/tsconfig/noUncheckedIndexedAccess.html)). The option defaults to `false` and is not part of the `strict` family; its membership and default are declared in the compiler's own option definitions ([microsoft/TypeScript compiler options](https://github.com/microsoft/TypeScript/blob/main/src/compiler/commandLineParser.ts)). Turning it on changes the type an author must handle at a call site; enabling it is a configuration decision, and configuration belongs to `node-quality-workflow -> reference/quality-scope-and-mutation.md`.

### Mapped And Conditional Types Derive From A Type

A mapped type is "a generic type which uses a union of `PropertyKey`s (frequently created via a `keyof`) to iterate through keys to create a type", and it builds on the index-signature syntax ([TypeScript Handbook: Mapped Types](https://www.typescriptlang.org/docs/handbook/2/mapped-types.html)). Its version ladder is specific: mapped types in 2.1, the `+` and `-` modifiers for `readonly` and `?` in 2.8 (an unprefixed modifier means `+`), `readonly` array coercion in 3.4, and `as` key remapping with `never` filtering in 4.1 ([TypeScript 2.8 release notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-2-8.html)). When the iterated list is `keyof T`, the mapping is homomorphic: it applies only to the properties of `T` and copies their existing modifiers. A mapped type may not declare members, which is `TS7061`; adding members means intersecting it with an object type.

```ts
type Optional<T> = { [K in keyof T]?: T[K] };
type Mutable<T> = { -readonly [K in keyof T]: T[K] };
type Flagged<T> = { [K in keyof T as `is${Capitalize<string & K>}`]: boolean };
```

A conditional type is written `T extends U ? X : Y` and selects `X` when `T` is assignable to `U`, else `Y`; it was introduced in 2.8 ([TypeScript Handbook: Conditional Types](https://www.typescriptlang.org/docs/handbook/2/conditional-types.html)). A conditional whose check depends on free type parameters is deferred rather than resolved at its definition, and the resolution test instantiates every type parameter with `any` before deciding ([TypeScript 2.8 release notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-2-8.html)). `infer` introduces a type variable from the compared type, and a conditional over a naked type parameter distributes over a union, which `[T] extends [U]` suppresses.

```ts
type ElementOf<T> = T extends readonly (infer E)[] ? E : never;
type Present<T> = T extends null | undefined ? never : T; // distributes over a union
type IsString<T> = [T] extends [string] ? true : false;  // no distribution
```

Because the resolvability test is the permissive instantiation with `any`, a generic conditional commonly stays deferred. When the selected branch matters, instantiate or assert at the use site rather than assuming the conditional resolved at the generic definition.

### Tuples Bind Position, And Their Releases Split By Form

A tuple type "knows exactly how many elements it contains, and exactly which types it contains at specific positions", and it has "no representation at runtime"; an out-of-range index is `TS2493` ([TypeScript Handbook: Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html)).

Tuple capabilities do not share one release, and two of them are easy to confuse:

- Optional elements, allowed only at the end and reflected in `length`, and rest elements restricted to the last position: TypeScript 3.0.
- `readonly` tuple types, and `const` assertions that infer them from array literals: TypeScript 3.4.
- Variadic tuple types — spreads of tuple types and generic array-like type parameters that compose a tuple — and labeled tuple elements: TypeScript 4.0 ([TypeScript 4.0 release notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-0.html)).
- Leading and middle rest elements of an unbounded array type: TypeScript 4.2 ([TypeScript 4.2 release notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-2.html)).

```ts
type Pair = [name: string, count: number]; // labeled elements: 4.0
declare function tail<T extends any[]>(items: readonly [any, ...T]): T; // variadic spread: 4.0
type Trail = [...string[], number]; // leading rest element: 4.2
```

The two forms read alike and are not the same capability. The 4.0 notes say the prior restriction that "A rest element must be last in a tuple type" is relaxed and that "rest elements can occur anywhere in a tuple - not just at the end!", while the 4.2 notes say that "In prior versions, TypeScript only allowed `...rest` elements at the very last position of a tuple type". Read together, the general phrases conflict; the syntactic form is the bound that reconciles them, because 4.0 covers spreads of tuple types and generic parameters while 4.2 covers a concrete rest element of an unbounded array type ([microsoft/TypeScript PR #41544](https://github.com/microsoft/TypeScript/pull/41544)). State each form with its own release; no universal "rest anywhere is 4.0" shorthand holds. A rest element still cannot follow another rest element (`TS1265`), and an optional element cannot follow a rest element (`TS1266`).

One bound remains open: the 4.0 notes do not establish that the concrete unbounded form `[...string[], number]` was accepted in 4.0, while the maintainer change and the 4.2 notes place it in 4.2.

### Wrapper Types Name Objects, Not Primitives

The uppercase names are types for boxed objects. The Handbook states that `Number`, `String`, `Boolean`, `Symbol`, and `Object` "refer to non-primitive boxed objects that are almost never used appropriately in JavaScript code", and recommends the lowercase primitives and the `object` type ([TypeScript Handbook: Do's and Don'ts](https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html)). At the type level a `String` annotation admits the corresponding primitive, which is why the page marks `function reverse(s: String): String` as wrong even though primitive strings are accepted: the annotation names a boxed-object type and guarantees no primitive.

```ts
function reverse(s: String): String {
  return s.split("").reverse().join("");
}

reverse("abc");          // accepted by the checker
const boxed = new String("abc"); // typeof boxed is "object", not "string"
```

The runtime side is a separate set of facts. MDN states that JavaScript distinguishes `String` objects from primitive string values, that `String` with `new` returns a wrapper object while a literal or a `String()` call in a non-constructor context does not, and that `typeof` is `"string"` for the primitive and `"object"` for the object. It also documents that primitives passed to `eval` are treated as source code while `String` objects are treated as objects, that `valueOf()` converts the object to its primitive, and that "the code may break when it encounters `String` objects when it expects a primitive string instead" ([MDN: `String`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String)).

`Object`, `object`, and `{}` are three different types, and substituting one for another is a semantic change rather than a rename. The lowercase `object` type, added in TypeScript 2.2, is the non-primitive type and rejects primitives; it "is distinct from the `{}` type and `Object` types" in this respect, because `{}` and `Object` also match primitives ([TypeScript 2.2 release notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-2-2.html), [TypeScript in 2.2 announcement](https://devblogs.microsoft.com/typescript/announcing-typescript-2-2/)). `Object` is the standard-library interface. Replacing `Object` with `object` therefore narrows the admitted value set, which is a change to what callers may pass.

## Read A Declaration As A Consumer Surface

A declaration records a local type for the file's own checking and, for a published package, it is also part of what typed consumers resolve. A declaration change can affect overload selection, inference, optional parameters, or assignability without changing any runtime code, and a runtime change can leave the declaration describing behavior that no longer exists. Type-check success does not establish runtime behavior, and runtime success does not establish declaration compatibility.

Read the package's actual module form, resolution mode, supported compiler range, and consumer entry points when those surfaces are in scope. The public source and API surface belongs to `node-project-reference -> reference/source-and-api-conventions.md`, and declaration consumption with package entry points belongs to `node-package-distribution -> reference/consumer-resolution-and-declarations.md`.

## Read Conventions As Conventions

The statements above are language, type, or runtime behavior. The following are preferences, each with the reason that actually applies:

- **An explicit return type on a public function.** Attributed to Google's guide above. Its rationale is a stated contract at the boundary plus the check the annotation adds; adopting it is a project decision, and an inferred return type is still checked, just against the inferred type.
- **`readonly` on properties that callers should not replace.** The modifier's consequence is a compile-time write error and only that; its rationale is the caller-facing statement, not immutability. Annotating a field regardless of contract adds restrictions the checker will enforce on writes the program never performs.
- **`as const` on literal tables.** The consequence is literal types instead of widened ones; the rationale is that a later `switch` or property read keeps its literal meaning. It protects nothing at run time.

No language rule requires any of these, and none of them changes what a value does when the program runs. Which alias or interface form to export is a separate question with its own conflict walkthrough, owned by [Imports, Names, And Comments](imports-names-and-comments.md#walk-one-alias-versus-interface-conflict).

## What Fails, And Where

- No runtime check is generated for an assertion: a wrong `as` produces no exception and no `null`, and the value keeps the shape it arrived with.
- Assigning to a `readonly` property is a compile-time error, reported as `TS2540`, while a write to state reached through the same property is accepted; nothing enforces the modifier at run time.
- Writing through a `readonly` index signature is `TS2542`.
- An `enum` declaration emits a runtime object with forward and reverse mappings, so `erasableSyntaxOnly` rejects it, as it rejects runtime namespaces, parameter properties, and `import =`/`export =` (`TS1294`).
- `<number>1` is rejected under `erasableSyntaxOnly` by TypeScript 6.0.3 (`TS1294`) even though the 5.8 release notes do not list angle-bracket assertions among the rejected constructs.
- Specifying `importsNotUsedAsValues` in TypeScript 6.0 produces `TS5102`, "Option 'importsNotUsedAsValues' has been removed", because the option no longer exists.
- A `.tsx` file run on Node's native path fails as an unsupported file rather than as a type error.
- A type-only import written without the `type` keyword becomes a value import at run time, so the module fails to load even when the check was green.
- `JSON.parse(text) as Config` compiles and validates nothing, and an unguarded `unknown` cannot be read at all (`TS18046`).
- An index signature reports `TS2413` for a numeric indexer whose value type is not a subtype of the string indexer's and `TS2411` for a declared property outside the index type; a missing property in an indexed access is `TS2339`, and a value used as an index type is `TS2538` or `TS2749`.
- A tuple index beyond the fixed positions is `TS2493`; a rest element after another rest element is `TS1265`, and an optional element after a rest element is `TS1266`.
- A mapped type that declares members is `TS7061`.

## Limits And Ownership

- The angle-bracket assertion list is an unresolved disagreement between two TypeScript pages: the `erasableSyntaxOnly` option page lists the construct, the 5.8 release notes omit it, and TypeScript 6.0.3 rejects it. The two statements stand as published, so no single reconciled list replaces them.
- Node's native execution is pinned to its v26 documentation, as cited: no exact release at which default enablement began is stated here, and the behavior described is that path's documented behavior rather than a statement about every release.
- The Bun pages cited above state no version, and their descriptions of the transpiler ("transpiles every file", "strips out all TypeScript syntax", "without checking their types") are not fully consistent; which wording governs is unresolved, so no claim is made about which constructs Bun transforms.
- The everyday-types and object-types pages are rolling, so re-read the annotation, assertion, and `readonly` text against the compiler version in use; the write and nested-write outcomes described here depend on that version's checking.
- All examples are non-normative illustrations. They were not compiled or executed, and a passing type check would not establish the runtime behavior described.
- JavaScript-only work is excluded: no `allowJs` or `checkJs` guidance, no JavaScript diagnostics, and no JSDoc typing of `.js` files appears here, and a JavaScript-only request is out of scope for this workspace.
- This page provides style guidance only. Validation design — schemas, guards as a contract, and where input is trusted — goes to the production owner (`node-project-writer -> reference/change-design-and-validation.md`); the caller-observable contract of a change belongs to `node-project-writer -> reference/behavior-and-caller-contracts.md`.
- Compiler configuration, option enablement, and the target set a check covers belong to `node-quality-workflow -> reference/quality-scope-and-mutation.md`. Loader, module-kind, and runtime behavior belong to `node-project-reference -> reference/runtime-and-project-structure.md`.
- The repository's deterministic utilities under `scripts/node/` keep their own Bun and repository conventions; they are not ordinary project defaults. Nothing here selects or presupposes Vite, forms an implicit pipeline, or promises compatibility for another runtime, package, or version.
- The method for weighing these sources, and the routing across the style pages, stays with the hub, [Contextual Source-Style Guidance](source-style-guidance.md).
