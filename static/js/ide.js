// Monaco Editor and Python IDE functionality for Education Management System

let editor;
let isCodeRunning = false;

// Initialize Monaco Editor when the page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeMonacoEditor();
    setupEventListeners();
    setupKeyboardShortcuts();
});

function initializeMonacoEditor() {
    // Configure Monaco Editor loader
    require.config({ 
        paths: { 
            'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs' 
        }
    });

    require(['vs/editor/editor.main'], function() {
        // Get initial code from assignment data or default
        let initialCode = '# Write your Python code here\nprint("Hello, World!")';
        
        if (window.assignmentData) {
            if (window.assignmentData.submissionCode) {
                initialCode = window.assignmentData.submissionCode;
            } else if (window.assignmentData.starterCode) {
                initialCode = window.assignmentData.starterCode;
            }
        }

        // Create Monaco Editor instance
        editor = monaco.editor.create(document.getElementById('codeEditor'), {
            value: initialCode,
            language: 'python',
            theme: 'vs-dark',
            fontSize: 14,
            fontFamily: "'Fira Code', 'Monaco', 'Consolas', monospace",
            fontLigatures: true,
            lineNumbers: 'on',
            roundedSelection: false,
            scrollBeyondLastLine: false,
            readOnly: false,
            automaticLayout: true,
            minimap: {
                enabled: true
            },
            wordWrap: 'on',
            contextmenu: true,
            selectOnLineNumbers: true,
            glyphMargin: true,
            folding: true,
            foldingStrategy: 'indentation',
            showFoldingControls: 'always',
            matchBrackets: 'always',
            autoIndent: 'full',
            formatOnPaste: true,
            formatOnType: true,
            tabSize: 4,
            insertSpaces: true,
            detectIndentation: false
        });

        // Configure Python language features
        monaco.languages.setMonarchTokensProvider('python', {
            tokenizer: {
                root: [
                    [/\b(def|class|if|elif|else|for|while|try|except|finally|with|import|from|return|yield|pass|break|continue|and|or|not|in|is|lambda|async|await)\b/, 'keyword'],
                    [/\b(True|False|None)\b/, 'constant'],
                    [/\b(int|float|str|bool|list|dict|tuple|set)\b/, 'type'],
                    [/\b(print|input|len|range|enumerate|zip|map|filter|sorted|sum|max|min|abs|round)\b/, 'builtin'],
                    [/#.*$/, 'comment'],
                    [/".*?"/, 'string'],
                    [/'.*?'/, 'string'],
                    [/\b\d+\b/, 'number'],
                    [/\b\d+\.\d+\b/, 'number']
                ]
            }
        });

        // Auto-save code as user types (debounced)
        let saveTimeout;
        editor.onDidChangeModelContent(() => {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                autoSaveCode();
            }, 2000);
        });

        console.log('Monaco Editor initialized successfully');
    });
}

function setupEventListeners() {
    // Run Code button
    const runButton = document.getElementById('runCode');
    if (runButton) {
        runButton.addEventListener('click', runCode);
    }

    // Submit Assignment button
    const submitButton = document.getElementById('submitAssignment');
    if (submitButton) {
        submitButton.addEventListener('click', submitAssignment);
    }

    // Reset Code button
    const resetButton = document.getElementById('resetCode');
    if (resetButton) {
        resetButton.addEventListener('click', resetCode);
    }

    // Clear Code button
    const clearButton = document.getElementById('clearCode');
    if (clearButton) {
        clearButton.addEventListener('click', clearCode);
    }

    // Format Code button
    const formatButton = document.getElementById('formatCode');
    if (formatButton) {
        formatButton.addEventListener('click', formatCode);
    }

    // Save Code button
    const saveButton = document.getElementById('saveCode');
    if (saveButton) {
        saveButton.addEventListener('click', saveCode);
    }

    // Copy Code button
    const copyButton = document.getElementById('copyCode');
    if (copyButton) {
        copyButton.addEventListener('click', copyCode);
    }
}

function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl+Enter or Cmd+Enter to run code
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            runCode();
        }

        // Ctrl+S or Cmd+S to save code
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            saveCode();
        }

        // Ctrl+Shift+F or Cmd+Shift+F to format code
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'F') {
            e.preventDefault();
            formatCode();
        }
    });
}

async function runCode() {
    if (!editor || isCodeRunning) return;

    const code = editor.getValue();
    const outputContainer = document.getElementById('outputContent');
    const loadingIndicator = document.getElementById('loadingIndicator');
    
    if (!code.trim()) {
        showOutput('Error: No code to execute', 'error');
        return;
    }

    // Show loading state
    isCodeRunning = true;
    const runButton = document.getElementById('runCode');
    if (runButton) {
        runButton.disabled = true;
        runButton.innerHTML = '<div class="spinner-border spinner-border-sm me-2"></div>Running...';
    }

    if (loadingIndicator) {
        loadingIndicator.classList.remove('d-none');
    }
    if (outputContainer) {
        outputContainer.style.display = 'none';
    }

    try {
        const requestData = {
            code: code
        };

        // Include assignment ID if this is an assignment
        if (window.assignmentData && window.assignmentData.id) {
            requestData.assignment_id = window.assignmentData.id;
        }

        const response = await fetch('/execute_code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });

        const result = await response.json();

        if (response.ok) {
            if (result.success) {
                showOutput(result.output || 'Code executed successfully (no output)', 'success');
            } else {
                showOutput(result.error || 'Unknown error occurred', 'error');
            }
        } else {
            showOutput(`Server error: ${result.error || 'Unknown error'}`, 'error');
        }

    } catch (error) {
        console.error('Error executing code:', error);
        showOutput(`Network error: ${error.message}`, 'error');
    } finally {
        // Reset loading state
        isCodeRunning = false;
        if (runButton) {
            runButton.disabled = false;
            runButton.innerHTML = '<i data-feather="play" class="me-1"></i>Run Code';
            feather.replace();
        }
        if (loadingIndicator) {
            loadingIndicator.classList.add('d-none');
        }
        if (outputContainer) {
            outputContainer.style.display = 'block';
        }
    }
}

async function submitAssignment() {
    if (!editor) return;

    const code = editor.getValue();
    
    if (!code.trim()) {
        showToast('Please write some code before submitting', 'warning');
        return;
    }

    if (!window.assignmentData || !window.assignmentData.id) {
        showToast('No assignment found to submit to', 'error');
        return;
    }

    const submitButton = document.getElementById('submitAssignment');
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<div class="spinner-border spinner-border-sm me-2"></div>Submitting...';
    }

    try {
        const response = await fetch('/execute_code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                code: code,
                assignment_id: window.assignmentData.id
            })
        });

        const result = await response.json();

        if (response.ok) {
            showToast('Assignment submitted successfully!', 'success');
            
            // Update submission status in UI
            setTimeout(() => {
                location.reload();
            }, 1500);
        } else {
            showToast(`Submission failed: ${result.error}`, 'error');
        }

    } catch (error) {
        console.error('Error submitting assignment:', error);
        showToast(`Submission failed: ${error.message}`, 'error');
    } finally {
        if (submitButton) {
            submitButton.disabled = false;
            submitButton.innerHTML = '<i data-feather="send" class="me-1"></i>Submit Assignment';
            feather.replace();
        }
    }
}

function resetCode() {
    if (!editor) return;

    const originalCode = window.assignmentData?.starterCode || '# Write your Python code here\nprint("Hello, World!")';
    
    if (confirm('Are you sure you want to reset your code to the original starter code? All changes will be lost.')) {
        editor.setValue(originalCode);
        showToast('Code reset to starter code', 'info');
    }
}

function clearCode() {
    if (!editor) return;

    if (confirm('Are you sure you want to clear all code? This action cannot be undone.')) {
        editor.setValue('# Write your Python code here\n');
        showToast('Code cleared', 'info');
    }
}

function formatCode() {
    if (!editor) return;

    // Trigger Monaco's built-in formatting
    editor.getAction('editor.action.formatDocument').run();
    showToast('Code formatted', 'success');
}

function saveCode() {
    if (!editor) return;

    const code = editor.getValue();
    
    // Save to localStorage
    const saveKey = window.assignmentData?.id ? `assignment_${window.assignmentData.id}` : 'ide_code';
    localStorage.setItem(saveKey, code);
    
    showToast('Code saved locally', 'success');
}

function copyCode() {
    if (!editor) return;

    const code = editor.getValue();
    
    if (!code.trim()) {
        showToast('No code to copy', 'warning');
        return;
    }

    // Use the Clipboard API to copy the code
    navigator.clipboard.writeText(code).then(() => {
        showToast('Code copied to clipboard!', 'success');
        
        // Update button temporarily to show feedback
        const copyButton = document.getElementById('copyCode');
        if (copyButton) {
            const originalText = copyButton.innerHTML;
            copyButton.innerHTML = '<i data-feather="check" class="me-1"></i>Copied!';
            copyButton.classList.remove('btn-outline-secondary');
            copyButton.classList.add('btn-success');
            
            setTimeout(() => {
                copyButton.innerHTML = originalText;
                copyButton.classList.remove('btn-success');
                copyButton.classList.add('btn-outline-secondary');
                feather.replace();
            }, 2000);
        }
    }).catch(err => {
        console.error('Failed to copy code: ', err);
        showToast('Failed to copy code. Please select and copy manually.', 'error');
    });
}

function autoSaveCode() {
    if (!editor) return;

    const code = editor.getValue();
    const saveKey = window.assignmentData?.id ? `assignment_${window.assignmentData.id}_autosave` : 'ide_code_autosave';
    localStorage.setItem(saveKey, code);
    
    // Show subtle save indicator
    const saveIndicator = document.createElement('div');
    saveIndicator.className = 'position-fixed top-0 end-0 p-2 text-muted small';
    saveIndicator.innerHTML = '<i data-feather="save" class="me-1"></i>Auto-saved';
    saveIndicator.style.zIndex = '9999';
    document.body.appendChild(saveIndicator);
    
    feather.replace();
    
    setTimeout(() => {
        saveIndicator.remove();
    }, 2000);
}

function showOutput(content, type = 'info') {
    const outputContainer = document.getElementById('outputContent');
    if (!outputContainer) return;

    // Style based on type
    let textColor = 'text-light';
    let icon = 'terminal';
    
    switch (type) {
        case 'success':
            textColor = 'text-success';
            icon = 'check-circle';
            break;
        case 'error':
            textColor = 'text-danger';
            icon = 'x-circle';
            break;
        case 'warning':
            textColor = 'text-warning';
            icon = 'alert-triangle';
            break;
    }

    // Format timestamp
    const timestamp = new Date().toLocaleTimeString();
    
    outputContainer.innerHTML = `
        <div class="${textColor} mb-2">
            <i data-feather="${icon}" class="me-2"></i>
            <small>[${timestamp}]</small>
        </div>
        <pre class="mb-0">${escapeHtml(content)}</pre>
    `;
    
    feather.replace();
}

function loadExample(exampleType) {
    if (!editor) return;

    const examples = {
        hello_world: `# Hello World Example
print("Hello, World!")
print("Welcome to Python programming!")

name = input("What's your name? ")
print(f"Nice to meet you, {name}!")`,

        variables: `# Variables and Data Types Example
# Numbers
age = 25
height = 5.9
pi = 3.14159

# Strings
name = "Alice"
message = "Hello, Python!"

# Booleans
is_student = True
is_graduated = False

# Lists
fruits = ["apple", "banana", "orange"]
numbers = [1, 2, 3, 4, 5]

# Print information
print(f"Name: {name}")
print(f"Age: {age}")
print(f"Height: {height}")
print(f"Fruits: {fruits}")
print(f"Is student: {is_student}")`,

        loops: `# Loops Example
# For loop with range
print("Counting from 1 to 5:")
for i in range(1, 6):
    print(f"Count: {i}")

print("\\nFruits in my basket:")
fruits = ["apple", "banana", "orange", "grape"]
for fruit in fruits:
    print(f"- {fruit}")

# While loop
print("\\nCountdown:")
count = 5
while count > 0:
    print(f"{count}...")
    count -= 1
print("Blast off! 🚀")

# List comprehension
squares = [x**2 for x in range(1, 6)]
print(f"\\nSquares: {squares}")`,

        functions: `# Functions Example
def greet(name, age=None):
    """Greet a person with their name and optionally their age."""
    if age:
        return f"Hello {name}! You are {age} years old."
    else:
        return f"Hello {name}!"

def calculate_area(length, width):
    """Calculate the area of a rectangle."""
    area = length * width
    return area

def is_even(number):
    """Check if a number is even."""
    return number % 2 == 0

# Using the functions
print(greet("Alice"))
print(greet("Bob", 25))

area = calculate_area(10, 5)
print(f"Area of rectangle: {area}")

numbers = [1, 2, 3, 4, 5, 6]
for num in numbers:
    if is_even(num):
        print(f"{num} is even")
    else:
        print(f"{num} is odd")`
    };

    const code = examples[exampleType];
    if (code) {
        editor.setValue(code);
        showToast(`Loaded ${exampleType.replace('_', ' ')} example`, 'success');
    }
}

// Utility function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Toast notification function (reuse from main.js if available)
function showToast(message, type = 'info') {
    if (window.EduSystem && window.EduSystem.showToast) {
        window.EduSystem.showToast(message, type);
        return;
    }

    // Fallback toast implementation
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// Export functions for external use
window.IDEController = {
    runCode,
    submitAssignment,
    resetCode,
    clearCode,
    formatCode,
    saveCode,
    loadExample,
    getEditorContent: () => editor ? editor.getValue() : '',
    setEditorContent: (code) => editor ? editor.setValue(code) : null
};

// Handle page unload to save code
window.addEventListener('beforeunload', function() {
    if (editor) {
        autoSaveCode();
    }
});
