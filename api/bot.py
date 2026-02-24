import os
import random
import string
import requests
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request

app = Flask(__name__)

# Firebase Initialize (Environment Variables ব্যবহার করা ভালো)
if not firebase_admin._apps:
    # আপনার Firebase Admin SDK JSON ফাইলটির ডাটা এখানে ডিকশনারি হিসেবে দিন
    # অথবা Vercel Environment Variable থেকে লোড করুন
    cred = credentials.Certificate("firebase-key.json") 
    firebase_admin.initialize_app(cred)

db = firestore.client()

def generate_slug(length=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

@app.route('/api/bot', methods=['POST'])
def telegram_bot():
    update = request.get_json()
    
    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        original_url = update["message"]["text"]

        if original_url.startswith("http"):
            slug = generate_slug()
            
            # Firestore-এ ডাটা সেভ
            db.collection("links").document(slug).set({
                "original_url": original_url,
                "slug": slug,
                "clicks": 0
            })

            your_domain = "https://your-vercel-project.vercel.app"
            final_link = f"{your_domain}/index.html?id={slug}"
            
            # ইউজারকে রিপ্লাই পাঠানো
            msg = f"আপনার লিংক তৈরি: {final_link}"
            requests.get(f"https://api.telegram.org/bot{os.environ['BOT_TOKEN']}/sendMessage?chat_id={chat_id}&text={msg}")

    return "OK", 200
  
