
import os
import re

TARGET_DIR = r"c:\Users\thesh\Downloads\BTL12-main\src\font-end\gui"

# Regex to find tk.Frame(..., pady=(10, 15)) or similar in constructors
# We want to catch instances where a tuple is passed to pady or padx in a widget constructor.
# Pattern: tk.Frame(...) or tk.Label(...) etc.
constructor_pattern = re.compile(r'(tk\.(?:Frame|Label|Canvas|Button|Entry|Checkbutton|Radiobutton|Listbox|Message|Scale|Scrollbar|Spinbox|Text))\s*\((.*?)\)', re.DOTALL)
padding_tuple_pattern = re.compile(r'(padx|pady)\s*=\s*\(([^)]+)\)')

for root, dirs, files in os.walk(TARGET_DIR):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            new_content = content
            # Find all widget constructors
            for match in constructor_pattern.finditer(content):
                constructor_call = match.group(0)
                widget_type = match.group(1)
                args = match.group(2)
                
                # Check if args contain a tuple padding
                if padding_tuple_pattern.search(args):
                    print(f"Found problematic padding in {file}: {constructor_call[:50]}...")
                    
                    # Fix: Change pady=(a, b) to pady=a (take the first value as the internal padding)
                    # And then we would ideally add a .pack(pady=(a, b)) but that's hard to automate perfectly.
                    # For now, just changing the tuple to a single value will prevent the crash.
                    
                    def fix_padding(m):
                        key = m.group(1)
                        vals = m.group(2).split(",")
                        first_val = vals[0].strip()
                        return f"{key}={first_val}"
                    
                    fixed_args = padding_tuple_pattern.sub(fix_padding, args)
                    fixed_call = f"{widget_type}({fixed_args})"
                    new_content = new_content.replace(constructor_call, fixed_call)
            
            if new_content != content:
                print(f"Updating {path}...")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)

print("Fix completed.")
