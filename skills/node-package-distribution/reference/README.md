# Package Artifact And Consumer References

Use this index to route a package artifact or consumer question to one of the three detail pages in this workspace: [Artifact And Consumer Boundaries](artifact-and-consumer-boundaries.md) for the delivered contract and registry limits, [Pack Preview And Archive Contents](pack-preview-and-archive-contents.md) for file selection and archive evidence, and [Consumer Resolution And Declarations](consumer-resolution-and-declarations.md) for resolution and declaration failures. The pages carry the distinctions, examples, and evidence limits; this index only routes.

## Find Guidance By Concern

- **Which package surface reaches the consumer.** [Identify the delivered contract](artifact-and-consumer-boundaries.md#identify-the-delivered-contract) covers package metadata, module formats, entry points, declarations, included files, and runtime targets.
- **Whether a build, pack, or publish result answers the question.** [Distinguish build, pack, and publish](artifact-and-consumer-boundaries.md#distinguish-build-pack-and-publish) separates their outcomes and scopes packer contracts to the manager and version that states them.
- **What a pack command would select.** [Read a preview as a selection contract](pack-preview-and-archive-contents.md#read-a-preview-as-a-selection-contract) keeps a prospective listing distinct from the tarball a consumer receives.
- **Why an expected file is missing from the archive.** [Trace an omitted checkout file](pack-preview-and-archive-contents.md#trace-an-omitted-checkout-file) explains the selection, ignore, and bundling rules that decide archive members.
- **Whether consumers can use the artifact.** [Verify the installed archive](consumer-resolution-and-declarations.md#verify-the-installed-archive) describes the bounded install-and-check chain and why a source-tree or linked test does not stand in for it.
- **Why a packed subpath fails.** [Diagnose a packed subpath in four ordered layers](consumer-resolution-and-declarations.md#diagnose-a-packed-subpath-in-four-ordered-layers) separates tarball contents, export-map rejection, loader or format failure, and declaration resolution.
- **Which compatibility claim is supportable.** [Preserve scope and compatibility](artifact-and-consumer-boundaries.md#preserve-scope-and-compatibility) covers registry-evidence limits, compatibility claims, and the direct-use Vite boundary.

## Keep Evidence At The Right Boundary

Build output, packed archive contents, consumer runtime behavior, declaration resolution, and registry publication are separate evidence layers. A result in one does not combine with another into a single pass: a successful build does not prove the archive contains the target, an installed runtime import does not prove declaration resolution, and neither establishes registry publication. Statements about `npm pack` behavior are scoped to npm and the version named beside them; do not transfer them to Bun or to another version.

Validate only the requested artifact surfaces, runtime conditions, and versions, and do not infer publication or broader compatibility from a local check.

## Keep Index Ownership Explicit

This index routes; it does not answer, and a route grants no operation, tool, edit, approval, sequence, or completion authority. The workspace covers TypeScript packages built for Node.js or Bun, and a JavaScript-only request is out of scope. This operation owns authorized package artifact and consumer outcomes only and does not imply application deployment, release governance, publication, registry administration, or organization-wide security policy. Do not select or rely on Vite workflows; incidental transitive presence is not a graph-absence claim.
