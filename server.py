# کد جدید و کامل برای server.py
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import os
import traceback # این خط برای ثبت خطای دقیق‌تر اضافه شده

# ---- پیکربندی اولیه ----
app = Flask(__name__, static_folder='static')

# ---- پیکربندی مدل هوش مصنوعی ----
model = None
try:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("خطا: متغیر محیطی GOOGLE_API_KEY پیدا نشد.")
    else:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        print("مدل Gemini با موفقیت پیکربندی شد.")
except Exception as e:
    print(f"خطا در هنگام پیکربندی Gemini: {e}")


# ---- پلی‌بوک محتوا (بدون تغییر) ----
CONTENT_PLAYBOOK = """
Playbook تولید محتوا
... (تمام متن پلی‌بوک شما اینجا قرار دارد) ...
"""

# ---- روت‌های برنامه ----

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-concerns', methods=['POST'])
def generate_concerns():
    print("\n--- درخواست جدید برای /generate-concerns دریافت شد ---")
    if not model:
        print("خطای داخلی: مدل هوش مصنوعی در دسترس نیست.")
        return jsonify({'error': 'مدل هوش مصنوعی به درستی پیکربندی نشده است.'}), 500
    try:
        brand_info = request.json
        print("اطلاعات برند از درخواست استخراج شد.")
        
        prompt = f"""
        شما یک استراتژیست ارشد برند هستید. بر اساس بریف استراتژی زیر، ۵ دغدغه اصلی مخاطبان را لیست کنید.
        بریف: {brand_info}
        """
        
        print("در حال ارسال درخواست به API گوگل...")
        response = model.generate_content(prompt)
        print("پاسخ از API گوگل دریافت شد.")
        
        # بررسی اینکه آیا پاسخ به دلیل فیلتر ایمنی مسدود شده است یا خیر
        if not response.parts:
            block_reason = response.prompt_feedback.block_reason
            print(f"درخواست توسط فیلتر ایمنی گوگل مسدود شد. دلیل: {block_reason}")
            error_msg = f"محتوای ارسالی شما توسط فیلتر ایمنی گوگل مسدود شد. دلیل: {block_reason}"
            return jsonify({'error': error_msg}), 400

        return jsonify({'concerns': response.text})
        
    except Exception as e:
        print("!!! یک خطای پیش‌بینی نشده در /generate-concerns رخ داد !!!")
        # ثبت کامل خطا در لاگ
        traceback.print_exc()
        return jsonify({'error': f'خطای داخلی سرور: {str(e)}'}), 500

@app.route('/generate-scenario', methods=['POST'])
def generate_scenario():
    print("\n--- درخواست جدید برای /generate-scenario دریافت شد ---")
    if not model:
        print("خطای داخلی: مدل هوش مصنوعی در دسترس نیست.")
        return jsonify({'error': 'مدل هوش مصنوعی به درستی پیکربندی نشده است.'}), 500
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
        
        print("در حال ارسال درخواست سناریو به API گوگل...")
        response = model.generate_content(prompt)
        print("پاسخ سناریو از API گوگل دریافت شد.")

        if not response.parts:
            block_reason = response.prompt_feedback.block_reason
            print(f"درخواست توسط فیلتر ایمنی گوگل مسدود شد. دلیل: {block_reason}")
            error_msg = f"محتوای ارسالی شما توسط فیلتر ایمنی گوگل مسدود شد. دلیل: {block_reason}"
            return jsonify({'error': error_msg}), 400

        return jsonify({'scenario': response.text})

    except Exception as e:
        print("!!! یک خطای پیش‌بینی نشده در /generate-scenario رخ داد !!!")
        traceback.print_exc()
        return jsonify({'error': f'خطای داخلی سرور: {str(e)}'}), 500

# برای اجرای سرور
if __name__ == '__main__':
    app.run(debug=True)
