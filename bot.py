from telethon import TelegramClient, events
import asyncio
import random
import time
from telethon.errors import FloodWaitError  # برای مدیریت FloodWait
# وارد کردن API ID و API Hash
api_id = 26665370   # API ID خود را وارد کنید
api_hash = '19323431934da1ab20b8f3247c3bdc96'  # API Hash خود را وارد کنید

client = TelegramClient('my_session11228001', api_id, api_hash)

# صف پیام‌های گروهی با حداکثر 50 پیام (تسک)
group_message_queue = asyncio.Queue(maxsize=50)

# دیکشنری برای ردیابی پیام‌های خصوصی:
# برای هر کاربر، تعداد پاسخ‌های ارسال شده و زمان مسدودسازی (blocked_until) ذخیره می‌شود.
private_message_info = {}  # key: user_id, value: {"count": int, "blocked_until": float}

# لیست پیام‌های تصادفی برای ریپلای در گروه (برای پیام‌های عادی صف‌بندی شده)
group_messages = [
    "سلام دوست عزیز، یه لحظه وقت داری؟",
    " میشه چند لحظه با هم صحبت کنیم؟",
    " ادد کردم لطفا بیا",
    " توروخدا ی لحظه بیا کارت دارم ",
    "خواهش میکنم ی لحظه بیاید",
    "من میخوام لطفا ی لحظه بیاید",
    "میشه الان راهنماییم کنی؟ موضوع مهمی دارم.",
    "منتظرم که سریع‌تر پاسخ بدی، لطفاً کمک کن."
]

# متغیر سراسری جهت کنترل وضعیت فعال بودن پردازش پیام‌های گروهی
group_processing_active = True

# متغیر سراسری جهت ذخیره شناسه ربات (برای تشخیص پیام‌های من)
bot_id = None

# ----------------- مدیریت وقفه پیام‌های گروهی -----------------
# 25 دقیقه فعال، سپس 5 دقیقه توقف
async def manage_group_pause():
    global group_processing_active
    while True:
        print("Group processing active for 25 minutes...")
        group_processing_active = True
        await asyncio.sleep(1500)  # 25 دقیقه = 1500 ثانیه

        print("Pausing group processing for 5 minutes...")
        group_processing_active = False
        await asyncio.sleep(300)   # 5 دقیقه = 300 ثانیه

# ----------------- پردازش پیام‌های گروهی -----------------
async def process_group_messages():
    while True:
        event = await group_message_queue.get()
        # در صورتی که وضعیت پردازش فعال نباشد، منتظر می‌مانیم
        while not group_processing_active:
            await asyncio.sleep(1)
        try:
            random_message = random.choice(group_messages)
            await client.send_message(event.chat_id, random_message, reply_to=event.id)
            print(f"Replied to group message in chat {event.chat_id}: {random_message}")
        except FloodWaitError as e:
            print(f"Flood wait triggered: waiting for {e.seconds} seconds before resuming group message processing.")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"Failed to process group message: {e}")
        finally:
            group_message_queue.task_done()
        # فاصله زمانی ۳ ثانیه قبل از پردازش پیام بعدی
        await asyncio.sleep(3)

# ----------------- متد اصلی -----------------
async def main():
    global bot_id
    await client.start()
    me = await client.get_me()
    bot_id = me.id
    print("Bot started successfully!")
    
    # راه‌اندازی تسک‌های مدیریت وقفه و پردازش پیام‌های گروهی
    asyncio.create_task(manage_group_pause())
    asyncio.create_task(process_group_messages())

    @client.on(events.NewMessage)
    async def handler(event):
        # ----------------- پیام‌های خصوصی -----------------
        if event.is_private:
            user_id = event.sender_id
            now = time.time()
            # دریافت اطلاعات کاربر یا مقدار پیش‌فرض
            info = private_message_info.get(user_id, {"count": 0, "blocked_until": 0})
            
            # اگر کاربر هنوز در حالت مسدود (block) است، پاسخی ارسال نمی‌شود.
            if now < info["blocked_until"]:
                print(f"User {user_id} is blocked until {info['blocked_until']}. No reply sent.")
                return
            
            # اگر دوره‌ی مسدودسازی به پایان رسیده باشد، شمارش ریست می‌شود.
            if info["blocked_until"] != 0 and now >= info["blocked_until"]:
                info["count"] = 0
                info["blocked_until"] = 0

            # اگر تعداد پاسخ‌های ارسال شده کمتر از 3 باشد، به پیام پاسخ می‌دهیم.
            if info["count"] < 3:
                try:
                    await client.send_message(event.chat_id, "https://t.me/Daroyaban")
                    info["count"] += 1
                    private_message_info[user_id] = info
                    print(f"Replied to private message from user: {user_id}. Reply count: {info['count']}")
                except Exception as e:
                    print(f"Failed to reply to private message: {e}")
            else:
                # اگر تعداد پاسخ‌ها 3 یا بیشتر شده باشد، کاربر به مدت 1 ساعت مسدود می‌شود.
                info["blocked_until"] = now + 3600  # 3600 ثانیه = 1 ساعت
                private_message_info[user_id] = info
                print(f"User {user_id} exceeded 3 replies. Blocking for 1 hour.")

        # ----------------- پیام‌های گروهی -----------------
        elif event.is_group:
            # قابلیت جدید:
            # اگر پیام دریافتی ریپلای به یکی از پیام‌های من (ربات) باشد،
            # بلافاصله در همان گروه به آن پیام، با متن "بیا چند لحظه من ریپم" پاسخ داده شود.
            if event.reply_to_msg_id:
                try:
                    replied_msg = await client.get_messages(event.chat_id, ids=event.reply_to_msg_id)
                    if replied_msg and replied_msg.sender_id == bot_id:
                        await client.send_message(event.chat_id, "بیا چند لحظه من ریپم", reply_to=event.id)
                        print(f"Sent immediate reply in group {event.chat_id} for a reply to bot's message.")
                        return  # پیام به صف اضافه نمی‌شود.
                except Exception as e:
                    print(f"Error processing group reply: {e}")

            # در غیر این صورت، پیام گروهی (که ریپلای به پیام‌های من نیست) به صف اضافه می‌شود.
            if not group_message_queue.full():
                await group_message_queue.put(event)
                print(f"Added group message from chat {event.chat_id} to queue.")
            else:
                print("Group message queue is full. Ignoring new group message.")

    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
