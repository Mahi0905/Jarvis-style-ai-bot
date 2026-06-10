import gradio as gr
import requests
import os
import tempfile
import json
from gtts import gTTS

# Groq API (FREE)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# --- FARMING KNOWLEDGE BASE (DATASET) ---
FARMING_DATA = [
  {"category": "Paddy/Rice", "q_en": "How to control Stem Borer (sundi) in paddy?", "q_hi": "धान में तना छेदक (सुंडी) को कैसे नियंत्रित करें?", "ans_en": "Apply Cartap Hydrochloride 4G @ 10kg/acre or Fipronil 0.3% GR @ 10kg/acre in standing water. Or spray Chlorantraniliprole 18.5% SC @ 60ml/acre.", "ans_hi": "खड़े पानी में कार्टाप हाइड्रोक्लोराइड 4जी 10 किलो/एकड़ या फिप्रोनिल 0.3% जीआर 10 किलो/एकड़ डालें। या क्लोरेंट्रानिलिप्रोल 18.5% एससी 60 मिली/एकड़ का छिड़काव करें।"},
  {"category": "Paddy/Rice", "q_en": "Paddy leaves turning yellow from tips.", "q_hi": "धान की पत्तियां ऊपर से पीली हो रही हैं।", "ans_en": "Likely Nitrogen deficiency. If soil is sandy, apply Urea. If yellowing persists, check for Zinc deficiency (rusty spots). Spray Zinc Sulphate 21% (1kg) + Urea (1kg) in 100L water.", "ans_hi": "यह नाइट्रोजन की कमी हो सकती है। यदि यूरिया से ठीक न हो, तो जिंक की कमी हो सकती है। 100 लीटर पानी में जिंक सल्फेट 21% (1 किलो) + यूरिया (1 किलो) मिलाकर छिड़काव करें।"},
  {"category": "Wheat", "q_en": "Treatment for Wheat Yellow Rust (Peela Ratua).", "q_hi": "गेहूं के पीला रतुआ रोग का इलाज।", "ans_en": "Spray Propiconazole 25% EC @ 200ml mixed in 200 liters of water per acre immediately.", "ans_hi": "लक्षण दिखते ही प्रति एकड़ 200 लीटर पानी में 200 मिली प्रोपिकोनाज़ोल 25% ईसी (Propiconazole) मिलाकर छिड़काव करें।"},
  {"category": "Wheat", "q_en": "Control Phalaris minor (Gulli Danda) in wheat.", "q_hi": "गेहूं में गुल्ली डंडा (मंडूसी) की रोकथाम।", "ans_en": "Use Pre-emergence: Pendimethalin 30% EC @ 1.5L/acre (0-2 days of sowing). Post-emergence (30-35 days): Clodinafop Propargyl 15% WP @ 160g/acre.", "ans_hi": "बुवाई के 2 दिन के भीतर पेंडिमेथालिन 30% ईसी 1.5 लीटर/एकड़ डालें। बुवाई के 30-35 दिन बाद क्लोडिनाफॉप प्रोपारगिल 15% डब्ल्यूपी 160 ग्राम/एकड़ छिड़कें।"},
  {"category": "Cotton", "q_en": "Medicine for Pink Bollworm in Cotton.", "q_hi": "कपास में गुलाबी सुंडी की दवा।", "ans_en": "Install Pheromone traps (5/acre). If severe, spray Emamectin Benzoate 5% SG @ 100g/acre or Profenofos 50% EC @ 400ml/acre.", "ans_hi": "फेरोमोन ट्रैप (5/एकड़) लगाएं। ज्यादा प्रकोप होने पर इमामेक्टिन बेंजोएट 5% एसजी 100 ग्राम/एकड़ या प्रोफेनोफोस 50% ईसी 400 मिली/एकड़ का छिड़काव करें।"},
  {"category": "Cotton", "q_en": "Cotton leaves curling upwards (Leaf Curl).", "q_hi": "कपास के पत्ते ऊपर मुड़ रहे हैं (मरोड़िया)।", "ans_en": "Caused by Whitefly. Spray Imidacloprid 17.8% SL @ 40ml/acre or Thiamethoxam 25% WG @ 40g/acre.", "ans_hi": "यह सफेद मक्खी के कारण है। इमिडाक्लोप्रिड 17.8% एसएल 40 मिली/एकड़ या थियामेथोक्सम 25% डब्ल्यूजी 40 ग्राम/एकड़ का छिड़काव करें।"},
  {"category": "Sugarcane", "q_en": "Red Rot disease in Sugarcane.", "q_hi": "गन्ने में लाल सड़न रोग।", "ans_en": "Uproot infected clumps. Treat seeds with Carbendazim 50% WP (0.1%) for 15 mins before planting. Use resistant varieties.", "ans_hi": "संक्रमित पौधों को जला दें। बुवाई से पहले बीजों को कार्बेन्डाज़िम 50% डब्ल्यूपी (0.1%) घोल में 15 मिनट उपचारित करें।"},
  {"category": "Potato", "q_en": "Late Blight (Jhulsarog) in Potato.", "q_hi": "आलू में पछेती झुलसा रोग।", "ans_en": "Preventive: Mancozeb 75% WP @ 2g/L. Curative: Cymoxanil 8% + Mancozeb 64% @ 2.5g/L water.", "ans_hi": "बचाव के लिए मैंकोज़ेब 75% डब्ल्यूपी 2 ग्राम/लीटर। रोग आने पर साइमोक्साहिल 8% + मैंकोज़ेब 64% 2.5 ग्राम/लीटर पानी का छिड़काव करें।"},
  {"category": "Mustard", "q_en": "Aphids (Chepa/Mahukit) control in Mustard.", "q_hi": "सरसों में चेपा/माहू कीट नियंत्रण।", "ans_en": "Spray Thiamethoxam 25% WG @ 50-100g/acre or Dimethoate 30% EC @ 250ml/acre in 200L water.", "ans_hi": "200 लीटर पानी में थियामेथोक्सम 25% डब्ल्यूजी 50-100 ग्राम/एकड़ या डाइमेथोएट 30% ईसी 250 मिली/एकड़ मिलाकर छिड़कें।"},
  {"category": "Fertilizer", "q_en": "How to use Nano Urea?", "q_hi": "नैनो यूरिया का उपयोग कैसे करें?", "ans_en": "Mix 2-4 ml Nano Urea per liter of water. Spray on leaves at active growth stages. 500ml bottle = 45kg Urea bag.", "ans_hi": "2-4 मिली नैनो यूरिया प्रति लीटर पानी में मिलाएं और पत्तियों पर छिड़कें। 500 मिली की बोतल एक बोरी यूरिया के बराबर है।"},
  {"category": "General", "q_en": "Soil Health Test.", "q_hi": "मिट्टी की जांच।", "ans_en": "Take 500g soil from 5-6 spots (6 inch deep), mix it, and take to KVK or Soil Lab.", "ans_hi": "5-6 जगहों से 6 इंच गहरी मिट्टी लें, मिलाएं और 500 ग्राम मिट्टी कृषि विज्ञान केंद्र (KVK) या लैब में ले जाएं।"}
]

def format_knowledge_base():
    """Converts JSON data into a text format for the LLM System Prompt"""
    kb_text = "--- AGRICULTURAL KNOWLEDGE BASE ---\n"
    for item in FARMING_DATA:
        kb_text += f"Topic: {item['category']}\n"
        kb_text += f"Q (Hindi): {item['q_hi']}\n"
        kb_text += f"A (Hindi): {item['ans_hi']}\n"
        kb_text += f"A (English): {item['ans_en']}\n"
        kb_text += "---\n"
    return kb_text

def detect_language(text):
    """Detect Hindi or English"""
    hindi_chars = any('\u0900' <= c <= '\u097F' for c in text)
    return "hi" if hindi_chars else "en"

def text_to_speech(text, lang="en"):
    """Convert text to speech"""
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)
        return temp_file.name
    except:
        return None

def get_jarvis_response(text):
    """Get AI response from Groq with injected Farming Knowledge"""
    
    farming_kb = format_knowledge_base()

    system_prompt = f"""You are GURU (General User Response Unit), an advanced AI Assistant specialized in Indian Agriculture.
PERSONALITY:
- You are like JARVIS, but for Farmers (Kisan Mitra).
- You are intelligent, polite, and precise.
- You speak mostly in the user's language (Hindi or English).
INSTRUCTIONS:
1. Below is a 'AGRICULTURAL KNOWLEDGE BASE'. 
2. IF the user asks a question related to these topics, use the EXACT chemical names, dosages, and solutions provided in the Knowledge Base. Do not make up your own medicines if the answer is there.
3. If the user asks general questions (weather, news, greeting), answer naturally like a smart assistant.
4. Keep answers concise. Avoid long paragraphs.
{farming_kb}
If the user asks in Hindi, answer in Hindi.
If the user asks in English, answer in English.
"""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                "max_tokens": 400,
                "temperature": 0.3
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return "Server error. Please try again."
    
    except Exception as e:
        return "Connection error. Please check internet."

def process_voice(audio):
    """Main function: Speech → AI → Text + Speech outputs"""
    
    if audio is None:
        return "❌ कृपया पहले रिकॉर्ड करें | Please record first", None
    
    # Step 1: Speech to Text
    try:
        with open(audio, "rb") as audio_file:
            response = requests.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                files={"file": audio_file},
                data={"model": "whisper-large-v3-turbo"}
            )
        
        if response.status_code == 200:
            user_text = response.json()["text"]
        else:
            return "❌ आवाज समझ नहीं आई | Could not understand", None
    
    except Exception as e:
        return "❌ ऑडियो में त्रुटि | Audio error", None
    
    # Step 2: Get AI Response
    ai_response = get_jarvis_response(user_text)
    
    # Step 3: Text to Speech
    lang = detect_language(ai_response)
    audio_output = text_to_speech(ai_response, lang)
    
    # Format output
    full_response = f"🎤 आपका सवाल: {user_text}\n\n🌾 गुरु का जवाब:\n{ai_response}"
    
    return full_response, audio_output


# ===================== COMPACT GRADIO UI =====================

with gr.Blocks(title="Kisan GURU", theme=gr.themes.Soft(), css="""

    /* PAGE */
    body, .gradio-container { 
        background-color: #e8f5e9 !important; 
        min-height: 100vh;
    }
    .gradio-container { padding: 10px !important; max-width: 800px !important; margin: auto; }
    
    /* HEADER */
    .header { 
        text-align: center; 
        padding: 15px; 
        background-color: #a5d6a7; 
        border-radius: 15px; 
        border: 3px solid #4caf50; 
        margin-bottom: 15px; 
    }
    .title { color: #1b5e20; font-size: 2.5em; font-weight: 900; margin: 0; }
    .subtitle { color: #2e7d32; font-size: 1.1em; font-weight: 700; margin-top: 5px; }
    
    /* RECORD SECTION */
    .record-section {
        background-color: #c8e6c9;
        border: 3px solid #66bb6a;
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        margin-bottom: 10px;
    }
    .record-label {
        color: #1b5e20;
        font-size: 1em;
        font-weight: 200;
        margin-bottom: 10px;
    }
    
    /* BIG AUDIO RECORDER */
    .big-recorder {
        border: 4px solid #4caf50 !important;
        border-radius: 15px !important;
        background-color: #f1f8e9 !important;
        min-height: 30px !important;
    }
    .big-recorder audio { height: 60px !important; }
    .big-recorder button { 
        font-size: 1em !important;
    }
    
    /* ASK BUTTON */
    .ask-btn {
        background-color: #4caf50 !important;
        color: white !important;
        font-size: 1.5em !important;
        font-weight: 800 !important;
        padding: 15px !important;
        border-radius: 12px !important;
        border: 3px solid #2e7d32 !important;
        width: 100% !important;
        margin: 10px 0 !important;
    }
    .ask-btn:hover { background-color: #43a047 !important; }
    
    /* OUTPUT SECTION */
    .output-section {
        background-color: #f1f8e9;
        border: 3px solid #81c784;
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .output-label {
        color: #1b5e20;
        font-size: 1.2em;
        font-weight: 800;
        text-align: center;
        margin-bottom: 5px;
    }
    
    /* TEXTBOX */
    textarea {
        font-size: 1.1em !important;
        font-weight: 600 !important;
        background-color: #fafafa !important;
        border: 2px solid #a5d6a7 !important;
        border-radius: 8px !important;
    }
    
    /* AUDIO OUTPUT */
    .audio-out { 
        border: 2px solid #81c784 !important; 
        border-radius: 10px !important; 
        background-color: #f9fbe7 !important;
    }
    
    /* CLEAR BUTTON */
    .clear-btn {
    background-color: #fff3e0 !important;
    color: #e65100 !important;
    font-size: 0.8em !important;
    font-weight: 600 !important;
    border: 1px solid #ffb74d !important;
    border-radius: 4px !important;
    padding: 2px 6px !important;
    }
    
    /* TIPS */
    .tips {
        background-color: #c8e6c9;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        font-size: 0.95em;
        color: #2e7d32;
        font-weight: 600;
    }

""") as demo:

    # === HEADER ===
    gr.HTML("""
    <div class="header">
        <div style="display: flex; align-items: center; justify-content: center;">
            <span style="font-size: 2em;">🌾</span>
            <h1 class="title">Kisan G.U.R.U.</h1>
            <span style="font-size: 2em;">🚜</span>
        </div>
        <p class="subtitle">🌱 AI for Indian Farmers | भारतीय किसान मित्र</p>
    </div>
    """)

    # === STEP 1: RECORD ===
    gr.HTML("""
    <div class="record-section">
        <div class="record-label">🎤 Step 1: सवाल बोलें | Speak Question</div>
        <div style="color: #388e3c; font-size: 1em;">🔴 बटन दबाएं → बोलें → बटन दबाएं</div>
    </div>
    """)
    
    audio_input = gr.Audio(
        sources=["microphone"],
        type="filepath",
        label="",
        elem_classes="big-recorder"
    )

    # === STEP 2: ASK BUTTON ===
    submit_btn = gr.Button(
        "🌾 Step 2: गुरु से पूछें | ASK GURU 🌾",
        elem_classes="ask-btn"
    )

    # === STEP 3: OUTPUTS ===
    gr.HTML('<div class="output-label">📋 Step 3: जवाब | Answer</div>')
    
    with gr.Row():
        with gr.Column(scale=3):
            answer_output = gr.Textbox(
                label="",
                lines=5,
                interactive=False,
                placeholder="जवाब यहाँ दिखेगा | Answer will appear here",
                elem_classes="output-section"
            )
        with gr.Column(scale=2):
            gr.HTML('<div style="text-align:center; color:#1b5e20; font-weight:700; margin-bottom:5px;">🔊 सुनें | Listen</div>')
            audio_output = gr.Audio(
                label="",
                autoplay=True,
                elem_classes="audio-out"
            )

    # === CLEAR BUTTON ===
    clear_btn = gr.Button("🗑️ साफ करें | Clear", elem_classes="clear-btn")

    # === TIPS ===
    gr.HTML("""
    <div class="tips">
        💡 <b>Try:</b> "गेहूं में पीला रतुआ का इलाज?" | "धान में सुंडी कैसे रोकें?" | "Nano Urea कैसे use करें?"
    </div>
    """)

    # === EVENTS ===
    submit_btn.click(
        fn=process_voice,
        inputs=[audio_input],
        outputs=[answer_output, audio_output]
    )
    
    clear_btn.click(
        fn=lambda: (None, "", None),
        inputs=[],
        outputs=[audio_input, answer_output, audio_output]
    )


if __name__ == "__main__":
    demo.launch() 
