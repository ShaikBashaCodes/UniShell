import json,os,subprocess,sys,re
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

class UniShell:
    
    # Initialize UniShell with configuration and session data
    def __init__(self):
        self.config = self.load_config(); self.session = self.config["session_data"].copy()
        self.history = []; self.hf_api_key = os.getenv("HUGGING_FACE_API_KEY", "")
        print("🚀 UniShell - Advanced Human-Focused Generator")
        print("🤖 Natural Commands: 'generate bubble sort using java in C:\\path' \n💡 Type 'help' for complete guide or 'cls' to clear screen\n")
    
    # Centralized AI method for all OpenAI API calls
    def AI(self, sys_prompt, user_prompt, temperature=0.2, max_tokens=800):
        if not self.hf_api_key: return None
        try:
            from openai import OpenAI 
            client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=self.hf_api_key)
            response = client.chat.completions.create(model="deepseek-ai/DeepSeek-V3",
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}], 
                temperature=temperature, max_tokens=max_tokens)
            return response.choices[0].message.content.strip()
        except: return None
    
    # Load configuration from JSON file with error handling
    def load_config(self):
        try: return json.load(open('config.json','r',encoding='utf-8'))
        except: print("❌ Config File error."); sys.exit(1)
    
    # Save current session data back to config file
    def save_config(self):
        self.config["session_data"] = self.session
        with open('config.json', 'w') as f: json.dump(self.config, f, indent=2)
    
    # Use AI to understand user input and extract structured data
    def ai_understand(self, user_input):
        if not self.hf_api_key: return self.human_parse(user_input)
        sys_prompt = "Extract from human request: action (generate/run/compile/explain), languages array, algorithm name, file if mentioned. Return JSON: {\"action\":\"generate\", \"languages\":[\"python\"], \"algorithm\":\"insertion_sort\"} or {\"action\":\"run\", \"file\":\"test.py\"}"
        content = self.AI(sys_prompt, user_input, 0.1, 100)
        if content and '{' in content:
            try:
                data = json.loads(content[(content.find('{')):(content.rfind('}') + 1)])
                data["path"] = self.extract_path_from_input(user_input)
                return data
            except: pass
        return self.human_parse(user_input)
    
    # Extract file path from user input using path markers
    def extract_path_from_input(self, user_input):
        for marker in self.config["path_markers"]:
            if marker in user_input.lower():
                idx = user_input.lower().find(marker) + len(marker)
                path_candidate = user_input[idx:].strip()
                if path_candidate: return os.path.normpath(path_candidate)
        return "."
    
    # Manual parsing fallback when AI is not available
    def human_parse(self, user_input):
        original_input = user_input.strip(); user_input = user_input.strip().lower()
        for polite in self.config["polite_words"]: 
            if user_input.startswith(polite): user_input = user_input[len(polite):].strip()
        path = self.extract_path_from_input(original_input)
        if any(w in user_input for w in ["generate", "create", "make", "build"]): 
            return {"action": "generate", "raw": user_input, "path": path}
        elif any(w in user_input for w in ["run", "execute"]): 
            return {"action": "run", "raw": user_input, "path": path}
        elif "compile" in user_input: return {"action": "compile", "raw": user_input, "path": path}
        elif "explain" in user_input: return {"action": "explain", "raw": user_input, "path": path}
        elif "help" in user_input: return {"action": "help"}
        elif user_input in ["clear", "reset"]: return {"action": "clear"}
        elif user_input in ["cls", "clr"]: return {"action": "cls"}
        elif "exit" in user_input or "quit" in user_input: return {"action": "exit"}
        return {"action": "generate", "raw": user_input, "path": path}
    
    # Add command to history and maintain session data
    def add_to_history(self, command):
        self.history.append(command)
        if len(self.history) > 10: self.history.pop(0)
        self.session["commands_run"].append(command); self.save_config()
    
    # Detect programming language from file extension
    def get_file_language(self, filepath): return self.config["languages"].get(Path(filepath).suffix.lower(), "unknown")
    
    # Display file contents with formatted output
    def show_file_content(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read(); print(f"📄 {os.path.basename(filepath)}\n{'='*50}\n{content}\n{'='*50}"); return content
        except Exception as e: print(f"❌ Cannot read file: {e}"); return None
    
    # Compile source code files based on language type
    def compile_code(self, filepath):
        if not os.path.exists(filepath): print(f"❌ File not found: {filepath}"); return False
        lang = self.get_file_language(filepath); print(f"🔧 Compiling {lang}: {os.path.basename(filepath)}")
        try:
            if lang == "java":
                result = subprocess.run(["javac", filepath], capture_output=True, text=True, cwd=os.path.dirname(filepath) or ".")
                if result.returncode == 0: print("✅ Compilation successful"); return True
                else: print(f"❌ Compilation failed:\n{result.stderr}"); self.get_ai_help(result.stderr); return False
            elif lang in ["c", "cpp"]:
                compiler = "gcc" if lang == "c" else "g++"; output_file = str(Path(filepath).with_suffix(".exe" if os.name == "nt" else ""))
                result = subprocess.run([compiler, filepath, "-o", output_file], capture_output=True, text=True)
                if result.returncode == 0: print("✅ Compilation successful"); return True
                else: print(f"❌ Compilation failed:\n{result.stderr}"); self.get_ai_help(result.stderr); return False
            else: print(f"✅ {lang} doesn\'t need compilation"); return True
        except FileNotFoundError: print("❌ Compiler not found"); return False
    
    # Execute compiled or interpreted code files
    def run_code(self, filepath):
        if not os.path.exists(filepath): print(f"❌ File not found: {filepath}"); return
        print(f"🚀 Running: {os.path.basename(filepath)}")
        lang = self.get_file_language(filepath); dirname = os.path.dirname(filepath) or "."
        try:
            if lang == "java":
                base = os.path.splitext(os.path.basename(filepath))[0]
                if not os.path.exists(os.path.join(dirname, f"{base}.class")): self.compile_code(filepath)
                subprocess.run(["java", "-cp", dirname, base], cwd=dirname); print()
            elif lang in ["c", "cpp"]:
                exe = os.path.splitext(filepath)[0] + (".exe" if os.name == "nt" else "")
                if not os.path.exists(exe): self.compile_code(filepath)
                subprocess.run([exe] if os.name == "nt" else [f"./{Path(exe).name}"], cwd=dirname); print()
            elif lang == "python": subprocess.run([sys.executable, filepath], cwd=dirname); print()
            else: print(f"❌ Language {lang} not supported")
        except Exception as e: print(f"❌ Execution error: {e}")
    
    # Get AI assistance for error analysis and solutions
    def get_ai_help(self, query):
        if not self.hf_api_key: print("💡 Set HUGGING_FACE_API_KEY environment variable for AI assistance"); return
        print("🤖 AI Analyzing.., please wait...")
        sys_prompt = "Programming expert. Provide clear, actionable solutions with examples. Keep response under 700 words."
        result = self.AI(sys_prompt, f"Fix this programming error or explanation and keep response under 650 words with completed solution: {query}", 0.2, 700)
        if result: print(f"🤖 AI Solution:\n{result}")
        else: print("❌ AI analysis failed")
        self.session["errors_explained"].append(query[:100]); self.save_config()
    
    # Generate smart filenames using AI or algorithm mapping
    def smart_filename(self, description):
        if self.hf_api_key:
            sys_prompt = "Expert filename generator. Suggest concise, relevant filename without extension."
            result = self.AI(sys_prompt, f"Suitable Filename for: {description} which is short but defines the code in that file.", 0.2, 10)
            if result:
                filename = ''.join(c for c in result if c.isalnum() or c in ['_', '-']).replace(' ', '_').strip()
                if filename: return filename.lower()
        desc = description.lower()
        for keyword, filename in self.config["algorithms"].items():
            if keyword in desc: return filename
        if "program" in desc:
            words = desc.split()
            for i, word in enumerate(words):
                if word == "program" and i > 0: return f"{words[i-1]}_program"
        return "program"
    
    # Detect programming languages from user description
    def detect_languages(self, description):
        desc = description.lower()
        for pattern, langs in self.config["language_patterns"]:
            if re.search(pattern, desc): return langs
        if re.search(r'\busing\s+(java|python|c\+\+|c|javascript)\b', desc):
            match = re.search(r'\busing\s+(java|python|c\+\+|c|javascript)\b', desc)
            lang = match.group(1); return ['cpp' if lang == 'c++' else lang]
        if 'java' in desc and 'javascript' not in desc: return ['java']
        if 'python' in desc: return ['python']
        if 'c++' in desc or 'cpp' in desc: return ['cpp']
        if ' c ' in desc or desc.endswith(' c'): return ['c']
        return ['python']
    
    # Clean AI-generated code by removing markdown formatting
    def clean_code(self, code):
        if not code: return ""
        lines = code.split('\n'); cleaned = []
        for line in lines:
            stripped = line.strip()
            if not any(marker in stripped for marker in ['```', '~~~', '---'] if stripped.startswith(marker)): 
                cleaned.append(line)
        result = '\n'.join(cleaned).strip()
        while '\n\n\n' in result: result = result.replace('\n\n\n', '\n\n')
        return result
    
    # Generate complete source code files using AI
    def generate_code(self, filepath, language, description):
        if os.path.dirname(filepath): os.makedirs(os.path.dirname(filepath), exist_ok=True)
        if os.path.exists(filepath): print(f"❌ File exists: {os.path.basename(filepath)}"); return
        print(f"🤖 Creating {language}: {os.path.basename(filepath)} → {os.path.dirname(filepath) or 'current directory'}")
        if self.hf_api_key:
            sys_prompt = f"Expert {language} programmer. Write clean, production-ready code without markdown formatting."
            user_prompt = f"Create complete {language} program for: {description}. Include imports, main function, and helpful comments. Return ONLY {language} code. With user inputs and proper error handling in the code."
            if language == "java": user_prompt += " Use public class with proper structure."
            code = self.AI(sys_prompt, user_prompt, 0.15, 800)
            if code:
                code = self.clean_code(code)
                if language == "java":
                    match = re.search(r'public\s+class\s+(\w+)', code)
                    if match:
                        class_name = match.group(1)
                        new_filepath = os.path.join(os.path.dirname(filepath), f"{class_name}.java")
                        if new_filepath != filepath: filepath = new_filepath; print(f"📁 Using class name: {class_name}.java")
                with open(filepath, 'w', encoding='utf-8') as f: f.write(code)
                print(f"✅ Generated: {os.path.basename(filepath)}"); self.session["files_generated"].append(filepath); self.save_config()
                self.show_file_content(filepath); return
        self.create_template(filepath, language, description)
    
    # Create basic code templates when AI is not available
    def create_template(self, filepath, language, description):
        class_name = Path(filepath).stem.replace('_', '').title()
        template = self.config["templates"].get(language, self.config["templates"]["python"])
        code = template.format(class_name=class_name, description=description)
        with open(filepath, 'w', encoding='utf-8') as f: f.write(code)
        print(f"✅ Template created: {os.path.basename(filepath)}"); self.session["files_generated"].append(filepath); self.save_config()
    
    # Extract filename with extension from user input text
    def extract_filename(self, text):
        for word in text.split():
            if "." in word and any(word.endswith(ext) for ext in [".py", ".java", ".c", ".cpp", ".js"]): return word
        return None
    
    # Display help guide from config or fallback text
    def show_help(self):
        try:
            help_data = self.config.get("help_commands", {})
            print("🚀 UniShell - Command Guide\n" + "="*40)
            for section, items in help_data.items():
                print(f"\n{section.replace('_', ' ').title()}:\n")
                for cmd in items:
                    print(f"  {cmd}")
            print("="*40)
        except Exception:
            print("Commands:\n generate <alg> using <lang> | run/compile/explain <file>\n clear/reset | cls/clr | help | exit")
    
    # Show session summary with statistics on exit
    def exit_summary(self):
        print("\n" + "=" * 50)
        print("📊 SESSION SUMMARY")
        print("=" * 50)
        print(f"🔢 Commands executed: {len(self.session['commands_run'])}")
        print(f"📁 Files generated: {len(self.session['files_generated'])}")
        print(f"🔍 Errors analyzed: {len(self.session['errors_explained'])}")
        if self.session["files_generated"]: 
            print(f"📂 Recent files: {', '.join([os.path.basename(f) for f in self.session['files_generated'][-3:]])}")
        print("=" * 50)
        self.save_config(); print("🚀 Thank you for using UniShell! Session saved.")
    
    # Main application loop handling user commands
    def run(self):
        while True:
            try:
                user_input = input("🚀 UniShell > ").strip()
                if not user_input: continue
                self.add_to_history(user_input); data = self.ai_understand(user_input); action = data.get("action", "help")
                if action == "exit": self.exit_summary(); break
                elif action == "help": self.show_help()
                elif action == "clear":
                    self.session = {"commands_run": [], "files_generated": [], "errors_explained": []}
                    self.history = []; self.save_config(); print("🧹 Session data cleared successfully")    
                elif action == "cls": os.system('cls' if os.name == 'nt' else 'clear')
                elif action in ("run", "compile", "explain"):
                    cmd = action
                    target = data.get("file") or self.extract_filename(data.get("raw", "")) or None
                    if not target:
                        print(f"❌ Please specify a file to {cmd}")
                        continue
                    if not os.path.isabs(target):
                        target = os.path.normpath(os.path.join(data.get("path","."), target))
                    if cmd == "run":
                        self.run_code(target)
                    elif cmd == "compile":
                        self.compile_code(target)
                    else: 
                        if os.path.exists(target):
                            content = self.show_file_content(target)
                            self.get_ai_help(f"Explain this code: {content}")
                        else:
                            print(f"❌ File not found: {target}")
                elif action == "generate":
                    if "languages" in data and "algorithm" in data:
                        languages, algorithm = data["languages"], data["algorithm"]
                        base_path = data.get("path", "."); lang_map = self.config["languages"]
                        for lang in languages:
                            ext = {v: k for k, v in lang_map.items()}.get(lang, ".py")
                            filepath = os.path.join(base_path, f"{algorithm}{ext}")
                            self.generate_code(filepath, lang, f"{algorithm} implementation")
                    elif "raw" in data:
                        raw, base_path = data["raw"], data.get("path", ".")
                        filename_base, languages = self.smart_filename(raw), self.detect_languages(raw)
                        lang_map = self.config["languages"]
                        for lang in languages:
                            ext = {v: k for k, v in lang_map.items()}.get(lang, ".py")
                            filepath = os.path.join(base_path, f"{filename_base}{ext}")
                            self.generate_code(filepath, lang, raw)
                    else: print("❌ Try: \'generate bubble sort using python\'")
                else: print("🤔 Type \'help\' for available commands")
            except KeyboardInterrupt: print("\n👋 Goodbye! Use \'exit\' for session summary."); break
            except Exception as e: print(f"❌ Unexpected error: {e}")

# Entry point of the script: create a UniShell instance and start the interactive run loop
if __name__ == "__main__": UniShell().run()