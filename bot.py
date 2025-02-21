from telethon import TelegramClient, events
import asyncio
import random
import time

# ---------------------- تنظیمات API و راه‌اندازی کلاینت ----------------------
api_id = 26665370 
api_hash = '19323431934da1ab20b8f3247c3bdc96'
client = TelegramClient('my_session', api_id, api_hash)

# ---------------------- تنظیمات مربوط به پیام‌های گروه ----------------------

group_messages = [
    
    "توروخدا کمک کنيد دنبال ي دارو ميگردم",
    "نيازمند گارداسيل ",
    "لطفا بیعیومو چک کنید",
    "چند لحظه ميشه تشريف بيارين؟",
    "ميشه چند لحظه بيايد لطفا؟",
    "لینک گروه بزرگ تبادل دارو نایاب تو بیعیوم گذاشتم مشتریا و همکارا عضو بشید لطفا",
    "بيومو ببينيد",
    "@Daroyaban",
    "ي لحظه بيا لطفا ",
    "@Daroyaban",
    "به شدت نيازمند ريتالين تورخدا اگر داريد بيايد",
    "سلام ، من ميخوام ، ميشه چند لحظه بيايد؟",
    "سلام ، من ميخوام ، ميشه چند لحظه بيايد؟",
    "نمياي ؟ من نميتونم پيام بدم",
    "تعداد بالا ميخوام",
    "نمياي؟؟؟؟؟",
    "بيا ديگه لطفا",
]

# دیکشنری نگهدارنده زمان آخرین ارسال پیام در هر گروه (کلید: chat_id)
group_last_sent = {}

# تنظیمات زمان خنک‌کننده برای گروه‌ها (برای همه گروه‌ها یکسان)
DEFAULT_COOLDOWN = 2 * 2   # 20 دقیقه

# ---------------------- تنظیمات محدودیت ارسال پیام‌های گروه ----------------------
group_msg_counter = 0         # شمارنده پیام‌های ارسال شده در گروه‌ها
group_pause_until = 0         # زمان پایان توقف ارسال پیام‌های گروهی (در حالت توقف 5 دقیقه‌ای)

# دیکشنری برای نگهداری زمان تعلیق گروه‌ها به دلیل خطا (برای مثال 1 ساعت)
group_banned_until = {}       # کلید: chat_id، مقدار: timestamp پایان تعلیق

# ---------------------- تنظیمات مربوط به پیام‌های خصوصی ----------------------
private_msg_history = {}
private_disabled_users = {}

# ---------------------- تابع ارسال خودکار پیام به گروه‌ها ----------------------
async def broadcast_group_messages():
    """
    این تابع به صورت مداوم (بی‌نهایت) اجرا می‌شود و گروه‌هایی که ربات عضو آن‌هاست را بررسی می‌کند.
    در صورتی که:
      - از ارسال آخرین پیام در یک گروه بیش از ۲۰ دقیقه گذشته باشد،
      - و آن گروه در وضعیت تعلیق (ban) نباشد،
    پیام تصادفی ارسال می‌شود.
    همچنین، پس از ارسال ۵۰ پیام، ارسال پیام‌ها به مدت ۵ دقیقه متوقف شده و در صورت بروز خطا (مانند ممنوعیت ارسال) گروه برای مدتی از لیست هدف کنار گذاشته می‌شود.
    """
    global group_msg_counter, group_pause_until
    while True:
        now = time.time()
        # اگر در حالت توقف (pause) هستیم، تا پایان توقف صبر می‌کنیم
        if now < group_pause_until:
            remaining = int(group_pause_until - now)
            print(f"Group messaging is paused for {remaining} more seconds.")
            await asyncio.sleep(1)
            continue

        try:
            dialogs = await client.get_dialogs()
            # فیلتر کردن تنها گروه‌های عمومی
            groups = [d for d in dialogs if d.is_group]
        except Exception as e:
            print(f"Error fetching dialogs: {e}")
            await asyncio.sleep(3)
            continue

        sent_any = False  # برای ردیابی اینکه در این چرخه حداقل یک پیام ارسال شده باشد

        for group in groups:
            chat_id = group.id

            # بررسی وضعیت تعلیق (ban) برای گروه
            if chat_id in group_banned_until and now < group_banned_until[chat_id]:
                # اگر هنوز زمان تعلیق به پایان نرسیده است، این گروه را رد می‌کنیم
                continue

            cooldown = DEFAULT_COOLDOWN
            last_sent = group_last_sent.get(chat_id, 0)
            if now - last_sent >= cooldown:
                try:
                    random_message = random.choice(group_messages)
                    # ارسال پیام به گروه به صورت عادی (بدون ریپلای)
                    await client.send_message(chat_id, random_message)
                    group_last_sent[chat_id] = time.time()
                    sent_any = True
                    group_msg_counter += 1
                    print(f"Sent message to group {chat_id}. Total group messages sent: {group_msg_counter}")

                    # اگر تعداد پیام‌های ارسال شده به 50 رسید، ارسال پیام‌ها برای 5 دقیقه متوقف می‌شود
                    if group_msg_counter >= 50:
                        group_pause_until = time.time() + 1 * 3  # توقف 5 دقیقه‌ای
                        print("Reached 50 group messages. Pausing group messaging for 5 minutes.")
                        group_msg_counter = 0  # بازنشانی شمارنده پس از توقف
                        break  # خروج از حلقه for جهت ادامه در چرخه بعدی

                    await asyncio.sleep(1)  # تأخیر 3 ثانیه‌ای بین ارسال پیام‌ها

                except Exception as e:
                    error_message = str(e)
                    print(f"Error sending message to group {chat_id}: {error_message}")
                    # در صورت بروز خطاهایی که نشان از ممنوعیت ارسال دارند، این گروه را برای مدت 1 ساعت تعلیق می‌کنیم
                    if "banned from sending messages" in error_message.lower() or "can't write" in error_message.lower():
                        group_banned_until[chat_id] = time.time() + 200  # تعلیق به مدت 1 ساعت
                        print(f"Group {chat_id} is banned for 1 hour. Skipping until then.")
                    # به سرعت به گروه بعدی می‌رویم
                    continue

        if not sent_any:
            await asyncio.sleep(1)

# ---------------------- هندلر پیام‌های خصوصی ----------------------
@client.on(events.NewMessage)
async def handle_private_messages(event):
    """
    در چت‌های خصوصی، پاسخ پیام‌ها بدون تأخیر ارسال می‌شود.
    اگر یک کاربر بیش از 3 پیام در بازه 1 ساعته ارسال کند، پاسخ‌دهی برای او به مدت 1 ساعت متوقف می‌شود.
    """
    if event.is_private:
        user_id = event.sender_id
        current_time = time.time()

        if user_id in private_disabled_users and current_time < private_disabled_users[user_id]:
            print(f"User {user_id} is temporarily disabled from private replies.")
            return

        history = private_msg_history.get(user_id, [])
        history = [t for t in history if current_time - t < 1800]
        history.append(current_time)
        private_msg_history[user_id] = history

        if len(history) > 3:
            private_disabled_users[user_id] = current_time + 1800  # تعلیق برای 1 ساعت
            private_msg_history[user_id] = []
            print(f"User {user_id} has been disabled for one hour due to excessive private messages.")
            return

        try:
            await client.send_message(event.chat_id, "https://t.me/Daroyaban")
            print(f"Replied to private message from user {user_id}.")
        except Exception as e:
            print(f"Error replying to private message from user {user_id}: {e}")

# ---------------------- تابع اصلی ----------------------
async def main():
    await client.start()
    print("Bot started successfully!")
    # شروع تسک ارسال خودکار پیام به گروه‌ها
    asyncio.create_task(broadcast_group_messages())
    # ادامه دریافت رویدادهای جدید (برای چت‌های خصوصی)
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
