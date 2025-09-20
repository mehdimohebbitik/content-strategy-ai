from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import os
import traceback

# ---- پیکربندی اولیه ----
app = Flask(__name__, static_folder='static')

# ---- پیکربندی مدل هوش مصنوعی (روش ساده با API Key) ----
model = None
try:
    # کلید API از متغیرهای محیطی خوانده می‌شود
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("خطا: متغیر محیطی GOOGLE_API_KEY پیدا نشد.")
    else:
        genai.configure(api_key=api_key)
        # از مدل پایدار و در دسترس gemini-1.0-pro استفاده می‌کنیم
        model = genai.GenerativeModel("gemini-1.0-pro")
        print("مدل Gemini (با API Key) با موفقیت پیکربندی شد.")
except Exception as e:
    print(f"!!! خطا در هنگام پیکربندی Gemini: {e} !!!")
    traceback.print_exc()

# ---- پلی‌بوک محتوا (بدون تغییر) ----
CONTENT_PLAYBOOK = """
Playbook تولید محتوا
... (تمام متن پلی‌بوک شما اینجا قرار دارد) ...
"""

# ---- روت‌های برنامه (بدون تغییر) ----
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-concerns', methods=['POST'])
def generate_concerns():
    # ... (این بخش بدون تغییر باقی می‌ماند) ...
    if not model: return jsonify({'error': 'مدل پیکربندی نشده است.'}), 500
    try:
        brand_info = request.json
        prompt = f"شما یک استراتژیست برند هستید. بر اساس بریف زیر، ۵ دغدغه اصلی مخاطبان را لیست کنید.\nبریف: {brand_info}"
        response = model.generate_content(prompt)
        return jsonify({'concerns': response.text})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'خطای داخلی سرور: {str(e)}'}), 500

@app.route('/generate-scenario', methods=['POST'])
def generate_scenario():
    # ... (این بخش بدون تغییر باقی می‌ماند) ...
    if not model: return jsonify({'error': 'مدل پیکربندی نشده است.'}), 500
    try:
        data = request.json
        brand_info = data['brandInfo']
        concerns = data['concerns']
        prompt = f"""
        شما یک کارگردان خلاق هستید. بر اساس اطلاعات زیر و با استفاده از پلی‌بوک، یک سناریو بنویسید.
        بریف: {brand_info}
        دغدغه‌ها: {concerns}
        پلی‌بوک: {CONTENT_PLAYBOOK}
        """
        response = model.generate_content(prompt)
        return jsonify({'scenario': response.text})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'خطای داخلی سرور: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
