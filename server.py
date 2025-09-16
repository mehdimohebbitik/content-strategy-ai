from flask import Flask, request, jsonify, render_template
import os
import traceback
import vertexai
from vertexai.generative_models import GenerativeModel

# ---- پیکربندی اولیه ----
app = Flask(__name__, static_folder='static')

# ---- پیکربندی Vertex AI ----
model = None
try:
    # این متغیرها باید در محیط Render تنظیم شوند
    project_id = os.environ.get("GOOGLE_PROJECT_ID")
    location = os.environ.get("GOOGLE_REGION", "us-central1") # یک منطقه پیش‌فرض

    if not project_id:
        print("خطا: متغیر محیطی GOOGLE_PROJECT_ID پیدا نشد.")
    else:
        # فایل کلید به صورت خودکار توسط Render خوانده می‌شود
        # نیازی به مشخص کردن مسیر فایل نیست
        vertexai.init(project=project_id, location=location)
        # از مدل جدیدتر و قدرتمندتر Gemini 1.5 Flash استفاده می‌کنیم
        model = GenerativeModel("gemini-1.5-flash-001") 
        print(f"Vertex AI با موفقیت برای پروژه '{project_id}' پیکربندی شد.")

except Exception as e:
    print(f"!!! خطا در هنگام پیکربندی Vertex AI: {e} !!!")
    traceback.print_exc()


# ---- پلی‌بوک محتوا (بدون تغییر) ----
# ... (محتوای کامل پلی‌بوک شما باید اینجا باشد) ...
CONTENT_PLAYBOOK = """
Playbook تولید محتوا
...
"""

# ---- روت‌های برنامه ----

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-concerns', methods=['POST'])
def generate_concerns():
    print("\n--- درخواست جدید (Vertex AI) برای /generate-concerns دریافت شد ---")
    if not model:
        return jsonify({'error': 'مدل Vertex AI به درستی پیکربندی نشده است.'}), 500
    try:
        brand_info = request.json
        prompt = f"شما یک استراتژیست برند هستید. بر اساس بریف زیر، ۵ دغدغه اصلی مخاطبان را لیست کنید.\nبریف: {brand_info}"
        
        print("در حال ارسال درخواست به Vertex AI...")
        response = model.generate_content(prompt)
        print("پاسخ از Vertex AI دریافت شد.")
        
        return jsonify({'concerns': response.text})
        
    except Exception as e:
        print("!!! یک خطای پیش‌بینی نشده در /generate-concerns رخ داد !!!")
        traceback.print_exc()
        return jsonify({'error': f'خطای داخلی سرور: {str(e)}'}), 500

# ... (بخش /generate-scenario بدون تغییر باقی می‌ماند، فقط از مدل جدید استفاده می‌کند) ...
@app.route('/generate-scenario', methods=['POST'])
def generate_scenario():
    print("\n--- درخواست جدید (Vertex AI) برای /generate-scenario دریافت شد ---")
    if not model:
        return jsonify({'error': 'مدل Vertex AI به درستی پیکربندی نشده است.'}), 500
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
        
        print("در حال ارسال درخواست سناریو به Vertex AI...")
        response = model.generate_content(prompt)
        print("پاسخ سناریو از Vertex AI دریافت شد.")
        
        return jsonify({'scenario': response.text})
    except Exception as e:
        print("!!! یک خطای پیش‌بینی نشده در /generate-scenario رخ داد !!!")
        traceback.print_exc()
        return jsonify({'error': f'خطای داخلی سرور: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True)
```

#### قدم پنجم: به‌روزرسانی نیازمندی‌ها و متغیرها در Render

1.  به داشبورد پروژه در Render برگردید و به تب **"Settings"** بروید.
2.  در بخش **"Build Command"**، دستور را به شکل زیر آپدیت کنید تا کتابخانه‌های جدید نصب شوند:
    ```
    pip install Flask gunicorn "google-cloud-aiplatform>=1.38"
    

