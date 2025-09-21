from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, jsonify
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for flash messages

# Configurations
SHARED_NETWORK_FOLDER = '\\DIGICODER\\serverFiles'  # Replace with your shared network path
LOG_FILE = os.path.join(SHARED_NETWORK_FOLDER, '\\DIGICODER\\serverFiles\\server_log.txt')
MAX_FILE_SIZE_MB = 5
MAX_FILES = 20

# Ensure shared network folder exists
os.makedirs(SHARED_NETWORK_FOLDER, exist_ok=True)
if not os.path.exists(LOG_FILE):  # Create the log file if it doesn't exist
    with open(LOG_FILE, 'w') as f:
        f.write("Shared Text Will Appear Here\n\n")

app.config['UPLOAD_FOLDER'] = SHARED_NETWORK_FOLDER


def log_text(message):
    """Log text messages to the shared text file."""
    with open(LOG_FILE, 'a') as f:
        f.write(f"{message}\n")


@app.route('/')
def home():
    files = [file for file in os.listdir(app.config['UPLOAD_FOLDER']) if file != 'server_log.txt']
    with open(LOG_FILE, 'r') as f:
        logs = f.readlines()
    file_path = '\\DIGICODER\\serverFiles\\server_log.txt'
    try:
        # Read the content of the text file
        with open(file_path, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        content = "File not found!"  # Default content if file does not exist
    
    return render_template('index.html', content=content ,files=files, logs=logs)
    


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or request.files['file'].filename == '':
        flash('No file selected!', 'danger')
        return redirect(url_for('home'))

    file = request.files['file']
    file_size = len(file.read()) / (1024 * 1024)  # Convert to MB
    file.seek(0)  # Reset file pointer for saving

    if file_size > MAX_FILE_SIZE_MB:
        flash(f'File size exceeds {MAX_FILE_SIZE_MB} MB!', 'danger')
        return redirect(url_for('home'))

    files = os.listdir(app.config['UPLOAD_FOLDER'])
    if len(files) >= MAX_FILES:
        flash(f'Maximum file limit of {MAX_FILES} reached!', 'danger')
        return redirect(url_for('home'))

    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    flash('File uploaded successfully!', 'success')
    return redirect(url_for('home'))


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/delete/<filename>')
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash('File deleted successfully!', 'success')
    return redirect(url_for('home'))



@app.route('/delete_text', methods=['POST'])
def delete_text():
    text_file = '\\DIGICODER\\serverFiles\\server_log.txt'  # Path to your text file
    try:
        with open(text_file, 'w') as file:
            file.write("Shared Text Will Appear Here")  # Clear the contents of the file
        return jsonify({"success": True, "message": "All text deleted successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}"})

def delete_specific_text(file_path, text_to_delete):
    # Read the content of the file
    with open(file_path, 'r') as file:
        content = file.read()

    # Remove the specific text
    content = content.replace(text_to_delete, '')

    # Write the modified content back to the file
    with open(file_path, 'w') as file:
        file.write(content)

# Usage

@app.route('/add_text', methods=['POST'])
def add_text():
    text = request.form.get('text', '').strip()
    if not text:
        flash('Text cannot be empty!', 'danger')
    else:
        delete_specific_text('\\DIGICODER\\serverFiles\\server_log.txt', 'Shared Text Will Appear Here')
        log_text(text)
        flash('Text added successfully!', 'success')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')  # Accessible on the network
