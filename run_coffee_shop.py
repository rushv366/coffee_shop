import os
import sys
import webbrowser
import threading

print("="*60)
print("COFFEE SHOP - QUICK START")
print("="*60)

# Check if app.py exists
if not os.path.exists('app.py'):
    print("Creating app.py...")
    # You need to copy the app.py content above
    print("Please copy the app.py content from above")
    sys.exit(1)

# Create templates directory
os.makedirs('templates', exist_ok=True)

# Check essential templates
essential_templates = ['index.html', 'login.html']
for template in essential_templates:
    if not os.path.exists(f'templates/{template}'):
        print(f"✗ Missing: templates/{template}")
        print("Please create the template files above")
        sys.exit(1)

print("\n✓ All files ready!")
print("\nStarting Coffee Shop Application...")
print("Opening browser in 3 seconds...")

# Open browser after delay
def open_browser():
    import time
    time.sleep(3)
    webbrowser.open('http://localhost:5000')

# Start browser thread
threading.Thread(target=open_browser, daemon=True).start()

# Run the app
os.system('python app.py')