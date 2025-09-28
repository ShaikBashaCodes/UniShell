# UniShell - Advanced Human-Focused Code Generator

UniShell is an intelligent command-line interface that combines AI-powered natural language processing with multi-language programming support. Built for developers who want to generate, compile, and run code using intuitive human commands, UniShell transforms coding workflows by understanding plain English instructions and converting them into executable programs across multiple programming languages.

## 🏆 Hackathon Track

**Track**: Python Language Challenge - Exactly 250 Lines  
This project was developed for a hackathon with the constraint of creating a feature-rich Python application in exactly 250 lines of code, demonstrating clean, efficient programming practices while maximizing functionality.

## ✨ Features

### 🤖 **AI-Powered Natural Language Processing**
- **Smart Command Understanding**: Converts natural language into structured actions
- **Example**: `"create a bubble sort algorithm using java in C:\Projects"` → Generates Java bubble sort code in specified directory
- **Fallback Parser**: Works without AI when API key is unavailable

### 🌐 **Multi-Language Support**
- **Supported Languages**: Python, Java, C, C++, JavaScript
- **Auto-Detection**: Intelligently detects target language from user input
- **Example**: `"generate calculator using python and java"` → Creates calculator programs in both languages

### 🔧 **Integrated Development Workflow**
- **Code Generation**: AI-generated production-ready code with proper error handling
- **Compilation**: Automatic compilation for Java, C, and C++ files
- **Execution**: Run programs directly from UniShell
- **Code Explanation**: AI-powered code analysis and documentation

### 📁 **Smart File Management**
- **Intelligent Naming**: AI-generated relevant filenames based on code purpose
- **Directory Handling**: Supports custom paths and automatic directory creation
- **File Detection**: Extracts filenames from natural language commands

### 🎯 **Interactive Commands**

#### Generation Commands:
```bash
🚀 UniShell > generate bubble sort using java
🚀 UniShell > create calculator using python in C:\Projects
🚀 UniShell > make fibonacci sequence using java and python
```

#### Execution Commands:
```bash
🚀 UniShell > run calculator.py
🚀 UniShell > compile BubbleSort.java
🚀 UniShell > explain fibonacci.py
```

#### System Commands:
```bash
🚀 UniShell > help          # Show command guide
🚀 UniShell > clear         # Reset session data
🚀 UniShell > cls           # Clear screen
🚀 UniShell > exit          # Exit with session summary
```

### 📊 **Session Management**
- **Command History**: Tracks last 10 commands
- **File Tracking**: Monitors all generated files
- **Error Logging**: Records AI-analyzed errors
- **Session Persistence**: Saves data to JSON configuration

## 🛠️ Technologies Used

- **Python 3.8+**: Core programming language
- **OpenAI API**: AI-powered natural language processing via Hugging Face
- **JSON**: Configuration and session data storage
- **Subprocess**: Cross-platform compiler and runtime integration
- **Regular Expressions**: Pattern matching for language detection
- **PathLib**: Modern file path handling
- **Python-dotenv**: Environment variable management

## 🚀 Setup and Installation

### Prerequisites
1. **Python 3.8 or newer** installed and added to system PATH
2. **Java Development Kit (JDK)** for Java compilation and execution
3. **C/C++ Compiler**:
   - **Windows**: Install MinGW or use WSL with gcc/g++
   - **Linux/macOS**: gcc and g++ (usually pre-installed)

### Step-by-Step Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/ShaikBashaCodes/UniShell.git
cd UniShell/UniShell
```

#### 2. Install Python Dependencies
```bash
pip install python-dotenv openai
```

#### 3. Set Up Environment Variables
Create a `.env` file in the project root:
```env
HUGGING_FACE_API_KEY=your_hugging_face_api_key_here
```

#### 4. Create Configuration File
The config.json file is already included in this repository with default settings and session data structure.

If you need to reset or create a new config.json, you can:
**Copy the sample config.json located in the repository root (or a subfolder named config)
**Or copy the following example content and save it as config.json in the project root:
```json
{
  "session_data": {
    "commands_run": [],
    "files_generated": [],
    "errors_explained": []
  },
  "languages": {
    ".py": "python",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".js": "javascript"
  },
  "algorithms": {
    "bubble": "bubble_sort",
    "insertion": "insertion_sort",
    "selection": "selection_sort",
    "quick": "quick_sort",
    "merge": "merge_sort",
    "binary": "binary_search",
    "fibonacci": "fibonacci",
    "factorial": "factorial",
    "calculator": "calculator"
  },
  "language_patterns": [
    ["\\b(java)\\s+and\\s+(python)\\b", ["java", "python"]],
    ["\\b(python)\\s+and\\s+(java)\\b", ["python", "java"]]
  ],
  "path_markers": [" at ", " in ", " to ", " directory ", " folder "],
  "polite_words": ["please", "kindly", "could you", "can you"],
  "templates": {
    "java": "public class {class_name} {\n    public static void main(String[] args) {\n        System.out.println(\"{description}\");\n    }\n}",
    "python": "\"\"\"{description}\"\"\"\ndef main():\n    print(\"{description}\")\n\nif __name__ == \"__main__\": main()",
    "c": "#include <stdio.h>\nint main() {\n    printf(\"{description}\\n\");\n    return 0;\n}",
    "cpp": "#include <iostream>\nusing namespace std;\nint main() {\n    cout << \"{description}\" << endl;\n    return 0;\n}"
  }
}
```


#### 5. Run UniShell
```bash
python unishell.py
```

### Verification Commands
Test your installation:
```bash
🚀 UniShell > help
🚀 UniShell > generate hello world using python
🚀 UniShell > run hello_world.py
```

## 📝 Important Notes

### API Key Requirements
- **With API Key**: Full AI-powered natural language understanding and intelligent code generation
- **Without API Key**: Basic template-based code generation with manual parsing (still functional)

### File Path Handling
- Use forward slashes `/` or escaped backslashes `\\` for Windows paths
- UniShell automatically creates directories if they don't exist
- Supports both absolute and relative path specifications

### Compiler Dependencies
- Ensure `javac`, `java`, `gcc`, and `g++` are available in your system PATH
- UniShell will display helpful error messages if compilers are missing

### Session Data
- All session data is automatically saved to `config.json`
- Command history, generated files, and error analyses persist between sessions
- Use `clear` command to reset session data when needed

### Language-Specific Notes
- **Java**: Class names are automatically extracted from generated code
- **C/C++**: Executables are created with platform-appropriate extensions
- **Python**: Runs directly through the Python interpreter

---

**Happy Coding with UniShell!** 🚀