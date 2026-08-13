#!/usr/bin/env node
/* Repository validator.  Its profile vocabulary is read from the published schema. */
const fs = require('node:fs');
const path = require('node:path');
const YAML = require('yaml');

const schemaPath = path.join(__dirname, '..', 'skills', 'skill-architect', 'references', 'skill-selection-profile.schema.json');
const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));
const classes = new Set(schema.properties.class.enum);
const groups = new Set(Object.keys(schema.properties.selection.properties.tags.properties));
const optional = new Set(['version', 'license', 'compatibility', 'metadata', 'permission']);
const obsolete = new Set(['schema_version', 'cues', 'relationships', 'facets', 'routing', 'location', 'score', 'rank', 'threshold']);
const nameRe = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;

function items(value, field, names = false) {
  if (!Array.isArray(value) || value.length < 1 || value.length > 32) throw new Error(`${field} must be a non-empty array of at most 32 items`);
  if (new Set(value).size !== value.length) throw new Error(`${field} must be unique`);
  for (const item of value) {
    if (typeof item !== 'string' || item.length < 1 || item.length > 128 || item.trim() !== item || /[\r\n]/.test(item)) throw new Error(`${field} must contain trimmed strings`);
    if (names && !nameRe.test(item)) throw new Error(`${field} must contain canonical skill names`);
  }
}
function profileErrors(data) {
  const errors = [];
  if (!data || typeof data !== 'object' || Array.isArray(data)) return ['frontmatter must be an object'];
  for (const key of Object.keys(data)) if (obsolete.has(key)) errors.push(`obsolete metadata field: ${key}`);
  const allowed = new Set(['name', 'description', 'selection', 'class', ...optional]);
  for (const key of Object.keys(data)) if (!allowed.has(key)) errors.push(`unknown metadata field: ${key}`);
  if (typeof data.name !== 'string' || !nameRe.test(data.name) || data.name.length > 128) errors.push('name must be a canonical skill name');
  if (typeof data.description !== 'string' || !data.description.trim() || data.description.length > 1024 || data.description.trim() !== data.description || /[\r\n]/.test(data.description)) errors.push('description must be a trimmed single-line string');
  if (!classes.has(data.class)) errors.push('class must be a canonical skill class');
  const s = data.selection;
  if (!s || typeof s !== 'object' || Array.isArray(s)) return [...errors, 'selection is required and must be an object'];
  for (const key of Object.keys(s)) if (!['role', 'aliases', 'tags', 'use_when', 'not_for', 'supports'].includes(key)) errors.push(`unknown selection field: ${key}`);
  if (!['owner', 'support', 'reference'].includes(s.role)) errors.push('selection.role must be owner, support, or reference');
  if ('aliases' in s) try { items(s.aliases, 'selection.aliases'); } catch (e) { errors.push(e.message); }
  if (!s.tags || typeof s.tags !== 'object' || !Object.keys(s.tags).length) errors.push('selection.tags must contain at least one tag group');
  else { for (const key of Object.keys(s.tags)) { if (!groups.has(key)) errors.push(`unknown tag group: ${key}`); else try { items(s.tags[key], `tags.${key}`); } catch (e) { errors.push(e.message); } } }
  for (const key of ['use_when', 'not_for']) if (key in s) try { items(s[key], `selection.${key}`); } catch (e) { errors.push(e.message); }
  if ('supports' in s) try { items(s.supports, 'selection.supports', true); } catch (e) { errors.push(e.message); }
  if (Array.isArray(s.supports) && s.supports.includes(data.name)) errors.push('selection.supports cannot contain the skill itself');
  for (const key of optional) if (key in data && key !== 'metadata' && (typeof data[key] !== 'string' || !data[key].trim() || data[key].trim() !== data[key])) errors.push(`${key} must be a trimmed string`);
  if ('metadata' in data && (!data.metadata || typeof data.metadata !== 'object' || Array.isArray(data.metadata))) errors.push('metadata must be an object');
  return errors;
}
function validateSkillFile(file) {
  const errors = [];
  if (!fs.existsSync(file)) return { valid: false, errors: [`File not found: ${file}`] };
  if (path.basename(file) !== 'SKILL.md') errors.push('path must end in SKILL.md');
  const text = fs.readFileSync(file, 'utf8');
  if (!text.startsWith('---\n')) return { valid: false, errors: [...errors, "frontmatter must start with '---'"] };
  const end = text.indexOf('\n---', 4);
  if (end < 0) return { valid: false, errors: [...errors, 'frontmatter closing delimiter is missing'] };
  let data; try { data = YAML.parse(text.slice(4, end)); } catch (e) { return { valid: false, errors: [...errors, `Frontmatter YAML parse error: ${e.message}`] }; }
  errors.push(...profileErrors(data));
  if (data && typeof data === 'object' && data.name && data.name !== path.basename(path.dirname(file))) errors.push(`name '${data.name}' does not match directory '${path.basename(path.dirname(file))}'`);
  const body = text.slice(end + 4);
  if (!body.trim()) errors.push('body must not be empty');
  else if (classes.has(data.class)) { const numbered = /^\s*\d+[.)]\s+/m.test(body); if (['operation', 'delegated', 'inline'].includes(data.class) && !numbered) errors.push('active classes must define numbered execution steps'); if (['planning', 'documentation'].includes(data.class) && numbered) errors.push('planning and documentation classes must not define execution steps'); if (['planning', 'documentation'].includes(data.class) && data.selection?.role !== 'reference') errors.push('planning and documentation classes must use selection.role reference'); }
  return { valid: errors.length === 0, errors };
}
if (require.main === module) { const results = process.argv.slice(2).map(validateSkillFile); process.stdout.write(JSON.stringify(results.length === 1 ? results[0] : results) + '\n'); if (results.some(r => !r.valid)) process.exitCode = 1; }
module.exports = { validateSkillFile, profileErrors };
