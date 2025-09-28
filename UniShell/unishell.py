import json,os,subprocess,sys,re
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
class UniShell:
    def __init__(self):
        self.config = self.load_config(); self.session = self.config["session_data"].copy()
        self.history = []; self.hf_api_key = os.getenv("HUGGING_FACE_API_KEY", "")
        print("🚀 UniShell AI - Human-Focused Generator\n🤖 Say: 'generate insertion sort using python' or 'create array program using c'\n")
    def load_config(self):
        try:
            with open('config.json', 'r') as f: return json.load(f)
        except FileNotFoundError:
            config = {"session_data": {"commands_run": [], "files_generated": [], "errors_explained": []}, 
                     "languages": {".py": "python", ".java": "java", ".c": "c", ".cpp": "cpp", ".js": "javascript"}}
            with open('config.json', 'w') as f: json.dump(config, f, indent=2); return config
    def save_config(self):
        self.config["session_data"] = self.session 
        with open('config.json', 'w') as f: json.dump(self.config, f, indent=2)
    def ai_understand(self, user_input):
        if not self.hf_api_key: return self.human_parse(user_input)
        try:
            from openai import OpenAI; client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=self.hf_api_key)
            response = client.chat.completions.create(model="deepseek-ai/DeepSeek-V3",
                messages=[{"role": "system", "content": "Extract from human request: action (generate/run/compile/explain), languages array, algorithm name, file if mentioned. Return JSON: {\"action\":\"generate\", \"languages\":[\"python\"], \"algorithm\":\"insertion_sort\"} or {\"action\":\"run\", \"file\":\"test.py\"}"},
                         {"role": "user", "content": user_input}], temperature=0.1, max_tokens=100)
            content = response.choices[0].message.content.strip()
            if '{' in content:
                start, end = content.find('{'), content.rfind('}') + 1
                data = json.loads(content[start:end])
                # Add path extraction to AI response
                data["path"] = self.extract_path_from_input(user_input)
                return data
        except: pass
        return self.human_parse(user_input)

    def extract_path_from_input(self, user_input):
        """Extract path from user input"""
        for marker in [" at ", " in ", " to ", " directory ", " folder ", " path "]:
            if marker in user_input.lower():
                idx = user_input.lower().find(marker) + len(marker)
                path_candidate = user_input[idx:].strip()
                if path_candidate:
                    return os.path.normpath(path_candidate)
        return "."

    def human_parse(self, user_input):
        original_input = user_input.strip()
        user_input = user_input.strip().lower()

        for polite in ["please", "kindly", "could you", "can you", "i want", "i need"]: 
            if user_input.startswith(polite): user_input = user_input[len(polite):].strip()

        # Extract path
        path = self.extract_path_from_input(original_input)

        if any(w in user_input for w in ["generate", "create", "make", "build"]): 
            return {"action": "generate", "raw": user_input, "path": path}
        elif any(w in user_input for w in ["run", "execute"]): 
            return {"action": "run", "raw": user_input, "path": path}
        elif "compile" in user_input: 
            return {"action": "compile", "raw": user_input, "path": path}
        elif "explain" in user_input: 
            return {"action": "explain", "raw": user_input, "path": path}
        elif "help" in user_input: 
            return {"action": "help"}
        elif "clear" in user_input: 
            return {"action": "clear"}
        elif "exit" in user_input or "quit" in user_input: 
            return {"action": "exit"}

        return {"action": "generate", "raw": user_input, "path": path}
    def add_to_history(self, command):
        self.history.append(command)
        if len(self.history) > 10: self.history.pop(0)
        self.session["commands_run"].append(command); self.save_config()
    def get_file_language(self, filepath):
        return self.config["languages"].get(Path(filepath).suffix.lower(), "unknown")
    def show_file_content(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read(); print(f"📄 {os.path.basename(filepath)}\n{'='*50}\n{content}\n{'='*50}"); return content
        except Exception as e: print(f"❌ Cannot read file: {e}"); return None
    def compile_code(self, filepath):
        if not os.path.exists(filepath): print(f"❌ File not found: {filepath}"); return False
        lang = self.get_file_language(filepath); print(f"🔧 Compiling {lang}: {os.path.basename(filepath)}")
        try:
            if lang == "java":
                result = subprocess.run(["javac", filepath], capture_output=True, text=True, cwd=os.path.dirname(filepath) or ".")
                if result.returncode == 0: print("✅ Success"); return True
                else: print(f"❌ Error:\n{result.stderr}"); self.get_ai_help(result.stderr); return False
            elif lang in ["c", "cpp"]:
                compiler = "gcc" if lang == "c" else "g++"; output_file = str(Path(filepath).with_suffix(".exe" if os.name == "nt" else ""))
                result = subprocess.run([compiler, filepath, "-o", output_file], capture_output=True, text=True)
                if result.returncode == 0: print("✅ Success"); return True
                else: print(f"❌ Error:\n{result.stderr}"); self.get_ai_help(result.stderr); return False
            else: print(f"✅ {lang} doesn't need compilation"); return True
        except FileNotFoundError: print("❌ Compiler not found"); return False
    def run_code(self, filepath):
        if not os.path.exists(filepath): print(f"❌ File not found: {filepath}"); return
        print(f"🚀 Running: {os.path.basename(filepath)}")
        lang = self.get_file_language(filepath); dirname = os.path.dirname(filepath) or "."
        try:
            if lang == "java":
                base = os.path.splitext(os.path.basename(filepath))[0]
                if not os.path.exists(os.path.join(dirname, f"{base}.class")): self.compile_code(filepath)
                subprocess.run(["java", "-cp", dirname, base], cwd=dirname)
            elif lang in ["c", "cpp"]:
                exe = os.path.splitext(filepath)[0] + (".exe" if os.name == "nt" else "")
                if not os.path.exists(exe): self.compile_code(filepath)
                subprocess.run([exe] if os.name == "nt" else [f"./{Path(exe).name}"], cwd=dirname)
            elif lang == "python": subprocess.run([sys.executable, filepath], cwd=dirname)
            else: print(f"❌ Not supported: {lang}")
        except Exception as e: print(f"❌ Error: {e}")
    def get_ai_help(self, query):
        if not self.hf_api_key: print("💡 Enable AI for detailed help"); return
        try:
            print(f"🤖 Analyzing the code, please hold on...")
            from openai import OpenAI; client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=self.hf_api_key)
            response = client.chat.completions.create(model="deepseek-ai/DeepSeek-V3",
                messages=[{"role": "system", "content": "Programming expert. Give clear solutions."}, {"role": "user", "content": f"Fix this in max word limit which is 700 and maintain clear explaination: {query}"}], temperature=0.3, max_tokens=700)
            print(f"🤖 Solution: {response.choices[0].message.content.strip()}")
        except Exception as e: print(f"❌ AI error: {e}")
    def smart_filename(self, description):
        if self.hf_api_key:
            try:
                from openai import OpenAI
                client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=self.hf_api_key)
                prompt = f"Suggest a concise and relevant filename (without extension) for a code file based on this description:\n{description}\nOnly provide the filename, no extensions or explanations."
                response = client.chat.completions.create(
                    model="deepseek-ai/DeepSeek-V3",
                    messages=[{"role": "system", "content": "You are an expert assistant for naming files."}, {"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=10,
                )
                filename_suggestion = response.choices[0].message.content.strip()
                # Sanitize filename (remove invalid characters, spaces)
                filename_suggestion = ''.join(c for c in filename_suggestion if c.isalnum() or c in ['_', '-']).replace(' ', '_')
                if filename_suggestion:
                    return filename_suggestion.lower()
            except Exception as e:
                # Log error or ignore and fallback
                pass
        desc = description.lower()
        algorithms = {"insertion": "insertion_sort", "selection": "selection_sort", "bubble": "bubble_sort", "quick": "quick_sort", 
                     "merge": "merge_sort", "heap": "heap_sort", "binary_search": "binary_search", "linear_search": "linear_search",
                     "fibonacci": "fibonacci", "factorial": "factorial", "calculator": "calculator", "matrix": "matrix", 
                     "array": "array_program", "linked_list": "linked_list", "stack": "stack", "queue": "queue",
                     "tree": "tree", "graph": "graph", "palindrome": "palindrome", "prime": "prime_checker", "game": "game"}
        for keyword, filename in algorithms.items():
            if keyword in desc: return filename
        if "program" in desc:
            words = desc.split()
            for i, word in enumerate(words):
                if word == "program" and i > 0: return f"{words[i-1]}_program"
        return "program"
    def detect_languages(self, description):
        desc = description.lower()
        patterns = [(r'\b(java)\s+and\s+(python)\b', ['java', 'python']), (r'\b(python)\s+and\s+(java)\b', ['python', 'java']),
                   (r'\b(c)\s+and\s+(python)\b', ['c', 'python']), (r'\b(java)\s*,\s*(python)\b', ['java', 'python'])]
        for pattern, langs in patterns:
            if re.search(pattern, desc): return langs
        if re.search(r'\busing\s+(java|python|c\+\+|c|javascript)\b', desc):
            match = re.search(r'\busing\s+(java|python|c\+\+|c|javascript)\b', desc)
            lang = match.group(1); return ['cpp' if lang == 'c++' else lang]
        if 'java' in desc and 'javascript' not in desc: return ['java']
        if 'python' in desc: return ['python']
        if 'c++' in desc or 'cpp' in desc: return ['cpp']
        if ' c ' in desc or desc.endswith(' c'): return ['c']
        return ['python']
    def clean_code(self, code):
        lines = code.split('\n'); cleaned = []
        for line in lines:
            stripped = line.strip()
            if not any(marker in stripped for marker in ['```', '~~~', '---', 'java', 'python', 'cpp'] if stripped.startswith(marker)): cleaned.append(line)
        result = '\n'.join(cleaned).strip()
        while '\n\n\n' in result: result = result.replace('\n\n\n', '\n\n')
        return result
    def generate_code(self, filepath, language, description):
        print(f"🔍 DEBUG: Generating file at: {filepath}")  # Debug line
        if os.path.dirname(filepath): os.makedirs(os.path.dirname(filepath), exist_ok=True)
        if os.path.exists(filepath): print(f"❌ Exists: {os.path.basename(filepath)}"); return
        print(f"🤖 Creating {language}: {os.path.basename(filepath)}")
        if self.hf_api_key:
            try:
                from openai import OpenAI; client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=self.hf_api_key)
                prompt = f"Create complete {language} program for: {description}. Include imports, main function, comments. Return ONLY {language} code, no markdown."
                response = client.chat.completions.create(model="deepseek-ai/DeepSeek-V3",
                    messages=[{"role": "system", "content": f"Expert {language} programmer. Write clean code without formatting. "}, {"role": "user", "content": "If the language is java use good structure and make main class as public. For other languages maintain good structure" + prompt}], temperature=0.2, max_tokens=800)
                code = self.clean_code(response.choices[0].message.content.strip())
                if language == "java":
                    match = re.search(r'public\s+class\s+(\w+)', code)
                    if match:
                        class_name = match.group(1); new_filepath = os.path.join(os.path.dirname(filepath), f"{class_name}.java")
                        if new_filepath != filepath: filepath = new_filepath; print(f"📁 Using: {class_name}.java")
                with open(filepath, 'w', encoding='utf-8') as f: f.write(code)
                print(f"✅ Generated: {filepath}"); self.session["files_generated"].append(filepath); self.save_config()
                self.show_file_content(filepath)
            except Exception as e: print(f"❌ Error: {e}"); self.create_template(filepath, language, description)
        else: self.create_template(filepath, language, description)
    def create_template(self, filepath, language, description):
        templates = {"java": f'public class {Path(filepath).stem.title()} {{\n    public static void main(String[] args) {{\n        System.out.println("{description}");\n    }}\n}}',
                    "python": f'"""\n{description}\n"""\ndef main():\n    print("{description}")\n\nif __name__ == "__main__": main()',
                    "c": f'#include <stdio.h>\nint main() {{\n    printf("{description}\\n");\n    return 0;\n}}',
                    "cpp": f'#include <iostream>\nusing namespace std;\nint main() {{\n    cout << "{description}" << endl;\n    return 0;\n}}'}
        code = templates.get(language, templates["python"])
        with open(filepath, 'w', encoding='utf-8') as f: f.write(code)
        print(f"✅ Template: {filepath}"); self.session["files_generated"].append(filepath); self.save_config()
    def extract_filename(self, text):
        words = text.split()
        for word in words:
            if "." in word and any(word.endswith(ext) for ext in [".py", ".java", ".c", ".cpp", ".js"]): return word
        return None
    def show_help(self):
        print("🚀 UniShell AI - Human Commands:")
        print("  🗣️  'generate insertion sort using python' → insertion_sort.py")
        print("  🗣️  'create array program using c' → array_program.c")
        print("  🗣️  'make calculator using java and python' → 2 files") 
        print("  🗣️  'please run test.py' → executes file")
        print("  📋 Direct: run/compile/explain <file>")
        print("  ⚙️  System: help/clear/exit")
        print("🤖 Just speak naturally - AI understands!")
    def show_history(self):
        print("📚 Recent:"); [print(f"  {i}. {cmd}") for i, cmd in enumerate(self.history[-5:], 1)] if self.history else print("  None")
    def clear_session(self):
        self.session = {"commands_run": [], "files_generated": [], "errors_explained": []}; self.history = []; self.save_config(); print("🧹 Cleared")
    def exit_summary(self):
        print(f"\n📊 Session: {len(self.session['commands_run'])} commands, {len(self.session['files_generated'])} files")
        if self.session["files_generated"]: print(f"Files: {', '.join([os.path.basename(f) for f in self.session['files_generated'][-3:]])}")
        self.save_config(); print("🚀 Thanks for using UniShell AI!")
    def run(self):
        while True:
            try:
                user_input = input("🚀 UniShell AI> ").strip()
                if not user_input: continue
                self.add_to_history(user_input); data = self.ai_understand(user_input); action = data.get("action", "help")

                # DEBUG: Print what was extracted
                print(f"🔍 DEBUG: Action={action}, Path={data.get('path', 'NOT_FOUND')}")

                if action == "exit": self.exit_summary(); break
                elif action == "help": self.show_help()
                elif action == "clear": self.clear_session()
                elif action == "run":
                    if "file" in data: self.run_code(data["file"])
                    elif "raw" in data:
                        filename = self.extract_filename(data["raw"])
                        if filename: self.run_code(filename)
                        else: print("❌ Specify file to run")
                elif action == "compile":
                    if "file" in data: self.compile_code(data["file"])
                    elif "raw" in data:
                        filename = self.extract_filename(data["raw"])
                        if filename: self.compile_code(filename)
                        else: print("❌ Specify file to compile")
                elif action == "explain":
                    if "file" in data: 
                        if os.path.exists(data["file"]): content = self.show_file_content(data["file"]); self.get_ai_help(f"Explain: {content}")
                        else: print(f"❌ File not found: {data['file']}")
                    elif "raw" in data: self.get_ai_help(data["raw"])
                elif action == "generate":
                    if "languages" in data and "algorithm" in data:
                        languages, algorithm = data["languages"], data["algorithm"]
                        base_path = data.get("path", ".")
                        print(f"🔍 DEBUG: Using base_path={base_path}")  # Debug line
                        lang_map = {"python": ".py", "java": ".java", "c": ".c", "cpp": ".cpp", "javascript": ".js"}
                        for lang in languages:
                            ext = lang_map.get(lang, ".py")
                            filepath = os.path.join(base_path, f"{algorithm}{ext}")
                            self.generate_code(filepath, lang, f"{algorithm} implementation")
                    elif "raw" in data:
                        raw = data["raw"]
                        base_path = data.get("path", ".")
                        print(f"🔍 DEBUG: Raw path={base_path}")  # Debug line
                        filename_base = self.smart_filename(raw)
                        languages = self.detect_languages(raw)
                        lang_map = {"python": ".py", "java": ".java", "c": ".c", "cpp": ".cpp", "javascript": ".js"}
                        if len(languages) > 1:
                            for lang in languages:
                                ext = lang_map.get(lang, ".py")
                                filepath = os.path.join(base_path, f"{filename_base}{ext}")
                                self.generate_code(filepath, lang, raw)
                        else:
                            lang = languages[0]
                            ext = lang_map.get(lang, ".py")
                            filepath = os.path.join(base_path, f"{filename_base}{ext}")
                            self.generate_code(filepath, lang, raw)
                    else: 
                        print("❌ Try: 'generate insertion sort using python'")
                else: print("🤔 Try 'help' for examples")
            except KeyboardInterrupt: print("\n👋 Goodbye!"); break
            except Exception as e: print(f"❌ Error: {e}")
if __name__ == "__main__": UniShell().run()
