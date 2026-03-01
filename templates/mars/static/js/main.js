/* =========================================
   MARS GOVERNMENT PORTAL - INTERACTION CORE
   System: Ares-OS Frontend Logic
   ========================================= */

document.addEventListener('DOMContentLoaded', () => {
    // Sayfa yüklendiğinde çalışacak kodlar
    initializeSystem();
    handleFlashMessages();
});

// --- 1. SİSTEM BAŞLATMA ---
function initializeSystem() {
    console.log(">> ARES-OS: System Initialized.");
    
    // Eğer başvuru sayfasındaysak konsola başlangıç mesajı at
    const consoleLog = document.getElementById('console-log');
    if (consoleLog) {
        logToConsole("SECURE CONNECTION ESTABLISHED...");
        setTimeout(() => logToConsole("USER BIOMETRICS SCANNING..."), 800);
        setTimeout(() => logToConsole("WAITING FOR INPUT..."), 1500);
    }
}

// --- 2. BİLDİRİM MESAJLARI (FLASH MESSAGES) ---
function handleFlashMessages() {
    // Python'dan gelen flash mesajlarını bul
    const alerts = document.querySelectorAll('.flash-message'); // Bu class'ı layout.html'de ekleyeceğiz
    
    if (alerts.length > 0) {
        // 5 saniye sonra otomatik kaybolsun
        setTimeout(() => {
            alerts.forEach(alert => {
                alert.style.transition = "opacity 0.5s ease";
                alert.style.opacity = "0";
                setTimeout(() => alert.remove(), 500);
            });
        }, 5000);
    }
}

// --- 3. BAŞVURU FORMU YÖNETİMİ (WIZARD LOGIC) ---

// Mevcut adım (Global değişken)
let currentStep = 1;

/**
 * Bir sonraki adıma geçişi kontrol eder.
 * @param {number} targetStep - Hedef adım numarası
 */
function nextStep(targetStep) {
    // İleri gidiyorsak (örn: 1 -> 2), mevcut adımı kontrol et
    if (targetStep > currentStep) {
        if (!validateStep(currentStep)) {
            logToConsole("ERROR: MISSING REQUIRED FIELDS", "error");
            alert("Lütfen zorunlu alanları doldurun."); // İsteğe bağlı: Daha şık bir modal yapılabilir
            return;
        }
    }
    
    jumpToStep(targetStep);
}

/**
 * Adımlar arası geçiş animasyonunu ve DOM manipülasyonunu yapar.
 * @param {number} step - Gidilecek adım
 */
function jumpToStep(step) {
    // 1. Tüm bölümleri gizle
    const sections = document.querySelectorAll('.form-section');
    sections.forEach(sec => {
        sec.classList.remove('active');
        sec.style.display = 'none'; // CSS transition için
    });

    // 2. Hedef bölümü göster
    const targetSection = document.getElementById(`step-${step}`);
    if (targetSection) {
        targetSection.style.display = 'block';
        // Küçük bir gecikme ile opacity class'ını ekle (fade-in için)
        setTimeout(() => targetSection.classList.add('active'), 10);
    }

    // 3. Sağ taraftaki nokta navigasyonunu güncelle
    document.querySelectorAll('.nav-dot').forEach((dot, index) => {
        if (index + 1 === step) {
            dot.classList.add('active');
            dot.style.background = "#E03C31"; // Aktif renk
        } else {
            dot.classList.remove('active');
            dot.style.background = "rgba(255,255,255,0.2)"; // Pasif renk
        }
    });

    // 4. Üstteki Başlık Metnini Güncelle
    const titles = ["IDENTITY VERIFICATION", "BIOMETRIC DATA", "ACADEMIC HISTORY", "FINAL MANIFESTO"];
    const progressText = document.getElementById('progress-text');
    if (progressText) {
        progressText.innerText = `PHASE ${step}/4: ${titles[step-1]}`;
    }

    // 5. Konsola Log Yaz
    logToConsole(`ACCESSING PHASE ${step}: ${titles[step-1]}...`);

    // Global değişkeni güncelle
    currentStep = step;
}

/**
 * O anki adımın inputlarının dolu olup olmadığını kontrol eder.
 * @param {number} step - Kontrol edilecek adım
 */
function validateStep(step) {
    const currentSection = document.getElementById(`step-${step}`);
    const inputs = currentSection.querySelectorAll('input, select, textarea');
    
    let isValid = true;
    inputs.forEach(input => {
        if (input.hasAttribute('required') && !input.value.trim()) {
            isValid = false;
            input.style.borderColor = "#E03C31"; // Hata durumunda kırmızı çerçeve
        } else {
            input.style.borderColor = "rgba(255, 255, 255, 0.1)"; // Normale dön
        }
    });
    
    return isValid;
}

// --- 4. KONSOL SİMÜLASYONU (Sidebar) ---
function logToConsole(message, type = "info") {
    const consoleDiv = document.getElementById('console-log');
    if (!consoleDiv) return;

    const p = document.createElement('p');
    // Zaman damgası ekle
    const time = new Date().toLocaleTimeString('en-US', { hour12: false });
    
    // Mesaj rengi
    let colorClass = "text-mars-cyan"; // Varsayılan (Mavi)
    if (type === "error") colorClass = "text-mars-red";
    if (type === "success") colorClass = "text-green-500";

    p.className = `text-[10px] font-mono mb-1 ${colorClass}`;
    p.innerHTML = `<span class="opacity-50">[${time}]</span> > ${message}`;
    
    consoleDiv.appendChild(p);
    
    // Otomatik en alta kaydır
    consoleDiv.scrollTop = consoleDiv.scrollHeight;
}

// Global scope'a fonksiyonları ekle (HTML onclick'ler çalışsın diye)
window.nextStep = nextStep;
window.jumpToStep = jumpToStep;

// --- CANLI KULLANICI ADI KONTROLÜ ---
    const usernameInput = document.getElementById('usernameInput');
    const feedbackDiv = document.getElementById('usernameFeedback');
    const loadingIcon = document.getElementById('loadingIcon');
    let timeout = null; // Yazarken sürekli istek atmamak için (Debounce)

    usernameInput.addEventListener('input', function() {
        const username = this.value.trim();
        
        // Önceki zamanlayıcıyı temizle (Hızlı yazıyorsa bekle)
        clearTimeout(timeout);
        
        // Alan boşsa temizle
        if (username.length === 0) {
            feedbackDiv.innerText = "";
            usernameInput.classList.remove('border-red-500', 'border-green-500');
            return;
        }

        // Simgeyi göster
        loadingIcon.classList.remove('hidden');
        feedbackDiv.innerText = "VERİTABANI SORGULANIYOR...";
        feedbackDiv.className = "text-[9px] font-mono mt-1 text-yellow-500 animate-pulse";

        // Yazmayı bitirdikten 500ms sonra sorgula
        timeout = setTimeout(() => {
            checkAvailability(username);
        }, 500);
    });

    async function checkAvailability(username) {
        try {
            const response = await fetch('/check_username', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username: username })
            });

            const data = await response.json();
            
            loadingIcon.classList.add('hidden'); // Simgeyi gizle

            if (data.available) {
                // MÜSAİT
                feedbackDiv.innerText = ">> ONAYLANDI: " + data.message;
                feedbackDiv.className = "text-[9px] font-mono mt-1 text-green-500";
                usernameInput.classList.remove('border-red-500', 'border-gray-700');
                usernameInput.classList.add('border-green-500');
                
                // Sistem Loguna Yaz
                addLog(`ID CHECK: ${username} [AVAILABLE]`);
            } else {
                // DOLU
                feedbackDiv.innerText = ">> HATA: " + data.message;
                feedbackDiv.className = "text-[9px] font-mono mt-1 text-red-500 font-bold blink";
                usernameInput.classList.remove('border-green-500', 'border-gray-700');
                usernameInput.classList.add('border-red-500');
                
                // Sistem Loguna Yaz
                addLog(`CRITICAL: ID ${username} ALREADY REGISTERED!`);
            }

        } catch (error) {
            console.error('Hata:', error);
        }
    }