document.addEventListener('DOMContentLoaded', () => {
    const steps = document.querySelectorAll('.step');
    const brandForm = document.getElementById('brandForm');
    const generateScenarioBtn = document.getElementById('generateScenarioBtn');
    
    const loaderConcerns = document.getElementById('loader-concerns');
    const loaderScenario = document.getElementById('loader-scenario');
    
    const concernsList = document.getElementById('concernsList');
    const scenarioResult = document.getElementById('scenarioResult');

    let brandData = {};
    let concernsData = "";

    const showStep = (stepNumber) => {
        steps.forEach((step, index) => {
            step.classList.toggle('active', index + 1 === stepNumber);
        });
        window.scrollTo(0, 0); // اسکرول به بالای صفحه هنگام تغییر مرحله
    };

    brandForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        showStep(2);
        loaderConcerns.style.display = 'block';
        concernsList.innerHTML = '';

        const formData = new FormData(brandForm);
        const formEntries = Object.fromEntries(formData.entries());

        // تبدیل داده‌های فرم به یک رشته خوانا برای ارسال به AI
        let formattedBrandInfo = "بریف استراتژی برند:\n\n";
        for (const [key, value] of Object.entries(formEntries)) {
            if (value) { // فقط فیلدهای پر شده را ارسال کن
                // کلیدها را برای خوانایی بهتر تمیز می‌کنیم
                const cleanKey = key.replace(/^\d+_/, '').replace(/_/g, ' ');
                formattedBrandInfo += `- ${cleanKey}: ${value}\n`;
            }
        }
        brandData = formattedBrandInfo;

        try {
            const response = await fetch('/generate-concerns', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(brandData),
            });

            if (!response.ok) throw new Error(`خطای سرور: ${response.statusText}`);

            const data = await response.json();
            if(data.error) throw new Error(data.error);

            concernsData = data.concerns;
            
            const concernsArray = concernsData.split('\n').filter(line => line.trim() !== '');
            concernsArray.forEach(concern => {
                const li = document.createElement('li');
                li.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${concern.replace(/^\d+\.\s*/, '')}`;
                concernsList.appendChild(li);
            });

        } catch (error) {
            const li = document.createElement('li');
            li.style.color = 'red';
            li.innerText = `خطا در تحلیل دغدغه‌ها: ${error.message}`;
            concernsList.appendChild(li);
        } finally {
            loaderConcerns.style.display = 'none';
        }
    });

    generateScenarioBtn.addEventListener('click', async () => {
        showStep(3);
        loaderScenario.style.display = 'block';
        scenarioResult.innerText = '';

        try {
            const response = await fetch('/generate-scenario', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    brandInfo: brandData,
                    concerns: concernsData,
                }),
            });

            if (!response.ok) throw new Error(`خطای سرور: ${response.statusText}`);
            
            const data = await response.json();
            if(data.error) throw new Error(data.error);

            scenarioResult.innerText = data.scenario;

        } catch (error) {
            scenarioResult.innerText = `خطا در تولید سناریو: ${error.message}`;
            scenarioResult.style.color = 'red';
        } finally {
            loaderScenario.style.display = 'none';
        }
    });
    
    showStep(1);
});
