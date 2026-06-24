import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# تفعيل التسجيل
logging.basicConfig(level=logging.INFO)

# قراءة المتغيرات
TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_USERNAME = 'bexo50'  # اسم القناة بدون @
VIDEO_FILE_ID = os.getenv('VIDEO_FILE_ID')  # معرف الفيديو من تليجرام

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # التحقق من الاشتراك
    try:
        member = await context.bot.get_chat_member(f'@{CHANNEL_USERNAME}', user_id)
        if member.status in ['member', 'administrator', 'creator']:
            # مشترك ✅
            keyboard = [
                [InlineKeyboardButton("🎬 مشاهدة الفيديو", callback_data='watch_video')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "🎉 مرحباً بك! أنت مشترك في القناة.\n"
                "اضغط على الزر لمشاهدة الفيديو.",
                reply_markup=reply_markup
            )
        else:
            # غير مشترك ❌
            keyboard = [
                [InlineKeyboardButton("📢 اشترك في القناة", url=f'https://t.me/{CHANNEL_USERNAME}')],
                [InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data='check_subscription')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "⚠️ يرجى الاشتراك في القناة أولاً:\n"
                f"👉 @{CHANNEL_USERNAME}",
                reply_markup=reply_markup
            )
    except Exception as e:
        logging.error(f"Error checking subscription: {e}")
        await update.message.reply_text("حدث خطأ، يرجى المحاولة لاحقاً.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == 'watch_video':
        # إرسال الفيديو
        if VIDEO_FILE_ID:
            await query.message.reply_video(
                VIDEO_FILE_ID,
                caption="🎥 هذا هو الفيديو المطلوب"
            )
        else:
            await query.message.reply_text("⚠️ الفيديو غير متوفر حالياً")
    
    elif data == 'check_subscription':
        # إعادة التحقق
        try:
            member = await context.bot.get_chat_member(f'@{CHANNEL_USERNAME}', user_id)
            if member.status in ['member', 'administrator', 'creator']:
                keyboard = [[InlineKeyboardButton("🎬 مشاهدة الفيديو", callback_data='watch_video')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.edit_text(
                    "✅ تم التحقق! أنت مشترك الآن.\n"
                    "اضغط على الزر لمشاهدة الفيديو.",
                    reply_markup=reply_markup
                )
            else:
                await query.answer("❌ لم تشترك بعد، يرجى الاشتراك ثم الضغط على تحقق مرة أخرى.", show_alert=True)
        except Exception as e:
            logging.error(f"Error rechecking: {e}")
            await query.answer("حدث خطأ، يرجى المحاولة لاحقاً.", show_alert=True)

def main():
    # إنشاء التطبيق
    app = Application.builder().token(TOKEN).build()
    
    # إضافة المعالجات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # تشغيل البوت
    port = int(os.getenv('PORT', 8080))
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        webhook_url=f"https://{os.getenv('RAILWAY_STATIC_URL')}/webhook" if os.getenv('RAILWAY_STATIC_URL') else None
    )

if __name__ == '__main__':
    main()
