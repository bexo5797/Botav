import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# تفعيل التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# قراءة المتغيرات
TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_USERNAME = 'bexo50'
VIDEO_FILE_ID = os.getenv('VIDEO_FILE_ID')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
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
                f"⚠️ يرجى الاشتراك في القناة أولاً:\n"
                f"👉 @{CHANNEL_USERNAME}",
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Error checking subscription: {e}")
        await update.message.reply_text("⚠️ حدث خطأ، يرجى المحاولة لاحقاً.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == 'watch_video':
        # إرسال الفيديو
        if VIDEO_FILE_ID:
            try:
                await query.message.reply_video(
                    VIDEO_FILE_ID,
                    caption="🎥 هذا هو الفيديو المطلوب"
                )
                logger.info(f"Video sent to user {user_id}")
            except Exception as e:
                logger.error(f"Error sending video: {e}")
                await query.message.reply_text("⚠️ حدث خطأ في إرسال الفيديو")
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
                logger.info(f"User {user_id} subscribed successfully")
            else:
                await query.answer("❌ لم تشترك بعد، يرجى الاشتراك ثم الضغط على تحقق مرة أخرى.", show_alert=True)
        except Exception as e:
            logger.error(f"Error rechecking: {e}")
            await query.answer("حدث خطأ، يرجى المحاولة لاحقاً.", show_alert=True)

def main():
    """تشغيل البوت"""
    # إنشاء التطبيق
    application = Application.builder().token(TOKEN).build()
    
    # إضافة المعالجات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # تشغيل البوت
    if os.getenv('RAILWAY_ENVIRONMENT'):
        # وضعية Railway - استخدام polling بدلاً من webhook
        logger.info("Starting bot in Railway mode with polling...")
        application.run_polling()
    else:
        # وضعية التطوير المحلي
        logger.info("Starting bot in local mode...")
        application.run_polling()

if __name__ == '__main__':
    main()
