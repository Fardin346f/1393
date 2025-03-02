from telethon import TelegramClient, events
import asyncio
import random
import time
# وارد کردن API ID و API Hash
api_id = 26665370 
api_hash = '19323431934da1ab20b8f3247c3bdc96'

client = TelegramClient('my_session', api_id, api_hash)

# صف پیام‌ها برای گروه‌ها
group_message_queue = asyncio.Queue()
group_processing_active = True  # فعال یا غیرفعال بودن پردازش پیام‌های گروه
group_semaphore = asyncio.Semaphore(10)  # محدود کردن تعداد پردازش همزمان پیام‌های گروه
private_msg_history = {}
private_disabled_users = {}
# مجموعه کاربران پاسخ داده‌شده در چت خصوصی
private_responded_users = set()

# پیام‌های تصادفی برای ریپلای به گروه‌ها
group_messages = [
    "توروخدا کمک کنيد دنبال ي دارو ميگردم",
    "نيازمند گارداسيل ",
    "لطفا بیعیومو چک کنید",
    "چند لحظه ميشه تشريف بيارين؟",
    "ميشه چند لحظه بيايد لطفا؟",
    "لینک گروه بزرگ تبادل دارو نایاب تو بیعیوم گذاشتم مشتریا و همکارا عضو بشید لطفا",
    "بيومو ببينيد",
    "@IR_Daro",
    "@IR_Daro",
    "ي لحظه بيا لطفا ",
    "@IR_Daro",
    "به شدت نيازمند ريتالين تورخدا اگر داريد بيايد",
    "سلام ، من ميخوام ، ميشه چند لحظه بيايد؟",
    "سلام ، @IR_Daro  ، ميشه چند لحظه بيايد؟",
    "نمياي ؟ من نميتونم پيام بدم",
    "تعداد بالا ميخوام",
    "نمياي؟؟؟؟؟",
    "بيا ديگه لطفا",
]


# تابع مدیریت وقفه‌های گروه
async def manage_group_pause():
    global group_processing_active
    while True:
        print("Group processing active for 15 minutes...")
        group_processing_active = True
        await asyncio.sleep(300)  # 15 دقیقه فعال

        print("Pausing group processing for 5 minutes...")
        group_processing_active = False
        await asyncio.sleep(150)  # 5 دقیقه غیرفعال

# تابع پردازش پیام‌های گروه
async def process_group_messages():
    while True:
        event = await group_message_queue.get()
        try:
            if group_processing_active:
                async with group_semaphore:  # محدودیت تعداد پردازش همزمان
                    random_message = random.choice(group_messages)
                    await client.send_message(event.chat_id, random_message, reply_to=event.id)
                    print(f"Replied to group message: {random_message}")
        except Exception as e:
            print(f"Failed to process group message: {e}")
        finally:
            group_message_queue.task_done()

# متد اصلی برای راه‌اندازی ربات
async def main():
    await client.start()
    print("Bot started successfully!")

    # شروع مدیریت وقفه‌ها و پردازش پیام‌های گروه
    asyncio.create_task(manage_group_pause())
    asyncio.create_task(process_group_messages())

    @client.on(events.NewMessage)
    async def handler(event):
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
                await client.send_message(event.chat_id, "https://t.me/IR_DARO")
                print(f"Replied to private message from user {user_id}.")
            except Exception as e:
                print(f"Error replying to private message from user {user_id}: {e}")

        elif event.is_group:  # پیام گروه
            if group_message_queue.qsize() < 25:  # محدود کردن تعداد پیام‌های در صف
                await group_message_queue.put(event)
                print(f"Added group message to queue: {event.chat_id}")
            else:
                print("Group message queue full. Ignoring new message.")

    


    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
