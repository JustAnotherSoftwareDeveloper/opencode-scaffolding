import type { Root, Table } from "mdast";
import { visit } from "unist-util-visit";
import type { VFile } from "vfile";

export type LintProfile = "generic" | "proposal";

function noTablesPlugin(_options?: undefined) {
  const transformer = (tree: Root, file: VFile): void => {
    visit(tree, "table", (node: Table) => {
      file.message("Tables are not allowed", node, "no-tables");
    });
  };
  return transformer;
}

export { noTablesPlugin };
