const fs = require('fs');
const path = require('path');

/**
 * Extracts variables from text formatted as {{variable_name}}.
 * @param {string} text - The text to parse for variables.
 * @returns {Object.<string, string>} An object mapping variable names to their type (defaulted to 'string').
 */
function extractVariables(text) {
    const regex = /\{\{([^}]+)\}\}/g; // Corrected regex: removed space before g
    const variables = {};
    let match;
    while ((match = regex.exec(text)) !== null) {
        const varName = match[1].trim();
        if (varName) { // Ensure varName is not empty
            variables[varName] = 'string'; // Default type to string
        }
    }
    return variables;
}

/**
 * Formats a plain text prompt into the schema-defined structure.
 * @param {string} plainText - The plain text content of the prompt.
 * @param {object} options - Configuration options.
 * @param {string} options.name - The name of the prompt.
 * @param {string} options.author - The author of the prompt.
 * @param {string} options.mode - The mode of the prompt ('text' or 'chat').
 * @param {number} [options.version=1] - The version of the prompt.
 * @param {string} [options.initialRole='user'] - The initial role for 'chat' mode prompts.
 * @param {Object.<string, string>} [options.inputs] - Predefined input variables. Auto-detected if not provided.
 * @returns {string} The formatted prompt string.
 */
function formatPrompt(plainText, options) {
    const {
        name,
        author,
        mode,
        version = 1,
        initialRole = 'user',
        inputs // User-provided inputs
    } = options;

    if (!name || !author || !mode) {
        throw new Error("Missing required options: name, author, and mode must be provided.");
    }
    if (mode !== 'text' && mode !== 'chat') {
        throw new Error("Mode must be 'text' or 'chat'.");
    }

    // Start with user-provided inputs, then add auto-detected ones from plainText if not already present
    const detectedInputs = { ...(inputs || {}) };
    const autoDetectedFromText = extractVariables(plainText);
    for (const key in autoDetectedFromText) {
        if (!detectedInputs.hasOwnProperty(key)) {
            detectedInputs[key] = autoDetectedFromText[key];
        }
    }

    let yamlString = '---\n';
    yamlString += `name: ${name}\n`;
    yamlString += `version: ${version}\n`;
    yamlString += `author: ${author}\n`;

    if (Object.keys(detectedInputs).length === 0) {
        yamlString += 'input: {}\n';
    } else {
        yamlString += 'input:\n';
        for (const [key, value] of Object.entries(detectedInputs)) {
            yamlString += `  ${key}: ${value}\n`;
        }
    }
    yamlString += `mode: ${mode}\n`;
    yamlString += '---\n';

    let body = '';
    if (mode === 'chat') {
        const chatHistoryLoop = `
{% for turn in chat_history %}
{{ turn.role }}:
{{ turn.content }}
{% endfor %}`; // Removed leading/trailing newlines to control spacing better
        const currentUserQueryVar = 'current_user_query';
        const rolePrefixRegex = /^\s*(system|user|assistant|tool):\s*/i;
        // Check if chat_history is already used in the template by the user
        const plainTextHandlesHistory = /\{\{[\s\S]*chat_history[\s\S]*\}\}|\{%[\s\S]*chat_history[\s\S]*%\}/i.test(plainText);

        if (!plainTextHandlesHistory) {
            // Auto-add history loop and current query placeholder
            const bodyParts = [];
            const currentMessageRole = initialRole.toLowerCase();
            const validRoles = ['system', 'user', 'assistant', 'tool'];
            if (!validRoles.includes(currentMessageRole)) {
                throw new Error(`Invalid initialRole '${initialRole}'. Must be one of ${validRoles.join(', ')}.`);
            }

            // Part 1: The initial message (from plainText and initialRole)
            bodyParts.push(`${currentMessageRole}:\n${plainText.trimStart()}`);

            // Part 2: The chat history loop
            bodyParts.push(chatHistoryLoop.trim());
            if (!detectedInputs.hasOwnProperty('chat_history')) {
                detectedInputs['chat_history'] = 'list';
            }

            // Part 3: Placeholder for the actual current user query
            bodyParts.push(`user:\n{{${currentUserQueryVar}}}`); // Standardizing to 'user:' for the query
            if (!detectedInputs.hasOwnProperty(currentUserQueryVar)) {
                detectedInputs[currentUserQueryVar] = 'string';
            }
            body = bodyParts.join('\n\n'); // Join with double newlines for separation

        } else {
            // plainText is assumed to handle history and roles structure itself
            if (rolePrefixRegex.test(plainText.trimStart())) {
                body = plainText; // User provided full structure starting with a role
            } else {
                // plainText handles history but doesn't start with a role, so prepend initialRole
                const roleToUse = initialRole.toLowerCase();
                const validRoles = ['system', 'user', 'assistant', 'tool'];
                if (!validRoles.includes(roleToUse)) {
                    throw new Error(`Invalid initialRole '${initialRole}'. Must be one of ${validRoles.join(', ')}.`);
                }
                body = `${roleToUse}:\n${plainText.trimStart()}`;
            }
        }
    } else { // mode === 'text'
        body = plainText;
    }

    // Re-generate YAML string for inputs as detectedInputs might have changed
    let inputYaml = '';
    if (Object.keys(detectedInputs).length === 0) {
        inputYaml = 'input: {}\n';
    } else {
        inputYaml = 'input:\n';
        for (const [key, value] of Object.entries(detectedInputs)) {
            inputYaml += `  ${key}: ${value}\n`;
        }
    }

    yamlString = '---\n';
    yamlString += `name: ${name}\n`;
    yamlString += `version: ${version}\n`;
    yamlString += `author: ${author}\n`;
    yamlString += inputYaml; // Use the updated inputYaml
    yamlString += `mode: ${mode}\n`;
    yamlString += '---\n';

    return yamlString + body;
}

// Command-line interface
if (require.main === module) {
    const args = process.argv.slice(2);
    const options = {
        version: 1 // Default version
    };
    let plainText;
    let textSource; // To store how text was provided, for error messages
    let outputFile;

    for (let i = 0; i < args.length; i++) {
        const arg = args[i];
        const nextArg = args[i+1];

        if (arg === '--text' && nextArg !== undefined) {
            plainText = nextArg; textSource = '--text'; i++;
        } else if (arg === '--file' && nextArg !== undefined) {
            try {
                plainText = fs.readFileSync(path.resolve(nextArg), 'utf-8');
                textSource = `--file ${nextArg}`;
                i++;
            } catch (e) {
                console.error(`Error reading file ${nextArg}: ${e.message}`);
                process.exit(1);
            }
        } else if (arg === '--output' && nextArg !== undefined) {
            outputFile = path.resolve(nextArg); i++;
        } else if (arg === '--name' && nextArg !== undefined) {
            options.name = nextArg; i++;
        } else if (arg === '--author' && nextArg !== undefined) {
            options.author = nextArg; i++;
        } else if (arg === '--mode' && nextArg !== undefined) {
            options.mode = nextArg; i++;
        } else if (arg === '--version' && nextArg !== undefined) {
            const v = parseInt(nextArg, 10);
            if (isNaN(v)) {
                console.error(`Error: --version must be an integer. Received: ${nextArg}`);
                process.exit(1);
            }
            options.version = v; i++;
        } else if (arg === '--initialRole' && nextArg !== undefined) {
            options.initialRole = nextArg; i++;
        } else if (arg === '--inputs' && nextArg !== undefined) {
            try {
                options.inputs = JSON.parse(nextArg); i++;
            } catch (e) {
                console.error(`Error parsing --inputs JSON string: ${e.message}\nProvided: ${nextArg}`);
                process.exit(1);
            }
        } else if (arg === '--help' || arg === '-h') {
            printUsage();
            process.exit(0);
        } else {
            console.error(`Unknown or incomplete argument: ${arg}`);
            printUsage();
            process.exit(1);
        }
    }

    if (plainText === undefined) {
        console.error("Error: Plain text prompt content must be provided via --text <string> or --file <filepath>.");
        printUsage();
        process.exit(1);
    }
     if (!options.name || !options.author || !options.mode) {
        console.error("Error: --name, --author, and --mode are required arguments.");
        printUsage();
        process.exit(1);
    }


    try {
        const formattedPrompt = formatPrompt(plainText, options);
        if (outputFile) {
            fs.writeFileSync(outputFile, formattedPrompt);
            console.log(`Formatted prompt written to ${outputFile}`);
        } else {
            console.log(formattedPrompt);
        }
    } catch (e) {
        console.error(`Error formatting prompt (source: ${textSource || 'unknown'}): ${e.message}`);
        process.exit(1);
    }
}

function printUsage() {
    console.log(`
Usage: node prompt_formatter.js [options]

Options:
  --text <string>         Plain text content for the prompt.
  --file <filepath>       Path to a file containing the plain text content.
                          (Either --text or --file is required)

  --name <string>         (Required) Name for the prompt (e.g., my_chat_prompt).
  --author <string>       (Required) Author of the prompt.
  --mode <text|chat>      (Required) Mode of the prompt.

  --output <filepath>     (Optional) Path to save the formatted prompt.
                          If not provided, output is printed to stdout.
  --version <int>         (Optional) Prompt version. Defaults to 1.
  --initialRole <role>    (Optional, for chat mode) Initial role (system, user,
                          assistant, tool). Defaults to 'user'.
  --inputs <json_string>  (Optional) JSON string for input variables and types.
                          Example: '{"query":"string", "context":"string"}'
                          If not provided, variables like {{var}} are auto-detected.
  -h, --help              Show this help message.

Examples:
  node prompt_formatter.js --text "Hello {{name}}!" --name greeting --author "Me" --mode text
  node prompt_formatter.js --file ./my_prompt.txt --name chat_init --author "AI Team" --mode chat --initialRole system --output ./formatted_prompt.md
  node prompt_formatter.js --text "Summarize: {{document}}" --name summarizer --author "Dev" --mode text --inputs '{"document":"string"}'
`);
}

module.exports = { formatPrompt, extractVariables }; // For programmatic use
