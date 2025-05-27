const assert = require('assert');
const { formatPrompt, extractVariables } = require('../scripts/prompt_formatter.js');

const CHAT_HISTORY_LOOP_SNIPPET = `{% for turn in chat_history %}\n{{ turn.role }}:\n{{ turn.content }}\n{% endfor %}`;

console.log('Running tests for prompt_formatter.js...\n');

// --- Test extractVariables --- 
console.log('Testing extractVariables...');
assert.deepStrictEqual(extractVariables("Hello world"), {}, 'EV1: No variables');
assert.deepStrictEqual(extractVariables("Hello {{name}}"), { name: 'string' }, 'EV2: One variable');
assert.deepStrictEqual(extractVariables("{{greeting}} {{name}}!"), { greeting: 'string', name: 'string' }, 'EV3: Multiple variables');
assert.deepStrictEqual(extractVariables("Data: {{user location}}"), { "user location": 'string' }, 'EV4: Variable with internal spaces');
assert.deepStrictEqual(extractVariables("Value: {{  spaced_var  }}"), { "spaced_var": 'string' }, 'EV5: Variable with leading/trailing spaces inside braces');
assert.deepStrictEqual(extractVariables("{{name}} and {{name}}"), { name: 'string' }, 'EV6: Repeated variables');
assert.deepStrictEqual(extractVariables("Hello {{}}"), {}, 'EV7: Empty variable tag');
assert.deepStrictEqual(extractVariables("{{variable}} is here"), { variable: 'string' }, 'EV8: Variable at start');
assert.deepStrictEqual(extractVariables("Here is {{variable}}"), { variable: 'string' }, 'EV9: Variable at end');
assert.deepStrictEqual(extractVariables("Hello {{name}}!"), { name: 'string' }, 'EV10: No space after variable'); // Depends on corrected regex
console.log('extractVariables tests passed.\n');

// --- Test formatPrompt - Text Mode ---
console.log('Testing formatPrompt - Text Mode...');
let options_t1 = { name: "text_basic", author: "Tester", mode: "text" };
let expected_t1 = `---
name: text_basic
version: 1
author: Tester
input: {}
mode: text
---
A simple text prompt.`;
assert.strictEqual(formatPrompt("A simple text prompt.", options_t1), expected_t1, 'T1: Basic text');

let options_t2 = { name: "text_autovar", author: "Tester", mode: "text" };
let expected_t2 = `---
name: text_autovar
version: 1
author: Tester
input:
  user_name: string
mode: text
---
Hello {{user_name}}.`;
assert.strictEqual(formatPrompt("Hello {{user_name}}.", options_t2), expected_t2, 'T2: Text with auto-detected variable');

let options_t3 = { name: "text_uservar", author: "Tester", mode: "text", inputs: { item_id: "integer" } };
let expected_t3 = `---
name: text_uservar
version: 1
author: Tester
input:
  item_id: integer
mode: text
---
Process {{item_id}}.`;
assert.strictEqual(formatPrompt("Process {{item_id}}.", options_t3), expected_t3, 'T3: Text with user-defined input type');

let options_t4 = { name: "text_mixedvar", author: "Tester", mode: "text", inputs: { user_name: "string" } };
let expected_t4 = `---
name: text_mixedvar
version: 1
author: Tester
input:
  user_name: string
  auth_code: string
mode: text
---
Welcome {{user_name}}, your code is {{auth_code}}.`;
assert.strictEqual(formatPrompt("Welcome {{user_name}}, your code is {{auth_code}}.", options_t4), expected_t4, 'T4: Text with mixed inputs');
console.log('formatPrompt - Text Mode tests passed.\n');

// --- Test formatPrompt - Chat Mode (Auto History Loop) ---
console.log('Testing formatPrompt - Chat Mode (Auto History Loop)...');
let options_c1 = { name: "chat_auto_user", author: "Tester", mode: "chat" };
let expected_c1_body = `user:\nThis is my first query.\n\n${CHAT_HISTORY_LOOP_SNIPPET}\n\nuser:\n{{current_user_query}}`;
let expected_c1_yaml_inputs = `input:\n  chat_history: list\n  current_user_query: string\n`;
let expected_c1 = `---
name: chat_auto_user
version: 1
author: Tester
${expected_c1_yaml_inputs}mode: chat
---
${expected_c1_body}`;
assert.strictEqual(formatPrompt("This is my first query.", options_c1), expected_c1, 'C1: Basic chat, default initialRole');

let options_c2 = { name: "chat_auto_system", author: "Tester", mode: "chat", initialRole: "system" };
let expected_c2_body = `system:\nYou are a helpful assistant.\n\n${CHAT_HISTORY_LOOP_SNIPPET}\n\nuser:\n{{current_user_query}}`;
let expected_c2 = `---
name: chat_auto_system
version: 1
author: Tester
${expected_c1_yaml_inputs}mode: chat
---
${expected_c2_body}`;
assert.strictEqual(formatPrompt("You are a helpful assistant.", options_c2), expected_c2, 'C2: Basic chat, initialRole: system');

let options_c3 = { name: "chat_auto_var", author: "Tester", mode: "chat", initialRole: "system" };
let expected_c3_yaml_inputs = `input:\n  field: string\n  chat_history: list\n  current_user_query: string\n`;
let expected_c3_body = `system:\nYou are an expert in {{field}}.\n\n${CHAT_HISTORY_LOOP_SNIPPET}\n\nuser:\n{{current_user_query}}`;
let expected_c3 = `---
name: chat_auto_var
version: 1
author: Tester
${expected_c3_yaml_inputs}mode: chat
---
${expected_c3_body}`;
assert.strictEqual(formatPrompt("You are an expert in {{field}}.", options_c3), expected_c3, 'C3: Chat with variable in plainText');

let options_c4 = { name: "chat_auto_userinputs", author: "Tester", mode: "chat", initialRole: "system", inputs: { chat_history: "special_list_type", current_user_query: "special_string_type", custom_var: "boolean" } };
let expected_c4_yaml_inputs = `input:\n  chat_history: special_list_type\n  current_user_query: special_string_type\n  custom_var: boolean\n`;
let expected_c4_body = `system:\nSystem prompt.\n\n${CHAT_HISTORY_LOOP_SNIPPET}\n\nuser:\n{{current_user_query}}`;
let expected_c4 = `---
name: chat_auto_userinputs
version: 1
author: Tester
${expected_c4_yaml_inputs}mode: chat
---
${expected_c4_body}`;
assert.strictEqual(formatPrompt("System prompt.", options_c4), expected_c4, 'C4: Chat with user-defined history/query types');

let options_c5 = { name: "chat_auto_empty", author: "Tester", mode: "chat", initialRole: "system" };
let expected_c5_body = `system:\n\n\n${CHAT_HISTORY_LOOP_SNIPPET}\n\nuser:\n{{current_user_query}}`;
let expected_c5 = `---
name: chat_auto_empty
version: 1
author: Tester
${expected_c1_yaml_inputs}mode: chat
---
${expected_c5_body}`;
assert.strictEqual(formatPrompt("", options_c5), expected_c5, 'C5: Chat with empty plainText');
console.log('formatPrompt - Chat Mode (Auto History Loop) tests passed.\n');

// --- Test formatPrompt - Chat Mode (User Handles History) ---
console.log('Testing formatPrompt - Chat Mode (User Handles History)...');
let c6_plainText = "system:\nThis prompt uses {{chat_history}} directly.\nuser:\n{{user_input}}";
let options_c6 = { name: "chat_userhist_role", author: "Tester", mode: "chat", initialRole: "user" };
let expected_c6_yaml_inputs = `input:\n  chat_history: string\n  user_input: string\n`;
let expected_c6 = `---
name: chat_userhist_role
version: 1
author: Tester
${expected_c6_yaml_inputs}mode: chat
---
${c6_plainText}`;
assert.strictEqual(formatPrompt(c6_plainText, options_c6), expected_c6, 'C6: User handles history, starts with role');

let c7_plainText = "My custom history: {{chat_history}}\nAnd query: {{user_input}}";
let options_c7 = { name: "chat_userhist_norole", author: "Tester", mode: "chat", initialRole: "system" };
let expected_c7_body = `system:\n${c7_plainText}`;
let expected_c7 = `---
name: chat_userhist_norole
version: 1
author: Tester
${expected_c6_yaml_inputs}mode: chat
---
${expected_c7_body}`;
assert.strictEqual(formatPrompt(c7_plainText, options_c7), expected_c7, 'C7: User handles history, no leading role');

let c8_plainText = "system:\nInitial.\n{% for turn in chat_history %}\n{{turn.role}}: {{turn.content}}\n{% endfor %}\nuser:\n{{user_input}}";
let options_c8 = { name: "chat_userhist_jinja", author: "Tester", mode: "chat" };
// extractVariables won't pick up chat_history from {% for ... %} only from {{...}}
// If user wants chat_history in inputs here, they must provide it via options.inputs
let expected_c8_yaml_inputs = `input:\n  user_input: string\n`; 
let expected_c8 = `---
name: chat_userhist_jinja
version: 1
author: Tester
${expected_c8_yaml_inputs}mode: chat
---
${c8_plainText}`;
assert.strictEqual(formatPrompt(c8_plainText, options_c8), expected_c8, 'C8: User handles history with Jinja loop');
console.log('formatPrompt - Chat Mode (User Handles History) tests passed.\n');

// --- Test formatPrompt - Error Handling ---
console.log('Testing formatPrompt - Error Handling...');
assert.throws(() => formatPrompt("text", { author: "T", mode: "text" }), Error, 'E1: Missing name');
assert.throws(() => formatPrompt("text", { name: "N", mode: "text" }), Error, 'E2: Missing author');
assert.throws(() => formatPrompt("text", { name: "N", author: "T" }), Error, 'E3: Missing mode');
assert.throws(() => formatPrompt("text", { name: "N", author: "T", mode: "unknown" }), Error, 'E4: Invalid mode');
assert.throws(() => formatPrompt("text", { name: "N", author: "T", mode: "chat", initialRole: "unknown" }), Error, 'E5: Invalid initialRole for auto-loop');
console.log('formatPrompt - Error Handling tests passed.\n');

console.log('All tests for prompt_formatter.js completed successfully!');
