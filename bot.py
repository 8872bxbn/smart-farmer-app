"""
🌾 بوت المساعد الزراعي الذكي
Smart Farmer AI Bot - Telegram Bot for Agricultural Assistance
"""

import os
import logging
from dotenv import load_dotenv
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.constants import ChatAction, ParseMode
import asyncio

from ai_assistant import get_ai_response, analyze_plant_image

# تحميل متغيرات البيئة
load_dotenv()

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# الحصول على التوكن
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN غير موجود في .env")


class SmartFarmerBot:
    def __init__(self):
        self.user_conversations = {}
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأمر /start"""
        user = update.effective_user
        welcome_text = f"""
🌾 مرحباً بك في المساعد الزراعي الذكي!
Welcome to Smart Farmer AI Bot!

👋 مرحباً {user.first_name}!

أنا بوت متخصص في تقديم استشارات زراعية:
✅ تشخيص أمراض النباتات والآفات
✅ نصائح الري والتسميد
✅ معلومات عن المحاصيل
✅ جداول زراعة وحصاد
✅ الزراعة العضوية والمستدامة

📸 أرسل لي صورة نبات لتحليلها
📝 أو اكتب سؤالك الزراعي مباشرة

/help - قائمة الأوامر
/tips - نصائح زراعية
/about - عن البوت
"""
        await update.message.reply_text(welcome_text)
        
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأمر /help"""
        help_text = """
📋 قائمة الأوامر:

/start - بدء البوت
/help - عرض الأوامر
/about - معلومات البوت
/tips - نصائح زراعية عملية
/clear - مسح سجل المحادثة

💡 طرق الاستخدام:

1️⃣ **أرسل صورة نبات:**
   البوت سيحللها تلقائياً ويشخص حالتها

2️⃣ **اكتب سؤال مباشرة:**
   اسأل عن أي موضوع زراعي

3️⃣ **صورة + نص:**
   أرسل صورة مع ملاحظتك في التسمية التوضيحية

📚 أمثلة أسئلة:
- "كيف أعتني بنبات الطماطم؟"
- "ما هو أفضل وقت لزراعة الخس؟"
- "كيف أتخلص من حشرات المن؟"
- "ما هي علامات نقص النيتروجين؟"
"""
        await update.message.reply_text(help_text)
        
    async def about_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأمر /about"""
        about_text = """
🤖 عن بوت المساعد الزراعي الذكي

📌 الاسم: Smart Farmer AI Bot
🎯 الهدف: تقديم استشارات زراعية متخصصة

✨ الميزات:
✅ تحليل صور النباتات بدقة عالية
✅ تشخيص الأمراض والآفات
✅ نصائح زراعية عملية
✅ معلومات عن المحاصيل
✅ جداول زراعة وحصاد
✅ توصيات الأسمدة والري
✅ زراعة عضوية ومستدامة

🔧 التقنية:
- Python + Telegram Bot API
- Claude AI للتحليل الذكي
- معالجة الصور والنصوص

💡 الشعار: "زراعة ذكية لمستقبل أخضر"

👨‍💻 طور بواسطة: فريق المزارع الذكي

📧 للمساعدة: اكتب سؤالك مباشرة!
"""
        await update.message.reply_text(about_text)
        
    async def tips_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأمر /tips"""
        await update.message.chat.send_action(ChatAction.TYPING)
        
        tips_request = "أعطني 5 نصائح زراعية عملية مهمة للمزارعين في الفترة الحالية"
        response = await get_ai_response(tips_request)
        
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
        
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأمر /clear"""
        user_id = update.effective_user.id
        if user_id in self.user_conversations:
            del self.user_conversations[user_id]
        
        await update.message.reply_text(
            "✅ تم مسح سجل المحادثة. ابدأ محادثة جديدة!"
        )
        
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الرسائل النصية"""
        user_id = update.effective_user.id
        user_message = update.message.text
        
        # إظهار مؤشر الكتابة
        await update.message.chat.send_action(ChatAction.TYPING)
        
        # الحصول على تاريخ المحادثة
        if user_id not in self.user_conversations:
            self.user_conversations[user_id] = []
        
        conversation_history = self.user_conversations[user_id]
        
        # الحصول على الإجابة من AI
        response = await get_ai_response(user_message, conversation_history)
        
        # حفظ الرسالة والإجابة
        conversation_history.append({"role": "user", "content": user_message})
        conversation_history.append({"role": "assistant", "content": response})
        
        # حد أقصى للمحادثة (آخر 20 رسالة)
        if len(conversation_history) > 20:
            self.user_conversations[user_id] = conversation_history[-20:]
        
        # إرسال الرد
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
        
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الصور"""
        user_id = update.effective_user.id
        
        # إظهار مؤشر التحميل
        await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
        
        try:
            # تحميل الصورة
            photo_file = await update.message.photo[-1].get_file()
            image_bytes = await photo_file.download_as_bytearray()
            
            # الحصول على ملاحظة المستخدم (إن وجدت)
            user_note = update.message.caption or ""
            
            # إظهار مؤشر الكتابة
            await update.message.chat.send_action(ChatAction.TYPING)
            
            # تحليل الصورة
            response = await analyze_plant_image(
                bytes(image_bytes),
                user_note,
                media_type="image/jpeg"
            )
            
            # إرسال الرد
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            
            # حفظ في السجل
            if user_id not in self.user_conversations:
                self.user_conversations[user_id] = []
            
            self.user_conversations[user_id].append({
                "role": "user",
                "content": f"[صورة نبات] {user_note}" if user_note else "[صورة نبات]"
            })
            self.user_conversations[user_id].append({
                "role": "assistant",
                "content": response
            })
            
        except Exception as e:
            error_msg = f"❌ حدث خطأ في معالجة الصورة:\n{str(e)}"
            await update.message.reply_text(error_msg)
            logger.error(f"Error processing photo: {e}")
            
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأخطاء"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ حدث خطأ أثناء معالجة طلبك.\nيرجى المحاولة مرة أخرى لاحقاً."
            )


async def setup_bot():
    """إعداد بوت تلجرام"""
    bot = SmartFarmerBot()
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # إضافة معالجات الأوامر
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("help", bot.help_command))
    app.add_handler(CommandHandler("about", bot.about_command))
    app.add_handler(CommandHandler("tips", bot.tips_command))
    app.add_handler(CommandHandler("clear", bot.clear_command))
    
    # معالج الصور
    app.add_handler(MessageHandler(filters.PHOTO, bot.handle_photo))
    
    # معالج الرسائل النصية
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_text))
    
    # معالج الأخطاء
    app.add_error_handler(bot.error_handler)
    
    # تعيين أوامر البوت
    commands = [
        BotCommand("start", "بدء البوت"),
        BotCommand("help", "عرض الأوامر"),
        BotCommand("about", "معلومات البوت"),
        BotCommand("tips", "نصائح زراعية"),
        BotCommand("clear", "مسح السجل"),
    ]
    await app.bot.set_my_commands(commands)
    
    return app


async def main():
    """البرنامج الرئيسي"""
    print("🌾 بدء تشغيل بوت المساعد الزراعي الذكي...")
    print("🤖 البوت: @smart_farmer_ai_bot")
    print("📱 الرابط: https://t.me/smart_farmer_ai_bot")
    print("-" * 50)
    
    app = await setup_bot()
    
    print("✅ البوت في وضع الاستقبال...")
    print("اضغط Ctrl+C لإيقاف البوت")
    await app.run_polling()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 تم إيقاف البوت.")
    except Exception as e:
        print(f"❌ خطأ: {e}")
        logger.error(f"Fatal error: {e}")
